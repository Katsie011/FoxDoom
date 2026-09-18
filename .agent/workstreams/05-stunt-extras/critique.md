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

---

# UX gate — 2026-09-18 (critic, kimi-k3-high)

**Target:** `contract.md` section F, `UX-01`…`UX-14` only. SX-01…SX-06 not re-graded. Surgical amendments in `02` (RL-08/RL-09), `04` (RR-04, PR-09), `03` (ES-11), and GOAL `dec_host_html_hud` / `/doom/walls` wording checked for consistency.
**Verdict: FAIL** — seven numbered amendments below. Missing-product FAILs (no `WALLS_TOPIC`, no `#key-hud`, no `build_walls` on today's tree) are expected and are **not** gate failures; every defect named here is a check that cannot be run as written, false-fails compliant code, or is evadable.

Method: every import, symbol, field order, repr pattern, and fence `rg` in the UX checks was executed or verified against the tree on disk (`.venv/bin/python`, `PYTHONPATH=$ROOT`). No product code was written; no boxes ticked; `contract.md` untouched.

## What verified clean (no amendment needed)

- **Runnability** — every UX check is headless stdlib/venv Python + `rg` + repo smokes from `$ROOT`. No browser, no Pro, no `.foxe`, no MCP clicking required by any Check. `./smoke` and `./smoke-pause-replay` are pre-existing gated commands.
- **Repr assumptions (UX-03, UX-13)** — executed `build_entities` on the installed SDK: repr is protobuf-style, so `cubes: [`, `id: "monster:7"`, and `z: <float>` tokens all render as the checks expect. Note: SDK `SceneUpdate` exposes only `encode`/`get_schema` (verified `AttributeError` on `.entities`) — repr-parsing is the *only* in-process content probe, which amendment 1 respects.
- **Constructors** — `WorldState(pose, player, entities, map_grid, logs)` positional construction in UX-03/UX-13 matches the dataclass (`world.py:156-163`, `map_name` defaults `""`). `PoseState` 4 fields, `PlayerState` 6, `Entity` kwarg set all match. `hollow_room("fallback")` signature matches (`world.py:192`). `world_channels()` / `publish_world(channels, world)` signatures match; `Channel.topic` is a bound method, and UX-13's `topic_of` callable branch handles it.
- **Fences pass the current tree** — `getContext(` / `<canvas` / `HTMLCanvasElement` / `installExtensions` / `.foxe` over `web/src` + `web/index.html`: zero hits (UX-04/UX-11 will not false-fail compliant code). `pointerlock` / `mouse-look` / `rosbridge` / `comparison.mode`: zero hits (UX-12). `struct.unpack` hits only `ws_client.py` (WS framing) and `record.py` (MCAP) — both pre-existing and legitimate.
- **UX-14 backend detection is deterministic** — `smoke.py:116` always prints `SMOKE engine backend={vizdoom|fallback} …`, so the ≥10 (vizdoom) / ≥4 (fallback) threshold selection is mechanical.
- **UX-10 AST** — current `smoke_pause_replay.py` uses `Thread(target=run_loop, kwargs={… "stop_event" …})`; the check's direct-call/Thread-kwargs walk covers both forms and the `ticks=` ban is PR-07-consistent.
- **Cross-contract consistency** — GOAL `dec_host_html_hud` explicitly supersedes the old no-HUD reading of `dec_stock_panels_only` and allows host HTML HUD; `/doom/walls` is in the GOAL topic contract; the IWAD-lump-parser non-goal matches UX-13. ES-11's allow-list names exactly `#key-hud`, `#hud-bars`/`#hud-health`/`#hud-armor`/`#hud-ammo`, `#replay-files`, `POST /new-game` — matches UX-01/04/05/08. RL-08/RL-09/RR-04 are Gauge-not-required, matching UX-09 (Gauge count 0 or 3 both pass; `ALLOWED` includes `Gauge`; extra `/doom/walls` on ThreeDee does not collide with RR-04's ticked asserts). PR-09 allows `POST /new-game` and forbids `/resume` — matches UX-05/UX-07/UX-12. RL-01's dummy dicts already include `'walls'` (`02-robotics-layout/contract.md:97,100`), matching UX-03/UX-13 dummy construction; the Grid stays.

## Amendments (required before PASS)

### 1. UX-13: the check never verifies extrusion on the message

The special-attack requirement is 3D extrusion (`size.z` > `DEFAULT_CELL_M`), but the check asserts only the *constant* (`WALL_HEIGHT_M == 2.4`) and `"size" in r.lower()`. A builder that emits flat plates (`size.z = 0.05`) — the 2D-Grid-in-SceneUpdate-clothing evasion — passes every assert while violating the item's core. Attribute-walking is impossible (verified: SDK messages expose only `encode`/`get_schema`). **Fix:** add a repr-regex height assert on the `build_walls([])` message (and the `dummy2` walls message), e.g.:

