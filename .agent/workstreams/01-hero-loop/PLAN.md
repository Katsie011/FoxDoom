# PLAN — 01-hero-loop

Phase 1 of the product plan. This file is the phase spec copied onto disk so a cold agent does not need the plan path. It does not replace `.agent/GOAL.md`. It does not rewrite `/Users/michael/.cursor/plans/foxglove_doom_stunt_84c1ef0a.plan.md`.

## Punchline

A visitor teleoperates a marine the way Foxglove teleoperates a robot. ViZDoom is the fake robot. The Foxglove SDK WebSocket is the live connection. The marine's framebuffer is a camera topic. Teleop publishes Twist. Fire and use are a second publish path. The picture comes through stock Foxglove panels, never a host canvas.

## Must ship in this phase

- **Foxglove SDK WebSocket** — custom non-ROS stack, `ClientPublish` enabled, `ws://localhost:8765`. Not rosbridge, not a custom protocol.
- **Teleop panel** — publishes `geometry_msgs/Twist` on `/cmd_vel`. Map `linear.x` to forward/back, `angular.z` to turn, optional `linear.y` to strafe. Stop-on-release zeros the command, matching a real base.
- **Image** — `/doom/camera` as `foxglove.CompressedImage`, JPEG about 320x200 at about 35 Hz. Tiny bandwidth; the camera on the robot.
- **Buttons** — `/doom/buttons` JSON `{ fire, use, weapon }` for shoot/use. Teleop D-pad is enough to move, not enough to play.
- **IWAD** — Freedoom (or shareware). Do not redistribute a commercial WAD.
- **Smoke** — one command from repo root that boots, steps N ticks, publishes at least one camera frame, accepts a Twist, exits 0; non-zero on failure.

Control caveat from the product plan: Teleop is a 4-way D-pad plus stop. Fire / use / weapon need the second publish path. WASD in the embed host is a later workstream (`03-embed-shell`); it publishes the same topics and does not replace Teleop.

## Engine

ViZDoom: headless framebuffer, player pose, objects, automap, button action space. Tank controls (id Tech 1 / diff-drive). No mouse-look.

If ViZDoom is painful on this macOS machine, the Python server and smoke test still have to run. Prefer a real ViZDoom path over a fake framebuffer. Document IWAD and ViZDoom install in the repo README.

## Out of this phase

Do not custom-render the game in a host canvas.

Do not implement 3D grid / TF / entities, embed page, MCAP, events, comparison, or remote access. Those belong to `02`–`05`.
