# Critique — README contract gate (RD-01…RD-18)

**Critic:** kimi-k3-high
**Date:** 2026-09-18
**Verdict: FAIL — amendments required.** Six defects, three of them proven with synthetic inputs, one proven against the live working tree. The must-fail fixtures all fail correctly; the frozen copies are faithful. The contract is close, but RD-06 has a real false-PASS bug, RD-17 cannot pass in this tree at all, and RD-02 false-FAILs good prose.

## Method

Every check was run verbatim from a clean shell at `$ROOT` with `$PY=.venv/bin/python` against today's `README.md`. Frozen items were diffed against HL-13 (`01-hero-loop/contract.md`), RR-05/RR-06 (`04-record-replay/contract.md`), SX-05/SX-06 (`05-stunt-extras/contract.md`).

## Must-fail fixtures: all fail as intended

| Item | Today's result | Evidence |
| --- | --- | --- |
| RD-01 | FAIL (correct) | `AssertionError: ## Requirements` — first `##` is Requirements |
| RD-02 | FAIL (correct) | `AssertionError: (3, [...])` — copula run of 3 in the current opening |
| RD-05 | FAIL (correct) | `AssertionError: ('brew cmake', 1490, 742)` — brew at byte 742, first run command at 1490 |
| RD-08 | FAIL (correct) | `AssertionError: 9` — nine consecutive `- \`/…` bullets |
| RD-16 | FAIL (correct) | body starts with `Skipped (needs a fleet … extras cut)` |

No "must fail today" item passes the current README. That part of the contract works.

## Per-item findings

- **RD-01** — mechanical, fails today correctly. Prescriptive needle set (`Foxglove`, `robot`, `marine`, `Image`, `canvas`, `teleoperat*`) matches PLAN's stated why; capital `Image` is intentional (the panel name). No amendment.
- **RD-02** — fails today correctly, but the copula regex is loose: `^(The|A|An)\s+\S.{0,120}?\bis\b\s+` matches any The/A/An sentence containing " is " anywhere within 120 chars, including subordinate clauses. It already matched `The smoke command will try to download official Freedoom 0.13.0 … if none is found.` in today's README — not an architecture copula. **Proven false FAIL:** the good prose `The smoke command downloads Freedoom if none is found. The live server binds port 8765 unless it is taken. A replay file is what you open afterwards.` scores worst=3 → FAIL. Amendment 1.
- **RD-03** — mechanical, passes today (no banned words present). Banned list matches PLAN anti-patterns. No amendment.
- **RD-04** — mechanical, fails today correctly (fallback hedge at line 22). Hole: it bans only the exact string `If ViZDoom cannot import`; a paraphrase (`If ViZDoom fails to import`, `when the ViZDoom wheel won't build`) in the first screen passes. Shared with RD-05/RD-06 — see Amendment 2.
- **RD-05** — mechanical, fails today correctly. Same paraphrase hole: ordering asserts are guarded by `if i >= 0`, so a renamed fallback section escapes ordering entirely. Amendment 2.
- **RD-06** — mechanical, fails today correctly, but has a **proven false PASS**: in the Requirements clause, `text.find('uv venv')` returns `-1` when the string is absent, and `-1 < req` is True, so `assert smoke < req or text.find('uv venv') < req or …` passes trivially. Proven with a synthetic README that puts `## Requirements` before any run command and never says `uv venv` — the check printed PASS. This is exactly the anti-pattern PLAN names (`## Requirements … before a working install+run`). Amendment 3. Minor: the embed needle `http://localhost:5173/` requires the trailing slash; `http://localhost:5173` (a correct URL) FAILs. Folded into Amendment 3.
- **RD-07** — mechanical, passes today (embed link exists in the Open Foxglove section). Same trailing-slash nit; fixed by Amendment 3.
- **RD-08** — mechanical, fails today correctly (worst=9). **Proven false PASS:** the same nine-topic catalog with one blank line after every fifth bullet scores worst=5 → PASS. The item bans the catalog, not the formatting trick. Amendment 4.
- **RD-09** — mechanical, passes today (hits=[]). Threshold `< 2` impl tokens is a reasonable vendoring tripwire. No amendment.
- **RD-10** — mechanical, passes today. Needle set is byte-identical to HL-13's string list. Frozen parity confirmed. No amendment.
- **RD-11** — passes today (3 rg hits). Regex identical to HL-13. No amendment.
- **RD-12** — passes today. rg needles identical to HL-13; the `Do not copy a commercial` / `doom.wad` / `doom2.wad` asserts pin the current line. No amendment.
- **RD-13** — passes today. Check is RR-05's verbatim plus the heading assert; RR-05's own text is unchanged. No amendment.
- **RD-14** — passes today. Identical to RR-06's README half. No amendment.
- **RD-15** — passes today. Heading, fence sentence, and three prompt bodies byte-identical to SX-05. The FastMCP/langchain rg half correctly stays with 05. No amendment.
- **RD-16** — mechanical, fails today correctly (`Skipped` opener, `extras cut`). Needles identical to SX-06's README half; the anti-agent-speak asserts are additive, not weakening. No amendment.
- **RD-17** — **proven contract defect.** Ran the check today: it FAILs with 19 extra paths, none of them produced by any README rewrite: `_vizdoom.ini`, `doom_foxglove/server.py`, `doom_foxglove/control.py`, `doom_foxglove/smoke_pause_replay.py`, `smoke-pause-replay`, `web/index.html`, `web/src/*` (6 files), the 03/04 workstream files — and, farcically, `.agent/workstreams/readme/` itself (the untracked workstream directory the contract lives in). The tree is dirty with in-flight PR-slice work and there is no reason to believe it will be clean when the generator runs. As written, a perfect README-only generator cannot pass. Amendment 5.
- **RD-18** — mechanical, passes today (no `06-*`, no image refs). No amendment.

