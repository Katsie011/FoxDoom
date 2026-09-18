# GOAL — play DOOM in Foxglove

This file is the north star for every agent working in this repository. It is written to be read cold, from disk, with no chat history and no plan file. If this file and a plan file disagree, this file wins until a human amends it.

Knowledge-graph mirror: every locked decision below carries its node id from `.agent/knowledge-graph/nodes.jsonl`, so prose and graph cannot drift apart.

## North star

A visitor opens Foxglove (app or embed) and **teleoperates a marine the way Foxglove teleoperates a robot**. A ViZDoom process is the fake robot. The Foxglove SDK WebSocket is the live connection. The marine's framebuffer is a camera topic. The WAD map is a 3D grid with a player transform. The Teleop panel publishes Twist. Fire and use are a second publish path. Every session can be recorded as MCAP and replayed in the same layout.

The picture must come through **stock Foxglove panels**. A canvas that happens to sit next to Foxglove is a failed stunt.

## Dates

There is no event deadline. This is a cheap side project. Sequence by phase gating, not by calendar. Do not invent a ship date.

## Locked decisions

A locked decision is not reopened by an agent; reopening one is an escalation to the human. Each bullet carries its knowledge-graph node id.

- `dec_vizdoom_engine` — The engine is **ViZDoom**, not chocolate-doom, doomgeneric, or a from-scratch WAD parser. It already exposes framebuffer, pose, objects, automap, and a button action space.
- `dec_freedoom_legal` — Ship **Freedoom** (or the shareware IWAD). Do not redistribute a commercial WAD.
- `dec_foxglove_sdk_ws` — Live path is **`foxglove-sdk` WebSocket** with `ClientPublish`, default `ws://localhost:8765`. Not rosbridge, not a custom WS protocol, not LeRobot `--display_mode=foxglove`.
- `dec_stock_panels_only` — v1 uses stock panels only (Image, 3D, Teleop, Gauge, Plot, Log, Raw Messages, Table). No custom `.foxe` HUD until gauges are proven too generic.
- `dec_teleop_twist` — Movement is `geometry_msgs/Twist` on `/cmd_vel` from the Teleop panel. Fire/use/weapon live on `/doom/buttons`. WASD in the embed host publishes the same topics; it does not replace Teleop.
- `dec_embed_viz` — The public/kiosk surface is **embedded Foxglove** (`@foxglove/embed` or `@foxglove/embed-react`) with parent-owned live transport and programmatic `Play` / `Debug` / `Replay` layouts.
- `dec_no_canvas` — Do not custom-render the game in a host canvas. If the image is not a Foxglove Image panel subscription, the stunt failed.
- `dec_tank_controls` — Keep id Tech 1 tank controls (diff-drive). No mouse-look FPS. That is the robot metaphor.
- `dec_cheap_models` — Every spawned sub-agent uses only `cursor-grok-4.6-high-fast` or `kimi-k3-high`. No Claude, no GPT, no Composer, no `inherit` (inherit drifts if the parent model changes).
- `dec_producer_neq_judge` — A model that produces a deliverable may not grade it. Generators are Grok. Critics and evaluators are Kimi K3.
- `dec_state_on_disk` — Durable state lives under `.agent/`. Chat is not a source of truth. Agents write findings to files; they do not dump the knowledge graph into chat.
- `dec_phase_gating` — Product workstreams run in order: harness → hero loop → robotics layout → embed shell → record/replay. Stunt extras (`05`) stay deferred until `01`–`03` are evaluated `done`.

## Phase definition of done

An evaluator ticks these, not a generator. Each line is also a `Capability` node.

- [ ] `cap_live_ws_camera_teleop` — ViZDoom + `foxglove-sdk` on `ws://localhost:8765`, Freedoom E1M1, `/doom/camera` as `CompressedImage`, Teleop Twist on `/cmd_vel` moves the marine, `/doom/buttons` fires. One smoke command from a clean shell.
- [ ] `cap_3d_map_hud` — `/doom/map` grid, `/tf` player transform, `/doom/entities` SceneUpdate, health/armor/ammo gauges, `/doom/log`, exported `Play` and `Debug` layouts.
- [ ] `cap_embed_page` — Host page embeds Foxglove, parent-owned live transport, WASD/Space keybindings publish the same topics, layout switcher for `Play` / `Debug`.
- [ ] `cap_mcap_replay` — Same SDK code writes MCAP; `Replay` layout loads it; Teleop hidden; playback bar works.
- [ ] `cap_stunt_extras` — Deferred. Events, comparison, agent prompts, remote spectator. Not started until the first three capabilities are `done`.

## Topic contract

Keep schemas in Foxglove/ROS types so stock panels work with zero extensions:

- `/doom/camera` — `foxglove.CompressedImage`
- `/tf` — `foxglove.FrameTransforms` (`map` → `base_link`)
- `/doom/map` — `foxglove.Grid` once per level
- `/doom/entities` — `foxglove.SceneUpdate`
- `/doom/player` — compact JSON: health, armor, ammo, weapon, tick, dead
- `/doom/log` — `foxglove.Log`
- `/cmd_vel` — `geometry_msgs/Twist` (client publish)
- `/doom/buttons` — JSON `{ fire, use, weapon }` (client publish)

Engine maps Twist to ViZDoom buttons at 35 Hz; zeros on Teleop stop-on-release.

## Non-goals

An agent that produces any of these has drifted and its work is restarted against its contract.

- ROS bridge, rosbridge, or a native ROS stack
- Custom HUD extension in v1
- Mouse-look, true FPS aiming, multiplayer deathmatch
- Commercial IWAD redistribution
- A general game engine
- Map-panel lat/lon fakery
- Audio
- Cloud recording upload, remote-access gateway, or comparison mode before `05` is un-deferred
- Spawning Claude, GPT, Composer, or `inherit`

## Where the rest of the state lives

- `.agent/COORDINATION.md` — roles, allowed models, handoff packet, DAG, stop/restart/escalate, resume order
- `.agent/knowledge-graph/` — schema, nodes, edges, validator
- `.agent/workstreams/<nn>-<name>/` — `PLAN.md` (phase spec), `contract.md`, `progress.md`, `log.md`
- `.agent/loops/README.md` — eval-after-generator and knowledge-graph sync

Workstream order for product code: `01-hero-loop` → `02-robotics-layout` → `03-embed-shell` → `04-record-replay`. `05-stunt-extras` is deferred. `00-harness` is the durable state layer and must evaluate before any product generator runs.
