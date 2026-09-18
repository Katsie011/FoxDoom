"""ViZDoom engine with a JPEG-producing fallback if ViZDoom cannot import or init."""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Protocol

import numpy as np

from doom_foxglove import SCREEN_HEIGHT, SCREEN_WIDTH
from doom_foxglove.iwad import resolve_iwad
from doom_foxglove.teleop import Command, binary_buttons
from doom_foxglove.world import (
    Entity,
    KIND_PICKUP,
    LogEvent,
    OccupancyGrid,
    PlayerState,
    PoseState,
    WorldState,
    doom_to_m,
    entities_from_objects,
    hollow_room,
    logs_from_delta,
    occupancy_from_lines,
    yaw_from_doom_degrees,
)


class Engine(Protocol):
    backend: str

    def reset(self) -> np.ndarray: ...
    def step(self, command: Command) -> np.ndarray: ...
    def observe(self) -> WorldState: ...
    def close(self) -> None: ...


@dataclass
class EngineInfo:
    backend: str
    iwad: str | None
    map_name: str
    note: str


def _blank_sky() -> np.ndarray:
    frame = np.zeros((SCREEN_HEIGHT, SCREEN_WIDTH, 3), dtype=np.uint8)
    frame[:80, :, :] = (40, 40, 70)
    frame[80:, :, :] = (50, 50, 50)
    return frame


class FallbackEngine:
    """RGB framebuffer published as CompressedImage. Not a host canvas."""

    backend = "fallback"

    def __init__(self) -> None:
        self._x = SCREEN_WIDTH // 2
        self._heading = 0.0
        self._frame = _blank_sky()
        self._tick = 0
        self._map_pending = True
        self._prev_player: PlayerState | None = None
        self._grid = hollow_room("fallback")

    def reset(self) -> np.ndarray:
        self._x = SCREEN_WIDTH // 2
        self._heading = 0.0
        self._tick = 0
        self._map_pending = True
        self._prev_player = None
        return self._draw()

    def step(self, command: Command) -> np.ndarray:
        self._heading += command.angular_z * 8.0
        self._x += int(command.linear_x * 6) + int(command.linear_y * 4)
        self._x = int(max(10, min(SCREEN_WIDTH - 10, self._x)))
        self._tick += 1
        return self._draw(command)

    def observe(self) -> WorldState:
        pose = PoseState(
            x=(self._x / SCREEN_WIDTH) * 10.0,
            y=5.0,
            z=1.4,
            yaw=yaw_from_doom_degrees(self._heading),
        )
        player = PlayerState(
            health=100.0,
            armor=0.0,
            ammo=50.0,
            weapon=2,
            tick=self._tick,
            dead=False,
        )
        logs = logs_from_delta(self._prev_player, player, "fallback")
        self._prev_player = player
        grid: OccupancyGrid | None = None
        if self._map_pending:
            grid = self._grid
            self._map_pending = False
        dummy = Entity(
            id="dummy-imp",
            kind="monster",
            name="DoomImp",
            x=7.0,
            y=5.0,
            z=0.0,
            yaw=0.0,
        )
        return WorldState(
            pose=pose,
            player=player,
            entities=[dummy],
            map_grid=grid,
            logs=logs,
            map_name="fallback",
        )

    def close(self) -> None:
        return None

    def _draw(self, command: Command | None = None) -> np.ndarray:
        frame = _blank_sky()
        x = self._x
        frame[140:180, x - 6 : x + 6, :] = (200, 180, 40)
        # Label so a Foxglove Image panel is obviously not E1M1 if ViZDoom is missing.
        _paint_label(frame, "FALLBACK NO VIZDOOM")
        if command and command.fire:
            frame[100:104, x - 1 : x + 1, :] = (255, 80, 80)
        self._frame = frame
        return frame


def _paint_label(frame: np.ndarray, text: str) -> None:
    # Tiny 3x5 bitmap font for a handful of capitals and digits — enough to read in Image.
    glyphs = {
        "A": [0b010, 0b101, 0b111, 0b101, 0b101],
        "B": [0b110, 0b101, 0b110, 0b101, 0b110],
        "C": [0b011, 0b100, 0b100, 0b100, 0b011],
        "D": [0b110, 0b101, 0b101, 0b101, 0b110],
        "E": [0b111, 0b100, 0b110, 0b100, 0b111],
        "F": [0b111, 0b100, 0b110, 0b100, 0b100],
        "G": [0b011, 0b100, 0b101, 0b101, 0b011],
        "H": [0b101, 0b101, 0b111, 0b101, 0b101],
        "I": [0b111, 0b010, 0b010, 0b010, 0b111],
        "K": [0b101, 0b101, 0b110, 0b101, 0b101],
        "L": [0b100, 0b100, 0b100, 0b100, 0b111],
        "M": [0b101, 0b111, 0b111, 0b101, 0b101],
        "N": [0b101, 0b111, 0b111, 0b101, 0b101],
        "O": [0b010, 0b101, 0b101, 0b101, 0b010],
        "V": [0b101, 0b101, 0b101, 0b101, 0b010],
        "Z": [0b111, 0b001, 0b010, 0b100, 0b111],
        " ": [0, 0, 0, 0, 0],
    }
    col = 4
    row = 6
    for ch in text:
        bits = glyphs.get(ch, glyphs[" "])
        for dy, rowbits in enumerate(bits):
            for dx in range(3):
                if rowbits & (1 << (2 - dx)):
                    yy = row + dy * 2
                    xx = col + dx * 2
                    frame[yy : yy + 2, xx : xx + 2, :] = (240, 240, 240)
        col += 8
        if col > SCREEN_WIDTH - 8:
            break


