status: planning complete
owner: Planner (cursor-grok-4.6-high-fast)
updated: 2026-09-18
next action: entry conditions (1)–(2) — KG capabilities done + 01/02/03 eval verdicts done — owned by those loops; then un-defer ws_05_stunt_extras
blockers: none

# Progress — 05-stunt-extras

Planner applied `critique.md` amendments 1–4 to this workstream `contract.md` only. Product code is unchanged this run. No boxes were ticked.

## State

`PLAN.md` still holds the phase spec. `contract.md` is the amended SX-01…SX-06 list (awaiting Kimi critic re-gate). Product code already exists: `/doom/events` JSON `{ kind, message, tick, map }` with `kind` in `death|weapon|level|pickup`; `./smoke-events` writes `recordings/smoke-events.mcap`; README has three copy-paste Foxglove agent/MCP prompts.

Workstream KG node stays `deferred` until the critic gates this list. `cap_live_ws_camera_teleop`, `cap_3d_map_hud`, and `cap_embed_page` are still not `done`; entry conditions (1) and (2) remain unmet. This amended contract is still the missing (3).

Skipped (named in SX-06, not required): remote-access gateway, comparison mode UI, cloud share links, ViZDoom policy vs human.

## What's left

1. ~~Kimi critic (kimi-k3-high) attacks SX-01…SX-06 and returns amendments or a gate.~~ Done 2026-09-18: **FAIL**, four amendments in `critique.md`.
2. ~~Planner applies amendments 1–4 to this workstream `contract.md` only (nits optional), then re-submits to the critic.~~ Done 2026-09-18: amendments 1–4 landed; nits left untouched.
3. ~~Critic re-gates the amended contract.~~ Done 2026-09-18: **PASS**, recorded in `critique.md`.
4. ~~Evaluator runs `./smoke-events` from a clean shell and ticks boxes.~~ Done 2026-09-18: **PASS 6/6** (SX-01…SX-06), failing ids none; boxes ticked in `contract.md`, evidence in `eval.md`. Generator did not tick.

## Amendments applied (2026-09-18, planner)

1. **SX-06** — any `rg` printed line is FAIL; comments are not exempt. Out-of-scope naming lives in `README.md` `## Not in this slice`.
2. **SX-06** — fence target is `smoke-events` plus all of `doom_foxglove/`. `web/` stays 03.
3. **SX-03** — negative path must exit 1 **and** stderr/captured output contain `SMOKE-EVENTS FAIL: critic-injected`.
4. **SX-05** — prose narrowed to the existing three-token `rg` (`FastMCP`, `langchain`, `@modelcontextprotocol`). Tokens not widened.

## Critic gate (2026-09-18, kimi-k3-high)

**FAIL** (first gate) — see `critique.md`. Amendments 1–4 are now in `contract.md`. Re-gate is the next action.

## Critic re-gate (2026-09-18, kimi-k3-high)

**PASS** — all four amendments verified in `contract.md`; both fence `rg` invocations re-run from `$ROOT` with zero hits, so the stricter rules are satisfiable by the current tree. SX-01…SX-06 are mechanical. Entry condition (3) is met; (1) and (2) remain unmet and are owned by the 01/02/03 loops. Next: Kimi evaluator ticks SX items.

## Evaluator SX verdict (2026-09-18, kimi-k3-high)

Ran every SX-01…SX-06 check verbatim from a clean shell at `$ROOT` against the critic-gated contract. **PASS 6/6, failing ids: none.** All six checkboxes in `contract.md` ticked by the evaluator. `./smoke-events` exit 0 (`live=1`, `mcap_events=1`, backend=vizdoom, ephemeral bind on busy 8765 — HL-12 note); negative path exit 1 with exact stderr banner `SMOKE-EVENTS FAIL: critic-injected`; MCAP parsed with in-repo `count_mcap_messages` (count 1 ≥ 1); README prompts verbatim; both fence `rg` invocations clean. Full evidence in `eval.md`. Entry conditions (1) and (2) remain unmet and are owned by the 01/02/03 loops — this verdict does not un-defer `ws_05_stunt_extras`.

## Evaluator note (2026-09-18, kimi-k3-high)

Verdict on the generator's thin-slice run is recorded in `eval.md`: **product PASS / process FAIL (SX-CONTRACT-GATE)** — the generator ran while `contract.md` was still the deferral stub; all three entry conditions were unmet. `./smoke-events` reproduced at exit 0; `/doom/events` verified live and in the MCAP (independent zstd decode); all four kinds exercised through real code; three README prompts confirmed verbatim; declared skips confirmed absent. Evidence is pre-staged against SX-01…SX-06 in the `eval.md` addendum, but **no boxes are ticked** — the SX list awaits the critic re-gate, and entry conditions (1) and (2) are still unmet. Side finding: harness self-check is red (H-17, `01-hero-loop/progress.md` status `gated` outside vocabulary; owned by 01's loop).
