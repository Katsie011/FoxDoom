# Log — 01-hero-loop

Append-only. One entry per action, newest at the bottom. Never edit or delete an existing entry. Format: `## [YYYY-MM-DD] op | title`.

## [2026-09-18] generator | hero loop server and smoke

Implemented ViZDoom-or-fallback engine plus `foxglove-sdk` WebSocket server with `ClientPublish` on `ws://localhost:8765`. Publishes `/doom/camera` as `foxglove.CompressedImage` JPEG. Maps `/cmd_vel` Twist (`linear.x`, `angular.z`, optional `linear.y`) onto move buttons and zeros on stop. Maps `/doom/buttons` JSON `{fire, use, weapon}` onto shoot/use. Smoke command: `python3 -m doom_foxglove.smoke` from repo root. README covers install, run server, open Foxglove live WS, add Image plus Teleop.

Did not implement Grid/TF/entities, embed page, MCAP, events, comparison, or remote access. Did not custom-render the game in a host canvas. Did not tick any contract checkbox. Contract remains the planning stub in this directory.

IWAD policy: Freedoom or shareware only. No commercial WAD in the tree.

## [2026-09-18] generator | smoke command result

Smoke command from repo root: `./smoke --no-fetch-iwad` (also `PYTHONPATH=. .venv/bin/python -m doom_foxglove.smoke`). Exit 0.

Engine: ViZDoom 1.3.0, map E1M1, IWAD `vizdoom/freedoom1.wad` bundled with the package (Freedoom, not a commercial WAD). Published 8 JPEG frames on `/doom/camera`. Accepted a forward Twist on `/cmd_vel` and a later zero Twist. Python 3.12 venv.

Port note: `ws://localhost:8765` is currently held by another process (`sim.foxglove_bridge` in robotArms). Smoke bound an ephemeral port, still started a ClientPublish server, and printed that the live default remains 8765. `python -m doom_foxglove` will fail to bind until 8765 is free. That is an environment collision, not a missing server.

Did not tick contract checkboxes. Risk node `vizdoom_macos_build` stays `open` for the librarian; this machine's 3.12 wheel path worked.

## [2026-09-18] evaluator | 01-hero-loop verdict

Kimi K3 adversarial eval. Harness validate exit 0 (876 checks). `./smoke` exit 0 on real ViZDoom 1.3.0 / Freedoom E1M1 (ephemeral port; 8765 held by external PID 50610). Independent raw-socket WS client verified ClientPublish capability, `/doom/camera` CompressedImage delivery, `/cmd_vel` Twist, and `/doom/buttons` over the wire: 5/5. Negative path exits 1. Live server fails loudly on busy 8765. No commercial WAD, no canvas, no 02–05 scope creep. Verdict: product PASS against PLAN.md bar; process FAIL — no gated HL-nn contract exists (stub only). Full evidence in eval.md. Findings: smoke never opens a socket to its own server; TeleopListener lacks on_subscribe/on_unsubscribe (server logs AttributeError callbacks).

## [2026-09-18] planner | gated HL-nn contract

Replaced the 01-hero-loop planning stub with numbered HL-01…HL-14 items, each with a mechanical check from `$ROOT`. Folded eval.md findings: HL-10 requires an in-repo ClientPublish socket proof (eval E-05 `/tmp` client does not pass); HL-11 requires `TeleopListener.on_subscribe` / `on_unsubscribe`; HL-12 treats busy 8765 as environment if smoke binds ephemeral and documents the live default. Out of scope: Grid/TF/entities, embed, MCAP, 02–05. Checkboxes left unticked. Did not edit `doom_foxglove/`, GOAL.md, or implement the listener fix. Next: Kimi critic gates this contract (retroactive; 02 already started).

## [2026-09-18] critic | HL-nn gate

Kimi K3 critic gate on contract.md HL-01…HL-14: **FAIL**, 8 required amendments (C-1…C-8), full text in `critique.md`. Verified each attack against source before pressing it. Confirmed: HL-09's `./smoke` is gated on 02 artifacts (`smoke.py:44-70` `_check_layouts`, `smoke.py:188-195` map/tf/entities/player/log requirements) and its negative path is waivable; HL-10's A-or-B split lets the wire proof live outside `./smoke`, never names subprotocol `foxglove.sdk.v1`, and leaves the WIRE line format undefined; HL-06/07 test only `apply_topic`/`binary_buttons` dict mapping, never `VizDoomEngine._action` motion; HL-01 keys on unquoted note substrings (`engine.py:384,396`); HL-02 has no check that env-unset default IWAD resolution rejects commercial names (`iwad.py:18-20` accepts `DOOM_IWAD=doom2.wad`); HL-05 asserts local JPEG bytes but never the `CompressedImageChannel` schema; HL-12 pass conditions are unanchored prose; HL-13's "canvas next to a negation" is undefined. HL-03/04/08/11/14 re-checked and reproducible as written. Did not edit contract.md, did not tick checkboxes, did not touch `doom_foxglove/`. Next: planner applies C-1…C-8; no generator starts until then.

