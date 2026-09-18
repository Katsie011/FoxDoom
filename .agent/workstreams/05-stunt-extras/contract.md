# Contract — 05-stunt-extras

**Workstream:** `05-stunt-extras`
**Item-id prefix:** `SX-`
**KG node:** `ws_05_stunt_extras` (stays `deferred` until this contract is critic-gated)
**Capability:** `cap_stunt_extras`
**Status:** SX-01…SX-06 evaluator-ticked PASS (2026-09-18). Section F `UX-01`…`UX-14` appended 2026-09-18 (demo UX polish + 3D linedef walls); planner applied critic UX A-1…A-7; awaiting Kimi critic re-gate on those items only. This file is a gradeable contract, not a product patch. Do **not** untick SX-01…SX-06. No generator starts on UX-nn until the critic and planner agree. No evaluator ticks UX boxes until that gate.

Source of truth for phase scope: `.agent/GOAL.md` (`cap_stunt_extras`, `dec_phase_gating`, `dec_host_html_hud`, `dec_stock_panels_only`, `dec_no_canvas`, `dec_vizdoom_engine`) and `.agent/workstreams/05-stunt-extras/PLAN.md` (including **Demo UX polish**). SX-01…SX-06 still grade the **thin extras already on disk**: tagged `/doom/events`, `./smoke-events`, and three README copy-paste prompts. Section F grades host HTML HUD, player mesh, new-game, replay file browser, and **`/doom/walls` linedef extrusion**. PLAN's comparison mode, remote gateway, user script, image-click, and shareable recording link stay out of these checkboxes.

## Entry condition (what un-defers `ws_05_stunt_extras`)

All of the following must hold. This paragraph keeps the word `deferred` and the entry condition H-16 greps for.

1. `cap_live_ws_camera_teleop`, `cap_3d_map_hud`, and `cap_embed_page` are `done` in the knowledge graph. (`ws_05_stunt_extras DEPENDS_ON ws_03_embed_shell`.)
2. Workstreams `01-hero-loop`, `02-robotics-layout`, and `03-embed-shell` have evaluator verdicts of `done`.
3. A Kimi critic has gated this `SX-nn` list (this file) per `.agent/COORDINATION.md`.

Until (3), the workstream stays **deferred** in the graph even though product code already exists. Generation preceded this gate; the gate is retroactive. This planner writes the gradeable list now so the critic can attack it; it does not un-defer the workstream and does not tick boxes.

## How this contract is graded

The evaluator (kimi-k3-high) is told stunt extras are broken and must prove it. For every `SX-nn` item it must run the stated **Check** from a clean shell at the repo root, or quote the exact file text the check names. "Looks fine" is a fail. An unrun check is a fail. A `/tmp` helper the evaluator wrote is not an in-repo check.

- Repo root is `$ROOT` (`/Users/michael/Documents/foxglove/work/doom`). Every command below is run after `cd "$ROOT"`.
- `$PY` is `$ROOT/.venv/bin/python` when that file is executable, otherwise `python3`. Always `export PYTHONPATH="$ROOT"`.
- Smoke for SX items is `./smoke-events`. `./smoke`, `./smoke --hero`, and `./smoke-replay` are 01/02/04. Using them as the SX-03 command is an SX-03 FAIL. Section F headless smoke is `./smoke-pause-replay --new-game` (UX-10); that flag must not weaken PR-07.
- An item is **PASS** only if its check succeeds. Checkboxes below start unchecked. **Only the evaluator ticks `- [ ]`.** The generator must not tick boxes, must not edit this file, and must not append `verified` / `failed` onto `ContractItem` nodes.
- Occupied `ws://localhost:8765` is an environment note, not an SX FAIL (HL-12). `./smoke-events` may bind ephemeral.
- 01/02/03/04 items stay on those contracts. This file does not re-own camera JPEG, Twist, Play/Debug, embed host, or Replay Teleop-hidden.
- Opening the Foxglove app or pasting prompts into a built-in agent is **not** required. SX-05 grades file text. Do not FAIL an item because the evaluator did not click MCP.
- Idle 8-tick smoke is expected to emit `kind=level` (entering the map). Do **not** FAIL SX-02, SX-03, or SX-04 because `death` / `weapon` / `pickup` did not appear in those 8 ticks.
- Occupied `8764` (control) or `8765` (WS) is an environment note, not a UX FAIL. `./smoke-pause-replay --new-game` may bind ephemeral WS **and** control ports.
- A UX item is **PASS** only if its check succeeds. UX checkboxes start unchecked. **Only the evaluator ticks `- [ ]`.** Absence of `#key-hud` FAILs the item that names it (UX-01), not an environment note.
- FAIL any UX item whose Check names the HUD if the generator adds `getContext(` / `<canvas` for that HUD (same bar as ES-06). HUD is HTML/CSS (`#key-hud`, `#hud-health`, etc.). Do **not** require a `.foxe` or `installExtensions`.

---

## A. Topic schema and kinds

### SX-01 — `/doom/events` JSON `{ kind, message, tick, map }`

- [x] Topic `/doom/events` publishes JSON objects with exactly the required keys `kind`, `message`, `tick`, and `map`. The live channel uses `EVENTS_SCHEMA`, not `foxglove.Log` (that remains `/doom/log`, RL-05). Extra JSON keys are forbidden (`additionalProperties: false`). FAIL if `EVENTS_TOPIC` is not `"/doom/events"`. FAIL if the channel is a `LogChannel`. FAIL if `event_payload` omits any required key.

**Check:**

```sh
$PY -c "
from doom_foxglove import EVENTS_TOPIC
from doom_foxglove.topics import EVENTS_SCHEMA, event_payload
from doom_foxglove.world import LogEvent
assert EVENTS_TOPIC == '/doom/events', EVENTS_TOPIC
assert EVENTS_SCHEMA.get('type') == 'object'
assert EVENTS_SCHEMA.get('additionalProperties') is False
props = EVENTS_SCHEMA.get('properties') or {}
need = ('kind', 'message', 'tick', 'map')
assert set(EVENTS_SCHEMA.get('required') or []) == set(need), EVENTS_SCHEMA.get('required')
assert set(props) == set(need), props
assert props['kind']['type'] == 'string' and props['message']['type'] == 'string'
assert props['tick']['type'] == 'integer' and props['map']['type'] == 'string'
payload = event_payload(LogEvent(message='Entering E1M1', kind='level'), 7, 'E1M1')
assert payload == {'kind': 'level', 'message': 'Entering E1M1', 'tick': 7, 'map': 'E1M1'}, payload
print('SX-01 schema-ok')
"
```

Quote `EVENTS_TOPIC = "/doom/events"` in `doom_foxglove/__init__.py`. Quote `EVENTS_SCHEMA` in `doom_foxglove/topics.py` with `"required": ["kind", "message", "tick", "map"]`. Quote `"events": Channel(EVENTS_TOPIC, schema=EVENTS_SCHEMA)` in `world_channels`. Quote `def event_payload` returning those four keys. If `world_channels` constructs the events channel as `LogChannel`, FAIL.

### SX-02 — `kind` is one of `death | weapon | level | pickup`

- [x] Tagged event kinds are exactly the four strings `death`, `weapon`, `level`, `pickup`. `level` covers entering a map (`Entering {map}`) and level complete (`Level complete: {map}`). `death` is `You died.` `weapon` is a weapon change. `pickup` is armor / ammo / health pickups. `publish_world` logs onto `/doom/events` only when `event.kind in EVENT_KINDS`. `/doom/log` messages stay the RL-05 strings; do **not** FAIL this item because log lines are unprefixed. Do **not** require all four kinds in an idle smoke run.