## Rubric

As written the rubric is close to rubber in the pass direction. why-first ≈ RD-01, human voice ≈ RD-02/RD-03, happy-path ≈ RD-05/06/07, no-spec-dump ≈ RD-08/09: a README that ticks every RD box scores ~1.0 almost by construction, so the 0.75 threshold adds little independent signal. Its only real value is the residual taste the checks can't see (manifesto cadence that dodges the banned-word list, prose concreteness). Keep a rubric, but point at least half the weight at things no checkbox grades, and force the evaluator to quote the first screen when scoring. Amendment 6.

## Amendments (planner applies; critic does not edit contract.md)

### Amendment 1 — RD-02: tighten the copula regex

Replace

```python
copula = re.compile(r'^(The|A|An)\s+\S.{0,120}?\bis\b\s+', re.I)
```

with

```python
copula = re.compile(r'^(The|A|An)\s+\S+(?:\s+\S+){0,4}\s+is\b\s+', re.I)
```

Verified: the tightened regex still scores worst=3 on today's bad opening (`A ViZDoom process is the fake robot. The Foxglove SDK WebSocket is the live connection. The framebuffer is …`) and scores worst=1 on the good-prose sample above. `is` must be the main verb within five words of the subject, which is what "X is the Y" means.

### Amendment 2 — RD-04/RD-05: close the fallback-paraphrase hole

In RD-04, replace the single-string assert with a regex over the first 40 lines:

```python
import re
assert not re.search(r'(?i)vizdoom.{0,40}(cannot|can\'t|fails?|won\'t|unable).{0,20}(import|build|install)', first), 'fallback hedge in first 40 lines'
```

(keep the existing exact-string assert too). In RD-05, add the same regex as a third late marker: compute `m = re.search(r'(?i)vizdoom.{0,40}(cannot|can\'t|fails?|won\'t|unable).{0,20}(import|build|install)', text)` and, if `m`, assert `first_run < m.start()`. This keeps today's FAIL (the literal string is present at byte 742 region and line 22) while catching renames.

### Amendment 3 — RD-06: fix the `-1` false PASS and the trailing-slash nit

Replace the Requirements clause

```python
if req >= 0:
    assert smoke < req or text.find('uv venv') < req or text.find('python -m doom_foxglove') < req, 'Requirements before a run command'
```

with

```python
if req >= 0:
    run_before_req = any(
        0 <= text.find(s) < req
        for s in ('./smoke', 'uv venv', 'python -m doom_foxglove')
    )
    assert run_before_req, 'Requirements before a run command'
```

In RD-06 and RD-07, change the embed needle from `http://localhost:5173/` to `http://localhost:5173` (prefix of the slashed form; strictly more lenient, still fails if the URL is absent).

### Amendment 4 — RD-08: count the catalog, not just the streak

