"""Stdlib HTTP control plane: pause, new-game, and serve recordings."""

from __future__ import annotations

import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlparse

from doom_foxglove.record import default_recording_path, open_recording, recordings_dir

DEFAULT_CONTROL_PORT = 8764
CORS_ORIGIN = "*"
_CONTROL_PATHS = ("/pause", "/new-game", "/recording", "/recordings")


class ControlState:
    """Shared pause / new-game / recording state for the live process and HTTP handlers."""

    def __init__(self) -> None:
        self.lock = threading.Lock()
        self.stop_event = threading.Event()
        self.new_game_event = threading.Event()
        self.writer: Any = None
        self.recording: Path | None = None
        self.paused = False
        self.engine: Any = None
        self.record_enabled = True

    def pause(self) -> dict[str, Any]:
        with self.lock:
            self.stop_event.set()
            writer = self.writer
            if writer is not None:
                try:
                    writer.close()
                except Exception:
                    pass
                self.writer = None
            self.paused = True
            payload: dict[str, Any] = {"paused": True}
            if self.recording is not None:
                payload["path"] = str(self.recording)
            return payload

    def new_game(self) -> dict[str, Any]:
        with self.lock:
            self.stop_event.set()
            writer = self.writer
            if writer is not None:
                try:
                    writer.close()
                except Exception:
                    pass
                self.writer = None
            engine = self.engine
            if engine is not None:
                engine.reset()
            if self.record_enabled:
                rec_path = default_recording_path()
                self.writer = open_recording(rec_path)
                self.recording = rec_path
            self.paused = False
            self.stop_event.clear()
            self.new_game_event.set()
            payload: dict[str, Any] = {"paused": False, "reset": True}
            if self.recording is not None:
                payload["path"] = str(self.recording)
            return payload

    def take_new_game(self) -> bool:
        with self.lock:
            if not self.new_game_event.is_set():
                return False
            self.new_game_event.clear()
            return True

    def wait_new_game(self, timeout: float) -> bool:
        return self.new_game_event.wait(timeout)

    def recording_path_if_ready(self) -> Path | None:
        with self.lock:
            if not self.paused or self.recording is None:
                return None
            return self.recording


def list_recording_files() -> list[dict[str, Any]]:
    dest = recordings_dir()
    out: list[dict[str, Any]] = []
    for path in sorted(dest.glob("*.mcap")):
        if not path.is_file():
            continue
        out.append({"name": path.name, "bytes": path.stat().st_size, "path": str(path)})
    return out


def resolve_recording_name(name: str) -> Path | None:
    if not name or ".." in name:
        return None
    base = recordings_dir().resolve()
    dest = (base / Path(name).name).resolve()
    if not dest.is_relative_to(base):
        return None
    return dest


class ControlHandler(BaseHTTPRequestHandler):
    state: ControlState

    def log_message(self, fmt: str, *args: Any) -> None:
        return

    def _cors(self) -> None:
        self.send_header("Access-Control-Allow-Origin", CORS_ORIGIN)
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def _json(self, status: int, payload: Any) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self._cors()
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _octet(self, blob: bytes) -> None:
        self.send_response(200)
        self._cors()
        self.send_header("Content-Type", "application/octet-stream")
        self.send_header("Content-Length", str(len(blob)))
        self.end_headers()
        self.wfile.write(blob)

    def do_OPTIONS(self) -> None:
        path = urlparse(self.path).path
        if path not in _CONTROL_PATHS:
            self.send_error(404)
            return
        self.send_response(204)
        self._cors()
        self.end_headers()

    def do_POST(self) -> None:
        path = urlparse(self.path).path
        if path == "/pause":
            self._json(200, self.state.pause())
            return
        if path == "/new-game":
            self._json(200, self.state.new_game())
            return
        self.send_error(404)

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        path = parsed.path
        if path == "/recordings":
            self._json(200, list_recording_files())
            return
        if path != "/recording":
            self.send_error(404)
            return
        query = parse_qs(parsed.query)
        names = query.get("name") or []
        if names:
            dest = resolve_recording_name(names[0])
            if dest is None:
                self._json(400, {"error": "invalid name"})
                return
            if not dest.is_file():
                self._json(404, {"error": "recording not found"})
                return
            self._octet(dest.read_bytes())
            return
        dest = self.state.recording_path_if_ready()
        if dest is None or not dest.is_file():
            self._json(409, {"error": "recording not available"})
            return
        self._octet(dest.read_bytes())


def start_control(
    state: ControlState,
    host: str = "127.0.0.1",
    port: int = DEFAULT_CONTROL_PORT,
    *,
    fallback_if_busy: bool = False,
) -> ThreadingHTTPServer:
    ControlHandler.state = state
    try:
        server = ThreadingHTTPServer((host, port), ControlHandler)
    except Exception as exc:
        busy = "already in use" in str(exc).lower() or "os error 48" in str(exc).lower()
        if not (fallback_if_busy and busy and port != 0):
            raise
        server = ThreadingHTTPServer((host, 0), ControlHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True, name="doom-control")
    thread.start()
    return server


def stop_control(server: ThreadingHTTPServer | None) -> None:
    if server is None:
        return
    try:
        server.shutdown()
    except Exception:
        pass
    try:
        server.server_close()
    except Exception:
        pass