class VizDoomEngine:
    backend = "vizdoom"

    def __init__(self, game: object, map_name: str) -> None:
        self._game = game
        self._map_name = map_name
        self._button_names: list[str] = []
        self._tick = 0
        self._map_pending = True
        self._cached_grid: OccupancyGrid | None = None
        self._prev_player: PlayerState | None = None
        self._itemcount = 0.0
        self._killcount = 0.0
        self._level_complete = False

    def reset(self) -> np.ndarray:
        game = self._game
        game.new_episode()  # type: ignore[attr-defined]
        self._tick = 0
        self._map_pending = True
        self._cached_grid = None
        self._prev_player = None
        self._itemcount = 0.0
        self._killcount = 0.0
        self._level_complete = False
        return self._screen()

    def step(self, command: Command) -> np.ndarray:
        game = self._game
        if game.is_episode_finished():  # type: ignore[attr-defined]
            dead = bool(self._var("DEAD", 0.0))
            self._level_complete = not dead
            game.new_episode()  # type: ignore[attr-defined]
            self._map_pending = True
            self._prev_player = None
        action = self._action(command)
        game.make_action(action, 1)  # type: ignore[attr-defined]
        self._tick += 1
        return self._screen()

    def observe(self) -> WorldState:
        game = self._game
        pose = PoseState(
            x=doom_to_m(self._var("POSITION_X")),
            y=doom_to_m(self._var("POSITION_Y")),
            z=doom_to_m(self._var("POSITION_Z")),
            yaw=yaw_from_doom_degrees(self._var("ANGLE")),
        )
        player = PlayerState(
            health=self._var("HEALTH", 100.0),
            armor=self._var("ARMOR", 0.0),
            ammo=self._var("SELECTED_WEAPON_AMMO", 0.0),
            weapon=int(self._var("SELECTED_WEAPON", 2.0)),
            tick=self._tick,
            dead=bool(self._var("DEAD", 0.0)),
        )
        logs = logs_from_delta(
            self._prev_player,
            player,
            self._map_name,
            level_complete=self._level_complete,
        )
        self._level_complete = False
        itemcount = self._var("ITEMCOUNT", 0.0)
        killcount = self._var("KILLCOUNT", 0.0)
        if self._prev_player is not None and itemcount > self._itemcount:
            logs.append(LogEvent(message="Picked up an item.", kind=KIND_PICKUP))
        if self._prev_player is not None and killcount > self._killcount:
            logs.append(LogEvent(message="Kill."))
        self._itemcount = itemcount
        self._killcount = killcount
        self._prev_player = player
        entities = entities_from_objects(self._objects())
        grid = None
        if self._map_pending:
            grid = self._occupancy()
            self._cached_grid = grid
            self._map_pending = False
        return WorldState(
            pose=pose,
            player=player,
            entities=entities,
            map_grid=grid,
            logs=logs,
            map_name=self._map_name,
        )

    def _var(self, name: str, default: float = 0.0) -> float:
        try:
            import vizdoom as vzd

            variable = getattr(vzd.GameVariable, name)
            return float(self._game.get_game_variable(variable))  # type: ignore[attr-defined]
        except Exception:
            return default

    def _objects(self) -> list[object]:
        state = self._game.get_state()  # type: ignore[attr-defined]
        if state is None:
            return []
        return list(getattr(state, "objects", None) or [])

    def _occupancy(self) -> OccupancyGrid:
        state = self._game.get_state()  # type: ignore[attr-defined]
        lines: list[object] = []
        sectors = []
        if state is not None:
            sectors = list(getattr(state, "sectors", None) or [])
        for sector in sectors:
            lines.extend(list(getattr(sector, "lines", None) or []))
        if not lines:
            return hollow_room(self._map_name)
        return occupancy_from_lines(lines, self._map_name)

    def close(self) -> None:
        try:
            self._game.close()  # type: ignore[attr-defined]
        except Exception:
            pass

    def _screen(self) -> np.ndarray:
        state = self._game.get_state()  # type: ignore[attr-defined]
        if state is None or state.screen_buffer is None:
            return _blank_sky()
        buf = np.asarray(state.screen_buffer)
        if buf.ndim == 3 and buf.shape[0] in (3, 4):
            buf = np.transpose(buf, (1, 2, 0))
        if buf.dtype != np.uint8:
            buf = np.clip(buf, 0, 255).astype(np.uint8)
        return buf

    def _action(self, command: Command) -> list[int]:
        flags = binary_buttons(command)
        action: list[int] = []
        for name in self._button_names:
            if name.startswith("SELECT_WEAPON") and flags.get("weapon") is not None:
                want = f"SELECT_WEAPON{int(flags['weapon'])}"
                action.append(1 if name == want else 0)
            else:
                action.append(1 if flags.get(name, False) else 0)
        return action