## [2026-09-18] planner | apply C-1..C-8

Applied critic amendments C-1…C-8 to `contract.md`. Checkboxes left unticked. HL-03, HL-04, HL-08, HL-11, HL-14 unchanged. Did not touch `doom_foxglove/`. Did not start a generator.

Changed items: HL-01 (C-4 quote `try_vizdoom` literals), HL-02 (C-5 env-unset default IWAD check + item-text scope), HL-05 (C-6 `CompressedImageChannel` isinstance), HL-06/HL-07 (C-3 engine pose-delta and ATTACK/USE), HL-09 (C-1 `./smoke --hero` + always-required `_fail` negative), HL-10 (C-2 strike option B; fixed `WIRE CHECK` + `foxglove.sdk.v1`), HL-12 (C-7 anchored steps 2 and 4), HL-13 (C-8 quoted canvas sentence + `rg` pattern).

Wrapping only: C-3 snippets needed `from doom_foxglove.engine import make_engine` inside the existing `$PY -c` blocks so the appended assertions are runnable. All other critic replacement check text applied verbatim. Next: Kimi critic re-gate of the amended contract.

## [2026-09-18] critic | HL-nn re-gate

Kimi K3 re-gate of the amended contract: **FAIL**, 2 remaining amendments (R-1, R-2), full text in `critique.md`. Audited all eight C-amendments against source: C-1…C-8 applied correctly and every referenced symbol verified (`_fail` smoke.py:39-41, `try_vizdoom` literals engine.py:384/396, `CompressedImageChannel` server.py:146-149, `fallback_if_busy` server.py:102 + smoke.py:123, README.md:5 canvas sentence). Planner-flagged leftovers cleared: C-3's added `make_engine` import is present in both blocks; C-1's busy-port sentence is attribution-only and waives nothing; C-2's rewritten prose has quotable FAIL conditions. Two residual softnesses pressed: R-1 — HL-12 step 2 still runs bare `./smoke`, whose `_check_layouts()` (smoke.py:107-109, before any bind) re-couples the port leg to 02 artifacts, contradicting the contract header's decoupling rule; fix is `./smoke --hero`. R-2 — HL-13's trailing "tells the reader not to copy a commercial doom.wad" is unanchored prose; anchor with `rg -in 'do not copy|commercial' README.md` (README.md:18 satisfies it today). Did not edit contract.md, did not tick checkboxes, did not touch doom_foxglove/. Side note for librarian: harness validate shows 15 H-17 failures, all in 02-robotics-layout/progress.md frontmatter — not a 01 gate issue. Next: planner applies R-1/R-2; no generator starts until then.

## [2026-09-18] planner | apply R-1 R-2

Applied critic re-gate amendments R-1 and R-2 to `contract.md` only. Checkboxes left unticked. Did not touch `doom_foxglove/`. Did not start a generator.

- R-1 (HL-12 step 2): replaced `Run ./smoke.` with `Run ./smoke --hero.` so the busy-port leg cannot fail on 02 `_check_layouts()`.
- R-2 (HL-13 check): replaced the unanchored commercial-WAD sentence with `rg -in 'do not copy|commercial' README.md` (currently `README.md:18`) plus the quoted README line `Do not copy a commercial doom.wad / doom2.wad into this tree.`

C-1…C-8 and all other HL items unchanged. Next: kimi critic re-gate.

## [2026-09-18] critic | HL-nn re-gate R-1 R-2

Kimi K3 re-gate of the R-1/R-2 amended contract: **PASS — the contract gates.** Verified both amendments against source, not the planner's log: R-1 — HL-12 step 2 is `./smoke --hero`, killing the residual 02 `_check_layouts()` coupling in the port leg while staying self-enforcing (dropped bind or busy-note fails the substring check). R-2 — HL-13 carries `rg -in 'do not copy|commercial' README.md` plus the quoted line; ran the pattern, it prints `README.md:18` and the quoted sentence is verbatim there. Full 14-item softness sweep: C-1…C-8 intact, no new prose without an anchor, every check reproducible from a clean shell. Did not edit contract.md, did not tick checkboxes, did not touch doom_foxglove/. Next: Grok generator implements remaining product gaps (HL-09 `--hero` split keeping bind + busy-note, HL-10 in-smoke WIRE CHECK socket proof, HL-11 `on_subscribe`/`on_unsubscribe`, HL-06/07 pose-delta must pass as written); generator does not tick boxes; Kimi evaluator re-runs gated checks after.

