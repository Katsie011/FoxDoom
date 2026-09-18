# Contract — 04-record-replay

**Workstream:** `04-record-replay`
**Item-id prefix:** `RR-`
**KG node:** `ws_04_record_replay` (stays `deferred` until this contract is critic-gated)
**Capability:** `cap_mcap_replay`
**Status:** awaiting Kimi critic re-gate. Planner applied `critique.md` amendments 1–3 (2026-09-18). This file is a gradeable contract, not a product patch. No generator starts until the critic and planner agree. No evaluator ticks boxes until that gate.

Source of truth for phase scope: `.agent/GOAL.md` (`cap_mcap_replay`, topic contract, `dec_foxglove_sdk_ws`) and `.agent/workstreams/04-record-replay/PLAN.md`. This contract does not rewrite either. GOAL wins if PLAN's optional share link or embed `setDataSource` line disagrees.

## Entry condition (what un-defers `ws_04_record_replay`)

All three must hold. This paragraph keeps the word `deferred` and the entry condition H-16 greps for.

1. `cap_embed_page` is `done` in the knowledge graph. (`ws_04_record_replay DEPENDS_ON ws_03_embed_shell`.)
2. A human can finish a short live session in the embed (move + fire) so there is something worth recording.
3. A Kimi critic has gated this `RR-nn` list (this file) per `.agent/COORDINATION.md`.

Until (3), the workstream stays **deferred** in the graph even though product code already exists. Generation preceded this gate; the gate is retroactive. This planner writes the gradeable list now so the critic can attack it; it does not un-defer the workstream and does not tick boxes.

## How this contract is graded

The evaluator (kimi-k3-high) is told record/replay is broken and must prove it. For every `RR-nn` item it must run the stated **Check** from a clean shell at the repo root, or quote the exact file text the check names. "Looks fine" is a fail. An unrun check is a fail. A `/tmp` helper the evaluator wrote is not an in-repo check.

- Repo root is `$ROOT` (`/Users/michael/Documents/foxglove/work/doom`). Every command below is run after `cd "$ROOT"`.
- `$PY` is `$ROOT/.venv/bin/python` when that file is executable, otherwise `python3`. Always `export PYTHONPATH="$ROOT"`.
- Smoke for this workstream is `./smoke-replay`. `./smoke` and `./smoke --hero` are 01/02; using them here is an RR-02 FAIL.
- An item is **PASS** only if its check succeeds. Checkboxes below start unchecked. **Only the evaluator ticks `- [ ]`.** The generator must not tick boxes, must not edit this file, and must not append `verified` / `failed` onto `ContractItem` nodes.
- Occupied `ws://localhost:8765` is an environment note, not an RR FAIL (HL-12). `./smoke-replay` may bind ephemeral.
- 01/02/03 items stay on those contracts. This file does not re-own camera JPEG, Twist, layouts Play/Debug, or the embed host.
- Opening the Foxglove desktop/web GUI is **not** required for any RR item (eval 2026-09-18 playback-bar UNVERIFIED). README documents the human open path (RR-05). Do not FAIL an item because the evaluator did not click Import layout.

## F-notes (eval.md 2026-09-18) — ownership, not extra product scope

- **Playback bar:** Foxglove file-source chrome, not a `panelType`. RR-04 walks `Replay.json`. RR-05 quotes README. Do **not** require a `PlaybackBar` panel. Do **not** require a GUI demo.
- **`setDataSource({ type: "live" | "remote-file" | "recording" })`:** PLAN mentions host control. GOAL `cap_mcap_replay` does not. Embed recording mode is **03/05**, not RR. `web/` staying live-only does **not** FAIL any RR item.
- **Optional shareable recording link:** PLAN marks it optional and GOAL forbids cloud recording upload before `05`. RR-06 PASSes with local files only. Do not require Data Platform.

---

## A. Same SDK writes MCAP

### RR-01 — Same `foxglove-sdk` Context writes the live WebSocket and the MCAP sidecar

- [x] Recording is a foxglove-sdk MCAP sink on the **default Context** that `foxglove.start_server` also uses (`dec_foxglove_sdk_ws`, GOAL `cap_mcap_replay`: "Same SDK code writes MCAP"). Live `python -m doom_foxglove` opens that sink unless `--no-record`. `./smoke-replay` records by calling the same `open_recording` + `run_loop` path, not a second bag writer. FAIL if `open_recording` constructs a separate `foxglove.Context(`. FAIL if MCAP is written with `rosbag`, `rosbag2`, or a standalone `mcap.Writer` that never goes through `foxglove.open_mcap`. FAIL if smoke builds messages and dumps them without `run_loop`.

