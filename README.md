# Foxglove DOOM

Teleoperate a marine the way Foxglove teleoperates a robot. A ViZDoom process is the fake robot. The Foxglove SDK WebSocket is the live connection. The framebuffer is `/doom/camera`. The Teleop panel publishes Twist on `/cmd_vel`. The WAD occupancy grid, player TF, and entity cubes land in a stock 3D panel.

The picture must come through a Foxglove Image panel. This repo does not draw the game in a host canvas.

## Requirements

- Python 3.10–3.13 recommended. ViZDoom currently ships wheels for those; system Python 3.14 on this Mac may not. The smoke command in this README uses a 3.12 venv.
- `foxglove-sdk`, `pillow`, `numpy`
- ViZDoom (preferred). On macOS, if `pip install vizdoom` tries a source build:

  ```sh
  brew install cmake boost sdl2 openal-soft
  pip install vizdoom
  ```

- A legal IWAD: **Freedoom** (`freedoom1.wad` for E1M1) or the shareware `doom1.wad`. Do not copy a commercial `doom.wad` / `doom2.wad` into this tree.

The smoke command will try to download official Freedoom 0.13.0 into `wad/freedoom1.wad` if none is found. You can also set `DOOM_IWAD` to a Freedoom or shareware file.

If ViZDoom cannot import or `game.init()` fails, the server still comes up and smoke still exits 0 using a labeled 320x200 framebuffer published on the same `/doom/camera` topic. That fallback is a CompressedImage, not a canvas. Prefer fixing the ViZDoom install.

## Install

From the repository root:

```sh
# recommended: Python 3.12 (ViZDoom wheels)
uv venv --python 3.12 .venv
source .venv/bin/activate
uv pip install foxglove-sdk pillow numpy
uv pip install vizdoom   # optional but preferred
```

Without `uv`:

```sh
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install vizdoom
```

## Smoke

One command from the repository root. Exits 0 on success, non-zero on failure. Boots the WebSocket, steps several ticks, publishes a JPEG on `/doom/camera`, accepts a `geometry_msgs/Twist` on `/cmd_vel`, and also publishes `/doom/map`, `/tf`, `/doom/entities`, `/doom/player`, and at least one `/doom/log` line.

```sh
./smoke
```

Equivalent: `PYTHONPATH=. .venv/bin/python -m doom_foxglove.smoke`

The live port is `ws://localhost:8765`. If that port is already taken (another Foxglove SDK process), smoke binds an ephemeral port, still exercises the topics, prints the bound URL, and exits 0. `python -m doom_foxglove` still defaults to 8765 and will fail loudly if that port is occupied.

Skip the Freedoom download with `./smoke --no-fetch-iwad`.

## Run the live server

```sh
source .venv/bin/activate
PYTHONPATH=. python -m doom_foxglove --fetch-iwad
```

Listens on `ws://localhost:8765` with `ClientPublish` enabled. The same `channel.log()` calls also write an MCAP sidecar under `recordings/doom-<utc-timestamp>.mcap`. Pass `--no-record` to skip the file, or `--recording path.mcap` to pick the path.

- `/doom/camera` — `foxglove.CompressedImage` JPEG, about 320x200, about 35 Hz
- `/doom/map` — `foxglove.Grid` occupancy of the WAD / automap, once per level, frame `map`
- `/tf` — `foxglove.FrameTransforms` `map` → `base_link` from ViZDoom pose/angle
- `/doom/entities` — `foxglove.SceneUpdate` (monsters, items, projectiles as cubes; empty update is still published)
- `/doom/player` — compact JSON `{ health, armor, ammo, weapon, tick, dead }`
- `/doom/log` — `foxglove.Log` pickups, deaths, and level messages (human-readable; Log panel)
- `/doom/events` — JSON `{ kind, message, tick, map }` with `kind` one of `death`, `weapon`, `level`, `pickup`. Same moments as the log, tagged so Replay can scrub. `level` covers entering a map and level complete.
- `/cmd_vel` — `geometry_msgs/Twist` from Teleop (`linear.x` forward/back, `angular.z` turn, optional `linear.y` strafe; zero on stop)
- `/doom/buttons` — JSON `{ "fire": true, "use": false, "weapon": 2 }` for shoot / use / weapon select

## Open Foxglove (Image + 3D + Teleop + Gauges)

