# Loops

Two loops keep the build honest between supervisor turns. Each one is specified below with the same four labels — **Trigger**, **Inputs**, **Output**, **Exit / stop** — so any agent can run it or disarm it without asking.

Every loop obeys the append-only rule from `.agent/COORDINATION.md`: its result lands as a dated `log.md` entry (and graph triples where relevant), never as a chat message that disappears. A loop that only reports into chat has produced nothing.

Loops are armed only after the harness exists and its evaluation passes. Arming a loop against an unevaluated harness just automates a broken read.

There is no event deadline. `.agent/GOAL.md` sequences by phase gating, not by calendar. **Do not invent a daily deadline loop.** There is no event deadline loop in this repository; if a later human adds a ship date, they must amend `GOAL.md` and this file together.

## 1. Eval-after-generator loop

**Trigger.** Fires automatically after **every** generator run, with no exceptions and no "this one was small" discount. The generator's own last log entry is the trigger signal.

**Inputs.** The owning workstream's `contract.md` (every numbered item), its `progress.md`, the generator's diff, and whatever the contract's checks tell it to execute. The evaluator runs on a **different model** from the generator — generators use `cursor-grok-4.6-high-fast`, evaluators use `kimi-k3-high` — and is told from its first instruction that the work is broken and its job is to prove it.

**Output.** A verdict written into the workstream's `progress.md` (the `status:` line plus a verdict section) and an appended `## [YYYY-MM-DD] evaluator | <workstream> verdict` entry in its `log.md`. The verdict must tick **every** contract item id individually, each with either the command output that proves it or the exact quoted file text that satisfies it.

Hard rules for this loop:

- The evaluator must **run** the smoke command from a clean shell. Reading the diff and reasoning about what it probably does is insufficient and scores the item as a fail. Eyeballing is not evidence.
- An item the evaluator did not mechanically check is a fail, not a pass. "Looks fine" is a fail.
- The evaluator may not fix anything. It grades and returns.
- Checkbox ink is evaluator-only: a generator that ticked a `- [ ]` has violated its own handoff, and that alone fails the run.

**Exit / stop.** On pass: hand back to the supervisor and let the knowledge-graph sync loop run. On fail: route back to the **generator** as a restart against the contract, not as a patch list — the fail entry names the failing item ids and nothing else, so the next attempt is a fresh read of the contract rather than archaeology on a broken diff. The loop stops routing and escalates to the human only when the failure shows the **contract itself is wrong**, never merely because an attempt failed.

## 2. Knowledge-graph sync loop

**Trigger.** Runs once at the end of each **successful** evaluation, immediately after the evaluator's pass verdict lands. It does not run after a fail — a failed attempt has no facts worth recording beyond its log entry.

**Inputs.** The evaluator's verdict, the `log.md` entries appended since the last sync, the workstream's `contract.md`, and the current `nodes.jsonl` / `edges.jsonl`. The librarian runs on `cursor-grok-4.6-high-fast` with deliberately narrow scope.

**Output.** Appended lines in `.agent/knowledge-graph/nodes.jsonl` and `.agent/knowledge-graph/edges.jsonl` — new `ContractItem` status records, new `Capability` or `Workstream` status assertions, and new edges for relationships the log and contracts already state. Any summary or index the graph carries is brought back into agreement with the files. Then re-run the validation command from `.agent/knowledge-graph/SCHEMA.md`:

```sh
python3 .agent/knowledge-graph/validate.py
```

A sync that leaves that command non-zero is not finished. The librarian closes with its own `## [YYYY-MM-DD] librarian | kg sync` entry naming the node and edge ids it appended.

**No scope creep.** The librarian records only what the log, the contracts, and the verdict already assert. It may **not** invent a new `Decision` node, reword a locked decision, soften a `Risk`, rewrite an existing graph line in place, or add a node for something it merely inferred. A fact that is not already written down somewhere else is not the librarian's to create — it is a question for the human, routed through the supervisor.

**Exit / stop.** Ends when the validation command exits 0 and the log entry is appended. It disarms permanently when the graph is retired (goal change or archive), and is skipped for any evaluation that failed.
