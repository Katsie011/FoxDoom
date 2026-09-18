"""Smoke: pause the live loop, fetch the closed sidecar, assert topics."""

from __future__ import annotations

import json
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from threading import Thread

from doom_foxglove import DEFAULT_HOST, DEFAULT_PORT
from doom_foxglove.control import ControlState, start_control, stop_control
from doom_foxglove.engine import make_engine
from doom_foxglove.record import (
    EXPECTED_TOPICS,
    MCAP_MAGIC,
    list_mcap_topics,
    open_recording,
    recordings_dir,
)
from doom_foxglove.server import TeleopListener, run_loop, start_ws

MIN_FRAMES = 8


def _fail(message: str) -> int:
    print(f"SMOKE-PAUSE-REPLAY FAIL: {message}", file=sys.stderr)
    return 1


def _request(method: str, url: str, timeout: float = 5.0) -> tuple[int, bytes]:
    req = urllib.request.Request(url, method=method, data=b"" if method == "POST" else None)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return int(resp.status), resp.read()
    except urllib.error.HTTPError as exc:
        return int(exc.code), exc.read()


def _post_pause(base: str) -> tuple[int, dict]:
    status, body = _request("POST", f"{base}/pause")
    try:
        payload = json.loads(body.decode("utf-8")) if body else {}
    except json.JSONDecodeError:
        payload = {}
    return status, payload