1. Start the live server (`PYTHONPATH=. python -m doom_foxglove --fetch-iwad`).
2. Open the Foxglove app (or https://app.foxglove.dev on localhost).
3. Open connection → **Foxglove WebSocket** → `ws://localhost:8765`.
4. Import a layout: **Layouts → Import layout from file** and choose `layouts/Play.json` (camera + teleop + health/armor/ammo gauges) or `layouts/Debug.json` (adds 3D map, health plot, log, raw `/doom/player`).
5. If you would rather add panels by hand: Image on `/doom/camera`, Teleop on `/cmd_vel` with stop-on-release, three Gauge panels on `/doom/player.health`, `/doom/player.armor`, `/doom/player.ammo`, and a 3D panel following `base_link` with `/doom/map` and `/doom/entities` visible.

You should see the marine's view in Image, the occupancy grid and entity cubes in 3D, and the D-pad should move the marine. There is no custom `.foxe` HUD and no host canvas.

Regenerate the JSON with `PYTHONPATH=. python -m doom_foxglove.layouts_export`.

## Replay an MCAP

Live sessions already write a sidecar under `recordings/`. Headless proof:

```sh
./smoke-replay
```

That records 8 ticks to `recordings/smoke.mcap`, asserts the file exists and contains `/doom/camera`, `/doom/map`, `/tf`, `/doom/entities`, `/doom/player`, and `/doom/log`, then exits 0. If port 8765 is busy it binds an ephemeral port the same way `./smoke` does.

Tagged events (deaths, weapon pickups, level enter/complete) are a separate extras smoke:

```sh
./smoke-events
```

That records 8 ticks to `recordings/smoke-events.mcap`, asserts at least one `/doom/events` JSON message with `kind` in `death|weapon|level|pickup` (idle reset always yields `level` / entering the map), and exits 0. Equivalent: `PYTHONPATH=. .venv/bin/python -m doom_foxglove.smoke_events`

To open a recording in Foxglove (desktop app or https://app.foxglove.dev):

1. **File → Open local file** (or drag the `.mcap` onto the window) and choose `recordings/smoke.mcap` or a `recordings/doom-*.mcap` from a live run.
2. **Layouts → Import layout from file** and choose `layouts/Replay.json`.
3. Use Foxglove's playback bar (play, pause, scrub). Replay hides Teleop; camera, 3D, gauges, and log stay. There is no cloud share link in v1.

The embed host in `web/` stays live-only. Replay is a file in the Foxglove app, not a rewrite of that page. `/doom/events` is in the MCAP; the Replay layout already has a Log panel on `/doom/log`. Add a Raw Messages panel on `/doom/events` if you want to scrub by `kind`.

## Ask Foxglove (copy-paste)

No custom agent ships in this repo. Open a recording (`recordings/doom-*.mcap` or `recordings/smoke-events.mcap`) in the Foxglove app with `layouts/Replay.json`, then paste one of these into the built-in agent / MCP box.

**When did health drop?**

```
Using /doom/player.health, /doom/events (kind=pickup or death), and /doom/log, when did health drop, and what happened in the two seconds before each drop? Give timestamps I can scrub to.
```

**Why did I die?**

```
Find /doom/events where kind=death (and the matching /doom/log line). Using /doom/player, /doom/entities, and health/ammo around that timestamp, why did I die? Point me at the scrub time.
```

**Build a layout for weapons**

```
Build a Foxglove layout that plots /doom/player.weapon and /doom/player.ammo vs time, shows /doom/events filtered to kind=weapon, keeps the Image panel on /doom/camera, and leaves Teleop hidden for replay.
```

The embed page at `web/` does not include an agent. Use these prompts in the Foxglove app against a Replay MCAP. Details: `web/README.md`.

## Not in this slice

Skipped (needs a fleet or a second playthrough, not this extras cut): remote-access gateway, comparison mode UI, cloud share links, ViZDoom policy vs human. Map-panel GPS fakery, audio, and mouse-look stay off-camera.

## Embedded Foxglove (host page)

The kiosk/public surface lives in `web/`. It embeds Foxglove (`@foxglove/embed`) with a **parent-owned live WebSocket** so the iframe does not have to guess CORS. WASD + Space `setKeybindings` publish the same `/cmd_vel` Twist and `/doom/buttons` fire messages as Teleop. Teleop stays in the layout. The game is not drawn on a host canvas.

Foxglove embed needs a **secure context** (HTTPS or localhost) and a Pro-capable org sign-in.

Two terminals from the repository root:

```sh
# terminal 1 — live fake robot
source .venv/bin/activate
PYTHONPATH=. python -m doom_foxglove --fetch-iwad
```

```sh
# terminal 2 — host page (http://localhost:5173 is a secure context)
cd web
npm install --no-audit --no-fund
npm run dev
```

Open [http://localhost:5173/](http://localhost:5173/). Play / Debug buttons force-load `layouts/Play.json` and `layouts/Debug.json`.

If port **8765 is already taken**, the Python server still defaults to 8765 and fails loudly. Bind another port and point the page at it:

```sh
PYTHONPATH=. python -m doom_foxglove --fetch-iwad --port 8766
# then open http://localhost:5173/?ws=ws://localhost:8766
```

Headless embed check (typecheck + production build, no browser): `./web/check`

More detail: `web/README.md`.