**Check:**

```sh
$PY -c "
from doom_foxglove.topics import publish_world
from doom_foxglove.world import (
    EVENT_KINDS, KIND_DEATH, KIND_LEVEL, KIND_PICKUP, KIND_WEAPON,
    PlayerState, logs_from_delta,
)
assert set(EVENT_KINDS) == {'death', 'weapon', 'level', 'pickup'}
assert len(EVENT_KINDS) == 4 and len(set(EVENT_KINDS)) == 4
assert (KIND_LEVEL, KIND_DEATH, KIND_WEAPON, KIND_PICKUP) == ('level', 'death', 'weapon', 'pickup')

def ps(**kw):
    base = dict(health=100.0, armor=0.0, ammo=50.0, weapon=2, tick=0, dead=False)
    base.update(kw)
    return PlayerState(**base)

enter = logs_from_delta(None, ps(), 'E1M1')
assert any(e.kind == KIND_LEVEL and e.message == 'Entering E1M1' for e in enter), enter
done = logs_from_delta(ps(), ps(tick=1), 'E1M1', level_complete=True)
assert any(e.kind == KIND_LEVEL and e.message == 'Level complete: E1M1' for e in done), done
dead = logs_from_delta(ps(dead=False), ps(dead=True, health=0.0, tick=1), 'E1M1')
assert any(e.kind == KIND_DEATH and e.message == 'You died.' for e in dead), dead
weap = logs_from_delta(ps(weapon=2), ps(weapon=3, tick=1), 'E1M1')
assert any(e.kind == KIND_WEAPON for e in weap), weap
armor = logs_from_delta(ps(armor=0.0), ps(armor=100.0, tick=1), 'E1M1')
assert any(e.kind == KIND_PICKUP and e.message == 'Picked up armor.' for e in armor), armor
print('SX-02 kinds-ok')
"
```

Quote these exact assignments in `doom_foxglove/world.py`: `KIND_LEVEL = "level"`, `KIND_DEATH = "death"`, `KIND_WEAPON = "weapon"`, `KIND_PICKUP = "pickup"`, and `EVENT_KINDS = (KIND_LEVEL, KIND_DEATH, KIND_WEAPON, KIND_PICKUP)`. Quote `if event.kind in EVENT_KINDS` in `publish_world` in `doom_foxglove/topics.py`. FAIL if `EVENT_KINDS` gains a fifth member or drops one of the four.

---

## B. Smoke and at least one event

### SX-03 — `./smoke-events` exits 0

- [x] From `$ROOT`, `./smoke-events` records the default tick count to `recordings/smoke-events.mcap`, prints a `SMOKE-EVENTS OK` line, and exits 0. A busy 8765 plus ephemeral bind is HL-12, not FAIL. This item grades the **command exit and banner**, not the event count (that is SX-04). FAIL if the evaluator runs `./smoke`, `./smoke-replay`, `python -m doom_foxglove.smoke_events` *instead of* `./smoke-events`, or a `/tmp` wrapper. FAIL if exit is non-zero.

**Check:**

```sh
./smoke-events
echo smoke_events_exit=$?
```

PASS only if exit is 0 and stdout contains `SMOKE-EVENTS OK` and `file=`. Quote `exec "$PY" -m doom_foxglove.smoke_events` in `./smoke-events`. Quote `def _fail` returning `1` in `doom_foxglove/smoke_events.py`, and `return 0` after the OK print. Quote `fallback_if_busy=True` at the `start_ws` call in that file.

Negative path, deterministic, no escape hatch:

```sh
set +e
neg_err="$($PY -c "import sys; from doom_foxglove.smoke_events import _fail; sys.exit(_fail('critic-injected'))" 2>&1 >/dev/null)"
neg_exit=$?
set -e
printf '%s\n' "$neg_err"
echo neg_exit=$neg_exit
```

PASS only if `neg_exit` is 1 **and** `neg_err` (stderr) contains the exact substring `SMOKE-EVENTS FAIL: critic-injected`. An ImportError, SyntaxError, or missing-dep crash that exits 1 without that banner is FAIL. If `_fail` is absent or returns 0, FAIL even if this run of `./smoke-events` exited 0.

### SX-04 — Live publish or MCAP contains at least one `/doom/events` message

- [x] After SX-03 (reuse `recordings/smoke-events.mcap`; re-run `./smoke-events` only if the file is missing), the file exists, starts with MCAP magic, lists topic `/doom/events`, and `count_mcap_messages` for that topic is ≥ 1. The SX-03 stdout line also reports `live=<n>` with n ≥ 1. Idle reset is enough: a single `level` / entering-map event satisfies this item. FAIL if the evaluator trusts only the smoke `mcap_events=` print and does not parse the file with in-repo `count_mcap_messages` in `doom_foxglove/record.py`. FAIL if `list_mcap_topics` is not that in-repo parser.

**Check:**

```sh
$PY -c "
from doom_foxglove import EVENTS_TOPIC
from doom_foxglove.record import MCAP_MAGIC, count_mcap_messages, list_mcap_topics, smoke_events_recording_path
path = smoke_events_recording_path()
assert path.is_file(), path
blob = path.read_bytes()
assert blob.startswith(MCAP_MAGIC), blob[:16]
assert path.stat().st_size >= 1
topics = list_mcap_topics(path)
assert EVENTS_TOPIC in topics, sorted(topics)
n = count_mcap_messages(path, EVENTS_TOPIC)
assert n >= 1, (n, sorted(topics), path)
print('SX-04', path, 'bytes', path.stat().st_size, 'mcap_events', n, 'topics', sorted(topics))
"
```

Also quote the SX-03 stdout substring `live=` followed by an integer ≥ 1, and `mcap_events=` followed by an integer ≥ 1. Quote `if not live_events:` and `if mcap_count < 1:` in `doom_foxglove/smoke_events.py`. Quote `smoke_events_recording_path` returning `recordings/smoke-events.mcap`. If smoke's OK line lists a count but this parse finds 0, this item FAILs and SX-03 may still PASS.

---

## C. Agent prompts (copy-paste, no custom agent)

### SX-05 — README has three exact Foxglove agent / MCP prompts

- [x] Repository `README.md` ships three copy-paste prompts for the built-in Foxglove agent / MCP box. No custom agent ships in this repo. A one-line pointer in `web/README.md` does not FAIL and does not satisfy this item by itself. Do not open the Foxglove app. FAIL if any of the three fenced prompt bodies is missing or paraphrased.

**Check:**

```sh
$PY -c "
from pathlib import Path
text = Path('README.md').read_text(encoding='utf-8')
assert '## Ask Foxglove (copy-paste)' in text
assert 'No custom agent ships in this repo.' in text
prompts = (
    'Using /doom/player.health, /doom/events (kind=pickup or death), and /doom/log, when did health drop, and what happened in the two seconds before each drop? Give timestamps I can scrub to.',
    'Find /doom/events where kind=death (and the matching /doom/log line). Using /doom/player, /doom/entities, and health/ammo around that timestamp, why did I die? Point me at the scrub time.',
    'Build a Foxglove layout that plots /doom/player.weapon and /doom/player.ammo vs time, shows /doom/events filtered to kind=weapon, keeps the Image panel on /doom/camera, and leaves Teleop hidden for replay.',
)
missing = [p for p in prompts if p not in text]
assert not missing, missing
print('SX-05 prompts-ok', len(prompts))
"
```

Quote the heading `## Ask Foxglove (copy-paste)` and the sentence `No custom agent ships in this repo.` The custom-agent fence is exactly three tokens. Run:

