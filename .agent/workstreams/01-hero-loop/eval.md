# Eval — 01-hero-loop (gated HL-01…HL-14, adversarial)

**Date:** 2026-09-18
**Evaluator:** kimi-k3-high (did not write this code, did not fix it)
**Target:** `contract.md` HL-01…HL-14 (critic-gated PASS, C-1…C-8 + R-1/R-2). Generator claims: `./smoke --hero` exit 0, WIRE CHECK on `foxglove.sdk.v1`, `on_subscribe`/`on_unsubscribe`, pose-delta present.
**Method:** every mechanical check re-run from a clean shell at `$ROOT` (`/Users/michael/Documents/foxglove/work/doom`), `$PY = .venv/bin/python`, `PYTHONPATH=$ROOT`. This file overwrites the prior stub-era eval.

## Verdict: FAIL — 12 of 14 items pass. Failing ids: HL-05, HL-14.

Both failures are **contract-check defects, not product defects** — the product behavior each item claims is present and verified; the check text as written cannot succeed in this tree. Per the contract ("An item is PASS only if its check succeeds"; unrun/failed check = FAIL) they are not ticked. These need planner/critic amendments, not generator fixes. Details below.

---

## Item results

### HL-01 — PASS

```
$ $PY -c "…make_engine(fetch_iwad=False, prefer_vizdoom=True)…"
backend vizdoom
map E1M1
iwad …/.venv/lib/python3.12/site-packages/vizdoom/freedoom1.wad
note iwad=… map=E1M1
exit=0
```

`rg -n 'chocolate-doom|doomgeneric' doom_foxglove --glob '*.py'` → empty (exit 1).
Quoted: `engine.py:174-175` `class VizDoomEngine:` / `backend = "vizdoom"`. Literals present verbatim: `engine.py:409` `return None, f"vizdoom import failed: {exc}"`, `engine.py:422` `return None, f"vizdoom init failed: {exc}"`.

### HL-02 — PASS

`find . \( -path './.venv' -o -path './.git' \) -prune -o -iname '*.wad' -print` → empty. Env-unset resolution:

```
HL-02 default iwad …/.venv/lib/python3.12/site-packages/vizdoom/freedoom1.wad
exit=0
```

Quoted `iwad.py:12-14`: `FREEDOOM_ZIP_URL = ("https://github.com/freedoom/freedoom/releases/download/v0.13.0/freedoom-0.13.0.zip")` — official Freedoom 0.13.0. Quoted `_candidate_paths` (`iwad.py:17-28`): default names `freedoom1.wad`, `freedoom.wad`, `doom1.wad` only.

### HL-03 — PASS

Quoted `__init__.py:5-6`: `DEFAULT_HOST = "127.0.0.1"`, `DEFAULT_PORT = 8765`. `foxglove.start_server` quoted at `server.py:119`. `rg -n 'rosbridge|rospy|display_mode=foxglove' doom_foxglove --glob '*.py'` → empty (exit 1).

### HL-04 — PASS

Quoted `server.py:119-126`:

```python
return foxglove.start_server(
    name="foxglove-doom",
    host=host,
    port=bind_port,
    capabilities=[Capability.ClientPublish],
    supported_encodings=["json"],
    server_listener=listener,
)
```

### HL-05 — FAIL (check defect; product behavior verified present)

The check as written exits 1:

```
AssertionError   (line 14: assert getattr(ch, 'topic', None) == CAMERA_TOPIC)
```

Root cause: in the installed foxglove SDK, `CompressedImageChannel.topic` is a **bound method**, not a string property. `getattr(ch, 'topic', None)` returns `<built-in method topic of …>`, which never equals `'/doom/camera'`. Verified directly:

```
type <class 'foxglove.channels.CompressedImageChannel'>
topic <built-in method topic of foxglove.channels.CompressedImageChannel object>
topic() -> '/doom/camera'
```

Every other assertion in the check passes when that one line is corrected to `ch.topic() == CAMERA_TOPIC`:

```
HL-05-minus-getattr vizdoom (320, 200) JPEG hz 35
exit=0
```

