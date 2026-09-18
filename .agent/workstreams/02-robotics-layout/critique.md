# Critique — 02-robotics-layout RL-01…RL-10 gate

**Date:** 2026-09-18
**Critic:** kimi-k3-high (did not write the contract or the product code)
**Target:** `contract.md` RL-01…RL-10 (planner's gated candidate)
**Verdict: FAIL** — 2 numbered amendments below. Everything else attacked held.

## Method

Not a vibe read. Every `repr` needle, quoted literal, and shell check was executed
against the repo from `$ROOT` with `$PY = .venv/bin/python`, `PYTHONPATH=$ROOT`:

- Built `Grid` / `FrameTransforms` / `SceneUpdate` (empty + one monster) / `Log`
  via `build_grid` / `build_tf` / `build_entities` / `build_log` and compared the
  real `repr` against every needle in RL-01/02/03/05.
- Ran the `publish_world` dummy-recorder portion of RL-01 verbatim.
- Ran `logs_from_delta` needles (RL-05) verbatim.
- Booted the real engine (`make_engine(fetch_iwad=False, prefer_vizdoom=True)` →
  vizdoom, freedoom1.wad, E1M1) and ran the observe/step portions of RL-01…RL-05
  in the contract's call order.
- Ran the RL-08 and RL-09 layout walks byte-for-byte as written: both PASS.
- Ran the RL-10 `rg` invocations verbatim: both exit 1, no output → PASS as specified.
- Ran `./smoke` (RL-06): exit 0, `SMOKE OK` line names all five 02 topics.
- `rg`-verified every literal the checks demand: `_map_pending = True` (5 sites in
  `engine.py`), `if world.map_grid is not None`, `parent_frame_id=MAP_FRAME` /
  `child_frame_id=BASE_FRAME`, `layout_error = _check_layouts()` inside `main()`,
  and the five `_fail` hooks naming `MAP_TOPIC`/`TF_TOPIC`/`ENTITIES_TOPIC`/
  `PLAYER_TOPIC`/`LOG_TOPIC`.

## Planner attack hints — disposition

- **repr needles vs encode/schema:** HELD. The `=` vs `:` split across items looks
  wrong but is exactly right: the SDK repr uses `field=value` at the top level of a
  message and `field: value` inside nested `{ ... }` structs. Verified:
  `frame_id="map"` (Grid), `parent_frame_id: "map"` / `child_frame_id: "base_link"`
  (FrameTransform), `frame_id: "map"` / `id: "monster:7"` / `cubes: [` /
  `entities=[]` (SceneUpdate), `name="doom"` / `message="Entering E1M1"` (Log).
  Every check also asserts `get_schema().name` and `len(msg.encode()) > 0`, so the
  needles are not the only leg.
- **topic is a callable:** HELD. `topic`/`schema_name` are methods on every channel;
  all five topic checks route through `topic_of`/`schema_of` callable shims.
- **RL-06 / RL-07 not collapsed:** HELD. RL-06 is exit-0 + quoted hooks and
  explicitly disclaims wire proof; RL-07 is the socket proof. `--hero` is an RL-06
  FAIL, stated twice. Confirmed `./smoke` currently has no `--hero` flag — that is
  01's HL-09 generator gap, and entry condition 2 correctly points there.
- **No GUI layout import:** HELD. F-3 plus RL-08/RL-09 item text; checks are pure
  JSON `panelType` walks, no app launch.
- **HL-11 not re-owned:** HELD. F-1 keeps `on_subscribe`/`on_unsubscribe` on HL-11;
  no RL item duplicates the getattr check.
- **rg no-match is PASS for RL-10:** HELD, stated explicitly; verified exit 1 today.
- **WIRE LAYOUT format / hardcoded print:** HELD with a noted residual. The line
  format is pinned token-for-token, counts and the four `*_schema=` values are
  mechanically matchable, and three explicit FAIL-ifs cover the known cheats
  (`publish_world` dicts, `/tmp` probe, out-of-repo client). Residual: judging that
  the quoted client code truly derives values from received frames is quote-based
  data-flow reading, not a regex. Accepted — the contract's own grading section
  sanctions "quote the exact file text the check names," the literals are exact
  (`foxglove.sdk.v1`, the `WIRE LAYOUT` prefix), and a fully mechanical anti-cheat
  for wire proofs does not exist. No amendment.

## Amendments (required before PASS)

### 1. RL-04 — "FAIL if the topic is a protobuf HUD" is uncheckable as written

The item text names a FAIL condition the check cannot detect. The check asserts
`PLAYER_SCHEMA['required']` order, `as_json()` keys/types, and the topic name —
none of which change if `world_channels()['player']` is swapped to a protobuf
channel. An evaluator running the check mechanically would PASS a protobuf HUD
that the item text says must FAIL. Item text and check disagree; the check is the
gradeable part, so the check must grow the assertion.

The mechanical assertion exists today (verified): `message_encoding` is a plain
attribute on the base `Channel` — `'json'` on `player`, `'protobuf'` on `map`.
Add to the RL-04 check, after the `topic_of(ch['player'])` assertion:

```python
enc = getattr(ch['player'], 'message_encoding', None)
enc = enc() if callable(enc) else enc
assert enc == 'json', enc
```

(Callable-shimmed because the contract already established that channel attributes
may be methods; today it is a plain attribute.)

### 2. RL-01 — dummy channel dicts omit `'events'`; check passes by comprehension laziness

`publish_world` reads `channels["events"]` (topics.py:258) whenever
`world.logs` is non-empty, and `world_channels()` does ship an `events` channel.
Both dummy dicts in the RL-01 check are built from
`('map', 'tf', 'entities', 'player', 'log')` only. The check passes today solely
because both calls pass `logs=[]`, so the list comprehension never evaluates
`channels["events"]` (verified by running the portion verbatim). A legal refactor
of `publish_world` — e.g. hoisting `ev_ch = channels["events"]` above the
comprehension — would turn RL-01 into a `KeyError` false-FAIL on a change that
has nothing to do with map cadence. A check must grade its item, not incidental
laziness. Add `'events'` to both dummy-dict key tuples:

```python
dummy = {k: Rec() for k in ('map', 'tf', 'entities', 'player', 'log', 'events')}
dummy2 = {k: Rec() for k in ('map', 'tf', 'entities', 'player', 'log', 'events')}
```

## Non-amendment observations (do not block)

- RL-09's `(topics.get('/doom/entities') or {}).get('visible', True)` passes when
  `visible` is absent. That matches Foxglove default-visible semantics; acceptable.
- RL-03 correctly refuses to pin `entity_count=209` (fallback may ship a dummy
  cube). Live engine today returns 209; the check does not depend on it.
- Entry conditions 1–3 are honestly unmet today (`cap_live_ws_camera_teleop` still
  `planned`; `./smoke --hero` does not exist yet — it is 01's HL-09 gap). That is
  gating state, not a contract defect.
- RL-07 currently fails (no `WIRE LAYOUT` in `smoke.py`) — the contract itself
  names this as the expected generator gap. Correct.

## Verdict

**FAIL.** Apply amendments 1 and 2 to RL-04 and RL-01 respectively, then re-gate.
Both are small, mechanical, and do not change what any item means — they make the
stated FAIL conditions actually reachable by the stated checks.

---

# Re-gate — 2026-09-18 (critic, kimi-k3-high)

**Target:** amended `contract.md` RL-01…RL-10 (planner applied amendments 1–2).
**Verdict: PASS.**

## Amendment verification (executed, not read)

- **Amendment 1 (RL-04):** the check now shims `message_encoding` and asserts
  `enc == 'json'` after the `topic_of(ch['player'])` assertion. Ran it against
  `world_channels()`: `player` channel reports `'json'` (and `map` still reports
  `'protobuf'`, so the assertion discriminates). The "FAIL if protobuf HUD" item
  text is now reachable by the check. HELD.
- **Amendment 2 (RL-01):** both dummy dicts are now built from
  `('map', 'tf', 'entities', 'player', 'log', 'events')`. Ran the verbatim
  `publish_world` portions: `map is None / n == 0` on the empty-grid call still
  passes, and with a `logs` entry whose `kind` is in `EVENT_KINDS`
  (`death/level/pickup/weapon`) the `events` recorder is reached with no
  `KeyError`. A hoist of `channels["events"]` above the comprehension no longer
  false-FAILs the item. HELD. (Note for the evaluator: a `LogEvent` with default
  `kind='info'` is filtered out by `EVENT_KINDS` before `channels["events"]` is
  touched — that is product behavior, not a check defect.)

## Full-list mechanicality

RL-02…RL-03 and RL-05…RL-10 are byte-identical to the versions executed in the
first gate; every attack disposition above still stands (repr needles verified
against real SDK messages, callable shims on topic/schema_name, RL-06/RL-07 split
with `--hero` as an RL-06 FAIL, RL-08/RL-09 pure JSON `panelType` walks, RL-10
`rg` no-match is PASS, RL-07 `WIRE LAYOUT` pinned token-for-token with named
anti-hardcode FAIL-ifs). The one accepted residual — RL-07's quote-based
data-flow reading of the wire client — is sanctioned by the contract's own
grading section and has no mechanical alternative; it does not block the gate.

All ten items are mechanical: each grades by running a stated shell check from
`$ROOT` or quoting named file literals. No further amendments.

## Next action

Gate is passed. Per `progress.md`: KG may un-defer `ws_02_robotics_layout`
(entry conditions 1–2 remain 01's burden), and the **Grok generator**
(cursor-grok-4.6-high-fast) implements the remaining product gap — **RL-07
`WIRE LAYOUT` inside `./smoke`** (still missing from `doom_foxglove/smoke.py` as
of this re-gate). Generator does not tick boxes and does not edit this contract.