```sh
rg -n -e 'FastMCP' -e 'langchain' -e '@modelcontextprotocol' doom_foxglove --glob '*.py'
```

PASS only if that `rg` prints nothing (ripgrep exit 1 on no match is PASS). FAIL if any of `FastMCP`, `langchain`, or `@modelcontextprotocol` appears in `doom_foxglove/**/*.py`. Do not FAIL this item on any other library, filename, or “agent-shaped” module that uses none of those three tokens.

---

## D. Scope fence

### SX-06 — Gateway, comparison UI, cloud, and policy-vs-human stay out

- [x] This thin extras slice does **not** deliver a remote-access gateway, a comparison-mode UI, a cloud share link, or a ViZDoom policy-vs-human runner. Their **absence** is PASS. Any `rg` hit (comment, string, docstring, or code) under the fence target is FAIL. Out-of-scope naming lives only in `README.md` under `## Not in this slice` (required; that heading is not a FAIL). Do not search `.agent/`, `PLAN.md`, `web/`, or other workstream contracts. Do not un-defer comparison/gateway under an SX id.

Fence target: `smoke-events` and the entire `doom_foxglove/` package. `web/` stays 03's business and is not in this `rg`.

**Check:**

```sh
rg -n -e 'remote-access' -e 'comparison.mode' -e 'comparison mode' \
  -e 'FOXGLOVE_API' -e 'data\.foxglove\.dev' -e 'upload_recording' -e 'DeviceCode' \
  -e 'policy vs human' -e 'stable_baselines' -e 'vizdoom.gym' \
  smoke-events doom_foxglove/
echo extras_fence_exit=$?
$PY -c "
from pathlib import Path
text = Path('README.md').read_text(encoding='utf-8')
assert '## Not in this slice' in text
for needle in (
    'remote-access gateway',
    'comparison mode UI',
    'cloud share links',
    'ViZDoom policy vs human',
):
    assert needle in text, needle
print('SX-06 readme-skip-ok')
"
```

PASS only if the `rg` invocation prints nothing (ripgrep exits 1 on no match — that is PASS; treat "no output" as the bar, not exit 0). **Any printed line is FAIL.** Comments are not exempt. Out-of-scope naming already has a required home (`README.md` `## Not in this slice`). Presence of `web/` live-only embed, `layouts/Replay.json`, or `./smoke-replay` does **not** FAIL (those are 03/04).

---

## Out of scope (do not FAIL 05 for these; do not require them)

These belong to other workstreams, later 05 cuts, or GOAL non-goals. Presence (01–04 already shipped) or absence does not decide any SX item except SX-06's named fence.

- Camera JPEG, Twist, buttons, ClientPublish inbound — `01-hero-loop`
- Grid / TF / entities / player JSON / log topic / Play and Debug layouts — `02-robotics-layout` (events are extra tagged copies of the same log moments)
- Embed host, WASD, `@foxglove/embed`, layout switcher — `03-embed-shell`
- Same-SDK MCAP sidecar, `layouts/Replay.json`, `./smoke-replay` — `04-record-replay` (`/doom/events` inside `recordings/smoke-events.mcap` **is** SX-04)
- Comparison mode UI, remote-access gateway, cloud share links, ViZDoom policy vs human — later extras; SX-06 forbids shipping them now
- User script (DPS / time-to-shotgun), image click/hover publish, shareable recording URL — PLAN garnish, not this contract
- Custom `.foxe` in the embed iframe, mouse-look FPS, ROS/rosbridge, commercial IWAD, audio
- Opening the Foxglove GUI and pasting the SX-05 prompts into MCP (documented by SX-05; not a headless FAIL)
- Editing `.agent/workstreams/01-hero-loop/contract.md`. Section F's planner already amended RL-08/RL-09, RR-04, PR-09, and ES-11; an SX generator still must not rewrite those files.

A generator handed **SX-01…SX-06** implements remaining SX gaps only. It does not tick boxes, does not edit other workstream contracts, and does not un-defer comparison/gateway/cloud/policy under an SX id.

SX-01…SX-06 stay evaluator-ticked. Do **not** untick them.

Section F (`UX-nn`) is a new slice on this same workstream (not a workstream `06-*`). The critic attacks those items next. This planner does not grade them. Do not tick any `- [ ]` on UX items.

---

## F. Demo UX polish (`UX-`)

Human demo feedback 2026-09-18. Pause & replay already works (FileSource, 3D cubes, gauges, playback bar). Occupancy `/doom/map` is still a **flat Grid** — that is not the 3D-map kicker. This slice is host-chrome + control-plane garnish **plus linedef walls in stock ThreeDee**, owned by `05` / `cap_stunt_extras`. Prefix `UX-`. Not a workstream `06-*`. SX-01…SX-06 stay as evaluated; do not untick them; do not re-grade them here.

`$PY`, `$ROOT`, and `PYTHONPATH=$ROOT` are the same as in the SX grading header. Every command is run after `cd "$ROOT"`. Opening a browser or a Foxglove Pro session is **not** required. Occupied 8765/8764 is not a FAIL if the smoke binds ephemeral.

