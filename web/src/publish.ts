import {
  BUTTONS_CHANNEL_ID,
  BUTTONS_TOPIC,
  CMD_VEL_CHANNEL_ID,
  CMD_VEL_TOPIC,
} from "./config";

const CLIENT_MESSAGE_DATA = 0x01;
const encoder = new TextEncoder();

const TWIST_SCHEMA = JSON.stringify({
  type: "object",
  additionalProperties: true,
  properties: {
    linear: {
      type: "object",
      properties: {
        x: { type: "number" },
        y: { type: "number" },
        z: { type: "number" },
      },
    },
    angular: {
      type: "object",
      properties: {
        x: { type: "number" },
        y: { type: "number" },
        z: { type: "number" },
      },
    },
  },
});

const BUTTONS_SCHEMA = JSON.stringify({
  type: "object",
  additionalProperties: false,
  properties: {
    fire: { type: "boolean" },
    use: { type: "boolean" },
    weapon: { type: ["integer", "null"] },
  },
  required: ["fire", "use"],
});

export type Twist = {
  linear: { x: number; y: number; z: number };
  angular: { x: number; y: number; z: number };
};

export type Buttons = {
  fire: boolean;
  use: boolean;
  weapon: number | null;
};

export const ZERO_TWIST: Twist = {
  linear: { x: 0, y: 0, z: 0 },
  angular: { x: 0, y: 0, z: 0 },
};

export function clientAdvertiseJson(): string {
  return JSON.stringify({
    op: "advertise",
    channels: [
      {
        id: CMD_VEL_CHANNEL_ID,
        topic: CMD_VEL_TOPIC,
        encoding: "json",
        schemaName: "geometry_msgs/Twist",
        schemaEncoding: "jsonschema",
        schema: TWIST_SCHEMA,
      },
      {
        id: BUTTONS_CHANNEL_ID,
        topic: BUTTONS_TOPIC,
        encoding: "json",
        schemaName: "doom.Buttons",
        schemaEncoding: "jsonschema",
        schema: BUTTONS_SCHEMA,
      },
    ],
  });
}

export function clientMessageFrame(channelId: number, payload: unknown): ArrayBuffer {
  const bytes = encoder.encode(JSON.stringify(payload));
  const frame = new ArrayBuffer(5 + bytes.byteLength);
  const view = new DataView(frame);
  view.setUint8(0, CLIENT_MESSAGE_DATA);
  view.setUint32(1, channelId, true);
  new Uint8Array(frame, 5).set(bytes);
  return frame;
}

export type FrameSender = (frame: string | ArrayBuffer) => void;

export class ClientPublisher {
  private sendFn: FrameSender | undefined;
  private advertised = false;
  private direct: WebSocket | undefined;

  get attached(): boolean {
    return this.sendFn !== undefined;
  }

  attach(send: FrameSender): void {
    this.dropDirect();
    this.sendFn = send;
    this.advertised = false;
    this.advertise();
  }

  detach(): void {
    this.sendFn = undefined;
    this.advertised = false;
  }

  /** Second parent socket used only when the iframe owns the live connection. */
  connectDirect(url: string): void {
    this.dropDirect();
    const socket = new WebSocket(url, ["foxglove.websocket.v1"]);
    socket.binaryType = "arraybuffer";
    this.direct = socket;
    socket.onopen = () => {
      this.sendFn = (frame) => {
        if (socket.readyState === WebSocket.OPEN) {
          socket.send(frame);
        }
      };
      this.advertised = false;
      this.advertise();
    };
    socket.onerror = () => {
      /* status is owned by the host page */
    };
  }

  publishTwist(twist: Twist): void {
    this.sendFrame(clientMessageFrame(CMD_VEL_CHANNEL_ID, twist));
  }

  publishButtons(buttons: Buttons): void {
    this.sendFrame(clientMessageFrame(BUTTONS_CHANNEL_ID, buttons));
  }

  close(): void {
    this.detach();
    this.dropDirect();
  }

  private advertise(): void {
    if (this.advertised) {
      return;
    }
    this.advertised = true;
    this.sendFrame(clientAdvertiseJson());
  }

  private sendFrame(frame: string | ArrayBuffer): void {
    this.sendFn?.(frame);
  }

  private dropDirect(): void {
    if (this.direct) {
      this.direct.onopen = null;
      this.direct.onerror = null;
      this.direct.close();
      this.direct = undefined;
    }
  }
}
