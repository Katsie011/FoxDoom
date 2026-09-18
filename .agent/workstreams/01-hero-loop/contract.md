# Contract — 01-hero-loop

**Workstream:** `01-hero-loop`
**Item-id prefix:** `HL-`
**KG node:** `ws_01_hero_loop`
**Capability:** `cap_live_ws_camera_teleop`
**Status:** awaiting critic re-gate of E-R1/E-R2 (HL-05 topic callable-safe; HL-14 node_modules glob). C-1…C-8 + R-1/R-2 already applied. Product code already exists; this planner applied evaluator amendments and does not grade.

Source of truth for phase scope: `.agent/GOAL.md` (`cap_live_ws_camera_teleop`) and `.agent/workstreams/01-hero-loop/PLAN.md`. This contract does not rewrite either.

## How this contract is graded

The evaluator (kimi-k3-high) is told the hero loop is broken and must prove it. For every `HL-nn` item it must run the stated **Check** from a clean shell at the repo root, or quote the exact file text the check names. "Looks fine" is a fail. An unrun check is a fail.

- Repo root is `$ROOT` (`/Users/michael/Documents/foxglove/work/doom`). Every command below is run after `cd "$ROOT"`.
- `$PY` is `$ROOT/.venv/bin/python` when that file is executable, otherwise `python3`. Always `export PYTHONPATH="$ROOT"`.
- Smoke is `./smoke` (equivalent: `$PY -m doom_foxglove.smoke`). HL-09 grades `./smoke --hero`. HL-10 grades the wire proof inside `./smoke` (not a second module).
- An item is **PASS** only if its check succeeds. Checkboxes below start unchecked. **Only the evaluator ticks `- [ ]`.** The generator must not tick boxes, must not edit this file, and must not append `verified` / `failed` onto `ContractItem` nodes.
- Reuse of `.agent/workstreams/01-hero-loop/eval.md` is allowed for unchanged file-quote checks. Runtime checks (`./smoke`, `$PY -c …`) must be re-run in the eval that ticks the box. A `/tmp` helper the evaluator wrote is not an in-repo check (see HL-10).
- Occupied `ws://localhost:8765` is an environment note, not a product FAIL (HL-12).
- `02-robotics-layout` has already started in `doom_foxglove/` and `layouts/`. Extra map/TF/entity/layout assertions inside `./smoke` or README do not bring those topics into this contract, and do not FAIL an HL item. Missing 02 layouts or 02 topics also do not FAIL HL-09: that item uses `./smoke --hero`.

---

## A. Engine and IWAD

### HL-01 — Engine is ViZDoom when the package imports

- [x] The live engine is ViZDoom (`dec_vizdoom_engine`), not chocolate-doom, doomgeneric, or a from-scratch WAD parser. `make_engine(prefer_vizdoom=True)` uses backend `vizdoom` and map `E1M1` whenever `import vizdoom` succeeds and `game.init()` succeeds. A labeled 320×200 fallback framebuffer is allowed only when that import or init fails; that case is risk `vizdoom_macos_build`, not an HL-01 FAIL. FAIL if vizdoom imports and inits and smoke/server still choose `fallback` without an explicit opt-out.

**Check:**

```sh
$PY -c "
from doom_foxglove.engine import make_engine
eng, info = make_engine(fetch_iwad=False, prefer_vizdoom=True)
print('backend', info.backend)
print('map', info.map_name)
print('iwad', info.iwad)
print('note', info.note)
eng.close()
if info.backend == 'fallback' and 'vizdoom import failed' not in info.note and 'vizdoom init failed' not in info.note:
    raise SystemExit('fallback without a vizdoom import/init failure: %s' % info.note)
if info.backend == 'vizdoom' and info.map_name != 'E1M1':
    raise SystemExit('expected E1M1, got %s' % info.map_name)
"
```

Also: `rg -n 'chocolate-doom|doomgeneric' doom_foxglove --glob '*.py'` is empty. Quote `class VizDoomEngine` and `backend = "vizdoom"` in `doom_foxglove/engine.py`.

Quote the exact literals `f"vizdoom import failed: {exc}"` and `f"vizdoom init failed: {exc}"` in `try_vizdoom` in `doom_foxglove/engine.py`. If either literal is absent from source, the substring check is void — FAIL.

