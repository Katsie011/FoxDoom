# Contract — README rewrite

**Workstream:** `readme` (not a numbered product phase; do not create `06-*`)
**Item-id prefix:** `RD-`
**Deliverable:** repository `README.md`
**Status:** amended. Critic amendments 7–10 applied to RD-19/RD-20; awaiting critic re-gate. This planner does not grade. RD-01…RD-18 stay as the evaluator left them.

Source of truth for the why: `.agent/GOAL.md` north star and `.agent/workstreams/readme/PLAN.md`. This contract does not rewrite GOAL.md.

## How this contract is graded

The evaluator (kimi-k3-high) is told the README is broken and must prove it. For every `RD-nn` item it must run the stated **Check** from a clean shell at `$ROOT`, or quote the exact file text the check names. "Reads well" is a fail. An unrun check is a fail.

- Repo root is `$ROOT` (`/Users/michael/Documents/foxglove/work/doom`). Every command below is run after `cd "$ROOT"`.
- `$PY` is `$ROOT/.venv/bin/python` when that file is executable, otherwise `python3`.
- An item is **PASS** only if its check succeeds. Checkboxes below start unchecked. **Only the evaluator ticks `- [ ]`.** The generator must not tick boxes and must not edit this file.
- Opening the Foxglove app is **not** required. These items grade file text.
- Absence of a screenshot, GIF, or `![...](...)` image is **not** a FAIL of any item (RD-18).
- Frozen items RD-10…RD-16 copy HL-13 / RR-05 / RR-06 / SX-05 / SX-06 README checks. Do not weaken them. If this file and an older workstream contract disagree on a README needle, the older check still has to pass — treat both as required.

---

## A. Why and voice

### RD-01 — Title, then why, before Requirements or brew

- [x] After the `# ` title, prose stating the robot/Foxglove why appears before the first `##` heading. That first `##` is not Requirements or troubleshooting. The why names Foxglove, a robot, the marine, an Image panel, and a canvas.

**Check:**

```sh
$PY -c "
from pathlib import Path
import re
text = Path('README.md').read_text(encoding='utf-8')
lines = text.splitlines()
assert lines, 'empty README'
assert lines[0].startswith('# '), lines[0]
first_h2 = next((i for i, l in enumerate(lines) if l.startswith('## ')), None)
assert first_h2 is not None, 'no ## heading'
pre = '\n'.join(lines[1:first_h2])
assert pre.strip(), 'no why prose between title and first ##'
for needle in ('Foxglove', 'robot', 'marine', 'Image', 'canvas'):
    assert needle in pre, needle
assert re.search(r'teleoperat', pre, re.I), 'missing teleoperat*'
h2 = lines[first_h2]
assert not re.match(r'## (Requirements|Troubleshooting|Fallback|Build notes)\b', h2, re.I), h2
assert 'brew install cmake' not in pre
assert 'If ViZDoom cannot import' not in pre
print('RD-01 why-first')
"
```

### RD-02 — No three-in-a-row "X is the Y" dump in the first 25 lines

- [x] The first 25 lines do not contain three consecutive architecture-copula sentences. A copula sentence matches `^(The|A|An) … is …` (article subject, verb `is`). The current README opening is the FAIL fixture.

**Check:**

```sh
$PY -c "
from pathlib import Path
import re
lines = Path('README.md').read_text(encoding='utf-8').splitlines()[:25]
blob = '\n'.join(lines)
# strip fenced code so install snippets do not count
blob = re.sub(r'\`\`\`[\s\S]*?\`\`\`', ' ', blob)
parts = re.split(r'(?<=[.!?])\s+', blob)
sents = [re.sub(r'\s+', ' ', p).strip() for p in parts if p.strip()]
copula = re.compile(r'^(The|A|An)\s+\S+(?:\s+\S+){0,4}\s+is\b\s+', re.I)
run = 0
worst = 0
hits = []
for s in sents:
    if copula.match(s):
        run += 1
        hits.append(s)
        worst = max(worst, run)
    else:
        run = 0
assert worst < 3, (worst, hits)
print('RD-02 no-copula-stack', len(sents))
"
```

