# Contract — 04-record-replay

**Workstream:** `04-record-replay`
**Item-id prefix:** `RR-`
**KG node:** `ws_04_record_replay` (stays `deferred` until this contract is critic-gated)
**Capability:** `cap_mcap_replay`
**Status:** RR-01…RR-07 evaluated PASS (2026-09-18). Pause-replay slice `PR-01`…`PR-10` appended 2026-09-18; awaiting Kimi critic gate on those new items only. This file is a gradeable contract, not a product patch. Do **not** untick RR-01…RR-07. No generator starts on PR-nn until the critic and planner agree. No evaluator ticks PR boxes until that gate.

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
- Occupied `8764` (control) or `8765` (WS) is an environment note, not a PR FAIL. `./smoke-pause-replay` may bind ephemeral WS **and** control ports. Do not FAIL a PR item because those defaults were busy.
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

- [x] `layouts/Replay.json` is JSON `version == 1` in the SDK programmatic layout shape. Walk `type == "panel"` nodes (do not `json.dumps` and substring-search). Allowed `panelType` strings (`dec_stock_panels_only` / `dec_host_html_hud`): `Image`, `Teleop`, `Gauge`, `ThreeDee`, `Plot`, `Log`, `RawMessages`, `Table`. **Zero** panels have `panelType == "Teleop"`. Required: Image on `/doom/camera`, ThreeDee (`fixedFrame` `map`, `followTf` `base_link`, `/doom/map` and `/doom/entities` visible), Log on `/doom/log`. Player **Gauges are not required** (host HTML HUD; extra Gauges do not FAIL). Plot and RawMessages are allowed extras. Playback is Foxglove's file-source bar, not a layout panel — do **not** require a `PlaybackBar` `panelType`. Do **not** open the Foxglove app.

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
assert types.count('Log') >= 1, types
images = [p for p in ps if p['panelType'] == 'Image']
assert any((p.get('config') or {}).get('imageMode', {}).get('imageTopic') == '/doom/camera' for p in images), images
td = next(p for p in ps if p['panelType'] == 'ThreeDee')
cfg = td['config']
assert cfg.get('fixedFrame') == 'map' and cfg.get('followTf') == 'base_link', cfg
topics = cfg.get('topics') or {}
assert (topics.get('/doom/map') or {}).get('visible', True)
assert '/doom/entities' in topics
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

Pause-replay (`PR-nn`, section E) owns the embed FileSource path. RR-01…RR-07 still do not grade `web/`. Do not treat the RR-07 "do not search `web/`" sentence as a PR-04 FAIL.

## Process (not an RR checkbox)

This file is the contract the phase DAG required before generation. Generation preceded the gate; the gate is retroactive. The critic (kimi-k3-high) attacks these items; this planner does not grade them. No generator ticks the boxes above.

Pause-replay `PR-01`…`PR-10` is a new slice on this same workstream (not a workstream `06-*`). The critic attacks those items next. This planner does not grade them. Do not untick RR-01…RR-07. Do not tick any `- [ ]` on PR items.

---

## E. Pause & replay in the embed (`PR-`)

Completes `cap_mcap_replay` inside the embed host (`web/`). Prefix `PR-` (pause-replay). Not a workstream `06-*`. RR-01…RR-07 stay as evaluated; do not untick them; do not re-grade them here.

`$PY`, `$ROOT`, and `PYTHONPATH=$ROOT` are the same as in the RR grading header. Every command is run after `cd "$ROOT"`. Opening a browser or a Foxglove Pro session is **not** required. Occupied 8765/8764 is not a FAIL if the smoke binds ephemeral (PR-07). ES-11's Replay/mcap carve-out lives on `03-embed-shell/contract.md`; do **not** duplicate that carve-out as a 04 FAIL.

A `/tmp` helper the evaluator wrote is not an in-repo check. Absence of `#pause-replay` or `./smoke-pause-replay` is a FAIL of the item that names it, not an environment note.

`run_loop` must keep `stop_event=None` as an optional kwarg so existing `./smoke-replay` (`ticks=`, no `stop_event`) still satisfies RR-02.

### PR-01 — Stdlib HTTP control plane on `--control-port` (default 8764)

