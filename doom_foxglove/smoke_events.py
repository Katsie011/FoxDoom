"""Smoke: at least one tagged event on /doom/events, live and in MCAP."""

from __future__ import annotations

import sys

from doom_foxglove import DEFAULT_HOST, DEFAULT_PORT, EVENTS_TOPIC
from doom_foxglove.engine import make_engine
from doom_foxglove.jpeg import encode_jpeg
from doom_foxglove.record import (
    count_mcap_messages,
    list_mcap_topics,
    open_recording,
    smoke_events_recording_path,
)
from doom_foxglove.server import TeleopListener, camera_channel, publish_camera, start_ws
from doom_foxglove.topics import publish_world, world_channels
from doom_foxglove.world import EVENT_KINDS, KIND_LEVEL

SMOKE_TICKS = 8


def _fail(message: str) -> int:
    print(f"SMOKE-EVENTS FAIL: {message}", file=sys.stderr)
    return 1


def _event_ok(payload: object) -> bool:
    if not isinstance(payload, dict):
        return False
    kind = payload.get("kind")
    message = payload.get("message")
    return (
        kind in EVENT_KINDS
        and isinstance(message, str)
        and bool(message)
        and "tick" in payload
        and "map" in payload
    )


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    ticks = SMOKE_TICKS
    if "--ticks" in argv:
        idx = argv.index("--ticks")
        try:
            ticks = int(argv[idx + 1])
        except (IndexError, ValueError):
            return _fail("--ticks needs an integer")
        if ticks < 1:
            return _fail("--ticks must be >= 1")
    fetch = "--no-fetch-iwad" not in argv

    engine, info = make_engine(fetch_iwad=fetch, prefer_vizdoom=True)
    print(f"SMOKE-EVENTS engine backend={info.backend} map={info.map_name} iwad={info.iwad}")
    print(f"SMOKE-EVENTS engine note: {info.note}")

    dest = smoke_events_recording_path()
    listener = TeleopListener()
    server = None
    writer = None
    try:
        server = start_ws(
            listener,
            host=DEFAULT_HOST,
            port=DEFAULT_PORT,
            fallback_if_busy=True,
        )
        bound = int(server.port)
        print(f"SMOKE-EVENTS websocket bound ws://{DEFAULT_HOST}:{bound}")
        if bound != DEFAULT_PORT:
            print(
                f"SMOKE-EVENTS note: {DEFAULT_PORT} was busy; live server still defaults to "
                f"ws://{DEFAULT_HOST}:{DEFAULT_PORT}"
            )

        writer = open_recording(dest, allow_overwrite=True)
        cam = camera_channel()
        extra = world_channels()
        live_events: list[dict] = []
        published = 0

        engine.reset()
        for _tick in range(ticks):
            frame = engine.step(listener.snapshot())
            jpeg = encode_jpeg(frame)
            if not jpeg or jpeg[:2] != b"\xff\xd8":
                return _fail("camera encode did not produce a JPEG")
            publish_camera(cam, jpeg)
            summary = publish_world(extra, engine.observe())
            published += 1
            for payload in summary.get("events") or []:
                if _event_ok(payload):
                    live_events.append(payload)

        writer.close()
        writer = None

        if published < ticks:
            return _fail(f"published {published} ticks, wanted {ticks}")
        if not live_events:
            return _fail(f"{EVENTS_TOPIC} never received a tagged event")
        if not any(event.get("kind") == KIND_LEVEL for event in live_events):
            return _fail(f"{EVENTS_TOPIC} missing a level event (enter or complete)")

        if not dest.is_file():
            return _fail(f"MCAP was not written: {dest}")
        size = dest.stat().st_size
        if size < 1:
            return _fail(f"MCAP is empty: {dest}")

        topics = list_mcap_topics(dest)
        if EVENTS_TOPIC not in topics:
            return _fail(
                f"MCAP {dest} missing {EVENTS_TOPIC}; found {sorted(topics)}"
            )

        mcap_count = count_mcap_messages(dest, EVENTS_TOPIC)
        if mcap_count < 1:
            return _fail(
                f"MCAP {dest} has {EVENTS_TOPIC} but 0 messages (live published "
                f"{len(live_events)})"
            )

        kinds = sorted({str(event["kind"]) for event in live_events})
        print(
            f"SMOKE-EVENTS OK ticks={ticks} published={published} "
            f"topic={EVENTS_TOPIC} live={len(live_events)} kinds={kinds} "
            f"file={dest} bytes={size} mcap_events={mcap_count} "
            f"backend={info.backend}"
        )
        return 0
    except Exception as exc:
        return _fail(repr(exc))
    finally:
        if writer is not None:
            try:
                writer.close()
            except Exception:
                pass
        if server is not None:
            try:
                server.stop()
            except Exception:
                pass
        engine.close()


if __name__ == "__main__":
    raise SystemExit(main())