After the existing `assert worst < 6, worst`, add:

```python
import re as _re
sections = _re.split(r'(?m)^## ', '\n'.join(lines))
for sec in sections:
    n = sum(1 for l in sec.splitlines() if topic_bullet.match(l))
    assert n < 6, ('topic catalog in one section', n)
```

Verified: today's live-server section has 9 such bullets → still FAILs; the blank-line-evasion sample has 9 in one section → now FAILs; a README naming two or three topics as bullets in passing still PASSes.

### Amendment 5 — RD-17: grade the generator's delta, not the world's dirt

Replace the body of the RD-17 check with a baseline-diff check:

```sh
$PY -c "
import subprocess
from pathlib import Path
allowed = {'README.md', 'web/README.md'}
baseline_file = Path('.agent/workstreams/readme/rd17-baseline.txt')
baseline = set()
if baseline_file.exists():
    baseline = {l.strip() for l in baseline_file.read_text().splitlines() if l.strip()}
names = set()
stat = subprocess.check_output(['git', 'status', '--porcelain'], text=True)
for line in stat.splitlines():
    path = line[3:].strip()
    if ' -> ' in path:
        path = path.split(' -> ', 1)[1]
    if path:
        names.add(path)
names |= {l.strip() for l in subprocess.check_output(['git', 'diff', 'HEAD', '--name-only'], text=True).splitlines() if l.strip()}
new = {n for n in names if n not in baseline and not n.startswith('.agent/workstreams/readme/')}
extra = new - allowed
assert not extra, extra
if 'web/README.md' in new:
    num = subprocess.check_output(['git', 'diff', 'HEAD', '--numstat', '--', 'web/README.md'], text=True).strip()
    if num:
        add, dele, _ = num.split('\t', 2)
        assert int(add) + int(dele) <= 4, ('web/README.md too large', num)
    web = Path('web/README.md').read_text(encoding='utf-8')
    assert 'README' in web
print('RD-17 scope', sorted(new))
"
```

And add to the item text: "Before generation starts, the evaluator (or planner at gate time) writes `.agent/workstreams/readme/rd17-baseline.txt` containing the current `git status --porcelain` path list, one path per line. The check FAILs only on dirty paths that are new relative to that baseline." Notes: (a) using `git diff HEAD` instead of `git diff` also closes the staged-changes bypass in the current numstat leg; (b) excluding `.agent/workstreams/readme/` stops the contract from flagging its own directory; (c) baseline subtraction means pre-existing PR-slice dirt (`_vizdoom.ini`, `web/src/*`, `doom_foxglove/*`) cannot fail a README-only generator, while any *new* product-file edit still fails.

### Amendment 6 — Rubric: grade what the checkboxes cannot

Replace the axis table with:

| Axis | Weight | 0 | 1 |
| --- | --- | --- | --- |
| first-screen usefulness | 0.35 | A stranger cannot tell what running this gets them | A stranger knows in one screen: Foxglove drives a DOOM marine, and the exact command to see it |
| prose concreteness | 0.35 | Manifesto cadence, abstraction, or slop the banned-word list misses | Short concrete sentences; every claim names a thing in this repo |
| section economy | 0.15 | Reader meets a detail wall before a payoff | Each section earns its place; details deferred past the happy path |
| calibration | 0.15 | Reads nothing like the good reference | Same register as gasmith/foxglove-lunar-lander: product as UI, then run |

Keep the 0.75 threshold and add: "The evaluator quotes the first 10 lines of the README in eval.md when scoring; an unscored or unquoted rubric is a fail." With these axes the rubric no longer duplicates RD-01…RD-09 (those already gate ordering/strings) and a checkbox-perfect but soulless rewrite can still fail on concreteness.

## What is NOT defective

- All five must-fail fixtures fail today's README with the intended assertion.
- RD-10…RD-16 are faithful copies of HL-13 / RR-05 / RR-06 / SX-05 / SX-06 README halves; nothing weakened.
- RD-18 correctly refuses to fail a missing screenshot.
- The grading header (`$PY`, `$ROOT`, evaluator-only ticking) is unambiguous.

---

## Re-gate (2026-09-18, second pass)

**Verdict: GATE PASS.** All six amendments are present in `contract.md`, still mechanical, and the must-fail fixtures still fail today's README. No new defects found.

### Amendment presence (quoted from amended contract.md)

