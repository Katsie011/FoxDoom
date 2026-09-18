# Knowledge graph — schema v1

Shared, durable, machine-readable memory for every agent in this repository. Deliberately **not** a graph database: two line-delimited JSON files that diff cleanly, merge by append, and can be queried with `python3` or `jq` from any shell.

- `nodes.jsonl` — one JSON object per line, one line per node.
- `edges.jsonl` — one JSON object per line, one line per directed edge.
- `validate.py` — the validator this file documents; the only executable under `.agent/knowledge-graph/`.

**Append-only.** Nodes and edges are added, never rewritten in place. A fact that stops being true gets a new node or edge (`SUPERSEDES`) or a status change appended as part of a librarian pass, and the change is explained in the acting workstream's `log.md`.

This graph is thinned relative to the robotArms house style: there is no event-deadline `Event` seed, and `Hardware` is only the development machine. The eight types and six edges stay, so later workstreams can grow the graph without a schema fork.

## Node record

Every node carries exactly these seven fields:

| Field | Meaning |
|---|---|
| `id` | Stable identifier: `snake_case`, or a contract item id matching `[A-Z]{1,3}-\d{2}` (for example `H-01`, `HL-01`). Never renamed — other lines point at it. |
| `type` | One of the eight node types below. |
| `label` | Short human name, one line, readable in a query result. |
| `body` | One-sentence assertion, written so the node is actionable **without** opening `GOAL.md`. |
| `status` | A value from that type's status vocabulary (see below). |
| `ts` | ISO date (`YYYY-MM-DD`) the node was first asserted. |
| `source` | Where the fact comes from: a plan path, a URL, a repository-relative file path, or a workstream directory. |

Three optional fields are allowed and validated: `url` (Repo), `date` and `date_end` (Event). Any other field is a schema violation.

## The eight node types

| Type | What it holds | Status vocabulary |
|---|---|---|
| `Decision` | A locked product or engineering decision that agents may not reopen. | `locked`, `superseded` |
| `Workstream` | One `.agent/workstreams/<nn>-<name>/` unit of work. `source` is its directory. | `planned`, `in_progress`, `done`, `deferred` |
| `ContractItem` | One numbered, individually checkable item from a workstream contract (`H-01`, `HL-01`). | `specified`, `implemented`, `verified`, `failed` |
| `Repo` | An external repository or example that is vendored, pinned, or read for patterns. `source`/`url` carry the URL. | `pinned`, `vendored`, `referenced`, `deferred` |
| `Hardware` | A physical machine the build depends on or is blocked by. | `present`, `absent`, `not_acquired` |
| `Capability` | An observable thing the system can do — one per definition-of-done line in `GOAL.md`. | `planned`, `in_progress`, `done`, `deferred` |
| `Risk` | A concrete way the build fails, with the consequence and a mitigation in `body`. | `open`, `mitigated`, `closed` |
| `Event` | A dated external commitment. `date` carries the machine-readable date. Unused in the seed: this repo has no event deadline. | `scheduled`, `past` |

`ContractItem` status is evaluator-only ink: a generator leaves items at `specified`. Only an evaluator may append `implemented`, `verified`, or `failed`, because a producer may not grade its own work.

## Edge record

| Field | Meaning |
|---|---|
| `from` | Source node `id`. Must resolve. |
| `type` | One of the six edge types below. |
| `to` | Target node `id`. Must resolve. |
| `ts` | ISO date (`YYYY-MM-DD`) the edge was asserted. |
| `note` | Optional one-line reason the edge exists. |

## The six edge types

Direction is significant. `validate.py` enforces the allowed `from-type → to-type` pairs listed here.

| Edge | Semantic | Allowed direction pairs |
|---|---|---|
| `DECIDES` | The decision governs how the target is built. | `Decision → Workstream`, `Decision → Capability`, `Decision → Event` |
| `DEPENDS_ON` | The source cannot be finished until the target is. | `Workstream → Workstream`, `Workstream → Capability`, `Capability → Capability`, `Capability → Hardware`, `Event → Capability` |
| `EVIDENCED_BY` | The source's claim is supported by external evidence. | `Decision → Repo`, `Decision → Event`, `Risk → Repo`, `Risk → Hardware`, `ContractItem → Repo` |
| `BLOCKS` | The source actively prevents the target from progressing. | `Risk → Workstream`, `Risk → Capability`, `Risk → Hardware`, `Hardware → Capability` |
| `IMPLEMENTS` | The source is the thing that delivers the target. | `Workstream → Capability`, `ContractItem → Workstream` |
| `SUPERSEDES` | The source replaces the target, which is retired. | `Decision → Decision`, `Workstream → Workstream` |

