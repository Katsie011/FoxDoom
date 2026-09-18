"""Publish /doom/map, /tf, /doom/entities, /doom/player, /doom/log, and /doom/events."""

from __future__ import annotations

import math
from typing import Any

from doom_foxglove import (
    BASE_FRAME,
    ENTITIES_TOPIC,
    EVENTS_TOPIC,
    LOG_TOPIC,
    MAP_FRAME,
    MAP_TOPIC,
    PLAYER_TOPIC,
    TF_TOPIC,
)
from doom_foxglove.world import EVENT_KINDS, Entity, LogEvent, OccupancyGrid, PlayerState, PoseState, WorldState

PLAYER_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "health": {"type": "number"},
        "armor": {"type": "number"},
        "ammo": {"type": "number"},
        "weapon": {"type": "integer"},
        "tick": {"type": "integer"},
        "dead": {"type": "boolean"},
    },
    "required": ["health", "armor", "ammo", "weapon", "tick", "dead"],
}

EVENTS_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "kind": {"type": "string"},
        "message": {"type": "string"},
        "tick": {"type": "integer"},
        "map": {"type": "string"},
    },
    "required": ["kind", "message", "tick", "map"],
}

_KIND_COLOR = {
    "monster": (1.0, 0.15, 0.1, 1.0),
    "item": (1.0, 0.85, 0.2, 1.0),
    "projectile": (1.0, 0.45, 0.1, 1.0),
    "other": (0.6, 0.6, 0.65, 1.0),
}
_KIND_SIZE = {
    "monster": 0.8,
    "item": 0.3,
    "projectile": 0.2,
    "other": 0.4,
}


def _fg():
    try:
        from foxglove import messages as m
    except ImportError:
        from foxglove import schemas as m
    return m


def timestamp():
    import time

    m = _fg()
    Timestamp = m.Timestamp
    now = time.time()
    if hasattr(Timestamp, "from_epoch_secs"):
        return Timestamp.from_epoch_secs(now)
    sec = int(now)
    nsec = int((now - sec) * 1_000_000_000)
    try:
        return Timestamp(sec=sec, nsec=nsec)
    except TypeError:
        return Timestamp(sec=sec, nsec=nsec)


def yaw_quaternion(yaw: float):
    m = _fg()
    half = yaw * 0.5
    return m.Quaternion(x=0.0, y=0.0, z=math.sin(half), w=math.cos(half))


def pose_msg(x: float, y: float, z: float, yaw: float = 0.0):
    m = _fg()
    return m.Pose(
        position=m.Vector3(x=x, y=y, z=z),
        orientation=yaw_quaternion(yaw),
    )


def build_grid(grid: OccupancyGrid):
    m = _fg()
    Numeric = m.PackedElementFieldNumericType
    return m.Grid(
        timestamp=timestamp(),
        frame_id=MAP_FRAME,
        pose=pose_msg(grid.origin_x, grid.origin_y, 0.0),
        column_count=grid.columns,
        cell_size=m.Vector2(x=grid.cell_size, y=grid.cell_size),
        row_stride=grid.columns,
        cell_stride=1,
        fields=[m.PackedElementField(name="occupancy", offset=0, type=Numeric.Uint8)],
        data=grid.occupancy,
    )


def build_tf(pose: PoseState):
    m = _fg()
    return m.FrameTransforms(
        transforms=[
            m.FrameTransform(
                timestamp=timestamp(),
                parent_frame_id=MAP_FRAME,
                child_frame_id=BASE_FRAME,
                translation=m.Vector3(x=pose.x, y=pose.y, z=pose.z),
                rotation=yaw_quaternion(pose.yaw),
            )
        ]
    )


def build_entities(entities: list[Entity]):
    m = _fg()
    DeletionType = m.SceneEntityDeletionType
    ts = timestamp()
    cubes: list[Any] = []
    for ent in entities:
        rgba = _KIND_COLOR.get(ent.kind, _KIND_COLOR["other"])
        size = _KIND_SIZE.get(ent.kind, _KIND_SIZE["other"])
        cubes.append(
            m.SceneEntity(
                timestamp=ts,
                frame_id=MAP_FRAME,
                id=f"{ent.kind}:{ent.id}",
                frame_locked=True,
                cubes=[
                    m.CubePrimitive(
                        pose=pose_msg(ent.x, ent.y, ent.z + size * 0.5, ent.yaw),
                        size=m.Vector3(x=size, y=size, z=size),
                        color=m.Color(r=rgba[0], g=rgba[1], b=rgba[2], a=rgba[3]),
                    )
                ],
            )
        )
    return m.SceneUpdate(
        deletions=[m.SceneEntityDeletion(timestamp=ts, type=DeletionType.All, id="")],
        entities=cubes,
    )


