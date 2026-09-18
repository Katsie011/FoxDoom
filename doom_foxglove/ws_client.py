"""Stdlib WebSocket client for foxglove.sdk.v1 ClientPublish and layout proofs."""

from __future__ import annotations

import base64
import json
import os
import socket
import struct
import time
from typing import Any

from doom_foxglove import (
    BUTTONS_TOPIC,
    CAMERA_TOPIC,
    CMD_VEL_TOPIC,
    ENTITIES_TOPIC,
    LOG_TOPIC,
    MAP_TOPIC,
    PLAYER_TOPIC,
    TF_TOPIC,
)

SDK_SUBPROTOCOL = "foxglove.sdk.v1"
CLIENT_MESSAGE_DATA = 0x01
SERVER_MESSAGE_DATA = 0x01
_CMD_VEL_CHANNEL_ID = 1
_BUTTONS_CHANNEL_ID = 2
_MESSAGE_DATA_HEADER = 13

_LAYOUT_TOPICS = {
    MAP_TOPIC: "map",
    TF_TOPIC: "tf",
    ENTITIES_TOPIC: "entities",
    PLAYER_TOPIC: "player",
    LOG_TOPIC: "log",
}

_TWIST_SCHEMA = json.dumps(
    {
        "type": "object",
        "additionalProperties": True,
        "properties": {
            "linear": {
                "type": "object",
                "properties": {
                    "x": {"type": "number"},
                    "y": {"type": "number"},
                    "z": {"type": "number"},
                },
            },
            "angular": {
                "type": "object",
                "properties": {
                    "x": {"type": "number"},
                    "y": {"type": "number"},
                    "z": {"type": "number"},
                },
            },
        },
    }
)
_BUTTONS_SCHEMA = json.dumps(
    {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "fire": {"type": "boolean"},
            "use": {"type": "boolean"},
            "weapon": {"type": ["integer", "null"]},
        },
        "required": ["fire", "use"],
    }
)

FORWARD_TWIST = {
    "linear": {"x": 1.0, "y": 0.0, "z": 0.0},
    "angular": {"x": 0.0, "y": 0.0, "z": 0.0},
}
FIRE_BUTTONS = {"fire": True, "use": False, "weapon": 2}


