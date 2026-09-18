# Eval — 00-harness

**Evaluator:** kimi-k3-high (adversarial; told the harness is broken and must prove it)
**Date:** 2026-09-18
**Verdict: FAIL** — failing item id: **H-16** (as written; reads as a stale contract item — see routing note)

Every item below was checked mechanically from a clean shell at `$ROOT` (`/Users/michael/Documents/foxglove/work/doom`). Command outputs are quoted; nothing here is "looks fine".

## Concurrency warning (read first)

This eval ran while other agents were actively editing the tree. Evidence:

- First `python3 .agent/knowledge-graph/validate.py --harness` run: **exit 0**, `OK: 1556 checks passed`.
- Mid-eval, same command: **exit 1**, 7 H-17 failures in `01-hero-loop/progress.md` (`blockers: HL-05, HL-14 contract-check defects (see eval.md)` — non-Risk ids) and `05-stunt-extras/progress.md` (`status: gated-fail` — outside vocabulary).
- The 01 and 05 planners repaired their own headers during the eval. Two consecutive stability runs at eval close: **exit 0**, `OK: 1563 checks passed`. Current headers: `01` = `status: amended` / `blockers: none`; `05` = `status: amended` / `blockers: none`.

H-17 and H-21 are graded **PASS** against the final, stable disk state; the transient failures are recorded here because they show the H-17 validator correctly catching illegal headers in real time.

## A. Scope and file tree

### H-01 — PASS (with observation)
`find .agent .cursor/rules -type f` shows every required path present. `validate.py --harness` reported no `H-01: missing required path` in any run.
Observation, not a fail of the stated check: `critique.md` under `01`–`04` are extra files referenced from neither `COORDINATION.md` nor `SCHEMA.md` (`grep -n 'critique.md' .agent/COORDINATION.md .agent/knowledge-graph/SCHEMA.md` → exit 1). `eval.md` extras are referenced (`COORDINATION.md:126`). The item's mechanical check passes; the supervisor may want the reference rule enforced or the files referenced.

### H-02 — PASS
`find` output: the only `*.py` under `.agent/` is `.agent/knowledge-graph/validate.py`. All H-01 paths exist.

### H-03 — PASS
`grep -rniE 'FIXME|lorem|<unfilled>' .agent --include='*.md' --include='*.jsonl' --exclude='contract.md' --exclude='critique.md' --exclude='eval.md' --exclude='log.md'` → no output, exit 1 (clean). A scripted scan for a heading immediately followed by another heading across all non-excluded `.md` files → `empty sections: none`.

### H-04 — PASS
Loop `grep -q` over all twelve `` `dec_*` `` ids in `GOAL.md` → no MISSING lines. `grep -c 'North star' .agent/GOAL.md` → 1. `grep -c 'ws://localhost:8765'` → 2.

### H-05 — PASS
`COORDINATION.md:20` names the banned slugs including `inherit`; both allowed slugs present; `COORDINATION.md:137` contains the literal `python3 .agent/knowledge-graph/validate.py --harness && echo "HARNESS OK"`.

## B. Knowledge graph

### H-06 — PASS
`SCHEMA.md` lists all eight node types with a status-vocabulary table (Decision `locked`/`superseded`; Risk `open`/`mitigated`/`closed`; Workstream and Capability `planned`/`in_progress`/`done`/`deferred`), all seven required fields (`id`, `type`, `label`, `body`, `status`, `ts`, `source`), and the id rule "`snake_case`, or a contract item id matching `[A-Z]{1,3}-\d{2}`".

### H-07 — PASS
`SCHEMA.md` edge table lists all six types (`DECIDES`, `DEPENDS_ON`, `EVIDENCED_BY`, `BLOCKS`, `IMPLEMENTS`, `SUPERSEDES`), each with explicit allowed `from-type → to-type` pairs and a one-line semantic; edge fields `from`, `type`, `to`, `ts`, optional `note` documented.

### H-08 — PASS
`python3 .agent/knowledge-graph/validate.py` → `OK: 1371 checks passed`, exit 0. Mutated copy test: `cp nodes.jsonl /tmp/nodes-broken.jsonl; printf '%s\n' '{"id":"x"' >> ...; validate.py --nodes /tmp/nodes-broken.jsonl` → exit 1, `FAIL: 1 of 1372 checks failed - /tmp/nodes-broken.jsonl:102: line does not parse as JSON`. The command is documented copy-pasteably in `SCHEMA.md`.

