# Contract — 00-harness (agentic operating system on disk)

**Workstream:** `00-harness`
**Planner:** unspawned this run; the supervisor handed the generator both 00 and 01.
**Generator scope for this workstream:** files under `.agent/` and `.cursor/rules/agent-os.mdc`. Product Python lives in workstream `01-hero-loop`.
**Deliverable:** the durable state layer (`GOAL.md`, `COORDINATION.md`, knowledge graph, workstream tree, loop specs, Cursor rule) that every later agent reads to resume.
**Source of truth for content:** `.agent/GOAL.md`, `.agent/COORDINATION.md`, and `/Users/michael/.cursor/plans/foxglove_doom_stunt_84c1ef0a.plan.md`. Do not rewrite the product plan.

## How this contract is graded

The evaluator is told the harness is broken and must prove it. For every item below it must either run the stated check or quote the exact file text that satisfies it. "Looks fine" is a fail. An item is **PASS** only if its check is mechanically reproducible from a clean shell at the repo root (`/Users/michael/Documents/foxglove/work/doom`).

Repo root is referred to as `$ROOT` below.

---

## A. Scope and file tree

### H-01 — Exact directory tree exists
`.agent/` and `.cursor/rules/` contain at least these paths (extra files under `.agent/` are allowed only if referenced from `COORDINATION.md` or `SCHEMA.md`):

```
.agent/GOAL.md
.agent/COORDINATION.md
.agent/knowledge-graph/SCHEMA.md
.agent/knowledge-graph/nodes.jsonl
.agent/knowledge-graph/edges.jsonl
.agent/knowledge-graph/validate.py
.agent/loops/README.md
.agent/workstreams/00-harness/{contract.md,progress.md,log.md,critique.md}
.agent/workstreams/01-hero-loop/{PLAN.md,contract.md,progress.md,log.md}
.agent/workstreams/02-robotics-layout/{PLAN.md,contract.md,progress.md,log.md}
.agent/workstreams/03-embed-shell/{PLAN.md,contract.md,progress.md,log.md}
.agent/workstreams/04-record-replay/{PLAN.md,contract.md,progress.md,log.md}
.agent/workstreams/05-stunt-extras/{PLAN.md,contract.md,progress.md,log.md}
.cursor/rules/agent-os.mdc
```

**Check:** every listed path exists as a file. `python3 .agent/knowledge-graph/validate.py --harness` reports no `H-01: missing required path`.

### H-02 — Harness-owned files stay under `.agent/` and `.cursor/rules/`
This workstream's durable-state deliverable is the tree in H-01. It does not own `doom_foxglove/`, `README.md`, or dependency files; those belong to `01-hero-loop`. Combining 00 and 01 in one generator spawn is a supervisor choice, not a license for 00 to claim product code.

**Check:** every path in H-01 exists; `validate.py` is the only `*.py` under `.agent/`.

### H-03 — No unfilled content markers and no empty sections
No deliverable file under `.agent/` contains `TODO`, `FIXME`, `lorem`, or `<unfilled>` as a content marker, and no `.md` file (except the filename exclusions below) has an empty section heading followed immediately by another heading.

Filename exclusions, each with a reason:

- `contract.md` — this item enumerates marker words, so quoting them matches itself.
- `critique.md` — the critic quotes contract text.
- `eval.md` — the evaluator quotes contract text.
- `log.md` — append-only history; H-18 forbids editing a past entry.

**Check:** `grep -rniE 'FIXME|lorem|<unfilled>' $ROOT/.agent --include='*.md' --include='*.jsonl' --exclude='contract.md' --exclude='critique.md' --exclude='eval.md' --exclude='log.md'` returns nothing.

### H-04 — GOAL.md north star and locked decisions remain intact
`.agent/GOAL.md` already existed. The generator does not rewrite the north star, the locked-decision ids, or the phase definition of done. All of `dec_vizdoom_engine`, `dec_freedoom_legal`, `dec_foxglove_sdk_ws`, `dec_stock_panels_only`, `dec_teleop_twist`, `dec_embed_viz`, `dec_no_canvas`, `dec_tank_controls`, `dec_cheap_models`, `dec_producer_neq_judge`, `dec_state_on_disk`, `dec_phase_gating` remain as backtick ids.

**Check:** those twelve ids each appear at least once in `.agent/GOAL.md`; a `North star` section exists; `ws://localhost:8765` is present.

