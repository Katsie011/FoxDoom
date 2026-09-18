# Eval — 04-record-replay

**Evaluator:** kimi-k3-high
**Date:** 2026-09-18
**Verdict: FAIL — process.** The generator ran against a deferral stub that explicitly forbids it. The artifact itself passes every headless check I could run, but there is no graded contract to accept it against, and the gating capability is not done.

## Contract status: stub (not gradeable)

`contract.md` states: *"This file is a deferral stub, not a gradeable contract. No generator may run against it and no evaluator may grade it until the entry condition below is met."* Entry conditions, checked against the knowledge graph:

| # | Entry condition | Evidence | Met? |
|---|---|---|---|
| 1 | `cap_embed_page` is `done` in the KG | `nodes.jsonl:28` — `"status": "planned"` | **NO** |
| 2 | Human finished a short live session in the embed | No evidence on disk; embed (03) is itself `deferred` | **NO** |
| 3 | Planner wrote a real `RR-nn` contract, critic gated it | No `RR-nn` items exist anywhere in the workstream | **NO** |

Zero of three entry conditions hold. `ws_04_record_replay` is still `status: deferred` in the KG (`nodes.jsonl:23`), and `dec_phase_gating` is locked. **Missing RR-nn contract: process FAIL.** The generator's deliverable, however competent, is uncontracted work produced out of sequence.

## Grading against PLAN.md (since the contract is a stub)

| PLAN.md item | Result | Evidence |
|---|---|---|
| MCAP logging with the same SDK code | **PASS** | `record.py` attaches `foxglove.open_mcap` to the same Context as the live WebSocket; smoke proves both sinks live |
| Every session is a recording | **PASS** | `python -m doom_foxglove` writes `recordings/doom-<utc>.mcap` unless `--no-record` (README.md:66) |
| Replay layout: hide Teleop | **PASS** | `layouts/Replay.json` panels: Image, ThreeDee, Gauge ×3, Plot, Log, RawMessages. No Teleop panel anywhere in the file |
| Replay layout: show playback bar | **UNVERIFIED (human step)** | Playback bar is Foxglove file-source chrome; cannot be proven headless. Progress.md correctly lists this as a human check |
| Optional shareable recording link | **SKIPPED (allowed)** | PLAN marks it optional; generator deferred it to 05 |
| `setDataSource({live|remote-file|recording})` host control | **NOT DONE** | Belongs to the embed host (03, deferred); README.md:105 explicitly keeps `web/` live-only. Acceptable given gating, but the PLAN line is unmet |

## Smoke test (run by evaluator, clean shell)

```
$ ./smoke-replay
SMOKE-REPLAY OK ticks=8 published=8 file=recordings/smoke.mcap bytes=52571
topics=['/doom/camera', '/doom/entities', '/doom/log', '/doom/map', '/doom/player', '/tf']
EXIT=0
```

- Exit code: **0** (claim verified)
- `recordings/smoke.mcap` exists, 52,571 bytes, all six claimed topics present (claim verified)
- Ephemeral port fallback worked (8765 was busy during my run)

## Harness check

`python3 .agent/knowledge-graph/validate.py --harness` exits **1** — 11 H-17 failures, all in `02-robotics-layout/progress.md` (bad status vocabulary, prose in the blockers field). Not caused by this workstream, but the harness is currently red and 02's generator should fix it.

## What the generator got right

- Did not tick contract checkboxes, did not un-defer 05, did not touch `01-hero-loop/contract.md`.
- Honestly reported in `progress.md` that the contract remains a stub.
- The code matches the claims; nothing in the smoke output is exaggerated.

## Required to reach a gradeable state

1. Un-defer per the entry conditions (03 done first), or get an explicit human override recorded on disk.
2. Planner authors real `RR-nn` items; Kimi K3 contract critic gates them.
3. Re-run this evaluation against that contract, including the human playback-bar check.

---

