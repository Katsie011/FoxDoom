# Log — readme

## [2026-09-18] supervisor | start README rewrite from why

Human: current README reads as AI slop; compare to best OSS READMEs; Grok reviews and improves. Ignore Granola. Lead with the why.

Why on disk (GOAL north star): Foxglove teleoperates robots; a ViZDoom marine is the fake robot; stock panels only; a host canvas is a failed stunt.

Work lives in `.agent/workstreams/readme/` because 04 PR-10 FAILs if `.agent/workstreams/06-*` exists. Deliverable is repository `README.md`. No product code. Frozen string checks from HL-13, RR-05, RR-06, SX-05, SX-06 stay satisfied.

Next: planner writes PLAN.md and contract.md.

## [2026-09-18] planner | README contract from why

Wrote `PLAN.md` (why this repo exists, then voice/order/scope) and `contract.md` (RD-01…RD-18, checkboxes unchecked). Frozen HL-13 / RR-05 / RR-06 / SX-05 / SX-06 README needles are RD-10…RD-16. Rubric is why-first 0.30 / human voice 0.30 / happy-path 0.20 / no-spec-dump 0.20, pass 0.75. No `README.md` edit. No `06-*`.

Next: Kimi critic gate.

## [2026-09-18] critic | README contract gate

Verdict FAIL — amendments required (`.agent/workstreams/readme/critique.md`). Ran all 18 checks against today's README: must-fail fixtures RD-01/RD-02/RD-05/RD-08/RD-16 all fail correctly; frozen RD-10…RD-16 are faithful copies of HL-13/RR-05/RR-06/SX-05/SX-06. Six defects: RD-02 regex false-FAILs good prose (proven), RD-04/RD-05 fallback-paraphrase hole, RD-06 `find()==-1` false PASS on Requirements order (proven), RD-08 blank-line catalog evasion (proven), RD-17 fails on 19 unrelated dirty paths incl. its own workstream dir (proven against live tree), rubric axes duplicate the checkboxes. Six numbered amendments with exact replacement text in critique.md.

Next: planner applies amendments, then re-gate.

## [2026-09-18] critic | README contract re-gate

Verdict GATE PASS. All six amendments verified present in `contract.md` (quoted in critique.md re-gate section). Re-ran amended must-fail checks verbatim against today's README: RD-01/RD-02/RD-05/RD-08/RD-16 all still FAIL correctly; RD-02's tightened hits list is now exactly the three architecture copulas. Fix verification on synthetic inputs: good prose passes RD-02 (worst=1), Requirements-first README caught by RD-06, blank-line catalog caught by RD-08 section count, RD-17 passes with the 23-path baseline the planner wrote (`rd17-baseline.txt`). Rubric axes no longer duplicate checkboxes; 0.75 threshold plus first-10-lines quote requirement stands.

Next: Grok generator rewrites `README.md` only.

## [2026-09-18] planner | apply critic amendments 1-6

Applied critique.md amendments 1–6 into `contract.md`: tighter RD-02 copula regex; RD-04/RD-05 fallback paraphrase regex; RD-06 `-1` false-PASS fix + embed prefix `http://localhost:5173`; RD-08 per-section catalog count; RD-17 baseline-diff check; rubric axes no longer duplicate RD boxes. Wrote `rd17-baseline.txt` from current porcelain. All RD boxes still `- [ ]`. Frozen RD-10…RD-16 untouched. No `README.md` edit.

Next: critic re-gate.

## [2026-09-18] generator | rewrite README from why

Rewrote `README.md`: why (Foxglove teleoperates a marine; Image not canvas), then `## Run` (`uv` / `./smoke` / `python -m doom_foxglove` / embed `http://localhost:5173/` / `ws://localhost:8765` + ClientPublish), then frozen `## Replay an MCAP`, `## Ask Foxglove (copy-paste)`, `## Not in this slice`, then brew cmake / ViZDoom fallback / ephemeral ports / `--port 8766`. Frozen needles copied verbatim. No contract ticks. No `web/README.md` edit. No `06-*`.

Next: Kimi evaluator.

## [2026-09-18] evaluator | readme verdict