**Check:**

```sh
$PY -c "
import inspect
from doom_foxglove.record import open_recording
from doom_foxglove.server import main, start_ws
from doom_foxglove.smoke_replay import main as smoke_main

rec = inspect.getsource(open_recording)
assert 'foxglove.open_mcap' in rec, rec
assert 'Context' not in open_recording.__code__.co_names, open_recording.__code__.co_names
assert 'rosbag' not in rec and 'mcap.Writer' not in rec, rec

ws = inspect.getsource(start_ws)
assert 'foxglove.start_server' in ws, ws

live = inspect.getsource(main)
assert 'open_recording' in live, live
assert 'no_record' in live, live

sm = inspect.getsource(smoke_main)
assert 'open_recording' in sm and 'run_loop' in sm, sm
assert 'mcap.Writer' not in sm, sm
print('RR-01 same-sdk-sink')
"
```

Quote these literals: `foxglove.open_mcap` in `doom_foxglove/record.py`; `from doom_foxglove.record import` plus `open_recording` in `doom_foxglove/server.py`; `if not args.no_record` in `main`; `writer = open_recording` in both `server.py` `main` and `doom_foxglove/smoke_replay.py`. If any of those is absent, FAIL.

---

## B. Smoke and file contents

### RR-02 — `./smoke-replay` exits 0

- [x] From `$ROOT`, `./smoke-replay` records the default tick count to `recordings/smoke.mcap`, prints a `SMOKE-REPLAY OK` line, and exits 0. A busy 8765 plus ephemeral bind is HL-12, not FAIL. This item grades the **command exit and banner**, not the topic set (that is RR-03). FAIL if the evaluator runs `./smoke`, `python -m doom_foxglove.smoke_replay` *instead of* `./smoke-replay`, or a `/tmp` wrapper. FAIL if exit is non-zero.

**Check:**

```sh
./smoke-replay
echo smoke_replay_exit=$?
```

PASS only if exit is 0 and stdout contains `SMOKE-REPLAY OK` and `file=`. Quote `exec "$PY" -m doom_foxglove.smoke_replay` in `./smoke-replay`. Quote `_fail` and `return 0` after the OK print in `doom_foxglove/smoke_replay.py`. If `_check_replay_layout` is not called from `main`, FAIL even if this run exited 0.

### RR-03 — Required topics are in the MCAP file

- [x] After RR-02 (reuse `recordings/smoke.mcap`; re-run `./smoke-replay` only if the file is missing), the file exists, starts with MCAP magic, and contains every topic in this exact set: `/doom/camera`, `/doom/map`, `/tf`, `/doom/entities`, `/doom/player`, `/doom/log`. Extra topics do not FAIL. `/cmd_vel` and `/doom/buttons` are inbound ClientPublish; they are **not** required in the file. FAIL if the evaluator trusts only the smoke `topics=` print and does not parse the file. FAIL if `list_mcap_topics` is not the in-repo parser under `doom_foxglove/record.py`.

**Check:**

```sh
$PY -c "
from doom_foxglove.record import EXPECTED_TOPICS, MCAP_MAGIC, list_mcap_topics, smoke_recording_path
path = smoke_recording_path()
assert path.is_file(), path
blob = path.read_bytes()
assert blob.startswith(MCAP_MAGIC), blob[:16]
assert path.stat().st_size >= 1
topics = list_mcap_topics(path)
need = ('/doom/camera', '/doom/map', '/tf', '/doom/entities', '/doom/player', '/doom/log')
assert EXPECTED_TOPICS == need, EXPECTED_TOPICS
missing = [t for t in need if t not in topics]
assert not missing, (missing, sorted(topics))
print('RR-03', path, 'bytes', path.stat().st_size, 'topics', sorted(topics))
"
```

Quote `EXPECTED_TOPICS` in `doom_foxglove/record.py` as those six strings. Quote `list_mcap_topics` walking opcode `OP_CHANNEL`. If smoke's OK line lists the topics but this parse finds a hole, this item FAILs and RR-02 may still PASS.

---

## C. Replay layout and README

### RR-04 — `layouts/Replay.json` has no Teleop (stock panels; playback bar is file chrome)

