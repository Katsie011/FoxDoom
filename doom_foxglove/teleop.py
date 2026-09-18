"""Map Foxglove Teleop Twist and /doom/buttons JSON onto ViZDoom-style commands."""

from __future__ import annotations

import json
from dataclasses import dataclass, replace
from typing import Any

from doom_foxglove import BUTTONS_TOPIC, CMD_VEL_TOPIC

DEADZONE = 0.05


@dataclass(frozen=True)
class Command:
    linear_x: float = 0.0
    linear_y: float = 0.0
    angular_z: float = 0.0
    fire: bool = False
    use: bool = False
    weapon: int | None = None

    def stopped(self) -> bool:
        return (
            abs(self.linear_x) < DEADZONE
            and abs(self.linear_y) < DEADZONE
            and abs(self.angular_z) < DEADZONE
            and not self.fire
            and not self.use
            and self.weapon is None
        )


def _num(value: Any, default: float = 0.0) -> float:
    if value is None:
        return default
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def command_from_twist_dict(payload: dict[str, Any], base: Command | None = None) -> Command:
    current = base or Command()
    linear = payload.get("linear") or {}
    angular = payload.get("angular") or {}
    if not isinstance(linear, dict):
        linear = {}
    if not isinstance(angular, dict):
        angular = {}
    return replace(
        current,
        linear_x=_num(linear.get("x")),
        linear_y=_num(linear.get("y")),
        angular_z=_num(angular.get("z")),
    )


def command_from_buttons_dict(payload: dict[str, Any], base: Command | None = None) -> Command:
    current = base or Command()
    weapon = payload.get("weapon")
    weapon_i: int | None
    try:
        weapon_i = int(weapon) if weapon not in (None, "", False) else None
    except (TypeError, ValueError):
        weapon_i = None
    fire = payload.get("fire")
    use = payload.get("use")
    return replace(
        current,
        fire=bool(fire) if fire not in (None, "") else current.fire,
        use=bool(use) if use not in (None, "") else current.use,
        weapon=weapon_i,
    )


def parse_client_json(data: bytes) -> dict[str, Any]:
    text = data.decode("utf-8")
    obj = json.loads(text)
    if not isinstance(obj, dict):
        raise ValueError("client JSON must be an object")
    return obj


def apply_topic(topic: str, data: bytes, current: Command) -> Command:
    payload = parse_client_json(data)
    if topic == CMD_VEL_TOPIC:
        return command_from_twist_dict(payload, current)
    if topic == BUTTONS_TOPIC:
        return command_from_buttons_dict(payload, current)
    return current


def binary_buttons(command: Command) -> dict[str, bool | int | None]:
    """Sign-thresholded button map. ROS +angular.z is CCW (turn left)."""
    return {
        "MOVE_FORWARD": command.linear_x > DEADZONE,
        "MOVE_BACKWARD": command.linear_x < -DEADZONE,
        "MOVE_LEFT": command.linear_y > DEADZONE,
        "MOVE_RIGHT": command.linear_y < -DEADZONE,
        "TURN_LEFT": command.angular_z > DEADZONE,
        "TURN_RIGHT": command.angular_z < -DEADZONE,
        "ATTACK": bool(command.fire),
        "USE": bool(command.use),
        "weapon": command.weapon,
    }
