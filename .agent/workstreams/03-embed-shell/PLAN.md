# PLAN — 03-embed-shell

Phase 3 of the product plan. Deferred until `02-robotics-layout` is evaluated `done` (`cap_3d_map_hud`).

## Spec (from the product plan, not rewritten)

Put the stunt in **embedded viz** (`@foxglove/embed` / `@foxglove/embed-react`) on a kiosk or `foxglove.dev/doom`-style page.

- Host app owns chrome, copy, and layout switching. Foxglove is the visualization layer (Fox Run pattern).
- Parent-owned live transport so the host owns auth and the connection. Direct `ws://` is the local developer path.
- `setKeybindings` (WASD + Space) in the host that publish the **same** topics as Teleop (`/cmd_vel`, `/doom/buttons`). D-pad remains the product screenshot; WASD is how people finish E1M1.
- Layout switcher: `selectLayout({ storageKey, opaqueLayout, force })` for `Play` / `Debug`.
- Secure context required (HTTPS or localhost). Embed is Pro.

Do not hide the product chrome entirely — people should recognize panels. Do not custom-render the game in a host canvas (`dec_no_canvas`).

## Out of this phase

MCAP recording, Replay layout, events, comparison, remote spectator, cloud share links.
