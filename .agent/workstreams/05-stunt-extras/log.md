# Log — 05-stunt-extras

Append-only. One entry per action, newest at the bottom. Never edit or delete an existing entry. Format: `## [YYYY-MM-DD] op | title`.

## [2026-09-18] generator | deferral stub created

Created this workstream's four files as a deferral stub while writing the `.agent/` harness. Wrote `PLAN.md` with the stunt-extras spec (events, comparison, agent, remote spectator) and a deferral contract naming the `SX-` prefix. Entry condition: workstreams `01`–`03` evaluated `done` (`cap_live_ws_camera_teleop`, `cap_3d_map_hud`, `cap_embed_page`). Per `dec_phase_gating`, extras are not on the DAG until those three capabilities are done.

No `SX-nn` items were authored and no product code was written. `blockers: none` because this workstream is gated by sequencing rather than by a hazard.

## [2026-09-18] generator | events plus agent prompts

Thin extras slice. Added `/doom/events` JSON `{ kind, message, tick, map }` with `kind` in `death|weapon|level|pickup`. `/doom/log` messages stay the RL-05 strings. `level` is entering a map (first observe) and level complete (episode finished while not dead). Did not prefix log lines (that would break RL-05 exact `Entering {map}` / `You died.` checks). README has three copy-paste Foxglove agent/MCP prompts; no custom agent. `web/README.md` only got a pointer. `./smoke-events` wrote `recordings/smoke-events.mcap` and exited 0: live=1 kinds=['level'] mcap_events=1 backend=vizdoom (8765 busy, ephemeral 54038). Did not tick contract checkboxes. Did not rewrite embed, Play/Debug/Replay layouts, or 01–04 contracts.

Skipped: remote-access gateway, comparison mode UI, cloud share links, ViZDoom policy vs human.

## [2026-09-18] evaluator | 05-stunt-extras verdict

Kimi K3 adversarial eval, graded against the PLAN thin slice because `contract.md` is still the deferral stub. Reproduced `./smoke-events` from a clean shell: exit 0, backend=vizdoom E1M1, ephemeral port (8765 busy), live=1 kinds=['level'], mcap_events=1. Independently decoded the zstd MCAP chunk and confirmed the `/doom/events` payload `{'kind': 'level', 'message': 'Entering E1M1', 'tick': 1, 'map': 'E1M1'}`; exercised death/weapon/pickup/level-complete through the real `logs_from_delta` → `event_payload` path (ALL_KINDS_OK). README's three agent prompts confirmed; declared skips (remote gateway, comparison UI, cloud links, ViZDoom policy) confirmed absent. Verdict: **product PASS / process FAIL (SX-CONTRACT-GATE)** — all three stub entry conditions unmet (KG capabilities still `planned`, 01 and 02 evals are process FAIL not `done`, no gated `SX-nn` contract). Workstream not `done`. Also found: harness self-check red (H-17, `01-hero-loop/progress.md` status `gated` outside vocabulary — owned by 01's loop). Full evidence in `eval.md`.

## [2026-09-18] planner | gated SX-nn contract

Replaced the 05-stunt-extras deferral stub with numbered SX-01…SX-06 items, each with a mechanical check from `$ROOT`. SX-01 `/doom/events` JSON schema `{ kind, message, tick, map }`; SX-02 kinds `death|weapon|level|pickup`; SX-03 `./smoke-events` exit 0; SX-04 at least one live event and one MCAP message (idle `level` is enough); SX-05 three exact README agent/MCP prompts and no custom agent; SX-06 remote-access gateway, comparison mode UI, cloud share links, and ViZDoom policy vs human stay out. Checkboxes left unticked. Did not edit other workstream contracts, GOAL.md, PLAN.md, or product code. Appended ContractItem nodes SX-01…SX-06 and IMPLEMENTS edges to `ws_05_stunt_extras`. Did not rewrite the seeded `ws_05_stunt_extras` workstream line. Next: kimi critic.

## [2026-09-18] critic | SX-nn gate