### RD-03 — Banned slop in the first 40 lines

- [x] The first 40 lines contain none of: `seamlessly`, `robust`, `comprehensive`, `leverage`, `cutting-edge`, `Welcome to`, `This project aims`, `designed to`.

**Check:**

```sh
$PY -c "
from pathlib import Path
first = '\n'.join(Path('README.md').read_text(encoding='utf-8').splitlines()[:40])
banned = (
    'seamlessly', 'robust', 'comprehensive', 'leverage', 'cutting-edge',
    'welcome to', 'this project aims', 'designed to',
)
low = first.lower()
hits = [w for w in banned if w in low]
assert not hits, hits
print('RD-03 no-slop')
"
```

### RD-04 — No install hedging in the first 40 lines

- [x] The first 40 lines do not mention ephemeral ports or `If ViZDoom cannot import`. Those notes may exist later (RD-05 / RD-06).

**Check:**

```sh
$PY -c "
from pathlib import Path
import re
first = '\n'.join(Path('README.md').read_text(encoding='utf-8').splitlines()[:40])
assert 'ephemeral' not in first.lower(), 'ephemeral in first 40 lines'
assert 'If ViZDoom cannot import' not in first, 'fallback hedge in first 40 lines'
assert not re.search(r'(?i)vizdoom.{0,40}(cannot|can\'t|fails?|won\'t|unable).{0,20}(import|build|install)', first), 'fallback hedge in first 40 lines'
print('RD-04 no-first-screen-hedge')
"
```

---

## B. Happy path, then details

### RD-05 — Working install/run before brew cmake and ViZDoom fallback

- [x] A working install or run command (`./smoke`, `uv venv`, or `python -m doom_foxglove`) appears in the file before `brew install cmake` and before `If ViZDoom cannot import`, when those strings exist.

**Check:**

```sh
$PY -c "
from pathlib import Path
import re
text = Path('README.md').read_text(encoding='utf-8')
starts = [text.find(s) for s in ('./smoke', 'uv venv', 'python -m doom_foxglove')]
starts = [i for i in starts if i >= 0]
assert starts, 'no install/run command'
first_run = min(starts)
for late, label in (
    ('brew install cmake', 'brew cmake'),
    ('If ViZDoom cannot import', 'vizdoom fallback'),
):
    i = text.find(late)
    if i >= 0:
        assert first_run < i, (label, first_run, i)
m = re.search(r'(?i)vizdoom.{0,40}(cannot|can\'t|fails?|won\'t|unable).{0,20}(import|build|install)', text)
if m:
    assert first_run < m.start()
print('RD-05 happy-path-before-troubleshoot')
"
```

### RD-06 — Section order: run and open, then frozen headings, then build notes

- [x] `./smoke` and `http://localhost:5173` appear before `## Replay an MCAP`. Frozen headings appear in order: Replay, then Ask Foxglove, then Not in this slice. If `brew install cmake` or `If ViZDoom cannot import` exists, it is after `## Not in this slice`. If `## Requirements` exists, a run command already appeared before that heading.

**Check:**

```sh
$PY -c "
from pathlib import Path
text = Path('README.md').read_text(encoding='utf-8')

def pos(s):
    i = text.find(s)
    assert i >= 0, s
    return i

smoke = pos('./smoke')
embed = pos('http://localhost:5173')
replay = pos('## Replay an MCAP')
ask = pos('## Ask Foxglove (copy-paste)')
skip = pos('## Not in this slice')
assert smoke < replay, (smoke, replay)
assert embed < replay, (embed, replay)
assert replay < ask < skip, (replay, ask, skip)
req = text.find('\n## Requirements')
if req < 0:
    req = 0 if text.startswith('## Requirements') else -1
if req >= 0:
    run_before_req = any(
        0 <= text.find(s) < req
        for s in ('./smoke', 'uv venv', 'python -m doom_foxglove')
    )
    assert run_before_req, 'Requirements before a run command'
for late in ('brew install cmake', 'If ViZDoom cannot import'):
    i = text.find(late)
    if i >= 0:
        assert i > skip, (late, i, skip)
print('RD-06 section-order')
"
```

