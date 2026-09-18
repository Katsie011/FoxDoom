"""World snapshot: occupancy, pose, entities, player HUD, and log events."""

from __future__ import annotations

import math
from dataclasses import dataclass, field

from doom_foxglove import DOOM_UNITS_PER_METER

OCCUPIED = 100
FREE = 0
DEFAULT_CELL_M = 0.5
MAX_GRID_DIM = 256

_PLAYER_NAMES = frozenset({"doomplayer", "player"})
_PROJECTILE_PARTS = (
    "ball",
    "missile",
    "puff",
    "tracer",
    "plasmaball",
    "bfgball",
    "fireball",
)
_MONSTER_PARTS = (
    "zombie",
    "shotgunguy",
    "chaingunguy",
    "imp",
    "demon",
    "spectre",
    "cacodemon",
    "baron",
    "lostsoul",
    "hellknight",
    "revenant",
    "mancubus",
    "arachnotron",
    "archvile",
    "spidermastermind",
    "cyberdemon",
    "wolfenstein",
    "ssnazi",
    "formerhuman",
    "formersergeant",
    "formercommando",
    "painelemental",
    "pinky",
)
_ITEM_PARTS = (
    "health",
    "stim",
    "medikit",
    "armor",
    "clip",
    "shell",
    "ammo",
    "cell",
    "shotgun",
    "chaingun",
    "plasma",
    "bfg",
    "chainsaw",
    "pistol",
    "backpack",
    "key",
    "skull",
    "bonus",
    "soulsphere",
    "megasphere",
    "invuln",
    "invis",
    "berserk",
    "rad",
    "goggles",
    "rocketammo",
    "rocketbox",
)
_WEAPON_NAMES = {
    1: "fist",
    2: "pistol",
    3: "shotgun",
    4: "chaingun",
    5: "rocket launcher",
    6: "plasma rifle",
    7: "BFG",
    8: "chainsaw",
}


@dataclass(frozen=True)
class PoseState:
    x: float
    y: float
    z: float
    yaw: float


@dataclass(frozen=True)
class Entity:
    id: str
    kind: str
    name: str
    x: float
    y: float
    z: float
    yaw: float


@dataclass(frozen=True)
class OccupancyGrid:
    origin_x: float
    origin_y: float
    cell_size: float
    columns: int
    rows: int
    occupancy: bytes
    map_id: str


@dataclass(frozen=True)
class PlayerState:
    health: float
    armor: float
    ammo: float
    weapon: int
    tick: int
    dead: bool

    def as_json(self) -> dict:
        return {
            "health": self.health,
            "armor": self.armor,
            "ammo": self.ammo,
            "weapon": self.weapon,
            "tick": self.tick,
            "dead": self.dead,
        }


KIND_LEVEL = "level"
KIND_DEATH = "death"
KIND_WEAPON = "weapon"
KIND_PICKUP = "pickup"
EVENT_KINDS = (KIND_LEVEL, KIND_DEATH, KIND_WEAPON, KIND_PICKUP)


@dataclass(frozen=True)
class LogEvent:
    message: str
    level: str = "info"
    kind: str = "info"


@dataclass
class WorldState:
    pose: PoseState
    player: PlayerState
    entities: list[Entity] = field(default_factory=list)
    map_grid: OccupancyGrid | None = None
    logs: list[LogEvent] = field(default_factory=list)
    map_name: str = ""


def doom_to_m(value: float) -> float:
    return float(value) / DOOM_UNITS_PER_METER


def yaw_from_doom_degrees(angle_deg: float) -> float:
    return math.radians(float(angle_deg))


def classify_entity(name: str) -> str:
    n = name.lower().replace(" ", "").replace("_", "")
    if n in _PLAYER_NAMES:
        return "player"
    if any(part in n for part in _PROJECTILE_PARTS):
        return "projectile"
    if n == "rocket" or (n.endswith("rocket") and "ammo" not in n and "box" not in n):
        return "projectile"
    if any(part in n for part in _MONSTER_PARTS):
        return "monster"
    if any(part in n for part in _ITEM_PARTS):
        return "item"
    return "other"


def weapon_name(weapon: int) -> str:
    return _WEAPON_NAMES.get(int(weapon), f"weapon {int(weapon)}")


def hollow_room(map_id: str, size_m: float = 10.0, cell_size: float = 0.5) -> OccupancyGrid:
    columns = max(4, int(round(size_m / cell_size)))
    rows = columns
    data = bytearray(columns * rows)
    for y in range(rows):
        for x in range(columns):
            if x == 0 or y == 0 or x == columns - 1 or y == rows - 1:
                data[y * columns + x] = OCCUPIED
    return OccupancyGrid(
        origin_x=0.0,
        origin_y=0.0,
        cell_size=cell_size,
        columns=columns,
        rows=rows,
        occupancy=bytes(data),
        map_id=map_id,
    )


