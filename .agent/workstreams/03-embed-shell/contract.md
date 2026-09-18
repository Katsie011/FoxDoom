# Contract — 03-embed-shell

**Workstream:** `03-embed-shell`
**Item-id prefix:** `ES-`
**KG node:** `ws_03_embed_shell`
**Capability:** `cap_embed_page`
**Status:** planning. This file replaces the 2026-09-18 deferral stub. It is a gradeable `ES-nn` contract. A Kimi critic must still gate it before an evaluator may tick boxes. This planner does not grade.

Source of truth for phase scope: `.agent/GOAL.md` (`cap_embed_page`, `dec_embed_viz`, `dec_no_canvas`, `dec_teleop_twist`) and `.agent/workstreams/03-embed-shell/PLAN.md`. This contract does not rewrite either.

Product code already exists under `web/`. These items grade that tree. Generation preceded this gate; the gate is retroactive. A generator handed this contract implements only remaining ES gaps. It does not tick boxes, does not edit this file, and does not edit `01-hero-loop/contract.md` or `02-robotics-layout/contract.md`.

## How this contract is graded

The evaluator (kimi-k3-high) is told the embed shell is broken and must prove it. For every `ES-nn` item it must run the stated **Check** from a clean shell at the repo root, or quote the exact file text the check names. "Looks fine" is a fail. An unrun check is a fail.

- Repo root is `$ROOT` (`/Users/michael/Documents/foxglove/work/doom`). Every command below is run after `cd "$ROOT"`.
- Headless smoke is `./web/check` (equivalent: `npm --prefix web run check`). It is `tsc --noEmit` including `web/src/compile-check.ts`, then `vite build`. It must not open a browser.
- An item is **PASS** only if its check succeeds. Checkboxes below start unchecked. **Only the evaluator ticks `- [ ]`.** The generator must not tick boxes, must not edit this file, and must not append `verified` / `failed` onto `ContractItem` nodes.
- A signed-in Foxglove Pro browser session is **never** required to PASS an item. Embed-is-Pro and `parentOwnedLiveTransport === "pending"` are product constraints. Quote the pending / fallback code path; do not fail the item because no one signed in.
- Occupied `ws://localhost:8765` is an environment note, not an ES FAIL. The documented `?ws=` / `VITE_FOXGLOVE_WS` override is the allowed workaround.
- `cap_3d_map_hud` still `planned` (eval EC-1) is a phase-DAG sequencing fact, not an ES FAIL of the host page. This contract grades the embed shell, not workstream 02.
- Reuse of `.agent/workstreams/03-embed-shell/eval.md` is allowed for unchanged file-quote checks. `./web/check` must be re-run in the eval that ticks ES-07.

---

## A. Host and transport

### ES-01 — Host page embeds Foxglove via `@foxglove/embed` in `web/`

- [x] The public/kiosk surface is a host page under `web/` that constructs `FoxgloveViewer` from `@foxglove/embed` (or `@foxglove/embed-react`). Foxglove is the visualization layer. The host owns chrome, copy, and Play/Debug layout switching (`dec_embed_viz`). Not a custom game renderer beside Foxglove.

**Check:** `web/package.json` lists `"@foxglove/embed"` under `dependencies`. Quote `import { FoxgloveViewer } from "@foxglove/embed"` and `new FoxgloveViewer({` in `web/src/main.ts`. Quote the constructor passing `parent` as the `#foxglove` element (not a `<canvas>`). Quote `#layout-play` and `#layout-debug` in `web/index.html` and the `selectLayout` click handlers in `web/src/main.ts`. `rg -n 'from "@foxglove/embed-react"|from '\''@foxglove/embed-react'\''' web/src` may be empty; `@foxglove/embed` alone is enough.

### ES-02 — Parent-owned live transport; pending Pro plus quoted fallback allowed