### RD-07 — Embed URL in the happy path; app WebSocket still documented

- [x] The happy path (before `## Replay an MCAP`) includes `http://localhost:5173`. The file also documents `ws://localhost:8765` for the Foxglove app.

**Check:**

```sh
$PY -c "
from pathlib import Path
text = Path('README.md').read_text(encoding='utf-8')
replay = text.find('## Replay an MCAP')
assert replay >= 0
assert 'http://localhost:5173' in text[:replay], 'embed URL missing from happy path'
assert 'ws://localhost:8765' in text, 'app websocket missing'
print('RD-07 embed-and-ws')
"
```

### RD-08 — Live/run section is not a topic-schema catalog

- [x] The README does not use six or more consecutive markdown bullets that start with a slash topic (`- \`/…`). That is the current live-server dump. Topics may be named in prose.

**Check:**

```sh
$PY -c "
from pathlib import Path
import re
lines = Path('README.md').read_text(encoding='utf-8').splitlines()
topic_bullet = re.compile(r'^- \`/')
run = 0
worst = 0
for line in lines:
    if topic_bullet.match(line):
        run += 1
        worst = max(worst, run)
    else:
        run = 0
assert worst < 6, worst
import re as _re
sections = _re.split(r'(?m)^## ', '\n'.join(lines))
for sec in sections:
    n = sum(1 for l in sec.splitlines() if topic_bullet.match(l))
    assert n < 6, ('topic catalog in one section', n)
print('RD-08 no-topic-catalog', worst)
"
```

### RD-09 — Root README does not duplicate `web/README.md`

- [x] Root `README.md` may point at `web/README.md`. It must not vendor embed implementation tokens from that file.

**Check:**

```sh
$PY -c "
from pathlib import Path
text = Path('README.md').read_text(encoding='utf-8')
impl = (
    'ParentTransportFactory',
    'foxglove-common-shim',
    'compile-check.ts',
    'VITE_FOXGLOVE_WS',
)
hits = [s for s in impl if s in text]
assert len(hits) < 2, hits
print('RD-09 no-web-readme-dup', hits)
"
```

---

## C. Frozen README checks (do not weaken)

These are the README-facing needles from HL-13, RR-05, RR-06, SX-05, and SX-06. A Kimi eval that still runs those older items against `README.md` must still PASS. Product-file `rg` halves of RR-06 / SX-05 stay owned by those workstreams; the generator must not touch those files (RD-17).

### RD-10 — HL-13 strings: install, smoke, live WS, Image plus Teleop

- [x] `README.md` contains each HL-13 string: `./smoke`, `python -m doom_foxglove`, `ws://localhost:8765`, `ClientPublish`, `/doom/camera`, `/cmd_vel`, `/doom/buttons`, `Freedoom`, `Teleop`, `Image`.

**Check:**

```sh
$PY -c "
from pathlib import Path
text = Path('README.md').read_text(encoding='utf-8')
need = (
    './smoke',
    'python -m doom_foxglove',
    'ws://localhost:8765',
    'ClientPublish',
    '/doom/camera',
    '/cmd_vel',
    '/doom/buttons',
    'Freedoom',
    'Teleop',
    'Image',
)
missing = [s for s in need if s not in text]
assert not missing, missing
print('RD-10 hl13-strings')
"
```

### RD-11 — HL-13 canvas forbid

- [x] `README.md` states the picture is not a host canvas. Same regex as HL-13.

**Check:**

