status: deferred
owner: Evaluator (kimi-k3-high)
updated: 2026-09-18
next action: un-defer requires cap_embed_page done (03) plus a live embed session; then human playback-bar spot-check per RR-05
blockers: none

# Progress — 04-record-replay

Planner applied `critique.md` amendments 1–3 to this workstream `contract.md` only. Product code is unchanged. No boxes were ticked.

## State

`PLAN.md` still holds the phase spec. `contract.md` is the amended RR-01…RR-07 list, gated PASS by the Kimi critic on 2026-09-18 (re-gate in `critique.md`). Product code already exists: same `foxglove-sdk` Context writes the live WebSocket and an MCAP sidecar; `layouts/Replay.json` hides Teleop; `./smoke-replay` writes `recordings/smoke.mcap`. Eval 2026-09-18 FAILed on process (stub, not product). First critic gate 2026-09-18 FAILed with three check bugs; those checks are now rewritten.

Critic gate (entry condition 3) is now PASS. The KG node stays `deferred` because `cap_embed_page` is still `planned` and no live embed session is on record — entry conditions (1) and (2) remain unmet.

**Evaluation 2026-09-18 (second run, against the gated contract): PASS — 7/7.** Every RR check was run verbatim from a clean shell at `$ROOT`, including `./smoke-replay` (exit 0, `SMOKE-REPLAY OK`, 53,331-byte `recordings/smoke.mcap` with all six required topics). The evaluator ticked all seven checkboxes. Full detail in `eval.md`. This PASS grades the RR-01…RR-07 items only; it does not un-defer the workstream — that still waits on 03 (`cap_embed_page`) and a live embed session.

## What's left

1. ~~Kimi critic (kimi-k3-high) attacks RR-01…RR-07~~ — DONE 2026-09-18: **FAIL**, 3 amendments in `critique.md`.
2. ~~Planner applies the 3 amendments to this workstream `contract.md` only~~ — DONE 2026-09-18.
3. ~~Kimi critic (kimi-k3-high) re-gates the amended RR-01…RR-07 list~~ — DONE 2026-09-18: **PASS**, re-gate appended to `critique.md`.
4. ~~After gate: evaluator re-runs `./smoke-replay` against the gated items~~ — DONE 2026-09-18: **PASS 7/7**, all boxes ticked by the evaluator.
5. Un-defer `ws_04_record_replay` once `cap_embed_page` is `done` and a live embed session is on record; human playback-bar spot-check per RR-05 at that point.
