# Critique — 04-record-replay contract gate

**Critic:** kimi-k3-high (contract critic; did not author the contract, did not write product code)
**Date:** 2026-09-18
**Target:** `contract.md` RR-01…RR-07
**Verdict: FAIL — 3 numbered amendments required.**

Method: every check was run verbatim from a clean shell at `$ROOT` (`.venv/bin/python`, `PYTHONPATH=$ROOT`), and every quoted literal was grepped against the named files. The bar was mechanical reproducibility, not product quality.

## What passes scrutiny

- **RR-01** — check runs clean (`RR-01 same-sdk-sink`). All quoted literals exist: `foxglove.open_mcap` (record.py:62), `from doom_foxglove.record import` + `open_recording` (server.py:27), `if not args.no_record` (server.py:228), `writer = open_recording` (server.py:230, smoke_replay.py:85).
- **RR-02** — mechanical from a clean shell. Verified that with `wad/` empty and no network, `make_engine` degrades to `FallbackEngine` (engine.py:405-448), so bare `./smoke-replay` still exits 0 offline. `exec "$PY" -m doom_foxglove.smoke_replay` (smoke-replay:12), `_fail` + `return 0` after the OK print (smoke_replay.py:105-109), `_check_replay_layout` called from `main` (smoke_replay.py:58) all present.
- **RR-03** — check runs clean against the existing `recordings/smoke.mcap` (52,571 bytes, six topics). `EXPECTED_TOPICS` order matches the `need` tuple exactly; `list_mcap_topics` walks `OP_CHANNEL` (record.py:91-100).
- **RR-05** — check runs clean (`RR-05 readme-ok`). All four required strings plus `## Replay an MCAP` heading present (README.md:89-103).
- **RR-06 / RR-07 rg invocations** — print nothing on the files they search (exit 1 = PASS as the contract states). README contains `cloud` ("no cloud share link in v1", README.md:103).

## Amendment 1 — RR-04's check false-fails on compliant code (disqualifying)

The verbatim check raises `AssertionError` today. `inspect.getsource(replay_layout)` includes the docstring:

```
"""File playback: camera, 3D, gauges, log. Teleop is hidden. Playback bar is Foxglove's."""
```

so `assert 'Teleop' not in src` fails even though `layouts/Replay.json` contains zero Teleop panels (verified by walking the JSON: Image, ThreeDee, Gauge ×3, Plot, Log, RawMessages). An evaluator running the stated check from a clean shell must FAIL RR-04 against correct work — the gate is broken, not the product.

**Fix:** make the source assertion docstring-proof. Either strip docstrings/comments before the substring test (e.g. via `ast`), or assert on the serialized layout (`json.loads(replay_layout().to_json())`) having no `panelType == "Teleop"`, and check that `replay_layout` does not reference `_teleop` via `__code__.co_names` or an AST call walk. Keep the JSON panel-walk half as-is; it is sound.

## Amendment 2 — RR-06 and RR-07 grep lists don't cover the 04-owned surface they claim

RR-07's own owned-files list names `replay_layout` in `doom_foxglove/layouts_export.py` and recording flags in `doom_foxglove/server.py`, yet both `rg` commands search only `record.py`, `smoke_replay.py`, `smoke-replay`, `Replay.json`. A cloud upload call (RR-06) or `setDataSource` / comparison / spectator code (RR-07) in `server.py` or `layouts_export.py` evades both checks. Verified the hole is currently empty (`rg` over those two files prints nothing), but the contract grades the check, not the current tree.

**Fix:** add `doom_foxglove/server.py` and `doom_foxglove/layouts_export.py` to both `rg` invocations.

## Amendment 3 — RR-07's events clause is not mechanically decidable

The prose FAILs on "events tagging … as product code in 04-owned files," but no `rg` pattern covers events, and `doom_foxglove/record.py` already ships an `EVENTS_TOPIC` import (record.py:16) and `smoke_events_recording_path` (record.py:51-52). An evaluator cannot tell from the stated check whether that existing code is a violation — the item is ungradeable as written.

