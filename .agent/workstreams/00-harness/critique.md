# Critique — 00-harness

This file is the landing place for the Kimi K3 contract critic. It has not run yet.

The generator created this path so the harness tree in H-01 is complete. A generator may not author a critic verdict, may not rubber-stamp this contract, and may not tick any item.

When the critic runs, it writes a verdict here (`PASS`, `PASS_WITH_AMENDMENTS`, or `FAIL`) with numbered amendments the planner must apply before any later harness-only generator is considered gated. Until that happens, evaluators still grade the files against the H-nn items as written: the items are mechanical, and the missing critic pass is a process gap the supervisor already accepted by combining 00 and 01 in one spawn.

## What a later critic should attack

- Whether H-02 honestly separates 00 from 01 after a combined spawn that also wrote `doom_foxglove/`.
- Whether a planning-stub `01-hero-loop/contract.md` is allowed to exist while product code ships against it.
- Whether seeding `SUPERSEDES` as unused is a schema hole or an honest empty set.
- Whether `vizdoom_macos_build` should `BLOCKS` the capability as well as the workstream.

## What this file is not

Not an evaluation. Not a generator self-grade. Not a substitute for `.agent/workstreams/00-harness/eval.md`.

---

## [2026-09-18] Critic re-gate of amended H-16 — verdict: PASS

**Critic:** kimi-k3-high. Scope: the amended H-16 stub-OR-gated check only. I did not author the contract, did not touch product code, did not edit `contract.md`.

### The check is mechanical and runs from `$ROOT`

I copy-pasted the exact loop from `contract.md` H-16 into a clean shell at `/Users/michael/Documents/foxglove/work/doom`. Output:

```
H-16 02-robotics-layout: gated (10) OK
H-16 03-embed-shell: gated (11) OK
H-16 04-record-replay: gated (7) OK
H-16 05-stunt-extras: gated (6) OK
OVERALL: PASS
```

Exit 0. Every command in the loop is `test -f` / `grep -c` with `|| true` guards, so the `grep` exit-1-on-no-match idiom cannot silently abort the loop. The both-match case is handled deterministically (gated checked first), matching the prose "matching both is a PASS".

### Attacks attempted and why they do not block PASS

1. **False-positive via fenced code.** `grep -cE '^### (RL|ES|RR|SX|HL)-'` cannot tell a real heading from a quoted heading inside a ```` ``` ```` fence. I inspected all four files: every match is a real section heading with body prose, none inside fences (fence counts even: 18/6/14/16). Not exploitable on the delivered tree; a future generator could game it, but the grading rule grades the stated check, and the evaluator reads files too.
2. **Prefix/workstream mismatch.** The gated regex accepts any of the five prefixes in any of the four files — `02-robotics-layout` would pass with `### HL-01`. Verified on disk: prefixes are correct per workstream (RL→02, ES→03, RR→04, SX→05). A tightening amendment (`02` must match `RL-`, etc.) is worth folding into a future planner pass but is not a current failure.
3. **Stub path under-enforces prose.** The prose requires a stub to name what the workstream owns and the KG nodes gating it; the check only greps `deferred` + `entry condition` (plus the 05 caps alternation, where one of six alternatives suffices). Moot today — all four workstreams are on the gated path — and the stub path remains correct for any workstream that regresses to deferred.
4. **H-01 not relaxed.** The loop still `test -f`s all four files; H-01 tree is untouched by the amendment. H-12 heading count unchanged (still 22 `### H-` items), so the ContractItem seed count is unaffected.

### Verdict

**PASS.** The amended H-16 is mechanical, reproducible from `$ROOT`, and resolves the stale-item failure the evaluator routed here (03 legitimately un-deferred). Next step: Kimi evaluator re-run of H-16 only.