- [x] The host opens the live Foxglove WebSocket in the parent (`ParentTransportFactory`) so the iframe does not guess CORS (`dec_embed_viz`). Default URL is `ws://localhost:8765`. When `viewer.getCapabilities().parentOwnedLiveTransport` is `"pending"`, the host waits (sign-in). When `"available"`, it calls `setDataSource` with a live `foxglove-websocket` source that includes the parent `transport`. When `"unavailable"`, a documented iframe-owned live source plus a second parent socket for WASD publish is allowed **only if this check quotes that fallback path**. Direct `ws://` is the local developer path. Not rosbridge. Not a custom host protocol.

**Check:** Quote `export function createDoomTransport` in `web/src/transport.ts` — return type is `ParentTransportFactory`; `onOpen` attaches the publisher to `socket.send`. Quote `parentOwnedLiveSource` returning `{ type: "live", protocol: "foxglove-websocket", url, transport }`. Quote `iframeOwnedLiveSource` returning the same shape without `transport`. Quote the three-way branch in `web/src/main.ts` (`connectFromCapabilities` or equivalent) that:

1. treats `"pending"` as wait (no `setDataSource` on that turn);
2. treats `"available"` as `parentOwnedLiveSource(wsUrl, transport)`;
3. treats `"unavailable"` as `iframeOwnedLiveSource(wsUrl)` plus `publisher.connectDirect(wsUrl)` (or the same second-socket call under another name).

Quote `DEFAULT_WS_URL = "ws://localhost:8765"` and `readWsUrl` (`?ws=` then `VITE_FOXGLOVE_WS` then default) in `web/src/config.ts`. FAIL if the only live path is iframe-owned with no parent `transport` and no quoted `connectDirect` fallback. Do **not** FAIL because `parentOwnedLiveTransport` is `"pending"` without a Pro sign-in. Do **not** open a browser to PASS this item.

### ES-03 — Force-load `Play.json` and `Debug.json`

- [x] Layout switching calls `selectLayout({ storageKey, layout, force: true })` for both `layouts/Play.json` and `layouts/Debug.json`. `layout` is the programmatic `@foxglove/layout-api` tree (`version` + `content`) that `foxglove.layouts` emits. Do **not** pass that tree as `opaqueLayout` — that field is only for a JSON file exported from the Foxglove app, and the embed will show "Incompatible layout". Force is required so a stale stored layout cannot hide the exported Play/Debug panels.

**Check:** `test -f layouts/Play.json && test -f layouts/Debug.json`. Quote both imports in `web/src/layouts.ts`. Quote `layoutParams("play")` and `layoutParams("debug")` — each returned object includes `storageKey`, `layout`, and `force: true`. Quote `playSelectLayoutCompileCheck` and `debugSelectLayoutCompileCheck` in `web/src/compile-check.ts` (typed as `Parameters<FoxgloveViewer["selectLayout"]>[0]` or equivalent). Quote `viewer.selectLayout(layoutParams(...))` for both Play and Debug in `web/src/main.ts`. FAIL if `force` is missing, false, or only present on one layout. FAIL if `opaqueLayout` is used for Play/Debug (SDK programmatic JSON is not an app export).

---

## B. Teleop topics and no canvas

### ES-04 — WASD+Space publish `/cmd_vel` and `/doom/buttons`

- [x] Host `setKeybindings` (WASD + Space) publish the **same** topics as Teleop (`dec_teleop_twist`): `geometry_msgs/Twist` on `/cmd_vel` and JSON `{ fire, use, weapon }` on `/doom/buttons`. W/S are `linear.x`, A/D are `angular.z` (tank / `dec_tank_controls`). Space fires. WASD does not replace the Teleop panel. No mouse-look FPS handler.