### H-05 — COORDINATION.md grok/kimi-only loop remains intact
`.agent/COORDINATION.md` already existed. Allowed model slugs remain exactly `cursor-grok-4.6-high-fast` and `kimi-k3-high`. Banned slugs remain named. Producer ≠ judge remains a hard rule. The harness self-check command is documented.

**Check:** both allowed slugs appear; `inherit` is named as banned; the literal `python3 .agent/knowledge-graph/validate.py --harness` appears.

---

## B. Knowledge graph

### H-06 — SCHEMA.md defines all eight node types with required fields
Documents exactly these node types: `Decision`, `Workstream`, `ContractItem`, `Repo`, `Hardware`, `Capability`, `Risk`, `Event`. Defines the required per-node fields: `id`, `type`, `label`, `body`, `status`, `ts`, `source`. Documents status vocabularies at least for Decision (`locked`/`superseded`), Risk (`open`/`mitigated`/`closed`), and Workstream/Capability (`planned`/`in_progress`/`done`/`deferred`). Node ids are `snake_case` or `[A-Z]{1,3}-\d{2}`.

**Check:** all eight type names present; all seven field names present; status vocabulary listed; the id pattern is stated.

### H-07 — SCHEMA.md defines all six edge types with direction
Documents exactly these edge types with allowed `from-type → to-type` pairs and a one-line semantic: `DECIDES`, `DEPENDS_ON`, `EVIDENCED_BY`, `BLOCKS`, `IMPLEMENTS`, `SUPERSEDES`. Edge record fields: `from`, `type`, `to`, `ts`, and optional `note`.

**Check:** all six edge type names present, each with an explicit direction pair; the four required edge field names present.

### H-08 — JSONL is valid, seeded, and validated by a documented command
`nodes.jsonl` and `edges.jsonl` are line-delimited JSON: one JSON object per line, no wrapping array, file ends with a newline, no blank lines. `SCHEMA.md` documents a copy-pasteable validation command that exits 0 on the seeded graph and non-zero on a malformed one.

**Check:** run `python3 .agent/knowledge-graph/validate.py` → exit 0. Append a line `{"id":"x"` to a copy and re-run with `--nodes` → non-zero.

### H-09 — Seed Decision nodes for every locked id in GOAL.md
`nodes.jsonl` contains one `type:"Decision"` node, `status:"locked"`, for each of the twelve ids in H-04. Each `body` restates the decision well enough to act on without reading `GOAL.md`.

**Check:** all twelve ids present exactly once; each has `"status": "locked"` and `"type": "Decision"`.

### H-10 — Seed Workstream nodes with existing source directories
Ids `ws_00_harness`, `ws_01_hero_loop`, `ws_02_robotics_layout`, `ws_03_embed_shell`, `ws_04_record_replay`, `ws_05_stunt_extras`. Each `source` is a directory that exists. `ws_02` through `ws_05` are `deferred` on first write. `ws_00_harness` and `ws_01_hero_loop` may be `in_progress`.

**Check:** all six ids present; `os.path.isdir(source)` is true for each; `ws_05_stunt_extras` is `deferred`.

### H-11 — Seed Capability, Repo, Risk, and Hardware nodes
Capabilities, one per `GOAL.md` definition-of-done line: `cap_live_ws_camera_teleop`, `cap_3d_map_hud`, `cap_embed_page`, `cap_mcap_replay`, `cap_stunt_extras` (`deferred`).

Repos: `repo_vizdoom`, `repo_foxglove_sdk`, `repo_freedoom`, `repo_lunar_lander`, each with a URL.

Risks: `vizdoom_macos_build` (open — ViZDoom on darwin 25 / Python wheels), `commercial_wad` (open — do not redistribute a commercial IWAD).

Hardware: `hw_mac_dev` with `status:"present"`.

No `Event` node is seeded. There is no event deadline.

**Check:** all five capability ids present; `cap_stunt_extras` is `deferred`; both risk ids present with `"status": "open"`; `hw_mac_dev` is `present`; `grep '"type": "Event"' nodes.jsonl` is empty.

### H-12 — ContractItem nodes for this contract
For every item id in this file (`H-01` … `H-NN`), `nodes.jsonl` contains a `type:"ContractItem"` node with `id` equal to that item id, `label` equal to the item's one-line title, and `source:".agent/workstreams/00-harness/contract.md"`. Each has an `IMPLEMENTS` edge to `ws_00_harness`. Status stays `specified`.

**Check:** the count of `"type": "ContractItem"` nodes with ids matching `^H-[0-9]{2}$` equals the number of `### H-` headings in this contract; every such node has a matching `IMPLEMENTS` edge to `ws_00_harness`.