- [x] Live `python -m doom_foxglove` serves a **stdlib** HTTP control plane on a dedicated port, default **8764**, flag `--control-port`. It is not rosbridge, not Flask/FastAPI, not a second `foxglove.start_server` / Foxglove WebSocket. `main` prints a banner line containing `control http://` so a human can see the bound URL. Pointers: `doom_foxglove/server.py` `main` ~202–255; existing `start_ws` stays the live WS. `start_control` takes `fallback_if_busy: bool = False` (same convention as `start_ws`); the Check asserts that parameter name.

**Check:**

```sh
$PY <<'PY'
import inspect
from doom_foxglove.server import main

src = inspect.getsource(main)
assert "--control-port" in src, src
compact = src.replace(" ", "")
assert "default=8764" in compact, src
assert "control http://" in src, src

try:
    from doom_foxglove.server import start_control
except ImportError:
    from doom_foxglove.control import start_control

ctl = inspect.getsource(start_control)
assert "foxglove.start_server" not in ctl, ctl
names = start_control.__code__.co_names
assert "HTTPServer" in names or "ThreadingHTTPServer" in names, names
assert "fallback_if_busy" in inspect.signature(start_control).parameters, inspect.signature(start_control)
assert "start_control" in src, src
print("PR-01 control-plane")
PY
```

Quote `--control-port` and `default=8764` on the argparse in `doom_foxglove/server.py` `main`. Quote `start_control(` called from `main`. Quote `control http://` in that banner print. `start_control` may live in `doom_foxglove/server.py` or `doom_foxglove/control.py` as long as `main` calls it and the import above succeeds.

FAIL if `start_control` is missing (ImportError is FAIL). FAIL if the control plane is rosbridge, a second Foxglove WS, or a non-stdlib HTTP stack: `rg -n -e 'rosbridge' -e 'flask' -e 'fastapi' -e 'aiohttp' doom_foxglove/server.py doom_foxglove/control.py` (skip `control.py` if that file does not exist) must print nothing, **or** every printed line is a comment that names those as forbidden. FAIL if `start_control` source contains `foxglove.start_server`.

**Attack:** a generator that reuses `--port` for HTTP, or that prints only the WS banner, FAILs the `8764` / `control http://` quotes.

---

### PR-02 — `POST /pause` stops `engine.step` and closes the foxglove-sdk MCAP writer

- [x] `POST /pause` (and CORS preflight `OPTIONS`) stops the ViZDoom tick loop: no more `engine.step` after the handler returns. It flushes/closes the existing foxglove-sdk writer (`writer.close()`, same `open_recording` / `foxglove.open_mcap` path — do **not** add `mcap.Writer` / rosbag). Response is `200` with JSON metadata including `"paused": true` and, when recording was on, a `path` string. Idempotent: a second `POST /pause` does not crash and returns the same `path`. `run_loop` (`doom_foxglove/server.py` ~163–199) takes optional `stop_event=None`; when that `threading.Event` is set, the loop must not call `engine.step` again. `run_loop` may poll `stop_event.is_set()` or use `stop_event.wait(timeout)` as the tick sleep; either satisfies the Check.

**Check:**

```sh
$PY <<'PY'
import inspect
from doom_foxglove.server import run_loop

sig = inspect.signature(run_loop)
assert "stop_event" in sig.parameters, sig
assert sig.parameters["stop_event"].default is None, sig
names = run_loop.__code__.co_names
assert "is_set" in names or "wait" in names, names
assert "step" in names, names

try:
    from doom_foxglove.server import start_control
except ImportError:
    from doom_foxglove.control import start_control

ctl_mod = inspect.getmodule(start_control)
text = inspect.getsource(ctl_mod)
assert "/pause" in text, text
assert "do_OPTIONS" in text, text
assert "Access-Control-Allow-Origin" in text, text
assert "mcap.Writer" not in text, text
assert "rosbag" not in text, text
print("PR-02 pause-stops-step")
PY
```

Quote `stop_event` on `run_loop`. Quote `writer.close()` on the pause path (handler or the `main` path it waits on) — same writer returned by `open_recording`. Quote `foxglove.open_mcap` still only in `doom_foxglove/record.py` (RR-01); FAIL if pause-replay adds a standalone `mcap.Writer`. Runtime proof that stepping actually stops, that `POST` is idempotent, and that `POST` before any ticks does not crash is PR-07 (`step_stopped=ok`, `double_pause=ok`, `./smoke-pause-replay --immediate-pause`).

**Attack:** `POST /pause` that only sets a flag and never closes the writer FAILs PR-03/PR-07 (`GET /recording` 409 forever or unreadable file). A `run_loop(..., ticks=8)` smoke that never POSTs FAILs PR-07, not this inspect.

