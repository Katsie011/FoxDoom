import playLayout from "../../layouts/Play.json";
import debugLayout from "../../layouts/Debug.json";
import { DEBUG_STORAGE_KEY, PLAY_STORAGE_KEY, type LayoutName } from "./config";

export const playLayoutData: unknown = playLayout;
export const debugLayoutData: unknown = debugLayout;

export type SelectLayoutParams = {
  storageKey: string;
  opaqueLayout?: unknown;
  force?: boolean;
};

export function layoutParams(name: LayoutName): SelectLayoutParams {
  if (name === "debug") {
    return {
      storageKey: DEBUG_STORAGE_KEY,
      opaqueLayout: debugLayoutData,
      force: true,
    };
  }
  return {
    storageKey: PLAY_STORAGE_KEY,
    opaqueLayout: playLayoutData,
    force: true,
  };
}

export function layoutIncludesTeleop(data: unknown): boolean {
  return JSON.stringify(data).includes("Teleop");
}
