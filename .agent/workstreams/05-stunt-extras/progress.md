status: done
owner: Evaluator (kimi-k3-high)
updated: 2026-09-18
next action: none for section F — UX-01…UX-14 PASS 14/14; workstream un-defer still gated on entry conditions (1) and (2) owned by 01/02/03 loops
blockers: none

# Progress — 05-stunt-extras

Generator implemented section F UX-01…UX-14 product code. SX-01…SX-06 stay evaluator-ticked. No boxes were ticked this run. No workstream `06-*`. No `.foxe` / `installExtensions` / canvas HUD.

## Generator (2026-09-18)

Shipped host `#key-hud` + `#hud-bars` + `#replay-files`, `POST /new-game`, `GET /recordings` + `GET /recording?name=`, player `player:` mesh, `/doom/walls` linedef extrusion (`WALL_HEIGHT_M = 2.4`), Debug/Replay ThreeDee walls, `./smoke` `walls=`, `./smoke-pause-replay --new-game`. Success commands from `$ROOT` all exit 0. Contract checkboxes left unchecked.

## UX amendments applied (2026-09-18, planner)

1. **UX-13** — repr-regex `max(z floats) > DEFAULT_CELL_M` on `build_walls([])` and the `publish_world` walls SceneUpdate. Flat plates (`size.z ≤ 0.5`) FAIL.
2. **UX-13** — `struct.unpack` fence is all of `doom_foxglove/`; only `ws_client.py` and `record.py` are exempt.
3. **UX-13** — walls come from `publish_world` when `map_grid` is set (once per level). Pending-flag alternative struck; a flag-less `WorldState` with `map_grid` still must publish hollow-room walls.
4. **UX-06** — traversal-token set is `".."` **or** `basename` **or** `is_relative_to` **or** `resolve`.
5. **UX-02** — any `web/src/*.ts` that mentions `key-hud` must also mention `HoldController` or `subscribe`/`onMotion` in that same file.
6. **UX-11** — one PASS rule: `rg` of `.foxe`/`installExtensions`/`getContext`/`<canvas` over `web/src` `web/index.html` `doom_foxglove/` prints nothing, **or** every printed line is a forbidden-naming comment with no call syntax.
7. **UX-04** — maxima `200`/`300` search blob includes `web/src/styles.css`.

Nits left unapplied.

## State

`PLAN.md` now has a **Demo UX polish** section. `contract.md` SX-01…SX-06 remain PASS; section F UX items are amended (A-1…A-7) and await critic re-gate. GOAL.md was human-escalated: `dec_host_html_hud` SUPERSEDES the old “no custom HUD until gauges fail” reading of `dec_stock_panels_only` (iframe stays stock; host HTML HUD allowed; `.foxe` out until self-hosted embed).

Surgical contract amendments (boxes left ticked): RL-08/RL-09 and RR-04 no longer require Gauge; PR-09 allows `POST /new-game` and still forbids `/resume`; ES-11 allow-list includes `key-hud` / `hud-*` / `replay-files` / `new-game`.

Skipped (still SX-06 / UX-12): remote-access gateway, comparison mode UI, cloud share links, ViZDoom policy vs human, resume-same-episode, workstream `06-*`.

## What's left

1. ~~Kimi critic (kimi-k3-high) attacks UX-01…UX-14 and returns amendments or a gate.~~ Done 2026-09-18: **FAIL**, seven amendments in `critique.md` (UX gate).
2. ~~Planner applies critic UX A-1…A-7 to this workstream `contract.md` only (nits optional), then re-submits.~~ Done 2026-09-18: A-1…A-7 landed; nits left untouched.
3. ~~Kimi critic (kimi-k3-high) **re-gates** UX-01…UX-14.~~ Done 2026-09-18: **PASS**, recorded in `critique.md`.
4. ~~Generator implements UX gaps only (no product work this planner run).~~ Done 2026-09-18: generator shipped section F product code.
5. ~~Evaluator ticks UX boxes; does not untick SX.~~ Done 2026-09-18: **PASS 14/14** (UX-01…UX-14), failing ids none; boxes ticked in `contract.md`, evidence in `eval.md`. SX-01…SX-06 untouched.

## Demo UX polish contract (2026-09-18, planner)

Fourteen mechanical `UX-` items: `#key-hud` + HoldController coupling; player `player:` SceneUpdate mesh; host HTML `#hud-bars`; `POST /new-game` + `GET /recordings` + `GET /recording?name=`; Play from FileSource starts a new live game; `#replay-files` `doom-*.mcap`; layouts Gauge-optional; `./smoke-pause-replay --new-game`; no `.foxe`/`installExtensions`/canvas HUD; no `06-*` / `/resume`; **`/doom/walls` linedef extrusion** (`WALL_HEIGHT_M = 2.4`, once per level) + Debug/Replay ThreeDee + `./smoke` `walls=`.


## Prior SX loop (kept)

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