```sh
rg -in 'does not draw.*canvas|no host canvas|not a [a-z ]*canvas|never [a-z ]*canvas' README.md
```

PASS only if that `rg` prints at least one line. Quote the matching sentence.

### RD-12 — HL-13 commercial WAD line

- [x] `README.md` forbids copying a commercial WAD. Same needles as HL-13, plus the current commercial line (do not drop it).

**Check:**

```sh
rg -in 'do not copy|commercial' README.md
```

PASS only if that `rg` prints at least one line.

```sh
$PY -c "
from pathlib import Path
text = Path('README.md').read_text(encoding='utf-8')
assert 'Do not copy a commercial' in text
assert 'doom.wad' in text and 'doom2.wad' in text
print('RD-12 commercial-wad')
"
```

Quote the line that forbids a commercial `doom.wad` / `doom2.wad`.

### RD-13 — RR-05 Replay heading, smoke-replay, local open, playback bar

- [x] Repository `README.md` tells a human how to prove replay without a cloud account: run `./smoke-replay`, open `recordings/smoke.mcap` as a local file, import `layouts/Replay.json`, and use the playback bar. Heading is exactly `## Replay an MCAP`. Copied from RR-05; do not weaken.

**Check:**

```sh
$PY -c "
from pathlib import Path
text = Path('README.md').read_text(encoding='utf-8')
need = (
    './smoke-replay',
    'layouts/Replay.json',
    'recordings/smoke.mcap',
    'playback bar',
)
missing = [s for s in need if s not in text]
assert not missing, missing
assert 'Open local file' in text or 'open local file' in text.lower() or 'drag' in text.lower(), 'no local-open instruction'
assert '## Replay an MCAP' in text
print('RR-05 readme-ok')
print('RD-13 rr05')
"
```

Quote the `## Replay an MCAP` heading. A one-line pointer in `web/README.md` does not satisfy this item.

### RD-14 — RR-06 README says cloud

- [x] `README.md` contains `cloud` (case-insensitive) so RR-06 still passes. Copied from the README half of RR-06; do not weaken.

**Check:**

```sh
$PY -c "
from pathlib import Path
text = Path('README.md').read_text(encoding='utf-8')
assert 'cloud' in text.lower(), 'README must say cloud is not required / not in v1'
print('RR-06 local-only')
print('RD-14 rr06-cloud')
"
```

`https://app.foxglove.dev` as a local-file viewer is allowed. FAIL if README makes a cloud recording URL the only way to open the file (no local-open instruction — graded by RD-13).

### RD-15 — SX-05 heading, fence sentence, three exact prompt bodies

- [x] Repository `README.md` ships three copy-paste prompts for the built-in Foxglove agent / MCP box. No custom agent ships in this repo. FAIL if any of the three fenced prompt bodies is missing or paraphrased. Copied from SX-05; do not weaken.

**Check:**

```sh
$PY -c "
from pathlib import Path
text = Path('README.md').read_text(encoding='utf-8')
assert '## Ask Foxglove (copy-paste)' in text
assert 'No custom agent ships in this repo.' in text
prompts = (
    'Using /doom/player.health, /doom/events (kind=pickup or death), and /doom/log, when did health drop, and what happened in the two seconds before each drop? Give timestamps I can scrub to.',
    'Find /doom/events where kind=death (and the matching /doom/log line). Using /doom/player, /doom/entities, and health/ammo around that timestamp, why did I die? Point me at the scrub time.',
    'Build a Foxglove layout that plots /doom/player.weapon and /doom/player.ammo vs time, shows /doom/events filtered to kind=weapon, keeps the Image panel on /doom/camera, and leaves Teleop hidden for replay.',
)
missing = [p for p in prompts if p not in text]
assert not missing, missing
print('SX-05 prompts-ok', len(prompts))
print('RD-15 sx05')
"
```

Quote the heading `## Ask Foxglove (copy-paste)` and the sentence `No custom agent ships in this repo.`