### H-13 — Required edges covering the five live edge types
`edges.jsonl` contains at minimum these edges (plus any others the generator justifies in `log.md`):

- `DECIDES`: `dec_vizdoom_engine → ws_01_hero_loop`; `dec_foxglove_sdk_ws → cap_live_ws_camera_teleop`; `dec_freedoom_legal → ws_01_hero_loop`; `dec_teleop_twist → ws_01_hero_loop`; `dec_embed_viz → ws_03_embed_shell`; `dec_no_canvas → ws_01_hero_loop`; `dec_phase_gating → ws_05_stunt_extras`; `dec_state_on_disk → ws_00_harness`.
- `DEPENDS_ON`: `ws_01_hero_loop → ws_00_harness`; `ws_02_robotics_layout → ws_01_hero_loop`; `ws_03_embed_shell → ws_02_robotics_layout`; `ws_04_record_replay → ws_03_embed_shell`; `ws_05_stunt_extras → ws_03_embed_shell`; `cap_3d_map_hud → cap_live_ws_camera_teleop`; `cap_embed_page → cap_3d_map_hud`; `cap_mcap_replay → cap_embed_page`.
- `EVIDENCED_BY`: `dec_foxglove_sdk_ws → repo_foxglove_sdk`; `dec_vizdoom_engine → repo_vizdoom`; `dec_freedoom_legal → repo_freedoom`.
- `BLOCKS`: `vizdoom_macos_build → ws_01_hero_loop`.
- `IMPLEMENTS`: `ws_01_hero_loop → cap_live_ws_camera_teleop`; `ws_02_robotics_layout → cap_3d_map_hud`; `ws_03_embed_shell → cap_embed_page`; `ws_04_record_replay → cap_mcap_replay`; `ws_05_stunt_extras → cap_stunt_extras`; plus the `H-xx → ws_00_harness` edges from H-12.

`SUPERSEDES` is legal in the schema and unused in the seed because nothing has been retired yet.

**Check:** every listed triple is present in `edges.jsonl`; `validate.py --harness` reports no `H-13: required edge missing`.

### H-14 — Graph is queryable by the stated resume questions
`SCHEMA.md` documents at least four copy-pasteable one-liner queries and their expected answers on the seeded graph: (1) list all open risks; (2) which workstream is next for product code; (3) list locked decisions and what each decides; (4) list what a given workstream depends on.

**Check:** run all four documented queries → each exits 0 and returns a non-empty result matching the expected answers in `SCHEMA.md`.

---

## C. Workstream tree and loops

### H-15 — Every workstream has the required files, correctly shaped
`00-harness` has `contract.md`, `progress.md`, `log.md`, `critique.md`. Product workstreams `01`–`05` each have `PLAN.md`, `contract.md`, `progress.md`, `log.md`. Every `contract.md` names its workstream.

**Check:** the H-01 paths exist; each `contract.md` identifies its workstream in the first 20 lines.

### H-16 — Deferred workstreams 02-05 state entry criteria — PASS (2026-09-18, evaluator kimi-k3-high)
`02-robotics-layout`, `03-embed-shell`, `04-record-replay`, and `05-stunt-extras` each still have the `contract.md` H-01 requires (this item does not delete, rename, or drop any H-01 path). While a workstream is still deferred, that file is an explicit deferral stub: it contains the word `deferred`, names what the workstream will own, names the entry condition that un-defers it, and names the KG nodes it is gated by. A workstream that already has a gated numbered contract (`ES-` / `RL-` / `RR-` / `SX-` / `HL-` item headings) is allowed to drop `deferred`. `05` stays deferred until `01`–`03` are evaluated `done` while it is still on the stub path.

**Check:** from `$ROOT`, for each of `.agent/workstreams/{02-robotics-layout,03-embed-shell,04-record-replay,05-stunt-extras}/contract.md` (file must exist; H-01 is not relaxed), at least one of these two greps succeeds:

1. **Stub (still deferred):** `grep -ci deferred $f` is non-zero **and** `grep -ciE 'entry condition' $f` is non-zero. For `05-stunt-extras` on this path, also `grep -ciE '01-hero-loop|02-robotics-layout|03-embed-shell|cap_live_ws_camera_teleop|cap_3d_map_hud|cap_embed_page' $f` is non-zero.
2. **Gated numbered contract:** `grep -cE '^### (RL|ES|RR|SX|HL)-' $f` is non-zero. This path PASSes even if `deferred` is absent.