def _configure_vizdoom(game: object, iwad: os.PathLike[str] | str | None) -> tuple[str, list[str]]:
    import vizdoom as vzd

    game.set_window_visible(False)
    game.set_sound_enabled(False)
    game.set_screen_resolution(vzd.ScreenResolution.RES_320X200)
    game.set_screen_format(vzd.ScreenFormat.RGB24)
    game.set_render_hud(True)
    game.set_render_crosshair(False)
    game.set_mode(vzd.Mode.PLAYER)
    game.set_ticrate(35)

    map_name = "E1M1"
    if iwad is not None:
        game.set_doom_game_path(str(iwad))
        lower = str(iwad).lower()
        if "freedoom2" in lower or lower.endswith("doom2.wad"):
            map_name = "MAP01"
            game.set_doom_map("MAP01")
        else:
            game.set_doom_map("E1M1")
    else:
        scenarios = getattr(vzd, "scenarios_path", None)
        cfg = None
        if scenarios:
            for name in ("freedoom1.cfg", "basic.cfg"):
                candidate = os.path.join(scenarios, name)
                if os.path.isfile(candidate):
                    cfg = candidate
                    break
        if cfg:
            game.load_config(cfg)
            try:
                game.set_doom_map("E1M1")
            except Exception:
                map_name = "MAP01"
        else:
            game.set_doom_map("E1M1")

    buttons = [
        vzd.Button.MOVE_FORWARD,
        vzd.Button.MOVE_BACKWARD,
        vzd.Button.MOVE_LEFT,
        vzd.Button.MOVE_RIGHT,
        vzd.Button.TURN_LEFT,
        vzd.Button.TURN_RIGHT,
        vzd.Button.ATTACK,
        vzd.Button.USE,
        vzd.Button.SELECT_WEAPON1,
        vzd.Button.SELECT_WEAPON2,
        vzd.Button.SELECT_WEAPON3,
        vzd.Button.SELECT_WEAPON4,
    ]
    names = [b.name if hasattr(b, "name") else str(b).split(".")[-1] for b in buttons]
    if hasattr(game, "set_available_buttons"):
        game.set_available_buttons(buttons)
    else:
        if hasattr(game, "clear_available_buttons"):
            game.clear_available_buttons()
        for button in buttons:
            game.add_available_button(button)

    if hasattr(game, "set_objects_info_enabled"):
        game.set_objects_info_enabled(True)
    if hasattr(game, "set_sectors_info_enabled"):
        game.set_sectors_info_enabled(True)
    variables = [
        vzd.GameVariable.HEALTH,
        vzd.GameVariable.ARMOR,
        vzd.GameVariable.SELECTED_WEAPON,
        vzd.GameVariable.SELECTED_WEAPON_AMMO,
        vzd.GameVariable.DEAD,
        vzd.GameVariable.ITEMCOUNT,
        vzd.GameVariable.KILLCOUNT,
        vzd.GameVariable.DEATHCOUNT,
        vzd.GameVariable.POSITION_X,
        vzd.GameVariable.POSITION_Y,
        vzd.GameVariable.POSITION_Z,
        vzd.GameVariable.ANGLE,
    ]
    if hasattr(game, "set_available_game_variables"):
        game.set_available_game_variables(variables)
    else:
        for variable in variables:
            game.add_available_game_variable(variable)
    return map_name, names


def try_vizdoom(*, fetch_iwad: bool = False) -> tuple[VizDoomEngine | None, str]:
    try:
        import vizdoom as vzd
    except Exception as exc:
        return None, f"vizdoom import failed: {exc}"

    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    iwad = resolve_iwad(fetch=fetch_iwad)
    game = vzd.DoomGame()
    try:
        map_name, names = _configure_vizdoom(game, iwad)
        game.init()
    except Exception as exc:
        try:
            game.close()
        except Exception:
            pass
        return None, f"vizdoom init failed: {exc}"
    engine = VizDoomEngine(game, map_name)
    engine._button_names = names
    return engine, f"iwad={iwad} map={map_name}"


def make_engine(*, fetch_iwad: bool = False, prefer_vizdoom: bool = True) -> tuple[Engine, EngineInfo]:
    if prefer_vizdoom:
        engine, note = try_vizdoom(fetch_iwad=fetch_iwad)
        if engine is not None:
            iwad = resolve_iwad(fetch=False)
            return engine, EngineInfo(
                backend="vizdoom",
                iwad=str(iwad) if iwad else None,
                map_name=engine._map_name,
                note=note,
            )
        fallback_note = note
    else:
        fallback_note = "vizdoom not requested"
    fallback = FallbackEngine()
    return fallback, EngineInfo(
        backend="fallback",
        iwad=None,
        map_name="none",
        note=fallback_note,
    )
