"""Foxglove SDK WebSocket server: camera out, Twist and buttons in."""

from __future__ import annotations

import argparse
import sys
import threading
import time
from pathlib import Path
from typing import Any

from doom_foxglove import (
    BUTTONS_TOPIC,
    CAMERA_TOPIC,
    CMD_VEL_TOPIC,
    DEFAULT_HOST,
    DEFAULT_PORT,
    ENTITIES_TOPIC,
    EVENTS_TOPIC,
    LOG_TOPIC,
    MAP_TOPIC,
    PLAYER_TOPIC,
    TF_TOPIC,
    TICK_HZ,
)
from doom_foxglove.control import ControlState, start_control, stop_control
from doom_foxglove.engine import Engine, make_engine
from doom_foxglove.jpeg import encode_jpeg
from doom_foxglove.record import default_recording_path, open_recording
from doom_foxglove.teleop import Command, apply_topic
from doom_foxglove.topics import publish_world, world_channels


class TeleopListener:
    """foxglove.websocket.ServerListener compatible: ClientPublish JSON in."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._command = Command()
        self._topics: dict[tuple[Any, Any], str] = {}
        self.cmd_vel_count = 0
        self.buttons_count = 0

    def snapshot(self) -> Command:
        with self._lock:
            return self._command

    def apply_raw(self, topic: str, data: bytes) -> Command:
        """In-process latch helper. Does not increment wire counts (HL-10)."""
        with self._lock:
            self._command = apply_topic(topic, data, self._command)
            return self._command

    def on_subscribe(self, client: Any, channel: Any) -> None:
        return None

    def on_unsubscribe(self, client: Any, channel: Any) -> None:
        return None

    def on_client_advertise(self, client: Any, channel: Any) -> None:
        client_id = getattr(client, "id", client)
        channel_id = getattr(channel, "id", None)
        topic = getattr(channel, "topic", "") or ""
        if channel_id is not None:
            self._topics[(client_id, channel_id)] = topic

    def on_client_unadvertise(self, client: Any, channel: Any) -> None:
        client_id = getattr(client, "id", client)
        channel_id = getattr(channel, "id", channel)
        self._topics.pop((client_id, channel_id), None)

    def on_message_data(self, client: Any, channel_or_id: Any, data: bytes | None = None) -> None:
        if data is None:
            return
        if hasattr(channel_or_id, "topic"):
            topic = channel_or_id.topic
        else:
            client_id = getattr(client, "id", client)
            topic = self._topics.get((client_id, channel_or_id), "")
        if topic in (CMD_VEL_TOPIC, BUTTONS_TOPIC):
            try:
                with self._lock:
                    self._command = apply_topic(topic, data, self._command)
                    if topic == CMD_VEL_TOPIC:
                        self.cmd_vel_count += 1
                    elif topic == BUTTONS_TOPIC:
                        self.buttons_count += 1
            except (ValueError, UnicodeDecodeError):
                return


def _timestamp():
    try:
        from foxglove.messages import Timestamp
    except ImportError:
        from foxglove.schemas import Timestamp

    now = time.time()
    if hasattr(Timestamp, "from_epoch_secs"):
        return Timestamp.from_epoch_secs(now)
    sec = int(now)
    nsec = int((now - sec) * 1_000_000_000)
    try:
        return Timestamp(sec=sec, nsec=nsec)
    except TypeError:
        return Timestamp(sec=sec, nsec=nsec)


def start_ws(
    listener: TeleopListener,
    host: str = DEFAULT_HOST,
    port: int = DEFAULT_PORT,
    *,
    fallback_if_busy: bool = False,
):
    import foxglove
    from foxglove.websocket import Capability

    def _bind(bind_port: int):
        return foxglove.start_server(
            name="foxglove-doom",
            host=host,
            port=bind_port,
            capabilities=[Capability.ClientPublish],
            supported_encodings=["json"],
            server_listener=listener,
        )

    try:
        server = _bind(port)
    except Exception as exc:
        busy = "already in use" in str(exc).lower() or "os error 48" in str(exc).lower()
        if not (fallback_if_busy and busy and port != 0):
            raise
        server = _bind(0)
    bound = int(server.port)
    if bound <= 0:
        raise RuntimeError("foxglove websocket bound an invalid port")
    return server


def publish_camera(channel: Any, jpeg: bytes) -> None:
    try:
        from foxglove.messages import CompressedImage
    except ImportError:
        from foxglove.schemas import CompressedImage

    channel.log(
        CompressedImage(
            timestamp=_timestamp(),
            frame_id="doom_camera",
            format="jpeg",
            data=jpeg,
        )
    )


def camera_channel():
    from foxglove.channels import CompressedImageChannel

    return CompressedImageChannel(topic=CAMERA_TOPIC)


def run_loop(
    engine: Engine,
    listener: TeleopListener,
    *,
    hz: float = TICK_HZ,
    forever: bool = True,
    ticks: int | None = None,
    on_frame=None,
    stop_event=None,
) -> int:
    cam = camera_channel()
    extra = world_channels()
    period = 1.0 / hz if hz > 0 else 0.0
    published = 0
    n = 0
    try:
        engine.reset()
        while True:
            if stop_event is not None and stop_event.is_set():
                break
            started = time.perf_counter()
            command = listener.snapshot()
            frame = engine.step(command)
            jpeg = encode_jpeg(frame)
            publish_camera(cam, jpeg)
            publish_world(extra, engine.observe())
            published += 1
            if on_frame is not None:
                on_frame(published, command, jpeg)
            n += 1
            if ticks is not None and n >= ticks:
                break
            if not forever and ticks is None:
                break
            leftover = period - (time.perf_counter() - started)
            if leftover > 0:
                if stop_event is not None:
                    if stop_event.wait(timeout=leftover):
                        break
                else:
                    time.sleep(leftover)
    finally:
        pass
    return published


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Foxglove DOOM live WebSocket server")
    parser.add_argument("--host", default=DEFAULT_HOST)
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    parser.add_argument("--fetch-iwad", action="store_true", help="download Freedoom if missing")
    parser.add_argument(
        "--fallback",
        action="store_true",
        help="skip ViZDoom and publish the labeled fallback framebuffer",
    )
    parser.add_argument(
        "--no-record",
        action="store_true",
        help="do not write an MCAP sidecar under recordings/",
    )
    parser.add_argument(
        "--recording",
        default=None,
        help="MCAP sidecar path (default: recordings/doom-<utc-timestamp>.mcap)",
    )
    parser.add_argument("--control-port", type=int, default=8764)
    args = parser.parse_args(argv)

    engine, info = make_engine(fetch_iwad=args.fetch_iwad, prefer_vizdoom=not args.fallback)
    print(f"engine backend={info.backend} map={info.map_name} iwad={info.iwad}")
    print(f"engine note: {info.note}")
    print(
        f"foxglove ws://{args.host}:{args.port}  camera={CAMERA_TOPIC}  "
        f"map={MAP_TOPIC} tf={TF_TOPIC} entities={ENTITIES_TOPIC} "
        f"player={PLAYER_TOPIC} log={LOG_TOPIC} events={EVENTS_TOPIC} "
        f"teleop={CMD_VEL_TOPIC}"
    )
    listener = TeleopListener()
    server = start_ws(listener, host=args.host, port=args.port)
    state = ControlState()
    state.engine = engine
    state.record_enabled = not args.no_record
    writer = None
    if not args.no_record:
        rec_path = Path(args.recording) if args.recording else default_recording_path()
        writer = open_recording(rec_path)
        state.writer = writer
        state.recording = rec_path
        print(f"recording {rec_path}")
    control = start_control(state, host=args.host, port=args.control_port)
    print(f"control http://{args.host}:{int(control.server_port)}")
    try:
        while True:
            run_loop(engine, listener, forever=True, stop_event=state.stop_event)
            if state.take_new_game():
                state.stop_event.clear()
                continue
            # Pause must not exit the process: the embed POSTs /pause then GETs
            # /recording. Idle until POST /new-game or KeyboardInterrupt, then
            # run_loop again for a fresh episode.
            print("paused; serving GET /recording until new-game or interrupt")
            while not state.wait_new_game(timeout=0.5):
                pass
            state.take_new_game()
            state.stop_event.clear()
    except KeyboardInterrupt:
        print("stopping")
    finally:
        state.stop_event.set()
        leftover = state.writer if writer is None else state.writer or writer
        if leftover is not None:
            try:
                leftover.close()
            except Exception:
                pass
            state.writer = None
        stop_control(control)
        try:
            server.stop()
        except Exception:
            pass
        engine.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
