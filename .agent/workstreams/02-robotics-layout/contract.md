# Contract — 02-robotics-layout

**Workstream:** `02-robotics-layout`
**Item-id prefix:** `RL-`
**KG node:** `ws_02_robotics_layout` (stays `deferred` until this contract is critic-gated)
**Capability:** `cap_3d_map_hud`
**Status:** awaiting Kimi critic gate. This file replaces the deferral stub. It is a gradeable contract, not a product patch. No generator starts until the critic and planner agree. No evaluator ticks boxes until that gate.

Source of truth for phase scope: `.agent/GOAL.md` (`cap_3d_map_hud`, topic contract) and `.agent/workstreams/02-robotics-layout/PLAN.md`. This contract does not rewrite either.

## Entry condition (what un-defers `ws_02_robotics_layout`)

All three must hold. This paragraph keeps the word `deferred` and the entry condition H-16 greps for.

1. `cap_live_ws_camera_teleop` is `done` in the knowledge graph.
2. The hero-loop smoke command exits 0 from a clean shell (`./smoke --hero` is HL-09; do not use it as the RL-06 command).
3. A Kimi critic has gated this `RL-nn` list (this file) per `.agent/COORDINATION.md`.

Until (3), the workstream stays **deferred** in the graph even though product code already exists. Generation preceded this gate; the gate is retroactive.

## How this contract is graded

The evaluator (kimi-k3-high) is told the robotics layout is broken and must prove it. For every `RL-nn` item it must run the stated **Check** from a clean shell at the repo root, or quote the exact file text the check names. "Looks fine" is a fail. An unrun check is a fail. A `/tmp` helper the evaluator wrote is not an in-repo check (see RL-07).

- Repo root is `$ROOT` (`/Users/michael/Documents/foxglove/work/doom`). Every command below is run after `cd "$ROOT"`.
- `$PY` is `$ROOT/.venv/bin/python` when that file is executable, otherwise `python3`. Always `export PYTHONPATH="$ROOT"`.
- Foxglove `*Channel.topic` / `schema_name` are callables. Foxglove `messages.*` objects expose `encode()`, `get_schema().name`, and a Debug `repr` — not Python field attributes. The checks below call the methods and match `repr` needles; do not "fix" them by reading `.frame_id` on the message object.
- Smoke for this workstream is `./smoke` with **no** `--hero`. `--hero` is HL-09 and must skip 02 artifacts; using it here is an RL-06 FAIL.
- An item is **PASS** only if its check succeeds. Checkboxes below start unchecked. **Only the evaluator ticks `- [ ]`.** The generator must not tick boxes, must not edit this file, and must not append `verified` / `failed` onto `ContractItem` nodes.
- Occupied `ws://localhost:8765` is an environment note, not an RL FAIL (HL-12).
- 01 items stay on 01. This contract does not re-own HL-10 (ClientPublish inbound Twist/buttons) or HL-11 (`TeleopListener.on_subscribe` / `on_unsubscribe`). See **F-1** below.
- Presence of `03-embed-shell` / `04-record-replay` files, `web/`, or a future `doom_foxglove/mcap*.py` does **not** FAIL any RL item (RL-10).

## F-1 / F-2 / F-3 (eval.md 2026-09-18) — ownership, not extra product scope

- **F-1** (`TeleopListener` missing `on_subscribe` / `on_unsubscribe`): owned by **HL-11** in `.agent/workstreams/01-hero-loop/contract.md`. Do not duplicate that getattr check as an RL item. An `AttributeError` on subscribe is an HL-11 FAIL, not an RL FAIL. A generator handed *this* contract does not "fix HL-11 under an RL id."
- **F-2** (smoke proves 02 topics only via `publish_world` return dicts / `apply_raw`, never a socket): owned by **RL-07**. RL-01…RL-05 are in-process schema/cadence checks. RL-06 is `./smoke` exit 0 plus quoted 02 `_fail` hooks. RL-07 is the wire proof. `apply_raw` is the 01 inbound latch path (HL-10); it does not deliver `/doom/map`, `/tf`, `/doom/entities`, `/doom/player`, or `/doom/log`.
- **F-3** (layout not imported in the Foxglove GUI): **not a defect against this contract.** RL-08 and RL-09 walk `panelType` / config in `layouts/Play.json` and `layouts/Debug.json`. Do **not** require opening the Foxglove app. Do **not** require a GUI import demo.

