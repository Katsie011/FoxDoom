# Eval — 05-stunt-extras (adversarial, Kimi K3)

**Date:** 2026-09-18
**Evaluator:** kimi-k3-high (did not write this code)
**Generator claims under test:** `./smoke-events` exit 0; `/doom/events` JSON with `kind` in `death|weapon|level|pickup`; three README agent prompts; remote/comparison/cloud/policy skipped.

## Contract status

`contract.md` is a **deferral stub**. Its own text: "This file is a deferral stub, not a gradeable contract. No generator may run against it and no evaluator may grade it until the entry condition below is met." Entry conditions, checked against disk state in this eval:

1. `cap_live_ws_camera_teleop`, `cap_3d_map_hud`, `cap_embed_page` are `done` in the knowledge graph — **UNMET.** All three are `status: planned` in `nodes.jsonl` (lines 26–28). `ws_05_stunt_extras` and `cap_stunt_extras` remain `deferred`.
2. Workstreams 01–03 have evaluator verdicts of `done` — **UNMET.** `01-hero-loop/eval.md`: product PASS / **process FAIL** (no gated HL-nn contract). `02-robotics-layout/eval.md`: product PASS / **process FAIL** (entry condition unmet). Only `03-embed-shell/eval.md` is a clean PASS (11/11, gated ES contract).
3. A planner has written a real `SX-nn` contract, gated by a critic — **UNMET.** The stub is unchanged; grep for `SX-\d` / `EX-\d` across the workstream finds only the stub's own mention of the prefix. (No `EX-` prefix exists anywhere in this repo; the stub names `SX-`.)

**SX-CONTRACT-GATE (process): FAIL.** Generation preceded the gate, same violation shape as 02. The product passing below does not retroactively un-defer the workstream.

## Checks run (clean shell, repo root)

### E-01 `./smoke-events` — PASS, exit 0

```
$ ./smoke-events
SMOKE-EVENTS engine backend=vizdoom map=E1M1 iwad=.../.venv/lib/python3.12/site-packages/vizdoom/freedoom1.wad
SMOKE-EVENTS websocket bound ws://127.0.0.1:54108
SMOKE-EVENTS note: 8765 was busy; live server still defaults to ws://127.0.0.1:8765
SMOKE-EVENTS OK ticks=8 published=8 topic=/doom/events live=1 kinds=['level'] file=recordings/smoke-events.mcap bytes=54707 mcap_events=1 backend=vizdoom
SMOKE_EVENTS_EXIT=0
```

Real ViZDoom backend (not the fallback), Freedoom E1M1, ephemeral-port fallback demonstrated. Generator's exit-0 claim reproduced independently.

### E-02 MCAP contents, independent decode — PASS

The in-repo smoke counts messages via its own `record.py` parser. I decoded the zstd-compressed MCAP chunk independently (stdlib `compression.zstd`, python 3.14) and read the actual message payload:

```
channels: {1: '/doom/camera', 2: '/doom/events', 3: '/tf', 4: '/doom/entities', 5: '/doom/player', 6: '/doom/log', 7: '/doom/map'}
/doom/events payloads: [{'kind': 'level', 'message': 'Entering E1M1', 'tick': 1, 'map': 'E1M1'}]
MCAP_PAYLOAD_OK
```

`/doom/events` is in the MCAP with a well-formed `{kind, message, tick, map}` JSON payload. All seven topics present.

### E-03 All four kinds flow through the real code — PASS

The smoke only ever demonstrates `level` (an idle marine produces nothing else). I exercised the other three kinds through the unmodified `logs_from_delta` → `event_payload` path with synthetic player states:

```
level:   {'kind': 'level',  'message': 'Entering E1M1', 'tick': 1, 'map': 'E1M1'}
death:   {'kind': 'death',  'message': 'You died.', 'tick': 2, 'map': 'E1M1'}
weapon:  {'kind': 'weapon', 'message': 'You got the shotgun!', 'tick': 2, 'map': 'E1M1'}
pickup:  {'kind': 'pickup', 'message': 'Picked up ammo.', 'tick': 2, 'map': 'E1M1'}
level_complete: {'kind': 'level', 'message': 'Level complete: E1M1', ...}
ALL_KINDS_OK
```

