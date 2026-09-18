import { FoxgloveViewer } from "@foxglove/embed";
import { isSecureContext, readControlUrl, readInitialLayout, readOrgSlug, readWsUrl, type LayoutName } from "./config";
import { subscribePlayerHud } from "./hud";
import { bindKeyHud, doomKeybindings, HoldController } from "./keybindings";
import { layoutIncludesTeleop, layoutParams, playLayoutData, replayLayoutParams } from "./layouts";
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
  bindKeyHud(hold);
  const stopPlayerHud = subscribePlayerHud(wsUrl);
  const transport = createDoomTransport(publisher);
  let replayActive = false;

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

  const setReplayFilesHidden = (hidden: boolean): void => {
    requireEl("replay-files").hidden = hidden;
  };

  const controlBase = (): string => readControlUrl().replace(/\/$/, "");

  const loadReplayBlob = async (blob: Blob, name: string): Promise<void> => {
    const file = new File([blob], name);
    hold.stop();
    replayActive = true;
    setReplayFilesHidden(false);
    viewer.setDataSource({ type: "file", file, autoplay: true });
    viewer.selectLayout(replayLayoutParams());
  };

  const refreshReplayFiles = async (): Promise<void> => {
    const list = requireEl("replay-files");
    list.replaceChildren();
    try {
      const recs = await fetch(`${controlBase()}/recordings`);
      if (!recs.ok) {
        return;
      }
      const items: unknown = await recs.json();
      const rows = Array.isArray(items) ? items : [];
      for (const item of rows) {
        if (!item || typeof item !== "object") {
          continue;
        }
        const name = String((item as { name?: string }).name ?? "");
        if (!name.startsWith("doom-") || !name.endsWith(".mcap")) {
          continue;
        }
        const button = document.createElement("button");
        button.type = "button";
        button.textContent = name;
        button.addEventListener("click", () => {
          void (async () => {
            const rec = await fetch(`${controlBase()}/recording?name=${encodeURIComponent(name)}`);
            if (!rec.ok) {
              setStatus(`Replay file failed: GET /recording?name= ${rec.status}`);
              return;
            }
            await loadReplayBlob(await rec.blob(), name);
            setStatus(`FileSource replay ${name}`);
          })();
        });
        list.append(button);
      }
    } catch (err) {
      setStatus(`Replay list failed: ${err}`);
    }
  };

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
    replayActive = false;
    setReplayFilesHidden(true);
    if (status === "available") {
      viewer.setDataSource(parentOwnedLiveSource(wsUrl, transport));
      setStatus(`Parent-owned live transport → ${wsUrl}`);
      return;
    }
    viewer.setDataSource(iframeOwnedLiveSource(wsUrl));
    publisher.connectDirect(wsUrl);
    setStatus(`Iframe-owned live WS; WASD publishes on a second parent socket → ${wsUrl}`);
  };

  requireEl("layout-play").addEventListener("click", () => {
    void (async () => {
      if (replayActive) {
        try {
          await fetch(`${controlBase()}/new-game`, { method: "POST" });
        } catch (err) {
          setStatus(`Play new-game failed: ${err}`);
        }
        hold.start();
        connectFromCapabilities();
      }
      viewer.selectLayout(layoutParams("play"));
      markLayout("play");
    })();
  });
  requireEl("layout-debug").addEventListener("click", () => {
    viewer.selectLayout(layoutParams("debug"));
    markLayout("debug");
  });

  requireEl("pause-replay").addEventListener("click", () => {
    void (async () => {
      const controlUrl = controlBase();
      try {
        await fetch(`${controlUrl}/pause`, { method: "POST" });
        const rec = await fetch(`${controlUrl}/recording`);
        if (rec.status === 409) {
          hold.stop();
          setStatus("Paused, but recording is off.");
          return;
        }
        if (!rec.ok) {
          setStatus(`Pause & replay failed: GET /recording ${rec.status}`);
          return;
        }
        await loadReplayBlob(await rec.blob(), "doom.mcap");
        await refreshReplayFiles();
        setStatus("Paused; FileSource replay loaded.");
      } catch (err) {
        setStatus(`Pause & replay failed: ${err}`);
      }
    })();
  });

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
    stopPlayerHud();
    viewer.destroy();
  });
}