A file that matches neither FAILs. Matching both is a PASS (a gated contract may still mention `deferred` as history). Copy-paste:

```sh
fail=0
for ws in 02-robotics-layout 03-embed-shell 04-record-replay 05-stunt-extras; do
  f=".agent/workstreams/$ws/contract.md"
  test -f "$f" || { echo "H-16 $ws: missing file FAIL"; fail=1; continue; }
  gated=$(grep -cE '^### (RL|ES|RR|SX|HL)-' "$f" || true)
  stub=$(grep -ci deferred "$f" || true)
  entry=$(grep -ciE 'entry condition' "$f" || true)
  if [ "$gated" -gt 0 ]; then
    echo "H-16 $ws: gated ($gated) OK"
  elif [ "$stub" -gt 0 ] && [ "$entry" -gt 0 ]; then
    if [ "$ws" = "05-stunt-extras" ]; then
      caps=$(grep -ciE '01-hero-loop|02-robotics-layout|03-embed-shell|cap_live_ws_camera_teleop|cap_3d_map_hud|cap_embed_page' "$f" || true)
      if [ "$caps" -eq 0 ]; then echo "H-16 $ws: stub missing 01–03/caps FAIL"; fail=1; continue; fi
    fi
    echo "H-16 $ws: stub OK"
  else
    echo "H-16 $ws: neither stub nor gated FAIL"
    fail=1
  fi
done
[ "$fail" -eq 0 ]
```

### H-17 — progress.md has a machine-readable header
Every `progress.md` starts with a header block carrying, one per line before the first blank line: `status:` (one of `planning`, `planning complete`, `amended`, `awaiting generator`, `in progress`, `blocked`, `done`, `deferred`), `owner:`, `updated:` (ISO date), `next action:`, `blockers:` (`none` or a KG `Risk` id).

**Check:** `validate.py --harness` reports no `H-17` failure.

### H-18 — log.md is append-only with the fixed entry format
Every `log.md` uses only `## [YYYY-MM-DD] op | title` headings, in ascending date order, one entry per action, and states at the top (first 8 lines) that the file is append-only.

**Check:** `validate.py --harness` reports no `H-18` failure; `00-harness/log.md` and `01-hero-loop/log.md` each gained a `generator` entry dated `2026-09-18`.

### H-19 — loops/README.md specifies eval-after-generator and kg-sync
Specifies the eval-after-generator loop and the knowledge-graph sync loop, each with trigger / inputs / output / exit. States that there is no event deadline loop.

**Check:** section exists for both loops; contains `smoke`, a statement that eyeballing is insufficient, the validation command `python3 .agent/knowledge-graph/validate.py`, and the phrase `no event deadline`.

### H-20 — Cursor rule alwaysApply, allowed models, resume from disk
`.cursor/rules/agent-os.mdc` has `alwaysApply: true`, names `cursor-grok-4.6-high-fast` and `kimi-k3-high`, tells agents to resume from `.agent/`, and tells them to write to files not chat.

**Check:** `validate.py --harness` reports no `H-20` failure; `grep -n 'alwaysApply: true' .cursor/rules/agent-os.mdc` matches.

---

## D. Resume and self-check

### H-21 — Harness self-check is one documented command
`.agent/COORDINATION.md` documents a single copy-pasteable command that verifies the harness and exits 0 on the delivered tree.

**Check:** run `python3 .agent/knowledge-graph/validate.py --harness && echo "HARNESS OK"` from `$ROOT` → exit 0; break one thing (rename `nodes.jsonl`) → non-zero; restore.

### H-22 — Generator closed the loop on disk
`.agent/workstreams/00-harness/log.md` gained a `## [YYYY-MM-DD] generator | ...` entry, and `progress.md` carries a legal `status:` with an updated `next action`. No knowledge-graph line was rewritten in place — only appended (or first-written).

**Check:** `log.md` has a `generator` entry; `progress.md` status is in the H-17 vocabulary; JSONL files have no in-place rewrite in this run (they are first writes).

---

## Out of scope for this contract (do not let a later harness-only generator drift here)

- Authoring a critic-gated `HL-nn` contract for `01-hero-loop` (planner + Kimi critic).
- Implementing Grid/TF/SceneUpdate, embed page, MCAP, events, comparison, or remote access.
- Inventing new locked decisions. Anything not in `GOAL.md` is a question for the human, not a node.
- Ticking any `- [ ]` in any contract.