**Fix:** either add an events pattern (e.g. `-e 'EVENTS_TOPIC' -e 'events'`) with an explicit carve-out naming the existing import/helper as allowed, or state in prose that the `EVENTS_TOPIC` import and `smoke_events_recording_path` in `record.py` are not events tagging and do not FAIL.

## Non-blocking observations (no amendment required)

- **RR-01** `assert 'Context(' not in rec` is the same docstring-fragile pattern as RR-04; it passes today only because the docstring writes "Context" without a parenthesis. Harden it while applying Amendment 1.
- **RR-03** pins the in-repo `list_mcap_topics`, which walks only top-level records; a future chunked MCAP (channels inside Chunk records) would false-fail. Acceptable today — the current file is unchunked and parses correctly — but the evaluator should know the parser's limit is deliberate.
- Gating this list satisfies entry condition (3) only. Conditions (1) `cap_embed_page == done` and (2) a completed live embed session remain unmet per `eval.md`; this gate does not un-defer `ws_04_record_replay` by itself.

## Bottom line

RR-01, RR-02, RR-03, RR-05 are mechanical and correct as written. RR-04's check cannot pass against compliant code; RR-06/RR-07 under-search their own declared scope; RR-07's events clause is ungradeable. **FAIL.** Planner applies Amendments 1-3 to `contract.md` only, then re-submit for gate.

---

# Re-gate — 04-record-replay contract

**Critic:** kimi-k3-high (contract critic; did not author the contract, did not write product code)
**Date:** 2026-09-18
**Target:** amended `contract.md` RR-01…RR-07 (planner applied amendments 1–3, 2026-09-18)
**Verdict: PASS.**

Method: every amended check was re-run verbatim from a clean shell at `$ROOT` (`.venv/bin/python`, `PYTHONPATH=$ROOT`). The bar remained mechanical reproducibility.

## Amendment verification

1. **RR-04 serialized layout, not getsource Teleop — APPLIED, mechanical.** The check no longer substring-searches `inspect.getsource`. It asserts `'_teleop' not in replay_layout.__code__.co_names` and `'TeleopPanel' not in replay_layout.__code__.co_names`, then walks the serialized `json.loads(replay_layout().to_json())` tree and the on-disk `layouts/Replay.json` for `panelType == "Teleop"` (count 0). Prose explicitly states the docstring naming Teleop is not a FAIL. Ran verbatim: passes — `RR-04 ['Image', 'ThreeDee', 'Gauge', 'Gauge', 'Gauge', 'Plot', 'Log', 'RawMessages']`. The docstring false-fail is gone; the check now passes against compliant code and would still catch a real Teleop panel or a `_teleop`/`TeleopPanel` reference.
2. **RR-06/RR-07 rg cover server.py and layouts_export.py — APPLIED.** Both `rg` invocations now list `doom_foxglove/record.py doom_foxglove/smoke_replay.py smoke-replay layouts/Replay.json doom_foxglove/server.py doom_foxglove/layouts_export.py`, matching RR-07's declared 04-owned surface. Ran verbatim: RR-06 rg prints nothing (exit 1 = PASS per contract).
3. **RR-07 events carve-out is decidable — APPLIED.** The rg now includes `-e 'EVENTS_TOPIC' -e 'events'`, and the prose names the exact allowed helpers: `EVENTS_TOPIC` import in `record.py` (if present), `smoke_events_recording_path` in `record.py`, `EVENTS_TOPIC` import and `events={EVENTS_TOPIC}` banner in `server.py`. Ran verbatim: 4 lines print — `record.py:52-53` (`smoke_events_recording_path` def + body), `server.py:19` (`EVENTS_TOPIC` import), `server.py:230` (`events={EVENTS_TOPIC}` banner). Every printed line maps 1:1 to a named carve-out entry; an evaluator can decide each line mechanically. No comparison-mode, remote-spectator, `setDataSource`, or agent-prompt lines print.

## Full-list re-verification

