# Embed shell — Foxglove DOOM host page

The public/kiosk surface. Foxglove is the visualization layer (`@foxglove/embed`). This page does **not** draw DOOM on a canvas; the marine’s view is a stock Image panel on `/doom/camera`.

WASD and Space publish the **same topics** as the Teleop panel (`/cmd_vel` Twist, `/doom/buttons` fire). Teleop stays in the layout.

## Requirements

- Node 20+
- The live server from the repo root (`python -m doom_foxglove`)
- A **secure context**: `http://localhost` or HTTPS. `http://127.0.0.1` is also a secure context. A LAN IP over plain HTTP is not.
- Foxglove embed is a Pro feature. Sign into an eligible org when the iframe prompts. Pass `?org=your-org-slug` if you know it.

## Run the page and the DOOM server together

From the **repository root**, two terminals:

```sh
# terminal 1 — fake robot (default ws://localhost:8765)
source .venv/bin/activate
PYTHONPATH=. python -m doom_foxglove --fetch-iwad
```

```sh
# terminal 2 — host page
cd web
npm install --no-audit --no-fund
npm run dev
```

Open [http://localhost:5173/](http://localhost:5173/). That origin is a secure context. Layout buttons force-load `layouts/Play.json` and `layouts/Debug.json`.

### Port 8765 is busy

The Python process still defaults to 8765 and fails loudly if something else (another Foxglove SDK server) already bound it. Pick a free port and point the host at it:

```sh
PYTHONPATH=. python -m doom_foxglove --fetch-iwad --port 8766
```

```sh
# same web/ dev server
open "http://localhost:5173/?ws=ws://localhost:8766"
```

Or set `VITE_FOXGLOVE_WS=ws://localhost:8766` before `npm run dev`. Query `?ws=` wins over the env default.

## What the host does

- Opens the Foxglove WebSocket **in the parent** (`ParentTransportFactory`) so the iframe does not have to guess CORS. If parent-owned live transport is unavailable (unsigned-in iframe, ineligible org), the host falls back to iframe-owned `foxglove-websocket` and opens a **second** parent socket only for WASD publish.
- `selectLayout({ storageKey, opaqueLayout, force: true })` for Play and Debug.
- `setKeybindings` for `KeyW`/`KeyA`/`KeyS`/`KeyD`/`Space`. W/S are `linear.x`, A/D are `angular.z` (tank / Teleop mapping). Space publishes `{ fire: true }` on `/doom/buttons`. The embed API only reports presses, not keyup, so a ~900 ms hold timeout plus parent-window keyup still sends zeros / `fire: false`. Teleop remains the hold-to-move D-pad.

## Headless check (no browser)

From `web/`:

```sh
./check
```

Equivalent: `npm install --no-audit --no-fund && npm run check`. That is `tsc --noEmit` (including a `FoxgloveViewer` options compile check in `src/compile-check.ts`) plus `vite build`.

`@foxglove/embed` 0.79.0 imports a private `@foxglove/common` workspace package that is not on npm. `src/foxglove-common-shim.ts` aliases the one runtime symbol (`toError`) so Vite can bundle.

## Out of scope here

Events, comparison, remote spectator. Replay an MCAP in the Foxglove app with `layouts/Replay.json` (see the repository README); this host stays live-only. Do not add a canvas renderer.

Copy-paste agent prompts (“when did health drop”, “why did I die”, “build a layout for weapons”) live in the repository README. This page does not ship a custom agent.