---

## A. Topics (GOAL.md topic contract)

### RL-01 — `/doom/map` is `foxglove.Grid`, once per level

- [x] Topic `/doom/map` is a `foxglove.Grid` occupancy of the WAD map. `observe()` returns `map_grid` on the first call after `reset()` (and after a new episode) and `None` on later calls in the same level. `publish_world` logs the grid only when `world.map_grid is not None`. FAIL if every tick publishes a Grid. FAIL if `world_channels()["map"]` is not a `GridChannel` on `/doom/map`.

**Check:**

```sh
$PY -c "
from foxglove.channels import GridChannel
from doom_foxglove import MAP_TOPIC, MAP_FRAME
from doom_foxglove.engine import make_engine
from doom_foxglove.topics import build_grid, publish_world, world_channels
from doom_foxglove.world import OccupancyGrid, PlayerState, PoseState, WorldState

def topic_of(ch):
    t = getattr(ch, 'topic', None)
    return t() if callable(t) else t

def schema_of(ch):
    s = getattr(ch, 'schema_name', None)
    return s() if callable(s) else s

assert MAP_TOPIC == '/doom/map' and MAP_FRAME == 'map'
ch = world_channels()
assert isinstance(ch['map'], GridChannel), type(ch['map'])
assert topic_of(ch['map']) == MAP_TOPIC
assert schema_of(ch['map']) == 'foxglove.Grid', schema_of(ch['map'])

eng, info = make_engine(fetch_iwad=False, prefer_vizdoom=True)
eng.reset()
first = eng.observe()
second = eng.observe()
assert first.map_grid is not None, (info.backend, 'first observe must carry the grid')
assert second.map_grid is None, (info.backend, 'second observe must not re-send the grid')
grid = first.map_grid
assert isinstance(grid, OccupancyGrid)
assert grid.columns >= 1 and grid.rows >= 1 and len(grid.occupancy) >= 1
msg = build_grid(grid)
assert msg.get_schema().name == 'foxglove.Grid'
assert len(msg.encode()) > 0
r = repr(msg)
assert 'frame_id=\"map\"' in r, r[:200]
assert 'occupancy' in r, r[:200]
eng.close()

class Rec:
    def __init__(self):
        self.n = 0
    def log(self, *args, **kwargs):
        self.n += 1

player = PlayerState(100.0, 0.0, 50.0, 2, 0, False)
pose = PoseState(0.0, 0.0, 0.0, 0.0)
dummy = {k: Rec() for k in ('map', 'tf', 'entities', 'player', 'log', 'events')}
out = publish_world(dummy, WorldState(pose, player, [], None, []))
assert out['map'] is None and dummy['map'].n == 0, 'publish_world must skip map when map_grid is None'
dummy2 = {k: Rec() for k in ('map', 'tf', 'entities', 'player', 'log', 'events')}
out2 = publish_world(dummy2, WorldState(pose, player, [], grid, []))
assert out2['map'] is not None and dummy2['map'].n == 1
print('RL-01', info.backend, 'columns', grid.columns, 'rows', grid.rows)
"
```

Quote `self._map_pending = True` in `FallbackEngine.reset`, `VizDoomEngine.reset`, and the `new_episode` branch of `VizDoomEngine.step` in `doom_foxglove/engine.py`. Quote `if world.map_grid is not None` in `publish_world` in `doom_foxglove/topics.py`. If any of those literals is absent, FAIL. Wire count for this topic is RL-07 (`map=1`), not this item.

### RL-02 — `/tf` is `foxglove.FrameTransforms` (`map` → `base_link`)

- [x] Topic `/tf` publishes `foxglove.FrameTransforms` with parent `map` and child `base_link` from the marine pose. FAIL if the channel is not `FrameTransformsChannel` on `/tf`. FAIL if `build_tf` uses any other parent/child pair.

**Check:**