```python
zs = [float(v) for v in re.findall(r"z: ([0-9.]+)", r)]
assert zs and max(zs) > DEFAULT_CELL_M, zs
```

Verified the SDK repr renders `z: <float>` tokens, so this is mechanical. A flat-plate builder (all z ≤ 0.5) FAILs; cubes with `size.z = 2.4` or line points at z = 2.4 PASS.

### 2. UX-13: the `struct.unpack` fence is evadable via a new module

The `rg` targets exactly `engine.py world.py topics.py`. A generator adding `doom_foxglove/wadparse.py` with a from-scratch IWAD lump parser passes the fence while violating the locked `dec_vizdoom_engine` non-goal — same evasion class as SX-06 amendment 2. **Fix:** widen the `rg` to all of `doom_foxglove/`; PASS only if every printed line is in `ws_client.py` or `record.py` (verified: those are the only current hits — WebSocket framing and MCAP record parsing, not WAD lumps); any hit in another file is FAIL. Filename-column check, no taste.

### 3. UX-13: prose permits a design the check fails

The prose allows "an equivalent once-per-level `world.walls` pending flag", but the check builds `WorldState(pose, player, [], grid, [])` — no walls state — and asserts `dummy2["walls"].n == 1`. A pure pending-flag design (walls emitted only when the engine supplied linedefs) false-FAILs here. **Fix (pick one):** (a) strike the pending-flag alternative and state flatly that with `map_grid` set and no engine lines, `publish_world` must emit the hollow-room fallback walls once; or (b) change the check to construct the world with the flag/lines set. Option (a) is one sentence and matches the `build_walls([])` fallback the check already locks.

### 4. UX-06: `assert ".." in text` false-fails compliant traversal guards

The item's requirement is "reject `..` path traversal (404 or 400; do not read outside `recordings/`)". A guard written as `os.path.basename(name)`, `Path(name).name != name`, or `resolve().is_relative_to(recordings_dir)` contains no literal `..` and FAILs the assert despite being compliant. **Fix:** widen to `assert any(t in text for t in ("..", "basename", "is_relative_to", "normpath"))` (or lock the guard style in the prose). Keep the runtime traversal probe in UX-10's territory as-is.

### 5. UX-02: the check cannot detect the keydown-only evasion the item forbids

All asserts run over the concatenated `joined` blob. `"HoldController" in joined` is already true today (`keybindings.ts:44`); `"aria-pressed" in joined` and `"pressed" in joined` are already true today (the layout-play button, `main.ts:51`). So once `subscribe` exists in `keybindings.ts` and the string `key-hud` appears anywhere in `web/src`, every assert passes even if `#key-hud` is painted from a window `keydown` listener that never reads `HoldController` motion — the exact FAIL case the prose names. **Fix:** add a per-file coupling assert:

```python
hud_files = [p for p in Path("web/src").glob("*.ts") if "key-hud" in p.read_text(encoding="utf-8")]
assert hud_files, "no key-hud ts"
for p in hud_files:
    t = p.read_text(encoding="utf-8")
    assert ("HoldController" in t) or ("onMotion" in t) or ("subscribe" in t), p
```

Mechanical; closes the cross-file split without forbidding a separate HUD module.

### 6. UX-11: self-contradictory PASS rule (same class as SX-06 amendment 1)

"PASS only if `rg` prints nothing (exit 1 = PASS)" versus "Comments that name `.foxe` as forbidden are allowed only if they do not call an API" — deciding whether a comment "calls an API" (commented-out code?) is taste, and it contradicts prints-nothing. **Fix:** one rule — PASS if `rg` prints nothing, **or** every printed line is a prose comment (first non-whitespace characters `//`, `/*`, `*`, or `<!--`) containing no `(` call syntax; any other printed line is FAIL.

### 7. UX-04: the 200/300 maxima are searched only in TS, not CSS

`joined` globs `web/src/*.ts` only, but the prose says "Width/style is CSS". A compliant design with the maxima in `styles.css` (e.g. `width: calc(var(--h) / 200 * 100%)`, TS setting `--h` raw) false-FAILs `assert "200" in joined and "300" in joined`. **Fix:** search the TS blob plus `styles.css` for the maxima (the check already reads `styles.css`; one-line change).

## Nits (non-blocking; planner may adopt)

- **UX-05:** `assert "new-game" in live or "new_game" in live` forces the token into `main`'s source; a restart-event design named otherwise is prose-compliant but fails. Natural implementations will contain the token; noted, not blocking.
- **UX-12:** the fence `rg` covers `web/` + `server.py`/`control.py` only; a rosbridge/comparison surface in a new `doom_foxglove/` module evades it (SX-06 already fences comparison tokens package-wide; rosbridge is a GOAL non-goal). Consider widening for symmetry.
- **UX-14:** "(or `backend=vizdoom` on a nearby engine line)" is loose; `backend=` is unconditionally printed (`smoke.py:116`), so threshold selection is in fact deterministic — tighten the sentence.
- **UX-13:** ViZDoom-linedef sourcing is carried by a quote instruction plus UX-14's ≥10-under-vizdoom threshold; in an eval env without vizdoom only the quote guards it. Acceptable under this contract family's quote convention; noted.
- **UX-01:** single-letter asserts (`"W" in chunk`) are weak, but the `#key-hud` CSS quote plus the Attack note carry the item.