## [2026-09-18] generator | HL product gaps

Implemented remaining 01 product gaps against the critic-gated HL-nn contract. Did not tick checkboxes. Did not edit contract.md. Did not rewrite embed. Did not drop 02 `_check_layouts()` or map/tf/entities/player/log `_fail` hooks from bare `./smoke`.

- HL-09: `./smoke --hero` skips `_check_layouts()` and the 02 topic requirements, still boots ViZDoom, binds (ephemeral when 8765 is busy, busy-note kept), publishes camera, accepts Twist, prints `SMOKE OK`, exits 0. `_fail` still returns 1. Bare `./smoke` remains the RL-06 path.
- HL-10: in-smoke `doom_foxglove/ws_client.py` opens a WebSocket to the bound port with subprotocol `foxglove.sdk.v1`, reads serverInfo/advertise, ClientPublishes Twist and `{fire,use,weapon}` JSON. Counts increment in `TeleopListener.on_message_data`, not `apply_raw`. Stdout line: `WIRE CHECK capability=clientPublish camera_schema=foxglove.CompressedImage cmd_vel=<n> buttons=<n>`.
- HL-11: `TeleopListener.on_subscribe` and `on_unsubscribe` exist and no-op.
- HL-06/07: engine pose-delta after Twist and ATTACK/USE in `_button_names` already held; left engine mapping in place.

Local `./smoke --hero` (2026-09-18): exit 0, backend=vizdoom E1M1, bound `ws://127.0.0.1:54225`, `SMOKE note: 8765 was busy; live server still defaults to ws://127.0.0.1:8765`, `WIRE CHECK capability=clientPublish camera_schema=foxglove.CompressedImage cmd_vel=1 buttons=1`, `SMOKE OK ticks=8 frames=8 topic=/doom/camera cmd_vel=/cmd_vel`. Bare `./smoke` also exit 0 (entity_count=209). Next: Kimi evaluator re-runs gated checks.


## [2026-09-18] evaluator | HL-nn verdict

Kimi evaluator re-ran every gated HL-01..HL-14 check from $ROOT. Verdict: FAIL 12/14. Ticked HL-01, HL-02, HL-03, HL-04, HL-06, HL-07, HL-08, HL-09, HL-10, HL-11, HL-12, HL-13. Failing: HL-05 (check asserts `.topic` property; installed foxglove SDK exposes a method — `ch.topic() == /doom/camera` verified, product correct) and HL-14 (rg matches only `web/node_modules`; zero product-file matches). Both are contract-check defects needing planner/critic amendments E-R1/E-R2 (eval.md), not generator fixes. Evidence: eval.md (overwritten).

## [2026-09-18] planner | E-R1 E-R2

Applied evaluator amendments E-R1 and E-R2 to `contract.md` only. Did not tick HL-05 or HL-14. Left the twelve already-ticked boxes alone. Did not touch `doom_foxglove/`. Did not start a generator.

- E-R1 (HL-05): replaced `assert getattr(ch, 'topic', None) == CAMERA_TOPIC` with callable-safe `_topic = ch.topic; assert (_topic() if callable(_topic) else _topic) == CAMERA_TOPIC` so the installed SDK method `topic()` compares equal to `CAMERA_TOPIC`.
- E-R2 (HL-14): added `--glob '!**/node_modules/**'` to the rg exclusions. Kept `!.venv/**`, `!.git/**`, `!.agent/**`, and `!*.md`.

Next: Kimi critic re-gate of those two items.
## [2026-09-18] critic | HL-05 HL-14 re-gate
E-R1 (HL-05 callable-safe topic assertion) and E-R2 (HL-14 `!**/node_modules/**` glob) verified applied and mechanical: amended HL-05 `$PY -c` block exits 0 (`HL-05 vizdoom (320, 200) JPEG hz 35`); amended HL-14 rg prints nothing. Verdict PASS. Next: Kimi evaluator re-run of HL-05 and HL-14 only.
## [2026-09-18] evaluator | HL-05 HL-14 re-eval