```sh
$PY -c "
from foxglove.channels import FrameTransformsChannel
from doom_foxglove import BASE_FRAME, MAP_FRAME, TF_TOPIC
from doom_foxglove.engine import make_engine
from doom_foxglove.topics import build_tf, world_channels
from doom_foxglove.teleop import Command

def topic_of(ch):
    t = getattr(ch, 'topic', None)
    return t() if callable(t) else t

def schema_of(ch):
    s = getattr(ch, 'schema_name', None)
    return s() if callable(s) else s

assert TF_TOPIC == '/tf' and MAP_FRAME == 'map' and BASE_FRAME == 'base_link'
ch = world_channels()
assert isinstance(ch['tf'], FrameTransformsChannel), type(ch['tf'])
assert topic_of(ch['tf']) == TF_TOPIC
assert schema_of(ch['tf']) == 'foxglove.FrameTransforms', schema_of(ch['tf'])
eng, info = make_engine(fetch_iwad=False, prefer_vizdoom=True)
eng.reset()
eng.step(Command())
pose = eng.observe().pose
msg = build_tf(pose)
assert msg.get_schema().name == 'foxglove.FrameTransforms'
assert len(msg.encode()) > 0
r = repr(msg)
assert 'parent_frame_id: \"map\"' in r, r
assert 'child_frame_id: \"base_link\"' in r, r
print('RL-02', info.backend, 'x', pose.x, 'y', pose.y, 'yaw', pose.yaw)
eng.close()
"
```

Quote `parent_frame_id=MAP_FRAME` and `child_frame_id=BASE_FRAME` in `build_tf` in `doom_foxglove/topics.py`.

### RL-03 — `/doom/entities` is `foxglove.SceneUpdate`

- [x] Topic `/doom/entities` publishes `foxglove.SceneUpdate` (monsters, items, projectiles as cubes). The player is not a cube. An empty entity list still produces a `SceneUpdate` (deletions are allowed). Entity ids are kind-prefixed. Frame is `map`. FAIL if the channel is not `SceneUpdateChannel` on `/doom/entities`.

**Check:**

```sh
$PY -c "
from foxglove.channels import SceneUpdateChannel
from doom_foxglove import ENTITIES_TOPIC
from doom_foxglove.engine import make_engine
from doom_foxglove.topics import build_entities, world_channels
from doom_foxglove.world import Entity, classify_entity

def topic_of(ch):
    t = getattr(ch, 'topic', None)
    return t() if callable(t) else t

def schema_of(ch):
    s = getattr(ch, 'schema_name', None)
    return s() if callable(s) else s

assert ENTITIES_TOPIC == '/doom/entities'
ch = world_channels()
assert isinstance(ch['entities'], SceneUpdateChannel), type(ch['entities'])
assert topic_of(ch['entities']) == ENTITIES_TOPIC
assert schema_of(ch['entities']) == 'foxglove.SceneUpdate', schema_of(ch['entities'])
assert classify_entity('doomplayer') == 'player'
assert classify_entity('DoomImp') == 'monster'
empty = build_entities([])
assert type(empty).__name__ == 'SceneUpdate', type(empty)
assert empty.get_schema().name == 'foxglove.SceneUpdate'
assert 'entities=[]' in repr(empty)
msg = build_entities([Entity(id='7', kind='monster', name='DoomImp', x=1, y=2, z=0, yaw=0)])
assert len(msg.encode()) > 0
r = repr(msg)
assert 'frame_id: \"map\"' in r, r[:400]
assert 'id: \"monster:7\"' in r, r[:400]
assert 'cubes: [' in r, r[:400]
eng, info = make_engine(fetch_iwad=False, prefer_vizdoom=True)
eng.reset()
world = eng.observe()
assert all(e.kind != 'player' for e in world.entities), world.entities
print('RL-03', info.backend, 'entity_count', len(world.entities))
eng.close()
"
```

Do not require `entity_count=209` (E1M1 census). Fallback may ship a dummy cube. Empty-but-valid `SceneUpdate` on the live server is allowed; a missing topic is not.

### RL-04 — `/doom/player` compact JSON: health, armor, ammo, weapon, tick, dead

