# Critique — 05-stunt-extras SX-01…SX-06 gate

**Critic:** kimi-k3-high (contract critic, per `.agent/COORDINATION.md`)
**Date:** 2026-09-18
**Target:** `.agent/workstreams/05-stunt-extras/contract.md` (planner's gated SX-nn list)
**Verdict: FAIL** — four numbered amendments below. The contract is close; every amendment is cheap and the current tree already satisfies the stricter form.

Method: every quoted string, import path, and command in the contract was checked against the files on disk. Nothing was graded for product quality; only mechanicality and evadability of the checks.

## What verified clean (no amendment needed)

- **SX-01** — Check runs SDK-free (`topics.py` imports `foxglove` lazily). All quotes exist verbatim: `EVENTS_TOPIC = "/doom/events"` (`doom_foxglove/__init__.py:15`), `EVENTS_SCHEMA` with `"required": ["kind", "message", "tick", "map"]` (`topics.py:34-44`), `"events": Channel(EVENTS_TOPIC, schema=EVENTS_SCHEMA)` (`topics.py:186`), `def event_payload` returning the four keys (`topics.py:239-245`). The worked example `event_payload(LogEvent(message='Entering E1M1', kind='level'), 7, 'E1M1')` returns exactly the asserted dict.
- **SX-02** — All five quoted assignments exist verbatim (`world.py:141-145`); `if event.kind in EVENT_KINDS` is at `topics.py:260`. Each `logs_from_delta` case in the check produces the asserted event through the real code path (traced, not just eyeballed).
- **SX-03 positive path** — Deterministic even with no ViZDoom, no IWAD, and no network: `make_engine` falls back to `FallbackEngine`, whose first `observe()` after `reset()` emits `Entering fallback` with `kind=level` (`engine.py:70-75, 99`), satisfying both the live-event and MCAP gates. Busy 8765 is handled by `fallback_if_busy=True` (`smoke_events.py:68`). Quoted `exec "$PY" -m doom_foxglove.smoke_events` is a verbatim substring of `./smoke-events`.
- **SX-04 parsers** — `MCAP_MAGIC`, `count_mcap_messages`, `list_mcap_topics`, `smoke_events_recording_path` all exist in `doom_foxglove/record.py` (lines 19, 102, 91, 51). `count_mcap_messages` reads MessageIndex records (16-byte entries), so chunked MCAPs count correctly.
- **SX-05 strings** — All three prompt bodies, the heading `## Ask Foxglove (copy-paste)`, and the sentence `No custom agent ships in this repo.` are verbatim in `README.md` (lines 117-136).
- **SX-06 README side** — `## Not in this slice` and all four needles (`remote-access gateway`, `comparison mode UI`, `cloud share links`, `ViZDoom policy vs human`) are present (`README.md:140-142`). The full `doom_foxglove/` package is currently clean for all ten fence needles (verified by rg, zero hits).

## Amendments (required before PASS)

### 1. SX-06: resolve the self-contradictory PASS rule

The item says "PASS only if the `rg` invocation prints nothing" and two sentences later "A comment that names them as out of scope is allowed only if it does not call an API." If a comment in the four files contains the string `comparison mode`, rg prints a line, and the evaluator must judge whether a comment "calls an API" — that is taste, not mechanics, and it contradicts the prints-nothing rule. **Fix:** make any printed line a FAIL, full stop. Out-of-scope naming already has a required home (`README.md` `## Not in this slice`), so the strict rule loses nothing. The four files have zero hits today; the strict rule is satisfiable as-is.

### 2. SX-06: the fence is evadable by adding a new file

The rg covers exactly four files: `smoke-events`, `smoke_events.py`, `world.py`, `topics.py`. A generator could add `doom_foxglove/gateway.py` (remote-access gateway), put a comparison mode in `server.py` or `engine.py`, or ship a policy runner as a new module, and SX-06 still PASSes — contradicting the item's own title ("stay out" of the slice). **Fix:** widen the rg target to `smoke-events doom_foxglove/` (whole package). Verified today: the entire package is clean for all ten needles, so the wider fence passes without touching product code. Scoping `web/` remains 03's business; say so explicitly if intended.

### 3. SX-03: the negative path can false-PASS on an import crash

`$PY -c "import sys; from doom_foxglove.smoke_events import _fail; sys.exit(_fail('critic-injected'))"` exits 1 in two cases: (a) `_fail` works, and (b) the import itself dies (ImportError, SyntaxError, a missing `pillow`/`numpy` on the evaluator's shell) — Python exits 1 either way. As written, `neg_exit=1` cannot distinguish "_fail returns 1" from "the module never imported." The negative path exists to prove the failure channel works; as written it proves nothing. **Fix:** add a stderr assertion — the run must print `SMOKE-EVENTS FAIL: critic-injected` to stderr *and* exit 1. One extra line, fully mechanical.

### 4. SX-05: the checkbox is wider than its check

The checkbox FAILs on "an MCP server, LangChain agent, or custom Foxglove extension whose job is to answer those prompts," but the mechanical check greps exactly three tokens (`FastMCP`, `langchain`, `@modelcontextprotocol`). A bespoke agent on raw `openai`/`anthropic` SDK calls, or a hand-rolled stdio MCP server using none of those tokens, evades the rg — and judging whether some future extension's "job is to answer those prompts" is not mechanical. **Fix (pick one):** (a) narrow the checkbox prose to exactly what the rg plus a filename gate checks — e.g. add `rg -l -e 'agent' -e 'mcp' doom_foxglove --glob '*.py'` must print nothing beyond the existing files; or (b) widen the token list (`openai`, `anthropic`, `mcp\.server`, `stdio_server`). Do not leave prose the evaluator cannot execute.

## Nits (non-blocking; planner may adopt)

- **SX-04:** "Quote `smoke_events_recording_path` returning `recordings/smoke-events.mcap`" — that literal string appears nowhere in `record.py`; the function body is `recordings_dir(root) / "smoke-events.mcap"` (`record.py:51-52`). The Python assert already proves the path; reword the quote instruction to name the body as it exists, or drop it as redundant.
- **SX-03:** "records the default tick count" is asserted by nothing in the check (the text then admits the item grades exit + banner). Trim the clause or point it at SX-04, which owns the file contents.

## Gate decision

**FAIL.** Amendments 1-4 must land in `contract.md` (planner's edit, not mine) before this SX list is critic-gated. Nits are optional. Per the entry condition, `ws_05_stunt_extras` stays `deferred` until the amended contract is re-attacked and passes.

---

# Re-gate — 2026-09-18 (critic, kimi-k3-high)

**Target:** amended `contract.md` (planner applied amendments 1–4; nits left untouched, which is allowed).
**Verdict: PASS.**

Method: each amendment was diffed against the amended contract text, and the two fence `rg` invocations were re-run from `$ROOT` to confirm the stricter rules are satisfiable by the tree on disk (a fence that false-FAILs the current tree would not be mechanical).

## Amendment verification

1. **SX-06 self-contradiction — resolved.** The "allowed only if it does not call an API" sentence is gone (grep: no match). The PASS rule now reads "PASS only if the `rg` invocation prints nothing … **Any printed line is FAIL.** Comments are not exempt." One rule, no taste.
2. **SX-06 fence widened — resolved.** Fence target is now "`smoke-events` and the entire `doom_foxglove/` package", the `rg` command targets `smoke-events doom_foxglove/`, and `web/` is explicitly declared 03's business and out of this `rg`. Re-ran the exact ten-needle `rg` from `$ROOT`: zero hits, exit 1 — the wider fence passes the current tree without product edits.
3. **SX-03 negative path — resolved.** The check now captures stderr (`2>&1 >/dev/null`) and PASS requires `neg_exit=1` **and** stderr containing the exact substring `SMOKE-EVENTS FAIL: critic-injected`. The contract explicitly states an ImportError/SyntaxError/missing-dep crash that exits 1 without the banner is FAIL. The false-PASS channel is closed.
4. **SX-05 prose narrowed — resolved.** The unexecutable "custom Foxglove extension whose job is to answer those prompts" prose is gone (grep: no match). The item now FAILs only on missing/paraphrased prompt bodies or a hit from the three-token `rg` (`FastMCP`, `langchain`, `@modelcontextprotocol`), and explicitly forbids FAILing on any other library, filename, or agent-shaped module. Checkbox and check are the same width. Re-ran the token `rg`: zero hits, exit 1.

## Mechanicality of SX-01…SX-06 as amended

- **SX-01** — pure Python asserts plus verbatim named quotes; no judgment calls.
- **SX-02** — asserts drive the real `logs_from_delta` path; quotes are exact assignments; fifth-member rule is a set-equality assert.
- **SX-03** — exit code + banner substring; negative path is deterministic and now distinguishes `_fail` from an import crash.
- **SX-04** — in-repo parser only (`count_mcap_messages`, `list_mcap_topics`), magic-bytes assert, count ≥ 1; smoke-print-only verification is an explicit FAIL.
- **SX-05** — exact string containment plus a bounded token rg with an explicit no-taste clause.
- **SX-06** — prints-nothing is PASS, any line is FAIL; README needles are exact string asserts.

Every check is runnable from a clean shell at `$ROOT` and has a binary outcome. Nits (SX-04 quote literal, SX-03 "default tick count" clause) remain unapplied; they are non-blocking and do not affect mechanicality.

## Re-gate decision

**PASS.** SX-01…SX-06 are mechanical. Entry condition (3) for `ws_05_stunt_extras` is now met by this gate; conditions (1) and (2) (KG capabilities `done`, 01/02/03 evaluator verdicts `done`) remain unmet and are owned by those loops, so the workstream stays `deferred` in the graph until they land. Next: Kimi evaluator runs the checks and ticks SX items.