1. **RD-02 tightened regex** — present: `copula = re.compile(r'^(The|A|An)\s+\S+(?:\s+\S+){0,4}\s+is\b\s+', re.I)`.
2. **RD-04/RD-05 fallback regex** — present in both: RD-04 gains `assert not re.search(r'(?i)vizdoom.{0,40}(cannot|can\'t|fails?|won\'t|unable).{0,20}(import|build|install)', first)`; RD-05 gains the same search with `assert first_run < m.start()`.
3. **RD-06 `-1` fix + slash** — present: `run_before_req = any(0 <= text.find(s) < req for s in ('./smoke', 'uv venv', 'python -m doom_foxglove'))`; embed needle is now `http://localhost:5173` in both RD-06 and RD-07.
4. **RD-08 section count** — present: per-`##`-section loop asserting `n < 6` topic bullets after the existing streak check.
5. **RD-17 baseline delta** — present: reads `.agent/workstreams/readme/rd17-baseline.txt`, subtracts baseline and the workstream's own prefix, uses `git diff HEAD` (staged-changes bypass closed), keeps the `web/README.md` ≤4-line and `README`-mention legs. Item text assigns baseline creation before generation; planner has already written the baseline file (23 paths, verified on disk).
6. **Rubric** — present: new axes (first-screen usefulness 0.35 / prose concreteness 0.35 / section economy 0.15 / calibration 0.15), threshold 0.75 kept, plus "The evaluator quotes the first 10 lines of the README in eval.md when scoring; an unscored or unquoted rubric is a fail."

### Must-fail fixtures re-run against today's README (amended checks, verbatim)

| Item | Result | Evidence |
| --- | --- | --- |
| RD-01 | FAIL (correct) | `AssertionError: ## Requirements` |
| RD-02 | FAIL (correct) | `AssertionError: (3, ['A ViZDoom process is the fake robot.', 'The Foxglove SDK WebSocket is the live connection.', 'The framebuffer is \`/doom/camera\`.'])` — note the tightened hits list is now exactly the three architecture copulas; the `The smoke command … if none is found.` false positive is gone |
| RD-05 | FAIL (correct) | `AssertionError: ('brew cmake', 1490, 742)` |
| RD-08 | FAIL (correct) | `AssertionError: 9` |
| RD-16 | FAIL (correct) | body starts with `Skipped (… extras cut)` |

Also re-run: RD-04 still fails today (intended), RD-06 still fails today (intended), RD-07 passes today (acceptable — not a must-fail item).

### Fix verification (synthetic inputs)

- Amended RD-02 regex on the good-prose sample from the original attack: worst=1 → PASS. False FAIL closed.
- Amended RD-06 clause on the Requirements-first synthetic README: `AssertionError: Requirements before a run command`. False PASS closed.
- Amended RD-08 on the blank-line-evasion catalog: `AssertionError: ('topic catalog in one section', 9)`. Evasion closed.
- Amended RD-17 with a baseline snapshot of today's 24 dirty paths: zero new paths beyond baseline → PASS. A README-only generator is no longer failed by pre-existing tree dirt; any new disallowed path still fails (`extra = new - allowed`).

### Residual notes (not gate-blocking)

- RD-07 passing today's README is acceptable: it guards the embed/WS needles, not voice; the voice items carry the must-fail weight.
- The baseline file is a point-in-time snapshot; if the tree gains new unrelated dirt between gate and evaluation, the evaluator should re-snapshot before generation per the item text. This is operational, not a check defect.

Gate PASSED. Generator may start on `README.md` (plus optional `web/README.md` pointer). No RD box ticked by this critic.

---

# Critic gate — RD-19 / RD-20 (2026-09-18, second round)

**Verdict: FAIL — four amendments required (7–10 below).** The placement logic of RD-19 is sound and both checks correctly FAIL today's README, but RD-20 as written passes two sloppy-diagram attacks and false-fails two good-diagram styles. Do not generate against these items until the planner applies 7–10.

## Must-fail fixture: today's README (checks run verbatim)

| Item | Result | Evidence |
| --- | --- | --- |
| RD-19 | FAIL (correct) | `AssertionError: no mermaid fence` |
| RD-20 | FAIL (correct) | `AssertionError: no mermaid fence` |

Today's README has no mermaid fence; both checks die on the first assert. Must-fail property holds.

## Attack results (synthetic preface fixtures, checks run verbatim)