def build_log(event: LogEvent):
    m = _fg()
    levels = m.LogLevel
    level = {
        "debug": levels.Debug,
        "info": levels.Info,
        "warning": levels.Warning,
        "error": levels.Error,
        "fatal": levels.Fatal,
    }.get(event.level, levels.Info)
    return m.Log(
        timestamp=timestamp(),
        level=level,
        message=event.message,
        name="doom",
    )


def world_channels() -> dict[str, Any]:
    from foxglove import Channel
    from foxglove.channels import FrameTransformsChannel, GridChannel, LogChannel, SceneUpdateChannel

    return {
        "map": GridChannel(topic=MAP_TOPIC),
        "tf": FrameTransformsChannel(topic=TF_TOPIC),
        "entities": SceneUpdateChannel(topic=ENTITIES_TOPIC),
        "player": Channel(PLAYER_TOPIC, schema=PLAYER_SCHEMA),
        "log": LogChannel(topic=LOG_TOPIC),
        "events": Channel(EVENTS_TOPIC, schema=EVENTS_SCHEMA),
    }


def publish_map(channel: Any, grid: OccupancyGrid) -> dict[str, Any]:
    msg = build_grid(grid)
    encoded = msg.encode()
    channel.log(msg)
    return {
        "frame_id": "map",
        "column_count": grid.columns,
        "rows": grid.rows,
        "bytes": len(grid.occupancy),
        "encoded": len(encoded),
    }


def publish_tf(channel: Any, pose: PoseState) -> dict[str, Any]:
    msg = build_tf(pose)
    encoded = msg.encode()
    channel.log(msg)
    return {
        "parent_frame_id": "map",
        "child_frame_id": "base_link",
        "x": pose.x,
        "y": pose.y,
        "z": pose.z,
        "yaw": pose.yaw,
        "encoded": len(encoded),
    }


def publish_entities(channel: Any, entities: list[Entity]) -> dict[str, Any]:
    msg = build_entities(entities)
    encoded = msg.encode()
    channel.log(msg)
    return {"count": len(entities), "ids": [ent.id for ent in entities], "encoded": len(encoded)}


def publish_player(channel: Any, player: PlayerState) -> dict[str, Any]:
    payload = player.as_json()
    channel.log(payload)
    return payload


def publish_log(channel: Any, event: LogEvent) -> dict[str, Any]:
    msg = build_log(event)
    encoded = msg.encode()
    channel.log(msg)
    return {"message": event.message, "level": event.level, "encoded": len(encoded)}


def event_payload(event: LogEvent, tick: int, map_name: str) -> dict[str, Any]:
    kind = event.kind if event.kind and event.kind != "info" else "info"
    return {
        "kind": kind,
        "message": event.message,
        "tick": int(tick),
        "map": map_name,
    }


def publish_event(channel: Any, event: LogEvent, tick: int, map_name: str) -> dict[str, Any]:
    payload = event_payload(event, tick, map_name)
    channel.log(payload)
    return payload


def publish_world(channels: dict[str, Any], world: WorldState) -> dict[str, Any]:
    tick = world.player.tick
    map_name = world.map_name
    events = [
        publish_event(channels["events"], event, tick, map_name)
        for event in world.logs
        if event.kind in EVENT_KINDS
    ]
    out: dict[str, Any] = {
        "tf": publish_tf(channels["tf"], world.pose),
        "entities": publish_entities(channels["entities"], world.entities),
        "player": publish_player(channels["player"], world.player),
        "logs": [publish_log(channels["log"], event) for event in world.logs],
        "events": events,
        "map": None,
    }
    if world.map_grid is not None:
        out["map"] = publish_map(channels["map"], world.map_grid)
    return out
