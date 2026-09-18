"""Smoke: camera + Twist plus map, tf, entities, player, and a log line."""

from __future__ import annotations

import json
import sys
from pathlib import Path

from doom_foxglove import (
    CAMERA_TOPIC,
    CMD_VEL_TOPIC,
    ENTITIES_TOPIC,
    LOG_TOPIC,
    MAP_TOPIC,
    PLAYER_TOPIC,
    TF_TOPIC,
    DEFAULT_HOST,
    DEFAULT_PORT,
)
from doom_foxglove.engine import make_engine
from doom_foxglove.jpeg import encode_jpeg
from doom_foxglove.server import TeleopListener, publish_camera, start_ws, camera_channel
from doom_foxglove.teleop import DEADZONE, binary_buttons
from doom_foxglove.topics import publish_world, world_channels
from doom_foxglove.ws_client import SDK_SUBPROTOCOL, LayoutWireProbe, prove_client_publish


SMOKE_TICKS = 8
FORWARD_TWIST = {
    "linear": {"x": 1.0, "y": 0.0, "z": 0.0},
    "angular": {"x": 0.0, "y": 0.0, "z": 0.0},
}
ZERO_TWIST = {
    "linear": {"x": 0.0, "y": 0.0, "z": 0.0},
    "angular": {"x": 0.0, "y": 0.0, "z": 0.0},
}
LAYOUT_ROOT = Path(__file__).resolve().parents[1] / "layouts"


def _fail(message: str) -> int:
    print(f"SMOKE FAIL: {message}", file=sys.stderr)
    return 1