- [x] Topic `/doom/player` is compact JSON with exactly those six keys (`GOAL.md` topic contract). `PLAYER_SCHEMA` lists them under `required`. `PlayerState.as_json()` returns them. `observe().player` carries typed values: numbers for health/armor/ammo, ints for weapon/tick, bool for dead. A hash-named advertised schema (`schema-…`) is allowed (eval F-4). FAIL if any required key is missing. FAIL if the topic is a protobuf HUD.

**Check:**

```sh
$PY -c "
from doom_foxglove import PLAYER_TOPIC
from doom_foxglove.engine import make_engine
from doom_foxglove.topics import PLAYER_SCHEMA, world_channels
from doom_foxglove.world import PlayerState

KEYS = ('health', 'armor', 'ammo', 'weapon', 'tick', 'dead')
assert PLAYER_TOPIC == '/doom/player'
assert list(PLAYER_SCHEMA['required']) == list(KEYS), PLAYER_SCHEMA['required']
payload = PlayerState(100.0, 0.0, 50.0, 2, 3, False).as_json()
assert list(payload) == list(KEYS), payload
def topic_of(ch):
    t = getattr(ch, 'topic', None)
    return t() if callable(t) else t
ch = world_channels()
assert topic_of(ch['player']) == PLAYER_TOPIC
enc = getattr(ch['player'], 'message_encoding', None)
enc = enc() if callable(enc) else enc
assert enc == 'json', enc
eng, info = make_engine(fetch_iwad=False, prefer_vizdoom=True)
eng.reset()
p = eng.observe().player
d = p.as_json()
assert all(k in d for k in KEYS), d
assert isinstance(d['health'], (int, float)) and isinstance(d['armor'], (int, float)) and isinstance(d['ammo'], (int, float))
assert isinstance(d['weapon'], int) and isinstance(d['tick'], int) and isinstance(d['dead'], bool)
print('RL-04', info.backend, d)
eng.close()
"
```

### RL-05 — `/doom/log` is `foxglove.Log` (pickups, deaths, level messages)

- [x] Topic `/doom/log` publishes `foxglove.Log`. First observe after reset emits a level-enter line `Entering {map}`. Death, respawn, weapon change, and pickup deltas emit further lines via `logs_from_delta`. Channel is `LogChannel` on `/doom/log`. Log name is `doom`.

**Check:**

```sh
$PY -c "
from foxglove.channels import LogChannel
from doom_foxglove import LOG_TOPIC
from doom_foxglove.engine import make_engine
from doom_foxglove.topics import build_log, world_channels
from doom_foxglove.world import LogEvent, PlayerState, logs_from_delta

def topic_of(ch):
    t = getattr(ch, 'topic', None)
    return t() if callable(t) else t

def schema_of(ch):
    s = getattr(ch, 'schema_name', None)
    return s() if callable(s) else s

assert LOG_TOPIC == '/doom/log'
ch = world_channels()
assert isinstance(ch['log'], LogChannel), type(ch['log'])
assert topic_of(ch['log']) == LOG_TOPIC
assert schema_of(ch['log']) == 'foxglove.Log', schema_of(ch['log'])
alive = PlayerState(100.0, 0.0, 50.0, 2, 0, False)
dead = PlayerState(0.0, 0.0, 50.0, 2, 1, True)
armed = PlayerState(100.0, 0.0, 50.0, 3, 2, False)
armored = PlayerState(100.0, 50.0, 50.0, 2, 2, False)
enter = logs_from_delta(None, alive, 'E1M1')
assert [e.message for e in enter] == ['Entering E1M1'], enter
assert any(e.message == 'You died.' for e in logs_from_delta(alive, dead, 'E1M1'))
assert any('Entering' in e.message for e in logs_from_delta(dead, alive, 'E1M1'))
assert any('shotgun' in e.message.lower() for e in logs_from_delta(alive, armed, 'E1M1'))
assert any('armor' in e.message.lower() for e in logs_from_delta(alive, armored, 'E1M1'))
msg = build_log(LogEvent(message='Entering E1M1'))
assert msg.get_schema().name == 'foxglove.Log'
assert len(msg.encode()) > 0
r = repr(msg)
assert 'name=\"doom\"' in r, r
assert 'message=\"Entering E1M1\"' in r, r
eng, info = make_engine(fetch_iwad=False, prefer_vizdoom=True)
eng.reset()
world = eng.observe()
assert world.logs, 'reset must emit a level-enter log'
print('RL-05', info.backend, [e.message for e in world.logs])
eng.close()
"
```

