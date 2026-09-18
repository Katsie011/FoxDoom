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