- **RR-01** — re-run verbatim after the planner's hardening (`'Context' not in open_recording.__code__.co_names` replaces the docstring-fragile `'Context(' not in rec`): passes, `RR-01 same-sdk-sink`. The non-blocking observation from the first gate is resolved.
- **RR-02, RR-03, RR-05** — unchanged by the amendments; verified mechanical in the first gate (clean-shell exit 0, six-topic MCAP parse, README strings). No re-amendment needed.

## Bottom line

All RR-01…RR-07 checks are mechanical: each runs verbatim from a clean shell at `$ROOT`, each FAIL condition is decidable from the stated output, and no check false-fails against the current compliant tree. **PASS.** This satisfies entry condition (3) for `ws_04_record_replay`. Conditions (1) `cap_embed_page == done` and (2) a completed live embed session remain unmet per `eval.md`; this gate does not un-defer the workstream by itself. Next: evaluator re-runs the gated items; generator does not tick boxes.

---

# PR-nn gate — 2026-09-18 (pause-replay slice, section E)

**Target:** `contract.md` PR-01…PR-10 only. RR-01…RR-07 not re-graded. ES-11 carve-out on `03-embed-shell/contract.md` confirmed.
**Verdict: FAIL — 6 amendments (A-1…A-6) must be applied to `contract.md` before a generator starts. A-7 is optional hardening on 03.**

Method: every PR Check was run verbatim from a clean shell at `$ROOT` (`.venv/bin/python`, `PYTHONPATH=$ROOT`). Product code does not implement pause-replay today, so most checks FAIL — that is expected and is **not** the basis of this verdict. The verdict rests on checks that would false-fail a compliant generator or false-pass a broken one.

## Clean-shell run record (today's tree)

| Item | Result today | Executable? | Notes |
|---|---|---|---|
| PR-01 | FAIL (exit 1: no `--control-port` in `main`) | yes | fails on missing product, correctly |
| PR-02 | FAIL (exit 1: `run_loop` has no `stop_event`) | yes | fails on missing product, correctly |
| PR-03 | FAIL (ImportError `start_control`) | yes | ImportError = FAIL per prose, correctly |
| PR-04 | FAIL (exit 1: no `id="pause-replay"`) | yes | all three `rg` fences print nothing today (exit 1 = PASS) |
| PR-05 | FAIL (exit 1: no `DEFAULT_CONTROL_URL`) | yes | fails on missing product, correctly |
| PR-06 | FAIL (static part: no `replaySelectLayoutCompileCheck`) | yes | `./web/check` itself exits 0, `EMBED CHECK OK` — the executable half works today |
| PR-07 | FAIL (exit 1/127: no `./smoke-pause-replay`) | yes | fails on missing product, correctly |
| PR-08 | FAIL (exit 127 + no `recording is off` in `web/src`) | yes | fails on missing product, correctly |
| PR-09 | FAIL (exit 1: `pause-replay` not in `main.ts`) | yes | resume fences print nothing today (PASS) |
| PR-10 | PASS today (`no-06`, both fences empty) | yes | optional-file guards work (`control.py` etc. absent, skipped) |
| ES-11 (03) | PASS (`carve-out-ok files 12`, forbid rg empty) | yes | see A-7 |

No check requires a browser, a Pro sign-in, or a `/tmp` helper. No vague criteria ("looks correct", "playable") found. The listed attacks are all covered somewhere: POST-before-ticks (`--immediate-pause`), double POST (`double_pause=ok`), GET before pause (`pre_pause=409`), `--no-record` (PR-08), `opaqueLayout` vs `layout` (PR-04/06/10), missing `#pause-replay` (PR-04 first assert), smoke that never POSTs (PR-07 AST `ticks` ban + `"/pause"` count).

## Defects found (the basis of FAIL)

1. **PR-02 false-fails a compliant `stop_event.wait()` loop.** The Check hard-requires `"is_set" in run_loop.__code__.co_names`, but the prose only requires "when that `threading.Event` is set, the loop must not call `engine.step` again". The idiomatic compliant shape `if stop_event is not None and stop_event.wait(1.0 / hz): break` (wait-as-sleep) never calls `is_set` and FAILs the Check. Check is stricter than prose → A-1.
2. **PR-02 false-passes a handler with no preflight.** `assert "do_OPTIONS" in text or "OPTIONS" in text` is satisfied by the `Access-Control-Allow-Methods: … OPTIONS` header line any compliant CORS handler emits, even if `do_OPTIONS` is absent and preflight 501s. No runtime check (PR-07) exercises `OPTIONS`, so this substring is the only gate → A-2.
3. **PR-07 AST walk misses the idiomatic thread form.** The prose says "`run_loop` on a thread"; the natural implementation `threading.Thread(target=run_loop, kwargs={"stop_event": ev, ...})` contains no `ast.Call` named `run_loop`, so the Check FAILs with "smoke never calls run_loop" (and separately on the missing `stop_event` keyword) against compliant code → A-3.
4. **PR-09 resume fence is evadable.** The `rg` only matches `path == "/resume"` / `endswith("/resume")`. A resume route written `self.path.startswith("/resume")` or as a routing-table entry `{"/resume": handler}` prints nothing and PASSes the fence while violating the item → A-4.
5. **PR-04 prose/check name mismatch.** Prose: "Quote `replayLayoutParams` **or the equivalent object**"; Check hard-requires the literal names `replayLayoutData` or `replayLayoutParams` in `web/src/layouts.ts`. A generator following the prose with a differently-named equivalent (e.g. `replayParams`) false-fails → A-5.
6. **PR-01 prose never names `fallback_if_busy`.** The Check requires `fallback_if_busy` in `inspect.signature(start_control).parameters`; the item prose and Pointers mention only the port, flag, and banner. The name is an established repo convention (`start_ws`, `server.py:113`), so this is discoverable, but the prose should state what the Check grades → A-6.

## Per-item attack notes (non-blocking)

- **PR-01** — `compact = src.replace(" ", "")` correctly tolerates `default = 8764` spacing. The `rosbridge|flask|fastapi|aiohttp` rg with the "every printed line is a comment" rule is decidable. Missing-file guard for `control.py` is present. Anti-hardcode adequate once A-6 lands.
- **PR-03** — `"409" in text` is a weak substring, but it is backed by the PR-07 runtime token `pre_pause=409`; the pair is sound. `MCAP_MAGIC` assert is exact.
- **PR-04** — `assert "click" in main` and `assert "setDataSource" in main` are already true on today's live-only tree; they carry no weight. The real teeth are `pause-replay in main`, the `type: "file"` / `.mcap` / `autoplay` / `new File` globs, and the quote clause ("Quote the `#pause-replay` `click` handler"). The mechanical check alone could PASS with the FileSource code living only in `compile-check.ts` and a dead `getElementById("pause-replay")` in `main.ts`; the mandatory quote is the anti-hardcode backstop. Acceptable, but the evaluator must be held to the quote — consider this a standing instruction, not an amendment.
- **PR-05** — order assert (`firstQuery` < `VITE_FOXGLOVE_CONTROL` < `DEFAULT_CONTROL_URL`) matches the `readWsUrl` shape; exact-literal `DEFAULT_CONTROL_URL = "http://localhost:8764"` matches repo style (double quotes, cf. `DEFAULT_WS_URL`). The 8766+control README line requirement is mechanical.
- **PR-06** — symbol names `replaySelectLayoutCompileCheck` / `fileSourceCompileCheck` appear only in the Check and PASS paragraph, not the item prose; consistent with ES-contract style (`playSelectLayoutCompileCheck`), acceptable.
- **PR-07** — happy-path token set (`SMOKE-PAUSE-REPLAY OK`, `ticks=`, `http://`, `bytes=`/`file=`, `pre_pause=409`, `double_pause=ok`, `step_stopped=ok`) and immediate-path `immediate_pause=ok` are fully mechanical. `src.count("/pause") >= 2` is gameable by a comment, but the runtime tokens close that hole.
- **PR-08** — tokens `no_record=409` + `step_stopped=ok` mechanical; `recording is off` scan is case-insensitive across `web/src`. Sound.
- **PR-10** — fences mechanical; `06-*` glob check runs and prints `no-06` today; per-file existence guards correct. The explicit statement that `setDataSource`/`FileSource`/`type: "file"` and the RR-07 `EVENTS_TOPIC` helpers do not FAIL is the right carve-out.

## ES-11 carve-out confirmation (03-embed-shell)

Ran the ES-11 Check verbatim: `rg comparison|spectator|rosbridge` prints nothing; the carve-out script prints `ES-11 carve-out-ok files 12`. PASS today. I also simulated every line a **compliant** PR generator is contractually required to add against the needle `mcap|Replay` and the allow regex: the `layouts/Replay.json` import (PR-04 requires the literal in `layouts.ts`), `replayLayoutData`, `readControlUrl` / `DEFAULT_CONTROL_URL` / `VITE_FOXGLOVE_CONTROL` (PR-05), `type: "file"` / `autoplay` / `new File` / `.mcap` (PR-04/06), `REPLAY_STORAGE_KEY`, and `#pause-replay` all match the allow regex or never trip the case-sensitive needle (`replaySelectLayoutCompileCheck` has no capital-R `Replay`; `MCAP` all-caps does not match `mcap`). The carve-out survives a compliant generator for all required lines. Residual: a gratuitous comment containing capital-R `Replay` (e.g. `// Replay.json is loaded as layout, not opaqueLayout`) on a line without an allow token would FAIL ES-11 — optional hardening A-7.

## Numbered amendments (planner applies to `contract.md` only; A-7 to `03-embed-shell/contract.md`)

- **A-1 (PR-02 Check):** replace `assert "is_set" in names, names` with `assert "is_set" in names or "wait" in names, names`, and add to the PR-02 prose: "`run_loop` may poll `stop_event.is_set()` or use `stop_event.wait(timeout)` as the tick sleep; either satisfies the Check."
- **A-2 (PR-02 Check):** replace `assert "do_OPTIONS" in text or "OPTIONS" in text, text` with `assert "do_OPTIONS" in text, text` (the stdlib `BaseHTTPRequestHandler` dispatch name), so a CORS `Allow-Methods` header line alone cannot satisfy the preflight requirement.
- **A-3 (PR-07 Check):** extend the AST walk to also accept the idiomatic thread form: treat an `ast.Call` whose `call_name` is `Thread` and whose keywords include `target=run_loop` (a `ast.Name` with `id == "run_loop"`) as a `run_loop` call site; for such a site require a `kwargs` `ast.Dict` keyword whose string keys include `"stop_event"` and exclude `"ticks"`. (Equivalent alternative: add prose "the smoke must invoke `run_loop(..., stop_event=...)` syntactically — a wrapper `def` is allowed; `Thread(target=run_loop, kwargs=...)` alone does not satisfy the AST check." Prefer the inclusive fix.)
- **A-4 (PR-09 Check):** broaden both resume-route `rg` invocations to `-e '"/resume"' -e "'/resume'"` (dropping the `path ==` / `endswith` anchors) so `startswith("/resume")` and routing-table forms are caught; keep the `control.py` existence guard.
- **A-5 (PR-04 prose):** change "Quote `replayLayoutParams` or the equivalent object" to "the Replay params object in `web/src/layouts.ts` must be named `replayLayoutData` or `replayLayoutParams` (the Check greps those literals)".
- **A-6 (PR-01 prose):** add one sentence: "`start_control` takes `fallback_if_busy: bool = False` (same convention as `start_ws`); the Check asserts that parameter name."
- **A-7 (ES-11, optional, non-blocking):** widen the allow regex with a bare `Replay\.json` alternative so a compliant generator's comment naming `Replay.json` without the `layouts/` prefix cannot trip the carve-out.

## Bottom line

**Gate: FAIL.** Nine of ten checks are fully mechanical and run verbatim today; PR-02 and PR-07 each contain a false-fail/false-pass pair that a compliant generator could hit (A-1…A-3), PR-09's fence is evadable (A-4), and two prose/check mismatches would diverge generator from evaluator (A-5, A-6). All amendments are mechanical edits to `contract.md` (A-7 to 03's). **A generator may not start.** Next: planner applies A-1…A-6 (optionally A-7), then re-gate. RR-01…RR-07 remain ticked and untouched; no PR box was ticked; no product code was written; `contract.md` was not edited by this critic.