class SdkWsClient:
    """RFC 6455 client that negotiates subprotocol foxglove.sdk.v1."""

    def __init__(self, sock: socket.socket) -> None:
        self._sock = sock
        self._buf = bytearray()

    @classmethod
    def connect(cls, host: str, port: int, *, timeout: float = 5.0) -> "SdkWsClient":
        sock = socket.create_connection((host, port), timeout=timeout)
        key = base64.b64encode(os.urandom(16)).decode("ascii")
        request = (
            f"GET / HTTP/1.1\r\n"
            f"Host: {host}:{port}\r\n"
            f"Upgrade: websocket\r\n"
            f"Connection: Upgrade\r\n"
            f"Sec-WebSocket-Key: {key}\r\n"
            f"Sec-WebSocket-Version: 13\r\n"
            f"Sec-WebSocket-Protocol: {SDK_SUBPROTOCOL}\r\n"
            f"\r\n"
        )
        sock.sendall(request.encode("ascii"))
        header = b""
        while b"\r\n\r\n" not in header:
            chunk = sock.recv(4096)
            if not chunk:
                sock.close()
                raise OSError("websocket handshake closed")
            header += chunk
        head, rest = header.split(b"\r\n\r\n", 1)
        status = head.split(b"\r\n", 1)[0]
        if b"101" not in status:
            sock.close()
            raise OSError(f"websocket handshake failed: {status!r}")
        headers = {
            line.split(b":", 1)[0].strip().lower(): line.split(b":", 1)[1].strip()
            for line in head.split(b"\r\n")[1:]
            if b":" in line
        }
        proto = headers.get(b"sec-websocket-protocol", b"").decode("ascii", "replace")
        if SDK_SUBPROTOCOL not in proto:
            sock.close()
            raise OSError(f"server did not negotiate {SDK_SUBPROTOCOL}: {proto!r}")
        client = cls(sock)
        client._buf.extend(rest)
        return client

    def close(self) -> None:
        try:
            self._send_frame(0x8, b"")
        except OSError:
            pass
        try:
            self._sock.close()
        except OSError:
            pass

    def send_json(self, payload: dict[str, Any]) -> None:
        self._send_frame(0x1, json.dumps(payload).encode("utf-8"))

    def send_client_message(self, channel_id: int, payload: dict[str, Any]) -> None:
        body = json.dumps(payload).encode("utf-8")
        frame = bytes([CLIENT_MESSAGE_DATA]) + struct.pack("<I", channel_id) + body
        self._send_frame(0x2, frame)

    def recv_json(self, timeout: float) -> dict[str, Any] | None:
        deadline = time.time() + timeout
        while time.time() < deadline:
            remaining = max(0.01, deadline - time.time())
            event = self.recv_event(remaining)
            if event is None:
                return None
            if event[0] == "json":
                return event[1]
        return None

    def recv_event(self, timeout: float) -> tuple[str, Any] | None:
        """Return ('json', dict) or ('bin', bytes). Pings are answered, not returned."""
        deadline = time.time() + timeout
        while time.time() < deadline:
            remaining = max(0.01, deadline - time.time())
            self._sock.settimeout(remaining)
            opcode, payload = self._recv_frame()
            if opcode is None:
                return None
            if opcode == 0x9:
                self._send_frame(0xA, payload)
                continue
            if opcode == 0x8:
                return None
            if opcode == 0x1:
                obj = json.loads(payload.decode("utf-8"))
                if isinstance(obj, dict):
                    return ("json", obj)
                continue
            if opcode == 0x2:
                return ("bin", payload)
        return None

    def _send_frame(self, opcode: int, payload: bytes) -> None:
        mask = os.urandom(4)
        header = bytearray()
        header.append(0x80 | (opcode & 0x0F))
        n = len(payload)
        if n < 126:
            header.append(0x80 | n)
        elif n < 65536:
            header.append(0x80 | 126)
            header.extend(struct.pack(">H", n))
        else:
            header.append(0x80 | 127)
            header.extend(struct.pack(">Q", n))
        header.extend(mask)
        masked = bytes(b ^ mask[i % 4] for i, b in enumerate(payload))
        self._sock.sendall(header + masked)

    def _recv_exact(self, n: int) -> bytes:
        while len(self._buf) < n:
            chunk = self._sock.recv(max(4096, n - len(self._buf)))
            if not chunk:
                raise OSError("websocket closed")
            self._buf.extend(chunk)
        data = bytes(self._buf[:n])
        del self._buf[:n]
        return data

    def _recv_frame(self) -> tuple[int | None, bytes]:
        try:
            b1, b2 = self._recv_exact(2)
        except (OSError, TimeoutError, socket.timeout):
            return None, b""
        opcode = b1 & 0x0F
        masked = bool(b2 & 0x80)
        length = b2 & 0x7F
        if length == 126:
            length = struct.unpack(">H", self._recv_exact(2))[0]
        elif length == 127:
            length = struct.unpack(">Q", self._recv_exact(8))[0]
        mask = self._recv_exact(4) if masked else b""
        payload = self._recv_exact(length)
        if masked:
            payload = bytes(b ^ mask[i % 4] for i, b in enumerate(payload))
        return opcode, payload


def _client_advertise() -> dict[str, Any]:
    return {
        "op": "advertise",
        "channels": [
            {
                "id": _CMD_VEL_CHANNEL_ID,
                "topic": CMD_VEL_TOPIC,
                "encoding": "json",
                "schemaName": "geometry_msgs/Twist",
                "schemaEncoding": "jsonschema",
                "schema": _TWIST_SCHEMA,
            },
            {
                "id": _BUTTONS_CHANNEL_ID,
                "topic": BUTTONS_TOPIC,
                "encoding": "json",
                "schemaName": "doom.Buttons",
                "schemaEncoding": "jsonschema",
                "schema": _BUTTONS_SCHEMA,
            },
        ],
    }