---

### PR-03 — `GET /recording` returns closed MCAP bytes; CORS; 409 before pause

- [x] After a successful `POST /pause` with recording on, `GET /recording` is `200`, `Content-Type: application/octet-stream`, body starts with MCAP magic `\x89MCAP0\r\n` (`doom_foxglove/record.py` `MCAP_MAGIC`), and CORS `Access-Control-Allow-Origin` is `*` or `http://localhost:5173`. Before pause, `GET /recording` is **409** (documented; do not use 404). `OPTIONS /recording` is allowed for preflight.

**Check:**

```sh
$PY <<'PY'
import inspect
from doom_foxglove.record import MCAP_MAGIC

assert MCAP_MAGIC == b"\x89MCAP0\r\n", MCAP_MAGIC
try:
    from doom_foxglove.server import start_control
except ImportError:
    from doom_foxglove.control import start_control
text = inspect.getsource(inspect.getmodule(start_control))
assert "/recording" in text, text
assert "application/octet-stream" in text, text
assert "Access-Control-Allow-Origin" in text, text
assert "409" in text, text
print("PR-03 get-recording")
PY
```

Quote `application/octet-stream` and `Access-Control-Allow-Origin` in the control module. Quote the 409 branch for `GET /recording` before pause. Runtime: PR-07 stdout contains `pre_pause=409` and a 200 body that `list_mcap_topics` accepts. FAIL if before-pause is 404. FAIL if CORS is missing from the handler source (browser fetch from `http://localhost:5173` is cross-origin; a Python smoke client is not a CORS proof).

**Attack:** `GET /recording` before any `POST /pause` must be 409. A handler that streams an open writer (no `close`) FAILs the magic/topics parse in PR-07.

---

### PR-04 — Embed `#pause-replay` loads FileSource + Replay `layout` (not `opaqueLayout`)

- [x] Host chrome in `web/index.html` (Play/Debug sit at ~20–23) grows a button `#pause-replay` whose visible label contains `Pause` (e.g. `Pause & replay`). It sits with the Play/Debug layout buttons in `#chrome` / `.controls` / `.layouts`, **not** inside `#foxglove`, **not** inside a Foxglove panel, **not** on a host `<canvas>` (`dec_no_canvas`, `dec_stock_panels_only`). Click: `POST` pause to the control URL, `GET` the MCAP as a `Blob`, `new File([blob], filename)` with a `.mcap` name, `viewer.setDataSource({ type: "file", file, autoplay: true })` (`@foxglove/embed` `FileSource`, `web/node_modules/@foxglove/embed/src/types.ts` ~153–156), then `viewer.selectLayout({ storageKey, layout: replayLayoutData, force: true })` loading `layouts/Replay.json` as programmatic `layout`. Do **not** pass `opaqueLayout` — that field is app-export JSON and shows "Incompatible layout". Play/Debug already use `layout` in `web/src/layouts.ts` ~1–32. Do not add a custom `PlaybackBar` panel. Do not custom-render frames. Replay already has zero Teleop (RR-04).

**Check:**

```sh
$PY <<'PY'
from pathlib import Path
import re
html = Path("web/index.html").read_text(encoding="utf-8")
assert 'id="pause-replay"' in html, html
m = re.search(r'<button[^>]*id="pause-replay"[^>]*>(.*?)</button>', html, re.S)
assert m, "pause-replay is not a button"
assert "Pause" in m.group(1), m.group(1)
assert 'id="foxglove"' in html
# button must appear before the foxglove main, not inside it
assert html.index('id="pause-replay"') < html.index('id="foxglove"'), "button inside #foxglove"
assert "<canvas" not in html.lower()

lay = Path("web/src/layouts.ts").read_text(encoding="utf-8")
assert "layouts/Replay.json" in lay, lay
assert re.search(r"opaqueLayout\s*:", lay) is None, lay
assert "replayLayoutData" in lay or "replayLayoutParams" in lay, lay

main = Path("web/src/main.ts").read_text(encoding="utf-8")
assert "pause-replay" in main, main
assert "click" in main, main
assert "setDataSource" in main, main
assert re.search(r'type:\s*["\']file["\']', main) or "type: \"file\"" in Path("web/src").joinpath("transport.ts").read_text(encoding="utf-8") or any(
    re.search(r'type:\s*["\']file["\']', p.read_text(encoding="utf-8"))
    for p in Path("web/src").glob("*.ts")
), "no FileSource type: file"
assert any(".mcap" in p.read_text(encoding="utf-8") for p in Path("web/src").glob("*.ts")), "File name must end .mcap"
assert any("autoplay" in p.read_text(encoding="utf-8") for p in Path("web/src").glob("*.ts")), "autoplay: true missing"
assert any("new File" in p.read_text(encoding="utf-8") for p in Path("web/src").glob("*.ts")), "new File([blob], filename) missing"
print("PR-04 embed-button")
PY
rg -n -e 'PlaybackBar' --glob '!*.md' web/src layouts/Replay.json
echo playbackbar_exit=$?
rg -n --glob '!*.md' -e 'getContext\s*\(' -e '<canvas' -e 'HTMLCanvasElement' web/src web/index.html
echo canvas_exit=$?
rg -n 'id="pause-replay"' layouts
echo pause_in_layouts_exit=$?
```