Kimi K3 contract critic attacked SX-01…SX-06 for mechanicality, verifying every quoted string, import, and command against the files on disk. Verdict: **FAIL** with four required amendments, recorded in `critique.md`: (1) SX-06's PASS rule contradicts itself (prints-nothing vs allowed comments) — make any rg hit a FAIL; (2) SX-06's fence covers only four files and is evadable via a new module — widen rg to all of `doom_foxglove/` (verified clean today); (3) SX-03's negative path exits 1 on import crash as well as on `_fail` — also assert stderr `SMOKE-EVENTS FAIL: critic-injected`; (4) SX-05's checkbox prose (custom agent/extension) is wider than its three-token rg — narrow the prose or widen the tokens. Two non-blocking nits (SX-04 quote literal, SX-03 "default tick count" clause). Verified clean: SX-01/SX-02 checks run SDK-free with all quotes verbatim; SX-03 is deterministic via `FallbackEngine` (no ViZDoom/IWAD/network needed); SX-04 parsers exist; SX-05 strings verbatim in README; SX-06 README needles present. Did not edit `contract.md` or product code. Next: planner applies amendments, then re-gate.

## [2026-09-18] planner | apply SX critique

Applied critic amendments 1–4 to `contract.md`. SX-06: any rg printed line is FAIL (comments not exempt); fence target is `smoke-events` plus all of `doom_foxglove/` (`web/` stays 03). SX-03 negative path now requires exit 1 and stderr `SMOKE-EVENTS FAIL: critic-injected`. SX-05: narrowed FAIL prose to the existing three-token rg (`FastMCP`, `langchain`, `@modelcontextprotocol`); did not widen tokens. Left nits unapplied. Did not tick boxes, did not write product code, did not rewrite KG ContractItem lines (still `specified`). `progress.md` status is `amended`. Next: kimi critic re-gate.

## [2026-09-18] critic | SX-nn re-gate

Re-attacked the amended SX-01…SX-06. Verified all four amendments landed: (1) SX-06 PASS rule is now prints-nothing with any printed line a FAIL, comments not exempt, contradictory sentence gone; (2) SX-06 fence widened to `smoke-events` plus all of `doom_foxglove/` with `web/` explicitly excluded — re-ran the ten-needle rg from `$ROOT`, zero hits, so the wider fence is satisfiable as-is; (3) SX-03 negative path now requires exit 1 and stderr `SMOKE-EVENTS FAIL: critic-injected`, closing the import-crash false-PASS; (4) SX-05 prose narrowed to the three-token rg with an explicit no-taste clause, checkbox and check now the same width. All six items are mechanical: binary checks from a clean shell at `$ROOT`. Verdict: **PASS**, recorded in `critique.md`. Did not edit `contract.md` or product code, did not tick boxes. Entry condition (3) met; (1) and (2) remain unmet and owned by 01/02/03 loops. Next: kimi evaluator ticks SX items.

## [2026-09-18] evaluator | SX-nn verdict

Kimi K3 evaluator ran every SX-01…SX-06 check verbatim from a clean shell at `$ROOT` (`$PY` = `.venv/bin/python`, `PYTHONPATH=$ROOT`). SX-01 `schema-ok` (all quotes verbatim; events channel is `Channel`, not `LogChannel`). SX-02 `kinds-ok` (all five `logs_from_delta` cases through the real path; five assignments quoted). SX-03: `./smoke-events` exit 0 with `SMOKE-EVENTS OK ticks=8 live=1 kinds=['level'] file=recordings/smoke-events.mcap mcap_events=1 backend=vizdoom` (8765 busy → ephemeral bind, HL-12 note); negative path `neg_exit=1` with stderr exactly `SMOKE-EVENTS FAIL: critic-injected`. SX-04: in-repo `list_mcap_topics`/`count_mcap_messages` on the MCAP — magic OK, `/doom/events` present, count 1 ≥ 1. SX-05 `prompts-ok 3`; three-token rg clean (exit 1). SX-06: ten-needle fence rg over `smoke-events doom_foxglove/` printed nothing (exit 1); README `## Not in this slice` needles all present. Verdict: **PASS — 6/6, failing ids: none.** Ticked all six checkboxes in `contract.md`. Did not edit product code. Entry conditions (1) and (2) remain owned by the 01/02/03 loops; this verdict does not un-defer `ws_05_stunt_extras`. Full evidence in `eval.md`.
