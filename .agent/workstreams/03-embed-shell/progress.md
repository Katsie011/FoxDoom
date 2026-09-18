status: done
owner: Supervisor (eval PASS; awaiting KG librarian / supervisor routing)
updated: 2026-09-18
next action: supervisor routes per phase DAG (E3 pass → P4); librarian may append `cap_embed_page` status triple
blockers: none

# Progress — 03-embed-shell

Planner replaced the deferral stub with a gradeable `ES-01`…`ES-11` contract. Critic gated it PASS. Evaluator (kimi-k3-high) ran every check and ticked all 11 boxes: **PASS 11/11**.

## State

Product code already exists under `web/` (`@foxglove/embed` FoxgloveViewer, parent-owned live transport with pending-Pro wait and iframe-owned + `connectDirect` fallback, force-load of `layouts/Play.json` and `layouts/Debug.json`, WASD/Space on `/cmd_vel` and `/doom/buttons`, Teleop kept in Play, no host canvas). Headless smoke is `./web/check`.

`progress.md` status is `planning`, not `deferred`: a real `ES-nn` contract now exists. The knowledge-graph `ws_03_embed_shell` node is still the seeded `deferred` line (append-only; this planner does not rewrite it). `cap_3d_map_hud` remains `planned` (eval EC-1) — a DAG fact, not a `blockers:` Risk id.

## What's left

1. ~~Kimi critic gate~~ — **done 2026-09-18: PASS, no amendments** (`critique.md`). Critic ran every shell check from `$ROOT` and verified each quoted symbol exists verbatim.
2. ~~Evaluator (`kimi-k3-high`) re-runs `./web/check`, quotes the named files, and ticks `ES-01`…`ES-11`~~ — **done 2026-09-18: PASS 11/11** (`eval.md`). `./web/check` re-run in the ticking eval: exit 0, `EMBED CHECK OK`. All rg fence checks empty; all quoted symbols verbatim. Failing ids: none.
3. Planner applies generator gaps only if the evaluator FAILs an item — **not needed**, no FAILs.
4. Human Pro-browser pass stays optional and is not an ES checkbox.