def prove_client_publish(
    host: str,
    port: int,
    listener: Any,
    *,
    timeout: float = 3.0,
) -> dict[str, Any]:
    """Connect with foxglove.sdk.v1, read serverInfo/advertise, ClientPublish Twist+buttons.

    Counted deliveries must land in TeleopListener.on_message_data, not apply_raw.
    """
    client = SdkWsClient.connect(host, port)
    capability = ""
    camera_schema = ""
    try:
        deadline = time.time() + timeout
        while time.time() < deadline and (not capability or not camera_schema):
            remaining = max(0.05, deadline - time.time())
            msg = client.recv_json(remaining)
            if msg is None:
                continue
            op = msg.get("op")
            if op == "serverInfo":
                caps = msg.get("capabilities") or []
                if "clientPublish" in caps:
                    capability = "clientPublish"
            if op == "advertise":
                for channel in msg.get("channels") or []:
                    if not isinstance(channel, dict):
                        continue
                    if channel.get("topic") == CAMERA_TOPIC:
                        camera_schema = str(channel.get("schemaName") or "")
        if capability != "clientPublish":
            raise OSError("serverInfo missing clientPublish capability")
        if camera_schema != "foxglove.CompressedImage":
            raise OSError(f"camera schema was {camera_schema!r}")

        client.send_json(_client_advertise())
        # Ordered WS frames: advertise is processed before the next send, but give
        # the SDK listener a tick so on_client_advertise fills topic maps.
        time.sleep(0.05)
        client.send_client_message(_CMD_VEL_CHANNEL_ID, FORWARD_TWIST)
        client.send_client_message(_BUTTONS_CHANNEL_ID, FIRE_BUTTONS)

        wait_until = time.time() + timeout
        while time.time() < wait_until:
            if int(getattr(listener, "cmd_vel_count", 0)) >= 1 and int(
                getattr(listener, "buttons_count", 0)
            ) >= 1:
                break
            time.sleep(0.01)
    finally:
        client.close()

    return {
        "capability": capability,
        "camera_schema": camera_schema,
        "cmd_vel": int(getattr(listener, "cmd_vel_count", 0)),
        "buttons": int(getattr(listener, "buttons_count", 0)),
    }


def _uvarint(buf: bytes, i: int) -> tuple[int, int]:
    shift = 0
    value = 0
    while i < len(buf):
        byte = buf[i]
        i += 1
        value |= (byte & 0x7F) << shift
        if not (byte & 0x80):
            return value, i
        shift += 7
        if shift > 70:
            break
    raise ValueError("truncated protobuf varint")


def _proto_fields(buf: bytes) -> list[tuple[int, bytes]]:
    fields: list[tuple[int, bytes]] = []
    i = 0
    n = len(buf)
    while i < n:
        key, i = _uvarint(buf, i)
        field = key >> 3
        wire = key & 7
        if wire == 0:
            _, i = _uvarint(buf, i)
            fields.append((field, b""))
        elif wire == 1:
            fields.append((field, buf[i : i + 8]))
            i += 8
        elif wire == 2:
            size, i = _uvarint(buf, i)
            fields.append((field, buf[i : i + size]))
            i += size
        elif wire == 5:
            fields.append((field, buf[i : i + 4]))
            i += 4
        else:
            break
    return fields


def _grid_frame_id(payload: bytes) -> str:
    for field, value in _proto_fields(payload):
        if field == 2:
            return value.decode("utf-8", "replace")
    return ""


def _tf_parent_child(payload: bytes) -> tuple[str, str]:
    parent = ""
    child = ""
    for field, value in _proto_fields(payload):
        if field != 1:
            continue
        for inner, raw in _proto_fields(value):
            if inner == 2:
                parent = raw.decode("utf-8", "replace")
            elif inner == 3:
                child = raw.decode("utf-8", "replace")
        if parent or child:
            break
    return parent, child


def _parse_message_data(payload: bytes) -> tuple[int, bytes] | None:
    if len(payload) < _MESSAGE_DATA_HEADER or payload[0] != SERVER_MESSAGE_DATA:
        return None
    sub_id = struct.unpack_from("<I", payload, 1)[0]
    return sub_id, payload[_MESSAGE_DATA_HEADER:]


def _player_keys(payload: bytes) -> str:
    obj = json.loads(payload.decode("utf-8"))
    if not isinstance(obj, dict):
        return ""
    return ",".join(str(key) for key in obj.keys())