- [x] `layouts/Replay.json` is JSON `version == 1` in the SDK programmatic layout shape. Walk `type == "panel"` nodes (do not `json.dumps` and substring-search). Allowed `panelType` strings (`dec_stock_panels_only`): `Image`, `Teleop`, `Gauge`, `ThreeDee`, `Plot`, `Log`, `RawMessages`, `Table`. **Zero** panels have `panelType == "Teleop"`. Required: Image on `/doom/camera`, ThreeDee (`fixedFrame` `map`, `followTf` `base_link`, `/doom/map` and `/doom/entities` visible), Gauge paths including `/doom/player.health`, `/doom/player.armor`, `/doom/player.ammo`, Log on `/doom/log`. Plot and RawMessages are allowed extras. Playback is Foxglove's file-source bar, not a layout panel — do **not** require a `PlaybackBar` `panelType`. Do **not** open the Foxglove app.

**Check:**

```sh
$PY -c "
import json
from pathlib import Path
from doom_foxglove.layouts_export import replay_layout
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

# Docstring-proof: do not substring-search inspect.getsource (Replay docstring names Teleop).
assert '_teleop' not in replay_layout.__code__.co_names, replay_layout.__code__.co_names
assert 'TeleopPanel' not in replay_layout.__code__.co_names, replay_layout.__code__.co_names
ser = json.loads(replay_layout().to_json())
assert all(p.get('panelType') != 'Teleop' for p in panels(ser)), [p.get('panelType') for p in panels(ser)]

replay = json.loads(Path('layouts/Replay.json').read_text(encoding='utf-8'))
assert replay.get('version') == 1, replay.get('version')
ps = panels(replay)
types = [p['panelType'] for p in ps]
assert set(types) <= ALLOWED, types
assert types.count('Teleop') == 0, types
assert types.count('Image') >= 1 and types.count('ThreeDee') >= 1, types
assert types.count('Gauge') >= 3 and types.count('Log') >= 1, types
images = [p for p in ps if p['panelType'] == 'Image']
assert any((p.get('config') or {}).get('imageMode', {}).get('imageTopic') == '/doom/camera' for p in images), images
td = next(p for p in ps if p['panelType'] == 'ThreeDee')
cfg = td['config']
assert cfg.get('fixedFrame') == 'map' and cfg.get('followTf') == 'base_link', cfg
topics = cfg.get('topics') or {}
assert (topics.get('/doom/map') or {}).get('visible', True)
assert '/doom/entities' in topics
paths = [(p.get('config') or {}).get('path') for p in ps if p['panelType'] == 'Gauge']
for needle in ('/doom/player.health', '/doom/player.armor', '/doom/player.ammo'):
    assert needle in paths, paths
logp = next(p for p in ps if p['panelType'] == 'Log')
assert (logp.get('config') or {}).get('topicToRender') == '/doom/log', logp
print('RR-04', types)
"
```

Quote `("Replay.json", replay_layout())` in `doom_foxglove/layouts_export.py`. If `replay_layout` references `_teleop` or `TeleopPanel` in `__code__.co_names`, or if the serialized `replay_layout().to_json()` tree has `panelType == "Teleop"`, FAIL even if the JSON on disk was hand-edited. Do **not** FAIL because the function docstring contains the word Teleop.

### RR-05 — README documents how to open the recording

- [x] Repository `README.md` tells a human how to prove replay without a cloud account: run `./smoke-replay`, open `recordings/smoke.mcap` (or a live `recordings/doom-*.mcap`) as a **local file** in Foxglove, import `layouts/Replay.json`, and use the **playback bar**. It may say the embed host stays live-only. Do not open the Foxglove app to grade this item. FAIL if any of the strings below is missing.

**Check:**

```sh
$PY -c "
from pathlib import Path
text = Path('README.md').read_text(encoding='utf-8')
need = (
    './smoke-replay',
    'layouts/Replay.json',
    'recordings/smoke.mcap',
    'playback bar',
)
missing = [s for s in need if s not in text]
assert not missing, missing
assert 'Open local file' in text or 'open local file' in text.lower() or 'drag' in text.lower(), 'no local-open instruction'
print('RR-05 readme-ok')
"
```

Quote the `## Replay an MCAP` heading in `README.md`. A one-line pointer in `web/README.md` does not FAIL and does not satisfy this item by itself.

---

## D. Cloud and 05 extras

### RR-06 — No cloud required

- [x] `cap_mcap_replay` is local MCAP + Replay layout. No RR check requires Foxglove Data Platform, a share URL, an API token, or `app.foxglove.dev` as a recording host. FAIL if `./smoke-replay` cannot pass without those. FAIL if 04-owned files call a cloud upload API. A README sentence that there is **no** cloud share link in v1 is allowed and expected. Optional PLAN share-link waits for `05`.