## Gate decision

**FAIL.** Amendments 1–7 must land in `contract.md` (planner's edit, not mine) before section F is critic-gated. Nits are optional. No generator starts on UX-01…UX-14 until the amended section is re-attacked and passes.

---

# UX re-gate — 2026-09-18 (critic, kimi-k3-high)

**Target:** `contract.md` section F after planner applied UX amendments A-1…A-7.
**Verdict: PASS.** A generator may start on UX-01…UX-14.

Method: each amendment was diffed against the amended contract text; the two widened fence `rg`s were re-run from `$ROOT`; the new repr-regex was executed against a real SDK `SceneUpdate`; the UX-09 check body and UX-12 `no-06` assert were run verbatim against today's tree. Missing product (`WALLS_TOPIC`, `#key-hud`, `build_walls`, `/new-game`, etc.) is expected and is not a gate issue.

## Amendment verification

1. **UX-13 extrusion verified on the message — resolved.** The check now asserts `zs = [float(v) for v in re.findall(r"z: ([0-9.]+)", r)]; assert zs and max(zs) > DEFAULT_CELL_M` on both the `build_walls([])` repr and the `dummy2` walls-channel repr. Executed the regex against a real SDK repr: it finds the z floats (`[0.4, 0.0, 0.8]` on a monster cube). A flat-plate builder (all z ≤ 0.5) now FAILs even with `WALL_HEIGHT_M == 2.4`; prose and Attack both name this.
2. **`struct.unpack` fence widened — resolved.** `rg` now covers all of `doom_foxglove/`; PASS is prints-nothing **or** every printed line's path is `ws_client.py` / `record.py` (filename-column check, comments in non-exempt files not exempt). Re-ran verbatim: 9 hits, all in the two exempt files → the fence passes the current tree and catches a new WAD-parser module.
3. **Pending-flag contradiction — resolved.** The "(or an equivalent `world.walls` pending flag)" alternative is gone. Prose now mandates: walls publish from `publish_world` when `map_grid` is set, and a flag-less `WorldState` with `map_grid` set must still emit the hollow-room fallback walls — exactly what the check asserts. The only remaining "pending flag" mention is the sentence forbidding the requirement.
4. **UX-06 traversal tokens — resolved.** Now `assert any(t in text for t in ("..", "basename", "is_relative_to", "resolve"))`, with matching quote prose. Compliant basename/resolve guards no longer false-FAIL.
5. **UX-02 per-file coupling — resolved.** Added `hud_files` walk: every `web/src/*.ts` file mentioning `key-hud` must also mention `HoldController` / `onMotion` / `subscribe` in the same file, with matching prose and Attack line. The keydown-only evasion (blob asserts passing on today's `aria-pressed` at `main.ts:51`) is now caught.
6. **UX-11 single PASS rule — resolved.** One rule: prints-nothing, or every printed line is a comment (first non-whitespace `//`, `/*`, `*`, `<!--`, or `#`) naming the extra as forbidden with no `(` call syntax; any other line is FAIL. The planner also widened the fence to include `doom_foxglove/` and broadened `getContext` — re-ran verbatim against the current tree: zero hits, exit 1, so the wider fence is satisfiable as-is.
7. **UX-04 maxima in TS or CSS — resolved.** The check now builds `blob = joined + css` and asserts `"200" in blob and "300" in blob`; quote prose names `web/src/*.ts` **or** `web/src/styles.css`. A CSS-`calc()` maxima design no longer false-FAILs.

## Mechanicality spot-checks on the amended section

- **UX-09** check body runs clean on today's tree (Play `['Image','Teleop','Gauge'×3]`, Debug/Replay include ThreeDee+Log, Replay has zero Teleop; extra Gauges allowed as specified) — the check is runnable and its PASS bar is satisfiable.
- **UX-12** `no-06` assert passes; resume/pointerlock/rosbridge/comparison fences print nothing on today's tree.
- **UX-13/UX-14** fail today only on missing product (`WALLS_TOPIC` import, `/doom/walls` in layout JSON) — expected.
- All UX checks remain headless: stdlib/venv Python, `rg`, and repo smokes from `$ROOT`.

## Re-gate decision

**PASS.** UX-01…UX-14 are mechanical and evasion-resistant. A generator may start on section F. Success commands for the evaluator loop: `./smoke-pause-replay --new-game` (UX-10), `./smoke` (UX-14), `cd web && npm run check` (TS compile of the HUD work; `web/package.json` `check` script), plus the in-process `$PY` checks in each item.