def _check_layouts() -> str | None:
    play = LAYOUT_ROOT / "Play.json"
    debug = LAYOUT_ROOT / "Debug.json"
    if not play.is_file() or not debug.is_file():
        return f"missing layout JSON under {LAYOUT_ROOT}"
    try:
        play_data = json.loads(play.read_text(encoding="utf-8"))
        debug_data = json.loads(debug.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return f"layout JSON is invalid: {exc}"
    play_text = json.dumps(play_data)
    debug_text = json.dumps(debug_data)
    for needle in ("Image", "Teleop", "Gauge", CAMERA_TOPIC, CMD_VEL_TOPIC, f"{PLAYER_TOPIC}.health"):
        if needle not in play_text:
            return f"Play.json is missing {needle}"
    for needle in (
        "ThreeDee",
        "Plot",
        "Log",
        "RawMessages",
        PLAYER_TOPIC,
        LOG_TOPIC,
        f"{PLAYER_TOPIC}.health",
    ):
        if needle not in debug_text:
            return f"Debug.json is missing {needle}"
    return None


def _tf_ok(summary: object) -> bool:
    if not isinstance(summary, dict):
        return False
    return (
        summary.get("parent_frame_id") == "map"
        and summary.get("child_frame_id") == "base_link"
        and int(summary.get("encoded") or 0) > 0
    )


def _grid_ok(summary: object) -> bool:
    if not isinstance(summary, dict):
        return False
    return (
        summary.get("frame_id") == "map"
        and int(summary.get("column_count") or 0) >= 1
        and int(summary.get("bytes") or 0) >= 1
        and int(summary.get("encoded") or 0) > 0
    )


def _scene_ok(summary: object) -> bool:
    if not isinstance(summary, dict):
        return False
    return "count" in summary and int(summary.get("encoded") or 0) > 0


def _player_ok(payload: object) -> bool:
    if not isinstance(payload, dict):
        return False
    return all(key in payload for key in ("health", "armor", "ammo", "weapon", "tick", "dead"))


def main() -> int:
    hero = "--hero" in sys.argv
    if not hero:
        layout_error = _check_layouts()
        if layout_error:
            return _fail(layout_error)

    fetch = "--no-fetch-iwad" not in sys.argv
    engine, info = make_engine(fetch_iwad=fetch, prefer_vizdoom=True)
    print(f"SMOKE engine backend={info.backend} map={info.map_name} iwad={info.iwad}")
    print(f"SMOKE engine note: {info.note}")

    listener = TeleopListener()
    server = None
    layout_probe = None
    try:
        server = start_ws(
            listener,
            host=DEFAULT_HOST,
            port=DEFAULT_PORT,
            fallback_if_busy=True,
        )
        bound = int(server.port)
        print(f"SMOKE websocket bound ws://{DEFAULT_HOST}:{bound}")
        if bound != DEFAULT_PORT:
            print(
                f"SMOKE note: {DEFAULT_PORT} was busy; live server still defaults to "
                f"ws://{DEFAULT_HOST}:{DEFAULT_PORT}"
            )

        cam = camera_channel()
        extra = world_channels()
        frames = 0
        twist_seen = False
        forward_latched = False
        saw_map = False
        saw_tf = False
        saw_scene = False
        saw_player = False
        saw_log = False
        entity_count = 0

        wire = prove_client_publish(DEFAULT_HOST, bound, listener)
        print(
            f"WIRE CHECK capability={wire['capability']} "
            f"camera_schema={wire['camera_schema']} "
            f"cmd_vel={wire['cmd_vel']} buttons={wire['buttons']}"
        )
        if wire["capability"] != "clientPublish":
            return _fail("WIRE CHECK missing clientPublish")
        if wire["camera_schema"] != "foxglove.CompressedImage":
            return _fail("WIRE CHECK camera schema is not foxglove.CompressedImage")
        if int(wire["cmd_vel"]) < 1 or int(wire["buttons"]) < 1:
            return _fail("WIRE CHECK cmd_vel/buttons counts must be >= 1 via on_message_data")
        twist_seen = listener.cmd_vel_count >= 1

        if not hero:
            layout_probe = LayoutWireProbe.connect(DEFAULT_HOST, bound)
            layout_probe.subscribe_world()

        engine.reset()
        for tick in range(SMOKE_TICKS):
            if tick == 1:
                payload = json.dumps(FORWARD_TWIST).encode("utf-8")
                command = listener.apply_raw(CMD_VEL_TOPIC, payload)
                flags = binary_buttons(command)
                if not flags["MOVE_FORWARD"]:
                    return _fail("forward Twist did not set MOVE_FORWARD")
                forward_latched = True
            if tick == SMOKE_TICKS - 1:
                listener.apply_raw(CMD_VEL_TOPIC, json.dumps(ZERO_TWIST).encode("utf-8"))
                if abs(listener.snapshot().linear_x) >= DEADZONE:
                    return _fail("zero Twist did not stop linear.x")

            command = listener.snapshot()
            frame = engine.step(command)
            jpeg = encode_jpeg(frame)
            if not jpeg or jpeg[:2] != b"\xff\xd8":
                return _fail("camera encode did not produce a JPEG")
            publish_camera(cam, jpeg)
            published = publish_world(extra, engine.observe())
            frames += 1

            if _grid_ok(published.get("map")):
                saw_map = True
            if _tf_ok(published.get("tf")):
                saw_tf = True
            scene = published.get("entities")
            if _scene_ok(scene):
                saw_scene = True
                entity_count = max(entity_count, int(scene.get("count") or 0))
            if _player_ok(published.get("player")):
                saw_player = True
            if published.get("logs"):
                saw_log = True
            if layout_probe is not None:
                layout_probe.drain(0.05)

        if frames < 1:
            return _fail("no camera frames published")
        if not twist_seen:
            return _fail("Twist was not accepted on /cmd_vel")
        if not forward_latched:
            return _fail("forward Twist was never applied")
        if not hero:
            if not saw_map:
                return _fail(f"{MAP_TOPIC} foxglove.Grid was not published")
            if not saw_tf:
                return _fail(f"{TF_TOPIC} map → base_link was not published")
            if not saw_scene:
                return _fail(f"{ENTITIES_TOPIC} SceneUpdate was not published")
            if not saw_player:
                return _fail(f"{PLAYER_TOPIC} JSON is missing required fields")
            if not saw_log:
                return _fail(f"{LOG_TOPIC} never received a log line")
            layout = layout_probe.finish() if layout_probe is not None else None
            if layout is None:
                return _fail("WIRE LAYOUT client was not opened")
            print(
                f"WIRE LAYOUT map_schema={layout['map_schema']} map={layout['map']} "
                f"map_frame={layout['map_frame']} "
                f"tf_schema={layout['tf_schema']} tf={layout['tf']} "
                f"tf_parent={layout['tf_parent']} tf_child={layout['tf_child']} "
                f"entities_schema={layout['entities_schema']} entities={layout['entities']} "
                f"player={layout['player']} player_keys={layout['player_keys']} "
                f"log_schema={layout['log_schema']} log={layout['log']}"
            )
            if layout["map_schema"] != "foxglove.Grid":
                return _fail("WIRE LAYOUT map_schema is not foxglove.Grid")
            if int(layout["map"]) != 1:
                return _fail("WIRE LAYOUT map count must be 1")
            if layout["map_frame"] != "map":
                return _fail("WIRE LAYOUT map_frame was not received as map")
            if layout["tf_schema"] != "foxglove.FrameTransforms":
                return _fail("WIRE LAYOUT tf_schema is not foxglove.FrameTransforms")
            if int(layout["tf"]) < 1:
                return _fail("WIRE LAYOUT tf count must be >= 1")
            if layout["tf_parent"] != "map" or layout["tf_child"] != "base_link":
                return _fail("WIRE LAYOUT tf parent/child were not received")
            if layout["entities_schema"] != "foxglove.SceneUpdate":
                return _fail("WIRE LAYOUT entities_schema is not foxglove.SceneUpdate")
            if int(layout["entities"]) < 1:
                return _fail("WIRE LAYOUT entities count must be >= 1")
            if int(layout["player"]) < 1:
                return _fail("WIRE LAYOUT player count must be >= 1")
            if layout["player_keys"] != "health,armor,ammo,weapon,tick,dead":
                return _fail("WIRE LAYOUT player_keys were not received")
            if layout["log_schema"] != "foxglove.Log":
                return _fail("WIRE LAYOUT log_schema is not foxglove.Log")
            if int(layout["log"]) < 1:
                return _fail("WIRE LAYOUT log count must be >= 1")

        if hero:
            print(
                f"SMOKE OK ticks={SMOKE_TICKS} frames={frames} "
                f"topic={CAMERA_TOPIC} cmd_vel={CMD_VEL_TOPIC} "
                f"backend={info.backend} subprotocol={SDK_SUBPROTOCOL}"
            )
        else:
            print(
                f"SMOKE OK ticks={SMOKE_TICKS} frames={frames} "
                f"topic={CAMERA_TOPIC} cmd_vel={CMD_VEL_TOPIC} "
                f"map={MAP_TOPIC} tf={TF_TOPIC} entities={ENTITIES_TOPIC} "
                f"entity_count={entity_count} player={PLAYER_TOPIC} "
                f"log={LOG_TOPIC} backend={info.backend}"
            )
        return 0
    except Exception as exc:
        return _fail(repr(exc))
    finally:
        if layout_probe is not None:
            try:
                layout_probe.close()
            except Exception:
                pass
        if server is not None:
            try:
                server.stop()
            except Exception:
                pass
        engine.close()


if __name__ == "__main__":
    sys.exit(main())
