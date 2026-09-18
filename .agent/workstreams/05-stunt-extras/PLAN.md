# PLAN — 05-stunt-extras

Phase 5 of the product plan. **Deferred until workstreams 01, 02, and 03 are evaluated `done`.** Record/replay (`04`) may proceed in parallel once `03` is done; extras still wait on the first three capabilities.

## Spec (from the product plan, not rewritten)

Garnish that turns a toy into a platform demo. Only after 1–3 are demo-stable:

- **Events** — tag deaths, weapon pickups, level complete. Scrub to the moment that matters.
- **Comparison mode** — two playthroughs, or human vs a ViZDoom policy, side by side.
- **Built-in agent / MCP** — when did health drop, why did I die, build a layout for weapons.
- **User script** — layout-local topic, for example damage-per-second or time-to-shotgun.
- **Remote access / gateway** — booth machine as a device; phones spectate without opening a port.
- **Image click/hover publish** — click the framebuffer to aim or inspect a pixel. Stretch.
- **Shareable recording link** if `04` did not already ship it.

## Demo UX polish (2026-09-18 live-demo feedback)

Garnish owned by this workstream (`05`), not a workstream `06-*`. Foxglove iframe stays stock panels (`dec_host_html_hud` / `dec_stock_panels_only`). Host HTML beside the iframe is allowed. Custom `.foxe` / `installExtensions` stays out (kiosk is `https://embed.foxglove.dev/`). `dec_no_canvas` still holds for the marine image.

1. **WASD visibility for video** — left-column `#key-hud` showing W/A/S/D and Space while `HoldController` motion is true. Live path only; do not reconstruct keys from MCAP during FileSource replay.
2. **Player mesh in 3D** — stock 3D panel already follows `base_link`; `/doom/entities` must include a distinct SceneUpdate mesh for the marine (`player:` id) so the actor is visible on the occupancy grid. Recorded into MCAP automatically.
3. **Health as a host HTML bar** — `#hud-bars` / `#hud-health` (armor, ammo) reading `/doom/player` JSON. Not a Gauge requirement on Play. Not a canvas framebuffer. Not a `.foxe`. Debug may keep a Plot of health vs time.
4. **Play after pause starts a new game** — `POST /new-game` then live WS + Play layout. `engine.reset()`, new MCAP sidecar, clear `stop_event`, `run_loop` again. Not resume of the paused tick (no `POST /resume`).
5. **Replay file browser** — `#replay-files` lists other `recordings/doom-*.mcap`. Click loads FileSource + Replay layout. `GET /recordings` from the stdlib control plane. Visible in replay mode only.
6. **WAD state in the 3D panel** — blocking linedefs from ViZDoom `get_state()` (same objects `_occupancy` already iterates) extruded as `/doom/walls` SceneUpdate cubes/lines with height (`WALL_HEIGHT_M = 2.4` when sector heights are missing). Once per level, like `/doom/map`. Occupancy Grid stays. Fallback hollow-room still publishes ≥ 4 walls. No IWAD file parser, no textured floors, no host-canvas map.

Out of this polish: mouse-look, `.foxe`, rosbridge, comparison, cloud upload, audio, resume-same-episode, from-scratch WAD parser, textured/sector-floor mesh.

## Skip (weak fit, stay off-camera)

Map panel lat/lon fakery. Diagnostics unless we emit `DiagnosticArray`. Custom `.foxe` in the embed iframe (host HTML HUD is allowed). Audio. True mouse-look FPS.

## Marketing beats this phase enables

Replay drop with agent questions. Spectator / fleet story. Human vs policy comparison layout.
