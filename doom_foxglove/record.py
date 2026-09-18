"""MCAP sidecar: same foxglove-sdk channel.log() sinks write the live file."""

from __future__ import annotations

import struct
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from doom_foxglove import (
    CAMERA_TOPIC,
    ENTITIES_TOPIC,
    LOG_TOPIC,
    MAP_TOPIC,
    PLAYER_TOPIC,
    TF_TOPIC,
)

MCAP_MAGIC = b"\x89MCAP0\r\n"
OP_CHANNEL = 0x04
OP_MESSAGE = 0x05
OP_MESSAGE_INDEX = 0x07
EXPECTED_TOPICS = (
    CAMERA_TOPIC,
    MAP_TOPIC,
    TF_TOPIC,
    ENTITIES_TOPIC,
    PLAYER_TOPIC,
    LOG_TOPIC,
)


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def recordings_dir(root: Path | None = None) -> Path:
    dest = (root or repo_root()) / "recordings"
    dest.mkdir(parents=True, exist_ok=True)
    return dest


def default_recording_path(root: Path | None = None) -> Path:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    return recordings_dir(root) / f"doom-{stamp}.mcap"


def smoke_recording_path(root: Path | None = None) -> Path:
    return recordings_dir(root) / "smoke.mcap"


def smoke_events_recording_path(root: Path | None = None) -> Path:
    return recordings_dir(root) / "smoke-events.mcap"


def open_recording(path: Path | str, *, allow_overwrite: bool = False) -> Any:
    """Attach an MCAP sink to the same Context the WebSocket server uses."""
    import foxglove

    dest = Path(path)
    dest.parent.mkdir(parents=True, exist_ok=True)
    return foxglove.open_mcap(dest, allow_overwrite=allow_overwrite)


def _read_prefixed_string(payload: bytes, offset: int) -> tuple[str, int]:
    if offset + 4 > len(payload):
        raise ValueError("truncated MCAP string length")
    (n,) = struct.unpack_from("<I", payload, offset)
    start = offset + 4
    end = start + n
    if end > len(payload):
        raise ValueError("truncated MCAP string")
    return payload[start:end].decode("utf-8"), end


def iter_mcap_records(blob: bytes):
    if len(blob) < len(MCAP_MAGIC) * 2 or not blob.startswith(MCAP_MAGIC):
        raise ValueError("not an MCAP file (missing magic)")
    cursor = len(MCAP_MAGIC)
    limit = len(blob) - len(MCAP_MAGIC)
    while cursor + 9 <= limit:
        opcode = blob[cursor]
        (length,) = struct.unpack_from("<Q", blob, cursor + 1)
        cursor += 9
        payload = blob[cursor : cursor + length]
        if len(payload) < length:
            break
        cursor += length
        yield opcode, payload


def list_mcap_topics(path: Path | str) -> set[str]:
    blob = Path(path).read_bytes()
    topics: set[str] = set()
    for opcode, payload in iter_mcap_records(blob):
        if opcode != OP_CHANNEL or len(payload) < 8:
            continue
        topic, _ = _read_prefixed_string(payload, 4)
        topics.add(topic)
    return topics


def count_mcap_messages(path: Path | str, topic: str) -> int:
    """Count messages for a topic via MessageIndex (chunked MCAPs have no top-level Message records)."""
    blob = Path(path).read_bytes()
    channel_ids: set[int] = set()
    for opcode, payload in iter_mcap_records(blob):
        if opcode != OP_CHANNEL or len(payload) < 8:
            continue
        channel_id = struct.unpack_from("<H", payload, 0)[0]
        name, _ = _read_prefixed_string(payload, 4)
        if name == topic:
            channel_ids.add(channel_id)
    if not channel_ids:
        return 0
    count = 0
    for opcode, payload in iter_mcap_records(blob):
        if opcode == OP_MESSAGE and len(payload) >= 2:
            channel_id = struct.unpack_from("<H", payload, 0)[0]
            if channel_id in channel_ids:
                count += 1
            continue
        if opcode != OP_MESSAGE_INDEX or len(payload) < 6:
            continue
        channel_id = struct.unpack_from("<H", payload, 0)[0]
        if channel_id not in channel_ids:
            continue
        (nbytes,) = struct.unpack_from("<I", payload, 2)
        count += nbytes // 16
    return count