# Eval — 04-record-replay (gated RR-01…RR-07)

**Evaluator:** kimi-k3-high (did not author the contract, did not write product code)
**Date:** 2026-09-18
**Target:** amended `contract.md` RR-01…RR-07 (critic re-gate PASS, `critique.md`)
**Verdict: PASS — 7/7.** Every check was run verbatim from a clean shell at `$ROOT` (`.venv/bin/python`, `PYTHONPATH=$ROOT`). I was told record/replay is broken; I could not prove it. Checkboxes ticked by this evaluator only.

| Item | Result | Evidence |
|---|---|---|
| RR-01 same-SDK sink | **PASS** | Check prints `RR-01 same-sdk-sink`. Quoted literals present: `foxglove.open_mcap` (record.py:62); `from doom_foxglove.record import … open_recording` (server.py:28); `if not args.no_record` (server.py:236); `writer = open_recording` (server.py:238, smoke_replay.py:85). No `Context(` in `open_recording.__code__.co_names`; no `rosbag`/`mcap.Writer`. |
| RR-02 `./smoke-replay` exit 0 | **PASS** | Ran `./smoke-replay` from `$ROOT`: exit 0, stdout contains `SMOKE-REPLAY OK` and `file=` (`ticks=8 published=8 file=…/recordings/smoke.mcap bytes=53331`). `exec "$PY" -m doom_foxglove.smoke_replay` (smoke-replay:12). `_fail` + `return 0` after the OK print (smoke_replay.py:101-109). `_check_replay_layout` called from `main` (smoke_replay.py:58). 8765 was busy; ephemeral bind note printed — HL-12, not a FAIL. |
| RR-03 topics in MCAP | **PASS** | Check prints `RR-03 … bytes 53331 topics ['/doom/camera', '/doom/entities', '/doom/events', '/doom/log', '/doom/map', '/doom/player', '/tf']`. File starts with MCAP magic; all six required topics present (`/doom/events` is an allowed extra). `EXPECTED_TOPICS` (record.py:23-30) equals the six-string tuple via constants in `doom_foxglove/__init__.py:7-14`. `list_mcap_topics` walks `OP_CHANNEL` (record.py:20, 96, 108). File parsed in-repo, not trusted from the smoke banner. |
| RR-04 Replay.json, no Teleop | **PASS** | Check prints `RR-04 ['Image', 'ThreeDee', 'Gauge', 'Gauge', 'Gauge', 'Plot', 'Log', 'RawMessages']`. Zero Teleop in both the serialized `replay_layout().to_json()` tree and on-disk `layouts/Replay.json` (walked `type == "panel"` nodes, no substring search). `_teleop`/`TeleopPanel` absent from `__code__.co_names`. `version == 1`; Image on `/doom/camera`; ThreeDee `fixedFrame=map`, `followTf=base_link`, `/doom/map` visible + `/doom/entities` in topics; Gauge paths include health/armor/ammo; Log `topicToRender=/doom/log`. `("Replay.json", replay_layout())` quoted at layouts_export.py:243. Docstring naming Teleop not failed, per contract. |
| RR-05 README replay doc | **PASS** | Check prints `RR-05 readme-ok`. All four strings present (`./smoke-replay`, `layouts/Replay.json`, `recordings/smoke.mcap`, `playback bar`) plus local-open instruction; `## Replay an MCAP` heading at README.md:90. Foxglove GUI not opened, per contract. |
| RR-06 no cloud required | **PASS** | `rg` invocation prints nothing (exit 1 = PASS per contract). No `FOXGLOVE_API`, `data.foxglove.dev`, `upload_recording`, or `DeviceCode` in any 04-owned file. README contains `cloud` ("no cloud share link in v1"); check prints `RR-06 local-only`. |
| RR-07 05 extras out of scope | **PASS** | `rg` prints exactly 4 lines, each mapping 1:1 to the named carve-out: `EVENTS_TOPIC` import (server.py:19), `events={EVENTS_TOPIC}` banner (server.py:230), `smoke_events_recording_path` def + body (record.py:52-53). No comparison-mode, remote-spectator, `setDataSource`, or agent-prompt lines. `web/` and `05-stunt-extras/` not searched, per contract. |