---

# PR-nn re-gate — 2026-09-18 (pause-replay slice, section E)

**Target:** `contract.md` PR-01…PR-10 after planner applied A-1…A-6 (and A-7 on `03-embed-shell/contract.md` ES-11).
**Verdict: PASS. A generator may start.**

Method: every PR Check re-run verbatim from a clean shell at `$ROOT` (`.venv/bin/python`, `PYTHONPATH=$ROOT`). Product still does not implement pause-replay; PR-01…PR-09 still FAIL on missing product — expected, not a re-gate FAIL. The re-gate question was whether the six contract defects are gone. They are.

## Amendment verification

- **A-1 (PR-02) — APPLIED.** Check now reads `assert "is_set" in names or "wait" in names, names`; prose adds "`run_loop` may poll `stop_event.is_set()` or use `stop_event.wait(timeout)` as the tick sleep; either satisfies the Check." A compliant wait-as-sleep loop no longer false-fails. Re-ran verbatim: exit 1 on missing `stop_event` (missing product), correct.
- **A-2 (PR-02) — APPLIED.** Check now `assert "do_OPTIONS" in text, text`; the `"OPTIONS"` substring fallback is gone. A CORS `Allow-Methods` header line alone can no longer satisfy preflight.
- **A-3 (PR-07) — APPLIED, simulated.** The AST walk now collects both `("direct", run_loop_call)` and `("thread", Thread_call)` sites via `thread_target_is_run_loop` / `thread_kwargs_keys` / `dict_str_keys`, requiring `stop_event` and banning `ticks` in both forms. Simulation against synthetic sources: `lambda: run_loop(..., stop_event=ev)` inside `Thread` → pass; `Thread(target=run_loop, kwargs={'stop_event': ev, 'forever': True})` → pass; `run_loop(..., ticks=8, ...)` → correctly fails; `Thread(target=run_loop)` without kwargs → correctly fails; `kwargs={'ticks': 8, ...}` → correctly fails. Re-ran the verbatim Check: exit 1 on missing `smoke-pause-replay` (missing product), correct.
- **A-4 (PR-09) — APPLIED, probed.** Both resume-route `rg` invocations now use `-e '"/resume"' -e "'/resume'"` (anchors dropped). Probes: `self.path.startswith("/resume")` → matched (exit 0); `ROUTES = {"/resume": handler}` → matched (exit 0). The evasion forms are caught. Re-ran verbatim: `resume_btn_exit=1`, `resume_route_server_exit=1` on today's tree (PASS); the py half fails on missing `pause-replay` in `main.ts` (missing product), correct.
- **A-5 (PR-04) — APPLIED.** Prose now reads "The Replay params object in `web/src/layouts.ts` must be named `replayLayoutData` or `replayLayoutParams` (the Check greps those literals)". Prose and Check agree.
- **A-6 (PR-01) — APPLIED.** Prose now states "`start_control` takes `fallback_if_busy: bool = False` (same convention as `start_ws`); the Check asserts that parameter name." Verified `start_ws` convention at `doom_foxglove/server.py:113`.
- **A-7 (ES-11, optional) — APPLIED, probed.** Allow regex now includes a bare `Replay\.json` alternative. Re-ran the ES-11 Check verbatim: `ES-11 carve-out-ok files 12`, forbid rg empty. Probe: the comment line `// Replay.json is loaded as layout, not opaqueLayout` trips the needle and is now allowed.