Vocabulary is enforced in code (`world.py` `EVENT_KINDS`; `topics.py` `publish_world` filters on it). `EVENTS_SCHEMA` requires exactly `{kind, message, tick, map}`. `/doom/log` strings are unchanged (RL-05-compatible: `Entering E1M1`, `You died.`).

### E-04 README agent prompts — PASS (3/3)

README "Ask Foxglove (copy-paste)" section contains exactly three prompts, each referencing real topics verified above: **"When did health drop?"** (`/doom/player.health`, `/doom/events`, `/doom/log`), **"Why did I die?"** (`kind=death` + `/doom/player` + `/doom/entities`), **"Build a layout for weapons"** (`/doom/player.weapon|ammo`, `kind=weapon`, Image, Teleop hidden). No custom agent ships; `web/README.md` carries only a pointer to the repo README. Matches the claim.

### E-05 Declared skips are actually absent — PASS

Remote-access gateway, comparison mode UI, cloud share links, ViZDoom policy: README "Not in this slice" names all four as skipped; `web/README.md` out-of-scope section agrees; no code for any of them exists. The generator disclosed the skips rather than claiming them — credited.

### E-06 Harness self-check — FAIL (environment finding, not caused by 05)

```
$ python3 .agent/knowledge-graph/validate.py --harness
graph: 95 nodes, 103 edges, ...
FAIL: 1 of 1467 checks failed
  - H-17: .agent/workstreams/01-hero-loop/progress.md: status 'gated' is outside the allowed vocabulary
exit=1
```

The harness gate is currently red because `01-hero-loop/progress.md` uses `status: gated` (allowed: planning, planning complete, amended, awaiting generator, in progress, blocked, done, deferred). Not introduced by this slice, but nothing can print `HARNESS OK` until it is fixed.

## PLAN.md thin-slice grading

The stub forbids grading against SX items (none exist), so this grades the generator's declared thin slice against the PLAN spec lines it touched:

| PLAN item | Verdict | Evidence |
|---|---|---|
| Events — tag deaths, weapon pickups, level complete; scrub to the moment | PASS (thin) | E-01…E-03. Tags exist live and in MCAP. "Scrub to the moment" is a Foxglove-app action against the MCAP; the data substrate is verified, the app interaction is not demonstrated (same caveat class as 02's F-3). |
| Built-in agent / MCP prompts (when did health drop, why did I die, build a layout for weapons) | PASS | E-04. Three copy-paste prompts, no custom agent, per the slice's scope. |
| Comparison mode | SKIPPED (declared) | E-05 |
| User script (layout-local topic) | NOT DONE, not claimed | No `/doom/dps`-style topic exists; generator did not claim it. PLAN lists it; absent from the thin slice. |
| Remote access / gateway | SKIPPED (declared) | E-05 |
| Image click/hover publish (stretch) | NOT DONE, not claimed | — |
| Shareable recording link | SKIPPED (declared) | E-05 |

## Findings (non-gating)

1. **Smoke only proves `level` end-to-end.** Death/weapon/pickup are verified only by direct function exercise (E-03), never by the smoke driving the marine into a hazard or onto an item. A gated SX contract should require a scripted pickup or death in `./smoke-events` (e.g. spawn-state manipulation) so all four kinds are covered by the repo's own check.
2. **Harness red (H-17).** `01-hero-loop/progress.md` status `gated` is outside the validator vocabulary; `validate.py --harness` exits 1. Fix belongs to 01's loop, not this one.
3. **`kind` is a free string in the JSON schema** (`EVENTS_SCHEMA` has no `enum`). The code enforces the vocabulary, so this is cosmetic; a gated contract may want the enum in the schema for Raw Messages panel clarity.
4. **KG drift:** 03 evaluated PASS 11/11 but `cap_embed_page` is still `planned` and `ws_03_embed_shell` still `deferred` in `nodes.jsonl`. The kg-sync loop has not run for 03; until it does, this workstream's entry condition 1 cannot be met even after 01/02 process FAILs are resolved.

## Verdict

**Product: PASS** for the declared thin slice — `./smoke-events` exit 0 reproduced independently (E-01), `/doom/events` verified live and inside the MCAP with the claimed JSON shape and kind vocabulary (E-02, E-03), three README agent prompts confirmed (E-04), declared skips genuinely absent (E-05).

**Process: FAIL — SX-CONTRACT-GATE.** The contract is a deferral stub whose entry conditions are all three unmet (capabilities `planned` in KG; 01 and 02 evals are process FAIL, not `done`; no planner-written, critic-gated `SX-nn` contract exists). No SX-nn items exist to tick, and none were ticked. The workstream may **not** be marked `done`; per the stub, it returns to deferred/blocked state.

**Required before the next evaluator visit:**

1. Resolve 01 and 02 process FAILs (gated HL-nn / RL-nn contracts, then re-eval).
2. Run kg-sync so `cap_live_ws_camera_teleop`, `cap_3d_map_hud`, `cap_embed_page` reflect reality.
3. Fix H-17 (`01-hero-loop/progress.md` status vocabulary) so the harness gate is green.
4. Planner writes numbered `SX-nn` items with mechanical checks (fold in finding 1: all four kinds in smoke); Kimi K3 contract critic gates it.
5. Only then does a generator run against this workstream again.

## Exit codes

| Command | Exit |
|---|---|
| `./smoke-events` | **0** |
| Independent MCAP zstd decode + payload check | **0** |
| Four-kind code-path probe | **0** |
| `python3 .agent/knowledge-graph/validate.py --harness` | **1** (H-17, pre-existing, owned by 01) |

## Addendum — contract changed mid-eval (2026-09-18, same session)

While this eval was being written, a Planner replaced the deferral stub with a numbered `SX-01…SX-06` contract (see `log.md` entry `planner | gated SX-nn contract`). That does not change the verdict above: the generator ran against the stub, and the new contract itself states "Generation preceded the gate; the gate is retroactive." The process FAIL for the generator's run stands.

State of the new contract as of this addendum:

- **Not yet gated.** `contract.md` header: "awaiting Kimi critic gate … No evaluator ticks boxes until that gate." Accordingly, **no SX checkbox is ticked by this evaluator**, and the SX-01…SX-06 ContractItem nodes stay `specified`.
- **Entry conditions (1) and (2) remain unmet** regardless of the new contract: the three gating capabilities are still `planned` in `nodes.jsonl`, and 01/02 evals are process FAIL, not `done`. The workstream stays `deferred`.
- **Evidence pre-staged.** The checks I ran against the stub map onto the new items: E-01 → SX-03 (`./smoke-events`, exit 0, `SMOKE-EVENTS OK`, `file=` present); E-02 → SX-04 (in-repo `list_mcap_topics` / `count_mcap_messages` on `recordings/smoke-events.mcap`, count = 1, plus an independent zstd payload decode); E-03 → SX-01/SX-02 (schema keys, `additionalProperties: false`, all four kinds plus level-complete through the real code path); E-04 → SX-05 (three verbatim README prompts, "No custom agent ships in this repo."); E-05 → SX-06 (fence items absent from the 05-owned files). Not run to the letter of the new contract: the SX-03 negative-path `_fail('critic-injected')` exit-1 check (source read shows `_fail` returns 1) and the exact SX-06 `rg` fence invocation. The post-gate evaluator should re-run every SX check verbatim from a clean shell rather than inheriting this mapping.
- **Finding 2 (H-17) still open** and now more relevant: the harness gate must be green before the critic/evaluator loop can trust `HARNESS OK`.

---

# SX-01…SX-06 verdict — 2026-09-18 (evaluator, kimi-k3-high)

**Target:** amended, critic-gated `contract.md` (re-gate PASS in `critique.md`). Every check run verbatim from a clean shell at `$ROOT` (`/Users/michael/Documents/foxglove/work/doom`), `$PY` = `$ROOT/.venv/bin/python` (executable), `PYTHONPATH=$ROOT`. I did not write this code. Boxes ticked only where the check passed.

## Verdict: PASS — SX-01, SX-02, SX-03, SX-04, SX-05, SX-06 all PASS. Failing ids: none.

| Item | Verdict | Evidence |
|---|---|---|
| SX-01 | PASS | Check prints `SX-01 schema-ok`. Quotes verified verbatim: `EVENTS_TOPIC = "/doom/events"` (`doom_foxglove/__init__.py:15`); `"required": ["kind", "message", "tick", "map"]` (`topics.py:43`); `"events": Channel(EVENTS_TOPIC, schema=EVENTS_SCHEMA)` (`topics.py:186` — `Channel`, not `LogChannel`; `LogChannel` is used only for `"log"` at `topics.py:185`); `def event_payload` (`topics.py:238`) returns the four keys. |
| SX-02 | PASS | Check prints `SX-02 kinds-ok` — all five `logs_from_delta` cases (enter, level-complete, death, weapon, armor pickup) produce the asserted events through the real code path. Quotes verbatim: `KIND_LEVEL = "level"`, `KIND_DEATH = "death"`, `KIND_WEAPON = "weapon"`, `KIND_PICKUP = "pickup"`, `EVENT_KINDS = (KIND_LEVEL, KIND_DEATH, KIND_WEAPON, KIND_PICKUP)` (`world.py:141-145`); `if event.kind in EVENT_KINDS` (`topics.py:260`). Set-equality assert forbids a fifth member. |
| SX-03 | PASS | `./smoke-events` (the script itself, not a module invocation or `/tmp` wrapper) exits 0. Stdout contains `SMOKE-EVENTS OK ticks=8 published=8 topic=/doom/events live=1 kinds=['level'] file=.../recordings/smoke-events.mcap bytes=54581 mcap_events=1 backend=vizdoom` — `SMOKE-EVENTS OK` and `file=` both present. 8765 was busy; ephemeral bind `ws://127.0.0.1:54831` via `fallback_if_busy=True` — HL-12 note, not a FAIL. Negative path: `neg_exit=1` and captured stderr is exactly `SMOKE-EVENTS FAIL: critic-injected`. Quotes verbatim: `exec "$PY" -m doom_foxglove.smoke_events` (`smoke-events:12`); `def _fail` prints to stderr and `return 1` (`smoke_events.py:23-25`); `fallback_if_busy=True` (`smoke_events.py:68`); `return 0` after the OK print (`smoke_events.py:133`). |
| SX-04 | PASS | In-repo parse only: `smoke_events_recording_path()` → `recordings/smoke-events.mcap` exists (54581 bytes), starts with `MCAP_MAGIC`, `list_mcap_topics` includes `/doom/events` (topics: camera, entities, events, log, map, player, tf), `count_mcap_messages(path, '/doom/events')` = 1 ≥ 1. Prints `SX-04 ... mcap_events 1`. SX-03 stdout substrings `live=1` and `mcap_events=1`, both ≥ 1. Quotes verbatim: `if not live_events:` (`smoke_events.py:102`), `if mcap_count < 1:` (`smoke_events.py:120`), `smoke_events_recording_path` body `return recordings_dir(root) / "smoke-events.mcap"` (`record.py:51-52`). |
| SX-05 | PASS | Check prints `SX-05 prompts-ok 3`: heading `## Ask Foxglove (copy-paste)`, sentence `No custom agent ships in this repo.`, and all three fenced prompt bodies verbatim in `README.md`. Token fence `rg -n -e 'FastMCP' -e 'langchain' -e '@modelcontextprotocol' doom_foxglove --glob '*.py'` printed nothing (exit 1 = PASS). |
| SX-06 | PASS | Fence `rg` over `smoke-events doom_foxglove/` with all ten needles printed nothing (`extras_fence_exit=1` = PASS; zero lines). README side prints `SX-06 readme-skip-ok`: `## Not in this slice` plus all four needles (`remote-access gateway`, `comparison mode UI`, `cloud share links`, `ViZDoom policy vs human`) present. |

## Scope notes (per contract, not FAILs)

- Idle 8-tick smoke emitted only `kind=level` (`Entering E1M1`); contract explicitly forbids FAILing SX-02/03/04 for missing `death`/`weapon`/`pickup` in an idle run.
- Busy `ws://localhost:8765` with ephemeral bind is HL-12, an environment note.
- Foxglove app was not opened; SX-05 grades file text only.
- Phase-DAG deferred items (comparison mode, remote gateway, user script, image-click, shareable link) are sequencing, not skips of this contract; SX-06 confirms their absence from the fence target.

## Entry-condition reminder (not an SX checkbox)

Entry conditions (1) and (2) — KG capabilities `done` and 01/02/03 evaluator verdicts `done` — are owned by those loops and were not re-graded here. This verdict ticks SX-01…SX-06 against the gated contract; it does not by itself un-defer `ws_05_stunt_extras`.
