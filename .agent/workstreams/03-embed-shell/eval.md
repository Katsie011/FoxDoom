# Eval — 03-embed-shell (ES-01…ES-11)

**Evaluator:** kimi-k3-high (did not write this code, did not author the contract)
**Date:** 2026-09-18
**Graded against:** `.agent/workstreams/03-embed-shell/contract.md` (gated by `critique.md`, PASS)
**Verdict:** **PASS — 11/11.** Every check below was run from `$ROOT` (`/Users/michael/Documents/foxglove/work/doom`) in this eval, or the exact file text is quoted. `./web/check` was re-run in this eval (not reused).

## ES-01 — Host page embeds Foxglove via `@foxglove/embed` — PASS

- `web/package.json` dependencies: `"@foxglove/embed": "^0.79.0"`.
- `web/src/main.ts:1`: `import { FoxgloveViewer } from "@foxglove/embed";`
- `web/src/main.ts:42`: `const viewer = new FoxgloveViewer({`
- Constructor passes `parent` as the `#foxglove` element, not a canvas — `web/src/main.ts:37`: `const parent = requireEl<HTMLElement>("foxglove");` then `web/src/main.ts:43`: `parent,`. `web/index.html:32`: `<main id="foxglove" aria-label="Embedded Foxglove"></main>`.
- `web/index.html:21-22`: `<button type="button" id="layout-play" data-layout="play">Play</button>` / `<button type="button" id="layout-debug" data-layout="debug">Debug</button>`.
- `web/src/main.ts:56-63`: `requireEl("layout-play").addEventListener("click", () => { viewer.selectLayout(layoutParams("play")); …` and the `layout-debug` handler calling `viewer.selectLayout(layoutParams("debug"))`.
- `embed-react` rg allowed-empty; `@foxglove/embed` alone present. PASS.

## ES-02 — Parent-owned live transport; pending Pro plus quoted fallback — PASS

- `web/src/transport.ts:7`: `export function createDoomTransport(publisher: ClientPublisher): ParentTransportFactory {`
- `onOpen` attaches publisher to `socket.send` — `web/src/transport.ts:12-18`: `socket.onopen = () => { onOpen(socket.protocol); publisher.attach((frame) => { if (socket.readyState === WebSocket.OPEN) { socket.send(frame); } }); };`
- `web/src/transport.ts:54-62`: `parentOwnedLiveSource` returns `{ type: "live", protocol: "foxglove-websocket", url, transport }`.
- `web/src/transport.ts:65-71`: `iframeOwnedLiveSource` returns the same shape without `transport`.
- Three-way branch `connectFromCapabilities` in `web/src/main.ts:65-84`:
  1. `"pending"` → `setStatus("Waiting for embed capabilities (sign in if prompted)…"); return;` (lines 72-75) — no `setDataSource` on that turn;
  2. `"available"` → `viewer.setDataSource(parentOwnedLiveSource(wsUrl, transport));` (line 77);
  3. `"unavailable"` → `viewer.setDataSource(iframeOwnedLiveSource(wsUrl)); publisher.connectDirect(wsUrl);` (lines 81-82).
- `web/src/config.ts:5`: `export const DEFAULT_WS_URL = "ws://localhost:8765";`
- `web/src/config.ts:25-27`: `export function readWsUrl(): string { return firstQuery("ws") ?? import.meta.env.VITE_FOXGLOVE_WS ?? DEFAULT_WS_URL; }` — `?ws=` then env then default.
- No browser opened; Pro sign-in not required. PASS.

## ES-03 — Force-load `Play.json` and `Debug.json` — PASS

- Ran: `test -f layouts/Play.json && test -f layouts/Debug.json` → exit 0 (`LAYOUTS EXIST`).
- `web/src/layouts.ts:1-2`: `import playLayout from "../../layouts/Play.json";` / `import debugLayout from "../../layouts/Debug.json";`
- `web/src/layouts.ts:14-26`: `layoutParams("debug")` returns `{ storageKey: DEBUG_STORAGE_KEY, opaqueLayout: debugLayoutData, force: true }`; the play branch returns `{ storageKey: PLAY_STORAGE_KEY, opaqueLayout: playLayoutData, force: true }`. `force: true` on both.
- `web/src/compile-check.ts:19`: `type SelectLayoutParams = Parameters<FoxgloveViewer["selectLayout"]>[0];` and lines 36-37: `export const playSelectLayoutCompileCheck: SelectLayoutParams = layoutParams("play");` / `export const debugSelectLayoutCompileCheck: SelectLayoutParams = layoutParams("debug");`
- `web/src/main.ts:57`: `viewer.selectLayout(layoutParams("play"));` and `web/src/main.ts:61`: `viewer.selectLayout(layoutParams("debug"));`. PASS.