## Full-list re-verification (verbatim, today's tree)

| Item | Result | Basis |
|---|---|---|
| PR-01 | FAIL (missing `--control-port`) | missing product; check executes |
| PR-02 | FAIL (missing `stop_event`) | missing product; check executes |
| PR-03 | FAIL (ImportError `start_control`) | missing product; ImportError = FAIL per prose |
| PR-04 | FAIL (missing `#pause-replay`) | missing product; all three rg fences empty (PASS) |
| PR-05 | FAIL (missing `DEFAULT_CONTROL_URL`) | missing product; check executes |
| PR-06 | FAIL (missing compile-check symbols) | missing product; `./web/check` exits 0 `EMBED CHECK OK` (first gate, unchanged tree) |
| PR-07 | FAIL (missing `./smoke-pause-replay`) | missing product; AST block simulated sound |
| PR-08 | FAIL (exit 127 + missing status string) | missing product; check executes |
| PR-09 | FAIL (missing `pause-replay` in `main.ts`) | missing product; fences empty (PASS) and now catch startswith/routing forms |
| PR-10 | PASS (`no-06`, fences empty) | unchanged |
| ES-11 (03) | PASS (`carve-out-ok files 12`) | widened regex re-verified |

## Bottom line

All six required amendments and the optional A-7 are present in the files, and the amended checks were re-run verbatim (A-3 and A-4 additionally validated against synthetic compliant/non-compliant inputs). No false-fail on `wait()` / `Thread` kwargs remains; `do_OPTIONS` is required; the resume fence catches `startswith` and routing-table forms; PR-04 names the literals; PR-01 names `fallback_if_busy`. **PASS.**