def occupancy_from_lines(
    lines: list[object],
    map_id: str,
    cell_size: float = DEFAULT_CELL_M,
) -> OccupancyGrid:
    segs: list[tuple[float, float, float, float]] = []
    xs: list[float] = []
    ys: list[float] = []
    for line in lines:
        if not getattr(line, "is_blocking", True):
            continue
        x1 = doom_to_m(getattr(line, "x1", 0.0))
        y1 = doom_to_m(getattr(line, "y1", 0.0))
        x2 = doom_to_m(getattr(line, "x2", 0.0))
        y2 = doom_to_m(getattr(line, "y2", 0.0))
        segs.append((x1, y1, x2, y2))
        xs.extend((x1, x2))
        ys.extend((y1, y2))
    if not segs:
        return hollow_room(map_id)
    pad = cell_size * 2
    min_x = min(xs) - pad
    max_x = max(xs) + pad
    min_y = min(ys) - pad
    max_y = max(ys) + pad
    columns = max(2, int(math.ceil((max_x - min_x) / cell_size)))
    rows = max(2, int(math.ceil((max_y - min_y) / cell_size)))
    if columns > MAX_GRID_DIM or rows > MAX_GRID_DIM:
        scale = max(columns / MAX_GRID_DIM, rows / MAX_GRID_DIM)
        cell_size *= scale
        columns = max(2, int(math.ceil((max_x - min_x) / cell_size)))
        rows = max(2, int(math.ceil((max_y - min_y) / cell_size)))
    data = bytearray(columns * rows)
    for x1, y1, x2, y2 in segs:
        _rasterize(data, columns, rows, min_x, min_y, cell_size, x1, y1, x2, y2)
    return OccupancyGrid(
        origin_x=min_x,
        origin_y=min_y,
        cell_size=cell_size,
        columns=columns,
        rows=rows,
        occupancy=bytes(data),
        map_id=map_id,
    )


def _rasterize(
    data: bytearray,
    columns: int,
    rows: int,
    origin_x: float,
    origin_y: float,
    cell: float,
    x1: float,
    y1: float,
    x2: float,
    y2: float,
) -> None:
    gx1 = (x1 - origin_x) / cell
    gy1 = (y1 - origin_y) / cell
    gx2 = (x2 - origin_x) / cell
    gy2 = (y2 - origin_y) / cell
    steps = max(int(abs(gx2 - gx1)), int(abs(gy2 - gy1)), 1)
    for i in range(steps + 1):
        t = i / steps
        gx = int(round(gx1 + t * (gx2 - gx1)))
        gy = int(round(gy1 + t * (gy2 - gy1)))
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                xx, yy = gx + dx, gy + dy
                if 0 <= xx < columns and 0 <= yy < rows:
                    data[yy * columns + xx] = OCCUPIED


def entities_from_objects(objects: list[object]) -> list[Entity]:
    out: list[Entity] = []
    for obj in objects:
        name = str(getattr(obj, "name", "object"))
        kind = classify_entity(name)
        if kind == "player":
            continue
        ident = getattr(obj, "id", None)
        eid = str(ident) if ident is not None else f"{name}-{len(out)}"
        out.append(
            Entity(
                id=eid,
                kind=kind,
                name=name,
                x=doom_to_m(getattr(obj, "position_x", 0.0)),
                y=doom_to_m(getattr(obj, "position_y", 0.0)),
                z=doom_to_m(getattr(obj, "position_z", 0.0)),
                yaw=yaw_from_doom_degrees(getattr(obj, "angle", 0.0)),
            )
        )
    return out


def logs_from_delta(
    prev: PlayerState | None,
    current: PlayerState,
    map_name: str,
    *,
    level_complete: bool = False,
) -> list[LogEvent]:
    events: list[LogEvent] = []
    if level_complete:
        events.append(LogEvent(message=f"Level complete: {map_name}", kind=KIND_LEVEL))
    if prev is None:
        events.append(LogEvent(message=f"Entering {map_name}", kind=KIND_LEVEL))
        return events
    if current.dead and not prev.dead:
        events.append(LogEvent(message="You died.", level="error", kind=KIND_DEATH))
    if (not current.dead) and prev.dead:
        events.append(LogEvent(message=f"Entering {map_name}", kind=KIND_LEVEL))
    if current.weapon != prev.weapon:
        events.append(
            LogEvent(
                message=f"You got the {weapon_name(current.weapon)}!",
                kind=KIND_WEAPON,
            )
        )
    if current.armor > prev.armor + 0.5:
        events.append(LogEvent(message="Picked up armor.", kind=KIND_PICKUP))
    elif current.ammo > prev.ammo + 0.5:
        events.append(LogEvent(message="Picked up ammo.", kind=KIND_PICKUP))
    elif current.health > prev.health + 0.5 and not prev.dead:
        events.append(LogEvent(message="Picked up a health item.", kind=KIND_PICKUP))
    return events