| Fixture | RD-19 | RD-20 | Correct? |
| --- | --- | --- | --- |
| A. Good subgraph-style diagram (ViZDoom/Freedoom → doom_foxglove → Foxglove subgraph with Image/Teleop/embed/Gauge, MCAP edge) | PASS | PASS | yes |
| B. Sloppy: all needles stuffed in one `%%` comment, single `A --> B` edge, empty `subgraph Foxglove` | PASS | **PASS** | **false PASS** — renders an empty diagram |
| C. Sloppy: all needles crammed into one node label, one edge | PASS | **PASS** | **false PASS** — keyword salad, not architecture |
| D. Good diagram but node labeled `Embed` (capital E), `log` lowercase | PASS | **FAIL: embed** | **false FAIL** — `'embed' in body` is case-sensitive while the class path lowercases |
| E. Good classDef-style diagram (`classDef fox`, `class I,T,E,G fox`) | PASS | **FAIL: need subgraph…** | **false FAIL** — the class path requires node *IDs* literally named sdk/embed/panel; natural mermaid uses short IDs with labels |
| F. Good diagram, fence written ` ``` mermaid ` (space before info string — valid CommonMark, renders on GitHub) | **FAIL: no mermaid fence** | **FAIL** | **false FAIL** — regex requires ` ```mermaid ` with no space |

PNG-only "diagram" (no mermaid fence) already FAILs both checks — that sloppy path is closed.

No conflicts with RD-01…RD-18: RD-02 strips fenced code before counting copulas, RD-01's preface needles coexist with the fence, RD-18 only grades `![...](...)` refs, RD-08/RD-09 unaffected by a mermaid body.

## Amendment 7 — RD-19: tolerate ` ``` mermaid ` and strip `%%` comments before body asserts

Replace the RD-19 **Check** fenced block with:

```sh
$PY -c "
from pathlib import Path
import re
text = Path('README.md').read_text(encoding='utf-8')
fence = chr(96) * 3
m = re.search(r'(?m)^' + re.escape(fence) + r'[ \t]*mermaid[ \t]*\n', text)
assert m, 'no mermaid fence'
fence_start = m.start()
why = ('Foxglove', 'robot', 'marine', 'Image', 'canvas')
for needle in why:
    i = text.find(needle)
    assert i >= 0, needle
    assert i < fence_start, (needle, 'must appear before mermaid', i, fence_start)
assert re.search(r'teleoperat', text[:fence_start], re.I), 'missing teleoperat* before mermaid'
run = text.find('## Run')
assert run >= 0, 'no ## Run'
assert fence_start < run, (fence_start, run)
first_h2 = re.search(r'(?m)^## ', text)
assert first_h2, 'no ## heading'
close_rel = text[m.end():].find(fence)
assert close_rel >= 0, 'unclosed mermaid fence'
fence_end = m.end() + close_rel
assert fence_end < first_h2.start(), ('mermaid not closed before first ##', fence_end, first_h2.start())
body = text[m.end():fence_end]
body = re.sub(r'(?m)%%[^\n]*', '', body)
assert body.strip(), 'empty mermaid'
assert ('flowchart' in body) or ('graph ' in body), 'need flowchart or graph '
assert '-->' in body, 'no flowchart edges'
print('RD-19 mermaid-in-preface')
"
```

Item text: append "Mermaid `%%` comments are stripped before the body assertions; the fence opener may have spaces around the `mermaid` info string."

## Amendment 8 — RD-20: strip `%%` comments and match needles case-insensitively

In the RD-20 **Check**, replace the body-extraction and needle block:

```python
body = text[m.end(): m.end() + close_rel]
assert 'ViZDoom' in body, 'ViZDoom'
assert ('foxglove-sdk' in body) or ('WebSocket' in body), 'foxglove-sdk or WebSocket'
assert 'Image' in body, 'Image'
assert 'Teleop' in body, 'Teleop'
assert 'embed' in body, 'embed'
assert 'MCAP' in body, 'MCAP'
assert ('3D' in body) or ('Three' in body), '3D or Three'
assert 'doom_foxglove' in body, 'doom_foxglove'
assert 'WASD' in body, 'WASD'
assert ('Freedoom' in body) or ('IWAD' in body), 'Freedoom or IWAD'
assert ('Gauge' in body) or ('Log' in body), 'Gauge or Log'
assert 'Replay' in body, 'Replay'
```