### H-09 — PASS
Scripted check: all twelve `dec_*` ids present exactly once (duplicate-id scan: none), each `"type": "Decision"`, `"status": "locked"`, non-empty actionable `body`. → `H-09 twelve locked Decisions: True`.

### H-10 — PASS
All six `ws_*` ids present; `os.path.isdir(source)` true for each; `ws_02`–`ws_05` are `deferred`; `ws_00_harness` and `ws_01_hero_loop` are `in_progress`.
Observation, not a fail of the stated check: `ws_03_embed_shell` is still `deferred` in the graph while `03-embed-shell/progress.md` says `status: done`. KG/progress drift for the librarian loop, outside this item's check.

### H-11 — PASS
All five `cap_*` ids present; `cap_stunt_extras` is `deferred`. All four `repo_*` ids carry a URL. `vizdoom_macos_build` and `commercial_wad` are `"status": "open"`. `hw_mac_dev` is `present`. Scripted scan: `H-11 Event nodes: none`.

### H-12 — PASS
`### H-` headings in this contract: 22. `ContractItem` nodes matching `^H-[0-9]{2}$`: 22. Scripted check: `missing IMPLEMENTS: none | bad source: none | bad status: none` (all `specified`, all `source: .agent/workstreams/00-harness/contract.md`, all with an `IMPLEMENTS` edge to `ws_00_harness`).

### H-13 — PASS
Scripted triple check over all 26 required edges from the contract: `H-13 missing required triples: none`. `validate.py --harness` reported no `H-13` failure in any run.

### H-14 — PASS
All four documented queries run from `$ROOT`, each exit 0, non-empty, matching `SCHEMA.md` expectations:
1. Open risks → `vizdoom_macos_build`, `commercial_wad` (two lines, as documented).
2. Next product workstream → `ws_01_hero_loop`.
3. Locked decisions → twelve lines, each `id -> [targets] :: body`.
4. `WS=ws_02_robotics_layout` deps → `ws_01_hero_loop`.

## C. Workstream tree and loops

### H-15 — PASS
All six `contract.md` files name their workstream in the first two lines (verified by `head -20 | grep` per file).

### H-16 — FAIL (as written; likely stale contract item)
Check: each of the four contracts `02`–`05` contains the word `deferred` and an entry condition.
- `02-robotics-layout`: `grep -ci 'deferred'` → 3; has `## Entry condition (what un-defers ws_02_robotics_layout)`. OK.
- `04-record-replay`: count 3; entry-condition section present. OK.
- `05-stunt-extras`: count 3; entry-condition section present; names `01-hero-loop`, `02-robotics-layout`, `03-embed-shell` and all three capabilities. OK.
- `03-embed-shell`: `grep -ci 'deferred'` → **0**; no entry-condition section. Its contract line 7 states: "This file replaces the 2026-09-18 deferral stub. It is a gradeable `ES-nn` contract."

The 03 stub was replaced by a gated `ES-nn` contract after the workstream was un-deferred and evaluated `done` — the phase DAG working as designed. The literal H-16 check still fails on 03. This looks like a **stale contract item** (it froze the seed-time assumption that 02–05 all stay deferred until the harness eval), i.e. supervisor/planner amendment territory per the escalate-on-wrong-contract rule, not a generator defect.

### H-17 — PASS (after concurrent mid-eval repair; see warning above)
Check: `validate.py --harness` reports no `H-17` failure. Two consecutive closing runs: exit 0, no H-17 lines. All six `progress.md` headers read directly: `status` in vocabulary (`in progress`, `awaiting generator`, `done`, `planning complete`, `amended`), `owner` / `updated` / `next action` / `blockers` present before the first blank line, `blockers` is `none`.
Transient failures observed mid-eval (since repaired by their owners): `01-hero-loop/progress.md` blockers line carried `HL-05, HL-14 contract-check defects (see eval.md)` (6 validator failures — ContractItem ids and prose are not Risk ids); `05-stunt-extras/progress.md` briefly carried `status: gated-fail` (outside vocabulary). The validator caught both in real time, which is the H-17 mechanism working.

