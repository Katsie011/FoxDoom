# PLAN — 04-record-replay

Phase 4 of the product plan. Deferred until `03-embed-shell` is evaluated `done` (`cap_embed_page`).

## Spec (from the product plan, not rewritten)

- **MCAP logging with the same SDK code** — every session is a recording. Same layout for live and replay. This is the live-to-playback story.
- **Replay layout** — load the MCAP; hide Teleop; show playback bar. Website follow-up: every run is data.
- Optional **shareable recording link** — tweet a run, open it in Foxglove. Cloud upload may wait for `05` if it needs Data Platform.

Host controls this with `setDataSource({ type: "live" | "remote-file" | "recording" })`.

## Out of this phase

Events tagging, comparison mode, built-in agent, remote spectator, unless a later `05` contract pulls them in. Do not start those here.