### HL-02 — Freedoom or shareware only; no commercial WAD in the tree

- [x] The IWAD is Freedoom (`freedoom1.wad` for E1M1) or shareware `doom1.wad`. The tree does not contain a commercial `doom.wad` / `doom2.wad`. Fetch, if any, is official Freedoom 0.13.0. VizDoom-package-bundled Freedoom under `.venv` is legal and is not "shipping a commercial WAD." A user setting `DOOM_IWAD` to their own WAD is a user action outside this contract; the shipped default resolution (env unset) must resolve only to Freedoom or shareware `doom1.wad`.

**Check:**

```sh
# no commercial WAD outside the venv / git
find . \( -path './.venv' -o -path './.git' \) -prune -o -iname '*.wad' -print
```

FAIL if any printed path is named `doom.wad` or `doom2.wad` (case-insensitive). `freedoom1.wad`, `freedoom2.wad`, and shareware `doom1.wad` are allowed. `wad/` may be empty if the vizdoom package supplies Freedoom.

Quote `FREEDOOM_ZIP_URL` in `doom_foxglove/iwad.py` — it must be the official `freedoom/freedoom` v0.13.0 GitHub release, not a commercial mirror. Quote `_candidate_paths` — default names are Freedoom or `doom1.wad` only.

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

---

## B. WebSocket and topics

### HL-03 — Default live URL is ws://localhost:8765

- [x] The live server defaults to Foxglove SDK WebSocket `ws://localhost:8765` (host `127.0.0.1` or `localhost`, port `8765`). Not rosbridge, not a custom protocol, not LeRobot `--display_mode=foxglove`.

**Check:** quote `DEFAULT_HOST` and `DEFAULT_PORT = 8765` in `doom_foxglove/__init__.py`. Host must be `127.0.0.1` or `localhost`. Quote `foxglove.start_server` in `doom_foxglove/server.py`. `rg -n 'rosbridge|rospy|display_mode=foxglove' doom_foxglove --glob '*.py'` is empty.

### HL-04 — ClientPublish is enabled with JSON client encoding

- [x] The server is started with `Capability.ClientPublish` and `supported_encodings` that include `json`, so a Foxglove Teleop panel can publish.

**Check:** quote the `foxglove.start_server(...)` call in `doom_foxglove/server.py`. It must pass `capabilities=[Capability.ClientPublish]` (or a list containing that capability) and `supported_encodings` containing `"json"`. Camera schema encoding may be protobuf; that does not FAIL this item.

### HL-05 — `/doom/camera` is foxglove.CompressedImage JPEG 320×200 at 35 Hz

- [x] Topic `/doom/camera` publishes `foxglove.CompressedImage`, JPEG, 320×200. Tick rate is 35 Hz (`TICK_HZ = 35`); `run_loop` paces to `1.0 / hz`.

**Check:**

```sh
$PY -c "
from io import BytesIO
from PIL import Image
from doom_foxglove import CAMERA_TOPIC, SCREEN_HEIGHT, SCREEN_WIDTH, TICK_HZ
from doom_foxglove.engine import make_engine
from doom_foxglove.jpeg import encode_jpeg
from doom_foxglove.teleop import Command
from doom_foxglove.server import camera_channel
assert CAMERA_TOPIC == '/doom/camera'
assert (SCREEN_WIDTH, SCREEN_HEIGHT, TICK_HZ) == (320, 200, 35)
from foxglove.channels import CompressedImageChannel
ch = camera_channel()
assert isinstance(ch, CompressedImageChannel), type(ch)
_topic = ch.topic
assert (_topic() if callable(_topic) else _topic) == CAMERA_TOPIC
eng, info = make_engine(fetch_iwad=False, prefer_vizdoom=True)
eng.reset()
frame = eng.step(Command())
assert frame.shape == (200, 320, 3), frame.shape
jpeg = encode_jpeg(frame)
assert jpeg[:2] == b'\xff\xd8'
im = Image.open(BytesIO(jpeg))
assert im.size == (320, 200) and im.format == 'JPEG', (im.size, im.format)
print('HL-05', info.backend, im.size, im.format, 'hz', TICK_HZ)
eng.close()
"
```