def _wait_frames(published: dict[str, int], need: int, timeout: float) -> bool:
    deadline = time.monotonic() + timeout
    while published["n"] < need:
        if time.monotonic() > deadline:
            return False
        time.sleep(0.05)
    return True


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    immediate = "--immediate-pause" in argv
    no_record = "--no-record" in argv
    new_game = "--new-game" in argv
    fetch = "--no-fetch-iwad" not in argv

    engine, info = make_engine(fetch_iwad=fetch, prefer_vizdoom=True)
    print(f"SMOKE-PAUSE-REPLAY engine backend={info.backend} map={info.map_name} iwad={info.iwad}")
    print(f"SMOKE-PAUSE-REPLAY engine note: {info.note}")

    listener = TeleopListener()
    state = ControlState()
    state.engine = engine
    state.record_enabled = not no_record
    published = {"n": 0}

    def on_frame(n: int, command, jpeg) -> None:
        published["n"] = n

    dest = recordings_dir() / "smoke-pause.mcap"
    server = None
    control = None
    writer = None
    loop_thread: Thread | None = None
    try:
        server = start_ws(
            listener,
            host=DEFAULT_HOST,
            port=DEFAULT_PORT,
            fallback_if_busy=True,
        )
        control = start_control(
            state,
            host=DEFAULT_HOST,
            port=8764,
            fallback_if_busy=True,
        )
        bound = int(control.server_port)
        control_url = f"http://{DEFAULT_HOST}:{bound}"
        print(f"SMOKE-PAUSE-REPLAY control {control_url}")
        print(f"SMOKE-PAUSE-REPLAY websocket bound ws://{DEFAULT_HOST}:{int(server.port)}")

        if not no_record:
            writer = open_recording(dest, allow_overwrite=True)
            state.writer = writer
            state.recording = dest
            writer = None

        loop_thread = Thread(
            target=run_loop,
            kwargs={
                "engine": engine,
                "listener": listener,
                "forever": True,
                "on_frame": on_frame,
                "stop_event": state.stop_event,
            },
        )

        if immediate:
            status, payload = _post_pause(control_url)
            if status != 200 or payload.get("paused") is not True:
                return _fail(f"immediate POST /pause -> {status} {payload}")
            print("immediate_pause=ok")
            loop_thread.start()
            loop_thread.join(timeout=5.0)
            print(
                f"SMOKE-PAUSE-REPLAY OK ticks={published['n']} {control_url} "
                f"file={dest}"
            )
            return 0

        loop_thread.start()

        if no_record:
            if not _wait_frames(published, 1, 15.0):
                return _fail("engine never stepped under --no-record")
            status, payload = _post_pause(control_url)
            if status != 200 or payload.get("paused") is not True:
                return _fail(f"--no-record POST /pause -> {status} {payload}")
            rec_status, _ = _request("GET", f"{control_url}/recording")
            if rec_status != 409:
                return _fail(f"--no-record GET /recording -> {rec_status}, wanted 409")
            print("no_record=409")
            time.sleep(0.15)
            frozen = published["n"]
            time.sleep(0.4)
            if published["n"] != frozen:
                return _fail(f"still stepping after --no-record pause: {frozen} -> {published['n']}")
            print("step_stopped=ok")
            print(
                f"SMOKE-PAUSE-REPLAY OK ticks={published['n']} {control_url} "
                f"bytes=0"
            )
            return 0

        if not _wait_frames(published, MIN_FRAMES, 20.0):
            return _fail(f"published {published['n']} frames, wanted {MIN_FRAMES}")

        pre_status, _ = _request("GET", f"{control_url}/recording")
        if pre_status != 409:
            return _fail(f"GET /recording before pause -> {pre_status}, wanted 409")
        print("pre_pause=409")

        first_status, first_payload = _post_pause(control_url)
        second_status, second_payload = _post_pause(control_url)
        if first_status != 200 or first_payload.get("paused") is not True:
            return _fail(f"first POST /pause -> {first_status} {first_payload}")
        if second_status != 200 or second_payload.get("paused") is not True:
            return _fail(f"second POST /pause -> {second_status} {second_payload}")
        if first_payload.get("path") != second_payload.get("path"):
            return _fail(f"pause path changed: {first_payload} vs {second_payload}")
        print("double_pause=ok")

        rec_status, rec_body = _request("GET", f"{control_url}/recording")
        if rec_status != 200:
            return _fail(f"GET /recording after pause -> {rec_status}")
        if not rec_body.startswith(MCAP_MAGIC):
            return _fail(f"GET /recording body missing MCAP magic: {rec_body[:16]!r}")
        if not dest.is_file():
            return _fail(f"sidecar missing: {dest}")
        topics = list_mcap_topics(dest)
        missing = [topic for topic in EXPECTED_TOPICS if topic not in topics]
        if missing:
            return _fail(f"sidecar missing topics {missing}; found {sorted(topics)}")

        time.sleep(0.15)
        frozen = published["n"]
        time.sleep(0.4)
        if published["n"] != frozen:
            return _fail(f"still stepping after pause: {frozen} -> {published['n']}")
        print("step_stopped=ok")

        if new_game:
            recs_status, recs_body = _request("GET", f"{control_url}/recordings")
            if recs_status != 200:
                return _fail(f"GET /recordings -> {recs_status}")
            try:
                recs = json.loads(recs_body.decode("utf-8")) if recs_body else []
            except json.JSONDecodeError:
                return _fail(f"GET /recordings not JSON: {recs_body[:80]!r}")
            names = [item.get("name") for item in recs if isinstance(item, dict)]
            if dest.name not in names:
                return _fail(f"GET /recordings missing sidecar {dest.name}: {names}")
            print(f"recordings_include={dest.name}")

            ng_status, ng_body = _request("POST", f"{control_url}/new-game")
            try:
                ng_payload = json.loads(ng_body.decode("utf-8")) if ng_body else {}
            except json.JSONDecodeError:
                ng_payload = {}
            if ng_status != 200:
                return _fail(f"POST /new-game -> {ng_status} {ng_payload}")
            if ng_payload.get("paused") is not False and ng_payload.get("reset") is not True:
                return _fail(f"POST /new-game payload {ng_payload}")
            new_path = ng_payload.get("path")
            if not new_path or Path(new_path).resolve() == dest.resolve():
                return _fail(f"new-game path not new: {new_path} vs {dest}")
            print("new_game=ok")
            print(f"old={dest} new={new_path}")

            published["n"] = 0
            loop_thread = Thread(
                target=run_loop,
                kwargs={
                    "engine": engine,
                    "listener": listener,
                    "forever": True,
                    "on_frame": on_frame,
                    "stop_event": state.stop_event,
                },
            )
            loop_thread.start()
            if not _wait_frames(published, MIN_FRAMES, 20.0):
                return _fail(f"new game published {published['n']} frames, wanted {MIN_FRAMES}")
            print("step_new_game=ok")

        print(
            f"SMOKE-PAUSE-REPLAY OK ticks={published['n']} {control_url} "
            f"file={dest} bytes={len(rec_body)} topics={sorted(topics)}"
        )
        return 0
    except Exception as exc:
        return _fail(repr(exc))
    finally:
        state.stop_event.set()
        if loop_thread is not None and loop_thread.is_alive():
            loop_thread.join(timeout=5.0)
        leftover = state.writer if writer is None else writer
        if leftover is not None:
            try:
                leftover.close()
            except Exception:
                pass
            state.writer = None
        stop_control(control)
        if server is not None:
            try:
                server.stop()
            except Exception:
                pass
        engine.close()


if __name__ == "__main__":
    raise SystemExit(main())