Planner-amended (this run, do not retick, do not re-own as UX FAILs): RL-08 / RL-09 Gauge drop; RR-04 Gauge drop; PR-09 allows `POST /new-game` and still forbids `/resume`; ES-11 allow-list for `key-hud` / `hud-health` / `replay-files` / `new-game`; RL-01 dummy channel dicts include `'walls'` so `publish_world` may log `/doom/walls` without KeyError (do **not** FAIL RL-01 if walls count is 0 on today's Grid-only tree). A generator handed **this section** implements UX gaps in product code. It does not tick boxes, does not edit `.agent/workstreams/01-hero-loop/contract.md`, and does not create `.agent/workstreams/06-*`.

Locked walls topic: **`/doom/walls`** (`WALLS_TOPIC`), `foxglove.SceneUpdate`, **once per level** (same cadence as `/doom/map`). Not `kind="wall"` on `/doom/entities` (that would republish every tick or fight RL-03). Default extrusion height when ViZDoom sector floor/ceiling is missing: **`WALL_HEIGHT_M = 2.4`**. Occupancy Grid stays (do not FAIL RL-01). No IWAD lump parser (`dec_vizdoom_engine`).

A `/tmp` helper the evaluator wrote is not an in-repo check. Absence of `#key-hud` is a FAIL of UX-01, not an environment note.

Do **not** require reconstructing WASD from MCAP during FileSource replay (live-only HUD is enough for video). Do **not** require a `.foxe` or `installExtensions`. FAIL UX-04 / UX-11 if the HUD uses `getContext(` / `<canvas`.

Prefer injecting the marine into `publish_world` / `build_entities` from `world.pose` so RL-03's `observe().entities` still has no `kind == "player"` (`entities_from_objects` may keep its skip). Do not break RL-07 `entities >= 1`.

`run_loop` must keep `stop_event=None` as an optional kwarg so existing `./smoke-replay` / PR-07 still pass. Do **not** add `ticks=` to any `run_loop` call in `doom_foxglove/smoke_pause_replay.py` (PR-07 AST).

### UX-01 — `#key-hud` left column with W/A/S/D/Space

- [x] Host chrome grows `#key-hud` **left** of `#foxglove` (left column of the host app, for screen-recording viewers). It is **not** inside `#foxglove`, **not** a Foxglove panel, **not** a host `<canvas>`. Visible keys include W, A, S, and D, plus Space (label `Space` or `SPACE`). Live Play is enough; FileSource replay need not drive the keys.

**Check:**

```sh
$PY <<'PY'
from pathlib import Path
import re
html = Path("web/index.html").read_text(encoding="utf-8")
assert 'id="key-hud"' in html, html
assert 'id="foxglove"' in html
assert html.index('id="key-hud"') < html.index('id="foxglove"'), "key-hud must not live inside #foxglove"
chunk = html[html.index('id="key-hud"'): html.index('id="foxglove"')]
for needle in ("W", "A", "S", "D"):
    assert needle in chunk, needle
assert "Space" in chunk or "SPACE" in chunk, chunk
assert "<canvas" not in html.lower()
css = Path("web/src/styles.css").read_text(encoding="utf-8")
assert "#key-hud" in css, css
print("UX-01 key-hud")
PY
```

Quote `id="key-hud"` in `web/index.html` appearing before `id="foxglove"`. Quote `#key-hud` in `web/src/styles.css`. FAIL if `#key-hud` is missing. FAIL if the only key legend is copy inside `#foxglove` or a layout JSON panel.

**Attack:** WASD HUD that is a screenshot overlay in README, or keys only documented in `web/README.md`, FAILs the first assert.

### UX-02 — `#key-hud` keys follow `HoldController` motion

- [x] When `HoldController` motion is true for a field, the matching key in `#key-hud` gets `aria-pressed="true"` **or** a `pressed` class (or both). Mapping: `forward`→W, `left`→A, `back`→S, `right`→D, `fire`→Space. Coupling is a subscribe/callback from `HoldController` (invoked from `flush`, or a `subscribe` / `onMotion` listener `flush` notifies). Live-only. Do **not** require FileSource replay to reconstruct keys from MCAP.

**Check:**

```sh
$PY <<'PY'
from pathlib import Path
kb = Path("web/src/keybindings.ts").read_text(encoding="utf-8")
assert "class HoldController" in kb
assert "flush(" in kb
assert "subscribe" in kb or "onMotion" in kb or "listeners" in kb, "HoldController must expose subscribe/onMotion/listeners"
# HUD updater must be reachable from HoldController, not only a disconnected window keydown
joined = "\n".join(p.read_text(encoding="utf-8") for p in Path("web/src").glob("*.ts"))
assert "key-hud" in joined or "keyHud" in joined or "KeyHud" in joined, "no key-hud coupling in web/src"
assert "aria-pressed" in joined or "pressed" in joined, "no pressed state"
assert "HoldController" in joined
hud_files = [p for p in Path("web/src").glob("*.ts") if "key-hud" in p.read_text(encoding="utf-8")]
assert hud_files, "no key-hud ts"
for p in hud_files:
    t = p.read_text(encoding="utf-8")
    assert ("HoldController" in t) or ("onMotion" in t) or ("subscribe" in t), p
print("UX-02 hold-coupling")
PY
```

Quote `flush` in `web/src/keybindings.ts` invoking a subscriber/`onMotion` callback (or iterating `listeners`). Quote the HUD code that sets `aria-pressed` or class `pressed` on the W/A/S/D/Space elements. Any `web/src/*.ts` file that mentions `key-hud` must also mention `HoldController` or `subscribe` / `onMotion` in that same file. FAIL if `#key-hud` is painted only from a window `keydown` listener that never reads `HoldController` motion. FAIL if FileSource replay is the only path that lights the keys.

**Attack:** a static WASD legend that never hooks `HoldController` FAILs `subscribe` / `onMotion` / `listeners`. A `key-hud` file that only paints from `keydown` while `HoldController` lives in another file FAILs the per-file assert.

### UX-03 — Player SceneUpdate mesh (`player:` id)

- [x] `/doom/entities` includes a distinct stock-3D mesh for the marine so Replay/Debug occupancy is not an empty follow-frame. `publish_world` / `build_entities` always includes a `kind="player"` entity from `world.pose` (and may use `world.player`). `frame_id` may be `map` (like others) or `base_link`. Color and size must differ from `monster`. Cube or arrow is allowed. Prefer **not** dropping the `entities_from_objects` `kind == "player"` skip — RL-03 still asserts `observe().entities` has no player. Recorded into MCAP automatically via the existing entities channel. Do not break RL-07 `entities >= 1`.

**Check:**

```sh
$PY <<'PY'
from doom_foxglove.topics import _KIND_COLOR, _KIND_SIZE, build_entities, publish_world
from doom_foxglove.world import Entity, PlayerState, PoseState, WorldState

assert "player" in _KIND_COLOR, _KIND_COLOR
assert "player" in _KIND_SIZE, _KIND_SIZE
assert _KIND_COLOR["player"] != _KIND_COLOR["monster"], _KIND_COLOR
assert _KIND_SIZE["player"] != _KIND_SIZE["monster"], _KIND_SIZE

pose = PoseState(1.25, 2.5, 0.0, 0.3)
player = PlayerState(100.0, 0.0, 50.0, 2, 0, False)
monster = Entity(id="7", kind="monster", name="DoomImp", x=3, y=4, z=0, yaw=0)

class Rec:
    def __init__(self):
        self.last = None
        self.n = 0
    def log(self, *args, **kwargs):
        self.n += 1
        self.last = args[0] if args else None

dummy = {k: Rec() for k in ("map", "tf", "entities", "player", "log", "events", "walls")}
out = publish_world(dummy, WorldState(pose, player, [monster], None, []))
assert dummy["entities"].n == 1
r = repr(dummy["entities"].last)
assert "player:" in r, r[:800]
assert "monster:7" in r, r[:800]
assert "cubes: [" in r or "arrows: [" in r, r[:800]
ids = (out.get("entities") or {}).get("ids") or []
kinds_ok = any(str(i).startswith("player:") or str(i) == "player" for i in ids) or "player:" in r
assert kinds_ok, (ids, r[:400])
# empty observe-entities list still injects the marine
dummy2 = {k: Rec() for k in ("map", "tf", "entities", "player", "log", "events", "walls")}
publish_world(dummy2, WorldState(pose, player, [], None, []))
r2 = repr(dummy2["entities"].last)
assert "player:" in r2, r2[:800]
print("UX-03 player-mesh")
PY
```

Quote `_KIND_COLOR` / `_KIND_SIZE` entries for `"player"` in `doom_foxglove/topics.py`. Quote the `publish_world` / `build_entities` injection from `world.pose` (an `Entity(..., kind="player", ...)` or equivalent). Do **not** FAIL because `entities_from_objects` still `continue`s on `kind == "player"` (RL-03). FAIL if the only cubes are monsters and the marine is still skipped with no pose injection.

**Attack:** leaving `world.py:290-291` `continue` **and** not injecting from pose FAILs `player:` in the empty-list `publish_world` repr.

### UX-04 — Host HTML health/armor/ammo bars from `/doom/player`

- [x] Host chrome grows `#hud-bars` containing `#hud-health`, `#hud-armor`, and `#hud-ammo`. Bars read `/doom/player` JSON `{health, armor, ammo}` on the parent publish socket (or a tiny extra parent socket). Width/style is CSS: health 0–200, armor 0–200, ammo 0–300 (percentage of those maxima). Quote `health` in the HUD element / updater. Not a canvas framebuffer. Not a `.foxe`. Extra Gauge panels in layouts do not FAIL.

**Check:**

```sh
$PY <<'PY'
from pathlib import Path
html = Path("web/index.html").read_text(encoding="utf-8")
for nid in ("hud-bars", "hud-health", "hud-armor", "hud-ammo"):
    assert f'id="{nid}"' in html, nid
assert html.index('id="hud-bars"') < html.index('id="foxglove"')
assert "<canvas" not in html.lower()
joined = "\n".join(p.read_text(encoding="utf-8") for p in Path("web/src").glob("*.ts"))
assert "/doom/player" in joined, "HUD must subscribe /doom/player"
assert "health" in joined
css = Path("web/src/styles.css").read_text(encoding="utf-8")
blob = joined + "\n" + css
assert "200" in blob and "300" in blob, "maxima 200 health/armor and 300 ammo missing"
assert "#hud-health" in css or "#hud-bars" in css, css
print("UX-04 hud-bars")
PY
rg -n --glob '!*.md' -e 'getContext\s*\(' -e '<canvas' -e 'HTMLCanvasElement' web/src web/index.html
echo ux04_canvas_exit=$?
```

The canvas `rg` must print nothing (exit 1 = PASS). Quote `id="hud-health"` in `web/index.html`. Quote `health` in the TS that sets the bar (style width or equivalent). Quote `/doom/player` subscribe/parse. Quote maxima `200` (health/armor) and `300` (ammo) in `web/src/*.ts` **or** `web/src/styles.css`. FAIL if health is only a Foxglove Gauge. FAIL if the HUD is a `<canvas>` / `getContext`.

**Attack:** a generator that keeps three Gauges and never adds `#hud-health` FAILs the id assert. A canvas HUD FAILs the `rg`.

### UX-05 — `POST /new-game` starts a new episode (not resume)

- [x] Stdlib control plane grows `POST /new-game` (name locked) returning **200** JSON `{"paused": false}` **or** `{"reset": true}` (extra keys allowed). CORS same as pause (`Access-Control-Allow-Origin` `*` or `http://localhost:5173`; `OPTIONS` allowed). Server: new `engine.reset()`, new MCAP sidecar path, `stop_event.clear()`, **`run_loop` again**. Live `python -m doom_foxglove` must not idle-forever after pause without a way to re-enter `run_loop` (today `server.py` sleep loop). This is a **new game**, not resume of the paused tick. Do **not** add `POST /resume`.

**Check:**

```sh
$PY <<'PY'
import inspect
from doom_foxglove.server import main, run_loop

try:
    from doom_foxglove.server import start_control
except ImportError:
    from doom_foxglove.control import start_control

ctl_mod = inspect.getmodule(start_control)
text = inspect.getsource(ctl_mod)
assert "/new-game" in text, text
assert "do_OPTIONS" in text, text
assert "Access-Control-Allow-Origin" in text, text
live = inspect.getsource(main)
assert "run_loop" in live, live
assert "new-game" in live or "new_game" in live, live
assert "reset" in live or "new_game" in text or "reset" in text, (live, text)
sig = inspect.signature(run_loop)
assert "stop_event" in sig.parameters, sig
print("UX-05 new-game")
PY
rg -n -e '"/resume"' -e "'/resume'" doom_foxglove/server.py
echo ux05_resume_server_exit=$?
if test -f doom_foxglove/control.py; then
  rg -n -e '"/resume"' -e "'/resume'" doom_foxglove/control.py
  echo ux05_resume_control_exit=$?
fi
```

The resume `rg` invocations must print nothing (exit 1 = PASS). Quote `POST` path `/new-game` and CORS in the control module. Quote `engine.reset(` (or `eng.reset(`) on the new-game path. Quote `stop_event.clear` (or equivalent clear) and a second `run_loop(` after pause in `doom_foxglove/server.py` `main`. Quote `open_recording` for a **new** sidecar path on that path. FAIL if Play-the-button only `selectLayout`s (that is UX-08). FAIL if new-game is implemented as `/resume` clearing the same writer.

**Attack:** `POST /new-game` that only flips `paused` and never `reset()` / never re-enters `run_loop` FAILs UX-10 (`step_new_game=ok`).

### UX-06 — `GET /recordings` list and `GET /recording?name=` bytes

- [x] `GET /recordings` is **200** JSON **array** of objects with `name` (string, `.mcap` suffix) and `bytes` (int) **or** `path` (string) for files under `recordings/` with `.mcap` suffix. CORS same as pause. `GET /recording?name=<basename>` is **200** `application/octet-stream` for that file (locked URL shape; not `GET /recordings/<name>`). Missing file is 404 (not 409 — 409 stays the no-query `GET /recording` before pause, PR-03). `OPTIONS` allowed. Reject `..` path traversal (404 or 400; do not read outside `recordings/`).

**Check:**

```sh
$PY <<'PY'
import inspect
try:
    from doom_foxglove.server import start_control
except ImportError:
    from doom_foxglove.control import start_control
text = inspect.getsource(inspect.getmodule(start_control))
assert "/recordings" in text, text
assert "/recording" in text, text
assert "name" in text, text
assert "application/octet-stream" in text, text
assert "Access-Control-Allow-Origin" in text, text
assert any(t in text for t in ("..", "basename", "is_relative_to", "resolve")), "path traversal guard missing"
print("UX-06 recordings-index")
PY
```

Quote `GET` `/recordings` returning a JSON list. Quote `GET` `/recording` reading query `name=`. Quote CORS. Quote a traversal guard: literal `..` **or** `basename` **or** `is_relative_to` **or** `resolve`. Runtime list + fetch is UX-10. FAIL if the list endpoint is missing CORS (browser fetch from `http://localhost:5173` is cross-origin). FAIL if the locked URL is `GET /recordings/<name>` instead of `GET /recording?name=`.

**Attack:** `GET /recordings` without CORS FAILs the quote. A generator that only documents files in README FAILs `/recordings` in the handler source.

### UX-07 — Play click from FileSource starts a new live game

- [x] Embed `#layout-play` click: if currently in file/replay mode (FileSource / pause-replay flag), `POST /new-game`, `setDataSource` live (existing `parentOwnedLiveSource` / `iframeOwnedLiveSource` helpers), `selectLayout(layoutParams("play"))`. If already live, `selectLayout(play)` may stay as today. Quote that branch in `web/src/main.ts`.

**Check:**

```sh
$PY <<'PY'
from pathlib import Path
main = Path("web/src/main.ts").read_text(encoding="utf-8")
assert "layout-play" in main
assert "/new-game" in main, main
assert "setDataSource" in main
assert 'layoutParams("play")' in main or "layoutParams('play')" in main, main
assert "parentOwnedLiveSource" in main or "iframeOwnedLiveSource" in main
print("UX-07 play-new-game")
PY
```

Quote the `#layout-play` `click` handler branch that POSTs `/new-game` when FileSource/replay is active, then live `setDataSource`, then `selectLayout(layoutParams("play"))`. FAIL if Play only `selectLayout(layoutParams("play"))` with no `/new-game` (today's `web/src/main.ts` ~56–58). FAIL if Play is `POST /resume`.

**Attack:** Play button that only `selectLayout`s after pause FAILs `/new-game` in `main.ts`.

### UX-08 — `#replay-files` lists `doom-*.mcap` and loads FileSource

- [x] Left column `#replay-files` is **shown** when FileSource is active and **hidden** during live. Rows are recordings whose names match `doom-*.mcap` (filter smoke-only junk: `smoke.mcap`, `smoke-events.mcap`, `smoke-pause.mcap` must not appear as rows even if `GET /recordings` lists them). Click a row → `GET /recording?name=` → `new File` → `setDataSource({ type: "file", file, autoplay: true })` and Replay layout. Visible in replay mode.

**Check:**

```sh
$PY <<'PY'
from pathlib import Path
import re
html = Path("web/index.html").read_text(encoding="utf-8")
assert 'id="replay-files"' in html, html
assert html.index('id="replay-files"') < html.index('id="foxglove"')
joined = "\n".join(p.read_text(encoding="utf-8") for p in Path("web/src").glob("*.ts"))
assert "replay-files" in joined
assert "/recordings" in joined, joined
assert "/recording?name=" in joined or "/recording?name=" in joined.replace("`", ""), joined
assert "doom-" in joined and ".mcap" in joined, "doom-*.mcap filter missing"
assert "new File" in joined
assert re.search(r'type:\s*["\']file["\']', joined), joined
assert "hidden" in joined or "hidden" in html
print("UX-08 replay-files")
PY
```

Quote `id="replay-files"` in `web/index.html`. Quote the `doom-` prefix filter in `web/src`. Quote `GET` `/recording?name=`. Quote hide-on-live / show-on-FileSource. FAIL if the list is visible during live Play. FAIL if click uses `GET /recordings/<name>`.

**Attack:** a left column that lists every `.mcap` including smoke wrappers FAILs the `doom-` filter quote.

### UX-09 — Layouts regenerated: Play is Image+Teleop; Gauge not required

- [x] Regenerate via `doom_foxglove/layouts_export.py`. Play: Image + Teleop; **no Gauge required**. Debug and Replay: `ThreeDee` with `/doom/entities` still visible; Gauges not required. Plot of `/doom/player.health` vs time may stay on Debug. Extra Gauges do not FAIL. Log/Raw on Debug and no-Teleop on Replay stay as today (RR-04 / RL-09 spirit).

**Check:**

```sh
$PY <<'PY'
import json
from pathlib import Path
from doom_foxglove.layouts_export import debug_layout, play_layout, replay_layout

ALLOWED = {"Image", "Teleop", "Gauge", "ThreeDee", "Plot", "Log", "RawMessages", "Table"}

def panels(node, out=None):
    out = [] if out is None else out
    if isinstance(node, dict):
        if node.get("type") == "panel" and "panelType" in node:
            out.append(node)
        for v in node.values():
            panels(v, out)
    elif isinstance(node, list):
        for v in node:
            panels(v, out)
    return out

play = json.loads(Path("layouts/Play.json").read_text(encoding="utf-8"))
ps = panels(play)
types = [p["panelType"] for p in ps]
assert set(types) <= ALLOWED, types
assert types.count("Image") >= 1 and types.count("Teleop") >= 1, types
images = [p for p in ps if p["panelType"] == "Image"]
assert any((p.get("config") or {}).get("imageMode", {}).get("imageTopic") == "/doom/camera" for p in images)

debug = json.loads(Path("layouts/Debug.json").read_text(encoding="utf-8"))
dps = panels(debug)
dtypes = [p["panelType"] for p in dps]
assert "ThreeDee" in dtypes and "Plot" in dtypes and "Log" in dtypes and "RawMessages" in dtypes, dtypes
td = next(p for p in dps if p["panelType"] == "ThreeDee")
topics = (td.get("config") or {}).get("topics") or {}
assert "/doom/entities" in topics and (topics.get("/doom/entities") or {}).get("visible", True)
# /doom/walls visibility is UX-14 (locked dedicated topic), not this item.

replay = json.loads(Path("layouts/Replay.json").read_text(encoding="utf-8"))
rps = panels(replay)
rtypes = [p["panelType"] for p in rps]
assert rtypes.count("Teleop") == 0, rtypes
assert "ThreeDee" in rtypes and "Image" in rtypes and "Log" in rtypes, rtypes
rtd = next(p for p in rps if p["panelType"] == "ThreeDee")
rtopics = (rtd.get("config") or {}).get("topics") or {}
assert "/doom/entities" in rtopics

src = Path("doom_foxglove/layouts_export.py").read_text(encoding="utf-8")
assert "play_layout" in src and "debug_layout" in src and "replay_layout" in src
print("UX-09 layouts", types, dtypes, rtypes)
PY
```

Quote `("Play.json", play_layout())` (or the existing export tuples) in `layouts_export.py`. Do **not** FAIL because Gauge count is 0. Do **not** FAIL because Gauge count is still 3 (extra Gauges allowed). FAIL if Play drops Teleop or Image. FAIL if Debug/Replay drop `/doom/entities` on ThreeDee. `/doom/walls` on those ThreeDee configs is **UX-14**, not this item.

**Attack:** forgetting to amend RL-08 and then requiring Gauge here would fight the planner Gauge drop — this item must **not** require Gauge.

### UX-10 — `./smoke-pause-replay --new-game` ticks, pause, list, reset, steps again

- [x] From `$ROOT`, `./smoke-pause-replay --new-game` extends the existing pause-replay smoke (do **not** add `./smoke-ux` unless a `ticks=` `run_loop` would be required — it must not; use `stop_event` on every `run_loop`). Sequence: publish ticks, `POST /pause`, `GET /recordings` includes the sidecar `name`, `POST /new-game` 200 with `paused: false` or `reset: true`, new recording path **different** from the paused one, engine steps again. Do **not** weaken PR-07 (`ticks` ban, `/pause` counts, default `./smoke-pause-replay` still PASS).

**Check:**

```sh
test -f ./smoke-pause-replay
./smoke-pause-replay --new-game
echo smoke_new_game_exit=$?
$PY <<'PY'
import ast
import inspect
from pathlib import Path
from doom_foxglove import smoke_pause_replay as sm_mod

src = inspect.getsource(sm_mod)
assert "--new-game" in src or "new_game" in src or "new-game" in src, src
assert "/recordings" in src, src
assert "/new-game" in src, src
assert "list_mcap_topics" in src or "MCAP_MAGIC" in src

def call_name(node):
    if isinstance(node.func, ast.Name):
        return node.func.id
    if isinstance(node.func, ast.Attribute):
        return node.func.attr
    return None

def dict_str_keys(node):
    if not isinstance(node, ast.Dict):
        return None
    out = []
    for k in node.keys:
        if isinstance(k, ast.Constant) and isinstance(k.value, str):
            out.append(k.value)
    return out

def is_run_loop_name(node):
    return isinstance(node, ast.Name) and node.id == "run_loop"

tree = ast.parse(src)
sites = []
for n in ast.walk(tree):
    if not isinstance(n, ast.Call):
        continue
    name = call_name(n)
    if name == "run_loop":
        sites.append(("direct", n))
    elif name == "Thread" and any(k.arg == "target" and is_run_loop_name(k.value) for k in n.keywords):
        sites.append(("thread", n))
assert sites, "smoke never calls run_loop"
for kind, c in sites:
    if kind == "direct":
        kw = {k.arg for k in c.keywords}
        assert "ticks" not in kw, "PR-07: do not stop the loop with ticks="
        assert "stop_event" in kw, kw
    else:
        keys = None
        for k in c.keywords:
            if k.arg == "kwargs":
                keys = dict_str_keys(k.value)
        assert keys is not None
        assert "stop_event" in keys and "ticks" not in keys, keys
print("UX-10 smoke-source")
PY
```

PASS only if `--new-game` exits 0. Stdout must contain `step_stopped=ok`, `new_game=ok`, `step_new_game=ok`, and a paused path plus a different new path (`path=` / `file=` twice, or `old=` and `new=`). Quote `GET /recordings` including the sidecar name. FAIL if the evaluator runs `./smoke-ux` instead of `./smoke-pause-replay --new-game`. FAIL if `ticks=` appears on any `run_loop` in `smoke_pause_replay.py` (that is also a PR-07 FAIL). FAIL if new-game is skipped when the flag is passed.

**Attack:** a fourth wrapper `./smoke-ux` that this item does not name FAILs `test -f` only if the generator never extends `--new-game`. Extending with `ticks=` FAILs the AST (and PR-07).

### UX-11 — No `.foxe`, no `installExtensions`, no canvas HUD

- [x] This kiosk cannot load extensions (`https://embed.foxglove.dev/`). Product HUD must not ship a `.foxe`, call `installExtensions`, or draw bars/keys on a canvas. Host HTML/CSS only.

**Check:**

```sh
rg -n --glob '!*.md' -e 'installExtensions' -e '\.foxe' -e 'getContext' -e '<canvas' \
  web/src web/index.html doom_foxglove/
echo ux11_ext_exit=$?
```

One PASS rule: that `rg` must print nothing (ripgrep exit 1 on no match is PASS), **or** every printed line is a comment that names `.foxe` / `installExtensions` / `getContext` / `<canvas` as forbidden and contains no call syntax (`installExtensions(`, `getContext(`). A comment is a printed line whose first non-whitespace characters are `//`, `/*`, `*`, `<!--`, or `#`. Any other printed line is FAIL. Do **not** search `web/node_modules` or `web/dist`.

**Attack:** a generator that adds `viewer.installExtensions` FAILs the first needle.

### UX-12 — Scope fence (no resume-same-episode, no workstream 06)

- [x] UX polish does not implement resume-live of the paused tick (`POST /resume`, `#resume`), mouse-look, rosbridge, comparison UI, cloud upload, audio, or a workstream `06-*`. Host HTML HUD and `POST /new-game` **are** in scope and do **not** FAIL this item.

**Check:**

```sh
$PY -c "from pathlib import Path; xs=sorted(p.name for p in Path('.agent/workstreams').glob('06-*')); assert not xs, xs; print('no-06')"
echo '---'
rg -n -e '"/resume"' -e "'/resume'" -e 'id="resume' \
  web/index.html web/src doom_foxglove/server.py
echo ux12_resume_exit=$?
if test -f doom_foxglove/control.py; then
  rg -n -e '"/resume"' -e "'/resume'" doom_foxglove/control.py
  echo ux12_resume_control_exit=$?
fi
rg -n -e 'pointerlock' -e 'mouse-look' -e 'rosbridge' -e 'comparison.mode' \
  web/src web/index.html doom_foxglove/server.py
echo ux12_fence_exit=$?
```

PASS if `no-06` prints and no `06-*` directory exists. PASS if resume/mouse-look/rosbridge/comparison `rg` invocations print nothing, **or** every printed line is a comment that names the extra as out of scope. `POST /new-game`, `#key-hud`, `#hud-bars`, `#replay-files`, and FileSource are **required** by UX-01…UX-10 and do **not** FAIL this item. FAIL if a `06-*` workstream directory exists.

**Attack:** inventing workstream 06 FAILs. `POST /resume` that clears `stop_event` without `engine.reset` FAILs the resume `rg`. `/doom/walls` linedef extrusion is **UX-13/UX-14** and does **not** FAIL this fence.

### UX-13 — `/doom/walls` linedef meshes from ViZDoom state (once per level)

- [x] Publish the map as **3D geometry** in the stock ThreeDee panel, not only the 2D occupancy Grid. Topic is locked: **`WALLS_TOPIC = "/doom/walls"`**, `foxglove.SceneUpdate` on a `SceneUpdateChannel`. Source linedefs are the same blocking lines `_occupancy` already iterates (`state.sectors` / `sector.lines` / `is_blocking` in `VizDoomEngine._occupancy`, `doom_foxglove/engine.py` ~276, and `occupancy_from_lines` in `world.py`). Extrude cubes or line primitives in Z. When ViZDoom exposes sector floor/ceiling heights, use them; otherwise default **`WALL_HEIGHT_M = 2.4`**. Height (`size.z` or equivalent) must be **> `DEFAULT_CELL_M` (0.5)** so walls are not flat grid cells; the Check asserts this on the built SceneUpdate repr (`max(z floats) > DEFAULT_CELL_M`), not only `WALL_HEIGHT_M == 2.4`. Flat plates (`size.z ≤ 0.5`) FAIL. Publish **once per level** from `publish_world` when `map_grid` is set (same cadence as `/doom/map`), not every tick. A flag-less `WorldState` with `map_grid` set still publishes the hollow-room fallback walls. Fallback engine (no vizdoom): still publish the hollow-room walls, **N ≥ 4**. `build_walls` is the locked builder name. Do **not** parse the IWAD file (`struct.unpack` of WAD lumps is FAIL except existing WS/MCAP parsers in `ws_client.py` and `record.py`). Do **not** FAIL RL-01 (Grid stays). Do **not** require sector-floor mesh or textures.

**Check:**

```sh
$PY <<'PY'
import re
from doom_foxglove import WALLS_TOPIC
from doom_foxglove.topics import WALL_HEIGHT_M, build_walls, publish_world, world_channels
from doom_foxglove.world import DEFAULT_CELL_M, PlayerState, PoseState, WorldState, hollow_room

assert WALLS_TOPIC == "/doom/walls", WALLS_TOPIC
assert WALL_HEIGHT_M == 2.4, WALL_HEIGHT_M
assert WALL_HEIGHT_M > DEFAULT_CELL_M

ch = world_channels()
assert "walls" in ch, sorted(ch)
from foxglove.channels import SceneUpdateChannel
assert isinstance(ch["walls"], SceneUpdateChannel), type(ch["walls"])
def topic_of(c):
    t = getattr(c, "topic", None)
    return t() if callable(t) else t
assert topic_of(ch["walls"]) == WALLS_TOPIC

msg = build_walls([])  # fallback / empty-line path must still yield hollow-room walls
assert type(msg).__name__ == "SceneUpdate", type(msg)
r = repr(msg)
assert "cubes: [" in r or "lines: [" in r, r[:600]
# Count wall entities in the fallback hollow room
n = r.count("id: \"wall:") + r.count("id: \"walls:")
if n < 4:
    # allow ids without the wall: prefix if count is reported another way
    n = len(re.findall(r"id: \"[^\"]+\"", r))
assert n >= 4, (n, r[:800])
assert "size" in r.lower() or "z=" in r or "z:" in r, r[:400]
zs = [float(v) for v in re.findall(r"z: ([0-9.]+)", r)]
assert zs and max(zs) > DEFAULT_CELL_M, zs

grid = hollow_room("fallback")
pose = PoseState(0.0, 0.0, 0.0, 0.0)
player = PlayerState(100.0, 0.0, 50.0, 2, 0, False)

class Rec:
    def __init__(self):
        self.n = 0
        self.last = None
    def log(self, *args, **kwargs):
        self.n += 1
        self.last = args[0] if args else None

dummy = {k: Rec() for k in ("map", "tf", "entities", "player", "log", "events", "walls")}
out = publish_world(dummy, WorldState(pose, player, [], None, []))
assert dummy["map"].n == 0 and dummy["walls"].n == 0, "walls must skip when map_grid is None"
dummy2 = {k: Rec() for k in ("map", "tf", "entities", "player", "log", "events", "walls")}
out2 = publish_world(dummy2, WorldState(pose, player, [], grid, []))
assert dummy2["map"].n == 1 and dummy2["walls"].n == 1, (dummy2["map"].n, dummy2["walls"].n)
wr = repr(dummy2["walls"].last)
assert "wall" in wr.lower(), wr[:600]
wzs = [float(v) for v in re.findall(r"z: ([0-9.]+)", wr)]
assert wzs and max(wzs) > DEFAULT_CELL_M, wzs
print("UX-13 walls-schema", "fallback_ids", n)
PY
rg -n -e 'struct\.unpack' doom_foxglove/
echo ux13_unpack_exit=$?
```

The `struct.unpack` `rg` covers the whole `doom_foxglove/` package. PASS only if it prints nothing (exit 1 = PASS), **or** every printed line's path is `doom_foxglove/ws_client.py` or `doom_foxglove/record.py` (existing WS framing / MCAP parsers). Any hit in another file is FAIL. Filename-column check; comments in a non-exempt file are not exempt. Quote `WALLS_TOPIC = "/doom/walls"` in `doom_foxglove/__init__.py`. Quote `WALL_HEIGHT_M = 2.4` and `def build_walls` in `doom_foxglove/topics.py` (or `doom_foxglove/world.py` if the builder lives next to `occupancy_from_lines`). Quote ViZDoom `sectors` / `lines` / `is_blocking` on the wall path (may share `_occupancy`). Quote `if world.map_grid is not None` still gating map **and** walls. Walls come from `publish_world` when `map_grid` is set (once per level), matching occupancy cadence. A flag-less `WorldState` with `map_grid` set must still publish the hollow-room fallback walls; do **not** require a `world.walls` pending flag. FAIL if walls are published every tick (`dummy["walls"].n != 0` when `map_grid is None`). FAIL if `/doom/walls` is missing and walls are stuffed onto `/doom/entities` as `kind="wall"` (topic lock is `/doom/walls`). FAIL if height ≤ cell size. A flat-plate SceneUpdate (all `z:` floats ≤ `DEFAULT_CELL_M` / `size.z ≤ 0.5`) FAILs the repr-regex even if `WALL_HEIGHT_M == 2.4`. FAIL if `build_walls` is missing.

**Attack:** leaving only the flat Grid FAILs `WALLS_TOPIC`. A from-scratch WAD parser with `struct.unpack` outside `ws_client.py` / `record.py` FAILs the `rg`. A flat-plate SceneUpdate (`size.z ≤ 0.5`) FAILs the `z:` regex even if `WALL_HEIGHT_M == 2.4`. Republishing walls every tick FAILs the `map_grid is None` cadence assert.

### UX-14 — Debug/Replay ThreeDee shows `/doom/walls`; `./smoke` prints `walls=`

- [x] `layouts/Debug.json` and `layouts/Replay.json` ThreeDee `topics` include `/doom/walls` with `visible` true (regenerate via `layouts_export.py`). Play need not show walls. `./smoke` (no `--hero`) still exits 0 and prints `walls=` or `wall_count=` as an integer. Occupied 8765 is not FAIL (ephemeral bind). When smoke `backend=vizdoom`, that integer must be **≥ 10** (E1M1 has many linedefs). When `backend=fallback`, **≥ 4** (hollow room). Do not change the RL-07 `WIRE LAYOUT` format string (extra stdout is allowed). Extra MCAP topics do not FAIL RR-03.

**Check:**

```sh
./smoke
echo smoke_walls_exit=$?
$PY <<'PY'
import json
import os
import re
from pathlib import Path

def panels(node, out=None):
    out = [] if out is None else out
    if isinstance(node, dict):
        if node.get("type") == "panel" and "panelType" in node:
            out.append(node)
        for v in node.values():
            panels(v, out)
    elif isinstance(node, list):
        for v in node:
            panels(v, out)
    return out

for name in ("layouts/Debug.json", "layouts/Replay.json"):
    doc = json.loads(Path(name).read_text(encoding="utf-8"))
    td = next(p for p in panels(doc) if p["panelType"] == "ThreeDee")
    topics = (td.get("config") or {}).get("topics") or {}
    assert "/doom/walls" in topics, (name, sorted(topics))
    assert (topics.get("/doom/walls") or {}).get("visible", True)
print("UX-14 layouts-walls")

export = Path("doom_foxglove/layouts_export.py").read_text(encoding="utf-8")
assert "WALLS_TOPIC" in export or "/doom/walls" in export, export
print("UX-14 export-quote")
PY
```

PASS only if `./smoke` exits 0, stdout contains `SMOKE OK`, and stdout matches `walls=` or `wall_count=` followed by an integer. If that stdout also contains `backend=vizdoom` (or `backend=vizdoom` on a nearby engine line), the integer must be ≥ 10. If it contains `backend=fallback`, the integer must be ≥ 4. Quote `/doom/walls` in both layout JSON files' ThreeDee `topics`. Quote `WALLS_TOPIC` (or the string `/doom/walls`) in `layouts_export.py` `debug_layout` / `replay_layout`. FAIL if the evaluator runs `./smoke --hero` as this item's command. FAIL if walls are only documented in README.

**Attack:** Debug ThreeDee that still lists only `/doom/map` + `/doom/entities` FAILs `/doom/walls` in `topics`. Smoke that never prints `walls=` FAILs even if `build_walls` exists (UX-13 may still PASS).

---

## Out of scope (do not FAIL 05 for these; do not require them)

These belong to other workstreams, later 05 cuts, or GOAL non-goals. Presence (01–04 already shipped) or absence does not decide any SX item except SX-06's named fence. UX items **do** require host HUD / new-game / replay-files / `/doom/walls` as named above.

- Camera JPEG, Twist, buttons, ClientPublish inbound — `01-hero-loop`
- Grid / TF / entities / player JSON / log topic / Play and Debug layouts — `02-robotics-layout` (player **mesh** on `/doom/entities` **is** UX-03; linedef **walls** on `/doom/walls` **are** UX-13/UX-14; Gauge drop is planner-amended on RL-08/RL-09). Occupancy Grid **stays**; do not FAIL RL-01.
- Embed host, WASD, `@foxglove/embed`, layout switcher — `03-embed-shell` (`#key-hud` / `#hud-bars` / `#replay-files` **are** UX)
- Same-SDK MCAP sidecar, `layouts/Replay.json`, `./smoke-replay`, pause-replay PR-nn — `04-record-replay` (`POST /new-game` and `GET /recordings` **are** UX-05/UX-06). Extra `/doom/walls` in an MCAP does **not** FAIL RR-03.
- Comparison mode UI, remote-access gateway, cloud share links, ViZDoom policy vs human — later extras; SX-06 forbids shipping them now
- User script (DPS / time-to-shotgun), image click/hover publish, shareable recording URL — PLAN garnish, not this contract
- Custom `.foxe` in the embed iframe, `installExtensions`, mouse-look FPS, ROS/rosbridge, commercial IWAD, audio, resume-same-episode (`POST /resume`)
- From-scratch IWAD lump parser; textured WAD rendering; full sector-floor meshes; host-canvas map renderer
- Opening the Foxglove GUI and pasting the SX-05 prompts into MCP (documented by SX-05; not a headless FAIL)
- Editing `.agent/workstreams/01-hero-loop/contract.md`
- Creating `.agent/workstreams/06-*`

A generator handed **section F** implements remaining UX gaps only. It does not tick boxes, does not untick SX-01…SX-06, does not edit the 01 contract, and does not un-defer comparison/gateway/cloud/policy under a UX id.

## Process (not an SX/UX checkbox)

SX-01…SX-06 were critic-gated and evaluator-ticked. Section F is the planner-authored UX list from 2026-09-18 demo feedback (host HUD + new-game + **linedef walls**). Planner applied critic UX A-1…A-7. The critic (kimi-k3-high) re-gates UX-01…UX-14; this planner does not grade them. No generator ticks the boxes above. Next action is the Kimi critic re-gate on section F, not a product-code generator.