### RD-16 — SX-06 Not-in-this-slice heading and four needles

- [x] `README.md` has heading `## Not in this slice` and the four SX-06 needles. The paragraph under that heading is not the current agent-speak opener. Copied from SX-06 README half; needles are not weakened.

**Check:**

```sh
$PY -c "
from pathlib import Path
text = Path('README.md').read_text(encoding='utf-8')
assert '## Not in this slice' in text
for needle in (
    'remote-access gateway',
    'comparison mode UI',
    'cloud share links',
    'ViZDoom policy vs human',
):
    assert needle in text, needle
start = text.find('## Not in this slice')
rest = text[start + len('## Not in this slice'):]
nxt = rest.find('\n## ')
body = rest if nxt < 0 else rest[:nxt]
body = body.strip()
assert body, 'empty Not in this slice body'
assert not body.startswith('Skipped'), body.splitlines()[0]
assert 'extras cut' not in body
print('SX-06 readme-skip-ok')
print('RD-16 sx06')
"
```

---

## D. Scope fence

### RD-17 — Generator may edit `README.md` only

- [x] After generation, changed paths are `README.md` and optionally `web/README.md`. No Python, no layouts, no `web/src`, no GOAL/COORDINATION, no `01`–`05` contracts, no knowledge-graph files. If `web/README.md` changed, it is a pointer fix (small diff) that still mentions the repository README. Before generation starts, the evaluator (or planner at gate time) writes `.agent/workstreams/readme/rd17-baseline.txt` containing the current `git status --porcelain` path list, one path per line. The check FAILs only on dirty paths that are new relative to that baseline.

**Check:**

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

### RD-18 — No `06-*` workstream; no invented screenshot file

- [x] `.agent/workstreams/06-*` does not exist. A missing GIF/PNG is PASS. FAIL only if README references a relative image path that is not a file.

**Check:**

```sh
$PY -c "
from pathlib import Path
import re
root = Path('.')
hits = list(root.glob('.agent/workstreams/06-*'))
assert not hits, hits
text = Path('README.md').read_text(encoding='utf-8')
missing = []
for src in re.findall(r'!\[[^\]]*\]\(([^)]+)\)', text):
    if src.startswith('http://') or src.startswith('https://') or src.startswith('data:'):
        continue
    if not Path(src.split()[0]).exists():
        missing.append(src)
assert not missing, missing
print('RD-18 no-06-no-fake-image')
"
```

Do **not** FAIL this item because `README.md` has no image.

---

## E. Architecture diagram (preface mermaid)

Placement is constrained by RD-01: the mermaid fence lives in the title→first-`##` preface, after the why paragraph, before `## Run`. Do not make `## Build notes` or `## Architecture` the first heading. Do not invent a PNG (RD-18). The diagram must not push `brew install cmake` or `If ViZDoom cannot import` above `## Not in this slice` (RD-06). Do not add a 6+ topic-bullet catalog (RD-08). Do not vendor more than one of `ParentTransportFactory` / `foxglove-common-shim` / `compile-check.ts` / `VITE_FOXGLOVE_WS` (RD-09). Do not weaken RD-10…RD-16. Opening Foxglove is not required to grade these items.

### RD-19 — Mermaid flowchart in the preface, before `## Run`

- [x] `README.md` contains a non-empty mermaid fence whose start is after the RD-01 why needles and before `## Run`. The fence sits in the title→first-`##` preface (it must close before the first `##`). The fence body contains `flowchart` or `graph `, and at least one `-->` edge. Mermaid `%%` comments are stripped before the body assertions; the fence opener may have spaces around the `mermaid` info string.

**Check:**

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

### RD-20 — Foxglove grouping and required node labels