## ES-04 — WASD+Space publish `/cmd_vel` and `/doom/buttons` — PASS

- `web/src/keybindings.ts:168-174`: `doomKeybindings` binds `KeyW` (forward), `KeyA` (left), `KeyS` (back), `KeyD` (right), `Space` (fire).
- `web/src/keybindings.ts:21-28`: `twistFromMotion` — `const linearX = (motion.forward ? 1 : 0) + (motion.back ? -1 : 0);` / `const angularZ = (motion.left ? 1 : 0) + (motion.right ? -1 : 0);` returned as `linear.x` / `angular.z`.
- `web/src/keybindings.ts:30-32`: `buttonsFromMotion` returns `{ fire: motion.fire, use: false, weapon: null }`.
- `web/src/keybindings.ts:133-146`: `HoldController.flush` calls `this.publisher.publishTwist(twist)` and `this.publisher.publishButtons(buttonsFromMotion(this.motion))`.
- `web/src/config.ts:2-3`: `export const CMD_VEL_TOPIC = "/cmd_vel";` / `export const BUTTONS_TOPIC = "/doom/buttons";`
- `web/src/publish.ts:61-83`: `clientAdvertiseJson` — `op: "advertise"`, channel on `CMD_VEL_TOPIC` with `schemaName: "geometry_msgs/Twist"`, channel on `BUTTONS_TOPIC` with `schemaName: "doom.Buttons"`.
- `web/src/compile-check.ts:47-50`: `const advertised = clientAdvertiseJson(); if (!advertised.includes(CMD_VEL_TOPIC) || !advertised.includes(BUTTONS_TOPIC)) { throw new Error("client advertise JSON must name /cmd_vel and /doom/buttons"); }` and line 65: `const needed: ShortcutKey[] = ["KeyW", "KeyA", "KeyS", "KeyD", "Space"];`
- Ran: `rg -n 'mousemove|pointerlock|mouse-look|LOOK_UP|LOOK_DOWN' web/src` → no output, exit 1. PASS.

## ES-05 — Teleop remains in the Play layout — PASS

- Ran: `rg -n '"panelType": "Teleop"' layouts/Play.json` → `31:                "panelType": "Teleop",`
- `web/src/layouts.ts:29-31`: `export function layoutIncludesTeleop(data: unknown): boolean { return JSON.stringify(data).includes("Teleop"); }`
- `web/src/main.ts:25-27`: `if (!layoutIncludesTeleop(playLayoutData)) { throw new Error("Play layout is missing the Teleop panel; WASD must not replace it"); }` — mentions `Teleop`.
- `web/src/compile-check.ts:51-53`: `if (!layoutIncludesTeleop(playLayoutData)) { throw new Error("Play layout must keep the Teleop panel"); }` — mentions `Teleop`.
- Ran: `python3 -c "import json; p=json.load(open('layouts/Play.json')); s=json.dumps(p); assert 'Teleop' in s"` → exit 0 (`TELEOP IN PLAY OK`). PASS.

## ES-06 — No host-canvas game view — PASS

- Ran the exact check:

```sh
rg -n --glob '!*.md' -e 'getContext\s*\(' -e '<canvas' -e 'HTMLCanvasElement' -e 'OffscreenCanvas' web/src web/index.html
```

No output, exit 1. `node_modules`/`dist` not searched. The `host-canvas` copy in `web/index.html` does not match `<canvas`. PASS.

## ES-07 — `./web/check` exits 0 (no browser) — PASS

- Ran in this eval from `$ROOT`: `./web/check` → `tsc --noEmit && vite build`, 19 modules transformed, `dist/` built, stdout ends `EMBED CHECK OK`, `CHECK_EXIT=0`.
- `web/check:3`: `# Does not open a browser.`
- `web/package.json:10`: `"check": "tsc --noEmit && vite build",`
- `web/tsconfig.json:18`: `"include": ["src"]` — `web/src/compile-check.ts` is inside the `tsc --noEmit` run. No browser, Pro session, or live socket involved. PASS.