The two `rg` invocations over `web/src` / `layouts/Replay.json` / `web/index.html` must print nothing (exit 1 = PASS). `rg` over `layouts` for `id="pause-replay"` must print nothing. The Replay params object in `web/src/layouts.ts` must be named `replayLayoutData` or `replayLayoutParams` (the Check greps those literals) with `storageKey`, `layout` (not `opaqueLayout`), `force: true`. Quote the `#pause-replay` `click` handler in `web/src/main.ts` (or a helper it calls). FAIL if the only Pause control is a `panelType` in a layout JSON. FAIL if Replay is loaded via `opaqueLayout`. FAIL if `#pause-replay` is missing from `web/index.html`.

**Attack:** `#pause-replay` missing from `index.html` FAILs the first assert. `opaqueLayout:` on the Replay params FAILs even if Play/Debug stay correct. A canvas next to `#foxglove` FAILs the canvas `rg` (same bar as ES-06).

---

### PR-05 — Control URL is `?control=` then `VITE_FOXGLOVE_CONTROL` then `http://localhost:8764`

- [x] `web/src/config.ts` (today `DEFAULT_WS_URL` / `readWsUrl` ~4–41) grows `DEFAULT_CONTROL_URL = "http://localhost:8764"` and `readControlUrl()` reading `?control=` then `VITE_FOXGLOVE_CONTROL` then the default. Do **not** derive the control port as WS-port-minus-one. `web/README.md` documents pairing `--port 8766` with an **explicit** `?control=` (8766 is already the WS-busy workaround; it is not a signal that control lives on 8765).

**Check:**

```sh
$PY <<'PY'
from pathlib import Path
cfg = Path("web/src/config.ts").read_text(encoding="utf-8")
assert 'DEFAULT_CONTROL_URL = "http://localhost:8764"' in cfg, cfg
assert "export function readControlUrl" in cfg, cfg
assert 'firstQuery("control")' in cfg or "firstQuery('control')" in cfg, cfg
assert "VITE_FOXGLOVE_CONTROL" in cfg, cfg
# order: query, then env, then default (same shape as readWsUrl)
fn = cfg.split("export function readControlUrl", 1)[1].split("export function", 1)[0]
assert "firstQuery" in fn and "VITE_FOXGLOVE_CONTROL" in fn and "DEFAULT_CONTROL_URL" in fn, fn
assert fn.find("firstQuery") < fn.find("VITE_FOXGLOVE_CONTROL") < fn.find("DEFAULT_CONTROL_URL"), fn

readme = Path("web/README.md").read_text(encoding="utf-8")
for needle in ("--control-port", "?control=", "VITE_FOXGLOVE_CONTROL", "8764"):
    assert needle in readme, needle
assert "8766" in readme and "?control=" in readme
# one documented example must mention both the 8766 WS workaround and an explicit control URL
assert any(("8766" in line and "control" in line.lower()) for line in readme.splitlines()), "no 8766+control pairing line"
assert "port-1" not in readme.lower() and "port minus 1" not in readme.lower()
print("PR-05 control-url")
PY
```

Quote `DEFAULT_CONTROL_URL = "http://localhost:8764"` and `export function readControlUrl` in `web/src/config.ts`. Quote the README example that pairs `--port 8766` with `?control=`. FAIL if the host assumes `controlPort === wsPort - 1`.

---

