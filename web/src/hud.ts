const PLAYER_TOPIC = "/doom/player";
const HEALTH_MAX = 200;
const ARMOR_MAX = 200;
const AMMO_MAX = 300;

export type PlayerHud = {
  health: number;
  armor: number;
  ammo: number;
};

function clampPct(value: number, max: number): number {
  if (!Number.isFinite(value) || max <= 0) {
    return 0;
  }
  return Math.max(0, Math.min(100, (value / max) * 100));
}

export function paintHudBars(player: PlayerHud): void {
  const health = document.getElementById("hud-health");
  const armor = document.getElementById("hud-armor");
  const ammo = document.getElementById("hud-ammo");
  if (health) {
    health.style.width = `${clampPct(player.health, HEALTH_MAX)}%`;
  }
  if (armor) {
    armor.style.width = `${clampPct(player.armor, ARMOR_MAX)}%`;
  }
  if (ammo) {
    ammo.style.width = `${clampPct(player.ammo, AMMO_MAX)}%`;
  }
}

function extractJson(data: ArrayBuffer | string): unknown | undefined {
  if (typeof data === "string") {
    try {
      return JSON.parse(data);
    } catch {
      return undefined;
    }
  }
  const text = new TextDecoder().decode(data);
  const start = text.indexOf("{");
  if (start < 0) {
    return undefined;
  }
  try {
    return JSON.parse(text.slice(start));
  } catch {
    return undefined;
  }
}

function asPlayer(value: unknown): PlayerHud | undefined {
  if (!value || typeof value !== "object") {
    return undefined;
  }
  const rec = value as Record<string, unknown>;
  if (typeof rec.health !== "number") {
    return undefined;
  }
  return {
    health: rec.health,
    armor: typeof rec.armor === "number" ? rec.armor : 0,
    ammo: typeof rec.ammo === "number" ? rec.ammo : 0,
  };
}

/** Parent WS subscribe to /doom/player JSON for the host HTML bars. */
export function subscribePlayerHud(wsUrl: string): () => void {
  let socket: WebSocket | undefined;
  try {
    socket = new WebSocket(wsUrl, ["foxglove.sdk.v1", "foxglove.websocket.v1"]);
  } catch {
    return () => undefined;
  }
  socket.binaryType = "arraybuffer";
  let playerChannelId: number | undefined;
  socket.onmessage = (event: MessageEvent<string | ArrayBuffer>) => {
    const parsed = extractJson(event.data);
    if (!parsed || typeof parsed !== "object") {
      return;
    }
    const msg = parsed as Record<string, unknown>;
    if (msg.op === "advertise") {
      const channels = Array.isArray(msg.channels) ? msg.channels : [];
      for (const channel of channels) {
        if (!channel || typeof channel !== "object") {
          continue;
        }
        const rec = channel as Record<string, unknown>;
        if (rec.topic === PLAYER_TOPIC && typeof rec.id === "number") {
          playerChannelId = rec.id;
          if (socket && socket.readyState === WebSocket.OPEN) {
            socket.send(
              JSON.stringify({
                op: "subscribe",
                subscriptions: [{ id: 1, channelId: rec.id }],
              }),
            );
          }
        }
      }
      return;
    }
    const player = asPlayer(parsed);
    if (player) {
      paintHudBars(player);
    }
    void playerChannelId;
  };
  return () => {
    socket?.close();
  };
}