Quote `publish_camera` logging `CompressedImage` with `format="jpeg"` in `doom_foxglove/server.py`. Quote `period = 1.0 / hz` in `run_loop`. Do not require a wall-clock 35 fps measurement over 8 smoke ticks.

### HL-06 — `/cmd_vel` Twist: linear.x, angular.z, optional linear.y, zero stops

- [x] `/cmd_vel` accepts `geometry_msgs/Twist`-shaped JSON. `linear.x` is forward/back, `angular.z` is turn (ROS CCW = turn left), optional `linear.y` is strafe. A zero Twist clears motion (stop-on-release).

**Check:**

```sh
$PY -c "
import json
from doom_foxglove import CMD_VEL_TOPIC
from doom_foxglove.engine import make_engine
from doom_foxglove.teleop import Command, apply_topic, binary_buttons, DEADZONE
assert CMD_VEL_TOPIC == '/cmd_vel'
def tw(x, y, z):
    return json.dumps({'linear':{'x':x,'y':y,'z':0},'angular':{'x':0,'y':0,'z':z}}).encode()
c = apply_topic(CMD_VEL_TOPIC, tw(1, 0, 0), Command())
assert binary_buttons(c)['MOVE_FORWARD'] is True
c = apply_topic(CMD_VEL_TOPIC, tw(-1, 0, 0), Command())
assert binary_buttons(c)['MOVE_BACKWARD'] is True
c = apply_topic(CMD_VEL_TOPIC, tw(0, 0, 1), Command())
assert binary_buttons(c)['TURN_LEFT'] is True
c = apply_topic(CMD_VEL_TOPIC, tw(0, 1, 0), Command())
assert binary_buttons(c)['MOVE_LEFT'] is True
c = apply_topic(CMD_VEL_TOPIC, tw(0, 0, 0), c)
assert abs(c.linear_x) < DEADZONE and abs(c.angular_z) < DEADZONE and abs(c.linear_y) < DEADZONE
print('HL-06 OK')
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
"
```

### HL-07 — `/doom/buttons` JSON `{ fire, use, weapon }`

- [x] `/doom/buttons` accepts JSON `{ fire, use, weapon }` and maps fire/use onto ViZDoom ATTACK/USE. Teleop D-pad is not enough to fire.

**Check:**

```sh
$PY -c "
import json
from doom_foxglove import BUTTONS_TOPIC
from doom_foxglove.engine import make_engine
from doom_foxglove.teleop import Command, apply_topic, binary_buttons
assert BUTTONS_TOPIC == '/doom/buttons'
c = apply_topic(BUTTONS_TOPIC, json.dumps({'fire': True, 'use': False, 'weapon': 2}).encode(), Command())
b = binary_buttons(c)
assert c.fire is True and c.weapon == 2
assert b['ATTACK'] is True and b['USE'] is False and b['weapon'] == 2
c = apply_topic(BUTTONS_TOPIC, json.dumps({'fire': False, 'use': True, 'weapon': None}).encode(), Command())
assert binary_buttons(c)['USE'] is True
print('HL-07 OK')
eng, info = make_engine(fetch_iwad=False, prefer_vizdoom=True)
if info.backend == 'vizdoom':
    assert 'ATTACK' in eng._button_names and 'USE' in eng._button_names, eng._button_names
eng.reset()
frame = eng.step(Command(fire=True, weapon=2))
assert frame.shape == (200, 320, 3)
eng.close()
"
```

### HL-08 — Tank controls; no mouse-look

- [x] Movement is id Tech 1 tank / diff-drive (`dec_tank_controls`). No mouse-look FPS. Available ViZDoom buttons are move/turn/attack/use/weapon, not look-pitch.

**Check:** quote `binary_buttons` in `doom_foxglove/teleop.py` (MOVE_FORWARD/BACKWARD, TURN_LEFT/RIGHT, optional MOVE_LEFT/RIGHT). `rg -n 'LOOK_UP|LOOK_DOWN|mouselook|mouse_look|set_mouse' doom_foxglove --glob '*.py'` is empty. Quote `set_window_visible(False)` in `_configure_vizdoom`.

---

## C. Smoke and the ClientPublish wire path

### HL-09 — One smoke command from repo root