## Validation

Run from the repository root (`/Users/michael/Documents/foxglove/work/doom`):

```sh
python3 .agent/knowledge-graph/validate.py
```

Exit 0 means all of the following hold:

1. Both files are line-delimited JSON — every line parses as one JSON object, there is no wrapping array, there are no blank lines, and each file ends with a newline.
2. Every node carries all seven required fields and no undocumented field.
3. Every node `id` is unique across `nodes.jsonl`.
4. Every node `type` is one of the eight.
5. Every node `status` is legal for its `type`, and every `ts` is an ISO date.
6. Every node `id` is `snake_case` or matches `[A-Z]{1,3}-\d{2}`.
7. Every `Workstream` node's `source` is a directory that exists on disk.
8. Every edge `type` is one of the six, and every edge `from` / `to` resolves to an existing node `id`.
9. Every edge's `from-type → to-type` pair appears in the direction table above.

To validate a mutated copy rather than the live graph, override the paths:

```sh
cp .agent/knowledge-graph/nodes.jsonl /tmp/nodes-broken.jsonl
printf '%s\n' '{"id":"x"' >> /tmp/nodes-broken.jsonl
python3 .agent/knowledge-graph/validate.py --nodes /tmp/nodes-broken.jsonl   # exits 1
```

The same script with `--harness` additionally checks the harness file tree, contract-item coverage, required edges, `progress.md` / `log.md` format, the two loops, and `.cursor/rules/agent-os.mdc`. `.agent/COORDINATION.md` documents that invocation as the one-command harness self-check.

## Resume queries

Four questions a resuming agent actually asks, each answerable with one command from the repository root. Expected answers below are for the seeded graph.

**1. What risks are open right now?**

```sh
python3 -c "import json;print('\n'.join(n['id'] for n in map(json.loads,open('.agent/knowledge-graph/nodes.jsonl')) if n['type']=='Risk' and n['status']=='open'))"
```

Expect two lines: `vizdoom_macos_build`, `commercial_wad`.

**2. Which workstream is next for product code?**

Walks `DEPENDS_ON` out from `ws_00_harness` in reverse: workstreams that depend on the harness and are not themselves deferred.

```sh
python3 -c "import json;N=list(map(json.loads,open('.agent/knowledge-graph/nodes.jsonl')));S={n['id']:n for n in N};E=[json.loads(l) for l in open('.agent/knowledge-graph/edges.jsonl')];print('\n'.join(sorted(e['from'] for e in E if e['type']=='DEPENDS_ON' and e['to']=='ws_00_harness' and S[e['from']]['type']=='Workstream')))"
```

Expect `ws_01_hero_loop`. That is the first product generator. Later phases depend on it, not on the harness directly.

**3. What is locked, and what does each locked decision govern?**

```sh
python3 -c "import json;E=[json.loads(l) for l in open('.agent/knowledge-graph/edges.jsonl')];[print(n['id'],'->',sorted(e['to'] for e in E if e['type']=='DECIDES' and e['from']==n['id']),'::',n['body']) for n in map(json.loads,open('.agent/knowledge-graph/nodes.jsonl')) if n['type']=='Decision' and n['status']=='locked']"
```

Expect one line per locked decision in `GOAL.md`, each with the workstream or capability it decides and its full assertion.

**4. What does a given workstream depend on?**

```sh
WS=ws_02_robotics_layout python3 -c "import json,os;print('\n'.join(e['to'] for e in map(json.loads,open('.agent/knowledge-graph/edges.jsonl')) if e['type']=='DEPENDS_ON' and e['from']==os.environ['WS']))"
```

Expect `ws_01_hero_loop` — robotics layout cannot start until the hero loop is real. Change `WS=` to query any other workstream id.

`jq` is also available if a one-liner is easier to read that way, for example `jq -r 'select(.type=="Risk" and .status=="open") | .id' .agent/knowledge-graph/nodes.jsonl`.