- [x] The mermaid fence from RD-19 names the high-level components and groups Foxglove visually. Inside that fence: `ViZDoom`, `foxglove-sdk` or `WebSocket`, `Image`, `Teleop`, `embed`, `MCAP`, and `3D` or `Three`; also `doom_foxglove`, `WASD`, `Freedoom` or `IWAD`, `Gauge` or `Log`, and `Replay`. A `subgraph` line whose title contains `Foxglove`, or a `classDef` whose class name contains `fox` (case-insensitive) plus a `class ` line assigning at least three nodes to that class. The fence does not contain `<canvas` or `getContext`. Needles must be spread over at least four distinct lines of the fence body, and the body must contain at least three `-->` edges — one keyword-salad node does not count.

**Check:**

```sh
$PY -c "
from pathlib import Path
import re
text = Path('README.md').read_text(encoding='utf-8')
fence = chr(96) * 3
m = re.search(r'(?m)^' + re.escape(fence) + r'[ \t]*mermaid[ \t]*\n', text)
assert m, 'no mermaid fence'
close_rel = text[m.end():].find(fence)
assert close_rel >= 0, 'unclosed mermaid fence'
body = text[m.end(): m.end() + close_rel]
body = re.sub(r'(?m)%%[^\n]*', '', body)
low = body.lower()
for n in ('vizdoom', 'doom_foxglove', 'wasd', 'image', 'teleop', 'embed', 'mcap', 'replay'):
    assert n in low, n
assert ('foxglove-sdk' in low) or ('websocket' in low), 'foxglove-sdk or WebSocket'
assert ('3d' in low) or ('three' in low), '3D or Three'
assert ('freedoom' in low) or ('iwad' in low), 'Freedoom or IWAD'
assert ('gauge' in low) or ('log' in low), 'Gauge or Log'
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
assert '<canvas' not in low, '<canvas in mermaid'
assert 'getcontext' not in low, 'getContext in mermaid'
print('RD-20 foxglove-group-labels')
"
```

---

## Quality rubric (not a checkbox)

The evaluator scores 0–1 and writes a paragraph naming the gap. This is taste with a written scale, not a vibe and not an `RD-` tick.

| Axis | Weight | 0 | 1 |
| --- | --- | --- | --- |
| first-screen usefulness | 0.35 | A stranger cannot tell what running this gets them | A stranger knows in one screen: Foxglove drives a DOOM marine, and the exact command to see it |
| prose concreteness | 0.35 | Manifesto cadence, abstraction, or slop the banned-word list misses | Short concrete sentences; every claim names a thing in this repo |
| section economy | 0.15 | Reader meets a detail wall before a payoff | Each section earns its place; details deferred past the happy path |
| calibration | 0.15 | Reads nothing like the good reference | Same register as gasmith/foxglove-lunar-lander: product as UI, then run |

**Pass threshold:** 0.75 (weighted sum). Below 0.75 is FAIL even if every `RD-` box is ticked. The evaluator quotes the first 10 lines of the README in eval.md when scoring; an unscored or unquoted rubric is a fail.

**Good reference:** [gasmith/foxglove-lunar-lander](https://github.com/gasmith/foxglove-lunar-lander) README voice — Foxglove app as the UI, then run. No fake screenshot required here.

**Bad reference:** current `README.md` opening (the parallel "X is the Y" paragraph: ViZDoom process / SDK WebSocket / framebuffer is `/doom/camera`).

---

## Out of scope (do not FAIL the README rewrite for these)

- Changing Python, layouts, `web/src`, smokes, or ViZDoom install behavior
- Inventing a screenshot or GIF
- Creating `.agent/workstreams/06-*`
- Editing GOAL.md, COORDINATION.md, `01`–`05` contracts, or knowledge-graph files
- Ticking this contract (evaluator only)
- Opening Foxglove or pasting the SX-05 prompts into MCP

A generator handed this contract rewrites `README.md` (plus an optional `web/README.md` pointer). It does not tick boxes.

## Process (not an RD checkbox)

This file is the critic-gated contract. The critic (kimi-k3-high) attacks these items; this planner does not grade them. No generator ticks the boxes above.