## ES-08 — `@foxglove/common` shim is explicit and documented — PASS

- `web/vite.config.ts:7`: `"@foxglove/common": fileURLToPath(new URL("./src/foxglove-common-shim.ts", import.meta.url)),`
- Ran: `rg -n 'export function toError' web/src/foxglove-common-shim.ts` → exactly one match: `6:export function toError(value: unknown): Error {`
- `web/README.md:64`: "`@foxglove/embed` 0.79.0 imports a private `@foxglove/common` workspace package that is not on npm. `src/foxglove-common-shim.ts` aliases the one runtime symbol (`toError`) so Vite can bundle." — names both `@foxglove/common` and `toError`, and states the limitation. The alias exists, so the build does not pass by `skipLibCheck` hiding a missing module. PASS.

## ES-09 — Publish path compile-checked / greppable; no Pro browser required — PASS

1. `web/src/compile-check.ts:47-50`: `clientAdvertiseJson()` assigned to `advertised`; throw when advertise JSON omits `CMD_VEL_TOPIC` or `BUTTONS_TOPIC`. Lines 27, 39-42: `const transport: ParentTransportFactory = createDoomTransport(publisher);` and `export const parentOwnedSourceCompileCheck: DataSource = parentOwnedLiveSource("ws://localhost:8765", transport);` with line 20 `type DataSource = Parameters<FoxgloveViewer["setDataSource"]>[0];`.
2. `web/src/publish.ts:7`: `const CLIENT_MESSAGE_DATA = 0x01;` Lines 85-93: `clientMessageFrame` does `view.setUint8(0, CLIENT_MESSAGE_DATA); view.setUint32(1, channelId, true);` — opcode then channel id. Line 139: `publishTwist` → `this.sendFrame(clientMessageFrame(CMD_VEL_CHANNEL_ID, twist));` Line 143: `publishButtons` → `clientMessageFrame(BUTTONS_CHANNEL_ID, buttons)`. Lines 151-157: `advertise()` → `this.sendFrame(clientAdvertiseJson());`.
3. `web/src/transport.ts:13-18`: `publisher.attach((frame) => { if (socket.readyState === WebSocket.OPEN) { socket.send(frame); } });` inside `createDoomTransport`.
4. `web/src/compile-check.ts:54-63`: idle-WASD assertion — `JSON.stringify(twistFromMotion({ forward: false, back: false, left: false, right: false, fire: false })) !== JSON.stringify(ZERO_TWIST)` throws `"idle WASD must publish a zero Twist"`.

No browser, no Pro session, no live socket used as evidence. PASS.

## ES-10 — Default live URL documented; 8765-busy not an ES FAIL — PASS

- `web/src/config.ts:5`: `export const DEFAULT_WS_URL = "ws://localhost:8765";`
- Ran per-string `rg -c -F` over `web/README.md`: `ws://localhost:8765` → 1 (line 19); `?ws=` → 2 (lines 43, 46); `VITE_FOXGLOVE_WS` → 1 (line 45); `8766` → 3 (lines 38, 43, 45); `secure context` → 2 (lines 11, 30); `Pro` → 1 (line 12). All present.
- Fallback snippet pairs the port with the query — `web/README.md:37-43`: `PYTHONPATH=. python -m doom_foxglove --fetch-iwad --port 8766` then `open "http://localhost:5173/?ws=ws://localhost:8766"`. PASS.

## ES-11 — Out-of-scope surfaces stay out of the host — PASS

- Ran the exact check:

```sh
rg -n -e 'mcap' -e 'Replay' -e 'comparison' -e 'spectator' -e 'rosbridge' web/src web/index.html web/package.json
```

No output, exit 1.
- The single README match is a permitted out-of-scope sentence — `web/README.md:68`: "Events, comparison, remote spectator. Replay an MCAP in the Foxglove app with `layouts/Replay.json` (see the repository README); this host stays live-only. Do not add a canvas renderer."
- No Replay `selectLayout`, no MCAP recorder, no comparison/spectator UI in `web/src`. PASS.

## Verdict

**PASS — ES-01, ES-02, ES-03, ES-04, ES-05, ES-06, ES-07, ES-08, ES-09, ES-10, ES-11 (11/11).** Failing ids: none. All eleven checkboxes ticked in `contract.md` by this evaluator. `cap_embed_page` product evidence is complete on the headless axis; the optional human Pro-browser pass remains out of scope per the contract.