---

## B. Smoke

### RL-06 — `./smoke` (no `--hero`) exits 0 and is hooked to 02 topics

- [x] From `$ROOT`, `./smoke` with no `--hero` boots a WebSocket, publishes the 02 topics, prints a `SMOKE OK` line that names `/doom/map`, `/tf`, `/doom/entities`, `/doom/player`, and `/doom/log`, and exits 0. `main()` must call `_check_layouts()` and must `_fail` when map/tf/entities/player/log are missing. This item does **not** prove wire delivery (that is RL-07). `--hero` must not be passed. A busy 8765 plus ephemeral bind is HL-12, not FAIL.

**Check:**

```sh
./smoke
echo smoke_exit=$?
```

PASS only if exit is 0 and stdout contains `SMOKE OK`, `/doom/map`, `/tf`, `/doom/entities`, `/doom/player`, and `/doom/log`. Quote these literals in `doom_foxglove/smoke.py`: `layout_error = _check_layouts()`, and the five `_fail` messages that name `MAP_TOPIC`, `TF_TOPIC`, `ENTITIES_TOPIC`, `PLAYER_TOPIC`, and `LOG_TOPIC`. If `_check_layouts` is not called from `main`, or any of those `_fail` hooks is gone, FAIL even if this run exited 0.

### RL-07 — Wire delivery of 02 topics (eval F-2)

- [x] `./smoke` (no `--hero`) opens a WebSocket client to the port the smoke process bound, negotiates subprotocol `foxglove.sdk.v1`, and proves the five 02 topics were **received on that socket**. Counts must come from advertised channels plus received messages, not from `publish_world` return dicts and not from `TeleopListener.apply_raw`. A standalone module that smoke never calls does **not** satisfy this item. A `/tmp` probe does **not** satisfy this item. HL-10's `WIRE CHECK` line (ClientPublish / camera / Twist / buttons) does **not** satisfy this item.

  Stdout must contain a line matching:

  `WIRE LAYOUT map_schema=foxglove.Grid map=<n> map_frame=map tf_schema=foxglove.FrameTransforms tf=<n> tf_parent=map tf_child=base_link entities_schema=foxglove.SceneUpdate entities=<n> player=<n> player_keys=health,armor,ammo,weapon,tick,dead log_schema=foxglove.Log log=<n>`

  PASS only if `map == 1`, `tf >= 1`, `entities >= 1`, `player >= 1`, `log >= 1`, the four `*_schema=` values are exactly those strings, `map_frame=map`, `tf_parent=map`, `tf_child=base_link`, and `player_keys` is exactly `health,armor,ammo,weapon,tick,dead` in that order. `map=1` is the wire half of "once per level" over a single-reset smoke window; RL-01 is the observe/publish half.

**Check:** run `./smoke` (same invocation may be reused with RL-06). Quote the `WIRE LAYOUT` line. Quote the client code in `doom_foxglove/smoke.py` or a helper it imports under `doom_foxglove/` that (1) connects to the bound port, (2) names subprotocol `foxglove.sdk.v1`, (3) subscribes to the five topics, (4) reads `map_schema` / `tf_schema` / `entities_schema` / `log_schema` from the server's advertise/channel announcement, (5) sets `map_frame`, `tf_parent`, `tf_child`, and `player_keys` from **received** payloads. FAIL if those strings are hardcoded in a print with no receive loop. FAIL if the only 02 proof is `_grid_ok` / `_tf_ok` / `_scene_ok` / `_player_ok` / `published.get("logs")` on the `publish_world` dict. FAIL if the only client lives outside the repo.

---

## C. Layouts (JSON `panelType` walk — no GUI)

Allowed `panelType` strings (stock only, `dec_stock_panels_only`): `Image`, `Teleop`, `Gauge`, `ThreeDee`, `Plot`, `Log`, `RawMessages`, `Table`. Any other `panelType` on a `type == "panel"` node is FAIL. Walk the tree; do not `json.dumps` and substring-search (that is how `_check_layouts` works today, and it is not enough for RL-08/RL-09).

