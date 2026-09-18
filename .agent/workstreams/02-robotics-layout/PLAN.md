# PLAN — 02-robotics-layout

Phase 2 of the product plan. Deferred until `01-hero-loop` is evaluated `done` (`cap_live_ws_camera_teleop`).

## Spec (from the product plan, not rewritten)

Add the robotics-shaped layout around the already-working camera and teleop:

- `/tf` — `foxglove.FrameTransforms` (`map` → `base_link` from ViZDoom pose/angle)
- `/doom/map` — `foxglove.Grid` occupancy of the WAD map, once per level
- `/doom/entities` — `foxglove.SceneUpdate` (monsters, items, projectiles as cubes)
- `/doom/player` — compact JSON: health, armor, ammo, weapon, tick, dead
- `/doom/log` — `foxglove.Log` (pickups, deaths, level messages)
- Gauges — health, armor, ammo
- Plot — health and ammo vs time
- Exported layouts the embed can `selectLayout`: `Play` (camera + teleop + gauges) and `Debug` (add 3D, plots, logs, raw)

Optional later in this phase: click-to-publish as a nav goal.

Stock panels only (`dec_stock_panels_only`). No custom `.foxe` HUD until gauges are proven too generic.

## Out of this phase

Embed shell, MCAP, events, comparison, remote access, host-canvas rendering.