## Sequencing note (not an RR FAIL)

Entry condition (3) is met (critic re-gate PASS). Conditions (1) `cap_embed_page == done` and (2) a completed live embed session remain unmet, so `ws_04_record_replay` stays `deferred` in the KG. The Phase-DAG "deferred because cap_embed_page is planned" note is sequencing only; it did not excuse skipping RR-01…RR-07, and all seven were run. The human playback-bar click remains a documented manual step (RR-05), not a headless FAIL.

---

# Eval — 04-record-replay PR-01…PR-10 (pause-replay slice)

**Evaluator:** kimi-k3-high
**Date:** 2026-09-18
**Verdict: PASS — 10/10.** Every PR Check run verbatim from a clean shell at `$ROOT` (`.venv/bin/python`, `PYTHONPATH=$ROOT`). RR-01…RR-07 left ticked; not re-graded. `./smoke-replay` re-run as a regression note only (see below). ES-11 on `03-embed-shell/contract.md` re-run as a regression (see below). No product code edited; only PR checkboxes ticked.

| Item | Result | Evidence |
|---|---|---|
| PR-01 stdlib control plane 8764 | **PASS** | Check prints `PR-01 control-plane`. Quotes: `--control-port` + `default=8764` argparse (server.py:230), `start_control(` called from `main` (server.py:252), `control http://` banner (server.py:253). `start_control` in `doom_foxglove/control.py` uses `ThreadingHTTPServer`, no `foxglove.start_server`, signature has `fallback_if_busy`. `rg` for rosbridge/flask/fastapi/aiohttp over server.py + control.py prints nothing (exit 1). |
| PR-02 POST /pause stops step, closes writer | **PASS** | Check prints `PR-02 pause-stops-step`. `run_loop` signature has `stop_event=None` default; `co_names` contains `is_set`, `wait`, `step`. Quotes: `stop_event` param (server.py:172), poll `stop_event.is_set()` (server.py:182) and `stop_event.wait(timeout=...)` (server.py:201), `writer.close()` on pause path (control.py:32; also server.py:262). `foxglove.open_mcap` still only in record.py:62. Control module has `/pause`, `do_OPTIONS`, `Access-Control-Allow-Origin`; no `mcap.Writer`, no `rosbag`. |
| PR-03 GET /recording bytes, CORS, 409 | **PASS** | Check prints `PR-03 get-recording`. `MCAP_MAGIC == b"\x89MCAP0\r\n"`. Quotes: `application/octet-stream` (control.py:96), `Access-Control-Allow-Origin` (control.py:56, `CORS_ORIGIN = "*"`), 409 branch before pause (control.py:91-92 `self._json(409, {"error": "recording not available"})`). Runtime 409/200 proof under PR-07. |
| PR-04 embed #pause-replay FileSource + layout | **PASS** | Check prints `PR-04 embed-button`. `id="pause-replay"` is a `<button>` labelled `Pause & replay`, appears before `id="foxglove"`; no `<canvas` in index.html. `web/src/layouts.ts` imports `layouts/Replay.json`, exports `replayLayoutData` and `replayLayoutParams()` with `storageKey`/`layout`/`force: true`; no `opaqueLayout:`. Click handler quoted at main.ts:65-85: POST `${controlUrl}/pause`, GET blob, `new File([blob], "doom.mcap")`, `viewer.setDataSource({ type: "file", file, autoplay: true })`, `viewer.selectLayout(replayLayoutParams())`. All three `rg` fences (PlaybackBar, canvas/getContext, pause-replay in layouts/) print nothing (exit 1). |
| PR-05 control URL precedence | **PASS** | Check prints `PR-05 control-url`. Quotes: `DEFAULT_CONTROL_URL = "http://localhost:8764"` and `export function readControlUrl` in web/src/config.ts; order query → env → default verified by the Check's `find` asserts. web/README.md contains `--control-port`, `?control=`, `VITE_FOXGLOVE_CONTROL`, `8764`, and a line pairing `8766` with an explicit control URL; no `port-1` / `port minus 1`. |
| PR-06 ./web/check + compile-check | **PASS** | `./web/check` exits 0, stdout ends `EMBED CHECK OK` (tsc --noEmit && vite build, 20 modules). Check prints `PR-06 compile-check`. Quotes: `replaySelectLayoutCompileCheck: SelectLayoutParams` with `layout: replayLayoutData`, `force: true` (compile-check.ts:38-42); `fileSourceCompileCheck: DataSource` with `type: "file"`, `autoplay: true` (compile-check.ts:43-46). No `opaqueLayout:` in compile-check.ts. |
| PR-07 ./smoke-pause-replay | **PASS** | `test -f ./smoke-pause-replay` ok. Happy path exit 0: `pre_pause=409`, `double_pause=ok`, `step_stopped=ok`, `SMOKE-PAUSE-REPLAY OK ticks=9 http://127.0.0.1:8764 file=.../recordings/smoke-pause.mcap bytes=59359 topics=[/doom/camera, /doom/entities, /doom/events, /doom/log, /doom/map, /doom/player, /tf]` (all six RR-03 topics present; extras allowed). `--immediate-pause` exit 0 with `immediate_pause=ok`, `ticks=0`. AST check prints `PR-07 smoke-source`: `Thread(target=run_loop, kwargs={... "stop_event" ...})`, no `ticks` key. Wrapper quotes `exec "$PY" -m doom_foxglove.smoke_pause_replay "$@"` (smoke-pause-replay:12). `_fail` returns 1 (smoke_pause_replay.py:28-30). |
| PR-08 --no-record | **PASS** | `./smoke-pause-replay --no-record` exits 0; stdout contains `no_record=409` and `step_stopped=ok` (engine stopped with no file). Embed string quoted: `setStatus("Paused, but recording is off.")` (main.ts:73). `if not args.no_record` still guards `open_recording` (server.py:246). |
| PR-09 one-way pause | **PASS** | Check prints `PR-09 one-way`. No `id="resume` in web/index.html; `#pause-replay` trigger is `addEventListener("click", ...)` (main.ts:65). All three resume `rg` invocations (index.html, server.py, control.py) print nothing (exit 1). |
| PR-10 scope fence | **PASS** | `no-06` printed; no `.agent/workstreams/06-*`. All fence `rg` invocations (server.py + web/src + web/index.html; control.py; smoke_pause_replay.py; smoke-pause-replay) print nothing (exit 1). `opaqueLayout\s*:` rg over layouts.ts/compile-check.ts/main.ts prints nothing (exit 1). |

## Regression notes (not re-grades)

- **RR-02 implication:** `./smoke-replay` re-run after the `run_loop(stop_event=None)` change: exit 0, `SMOKE-REPLAY OK ticks=8 published=8 file=.../recordings/smoke.mcap bytes=59366` with all six required topics. The optional-kwarg contract holds; PR-02's "do not break run_loop ticks=" implication is satisfied.
- **ES-11 (03-embed-shell):** run verbatim. `rg` forbid-list over web/src + web/index.html + web/package.json prints nothing (exit 1); carve-out script prints `ES-11 carve-out-ok files 12`. ES-11 stays PASS; no PR-04/PR-10 process note needed.

## Environment notes

8765/8764 were free during this eval; smoke bound the defaults directly. Ephemeral fallback path (`fallback_if_busy`) is present in `start_control` and the smoke source per the Checks but was not exercised at runtime.
