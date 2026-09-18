import type { Layout } from "@foxglove/embed";
import playLayout from "../../layouts/Play.json";
import debugLayout from "../../layouts/Debug.json";
import replayLayout from "../../layouts/Replay.json";
import { DEBUG_STORAGE_KEY, PLAY_STORAGE_KEY, REPLAY_STORAGE_KEY, type LayoutName } from "./config";

export const playLayoutData = playLayout as Layout;
export const debugLayoutData = debugLayout as Layout;
export const replayLayoutData = replayLayout as Layout;

export type SelectLayoutParams = {
  storageKey: string;
  layout?: Layout;
  force?: boolean;
};

export function layoutParams(name: LayoutName): SelectLayoutParams {
  if (name === "debug") {
    return {
      storageKey: DEBUG_STORAGE_KEY,
      layout: debugLayoutData,
      force: true,
    };
  }
  return {
    storageKey: PLAY_STORAGE_KEY,
    layout: playLayoutData,
    force: true,
  };
}

export function replayLayoutParams(): SelectLayoutParams {
  return {
    storageKey: REPLAY_STORAGE_KEY,
    layout: replayLayoutData,
    force: true,
  };
}

export function layoutIncludesTeleop(data: unknown): boolean {
  return JSON.stringify(data).includes("Teleop");
}
