import { FoxgloveViewer } from "@foxglove/embed";
import { isSecureContext, readInitialLayout, readOrgSlug, readWsUrl, type LayoutName } from "./config";
import { doomKeybindings, HoldController } from "./keybindings";
import { layoutIncludesTeleop, layoutParams, playLayoutData } from "./layouts";
import { ClientPublisher } from "./publish";
import "./styles.css";
import {
  createDoomTransport,
  iframeOwnedLiveSource,
  parentOwnedLiveSource,
} from "./transport";

function requireEl<T extends HTMLElement>(id: string): T {
  const el = document.getElementById(id);
  if (!el) {
    throw new Error(`missing #${id}`);
  }
  return el as T;
}

function setStatus(text: string): void {
  requireEl("status").textContent = text;
}

if (!layoutIncludesTeleop(playLayoutData)) {
  throw new Error("Play layout is missing the Teleop panel; WASD must not replace it");
}

const wsUrl = readWsUrl();
requireEl("ws-url").textContent = wsUrl;

if (!isSecureContext()) {
  requireEl("secure-warning").hidden = false;
  setStatus("Blocked: not a secure context.");
} else {
  const parent = requireEl<HTMLElement>("foxglove");
  const publisher = new ClientPublisher();
  const hold = new HoldController(publisher);
  hold.start();
  const transport = createDoomTransport(publisher);

  const viewer = new FoxgloveViewer({
    parent,
    orgSlug: readOrgSlug(),
    colorScheme: "dark",
    keybindings: doomKeybindings(hold),
    initialLayoutParams: layoutParams(readInitialLayout()),
  });

  const markLayout = (name: LayoutName): void => {
    requireEl("layout-play").setAttribute("aria-pressed", name === "play" ? "true" : "false");
    requireEl("layout-debug").setAttribute("aria-pressed", name === "debug" ? "true" : "false");
  };
  markLayout(readInitialLayout());

  requireEl("layout-play").addEventListener("click", () => {
    viewer.selectLayout(layoutParams("play"));
    markLayout("play");
  });
  requireEl("layout-debug").addEventListener("click", () => {
    viewer.selectLayout(layoutParams("debug"));
    markLayout("debug");
  });

  const connectFromCapabilities = (): void => {
    let status: "pending" | "available" | "unavailable" = "unavailable";
    try {
      status = viewer.getCapabilities().parentOwnedLiveTransport;
    } catch {
      status = "unavailable";
    }
    if (status === "pending") {
      setStatus("Waiting for embed capabilities (sign in if prompted)…");
      return;
    }
    if (status === "available") {
      viewer.setDataSource(parentOwnedLiveSource(wsUrl, transport));
      setStatus(`Parent-owned live transport → ${wsUrl}`);
      return;
    }
    viewer.setDataSource(iframeOwnedLiveSource(wsUrl));
    publisher.connectDirect(wsUrl);
    setStatus(`Iframe-owned live WS; WASD publishes on a second parent socket → ${wsUrl}`);
  };

  viewer.addEventListener("ready", () => {
    viewer.setKeybindings(doomKeybindings(hold));
    viewer.selectLayout(layoutParams(readInitialLayout()));
    connectFromCapabilities();
  });
  viewer.addEventListener("capabilities", connectFromCapabilities);
  viewer.addEventListener("error", (event) => {
    setStatus(`Embed error: ${event.detail}`);
  });
  connectFromCapabilities();

  window.addEventListener("beforeunload", () => {
    hold.stop();
    publisher.close();
    viewer.destroy();
  });
}