**A generator may start.** Files it should touch:

- `doom_foxglove/server.py:163` — `run_loop` gains optional `stop_event=None` kwarg; loop must not call `engine.step` once set (`is_set()` poll or `wait(timeout)` sleep both pass).
- `doom_foxglove/server.py:202` — `main` gains `--control-port` (default 8764), prints a `control http://` banner, calls `start_control(`; keep `if not args.no_record` guarding `open_recording` (RR-01).
- `doom_foxglove/server.py` or new `doom_foxglove/control.py` — `start_control` with `fallback_if_busy: bool = False` (mirror `start_ws` at `doom_foxglove/server.py:108-132`), stdlib `HTTPServer`/`ThreadingHTTPServer`, `do_OPTIONS`, `POST /pause` (idempotent, closes the `open_recording` writer, 200 `{"paused": true, "path": …}`), `GET /recording` (200 `application/octet-stream` after pause, **409** before), `Access-Control-Allow-Origin` on all responses. No `mcap.Writer`, no rosbridge/flask/fastapi/aiohttp.
- New `doom_foxglove/smoke_pause_replay.py` + new `./smoke-pause-replay` wrapper (`exec "$PY" -m doom_foxglove.smoke_pause_replay`, `_fail` returning 1; copy the shape of `doom_foxglove/smoke_replay.py` and `./smoke-replay`). Must call `run_loop` with `stop_event=` and no `ticks=` (direct call or `Thread(target=run_loop, kwargs={...})`), POST `/pause` twice, GET before pause (`pre_pause=409`), `--immediate-pause` and `--no-record` modes, ephemeral WS+control ports via `fallback_if_busy`.
- `web/index.html:21-22` — add `<button id="pause-replay">` with `Pause` in the label, next to Play/Debug, before `#foxglove` (`web/index.html:32`).
- `web/src/config.ts:5,25-26` — add `DEFAULT_CONTROL_URL = "http://localhost:8764"` and `readControlUrl()` (`firstQuery("control")` → `VITE_FOXGLOVE_CONTROL` → default, same shape as `readWsUrl`).
- `web/src/layouts.ts` — import `layouts/Replay.json` and export `replayLayoutData` (or `replayLayoutParams`) with `storageKey`, `layout`, `force: true`; never `opaqueLayout`.
- `web/src/main.ts` — `#pause-replay` `click` handler: POST pause to the control URL, GET the MCAP as `Blob`, `new File([blob], "<name>.mcap")`, `viewer.setDataSource({ type: "file", file, autoplay: true })`, then `selectLayout` with the Replay params; `--no-record` path sets `#status` mentioning `recording is off`.
- `web/src/compile-check.ts:19,36-37` — add `replaySelectLayoutCompileCheck: SelectLayoutParams` and `fileSourceCompileCheck: DataSource` (`type: "file"`, `autoplay: true`).
- `web/README.md` — document `--control-port`, `?control=`, `VITE_FOXGLOVE_CONTROL`, `8764`, and one line pairing `--port 8766` with an explicit `?control=`.

Success = `./smoke-pause-replay` exit 0 (also `--immediate-pause` and `--no-record`) **and** `./web/check` exit 0. The generator does not tick boxes, does not edit this contract or 01/02/03/05 contracts, and does not create `06-*`.