Verdict FAIL — RD-17 only. Ran all 18 checks verbatim against `README.md` (`$PY` = `.venv/bin/python`): RD-01…RD-16 and RD-18 PASS, boxes ticked by this evaluator. Rubric 0.89 ≥ 0.75 (first-screen 0.9 / concreteness 0.9 / economy 0.9 / calibration 0.85; first 10 lines quoted in eval.md). RD-17 FAILs on dirty path `.agent/workstreams/04-record-replay/eval.md` (mtime 16:20:54, 24 s after baseline, before README mtime 16:25:29) — evidence points to a concurrent 04-workstream evaluator, not the readme generator, whose footprint is `README.md` only. Generator did not tick any box (process clean). Full evidence in `eval.md`.

Next: supervisor confirms the 04 eval write, refreshes `rd17-baseline.txt`, re-runs the RD-17 check. Do not restart the generator for a path it did not touch.

## [2026-09-18] evaluator | RD-17 re-eval

Supervisor added `.agent/workstreams/04-record-replay/eval.md` to `rd17-baseline.txt` (concurrent 04 evaluator write, not the README generator). Re-ran the RD-17 Check verbatim: `RD-17 scope []` — PASS. Ticked RD-17. All 18 items now PASS; rubric 0.89 ≥ 0.75 stands. Final verdict: PASS.

Next: none. Workstream done.

## [2026-09-18] librarian | kg sync

Appended Workstream `ws_readme` (done) and ContractItem nodes `RD-01` through `RD-18` (verified), plus IMPLEMENTS edges RD-01…RD-18 → ws_readme. Skipped optional Repo nodes: `repo_lunar_lander` already exists; did not add `repo_age`, `repo_jq`, or `repo_mcap`. No SUPERSEDES. No Decision nodes.

## [2026-09-18] supervisor | README rewrite closed

Human asked for an OSS-style README starting from why. Grok rewrote `README.md`; Kimi graded RD-01…RD-18 PASS, rubric 0.89. KG sync done. Harness OK. Workstream `readme` (not `06-*`) is done.

## [2026-09-18] planner | architecture diagram contract

Human: add a high-level mermaid architecture diagram near the top of the README, Foxglove components grouped. Planner appended only: RD-19 (mermaid fence in the RD-01 preface, after why needles, before `## Run`, `flowchart`/`graph ` plus `-->`) and RD-20 (required labels + Foxglove `subgraph` or `classDef`/`class `, no `<canvas`/`getContext`). PLAN.md got a short Architecture section and an extra happy-path step. RD-01…RD-18 stay `[x]`. RD-19/RD-20 stay `[ ]`. No `README.md` edit. Current README fails both new checks on `no mermaid fence` (must-fail fixture).

Next: Kimi critic gate on RD-19/RD-20.

## [2026-09-18] critic | RD-19 RD-20 gate

Verdict FAIL — four amendments (7–10) with exact replacement text in `critique.md`. Ran both new checks verbatim against today's README: both FAIL correctly on `no mermaid fence` (must-fail fixture holds; PNG-only "diagram" also fails). Synthetic-fixture attacks proved two false PASSes (needles stuffed in a `%%` comment render nothing yet pass; one keyword-salad node passes) and three false FAILs (capitalized `Embed` node, idiomatic `classDef fox` + `class I,T,E,G fox` short-ID style, spaced ` ``` mermaid ` fence). Amendments: strip `%%` comments and case-insensitive needles (7, 8), structural floors ≥4 needle-lines / ≥3 `-->` edges (9), classDef alternative grades the fox-named class with ≥3 classed nodes instead of literal sdk/embed/panel node IDs (10). Post-amendment checks re-verified against all eight fixtures: good diagrams pass, sloppy ones fail, today's README still fails. No contract edit, no boxes ticked, no README edit.

Next: planner applies amendments 7–10, then critic re-gate.

## [2026-09-18] critic | RD-19 RD-20 re-gate

Verdict GATE PASS. All four amendments verified present in `contract.md` (quoted in critique.md re-gate section): RD-19 spaced-fence regex + `%%` strip; RD-20 `%%` strip + case-insensitive needles; ≥4 needle-line / ≥3 `-->` edge floors; classDef alternative grading a fox-named class with ≥3 classed nodes. Re-ran both amended checks verbatim against today's README: both still FAIL on `no mermaid fence` (must-fail holds). Re-ran the contract's verbatim code against the six attack fixtures: good subgraph / classDef / caps-Embed / spaced-fence diagrams PASS, comment-stuffed and keyword-salad diagrams FAIL. Checks still mechanical (text-only). No contract edit, no boxes ticked, no README edit.

