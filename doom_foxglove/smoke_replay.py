"""Smoke: record N ticks to an MCAP sidecar and assert expected topics."""

from __future__ import annotations

import json
import sys
from pathlib import Path

from doom_foxglove import DEFAULT_HOST, DEFAULT_PORT
from doom_foxglove.engine import make_engine
from doom_foxglove.record import (
    EXPECTED_TOPICS,
    list_mcap_topics,
    open_recording,
    smoke_recording_path,
)
from doom_foxglove.server import TeleopListener, run_loop, start_ws

SMOKE_TICKS = 8
LAYOUT_ROOT = Path(__file__).resolve().parents[1] / "layouts"


def _fail(message: str) -> int:
    print(f"SMOKE-REPLAY FAIL: {message}", file=sys.stderr)
    return 1


def _check_replay_layout() -> str | None:
    path = LAYOUT_ROOT / "Replay.json"
    if not path.is_file():
        return f"missing {path}"
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return f"Replay.json is invalid: {exc}"
    text = json.dumps(data)
    if "Teleop" in text:
        return "Replay.json must hide Teleop"
    for needle in ("Image", "ThreeDee", "Gauge", "Log", "/doom/camera", "/doom/log"):
        if needle not in text:
            return f"Replay.json is missing {needle}"
    return None


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

    layout_error = _check_replay_layout()
    if layout_error:
        return _fail(layout_error)

    engine, info = make_engine(fetch_iwad=fetch, prefer_vizdoom=True)
    print(f"SMOKE-REPLAY engine backend={info.backend} map={info.map_name} iwad={info.iwad}")
    print(f"SMOKE-REPLAY engine note: {info.note}")

    dest = smoke_recording_path()
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
        print(f"SMOKE-REPLAY websocket bound ws://{DEFAULT_HOST}:{bound}")
        if bound != DEFAULT_PORT:
            print(
                f"SMOKE-REPLAY note: {DEFAULT_PORT} was busy; live server still defaults to "
                f"ws://{DEFAULT_HOST}:{DEFAULT_PORT}"
            )

        writer = open_recording(dest, allow_overwrite=True)
        published = run_loop(engine, listener, forever=False, ticks=ticks)
        writer.close()
        writer = None

        if published < ticks:
            return _fail(f"published {published} ticks, wanted {ticks}")
        if not dest.is_file():
            return _fail(f"MCAP was not written: {dest}")
        size = dest.stat().st_size
        if size < 1:
            return _fail(f"MCAP is empty: {dest}")

        topics = list_mcap_topics(dest)
        missing = [topic for topic in EXPECTED_TOPICS if topic not in topics]
        if missing:
            return _fail(
                f"MCAP {dest} missing topics {missing}; found {sorted(topics)}"
            )

        print(
            f"SMOKE-REPLAY OK ticks={ticks} published={published} "
            f"file={dest} bytes={size} topics={sorted(topics)}"
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
