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