### PR-06 — `./web/check` still exits 0; compile-check includes Replay `selectLayout` + FileSource

- [x] From `$ROOT`, `./web/check` still typechecks (including `web/src/compile-check.ts`) and builds, prints `EMBED CHECK OK`, and exits 0. `compile-check.ts` (today SelectLayoutParams + live DataSource ~18–45) grows a Replay `selectLayout` params object (`layout`, `force: true`, not `opaqueLayout`) and a FileSource `DataSource` (`type: "file"`, `autoplay: true`). No browser.

**Check:**

```sh
./web/check
echo web_check_exit=$?
$PY <<'PY'
from pathlib import Path
import re
cc = Path("web/src/compile-check.ts").read_text(encoding="utf-8")
assert "replaySelectLayoutCompileCheck" in cc, cc
assert "fileSourceCompileCheck" in cc, cc
assert re.search(r"opaqueLayout\s*:", cc) is None, cc
assert "autoplay" in cc, cc
assert re.search(r'type:\s*["\']file["\']', cc), cc
print("PR-06 compile-check")
PY
```

PASS only if `./web/check` exits 0, stdout contains `EMBED CHECK OK`, and the quotes above exist. Quote `replaySelectLayoutCompileCheck` typed as `Parameters<FoxgloveViewer["selectLayout"]>[0]` (or the existing `SelectLayoutParams` alias) and `fileSourceCompileCheck` typed as `Parameters<FoxgloveViewer["setDataSource"]>[0]` (or the existing `DataSource` alias). FAIL if Replay compile-check uses `opaqueLayout`. FAIL if `./web/check` is skipped.

---

### PR-07 — `./smoke-pause-replay` records, `POST /pause`, `GET /recording`, asserts magic + RR-03 topics

