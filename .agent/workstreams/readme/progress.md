status: done
owner: Supervisor
updated: 2026-09-18
next action: none — all 20 RD items ticked; rubric 0.85 ≥ 0.75
blockers: none
failing ids: none

# Progress — readme

Root `README.md` rewrite. Not a numbered product phase. Must not create `.agent/workstreams/06-*` (04 PR-10).

## Why (seed, locked by GOAL.md)

Foxglove already teleoperates robots. This repo asks whether the same product can teleoperate a DOOM marine through **stock panels**. If the camera is an Image subscription and Twist comes from Teleop, Foxglove is the UI. A canvas next to Foxglove is the failed stunt.

## State

Generator inserted a `flowchart TB` mermaid fence into the README preface: after the unchanged why paragraph, closed before `## Run`. Foxglove grouping is `subgraph foxglove["Foxglove"]` plus `classDef fox` classing sdk / Image / 3D / Teleop / Gauge / embed / app. Why / Run / frozen Replay / Ask / Not-in-this-slice / Build notes stay. No `## Architecture` heading. No PNG. No contract ticks. RD-19/RD-20 stay unchecked.

Generator self-check (not a grade): RD-19 and RD-20 Check blocks PASS; RD-01 first `##` is still `## Run` with mermaid closed before it; RD-02…RD-16 and RD-18 still PASS on this file.

## What's left

Nothing. Evaluator (kimi-k3-high) ran RD-19 / RD-20 verbatim — PASS — re-ran RD-01 against the new preface — PASS — and sampled RD-06 / RD-08 / RD-10 with no regression. RD-19 / RD-20 ticked. Rubric 0.85 ≥ 0.75 (first-screen 0.8: the 41-line fence pushes the run command just past screen one). Evidence and skipped-item list in `eval.md`.