with:

```python
body = text[m.end(): m.end() + close_rel]
body = re.sub(r'(?m)%%[^\n]*', '', body)
low = body.lower()
for n in ('vizdoom', 'doom_foxglove', 'wasd', 'image', 'teleop', 'embed', 'mcap', 'replay'):
    assert n in low, n
assert ('foxglove-sdk' in low) or ('websocket' in low), 'foxglove-sdk or WebSocket'
assert ('3d' in low) or ('three' in low), '3D or Three'
assert ('freedoom' in low) or ('iwad' in low), 'Freedoom or IWAD'
assert ('gauge' in low) or ('log' in low), 'Gauge or Log'
```

Also update the RD-20 fence-opener regex to match Amendment 7 (`re.escape(fence) + r'[ \t]*mermaid[ \t]*\n'`), and change the final two asserts to use `low`:

```python
assert '<canvas' not in low, '<canvas in mermaid'
assert 'getcontext' not in low, 'getContext in mermaid'
```

## Amendment 9 — RD-20: structural floors against keyword-salad stuffing

In the RD-20 **Check**, immediately after the needle asserts (Amendment 8), insert:

```python
groups = (
    ('vizdoom',), ('foxglove-sdk', 'websocket'), ('image',), ('teleop',),
    ('embed',), ('mcap',), ('3d', 'three'), ('doom_foxglove',), ('wasd',),
    ('freedoom', 'iwad'), ('gauge', 'log'), ('replay',),
)
needle_lines = set()
lines = low.splitlines()
for group in groups:
    for i, line in enumerate(lines):
        if any(g in line for g in group):
            needle_lines.add(i)
            break
assert len(needle_lines) >= 4, ('needles crammed into too few lines', len(needle_lines))
edges = low.count('-->')
assert edges >= 3, ('need at least 3 flowchart edges', edges)
```

Item text: append "Needles must be spread over at least four distinct lines of the fence body, and the body must contain at least three `-->` edges — one keyword-salad node does not count." Verified: the natural good diagram scores 8 needle-lines / 4 edges; a compact honest four-node diagram scores 4 / 4; the giant-node attack scores 1 / 1 and now FAILs.

## Amendment 10 — RD-20: fix the classDef grouping alternative

The item text offers "a `classDef` plus a `class ` line that includes sdk/embed/panel nodes", but the check reads node *IDs* literally, so idiomatic mermaid (`class I,T,E,G fox`) false-fails. Replace the item-text alternative with: "a `classDef` whose class name contains `fox` (case-insensitive) plus a `class ` line assigning at least three nodes to that class." In the **Check**, replace:

```python
has_sub = bool(re.search(r'(?im)^\s*subgraph\b[^\n]*Foxglove', body))
classdef = bool(re.search(r'(?m)^\s*classDef\b', body))
class_lines = [
    l for l in body.splitlines()
    if re.match(r'\s*class\s+', l) and not re.match(r'\s*classDef\b', l)
]
class_blob = '\n'.join(class_lines).lower()
has_class = (
    classdef
    and class_lines
    and (('sdk' in class_blob) or ('websocket' in class_blob))
    and ('embed' in class_blob)
    and (
        ('panel' in class_blob)
        or ('image' in class_blob)
        or ('teleop' in class_blob)
        or ('gauge' in class_blob)
    )
)
assert has_sub or has_class, 'need subgraph titled Foxglove or classDef+class on sdk/embed/panel'
```

with:

```python
has_sub = bool(re.search(r'(?im)^\s*subgraph\b[^\n]*foxglove', body))
has_class = False
m_cd = re.search(r'(?im)^\s*classDef\s+(\w*fox\w*)\b', body)
if m_cd:
    cname = m_cd.group(1)
    for l in body.splitlines():
        m_c = re.match(r'\s*class\s+(\S+)\s+' + re.escape(cname) + r'\s*;?\s*$', l)
        if m_c:
            nodes = [x for x in re.split(r'[, ]+', m_c.group(1)) if x]
            if len(nodes) >= 3:
                has_class = True
assert has_sub or has_class, 'need subgraph titled Foxglove or classDef fox* classing 3+ nodes'
```

## Post-amendment verification (amended checks run against all fixtures)