**Check:**

```sh
rg -n -e 'FOXGLOVE_API' -e 'data\.foxglove\.dev' -e 'upload_recording' -e 'DeviceCode' \
  doom_foxglove/record.py doom_foxglove/smoke_replay.py smoke-replay layouts/Replay.json \
  doom_foxglove/server.py doom_foxglove/layouts_export.py
echo cloud_api_exit=$?
$PY -c "
from pathlib import Path
text = Path('README.md').read_text(encoding='utf-8')
assert 'cloud' in text.lower(), 'README must say cloud is not required / not in v1'
print('RR-06 local-only')
"
```

PASS only if the `rg` invocation prints nothing (ripgrep exits 1 on no match — that is PASS; treat "no output" as the bar, not exit 0). FAIL if any printed line is a product import or upload call. `https://app.foxglove.dev` as a **local-file** viewer in README is allowed; FAIL if README makes a cloud recording URL the only way to open the file.

### RR-07 — Events, comparison, agent, remote spectator are 05 (out of scope)

- [x] This workstream does not deliver `cap_stunt_extras`. Grade **only** the 04-owned files below. Absence of events tagging, comparison mode, built-in agent prompts, and remote spectator does **not** FAIL. Presence of those as product code in 04-owned files **does** FAIL. The existing `EVENTS_TOPIC` import and `smoke_events_recording_path` helper in `doom_foxglove/record.py` are **not** events tagging and do **not** FAIL. The existing `EVENTS_TOPIC` import and `events={EVENTS_TOPIC}` banner in `doom_foxglove/server.py` are the same class of helper (topic constant / log line) and do **not** FAIL. Embed `setDataSource` recording mode is not required. Do not un-defer `05`. Do not edit other workstream contracts.

04-owned files for this item: `doom_foxglove/record.py`, `doom_foxglove/smoke_replay.py`, `smoke-replay`, `layouts/Replay.json`, `replay_layout` in `doom_foxglove/layouts_export.py`, recording flags in `doom_foxglove/server.py`.

**Check:**

```sh
rg -n -e 'comparison.mode' -e 'remote.spectator' -e 'setDataSource' -e 'agent.prompt' \
  -e 'EVENTS_TOPIC' -e 'events' \
  doom_foxglove/record.py doom_foxglove/smoke_replay.py smoke-replay layouts/Replay.json \
  doom_foxglove/server.py doom_foxglove/layouts_export.py
echo extras_exit=$?
```

PASS if `rg` prints nothing, **or** every printed line is one of these allowed existing helpers (explicit carve-out; do not FAIL): `EVENTS_TOPIC` import in `doom_foxglove/record.py` (if present); `smoke_events_recording_path` in `doom_foxglove/record.py`; `EVENTS_TOPIC` import and `events={EVENTS_TOPIC}` banner in `doom_foxglove/server.py`. FAIL if any printed line implements comparison mode, remote spectator, `setDataSource`, agent prompts, or events tagging beyond that carve-out. A comment that names them as out of scope is allowed only if it does not call an API. Do **not** search `web/` or `.agent/workstreams/05-stunt-extras/` for this item. Presence of those trees does not FAIL.

---

## Out of scope (do not FAIL 04 for these; do not require them)

- Camera JPEG, Twist, buttons, ClientPublish inbound — `01-hero-loop`
- Play/Debug layouts, Grid/TF/entities/player/log **live** schema — `02-robotics-layout` (recording those topics into MCAP **is** RR-03)
- Embed host, WASD, `@foxglove/embed`, layout switcher, `setDataSource` recording — `03-embed-shell`
- Events, comparison, agent prompts, remote spectator, cloud share link — `05-stunt-extras`
- Custom `.foxe` HUD, mouse-look FPS, ROS/rosbridge, commercial IWAD, audio
- Opening the Foxglove GUI and clicking the playback bar (documented by RR-05; not a headless FAIL)

A generator handed this contract implements remaining RR gaps only. It does not tick boxes, does not edit `.agent/workstreams/01-hero-loop/contract.md` (or 02/03/05 contracts), and does not un-defer `05` under an RR id.

## Process (not an RR checkbox)

This file is the contract the phase DAG required before generation. Generation preceded the gate; the gate is retroactive. The critic (kimi-k3-high) attacks these items; this planner does not grade them. No generator ticks the boxes above.
