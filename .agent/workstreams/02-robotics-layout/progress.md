status: done
owner: Evaluator (kimi-k3-high)
updated: 2026-09-18
next action: none for 02 — all RL items ticked; KG un-defer of ws_02_robotics_layout still waits on 01 entry conditions 1–2
blockers: none

# Progress — 02-robotics-layout

Generator implemented RL-07. Contract checkboxes were not ticked.

## State

`PLAN.md` still holds the phase spec. `contract.md` is the critic-gated RL-nn list (re-gate PASS). Product code lives in `doom_foxglove/` and `layouts/Play.json` plus `layouts/Debug.json`. Smoke is `./smoke` from repo root with no `--hero`.

F-1 stays on HL-11. F-2 (wire delivery of 02 topics) is implemented as an in-smoke `foxglove.sdk.v1` subscribe/receive loop in `doom_foxglove/ws_client.py` (`LayoutWireProbe`), called from `doom_foxglove/smoke.py` only on the non-`--hero` path. F-3 stays accepted: RL-08/RL-09 walk layout JSON.

## What's left

1. ~~Kimi critic (kimi-k3-high) attacks RL-01…RL-10~~ — DONE 2026-09-18: **FAIL**, 2 amendments in `critique.md`.
2. ~~Planner applies the two amendments to this workstream `contract.md` only~~ — DONE 2026-09-18.
3. ~~Kimi critic re-gate of the amended RL-01…RL-10 list~~ — DONE 2026-09-18: **PASS**.
4. ~~Grok generator implements RL-07 WIRE LAYOUT inside `./smoke`~~ — DONE 2026-09-18. Local `./smoke` exit 0 printed `WIRE LAYOUT map_schema=foxglove.Grid map=1 map_frame=map tf_schema=foxglove.FrameTransforms tf=8 tf_parent=map tf_child=base_link entities_schema=foxglove.SceneUpdate entities=8 player=8 player_keys=health,armor,ammo,weapon,tick,dead log_schema=foxglove.Log log=1`. `./smoke --hero` still exit 0 (HL-09), no WIRE LAYOUT line.
5. ~~Kimi evaluator re-runs the gated checks~~ — DONE 2026-09-18: **PASS, 10/10, failing ids: none.** All checks run verbatim from `$ROOT`; `./smoke` exit 0 with `SMOKE OK` + `WIRE LAYOUT` (map=1, tf=8, entities=8, player=8, log=1, schemas and player_keys exact). All ten contract checkboxes ticked by the evaluator. Verdict appended to `eval.md`.
