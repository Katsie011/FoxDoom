# PLAN — README rewrite

This is not a numbered product phase. The deliverable is repository `README.md`. The generator writes that file. This planner does not.

## Why this repo exists

Foxglove is already the UI for teleoperating robots. This repo is a stunt that treats a DOOM marine as that robot.

ViZDoom is a fake robot process. The marine camera is a camera topic. Twist from the Teleop panel is how you drive. If the picture is a stock Foxglove Image panel, the stunt worked. If someone draws DOOM on a host canvas next to Foxglove, the stunt failed.

That is the whole point. Architecture, topic lists, and build notes are details. They are not the opening.

The generator must open `README.md` with that why: short, concrete, no manifesto cadence. Do not stack three "X is the Y" sentences to say it. Then how to run. Then details.

## What the new README is for

A visitor who has never opened this tree should understand, in the first screen:

1. Foxglove already drives robots. This repo asks the same product to drive a marine.
2. How to install and get a picture in a stock Image panel (embed at `http://localhost:5173/` preferred; Foxglove app WebSocket also fine).
3. Then replay, the three copy-paste agent prompts, and what this slice does not ship.

They should not meet brew, cmake, ephemeral ports, or a fallback framebuffer before a working command.

## Voice (read these, do not vendor them)

Closest analog: [gasmith/foxglove-lunar-lander](https://github.com/gasmith/foxglove-lunar-lander) — one-line why (Foxglove as the UI), then run. This tree has no screenshot. Do not invent a GIF or PNG. Do not fail the slice for a missing image.

Also read, do not copy:

- [FiloSottile/age](https://github.com/FiloSottile/age) — one-line what/why, then a working command in the first screen
- [jqlang/jq](https://github.com/jqlang/jq) — one-line what, then docs/install; no architecture dump
- [foxglove/mcap](https://github.com/foxglove/mcap) — one-line what, then pointers; not a topic encyclopedia

## Happy-path order the generator must keep

1. `# ` title, then the why (robot / Foxglove / marine / Image / canvas).
2. Still in that preface, after the why paragraph and before the first `##`: a compact mermaid flowchart of high-level components (RD-19 / RD-20). Do not add `## Architecture` or `## Build notes` as the first heading. Do not invent a PNG.
3. Install + `./smoke` or live server + open. Prefer embed `http://localhost:5173/`. Also document `ws://localhost:8765` for the Foxglove app.
4. Frozen headings, in this order: `## Replay an MCAP`, `## Ask Foxglove (copy-paste)`, `## Not in this slice`.
5. Only then: ViZDoom source build (`brew install cmake`), "If ViZDoom cannot import", busy 8765, ephemeral ports, fallback framebuffer.

## Architecture (diagram the generator must draw)

High-level components talking to each other. Not a topic encyclopedia. Keep it compact so the why still sits on the first screen.

Non-Foxglove nodes:

- Freedoom / IWAD
- ViZDoom (fake robot)
- `doom_foxglove` process
- Host page WASD (publishes the same topics as Teleop; does not replace Teleop)

Foxglove nodes — visually grouped with a subgraph titled Foxglove and/or mermaid `classDef` plus `class ` on the sdk / embed / panel nodes:

- foxglove-sdk WebSocket `ws://localhost:8765` with ClientPublish
- Stock panels: Image, 3D, Teleop, Gauge/Log
- `@foxglove/embed` (kiosk/host)
- Foxglove app (alternate client)
- MCAP sidecar + Replay into the app

Edges (component arrows, not nine `/topic` bullets):

- ViZDoom → doom_foxglove → foxglove-sdk (camera / map / pose)
- Teleop and WASD → sdk (Twist / buttons)
- sdk → stock panels (live)
- sdk → MCAP → Foxglove app Replay
- Host page → `@foxglove/embed` → panels

No host-canvas renderer in the data path. Do not vendor `ParentTransportFactory` / `foxglove-common-shim` / `compile-check.ts` / `VITE_FOXGLOVE_WS` into the root README (RD-09 allows at most one). The diagram must not push `brew install cmake` or `If ViZDoom cannot import` above `## Not in this slice`.

## Anti-patterns the current README already has (kill them)

- Opening as parallel "X is the Y" architecture sentences (LLM cadence). The current first paragraph is the bad reference.
- `## Requirements`, troubleshooting, fallback framebuffer, or `brew install cmake` before a working install+run.
- The live-server section as a full topic/schema catalog.
- Agent-speak around the frozen `## Not in this slice` heading (`Skipped (… extras cut)`). The heading stays. The prose around it should be a human sentence that still contains the four frozen needles.
- Hedging in the first screen (ephemeral ports, "if ViZDoom cannot import").
- Duplicating `web/README.md` (parent transport, shims, Vite env). A one-line pointer is enough.
- An invented PNG/GIF architecture picture (RD-18). The diagram is mermaid in the preface, not a screenshot.

## Frozen strings (do not drop, do not paraphrase)

Older evals still have to pass. Copy the exact prompt bodies. Keep the exact frozen headings. Keep HL-13 install/smoke/WS/Image/Teleop/canvas/commercial needles. Keep RR-05 replay strings and a local-open path. Keep the word `cloud` so RR-06 still passes.

## Scope

Generator may edit `README.md` only. Optional one-line pointer fix in `web/README.md` only if a heading that file points at moved. No Python, no layouts, no `web/src`, no `.agent/GOAL.md`, no `01`–`05` contracts, no knowledge-graph writes, no `.agent/workstreams/06-*`.

## Done

`contract.md` is the grade. A Kimi critic attacks new RD-19 / RD-20 (and must not weaken RD-01…RD-18) before any further README edit. This planner does not generate the README and does not tick boxes.