**Check:** Quote `doomKeybindings` in `web/src/keybindings.ts` — bindings exist for `KeyW`, `KeyA`, `KeyS`, `KeyD`, and `Space`. Quote `twistFromMotion`: forward/back set `linear.x` to `1`/`-1`; left/right set `angular.z` to `1`/`-1`. Quote `buttonsFromMotion` returning `{ fire, use: false, weapon: null }`. Quote `HoldController.flush` calling `publishTwist` and `publishButtons`. Quote `CMD_VEL_TOPIC = "/cmd_vel"` and `BUTTONS_TOPIC = "/doom/buttons"` in `web/src/config.ts`. Quote `clientAdvertiseJson` in `web/src/publish.ts` — `op: "advertise"`, `schemaName: "geometry_msgs/Twist"` on `/cmd_vel`, buttons schema on `/doom/buttons`. Quote `web/src/compile-check.ts` throwing if advertise JSON omits either topic, and the `needed` key list `["KeyW", "KeyA", "KeyS", "KeyD", "Space"]`. `rg -n 'mousemove|pointerlock|mouse-look|LOOK_UP|LOOK_DOWN' web/src` is empty.

### ES-05 — Teleop remains in the Play layout

- [x] The Play layout still contains a Teleop panel. WASD is an additional publish path, not a replacement (`dec_teleop_twist`). Removing Teleop from Play is an ES-05 FAIL even if WASD works.

**Check:** Quote `"panelType": "Teleop"` in `layouts/Play.json`. Quote `layoutIncludesTeleop` in `web/src/layouts.ts`. Quote the throw in `web/src/main.ts` and in `web/src/compile-check.ts` when Play lacks Teleop (messages must mention `Teleop`). `python3 -c "import json; p=json.load(open('layouts/Play.json')); s=json.dumps(p); assert 'Teleop' in s"`. Presence of Teleop in `layouts/Debug.json` is allowed and does not decide this item.

### ES-06 — No host-canvas game view

- [x] The marine view is a Foxglove Image panel subscription, not a host `<canvas>` / `getContext` renderer (`dec_no_canvas`). Host chrome may say that in copy. A canvas that happens to sit next to Foxglove is a failed stunt.

**Check:**

```sh
rg -n --glob '!*.md' -e 'getContext\s*\(' -e '<canvas' -e 'HTMLCanvasElement' -e 'OffscreenCanvas' \
  web/src web/index.html
```

Must print nothing. The word `canvas` in comments, `web/README.md`, or the index copy (`host-canvas`) is allowed. Do **not** search `web/node_modules` or `web/dist`. FAIL if any host file draws the framebuffer into a browser canvas.

---

## C. Headless smoke and residual risks

### ES-07 — `./web/check` exits 0 (no browser)

- [x] From `$ROOT`, `./web/check` typechecks (including `web/src/compile-check.ts`) and builds the host, prints `EMBED CHECK OK`, and exits 0. It does not open a browser, does not require a signed-in Pro org, and does not require a live `ws://` server.

**Check:**

```sh
./web/check
```

Exit 0. Stdout contains `EMBED CHECK OK`. Quote the comment `Does not open a browser` in `web/check`. Quote `web/package.json` script `check` as `tsc --noEmit && vite build`. Quote `web/tsconfig.json` `"include": ["src"]` so `compile-check.ts` is inside `tsc --noEmit`. FAIL on non-zero exit. Do **not** FAIL this item because no Pro session or live socket was available.

### ES-08 — `@foxglove/common` shim is explicit and documented

- [x] `@foxglove/embed` imports unpublished `@foxglove/common`. The host aliases that name to a local shim that exports the runtime symbol the bundle actually calls (`toError`). The alias and the limitation (runtime coverage is that symbol, not the full package) are documented in `web/README.md`. This is the eval residual risk; hiding the alias or deleting the shim is an ES-08 FAIL even if a future upstream publish would make it unnecessary.

**Check:** Quote the Vite alias `"@foxglove/common"` → `./src/foxglove-common-shim.ts` (or equivalent path) in `web/vite.config.ts`. Quote `export function toError` in `web/src/foxglove-common-shim.ts`. Quote the `web/README.md` sentence that names `@foxglove/common` and `toError`. `rg -n 'export function toError' web/src/foxglove-common-shim.ts` prints exactly one match. FAIL if `./web/check` only succeeds because `skipLibCheck` hid a missing module and no alias exists.