class LayoutWireProbe:
    """Subscribe to the five 02 topics over foxglove.sdk.v1 and count wire deliveries."""

    def __init__(self, client: SdkWsClient) -> None:
        self._client = client
        self._channels: dict[str, dict[str, Any]] = {}
        self._sub_topic: dict[int, str] = {}
        self.map_schema = ""
        self.tf_schema = ""
        self.entities_schema = ""
        self.log_schema = ""
        self.map_frame = ""
        self.tf_parent = ""
        self.tf_child = ""
        self.player_keys = ""
        self.counts = {"map": 0, "tf": 0, "entities": 0, "player": 0, "log": 0}

    @classmethod
    def connect(cls, host: str, port: int, *, timeout: float = 5.0) -> "LayoutWireProbe":
        return cls(SdkWsClient.connect(host, port, timeout=timeout))

    def close(self) -> None:
        self._client.close()

    def subscribe_world(self, *, timeout: float = 3.0) -> None:
        """Read advertise schemas, then subscribe to the five 02 topics."""
        deadline = time.time() + timeout
        while time.time() < deadline and not self._have_advertise():
            remaining = max(0.05, deadline - time.time())
            event = self._client.recv_event(remaining)
            if event is None:
                continue
            if event[0] != "json":
                continue
            self._ingest_json(event[1])
        if not self._have_advertise():
            missing = [topic for topic in _LAYOUT_TOPICS if topic not in self._channels]
            raise OSError(f"advertise missing 02 topics: {missing}")

        subscriptions: list[dict[str, int]] = []
        for sub_id, topic in enumerate(_LAYOUT_TOPICS):
            channel = self._channels[topic]
            subscriptions.append({"id": sub_id, "channelId": int(channel["id"])})
            self._sub_topic[sub_id] = topic
        self._client.send_json({"op": "subscribe", "subscriptions": subscriptions})
        time.sleep(0.05)

    def drain(self, timeout: float) -> None:
        deadline = time.time() + timeout
        while time.time() < deadline:
            remaining = max(0.01, deadline - time.time())
            event = self._client.recv_event(remaining)
            if event is None:
                return
            if event[0] == "json":
                self._ingest_json(event[1])
                continue
            self._ingest_bin(event[1])

    def finish(self, *, timeout: float = 2.0) -> dict[str, Any]:
        deadline = time.time() + timeout
        while time.time() < deadline and not self._have_payloads():
            self.drain(max(0.05, deadline - time.time()))
        return self.snapshot()

    def snapshot(self) -> dict[str, Any]:
        return {
            "map_schema": self.map_schema,
            "map": int(self.counts["map"]),
            "map_frame": self.map_frame,
            "tf_schema": self.tf_schema,
            "tf": int(self.counts["tf"]),
            "tf_parent": self.tf_parent,
            "tf_child": self.tf_child,
            "entities_schema": self.entities_schema,
            "entities": int(self.counts["entities"]),
            "player": int(self.counts["player"]),
            "player_keys": self.player_keys,
            "log_schema": self.log_schema,
            "log": int(self.counts["log"]),
        }

    def _have_advertise(self) -> bool:
        return all(topic in self._channels for topic in _LAYOUT_TOPICS)

    def _have_payloads(self) -> bool:
        return (
            self.counts["map"] >= 1
            and self.counts["tf"] >= 1
            and self.counts["entities"] >= 1
            and self.counts["player"] >= 1
            and self.counts["log"] >= 1
            and bool(self.map_frame)
            and bool(self.tf_parent)
            and bool(self.tf_child)
            and bool(self.player_keys)
        )

    def _ingest_json(self, msg: dict[str, Any]) -> None:
        if msg.get("op") != "advertise":
            return
        for channel in msg.get("channels") or []:
            if not isinstance(channel, dict):
                continue
            topic = str(channel.get("topic") or "")
            if topic not in _LAYOUT_TOPICS:
                continue
            schema = str(channel.get("schemaName") or channel.get("schema_name") or "")
            self._channels[topic] = {"id": int(channel["id"]), "schema": schema}
            key = _LAYOUT_TOPICS[topic]
            if key == "map":
                self.map_schema = schema
            elif key == "tf":
                self.tf_schema = schema
            elif key == "entities":
                self.entities_schema = schema
            elif key == "log":
                self.log_schema = schema

    def _ingest_bin(self, payload: bytes) -> None:
        parsed = _parse_message_data(payload)
        if parsed is None:
            return
        sub_id, body = parsed
        topic = self._sub_topic.get(sub_id)
        if topic is None:
            return
        key = _LAYOUT_TOPICS[topic]
        self.counts[key] += 1
        if key == "map" and not self.map_frame:
            self.map_frame = _grid_frame_id(body)
        elif key == "tf" and (not self.tf_parent or not self.tf_child):
            parent, child = _tf_parent_child(body)
            if parent:
                self.tf_parent = parent
            if child:
                self.tf_child = child
        elif key == "player" and not self.player_keys:
            try:
                self.player_keys = _player_keys(body)
            except (UnicodeDecodeError, json.JSONDecodeError, ValueError):
                self.player_keys = ""
