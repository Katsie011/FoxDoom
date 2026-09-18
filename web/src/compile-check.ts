/**
 * Headless compile check: FoxgloveViewer constructor options, selectLayout
 * params, live data sources, and WASD keybindings must typecheck.
 * This module is not imported by the page; `tsc --noEmit` is the smoke.
 */
import { FoxgloveViewer } from "@foxglove/embed";
import type { Keybinding, ParentTransportFactory, ShortcutKey } from "@foxglove/embed";
import { BUTTONS_TOPIC, CMD_VEL_TOPIC, REPLAY_STORAGE_KEY } from "./config";
import { doomKeybindings, HoldController, twistFromMotion } from "./keybindings";
import { layoutIncludesTeleop, layoutParams, playLayoutData, replayLayoutData } from "./layouts";
import { ClientPublisher, clientAdvertiseJson, ZERO_TWIST } from "./publish";
import {
  createDoomTransport,
  iframeOwnedLiveSource,
  parentOwnedLiveSource,
} from "./transport";

type ViewerOptions = ConstructorParameters<typeof FoxgloveViewer>[0];
type SelectLayoutParams = Parameters<FoxgloveViewer["selectLayout"]>[0];
type DataSource = Parameters<FoxgloveViewer["setDataSource"]>[0];

const dummyParent = {} as HTMLElement;
const publisher = new ClientPublisher();
const hold = new HoldController(publisher);
const keybindings: Keybinding[] = doomKeybindings(hold);
const transport: ParentTransportFactory = createDoomTransport(publisher);

export const foxgloveViewerOptionsCompileCheck: ViewerOptions = {
  parent: dummyParent,
  orgSlug: undefined,
  colorScheme: "dark",
  keybindings,
  initialLayoutParams: layoutParams("play"),
};

export const playSelectLayoutCompileCheck: SelectLayoutParams = layoutParams("play");
export const debugSelectLayoutCompileCheck: SelectLayoutParams = layoutParams("debug");
export const replaySelectLayoutCompileCheck: SelectLayoutParams = {
  storageKey: REPLAY_STORAGE_KEY,
  layout: replayLayoutData,
  force: true,
};
export const fileSourceCompileCheck: DataSource = {
  type: "file",
  file: new File([new Uint8Array()], "smoke.mcap"),
  autoplay: true,
};

export const parentOwnedSourceCompileCheck: DataSource = parentOwnedLiveSource(
  "ws://localhost:8765",
  transport,
);
export const iframeOwnedSourceCompileCheck: DataSource = iframeOwnedLiveSource(
  "ws://localhost:8765",
);

const advertised = clientAdvertiseJson();
if (!advertised.includes(CMD_VEL_TOPIC) || !advertised.includes(BUTTONS_TOPIC)) {
  throw new Error("client advertise JSON must name /cmd_vel and /doom/buttons");
}
if (!layoutIncludesTeleop(playLayoutData)) {
  throw new Error("Play layout must keep the Teleop panel");
}
if (JSON.stringify(twistFromMotion({
  forward: false,
  back: false,
  left: false,
  right: false,
  fire: false,
})) !== JSON.stringify(ZERO_TWIST)) {
  throw new Error("idle WASD must publish a zero Twist");
}

const keys = new Set(keybindings.map((binding) => binding.key));
const needed: ShortcutKey[] = ["KeyW", "KeyA", "KeyS", "KeyD", "Space"];
for (const need of needed) {
  if (!keys.has(need)) {
    throw new Error(`missing keybinding ${need}`);
  }
}