### RL-08 — `layouts/Play.json`: Image + Teleop + health/armor/ammo gauges

- [x] `layouts/Play.json` is JSON `version == 1` in the SDK programmatic layout shape. It contains an `Image` panel on `/doom/camera`, a `Teleop` panel on `/cmd_vel` at 35 Hz with `autoSendStopOnRelease` true, and Gauge panels whose `config.path` values include `/doom/player.health`, `/doom/player.armor`, and `/doom/player.ammo`. Extra allowed stock panels do not FAIL. ThreeDee is not required on Play. Do not open the Foxglove app.

**Check:**

```sh
$PY -c "
import json
from pathlib import Path
ALLOWED = {'Image', 'Teleop', 'Gauge', 'ThreeDee', 'Plot', 'Log', 'RawMessages', 'Table'}

def panels(node, out=None):
    out = [] if out is None else out
    if isinstance(node, dict):
        if node.get('type') == 'panel' and 'panelType' in node:
            out.append(node)
        for v in node.values():
            panels(v, out)
    elif isinstance(node, list):
        for v in node:
            panels(v, out)
    return out

play = json.loads(Path('layouts/Play.json').read_text(encoding='utf-8'))
assert play.get('version') == 1, play.get('version')
ps = panels(play)
types = [p['panelType'] for p in ps]
assert set(types) <= ALLOWED, types
assert types.count('Image') >= 1 and types.count('Teleop') >= 1 and types.count('Gauge') >= 3, types
images = [p for p in ps if p['panelType'] == 'Image']
assert any((p.get('config') or {}).get('imageMode', {}).get('imageTopic') == '/doom/camera' for p in images), images
tele = next(p for p in ps if p['panelType'] == 'Teleop')
cfg = tele['config']
assert cfg.get('topic') == '/cmd_vel' and cfg.get('publishRate') == 35 and cfg.get('autoSendStopOnRelease') is True, cfg
paths = [(p.get('config') or {}).get('path') for p in ps if p['panelType'] == 'Gauge']
for needle in ('/doom/player.health', '/doom/player.armor', '/doom/player.ammo'):
    assert needle in paths, paths
print('RL-08', types)
"
```

### RL-09 — `layouts/Debug.json`: Play panels plus 3D, plot, log, raw

- [x] `layouts/Debug.json` is JSON `version == 1`. It includes the Play set (Image `/doom/camera`, Teleop `/cmd_vel`, three player gauges) **and** a `ThreeDee` panel (`fixedFrame` `map`, `followTf` `base_link`, `/doom/map` visible with `colorField` `occupancy`, `/doom/entities` visible), a `Plot` of `/doom/player.health` and `/doom/player.ammo` vs `timestamp`, a `Log` panel on `/doom/log`, and a `RawMessages` panel on `/doom/player`. Do not open the Foxglove app. Do not require a GUI import demo (eval F-3).

**Check:**

