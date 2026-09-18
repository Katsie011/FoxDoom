# Contract — 05-stunt-extras

**Workstream:** `05-stunt-extras`
**Item-id prefix:** `SX-`
**KG node:** `ws_05_stunt_extras` (stays `deferred` until this contract is critic-gated)
**Capability:** `cap_stunt_extras`
**Status:** awaiting Kimi critic re-gate. Planner applied `critique.md` amendments 1–4 (2026-09-18). This file is a gradeable contract, not a product patch. No evaluator ticks boxes until that gate.

Source of truth for phase scope: `.agent/GOAL.md` (`cap_stunt_extras`, `dec_phase_gating`) and `.agent/workstreams/05-stunt-extras/PLAN.md`. This contract does not rewrite either. This slice grades the **thin extras already on disk**: tagged `/doom/events`, `./smoke-events`, and three README copy-paste prompts. PLAN's comparison mode, remote gateway, user script, image-click, and shareable recording link stay out of these checkboxes.

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
- Smoke for this workstream is `./smoke-events`. `./smoke`, `./smoke --hero`, and `./smoke-replay` are 01/02/04. Using them here is an SX-03 FAIL.
- An item is **PASS** only if its check succeeds. Checkboxes below start unchecked. **Only the evaluator ticks `- [ ]`.** The generator must not tick boxes, must not edit this file, and must not append `verified` / `failed` onto `ContractItem` nodes.
- Occupied `ws://localhost:8765` is an environment note, not an SX FAIL (HL-12). `./smoke-events` may bind ephemeral.
- 01/02/03/04 items stay on those contracts. This file does not re-own camera JPEG, Twist, Play/Debug, embed host, or Replay Teleop-hidden.
- Opening the Foxglove app or pasting prompts into a built-in agent is **not** required. SX-05 grades file text. Do not FAIL an item because the evaluator did not click MCP.
- Idle 8-tick smoke is expected to emit `kind=level` (entering the map). Do **not** FAIL SX-02, SX-03, or SX-04 because `death` / `weapon` / `pickup` did not appear in those 8 ticks.

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
- Custom `.foxe` HUD, mouse-look FPS, ROS/rosbridge, commercial IWAD, audio
- Opening the Foxglove GUI and pasting the SX-05 prompts into MCP (documented by SX-05; not a headless FAIL)
- Editing `.agent/workstreams/01-hero-loop/contract.md` (or 02/03/04 contracts)

A generator handed this contract implements remaining SX gaps only. It does not tick boxes, does not edit other workstream contracts, and does not un-defer comparison/gateway/cloud/policy under an SX id.

## Process (not an SX checkbox)

This file is the contract the phase DAG required before generation. Generation preceded the gate; the gate is retroactive. The critic (kimi-k3-high) attacks these items; this planner does not grade them. No generator ticks the boxes above.