Next: Grok generator inserts the mermaid diagram into `README.md` only. Must not tick boxes.

## [2026-09-18] planner | apply critic amendments 7-10

Applied critique.md amendments 7–10 into `contract.md` RD-19/RD-20 only, using the critic's exact replacement text: spaced ` ``` mermaid ` fence opener; strip `%%` comments before body asserts; case-insensitive needles and `<canvas`/`getContext`; ≥4 distinct needle-lines and ≥3 `-->` edges; `classDef` whose name contains `fox` plus a `class ` line assigning 3+ nodes. RD-01…RD-18 stay `- [x]`. RD-19/RD-20 stay `- [ ]`. No `README.md` edit. No `06-*`. Status `amended`.

Next: critic re-gate.

## [2026-09-18] generator | preface architecture mermaid

Inserted a GitHub-safe `flowchart TB` mermaid fence in `README.md` after the unchanged why paragraph and before `## Run`. Nodes: Freedoom / IWAD, ViZDoom, doom_foxglove, foxglove-sdk WebSocket (ClientPublish, :8765), host WASD, @foxglove/embed, Foxglove app, Image / 3D / Teleop / Gauge / Log, MCAP sidecar, Replay. Foxglove grouped with `subgraph foxglove["Foxglove"]` and `classDef fox` on seven nodes. No `## Architecture` heading. No PNG. No contract ticks. No Python/layouts/web/src edits.

Self-check: RD-19 and RD-20 Check blocks PASS; RD-01 still why-then-`## Run` with mermaid closed in the preface; RD-02…RD-16 and RD-18 still PASS.

Next: Kimi evaluator.

## [2026-09-18] evaluator | mermaid diagram verdict

Verdict PASS. Ran RD-19 and RD-20 Checks verbatim (`$PY` = `.venv/bin/python`): `RD-19 mermaid-in-preface`, `RD-20 foxglove-group-labels`. Re-ran RD-01 verbatim against the changed preface: `RD-01 why-first` (first `##` still `## Run`, fence closed inside the preface). Sampled RD-06 / RD-08 / RD-10 for mermaid regressions: all PASS. Skipped RD-02…RD-05, RD-07, RD-09, RD-11…RD-18 (stated in eval.md; prior ticks stand). Ticked RD-19 and RD-20 only. Rubric 0.85 ≥ 0.75 (first-screen 0.8 — the 41-line fence pushes the run command just past screen one; concreteness 0.9; economy 0.85; calibration 0.85), first 10 lines quoted in eval.md.

Next: none. All 20 items ticked; workstream done.

## [2026-09-18] generator | MCAP Replay inside Foxglove subgraph

Moved `mcap["MCAP sidecar"]` and `replay["Replay"]` node declarations from outside the mermaid fence into `subgraph foxglove["Foxglove"]`. Added `mcap` and `replay` to the `class ... fox` line. Edges stay `sdk --> mcap --> replay --> app`. WASD / ViZDoom / doom_foxglove / Freedoom stay outside. Why paragraph unchanged. Fence still closes before `## Run`. No contract ticks. No other files. No `06-*`.

Self-check (not a grade): RD-19 and RD-20 Check blocks PASS; `flowchart` present; ≥3 `-->`; subgraph foxglove; classDef fox classes ≥3 nodes including `mcap`.

Next: Kimi evaluator re-eval of RD-19 / RD-20.

## [2026-09-18] evaluator | mermaid MCAP-in-Foxglove re-eval

Generator moved `mcap` / `replay` nodes into `subgraph foxglove["Foxglove"]` and extended `class ... fox` to 9 nodes. Re-ran RD-19 and RD-20 Checks verbatim (`$PY` = `.venv/bin/python`): `RD-19 mermaid-in-preface`, `RD-20 foxglove-group-labels` — both PASS. Subgraph block quoted in eval.md proving mcap/replay are inside. Ticks were already set; they stay. No other items re-run.

Next: none. Progress remains done.

## [2026-09-18] librarian | kg sync RD-19 RD-20

Appended ContractItem nodes RD-19 and RD-20 (verified) and IMPLEMENTS edges to ws_readme. Evaluator PASS on mermaid-in-preface and foxglove-group-labels; Foxglove subgraph includes sdk, panels, embed, app, MCAP, Replay. No Decision nodes. No 06-*. Did not edit README.md. Did not rewrite JSONL in place.