### ES-09 — Publish path is compile-checked or greppable; no Pro browser required

- [x] Advertise + client-message frames on the parent socket are proven by a compile-time assertion already in `web/src/compile-check.ts` and/or a mechanical quote/typecheck of the frame builders. `./web/check` never opening a `ws://` connection is **not** an ES-09 FAIL. A signed-in Pro embed is **not** required and must not be the only proposed proof (eval residual risk).

**Check:** All of the following, none of which open a browser:

1. Quote in `web/src/compile-check.ts`: `clientAdvertiseJson()` assigned and the throw when advertise JSON omits `CMD_VEL_TOPIC` or `BUTTONS_TOPIC`; `parentOwnedSourceCompileCheck` constructed with `createDoomTransport(publisher)` and typed as `Parameters<FoxgloveViewer["setDataSource"]>[0]` (or equivalent `DataSource`).
2. Quote in `web/src/publish.ts`: `CLIENT_MESSAGE_DATA = 0x01`; `clientMessageFrame` writes that opcode then the channel id; `publishTwist` calls `clientMessageFrame(CMD_VEL_CHANNEL_ID, twist)`; `publishButtons` calls `clientMessageFrame(BUTTONS_CHANNEL_ID, buttons)`; `advertise()` sends `clientAdvertiseJson()`.
3. Quote in `web/src/transport.ts`: `publisher.attach` → `socket.send(frame)` inside `createDoomTransport`.
4. Quote in `web/src/compile-check.ts` the idle-WASD assertion `twistFromMotion({...})` equals `ZERO_TWIST`.

FAIL if any of those symbols are missing. FAIL if the evaluator's only evidence is "a human signed into Pro and pressed W". Do **not** FAIL because `./web/check` did not send a frame to a live server.

### ES-10 — Default live URL documented; 8765-busy is not an ES FAIL

- [x] Default live URL is `ws://localhost:8765`. `web/README.md` documents the host, the Python server, secure context (localhost or HTTPS), embed-is-Pro, and the busy-8765 workaround (`python -m doom_foxglove --port 8766` plus `http://localhost:5173/?ws=ws://localhost:8766` or `VITE_FOXGLOVE_WS`). Occupied 8765 is an environment note, not an ES FAIL.

**Check:** Quote `DEFAULT_WS_URL = "ws://localhost:8765"` in `web/src/config.ts`. `web/README.md` contains each of these strings: `ws://localhost:8765`, `?ws=`, `VITE_FOXGLOVE_WS`, `8766`, `secure context`, `Pro`. Quote the README fallback snippet that pairs `--port 8766` with `?ws=ws://localhost:8766`.

---

## D. Scope fence

### ES-11 — Out-of-scope surfaces stay out of the host

- [x] This workstream does not add events, comparison, a remote-access gateway, mouse-look FPS, or a custom `.foxe` HUD. 04 pause-replay may add `#pause-replay`, a `layouts/Replay.json` import, FileSource `type: "file"`, and `readControlUrl` to `web/` (`PR-nn` on `04-record-replay`). 05 demo UX polish may add `#key-hud`, `#hud-bars` / `#hud-health` / `#hud-armor` / `#hud-ammo`, `#replay-files`, and `POST /new-game` (`UX-nn` on `05-stunt-extras`). Those Replay/mcap/HUD hits do **not** FAIL. A comparison / spectator / rosbridge surface in `web/` still FAILs. Mentions of Replay as "use the Foxglove app, not this host" in `web/README.md` do not FAIL. Do **not** search `web/node_modules` or `web/dist`.

**Check:**