- [x] From `$ROOT`, `./smoke-pause-replay` starts the **live** path with recording (`open_recording` + `run_loop` on a thread, `forever` / no `ticks=`), publishes **≥ 8** ticks, `POST /pause`, `GET /recording`, asserts MCAP magic and the six RR-03 topics (`/doom/camera`, `/doom/map`, `/tf`, `/doom/entities`, `/doom/player`, `/doom/log`) using `doom_foxglove/record.py` `list_mcap_topics` / `MCAP_MAGIC`. Binds ephemeral WS **and** control ports when 8765/8764 are busy (HL-12 spirit). Exit 0 prints `SMOKE-PAUSE-REPLAY OK` naming ticks, control URL, and file/bytes. Pattern to copy: `./smoke-replay` + `doom_foxglove/smoke_replay.py` (do not reuse `./smoke-replay` as this item's command).

**Check:**

```sh
test -f ./smoke-pause-replay
./smoke-pause-replay
echo smoke_pause_exit=$?
./smoke-pause-replay --immediate-pause
echo smoke_immediate_exit=$?
$PY <<'PY'
import ast
import inspect
from pathlib import Path

wrapper = Path("smoke-pause-replay").read_text(encoding="utf-8")
assert 'doom_foxglove.smoke_pause_replay' in wrapper, wrapper

from doom_foxglove.smoke_pause_replay import main as smoke_main
from doom_foxglove import smoke_pause_replay as sm_mod

src = inspect.getsource(sm_mod)

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

def thread_target_is_run_loop(c):
    return any(k.arg == "target" and is_run_loop_name(k.value) for k in c.keywords)

def thread_kwargs_keys(c):
    for k in c.keywords:
        if k.arg == "kwargs":
            return dict_str_keys(k.value)
    return None

tree = ast.parse(src)
sites = []
for n in ast.walk(tree):
    if not isinstance(n, ast.Call):
        continue
    name = call_name(n)
    if name == "run_loop":
        sites.append(("direct", n))
    elif name == "Thread" and thread_target_is_run_loop(n):
        sites.append(("thread", n))
assert sites, "smoke never calls run_loop"
for kind, c in sites:
    if kind == "direct":
        kw = {k.arg for k in c.keywords}
        assert "ticks" not in kw, "smoke must not stop the loop with ticks=; POST /pause must"
        assert "stop_event" in kw, kw
    else:
        keys = thread_kwargs_keys(c)
        assert keys is not None, "Thread(target=run_loop) must pass a kwargs dict"
        assert "stop_event" in keys, keys
        assert "ticks" not in keys, "smoke must not stop the loop with ticks=; POST /pause must"
assert src.count("/pause") >= 2 or src.count("_post_pause") >= 2, src
assert "/recording" in src, src
assert "list_mcap_topics" in src and "MCAP_MAGIC" in src, src
assert "open_recording" in src, src
assert "mcap.Writer" not in src, src
assert "fallback_if_busy" in src, src
print("PR-07 smoke-source")
PY
```

PASS only if both smoke invocations exit 0. Happy-path stdout must contain `SMOKE-PAUSE-REPLAY OK`, `ticks=`, `http://` (the control URL), and `bytes=` or `file=`, plus `pre_pause=409`, `double_pause=ok`, and `step_stopped=ok`. Immediate-pause stdout must contain `immediate_pause=ok` and must not raise. Quote `exec "$PY" -m doom_foxglove.smoke_pause_replay` in `./smoke-pause-replay` (same shape as `./smoke-replay`). Quote `_fail` returning 1. FAIL if the evaluator runs `./smoke-replay` instead of `./smoke-pause-replay`. FAIL if smoke never POSTs `/pause`. FAIL if 8765/8764 busy causes a non-zero exit (must bind ephemeral). FAIL if topics are trusted only from a print and `list_mcap_topics` is not called.

**Attack:** smoke that only calls `run_loop(..., ticks=8)` and never POSTs FAILs the AST `ticks` ban. Smoke that never POSTs FAILs `src.count("/pause")`. `GET` before pause is the `pre_pause=409` token. Double `POST /pause` is `double_pause=ok`. `--immediate-pause` is POST before any ticks.

---

### PR-08 — `--no-record`: POST still stops the engine; GET `/recording` is 409; embed says recording is off

- [x] Live default remains recording-on (RR-01). With `--no-record`, `POST /pause` still sets `stop_event` and returns 200 / `"paused": true`; `GET /recording` is **409**; the embed `#status` text mentions `recording is off`. Pick is locked: do **not** no-op the Pause button without pausing the engine; do **not** use 404 here.

**Check:**

```sh
./smoke-pause-replay --no-record
echo smoke_norecord_exit=$?
$PY <<'PY'
from pathlib import Path
found = False
for path in Path("web/src").glob("*.ts"):
    if "recording is off" in path.read_text(encoding="utf-8").lower():
        found = True
        break
assert found, "web/src must set #status mentioning recording is off"
print("PR-08 no-record-status")
PY
```

PASS only if `./smoke-pause-replay --no-record` exits 0 and stdout contains `no_record=409` and `step_stopped=ok` (engine stopped even though there is no file). Quote the embed string `recording is off` (case-insensitive) in `web/src`. Quote `if not args.no_record` still guarding `open_recording` in `server.py` `main` (RR-01). FAIL if `--no-record` leaves `run_loop` stepping. FAIL if GET is 404. FAIL if the Pause button no-ops and leaves the engine live.

**Attack:** `--no-record` plus `GET /recording` expecting 200 FAILs. A status string that only says `paused` without `recording is off` FAILs the quote.

---

### PR-09 — Pause is one-way; WASD is not required to replay; Play starts a **new** game

- [x] This slice does not require a Resume-live button of the **paused tick**. After pause, WASD/Teleop must not keep stepping the engine (`stop_event` already set). Host may `hold.stop()` / stop publishing; not required to keep the live WS. Replay visualization is FileSource + Replay layout + Foxglove playback bar — it must not depend on a keydown. Do not add `#resume` / `#resume-live` / `POST /resume`. **Play after pause is a new episode** (`POST /new-game`, UX-05/UX-07): `engine.reset()`, new sidecar, `run_loop` again — not resume of the paused tick. Presence of `POST /new-game` / `#layout-play` posting it does **not** FAIL this item.

**Check:**

```sh
$PY <<'PY'
from pathlib import Path
html = Path("web/index.html").read_text(encoding="utf-8")
assert 'id="resume' not in html, html
main = Path("web/src/main.ts").read_text(encoding="utf-8")
assert "pause-replay" in main
assert "addEventListener" in main and "click" in main
print("PR-09 one-way")
PY
rg -n -e 'id="resume' -e "id='resume" web/index.html
echo resume_btn_exit=$?
rg -n -e '"/resume"' -e "'/resume'" \
  doom_foxglove/server.py
echo resume_route_server_exit=$?
if test -f doom_foxglove/control.py; then
  rg -n -e '"/resume"' -e "'/resume'" \
    doom_foxglove/control.py
  echo resume_route_control_exit=$?
fi
```

The resume `rg` invocations must print nothing (ripgrep exits 1 on no match — PASS). `control.py` is searched only when that file exists (do not pass a missing path to `rg`). A comment that names resume as out of scope is allowed. FAIL if `web/index.html` grows `#resume` / `#resume-live`. FAIL if the only `#pause-replay` trigger is `keydown` (must be a `click` on the chrome button). Do **not** FAIL if `hold.stop()` is absent. Do **not** FAIL because WASD still exists for the live Play path (ES-04). Do **not** FAIL because Play POSTs `/new-game` (that is a new game, UX-05/UX-07, not `/resume`).

**Attack:** a Resume-live button or `POST /resume` that clears `stop_event` without `engine.reset()` is a FAIL. Requiring WASD to start playback is a FAIL (FileSource `autoplay: true` is PR-04). `POST /new-game` is the allowed successor and does **not** FAIL.

---

### PR-10 — Scope fence (no resume-cloud-comparison; no workstream 06)

- [x] Pause-replay files do not implement resume-live, cloud upload, share URL, Data Platform, comparison mode, remote spectator, events tagging UI, mouse-look, host `<canvas>` / `getContext`, custom `.foxe`, rosbridge, commercial WAD, or audio. They do not rewrite Play/Debug layouts, change topic schemas, replace Teleop, or switch Play/Debug back to `opaqueLayout`. They do not edit `.agent/workstreams/01-hero-loop/contract.md` or `02-robotics-layout/contract.md`. They do not create `.agent/workstreams/06-*`. ES-11's carve-out is graded on 03, not here.

04-owned pause-replay files for this item: `doom_foxglove/server.py` (control-plane additions), `doom_foxglove/control.py` if present, `doom_foxglove/smoke_pause_replay.py`, `./smoke-pause-replay`, `web/src`, `web/index.html`. Do **not** search `web/node_modules`, `web/dist`, `.agent/workstreams/05-stunt-extras/`, or 01/02 contracts.

**Check:**

```sh
$PY -c "from pathlib import Path; xs=sorted(p.name for p in Path('.agent/workstreams').glob('06-*')); assert not xs, xs; print('no-06')"
echo '---'
rg -n -e 'comparison.mode' -e 'remote.spectator' -e 'upload_recording' -e 'FOXGLOVE_API' \
  -e 'data\.foxglove\.dev' -e 'rosbridge' -e 'PlaybackBar' -e 'pointerlock' -e 'mouse-look' \
  -e '\.foxe' \
  doom_foxglove/server.py web/src web/index.html
echo fence_exit=$?
for p in doom_foxglove/control.py doom_foxglove/smoke_pause_replay.py smoke-pause-replay; do
  if test -e "$p"; then
    rg -n -e 'comparison.mode' -e 'remote.spectator' -e 'upload_recording' -e 'FOXGLOVE_API' \
      -e 'data\.foxglove\.dev' -e 'rosbridge' -e 'PlaybackBar' -e 'pointerlock' -e 'mouse-look' \
      -e '\.foxe' \
      "$p"
    echo fence_extra_$p=$?
  fi
done
rg -n -e 'opaqueLayout\s*:' web/src/layouts.ts web/src/compile-check.ts web/src/main.ts
echo opaque_exit=$?
```

PASS if `no-06` prints and no `06-*` directory exists. PASS if every `rg` invocation prints nothing, **or** every printed line is a comment that names the extra as out of scope (not an API call). Optional files are searched only when they exist (do not pass a missing path to `rg`). `setDataSource` / `FileSource` / `type: "file"` in `web/src` are **required** by PR-04 and do **not** FAIL this item. Existing `EVENTS_TOPIC` import and `events={EVENTS_TOPIC}` banner in `doom_foxglove/server.py` are the RR-07 helpers and do **not** FAIL. FAIL if `opaqueLayout:` appears in the Replay/Play/Debug host params (second `rg` must print nothing). FAIL if a `06-*` workstream directory exists. Do **not** FAIL 04 because ES-11 was amended; that carve-out is 03's item.

**Attack:** implementing comparison / spectator / rosbridge / resume-live / cloud upload in the files above FAILs. Inventing workstream 06 FAILs. A PR item that required rewriting `layouts/Play.json` / `layouts/Debug.json` or 01/02 contracts would be a contract defect — none of PR-01…PR-09 require those files to change.