- [x] `./smoke --hero` from `$ROOT` boots a WebSocket, steps N ticks, publishes at least one JPEG on `/doom/camera`, accepts a Twist on `/cmd_vel`, prints a `SMOKE OK` line, and exits 0. `--hero` must skip `_check_layouts()` and the map/tf/entities/player/log requirements, so this item cannot fail on 02 artifacts. It exits non-zero on failure.

**Check:**

```sh
./smoke --hero
echo smoke_exit=$?
```

PASS only if exit is 0 and stdout contains `SMOKE OK`, `/doom/camera`, and `/cmd_vel`. `--hero` must skip `_check_layouts()` and the map/tf/entities/player/log requirements, so HL-09 cannot fail on 02 artifacts. If the process binds a port other than 8765, that is HL-12, not HL-09 FAIL.

Negative path, deterministic, no escape hatch:

```sh
$PY -c "import sys; from doom_foxglove.smoke import _fail; sys.exit(_fail('critic-injected'))"
echo neg_exit=$?
```

must exit 1, and the evaluator quotes `def _fail` returning 1 in `doom_foxglove/smoke.py`. Additionally, when an interpreter without deps exists — proven by quoting `python3 -c 'import numpy'` exiting non-zero — `python3 -m doom_foxglove.smoke --no-fetch-iwad` must also exit non-zero. The `_fail` leg is always required; the dep-less runtime leg is required whenever such an interpreter exists.

### HL-10 — ClientPublish proven over a real socket, not only apply_raw()

- [x] `./smoke` opens a WebSocket client to the port the smoke process bound and proves all four:

  1. Server capability list includes ClientPublish (`clientPublish`).
  2. `/doom/camera` is advertised as `foxglove.CompressedImage`.
  3. Client-published Twist JSON on `/cmd_vel` is applied (`cmd_vel_count` increments) **without** that increment coming from `TeleopListener.apply_raw`.
  4. Client-published `{ fire, use, weapon }` JSON on `/doom/buttons` is applied (`buttons_count` increments) **without** `apply_raw` for that increment.

  Counted Twist/buttons deliveries must arrive through `TeleopListener.on_message_data`, not `apply_raw`. `listener.apply_raw(...)` inside `./smoke` may still exist for latch assertions. It does **not** satisfy this item. A standalone `doom_foxglove.wire_check` module does **not** satisfy this item.

**Check:** `./smoke` stdout contains a line matching `WIRE CHECK capability=clientPublish camera_schema=foxglove.CompressedImage cmd_vel=<n> buttons=<n>` with both counts ≥ 1. `doom_foxglove/smoke.py` (or a helper it imports under `doom_foxglove/`) must open a WebSocket client to the bound port negotiating subprotocol `foxglove.sdk.v1`, and the counted Twist/buttons deliveries must arrive through `TeleopListener.on_message_data`, not `apply_raw`. The evaluator quotes the client code and the WIRE CHECK line. FAIL if the only `/cmd_vel` or `/doom/buttons` injection is `listener.apply_raw(...)`, if the counts exist without a socket, or if the only proof lives outside the repo (`/tmp` or otherwise).

### HL-11 — TeleopListener implements on_subscribe and on_unsubscribe

- [x] `TeleopListener` defines callable `on_subscribe` and `on_unsubscribe` so the Foxglove SDK server does not log `AttributeError: 'TeleopListener' object has no attribute 'on_subscribe'` / `on_unsubscribe` on every subscribe. Methods may no-op. They must not raise `AttributeError`.

**Check:**

```sh
$PY -c "
from doom_foxglove.server import TeleopListener
l = TeleopListener()
assert callable(getattr(l, 'on_subscribe', None)), 'missing on_subscribe'
assert callable(getattr(l, 'on_unsubscribe', None)), 'missing on_unsubscribe'
l.on_subscribe(object(), object())
l.on_unsubscribe(object(), object())
print('HL-11 OK')
"
```

---

## D. Port 8765 and docs

### HL-12 — Busy 8765 is an environment note; smoke may bind ephemeral

- [x] Smoke may bind an ephemeral port when 8765 is taken, still start a ClientPublish server, print the bound URL, and exit 0. Stdout must say that the live default remains `ws://127.0.0.1:8765` (or localhost:8765). The live server (`$PY -m doom_foxglove`) defaults to 8765 **without** that fallback and fails loudly on bind error. `lsof` showing another process on 8765 is **not** an HL FAIL.

