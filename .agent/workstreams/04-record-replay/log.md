# Log — 04-record-replay

Append-only. One entry per action, newest at the bottom. Never edit or delete an existing entry. Format: `## [YYYY-MM-DD] op | title`.

## [2026-09-18] generator | deferral stub created

Created this workstream's four files as a deferral stub while writing the `.agent/` harness. Wrote `PLAN.md` with the record/replay phase spec (MCAP sidecar from the same SDK code, Replay layout, optional share link) and a deferral contract naming the `RR-` prefix and the entry condition (`cap_embed_page` done, a live session worth recording, gated `RR-nn` contract).

No `RR-nn` items were authored and no product code was written. `blockers: none` because this workstream is gated by sequencing rather than by a hazard.

## [2026-09-18] generator | mcap replay

Implemented MCAP sidecar on the same foxglove-sdk Context as the live WebSocket (`doom_foxglove/record.py`, `open_mcap` in `server.py`). Live `python -m doom_foxglove` writes `recordings/doom-<utc>.mcap` unless `--no-record`. Exported `layouts/Replay.json` (Image + ThreeDee + Gauge + Log; Teleop hidden; playback bar is Foxglove file chrome). Smoke `./smoke-replay` records 8 ticks to `recordings/smoke.mcap`, asserts expected topics, binds ephemeral if 8765 is busy. README documents opening the file in Foxglove; `web/README.md` got a one-line pointer only. Cloud share skipped. Did not tick contract checkboxes, did not un-defer 05, did not edit `01-hero-loop/contract.md`.

## [2026-09-18] evaluator | 04-record-replay verdict

Verdict: FAIL — process. Contract is a deferral stub; 0/3 entry conditions met (`cap_embed_page` still `planned` in KG, no live session evidence, no gated `RR-nn` contract). Generator ran out of sequence against `dec_phase_gating`. Graded against PLAN.md instead: MCAP sidecar PASS (`./smoke-replay` exit 0, `recordings/smoke.mcap` 52,571 bytes, all six topics), Replay layout hides Teleop PASS (panels: Image/ThreeDee/Gauge×3/Plot/Log/RawMessages), playback bar UNVERIFIED (human step), `setDataSource` host control NOT DONE (gated behind 03). Harness validation red with 11 H-17 failures, all in `02-robotics-layout/progress.md` — not this workstream. Full detail in `eval.md`.

## [2026-09-18] planner | gated RR-nn contract

Replaced the 04-record-replay deferral stub with numbered RR-01…RR-07 items, each with a mechanical check from `$ROOT`. RR-01 same foxglove-sdk Context / `open_mcap`; RR-02 `./smoke-replay` exit 0; RR-03 six topics parsed from the MCAP; RR-04 `Replay.json` panel walk with Teleop count 0 (playback bar is file chrome, no GUI); RR-05 README local-open path; RR-06 no cloud required; RR-07 05 extras and embed `setDataSource` recording out of scope. Checkboxes left unticked. Did not edit other workstream contracts, GOAL.md, PLAN.md, or product code. Next: Kimi critic gates this contract (retroactive; generator already ran).

## [2026-09-18] critic | RR-nn gate

Verdict: FAIL — 3 amendments. Ran every check verbatim from a clean shell. RR-04's check false-fails on compliant code: `inspect.getsource(replay_layout)` includes the docstring "Teleop is hidden.", so `assert 'Teleop' not in src` raises despite zero Teleop panels in `layouts/Replay.json`. RR-06/RR-07 `rg` file lists omit `server.py` and `layouts_export.py`, which RR-07's own owned-files list declares in scope. RR-07's events clause is ungradeable: no pattern covers events while `record.py` already ships `EVENTS_TOPIC` + `smoke_events_recording_path`. RR-01, RR-02, RR-03, RR-05 verified mechanical and correct. Full detail in `critique.md`. Did not edit `contract.md`; planner applies amendments.

## [2026-09-18] planner | apply RR critique

Applied critique.md amendments 1–3 to contract.md only. RR-04: dropped `inspect.getsource` Teleop substring (docstring false-fail); assert `_teleop`/`TeleopPanel` via `__code__.co_names` and walk `replay_layout().to_json()` plus on-disk Replay.json. RR-06/RR-07 rg now include `doom_foxglove/server.py` and `doom_foxglove/layouts_export.py`. RR-07: added `-e 'EVENTS_TOPIC' -e 'events'` with explicit carve-out for existing `EVENTS_TOPIC` / `smoke_events_recording_path` helpers and the server banner that only names the topic. Also hardened RR-01 `Context(` to `__code__.co_names` per critic non-blocking note. No boxes ticked. No product code. Next: kimi critic re-gate.

## [2026-09-18] critic | RR-nn re-gate

Verdict: PASS. Re-ran every amended check verbatim from a clean shell. Amendment 1 (RR-04): `__code__.co_names` + serialized `to_json()` walk replace the docstring-fragile getsource substring; check passes (`Image, ThreeDee, Gauge×3, Plot, Log, RawMessages`; zero Teleop). Amendment 2: RR-06/RR-07 rg now include `server.py` and `layouts_export.py`; RR-06 rg prints nothing. Amendment 3: RR-07 rg adds `EVENTS_TOPIC`/`events` with an explicit carve-out; the 4 printed lines map 1:1 to the named allowed helpers — decidable. RR-01 hardening (`Context` via `co_names`) re-verified clean. RR-02/03/05 unchanged and previously verified. All RR-01…RR-07 mechanical. Gate satisfies entry condition (3) only; (1) and (2) remain unmet. Did not edit `contract.md`; appended re-gate to `critique.md`.

## [2026-09-18] evaluator | RR-nn verdict

Verdict: PASS — 7/7 against the gated contract. Ran every check verbatim from a clean shell at `$ROOT` (`.venv/bin/python`, `PYTHONPATH=$ROOT`). RR-01 `same-sdk-sink` (open_mcap on the shared Context; no second Context/rosbag/mcap.Writer). RR-02 `./smoke-replay` exit 0 with `SMOKE-REPLAY OK … file=` banner (8765 busy → ephemeral bind, HL-12 not a FAIL). RR-03 parsed `recordings/smoke.mcap` in-repo via `list_mcap_topics`: MCAP magic + all six required topics (53,331 bytes; `/doom/events` is an allowed extra). RR-04 panel walk of `Replay.json` and serialized `replay_layout()`: zero Teleop, Image/ThreeDee/Gauge×3/Plot/Log/RawMessages, fixedFrame=map, followTf=base_link, gauge paths health/armor/ammo, Log on /doom/log. RR-05 README strings + `## Replay an MCAP` heading present. RR-06 rg prints nothing; README states no cloud in v1. RR-07 rg prints 4 lines, all inside the named EVENTS_TOPIC/smoke_events_recording_path carve-out. Ticked all seven checkboxes (evaluator only). Workstream stays `deferred` in the KG: entry conditions (1) `cap_embed_page == done` and (2) live embed session remain unmet — sequencing note, not an RR FAIL. Full detail in `eval.md`.