| Fixture | RD-19 | RD-20 |
| --- | --- | --- |
| A. Good subgraph-style | PASS | PASS |
| B. Comment-stuffed | PASS | **FAIL: vizdoom** (comments stripped, nothing renders) |
| C. Giant-node keyword salad | PASS | **FAIL: needles crammed into too few lines (1)** |
| D. Caps `Embed` / lowercase `log` | PASS | PASS (false FAIL closed) |
| E. classDef-style `class I,T,E,G fox` | PASS | PASS (false FAIL closed) |
| F. Spaced fence ` ``` mermaid ` | PASS | PASS (false FAIL closed) |
| G. Compact honest diagram (4 nodes, subgraph Foxglove) | PASS | PASS |
| H. Today's README | **FAIL: no mermaid fence** | **FAIL: no mermaid fence** (must-fail holds) |

## Residual notes (not gate-blocking)

- RD-19 hard-requires the literal heading `## Run`. That matches the item text and today's README; if a future planner renames the happy-path heading, both must change together.
- `text.find('## Run')` is a substring match, not a heading-anchored regex; a `## Run` mention inside an earlier code fence would move the boundary earlier. No such text exists today and the preface carries no code fences; noted, not amended.
- Structural floors (≥4 needle-lines, ≥3 edges) grade shape, not truth. A determined stuffer can still add dummy edges; the quality rubric and evaluator judgment remain the backstop, as with RD-01…RD-18.

No RD box ticked by this critic. `contract.md` not edited — planner applies amendments 7–10, then re-gate.

---

# Critic re-gate — RD-19 / RD-20 (2026-09-18)

**Verdict: GATE PASS.** All four amendments are present in `contract.md`, still mechanical (pure file-text checks, no app), and the must-fail fixture holds.

## Amendment verification (quoted from contract.md)

7. **RD-19 fence regex + comment strip** — present: opener is now `re.escape(fence) + r'[ \t]*mermaid[ \t]*\n'`; `body = re.sub(r'(?m)%%[^\n]*', '', body)` runs before the empty/flowchart/edge asserts; item text carries the new sentence about `%%` stripping and spaced info string.
8. **RD-20 comment strip + case-insensitive needles** — present: same `%%` strip, `low = body.lower()`, lowercase needle loop (`'vizdoom'`, `'doom_foxglove'`, `'wasd'`, `'image'`, `'teleop'`, `'embed'`, `'mcap'`, `'replay'`) plus lowercased alternates; fence regex matches Amendment 7; final asserts use `low` (`'<canvas' not in low`, `'getcontext' not in low`).
9. **RD-20 structural floors** — present: twelve needle groups mapped to first-matching line indices, `assert len(needle_lines) >= 4`, and `edges = low.count('-->')` with `assert edges >= 3`; item text carries the "at least four distinct lines … at least three `-->` edges" sentence.
10. **RD-20 classDef alternative** — present: `classDef\s+(\w*fox\w*)` capture, then a `class ` line match assigning ≥3 nodes to that class; item text now reads "a `classDef` whose class name contains `fox` (case-insensitive) plus a `class ` line assigning at least three nodes to that class."

## Must-fail fixture re-run (amended checks, verbatim, today's README)

| Item | Result | Evidence |
| --- | --- | --- |
| RD-19 | FAIL (correct) | `AssertionError: no mermaid fence` |
| RD-20 | FAIL (correct) | `AssertionError: no mermaid fence` |

## Attack fixtures re-run against the contract's verbatim amended code

| Fixture | RD-19 | RD-20 | Correct? |
| --- | --- | --- | --- |
| A. Good subgraph-style | PASS | PASS | yes |
| B. Comment-stuffed | PASS | FAIL: vizdoom | yes — sloppy diagram caught |
| C. Giant-node keyword salad | PASS | FAIL: needles crammed into too few lines (1) | yes — sloppy diagram caught |
| D. Caps `Embed` / lowercase `log` | PASS | PASS | yes — false FAIL stays closed |
| E. classDef-style `class I,T,E,G fox` | PASS | PASS | yes — false FAIL stays closed |
| F. Spaced fence ` ``` mermaid ` | PASS | PASS | yes — false FAIL stays closed |

No transcription drift between the amendment text and the applied contract. Checks remain mechanical: string/regex assertions over `README.md` text only.

Gate PASSED. Generator may insert the mermaid diagram into `README.md` only. No RD box ticked by this critic.