**Check:**

1. Quote `fallback_if_busy: bool = False` on `start_ws` in `doom_foxglove/server.py` and `fallback_if_busy=True` at the smoke call site in `doom_foxglove/smoke.py`.
2. Run `./smoke --hero`. If the bound port is not 8765, stdout must contain both substrings `was busy` and `ws://127.0.0.1:8765` (quote the line). If the bound port is 8765, this leg passes.
3. `lsof -nP -iTCP:8765 -sTCP:LISTEN` — record the result. Occupied = environment note, not FAIL.
4. If 8765 is occupied: `$PY -m doom_foxglove` must exit non-zero and its output must match `(?i)bind|already in use` (quote the line; do not leave the process running). If 8765 is free: quote `main()` in `doom_foxglove/server.py` calling `start_ws` without `fallback_if_busy=True`.

### HL-13 — README documents install, smoke, live WS, Image plus Teleop

- [x] `README.md` documents: Python / venv install, ViZDoom notes, legal IWAD (Freedoom or shareware; no commercial WAD), `./smoke`, `python -m doom_foxglove` on `ws://localhost:8765` with ClientPublish, and opening Foxglove to add Image on `/doom/camera` plus Teleop on `/cmd_vel`. It states the picture is not a host canvas. Mentions of Grid/TF/entities/layouts are 02 text and do not FAIL HL-13.

**Check:** `README.md` contains each of these strings: `./smoke`, `python -m doom_foxglove`, `ws://localhost:8765`, `ClientPublish`, `/doom/camera`, `/cmd_vel`, `/doom/buttons`, `Freedoom`, `Teleop`, `Image`. Quote the README sentence forbidding a host canvas (currently `This repo does not draw the game in a host canvas.`). `rg -in 'does not draw.*canvas|no host canvas|not a [a-z ]*canvas|never [a-z ]*canvas' README.md` must print at least one line. `rg -in 'do not copy|commercial' README.md` must print at least one line (currently `README.md:18`). Quote the line: Do not copy a commercial `doom.wad` / `doom2.wad` into this tree.

### HL-14 — No host-canvas renderer

- [x] The marine view is a Foxglove Image panel subscription to `/doom/camera`, not a host `<canvas>` / `getContext` renderer (`dec_no_canvas`). FallbackEngine's labeled framebuffer still goes through `CompressedImage`, not a window.

**Check:**

```sh
rg -n --glob '!*.md' --glob '!.venv/**' --glob '!**/node_modules/**' --glob '!.git/**' --glob '!.agent/**' \
  -e 'getContext\s*\(' -e '<canvas' -e 'HTMLCanvasElement' .
```

Must print nothing. The word `canvas` in comments or README is allowed. Do **not** FAIL this item because `SceneUpdate` / `Grid` / `FrameTransforms` code exists (that is 02). FAIL if any product file draws the framebuffer into a browser or OS canvas.

---

## Out of scope (do not FAIL 01 for these; do not require them)

These belong to later workstreams. Presence (02 has already started) or absence does not decide any HL item.

- Grid / TF / entities / player JSON / log topic / Play and Debug layouts — `02-robotics-layout` (`cap_3d_map_hud`)
- Embed host, WASD keybindings, `@foxglove/embed` — `03-embed-shell` (`cap_embed_page`)
- MCAP record/replay — `04-record-replay` (`cap_mcap_replay`)
- Events, comparison, agent prompts, remote spectator — `05-stunt-extras` (`cap_stunt_extras`)
- Custom `.foxe` HUD, mouse-look FPS, ROS/rosbridge, commercial IWAD redistribution, a general game engine, audio, cloud upload

A generator handed this contract implements only remaining HL gaps (expected: HL-09 `--hero` split, HL-10 in-smoke wire proof, HL-11 listener callbacks). It does not "complete 02" under this id prefix.

## Process (not an HL checkbox)

This file is the critic-gated contract the phase DAG required before generation. Generation preceded the gate; the gate is retroactive. The critic (kimi-k3-high) attacks these items; this planner does not grade them. No generator ticks the boxes above.