i.e. `CAMERA_TOPIC == '/doom/camera'`, `(SCREEN_WIDTH, SCREEN_HEIGHT, TICK_HZ) == (320, 200, 35)`, `isinstance(ch, CompressedImageChannel)`, channel constructed with the camera topic (`server.py:157-160` `CompressedImageChannel(topic=CAMERA_TOPIC)`), frame `(200, 320, 3)`, JPEG magic `ff d8`, PIL `(320, 200) JPEG`. Quoted `server.py:151` `format="jpeg"`; quoted `server.py:174` `period = 1.0 / hz if hz > 0 else 0.0`.

**This is a contract bug** (C-6's amended block assumed a property the SDK does not expose), not fixable in product code — the channel already carries the right topic. Needs a planner/critic amendment (e.g. `ch.topic() == CAMERA_TOPIC` or quoting the `topic=CAMERA_TOPIC` construction). Box left unticked per grading rules.

### HL-06 — PASS

```
HL-06 OK
exit=0
```

All Twist mapping assertions (forward/back/turn-left/strafe/zero-stop) plus the C-3 pose-delta block: 20 forward steps moved `pose` (`|Δx|+|Δy| > 0.01`), 10 turn steps changed `yaw > 0.01`, backend `vizdoom`.

### HL-07 — PASS

```
HL-07 OK
exit=0
```

`{fire, use, weapon}` → ATTACK/USE/weapon mapping verified; `'ATTACK' in eng._button_names` and `'USE' in eng._button_names`; `eng.step(Command(fire=True, weapon=2))` returns `(200, 320, 3)`.

### HL-08 — PASS

Quoted `teleop.py:94-106` `binary_buttons` (MOVE_FORWARD/BACKWARD, MOVE_LEFT/RIGHT, TURN_LEFT/RIGHT, ATTACK, USE, weapon). `rg -n 'LOOK_UP|LOOK_DOWN|mouselook|mouse_look|set_mouse' doom_foxglove --glob '*.py'` → empty (exit 1). Quoted `engine.py:320` `game.set_window_visible(False)`.

### HL-09 — PASS

```
$ ./smoke --hero
SMOKE engine backend=vizdoom map=E1M1 iwad=…/freedoom1.wad
SMOKE websocket bound ws://127.0.0.1:54430
SMOKE note: 8765 was busy; live server still defaults to ws://127.0.0.1:8765
WIRE CHECK capability=clientPublish camera_schema=foxglove.CompressedImage cmd_vel=1 buttons=1
SMOKE OK ticks=8 frames=8 topic=/doom/camera cmd_vel=/cmd_vel backend=vizdoom subprotocol=foxglove.sdk.v1
smoke_exit=0
```

Exit 0; stdout contains `SMOKE OK`, `/doom/camera`, `/cmd_vel`. Negative leg: `$PY -c "…sys.exit(_fail('critic-injected'))"` → prints `SMOKE FAIL: critic-injected`, `neg_exit=1`; quoted `smoke.py:40-42` `def _fail(message: str) -> int: … return 1`. Dep-less premise holds: `python3 -c 'import numpy'` → `ModuleNotFoundError`, exit 1; `python3 -m doom_foxglove.smoke --no-fetch-iwad` → `ModuleNotFoundError: No module named 'numpy'`, exit 1. Both negative legs pass.

### HL-10 — PASS

WIRE CHECK line in `./smoke --hero` stdout (quoted above): `capability=clientPublish camera_schema=foxglove.CompressedImage cmd_vel=1 buttons=1`, both counts ≥ 1.

Client code quoted — `doom_foxglove/ws_client.py` (imported by `smoke.py:25`): `SDK_SUBPROTOCOL = "foxglove.sdk.v1"` (line 15); handshake sends `Sec-WebSocket-Protocol: foxglove.sdk.v1` and rejects servers that don't negotiate it (lines 82, 103-106); `prove_client_publish` reads `serverInfo` capabilities and the advertised `/doom/camera` schema, advertises `/cmd_vel` + `/doom/buttons` client channels, sends binary ClientMessageData frames, and reads counts from the listener (lines 219-278).

Counted deliveries arrive through `TeleopListener.on_message_data`: `server.py:71-88` increments `cmd_vel_count`/`buttons_count` only there; `server.py:47-51` `apply_raw` is documented "Does not increment wire counts (HL-10)" and does not. `smoke.py:148-159` calls `prove_client_publish(DEFAULT_HOST, bound, listener)` and `_fail`s on missing capability/schema/counts. No `doom_foxglove.wire_check` module; no `/tmp` proof.

### HL-11 — PASS

```
HL-11 OK
exit=0
```

Quoted `server.py:53-57`: `def on_subscribe(self, client, channel) -> None: return None` / `def on_unsubscribe(…)`. Both callable, invoked with `(object(), object())`, no raise.

### HL-12 — PASS

1. Quoted `server.py:113` `fallback_if_busy: bool = False` on `start_ws`; quoted `smoke.py:126` `fallback_if_busy=True` at the smoke call site.
2. `./smoke --hero` bound 54430 ≠ 8765; stdout line quoted: `SMOKE note: 8765 was busy; live server still defaults to ws://127.0.0.1:8765` — contains both `was busy` and `ws://127.0.0.1:8765`.
3. `lsof -nP -iTCP:8765 -sTCP:LISTEN` → `python3.1 50610 michael … TCP 127.0.0.1:8765 (LISTEN)`. Occupied = environment note, not a FAIL.
4. Occupied leg: `$PY -m doom_foxglove` exited 1 (not left running) with `RuntimeError: FoxgloveError: Failed to bind port: Address already in use (os error 48)` — matches `(?i)bind|already in use`.

### HL-13 — PASS

All ten required strings present in `README.md`: `./smoke`, `python -m doom_foxglove`, `ws://localhost:8765`, `ClientPublish`, `/doom/camera`, `/cmd_vel`, `/doom/buttons`, `Freedoom`, `Teleop`, `Image`. Canvas `rg` pattern prints 3 lines; quoted `README.md:5`: `The picture must come through a Foxglove Image panel. This repo does not draw the game in a host canvas.` `rg -in 'do not copy|commercial' README.md` prints `README.md:18`; quoted: `A legal IWAD: **Freedoom** (`freedoom1.wad` for E1M1) or the shareware `doom1.wad`. Do not copy a commercial `doom.wad` / `doom2.wad` into this tree.`

### HL-14 — FAIL (check defect; zero product-file matches)

The check as written prints 60+ lines, so "must print nothing" does not hold:

```
./web/node_modules/rollup/dist/es/shared/node-entry.js:4497:    HTMLCanvasElement: C,
./web/node_modules/typescript/lib/lib.dom.d.ts:7555–39229:  (TypeScript DOM lib type definitions)
…
hl14_rg_exit=0
```

**Every match is inside `web/node_modules/`** — vendored third-party bundles (rollup, TypeScript `lib.dom.d.ts` / `lib.webworker.d.ts`). Re-running the identical check with node_modules filtered:

```
$ rg … -e 'getContext\s*\(' -e '<canvas' -e 'HTMLCanvasElement' . | rg -v 'node_modules'
product_matches_exit=1   (zero product-file matches)
```

No product file draws the framebuffer into a browser or OS canvas — the item's actual FAIL condition is not met. The contract's exclusion globs (`!*.md`, `!.venv/**`, `!.git/**`, `!.agent/**`) omit `node_modules`, the exact analogue of the already-excluded `.venv`. **Contract bug**, needs a planner/critic amendment (add `--glob '!**/node_modules/**'`). Box left unticked per grading rules.

---

## Summary table

| Item | Verdict | Basis |
|---|---|---|
| HL-01 | PASS | runtime backend=vizdoom E1M1; rg empty; literals quoted |
| HL-02 | PASS | no WADs outside .venv; env-unset resolves freedoom1.wad; URL + candidates quoted |
| HL-03 | PASS | 127.0.0.1:8765 quoted; start_server quoted; rg empty |
| HL-04 | PASS | ClientPublish + json quoted at server.py:119-126 |
| HL-05 | **FAIL** | check asserts `.topic` property; SDK exposes method. Product correct (`topic() == '/doom/camera'`). Contract defect |
| HL-06 | PASS | mapping + pose-delta (move + turn) on vizdoom |
| HL-07 | PASS | buttons mapping + ATTACK/USE in _button_names + fire step |
| HL-08 | PASS | binary_buttons quoted; mouselook rg empty; set_window_visible(False) quoted |
| HL-09 | PASS | `--hero` exit 0 with required substrings; `_fail` leg exit 1; dep-less leg exit 1 |
| HL-10 | PASS | WIRE CHECK line counts 1/1; in-repo `ws_client.py` negotiates foxglove.sdk.v1; counts via on_message_data only |
| HL-11 | PASS | on_subscribe/on_unsubscribe callable, no raise |
| HL-12 | PASS | both fallback_if_busy quotes; busy-note substrings; lsof note; live bind failure exit 1 |
| HL-13 | PASS | all strings + both rg patterns + quoted lines |
| HL-14 | **FAIL** | check prints matches, all in `web/node_modules/`; zero product-file matches. Contract defect (missing node_modules glob) |

## Required amendments (for planner/critic, not generator)

- **E-R1 (HL-05):** replace `assert getattr(ch, 'topic', None) == CAMERA_TOPIC` with `assert ch.topic() == CAMERA_TOPIC` (or quote the `CompressedImageChannel(topic=CAMERA_TOPIC)` construction at `server.py:160`). The current line cannot pass against the installed foxglove SDK regardless of product code.
- **E-R2 (HL-14):** add `--glob '!**/node_modules/**'` to the rg exclusions. `web/node_modules` appeared with the 03 workstream's scaffold and is the same class of vendored tree as the already-excluded `.venv`.

This evaluator did not edit `doom_foxglove/`, did not fix any product code, and ticked only the twelve passed boxes in `contract.md`.

---

# Re-eval — 2026-09-18 (evaluator, kimi-k3-high): HL-05 and HL-14 only

**Gate:** critic Re-gate 3 on E-R1/E-R2 = PASS (`critique.md`). Scope: re-run the two amended checks only; the other 12 ticks from the 2026-09-18 eval are untouched. No product code edited.

## Verdict: PASS — 14 of 14. HL-05 and HL-14 ticked.

### HL-05 — PASS (E-R1 amended check, run verbatim from `$ROOT`)

```
$ $PY -c "…camera_channel(); _topic = ch.topic; assert (_topic() if callable(_topic) else _topic) == CAMERA_TOPIC …"
HL-05 vizdoom (320, 200) JPEG hz 35
hl05_exit=0
```

The callable-safe topic assertion resolves the SDK's bound method to `'/doom/camera'` and passes; all other assertions unchanged and passing (`isinstance(ch, CompressedImageChannel)`, `(320, 200, 35)`, frame `(200, 320, 3)`, JPEG magic `ff d8`, PIL `(320, 200) JPEG`). Quotes re-verified in source: `server.py:151` `format="jpeg"` in `publish_camera`; `server.py:174` `period = 1.0 / hz if hz > 0 else 0.0` in `run_loop`. Box ticked.

### HL-14 — PASS (E-R2 amended check, run verbatim from `$ROOT`)

```
$ rg -n --glob '!*.md' --glob '!.venv/**' --glob '!**/node_modules/**' --glob '!.git/**' --glob '!.agent/**' \
    -e 'getContext\s*\(' -e '<canvas' -e 'HTMLCanvasElement' .
(no output)
hl14_rg_exit=1
```

Prints nothing — "must print nothing" holds with `node_modules` excluded alongside the already-excluded `.venv`. Zero product-file canvas matches; the item's FAIL condition is not met. Box ticked.

This evaluator did not edit `doom_foxglove/`, did not fix any product code, and ticked only HL-05 and HL-14 in `contract.md`.