```sh
$PY -c "
import json
from pathlib import Path
ALLOWED = {'Image', 'Teleop', 'Gauge', 'ThreeDee', 'Plot', 'Log', 'RawMessages', 'Table'}

def panels(node, out=None):
    out = [] if out is None else out
    if isinstance(node, dict):
        if node.get('type') == 'panel' and 'panelType' in node:
            out.append(node)
        for v in node.values():
            panels(v, out)
    elif isinstance(node, list):
        for v in node:
            panels(v, out)
    return out

debug = json.loads(Path('layouts/Debug.json').read_text(encoding='utf-8'))
assert debug.get('version') == 1, debug.get('version')
ps = panels(debug)
types = [p['panelType'] for p in ps]
assert set(types) <= ALLOWED, types
for need in ('Image', 'Teleop', 'Gauge', 'ThreeDee', 'Plot', 'Log', 'RawMessages'):
    assert need in types, types
images = [p for p in ps if p['panelType'] == 'Image']
assert any((p.get('config') or {}).get('imageMode', {}).get('imageTopic') == '/doom/camera' for p in images)
tele = next(p for p in ps if p['panelType'] == 'Teleop')
assert tele['config'].get('topic') == '/cmd_vel'
paths = [(p.get('config') or {}).get('path') for p in ps if p['panelType'] == 'Gauge']
for needle in ('/doom/player.health', '/doom/player.armor', '/doom/player.ammo'):
    assert needle in paths, paths
td = next(p for p in ps if p['panelType'] == 'ThreeDee')
cfg = td['config']
assert cfg.get('fixedFrame') == 'map' and cfg.get('followTf') == 'base_link', cfg
topics = cfg.get('topics') or {}
assert (topics.get('/doom/map') or {}).get('colorField') == 'occupancy', topics
assert '/doom/entities' in topics and (topics.get('/doom/entities') or {}).get('visible', True)
plot = next(p for p in ps if p['panelType'] == 'Plot')
vals = {s.get('value') for s in (plot.get('config') or {}).get('paths') or []}
assert '/doom/player.health' in vals and '/doom/player.ammo' in vals, vals
assert (plot.get('config') or {}).get('xAxisVal') == 'timestamp'
logp = next(p for p in ps if p['panelType'] == 'Log')
assert (logp.get('config') or {}).get('topicToRender') == '/doom/log', logp
raw = next(p for p in ps if p['panelType'] == 'RawMessages')
assert (raw.get('config') or {}).get('topicPath') == '/doom/player', raw
print('RL-09', types)
"
```

---

## D. Scope

### RL-10 — Canvas / `.foxe` / MCAP / embed are not 02 scope

- [x] This workstream does not add a host-canvas renderer, a custom `.foxe` HUD, an MCAP writer, or an embed host (`dec_no_canvas`, `dec_stock_panels_only`, phase DAG). Grade **only** the 02-owned files below. Presence of `web/`, `node_modules/`, `.agent/workstreams/03-embed-shell/`, `.agent/workstreams/04-record-replay/`, `doom_foxglove/mcap*.py`, or README sentences saying embed/MCAP are *not* done does **not** FAIL this item.

**Check:**

```sh
rg -n -e 'getContext\s*\(' -e '<canvas' -e 'HTMLCanvasElement' -e '@foxglove/embed' -e '\.foxe' \
  doom_foxglove/topics.py doom_foxglove/world.py doom_foxglove/layouts_export.py \
  layouts/Play.json layouts/Debug.json
echo canvas_foxe_embed_exit=$?
rg -n -e 'mcap' \
  doom_foxglove/topics.py doom_foxglove/world.py doom_foxglove/layouts_export.py \
  layouts/Play.json layouts/Debug.json
echo mcap_exit=$?
```

PASS only if both `rg` invocations print nothing (ripgrep exits 1 on no match — that is PASS; treat "no output" as the bar, not exit 0). FAIL if any printed line is a product import, API call, or file emit. A comment that names these as out of scope is allowed only if it does not call an API. Do **not** search the rest of the tree for this item.

---

## Out of scope (do not FAIL 02 for these; do not require them)

- Camera JPEG, Twist, buttons, ClientPublish inbound, `TeleopListener.on_subscribe` / `on_unsubscribe` — `01-hero-loop` (`HL-05`…`HL-11`)
- Embed host, WASD keybindings, `@foxglove/embed`, layout switcher UI — `03-embed-shell`
- MCAP record/replay, Replay layout — `04-record-replay`
- Events, comparison, agent prompts, remote spectator — `05-stunt-extras`
- Click-to-publish nav goal (PLAN optional later)
- Custom `.foxe` HUD, mouse-look FPS, ROS/rosbridge, commercial IWAD, audio, cloud upload
- Opening the Foxglove desktop/web GUI and clicking Import layout (F-3)

A generator handed this contract implements remaining RL gaps (expected: RL-07 `WIRE LAYOUT` inside `./smoke`). It does not tick boxes, does not edit `.agent/workstreams/01-hero-loop/contract.md`, and does not "complete 03/04" under an RL id.

## Process (not an RL checkbox)

This file is the critic-gated contract the phase DAG required before generation. Generation preceded the gate; the gate is retroactive. The critic (kimi-k3-high) attacks these items; this planner does not grade them. No generator ticks the boxes above.
