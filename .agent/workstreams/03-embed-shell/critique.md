# Critique — 03-embed-shell contract gate

**Critic:** kimi-k3-high (did not author the contract, did not write the product code)
**Date:** 2026-09-18
**Target:** `.agent/workstreams/03-embed-shell/contract.md` (`ES-01`…`ES-11`)
**Verdict:** **PASS** — every item is reproducible from a clean shell via quote / `rg` / `./web/check`. No amendments required.

## Method

I read `contract.md`, `PLAN.md`, `eval.md`, and every file the checks name (`web/package.json`, `web/index.html`, `web/check`, `web/tsconfig.json`, `web/vite.config.ts`, `web/README.md`, all of `web/src/`, `layouts/Play.json`). I then executed each shell check from `$ROOT` and confirmed every quoted symbol exists verbatim in the named file. An item fails this gate if its check demands text that does not exist, tolerates "looks correct", leaves a "mention" unanchored, or makes a browser/Pro session load-bearing.

## Per-item attack

- **ES-01** — `"@foxglove/embed": "^0.79.0"` is under `dependencies` in `web/package.json`. `import { FoxgloveViewer } from "@foxglove/embed"` (main.ts:1), `new FoxgloveViewer({` (main.ts:42), `const parent = requireEl<HTMLElement>("foxglove")` (main.ts:37), `#layout-play` / `#layout-debug` (index.html:21-22) and both `selectLayout` click handlers (main.ts:56-63) all exist. The `embed-react` rg is explicitly allowed-empty. Mechanical.
- **ES-02** — `createDoomTransport` (transport.ts:7, return type `ParentTransportFactory`), `onOpen` + `publisher.attach(... socket.send(frame))` (transport.ts:12-18), `parentOwnedLiveSource` / `iframeOwnedLiveSource` shapes (transport.ts:54-71), the three-way `connectFromCapabilities` branch with `pending` returning before any `setDataSource` (main.ts:65-84), `publisher.connectDirect(wsUrl)` (main.ts:82), `DEFAULT_WS_URL` (config.ts:5) and `readWsUrl` `?ws=` → `VITE_FOXGLOVE_WS` → default (config.ts:25-27) all verified. Browser and Pro sign-in explicitly excluded from PASS. Mechanical.
- **ES-03** — `test -f layouts/Play.json && test -f layouts/Debug.json` passes. Both imports (layouts.ts:1-2), `force: true` on both branches of `layoutParams` (layouts.ts:16-20, 22-26), `playSelectLayoutCompileCheck` / `debugSelectLayoutCompileCheck` typed as `Parameters<FoxgloveViewer["selectLayout"]>[0]` (compile-check.ts:19, 36-37), and both `viewer.selectLayout(layoutParams(...))` calls (main.ts:57, 61) verified. FAIL condition (`force` missing/false/single-sided) is decidable from the quote alone. Mechanical.
- **ES-04** — `doomKeybindings` binds `KeyW/KeyA/KeyS/KeyD/Space` (keybindings.ts:168-174); `twistFromMotion` maps forward/back → `linear.x` ±1, left/right → `angular.z` ±1 (keybindings.ts:21-28); `buttonsFromMotion` returns `{ fire: motion.fire, use: false, weapon: null }` (keybindings.ts:31); `flush` calls `publishTwist` / `publishButtons` (keybindings.ts:133-146); topic constants (config.ts:2-3); `clientAdvertiseJson` with `op: "advertise"`, `geometry_msgs/Twist`, both topics (publish.ts:61-83); compile-check throw and `needed` list (compile-check.ts:47-50, 65). `rg -n 'mousemove|pointerlock|mouse-look|LOOK_UP|LOOK_DOWN' web/src` → no output, exit 1. Nit (non-blocking): the check writes the buttons shape as `{ fire, ... }` shorthand while the code is `{ fire: motion.fire, ... }`; the quote requirement makes the real text decisive, so this cannot produce a false fail. Mechanical.
- **ES-05** — `"panelType": "Teleop"` at layouts/Play.json:31. `layoutIncludesTeleop` (layouts.ts:29-31). Both throws mention `Teleop` (main.ts:26, compile-check.ts:51-53). The `python3 -c` assert exits 0. Mechanical.
- **ES-06** — Ran the exact `rg` with `--glob '!*.md'`: no output, exit 1. Scope limited to `web/src web/index.html`; `node_modules`/`dist` excluded; the `host-canvas` copy does not match `<canvas`. Mechanical.
- **ES-07** — Ran `./web/check` from `$ROOT`: `tsc --noEmit && vite build`, 19 modules, prints `EMBED CHECK OK`, exit 0. Comment `Does not open a browser` present (web/check:3). `check` script and `tsconfig` `"include": ["src"]` verified, so `compile-check.ts` is inside the typecheck. No browser, Pro session, or live socket required. Mechanical.
- **ES-08** — Vite alias `"@foxglove/common"` → `./src/foxglove-common-shim.ts` (vite.config.ts:7). `rg -n 'export function toError' web/src/foxglove-common-shim.ts` prints exactly one match (line 6). README names both `@foxglove/common` and `toError` (README.md:64). The `skipLibCheck` fail condition is checkable by quoting `vite.config.ts`. Mechanical.
- **ES-09** — All four numbered quotes verified: compile-check advertise assignment + throw and `parentOwnedSourceCompileCheck` typed `DataSource = Parameters<FoxgloveViewer["setDataSource"]>[0]` (compile-check.ts:20, 39-42, 47-50); `CLIENT_MESSAGE_DATA = 0x01`, opcode-then-channel-id frame, `publishTwist`/`publishButtons`/`advertise()` (publish.ts:7, 85-93, 137-143, 151-157); `publisher.attach` → `socket.send(frame)` (transport.ts:13-18); idle-WASD `ZERO_TWIST` assertion (compile-check.ts:54-63). "Human signed into Pro and pressed W" is explicitly rejected as sole evidence. Mechanical.
- **ES-10** — `DEFAULT_WS_URL` (config.ts:5). README contains all six required strings: `ws://localhost:8765` (line 19), `?ws=` (lines 43, 46), `VITE_FOXGLOVE_WS` (line 45), `8766` (lines 38, 43), `secure context` (lines 11, 30), `Pro` (line 12). The fallback snippet pairs `--port 8766` with `?ws=ws://localhost:8766` (lines 37-43). Mechanical.
- **ES-11** — Ran the exact `rg` over `web/src web/index.html web/package.json`: no output, exit 1. The single README match (line 68: "Events, comparison, remote spectator. Replay an MCAP in the Foxglove app… this host stays live-only.") is an out-of-scope sentence, which the check explicitly permits and requires quoting. `layouts/Replay.json` exists at repo root but is outside the rg scope and belongs to 04. Mechanical.

## Process checks

- Grading rules forbid "looks fine" and unrun checks; checkboxes start unchecked; only the evaluator ticks; generator edit prohibitions are stated.
- eval.md reuse is restricted to unchanged file-quote checks, and `./web/check` must be re-run in the ticking eval — the one dynamic check cannot go stale.
- No item requires a browser, a signed-in Pro session, or a live `ws://` server; the three environmental facts (pending Pro transport, busy 8765, `cap_3d_map_hud` planned) are fenced off as non-FAILs with the fallback quote path named.
- Scope fence (ES-11) and the out-of-scope list match `PLAN.md` and `GOAL.md` phase boundaries; 01/02 contracts are explicitly untouchable.

## Gate

**PASS.** The contract is gradeable as written. Next action: evaluator (kimi-k3-high, not the generator) runs the checks and ticks `ES-01`…`ES-11`.
