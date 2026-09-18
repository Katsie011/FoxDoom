# Critique — 01-hero-loop contract gate

**Date:** 2026-09-18
**Critic:** kimi-k3-high (did not author this contract, does not grade product code)
**Target:** `.agent/workstreams/01-hero-loop/contract.md` HL-01…HL-14
**Verdict: FAIL — 8 required amendments (C-1…C-8) below. No generator starts until the planner applies them.**

Every attack was checked against the product source, not taken on faith. File:line pointers are to the current tree.

Unattacked items re-checked and found mechanically reproducible as written: HL-03, HL-04, HL-08, HL-11, HL-14. No amendment needed for those.

---

## C-1 — HL-09: `./smoke` is gated on 02 artifacts; negative path is waivable

**Attack confirmed.** The contract says extra 02 topics are "neither required nor forbidden" for HL-09, but the artifact under test contradicts that:

- `doom_foxglove/smoke.py:44-70` — `_check_layouts()` fails smoke unless `layouts/Play.json` and `layouts/Debug.json` exist and contain 02 panels (`Gauge`, `ThreeDee`, `Plot`, `Log`, `RawMessages`).
- `doom_foxglove/smoke.py:188-195` — smoke exits 1 unless `/doom/map`, `/tf`, `/doom/entities`, `/doom/player`, and `/doom/log` all publish.

So `./smoke` exit 0 — HL-09's only positive check — couples this contract to the 02 workstream. An 02 regression (or `rm -rf layouts/`) fails HL-09 while the hero loop is intact, and the evaluator cannot attribute the failure from the check as written. Separately, the negative path ("exits non-zero on failure") is fully waivable: "if every `python3` on the machine already has the deps … do not FAIL HL-09 for that alone." On a machine without a dep-less interpreter the item passes with zero evidence of the non-zero path.

**Amendment required.** Replace the HL-09 check with:

```sh
./smoke --hero
echo smoke_exit=$?
```

PASS only if exit is 0 and stdout contains `SMOKE OK`, `/doom/camera`, and `/cmd_vel`. `--hero` must skip `_check_layouts()` and the map/tf/entities/player/log requirements, so HL-09 cannot fail on 02 artifacts. (If the planner rejects a flag, the alternative is a check that greps stdout for the hero assertions and attributes any failure line naming a layout or an 02 topic to 02 — pick one, not both.)

Negative path, deterministic, no escape hatch:

```sh
$PY -c "import sys; from doom_foxglove.smoke import _fail; sys.exit(_fail('critic-injected'))"
echo neg_exit=$?
```

must exit 1, and the evaluator quotes `def _fail` returning 1 in `doom_foxglove/smoke.py`. Additionally, when an interpreter without deps exists — proven by quoting `python3 -c 'import numpy'` exiting non-zero — `python3 -m doom_foxglove.smoke --no-fetch-iwad` must also exit non-zero. The `_fail` leg is always required; the dep-less runtime leg is required whenever such an interpreter exists.

## C-2 — HL-10: A-or-B splits the "one smoke command"; subprotocol and line format undefined

**Attack confirmed.** PLAN.md defines smoke as "one command from repo root." HL-10 lets the generator satisfy the wire proof in a *separate* module (`doom_foxglove.wire_check`, option B), leaving `./smoke` itself never opening a socket — the exact gap eval.md finding 1 flagged, preserved under a passed contract. Three more holes:

1. "`cmd_vel_count` increments, **or equivalent**" — undefined; anything can be claimed equivalent.
2. The Foxglove SDK subprotocol `foxglove.sdk.v1` is never named. Option A's wording is satisfied by a bare `socket.create_connection` to the bound port, which proves nothing about ClientPublish.
3. The `WIRE` line format is undefined, so the four proofs are self-reported text with no mechanical shape to grep.

**Amendment required.** Strike option B; the wire proof lives in `./smoke`. Replace the HL-10 check with:

> `./smoke` stdout contains a line matching `WIRE CHECK capability=clientPublish camera_schema=foxglove.CompressedImage cmd_vel=<n> buttons=<n>` with both counts ≥ 1. `doom_foxglove/smoke.py` (or a helper it imports under `doom_foxglove/`) must open a WebSocket client to the bound port negotiating subprotocol `foxglove.sdk.v1`, and the counted Twist/buttons deliveries must arrive through `TeleopListener.on_message_data`, not `apply_raw`. The evaluator quotes the client code and the WIRE CHECK line. FAIL if the only `/cmd_vel` or `/doom/buttons` injection is `listener.apply_raw(...)`, if the counts exist without a socket, or if the only proof lives outside the repo (`/tmp` or otherwise).

(If the planner insists on keeping a standalone module, then HL-09's and PLAN.md's "one smoke command" language must be amended to say the wire proof is a second command — but the critic's recommendation is option A only.)

## C-3 — HL-06/HL-07: teleop.py dict-mapping unit tests, never engine motion

**Attack confirmed.** Both checks exercise only `apply_topic` + `binary_buttons` — pure JSON→dict mapping. The item texts claim "`linear.x` is forward/back" and "maps fire/use onto ViZDoom ATTACK/USE" — motion claims. The actual motion path is `VizDoomEngine._action` (`doom_foxglove/engine.py:280-288`), which maps flags positionally onto `self._button_names`; a button-order or naming bug there passes HL-06/HL-07 while the marine never moves and never fires.

**Amendment required.** Append to the HL-06 check:

```python
eng, info = make_engine(fetch_iwad=False, prefer_vizdoom=True)
eng.reset()
before = eng.observe().pose
for _ in range(20):
    eng.step(Command(linear_x=1.0))
after = eng.observe().pose
assert abs(after.x - before.x) + abs(after.y - before.y) > 0.01, (info.backend, before, after)
yaw0 = after.yaw
for _ in range(10):
    eng.step(Command(angular_z=1.0))
assert abs(eng.observe().pose.yaw - yaw0) > 0.01, 'turn did not change yaw'
eng.close()
```

This is backend-agnostic: `FallbackEngine.step` moves `_x`/heading (`engine.py:76-81`), ViZDoom moves the player; both surface through `observe().pose`.

Append to the HL-07 check:

```python
eng, info = make_engine(fetch_iwad=False, prefer_vizdoom=True)
if info.backend == 'vizdoom':
    assert 'ATTACK' in eng._button_names and 'USE' in eng._button_names, eng._button_names
eng.reset()
frame = eng.step(Command(fire=True, weapon=2))
assert frame.shape == (200, 320, 3)
eng.close()
```

## C-4 — HL-01: fallback gate matches unquoted note substrings

**Attack confirmed (minor).** The check keys on `'vizdoom import failed'` / `'vizdoom init failed'` substrings. Those literals exist at `doom_foxglove/engine.py:384` and `engine.py:396`, but the contract never quotes them, so the check is coupled to source text the evaluator is not told to verify. It fails safe on rewording, but the coupling is invisible and a note like `"vizdoom import failed: <hardcoded>"` would pass.

**Amendment required.** Append to the HL-01 check:

> Quote the exact literals `f"vizdoom import failed: {exc}"` and `f"vizdoom init failed: {exc}"` in `try_vizdoom` in `doom_foxglove/engine.py`. If either literal is absent from source, the substring check is void — FAIL.

## C-5 — HL-02: `DOOM_IWAD=doom2.wad` does not fail anything

**Attack confirmed.** `doom_foxglove/iwad.py:18-20` prepends `DOOM_IWAD` / `FREEDOOM1_WAD` to the candidate list with no name check, and `engine.py:308-310` even special-cases `doom2.wad` → MAP01. The item text asserts "The IWAD is Freedoom … or shareware `doom1.wad`," yet with `DOOM_IWAD=/path/to/doom2.wad` the resolved IWAD is a commercial WAD and no check fails. (A user pointing the env var at their own WAD is not redistribution, so the fix is to scope the claim to default resolution — not to ban the override.)

**Amendment required.** Append to the HL-02 check:

```sh
$PY -c "
import os
os.environ.pop('DOOM_IWAD', None)
os.environ.pop('FREEDOOM1_WAD', None)
from doom_foxglove.iwad import find_iwad
p = find_iwad()
assert p is not None, 'no IWAD resolved with env unset'
assert p.name.lower() in ('freedoom1.wad', 'freedoom.wad', 'freedoom2.wad', 'doom1.wad'), p
print('HL-02 default iwad', p)
"
```

And amend the item text with: "A user setting `DOOM_IWAD` to their own WAD is a user action outside this contract; the shipped default resolution (env unset) must resolve only to Freedoom or shareware `doom1.wad`."

## C-6 — HL-05: local JPEG bytes checked, on-wire schema never asserted

**Attack confirmed.** The check encodes a frame locally via `encode_jpeg` and opens it with PIL, and asserts only `getattr(ch, 'topic', …)` on the channel. The `foxglove.CompressedImage` schema is implicit in `camera_channel()` returning `CompressedImageChannel` (`doom_foxglove/server.py:146-149`) and is never asserted. HL-10 item 2 covers the advertised schema, but HL-10 is an open gap; HL-05 must stand alone.

**Amendment required.** In the HL-05 check, replace the channel lines with:

```python
from foxglove.channels import CompressedImageChannel
ch = camera_channel()
assert isinstance(ch, CompressedImageChannel), type(ch)
assert getattr(ch, 'topic', None) == CAMERA_TOPIC
```

## C-7 — HL-12: pass conditions are unanchored prose, easy to rubber-stamp

**Attack confirmed (minor).** Step 2 requires stdout to "mention that 8765 was busy and that the live default remains 8765" with no exact strings; step 4 accepts "a bind / 'already in use' error" loosely. The product emits stable text — `smoke.py:128-131` prints `SMOKE note: 8765 was busy; live server still defaults to ws://127.0.0.1:8765`, and eval E-04 recorded `Failed to bind port: Address already in use` — so anchor to it.

**Amendment required.** Replace steps 2 and 4 with:

> 2. Run `./smoke`. If the bound port is not 8765, stdout must contain both substrings `was busy` and `ws://127.0.0.1:8765` (quote the line). If the bound port is 8765, this leg passes.
> 4. If 8765 is occupied: `$PY -m doom_foxglove` must exit non-zero and its output must match `(?i)bind|already in use` (quote the line; do not leave the process running). If 8765 is free: quote `main()` in `doom_foxglove/server.py` calling `start_ws` without `fallback_if_busy=True`.

## C-8 — HL-13: "canvas next to a negation" is undefined

**Attack confirmed (minor).** "The word `canvas` next to a negation such as `not` / `does not` / `never`" — "next to" has no definition (same line? same sentence? within k words?). The string-presence list itself is mechanical and stays. The README currently satisfies the intent with `README.md:6` ("This repo does not draw the game in a host canvas.").

**Amendment required.** Replace the canvas sentence of the HL-13 check with:

> Quote the README sentence forbidding a host canvas (currently `This repo does not draw the game in a host canvas.`). `rg -in 'does not draw.*canvas|no host canvas|not a [a-z ]*canvas|never [a-z ]*canvas' README.md` must print at least one line.

---

## Summary for the planner

| # | Item | Amendment |
|---|---|---|
| C-1 | HL-09 | Hero-scoped smoke (`--hero` or stdout attribution); deterministic always-required negative leg |
| C-2 | HL-10 | Strike option B; name `foxglove.sdk.v1`; fixed `WIRE CHECK` line format; counts via `on_message_data` |
| C-3 | HL-06/07 | Add engine pose-delta (move + turn) and ATTACK/USE button-availability assertions |
| C-4 | HL-01 | Quote the two exact note literals in `engine.py`; absence voids the substring check |
| C-5 | HL-02 | Add env-unset default-resolution check; scope the claim away from user `DOOM_IWAD` override |
| C-6 | HL-05 | Assert `isinstance(ch, CompressedImageChannel)` |
| C-7 | HL-12 | Exact stdout substrings (`was busy`, `ws://127.0.0.1:8765`) and `(?i)bind\|already in use` on the loud-fail leg |
| C-8 | HL-13 | Replace "next to a negation" with a quoted sentence plus a fixed `rg` pattern |

This critic did not edit `contract.md`, did not tick any checkbox, and did not touch `doom_foxglove/`.

---

# Re-gate — 2026-09-18 (critic, kimi-k3-high)

**Target:** amended `contract.md` C-1…C-8.
**Verdict: FAIL — 2 remaining amendments (R-1, R-2). Both are one-line; everything else gates clean.**

## Amendment application audit (all verified against source, not the planner's log)

| # | Applied? | Verification |
|---|---|---|
| C-1 | Yes | HL-09 check is `./smoke --hero` + exit 0 + stdout substrings; `_fail` negative leg always required (`smoke.py:39-41` returns 1, so the leg is runnable today); dep-less leg gated on a mechanical premise. The kept busy-port sentence is attribution-only — the HL-09 check never inspects a port, so it waives nothing. OK. |
| C-2 | Yes | Option B struck (`doom_foxglove.wire_check` explicitly insufficient); `foxglove.sdk.v1` named; `WIRE CHECK capability=… cmd_vel=<n> buttons=<n>` fixed with counts ≥ 1; FAIL conditions (`apply_raw`-only injection, counts without a socket, proof outside repo) are all quotable. OK. |
| C-3 | Yes | Pose-delta blocks appended to HL-06/HL-07; planner's added `from doom_foxglove.engine import make_engine` is present in both `$PY -c` blocks, so they run as written. Symbols verified: `PoseState(x,y,z,yaw)`, `VizDoomEngine._button_names`, `FallbackEngine.step` moves `_x`/`_heading` (`engine.py:76-81`) so the assertions are backend-agnostic. OK. |
| C-4 | Yes | Both literals exist verbatim: `engine.py:384` `f"vizdoom import failed: {exc}"`, `engine.py:396` `f"vizdoom init failed: {exc}"`. OK. |
| C-5 | Yes | Env-unset `find_iwad()` block present; item text scopes user `DOOM_IWAD` override out. `find_iwad` exists (`iwad.py:46-50`). OK. |
| C-6 | Yes | `isinstance(ch, CompressedImageChannel)` in HL-05; `camera_channel()` returns exactly that (`server.py:146-149`). OK. |
| C-7 | Yes | HL-12 steps 2/4 anchored: `was busy` + `ws://127.0.0.1:8765` match the product's emitted line (`smoke.py:128-131`); `(?i)bind\|already in use` matches the loud-fail path (`server.py:119-122` re-raises when `fallback_if_busy=False`). OK. |
| C-8 | Yes | Quoted sentence matches `README.md:5` verbatim; the `rg` pattern prints 3 lines today. OK. |

Unchanged items re-spot-checked: HL-03 (`__init__.py:5-6`, `server.py:109`), HL-04 (`server.py:112-113`), HL-08 (`engine.py:294` `set_window_visible(False)`), HL-11, HL-14 — all still mechanical.

## R-1 — HL-12 step 2 re-couples to 02 artifacts (C-1 defect class, surviving)

**Attack confirmed.** Step 2 says "Run `./smoke`" — the bare command. But `smoke.py:107-109` runs `_check_layouts()` *before* any bind, and `_check_layouts()` (`smoke.py:44-70`) fails unless `layouts/Play.json` and `layouts/Debug.json` exist with 02 panels. So a 02 regression (or a tree without `layouts/`) kills smoke before it binds: no bound port, neither branch of step 2 ("not 8765" / "is 8765") applies, the leg is unevaluable — and under "an unrun check is a fail," HL-12 FAILs for a 02 reason. That contradicts the contract's own header ("Extra map/TF/entity/layout assertions inside `./smoke` … do not FAIL an HL item") and is precisely the coupling C-1 was written to kill. C-1 gave us `--hero`; HL-12 step 2 must use it.

**Amendment required.** In HL-12 step 2, replace "Run `./smoke`." with "Run `./smoke --hero`." (The port behavior under test — `fallback_if_busy=True` at the smoke call site, the busy-note line — is identical in hero mode; the generator implementing HL-09's `--hero` split must keep the bind and the note on that path.)

## R-2 — HL-13's final sentence is unanchored prose (same item C-8 just fixed)

**Attack confirmed (minor).** After the mechanical string list, the quoted canvas sentence, and the `rg` pattern, the check ends with: "It names Freedoom or shareware and tells the reader not to copy a commercial `doom.wad`." No string, no pattern, no named quote anchors either clause — "shareware" is not even in the required-string list, and "tells the reader not to copy" is a judgment call on phrasing. The product satisfies the intent today (`README.md:18`: "Do not copy a commercial `doom.wad` / `doom2.wad` into this tree."), so anchor to it exactly as C-8 anchored the canvas sentence.

**Amendment required.** Replace that final sentence of the HL-13 check with:

> `rg -in 'do not copy|commercial' README.md` must print at least one line (currently `README.md:18`). Quote the line.

## Summary for the planner

| # | Item | Amendment |
|---|---|---|
| R-1 | HL-12 | Step 2 runs `./smoke --hero`, not bare `./smoke` — kills the residual 02 coupling in the port leg |
| R-2 | HL-13 | Anchor "do not copy a commercial doom.wad" with a fixed `rg` pattern plus a quoted line |

Everything else in C-1…C-8 verified applied and mechanical. With R-1/R-2 applied, every HL item is reproducible from a clean shell. This critic did not edit `contract.md`, did not tick any checkbox, and did not touch `doom_foxglove/`. Harness note (not part of this verdict): `validate.py --harness` reports 15 H-17 failures, all inside `02-robotics-layout/progress.md` frontmatter — 02's hygiene issue, not a 01 gate blocker; hand to the librarian.

---

# Re-gate 2 — 2026-09-18 (critic, kimi-k3-high)

**Target:** amended `contract.md` R-1/R-2 (on top of verified C-1…C-8).
**Verdict: PASS. The contract gates. A generator may start.**

## R-amendment application audit (verified against source, not the planner's log)

| # | Applied? | Verification |
|---|---|---|
| R-1 | Yes | HL-12 step 2 now reads "Run `./smoke --hero`." — the bare-`./smoke` 02 coupling (`smoke.py:107-109` `_check_layouts()` before bind) can no longer make the port leg unevaluable. The leg stays self-enforcing: if `--hero` drops the bind or the busy-note, the substring check fails. OK. |
| R-2 | Yes | HL-13 check now requires `rg -in 'do not copy|commercial' README.md` to print ≥ 1 line plus the quoted line. Ran the pattern: prints `README.md:18`, and the quoted sentence `Do not copy a commercial `doom.wad` / `doom2.wad` into this tree.` is verbatim in that line. The canvas `rg` pattern still prints 3 lines (README.md:5, 22, 85). OK. |

## Full-contract softness sweep (C-1…C-8 + R-1/R-2, all 14 items)

- HL-01: literals quoted, substring check voided on absence — mechanical.
- HL-02: env-unset `find_iwad()` block + item text scoping user `DOOM_IWAD` out — mechanical.
- HL-03/HL-04: quoted constants and call-site quotes, empty-`rg` legs — mechanical.
- HL-05: `isinstance(ch, CompressedImageChannel)` + JPEG magic bytes + PIL size/format — mechanical.
- HL-06/HL-07: dict-mapping assertions plus engine pose-delta (move + turn) and ATTACK/USE button-availability blocks, imports present in-block — runnable as written, backend-agnostic.
- HL-08: quoted `binary_buttons` + empty-`rg` mouselook leg + quoted `set_window_visible(False)` — mechanical.
- HL-09: `./smoke --hero` positive leg with fixed stdout substrings; `_fail` negative leg always required; dep-less leg gated on a mechanical premise (`python3 -c 'import numpy'` exit non-zero) — no escape hatch.
- HL-10: option B struck; `foxglove.sdk.v1` named; fixed `WIRE CHECK` line with counts ≥ 1; quotable FAIL conditions (`apply_raw`-only, counts without socket, proof outside repo) — mechanical.
- HL-11: callable assertions plus no-raise invocation — mechanical.
- HL-12: quoted `fallback_if_busy` both sides; step 2 hero-scoped with exact substrings; step 3 `lsof` recorded as note; step 4 fixed regex `(?i)bind|already in use` — mechanical.
- HL-13: fixed string list, quoted canvas sentence, two fixed `rg` patterns, quoted commercial-WAD line — mechanical.
- HL-14: fixed `rg` with explicit glob exclusions, "must print nothing" — mechanical.

No new softness introduced by the R-1/R-2 edits. Every check is reproducible from a clean shell at `$ROOT`; every prose claim is anchored to a quoted literal, a fixed pattern, or an exit code.

This critic did not edit `contract.md`, did not tick any checkbox, and did not touch `doom_foxglove/`. Next: Grok generator implements the remaining product gaps — HL-09 `--hero` split (keeping the bind and busy-note on that path), HL-10 in-smoke WIRE CHECK socket proof, HL-11 `on_subscribe`/`on_unsubscribe`, and the HL-06/07 pose-delta assertions must then pass as written. Generator does not tick boxes; Kimi evaluator re-runs the gated checks after.

---

# Re-gate 3 — 2026-09-18 (critic, kimi-k3-high)

**Target:** evaluator amendments E-R1 (HL-05 topic callable) and E-R2 (HL-14 node_modules glob), applied by the planner to `contract.md`.
**Verdict: PASS. Both amendments are mechanical; both amended checks run clean from a clean shell.**

## E-amendment application audit (re-run verbatim, not taken from the planner's log)

| # | Applied? | Verification |
|---|---|---|
| E-R1 (HL-05) | Yes | The amended check replaces the property assertion with `_topic = ch.topic; assert (_topic() if callable(_topic) else _topic) == CAMERA_TOPIC`. Ran the full amended `$PY -c` block verbatim from `$ROOT`: exit 0, stdout `HL-05 vizdoom (320, 200) JPEG hz 35`. The callable-safe form is not softness: the asserted equality is on the resolved string value against `CAMERA_TOPIC`, so a wrong topic still fails; it only tolerates the SDK exposing `topic` as either method or property. All other assertions (isinstance `CompressedImageChannel`, `(320, 200, 35)` constants, frame `(200, 320, 3)`, JPEG magic `ff d8`, PIL `(320, 200) JPEG`) unchanged and passing. |
| E-R2 (HL-14) | Yes | The rg exclusion list now includes `--glob '!**/node_modules/**'`. Ran the amended rg verbatim: prints nothing, `rg` exit 1 — "must print nothing" holds. The added glob is the same vendored-tree class as the already-excluded `.venv`; it does not mask product code (eval.md verified zero product-file matches with node_modules filtered). FAIL condition (any product file drawing into a browser/OS canvas) is unchanged. |

No new softness introduced by either edit. Both items are now reproducible from a clean shell at `$ROOT` and the product satisfies them today.

This critic did not edit `contract.md`, did not tick any checkbox, and did not touch `doom_foxglove/`. Next: Kimi evaluator re-runs HL-05 and HL-14 only and ticks those two boxes if the checks pass.