### H-18 — PASS
`validate.py --harness` reported no `H-18` failure in any run (including the otherwise-failing ones). Every `log.md` states append-only in its first 4 lines. Scripted heading-format scan across all six logs → no violations (exit 1, clean). `00-harness/log.md` has `## [2026-09-18] generator | ...` at lines 5, 17, 21; `01-hero-loop/log.md` at lines 5, 13, 60.

### H-19 — PASS
`loops/README.md` has a section per loop, each with Trigger / Inputs / Output / Exit. Contains `smoke` (the clean-shell smoke-command rule), "Eyeballing is not evidence", the literal `python3 .agent/knowledge-graph/validate.py`, and the phrase `no event deadline` ("There is no event deadline loop in this repository").

### H-20 — PASS
`grep -n 'alwaysApply: true' .cursor/rules/agent-os.mdc` → `3:alwaysApply: true`. Both allowed slugs present. The rule tells agents to resume from `.agent/` and to write to files, not chat. `validate.py --harness` reported no `H-20` failure.

## D. Resume and self-check

### H-21 — PASS (after concurrent mid-eval repair; see warning above)
Check: `python3 .agent/knowledge-graph/validate.py --harness && echo "HARNESS OK"` → exit 0; break one thing → non-zero; restore.
- Break test: `mv nodes.jsonl nodes.jsonl.bak` → exit 1 (`FileNotFoundError`); restored; graph re-parsed (101 nodes, 109 edges). That half passes.
- Delivered-tree half: exit 0 on the first run this session (1556 checks), transiently exit 1 during the concurrent 01/05 header edits, and exit 0 on two consecutive closing stability runs (`OK: 1563 checks passed`). The documented one-command self-check exits 0 on the tree as delivered at eval close.

### H-22 — PASS (with caveat)
`00-harness/log.md` carries `## [2026-09-18] generator | ...` entries. `00-harness/progress.md` status `in progress` is in the H-17 vocabulary with an updated `next action`. Caveat: `$ROOT` is not a git repository (`git rev-parse` → fatal), so the "no in-place rewrite" prong cannot be diff-verified; nothing on disk contradicts the first-writes parenthetical, and the append-only validator checks pass.

## Summary

| | |
|---|---|
| PASS | H-01, H-02, H-03, H-04, H-05, H-06, H-07, H-08, H-09, H-10, H-11, H-12, H-13, H-14, H-15, H-17, H-18, H-19, H-20, H-21, H-22 |
| FAIL | **H-16** (03 contract no longer a deferral stub — likely stale item) |

**Exit codes:** `validate.py --harness` = 0 at eval open (1556 checks), transiently 1 during concurrent 01/05 header edits, 0 on two closing stability runs (1563 checks); graph-only = 0; malformed-graph test = 1; H-21 break test = 1.

**Routing note:** the only failing item, H-16, fails because `03-embed-shell` was un-deferred per its entry condition and its deferral stub was legitimately replaced by a gated `ES-nn` contract — the phase DAG working as designed. That is a **stale contract item**, not a generator defect: escalate to the human/planner to amend H-16 (e.g. scope it to workstreams still `deferred`) rather than restarting the 00 generator. The transient H-17/H-21 failures were introduced and repaired by the 01/05 planners during this eval; no 00 action needed. Secondary observations for the supervisor: unreferenced `critique.md` extras under 01–04 (H-01 parenthetical), and `ws_03_embed_shell` still `deferred` in the graph while its progress says `done` (KG-sync loop territory).

---

# Re-eval — H-16 only (amended stub-OR-gated loop)

**Evaluator:** kimi-k3-high
**Date:** 2026-09-18
**Scope:** H-16 only, after planner amendment and critic PASS (`log.md`: `## [2026-09-18] critic | H-16 re-gate` → PASS). No other item re-graded; the 21/22 PASS verdicts above stand.
**Verdict: PASS** — H-16 ticked in `contract.md`.

Ran the amended copy-paste loop verbatim from `$ROOT`:

```
H-16 02-robotics-layout: gated (10) OK
H-16 03-embed-shell: gated (11) OK
H-16 04-record-replay: gated (7) OK
H-16 05-stunt-extras: gated (6) OK
exit=0
```

All four workstream contracts exist (H-01 tree not relaxed) and each carries real `### (RL|ES|RR|SX)-` numbered headings, so the gated path applies; the stub prong was not needed. Exit code 0. H-16 is now PASS; 00-harness stands at 22/22.
