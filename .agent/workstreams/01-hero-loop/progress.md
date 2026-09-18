status: done
owner: Planner (cursor-grok-4.6-high-fast)
updated: 2026-09-18
next action: none for 01 — all 14 HL items ticked (evaluator re-run 2026-09-18: HL-05 and HL-14 PASS under E-R1/E-R2). 02-robotics-layout continues on its own track.
blockers: none

# Progress — 01-hero-loop

Hero-loop product code lives in `doom_foxglove/`. The numbered HL-01…HL-14 contract is critic-gated PASS (C-1…C-8 plus R-1/R-2). Evaluator 2026-09-18: 12/14 PASS; HL-05 and HL-14 failed as written (contract-check defects). Planner applied E-R1/E-R2. `02-robotics-layout` continues on its own track; do not treat this gate as a stop on 02.

## State

`PLAN.md` holds the phase spec. `contract.md` is the gradeable HL-nn list. Smoke command is `./smoke` from repo root; HL-09 and HL-12 step 2 grade `./smoke --hero`. Port 8765 busy (external process) is an environment note; smoke binds ephemeral (HL-12).

Evaluator-ticked (leave alone): HL-01, HL-02, HL-03, HL-04, HL-06, HL-07, HL-08, HL-09, HL-10, HL-11, HL-12, HL-13.

Unticked (evaluator ink; planner did not tick):

- HL-05: check now uses callable-safe `ch.topic` — call if callable else compare — so the installed SDK method `topic()` equals `CAMERA_TOPIC`. Product already publishes `/doom/camera` as JPEG 320×200 at 35 Hz.
- HL-14: rg now includes `--glob '!**/node_modules/**'` in addition to `.venv` / `.git` / `.agent` / `*.md`. Product files already have zero canvas matches.

## What's left

1. ~~Kimi critic attacks HL-01…HL-14 and returns amendments or a gate.~~ Done 2026-09-18: **FAIL**, amendments C-1…C-8 in `critique.md`.
2. ~~Planner applies critic amendments C-1…C-8 (same workstream `contract.md` only).~~ Done 2026-09-18.
3. ~~Kimi critic re-gates the amended contract.~~ Done 2026-09-18: **FAIL**, 2 one-line amendments R-1/R-2 in `critique.md` (C-1…C-8 verified applied and mechanical).
4. ~~Planner applies R-1 (HL-12 step 2 → `./smoke --hero`) and R-2 (anchor HL-13 commercial-WAD clause).~~ Done 2026-09-18.
5. ~~Kimi critic re-gates the R-1/R-2 amended contract.~~ Done 2026-09-18: **PASS** — contract gates; full audit in `critique.md` (Re-gate 2).
6. ~~Grok generator implements remaining HL product gaps.~~ Done 2026-09-18. Generator did not tick boxes.
7. ~~Kimi evaluator re-runs the gated checks.~~ Done 2026-09-18: **FAIL 12/14** — HL-01…04, 06…13 ticked; HL-05 and HL-14 fail as written, both contract-check defects. Full evidence in `eval.md`.
8. ~~Planner applies E-R1/E-R2.~~ Done 2026-09-18.
9. ~~Kimi critic re-gates E-R1 (HL-05 callable-safe topic) and E-R2 (HL-14 node_modules glob).~~ Done 2026-09-18: **PASS** (Re-gate 3 in `critique.md`).
10. ~~Kimi evaluator re-runs HL-05 and HL-14.~~ Done 2026-09-18: **PASS 14/14** — both boxes ticked; evidence in `eval.md` (Re-eval). 01-hero-loop is done. 02 continues on its own track.
