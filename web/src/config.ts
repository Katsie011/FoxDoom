/** Same topics the Teleop panel and Python server already use. */
export const CMD_VEL_TOPIC = "/cmd_vel";
export const BUTTONS_TOPIC = "/doom/buttons";

export const DEFAULT_WS_URL = "ws://localhost:8765";
export const TICK_HZ = 35;
export const HOLD_TIMEOUT_MS = 900;

export const CMD_VEL_CHANNEL_ID = 9001;
export const BUTTONS_CHANNEL_ID = 9002;

export const PLAY_STORAGE_KEY = "foxglove-doom-play";
export const DEBUG_STORAGE_KEY = "foxglove-doom-debug";

export type LayoutName = "play" | "debug";

function firstQuery(name: string): string | undefined {
  if (typeof window === "undefined") {
    return undefined;
  }
  const value = new URLSearchParams(window.location.search).get(name);
  return value && value.length > 0 ? value : undefined;
}

export function readWsUrl(): string {
  return firstQuery("ws") ?? import.meta.env.VITE_FOXGLOVE_WS ?? DEFAULT_WS_URL;
}

export function readOrgSlug(): string | undefined {
  const fromQuery = firstQuery("org");
  if (fromQuery) {
    return fromQuery;
  }
  const fromEnv = import.meta.env.VITE_FOXGLOVE_ORG;
  return fromEnv && fromEnv.length > 0 ? fromEnv : undefined;
}

export function readInitialLayout(): LayoutName {
  const value = (firstQuery("layout") ?? "play").toLowerCase();
  return value === "debug" ? "debug" : "play";
}

export function isSecureContext(): boolean {
  if (typeof window === "undefined") {
    return true;
  }
  return window.isSecureContext;
}
