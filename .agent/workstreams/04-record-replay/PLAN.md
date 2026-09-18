# PLAN — 04-record-replay

Phase 4 of the product plan. Deferred until `03-embed-shell` is evaluated `done` (`cap_embed_page`).

## Spec (from the product plan, not rewritten)

- **MCAP logging with the same SDK code** — every session is a recording. Same layout for live and replay. This is the live-to-playback story.
- **Replay layout** — load the MCAP; hide Teleop; show playback bar. Website follow-up: every run is data.
- Optional **shareable recording link** — tweet a run, open it in Foxglove. Cloud upload may wait for `05` if it needs Data Platform.

Host controls this with `setDataSource({ type: "live" | "remote-file" | "recording" })`.

## Out of this phase

Events tagging, comparison mode, built-in agent, remote spectator, unless a later `05` contract pulls them in. Do not start those here.

## Pause & replay in the embed

This slice completes `cap_mcap_replay` inside the embed host (`web/`). It is still workstream 04 (prefix `PR-`); it is not a new workstream. Numbered items: `PR-01`…`PR-10` in `contract.md`.

Host chrome `#pause-replay` (visible label contains Pause) sits with Play/Debug. Click POSTs a stdlib HTTP control plane (`--control-port`, default 8764) to stop `run_loop` / `engine.step` and `writer.close()` the foxglove-sdk MCAP sidecar, then GETs the closed bytes (CORS, `application/octet-stream`, magic `\x89MCAP0\r\n`) and calls `@foxglove/embed` `setDataSource({ type: "file", file, autoplay: true })` plus `selectLayout({ storageKey, layout: layouts/Replay.json, force: true })` — `layout`, not `opaqueLayout`. Playback bar is Foxglove file-source chrome. Pause is one-way in this slice. `--no-record`: POST still stops the engine; GET `/recording` is 409; embed status mentions recording is off. Headless proof: `./smoke-pause-replay`.

Out of this slice: resume-live, cloud upload, share URL, Data Platform, comparison, remote spectator, events tagging UI, mouse-look, host canvas, custom `.foxe`, rosbridge, commercial WAD, audio, rewriting Play/Debug, switching Play/Debug to `opaqueLayout`, a workstream `06-*`. ES-11's Replay/mcap carve-out is on workstream 03.