```sh
rg -n -e 'comparison' -e 'spectator' -e 'rosbridge' \
  web/src web/index.html web/package.json
echo es11_forbid_exit=$?
python3 <<'PY'
from pathlib import Path
import re
# Carve-out (quote this sentence): the only allowed Replay/mcap hits in web/src,
# web/index.html, and web/package.json are 04 pause-replay lines that also match
# pause-replay | readControlUrl | DEFAULT_CONTROL_URL | VITE_FOXGLOVE_CONTROL |
# layouts/Replay.json | Replay.json | replayLayoutData | REPLAY_STORAGE_KEY | FileSource |
# type: "file" | .mcap
# plus 05 UX polish: key-hud | hud-bars | hud-health | hud-armor | hud-ammo |
# replay-files | new-game
allow = re.compile(
    r"pause-replay|readControlUrl|DEFAULT_CONTROL_URL|VITE_FOXGLOVE_CONTROL|"
    r"layouts/Replay\.json|Replay\.json|replayLayoutData|REPLAY_STORAGE_KEY|FileSource|"
    r"type:\s*[\"']file[\"']|\.mcap|"
    r"key-hud|hud-bars|hud-health|hud-armor|hud-ammo|replay-files|new-game"
)
needle = re.compile(r"mcap|Replay")
roots = [Path("web/src"), Path("web/index.html"), Path("web/package.json")]
files = []
for root in roots:
    if root.is_file():
        files.append(root)
    elif root.is_dir():
        files.extend(sorted(p for p in root.rglob("*") if p.is_file()))
bad = []
for path in files:
    text = path.read_text(encoding="utf-8")
    for i, line in enumerate(text.splitlines(), 1):
        if needle.search(line) and not allow.search(line):
            bad.append("%s:%s:%s" % (path, i, line))
assert not bad, bad
print("ES-11 carve-out-ok", "files", len(files))
PY
```

The `rg` invocation must print nothing (ripgrep exits 1 on no match — that is PASS; treat "no output" as the bar, not exit 0). The `$PY` carve-out PASSes when there are zero `mcap`/`Replay` hits **or** every such hit matches the allow regex above. FAIL if any printed `rg` line is a comparison / spectator / rosbridge product surface. FAIL if a `mcap`/`Replay` line is not a 04 pause-replay or 05 UX-polish carve-out (for example a Replay layout button that is not `#pause-replay` / `#replay-files`, a host MCAP recorder, or a `type: "recording"` Data Platform source). `rg -n 'Replay|MCAP|comparison|spectator' web/README.md` may mention those words only in an "out of scope" / "not this host" / pause-replay-docs sentence — quote that sentence if it matches.

---

## Out of scope (do not FAIL 03 for these; do not require them)

These belong to other workstreams. Presence in `doom_foxglove/` or `layouts/` (02/04 already started) or absence does not decide any ES item except as named above.

- ViZDoom engine, IWAD, `/doom/camera`, server `ClientPublish` — `01-hero-loop`
- Grid / TF / entities / gauges / exporting Play and Debug — `02-robotics-layout` (`cap_3d_map_hud`). This contract **consumes** those JSON files; it does not re-export them.
- MCAP record/replay — `04-record-replay`
- Events, comparison, agent prompts, remote spectator — `05-stunt-extras`
- Custom `.foxe` HUD, mouse-look FPS, ROS/rosbridge, commercial IWAD, a general game engine, audio, cloud upload
- Editing `.agent/workstreams/01-hero-loop/contract.md` or `.agent/workstreams/02-robotics-layout/contract.md`
- A signed-in Pro browser pass (human optional; never an ES checkbox)

## Process (not an ES checkbox)

This file is the planner-authored `ES-nn` contract that eval EC-3 / ES-GATE required. The critic (kimi-k3-high) attacks these items; this planner does not grade them. No generator ticks the boxes above. Next action is the Kimi critic gate, not a product-code generator, unless the critic returns amendments this planner must apply.

Prior eval (2026-09-18) process FAILs that this file is meant to close: **ES-GATE** (no numbered items), **EC-3** (no planner-authored contract). **EC-1** (`cap_3d_map_hud` not `done`) remains a DAG fact outside these checkboxes.
