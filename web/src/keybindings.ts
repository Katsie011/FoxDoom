import type { Keybinding } from "@foxglove/embed";
import { HOLD_TIMEOUT_MS, TICK_HZ } from "./config";
import { ZERO_TWIST, type Buttons, type ClientPublisher, type Twist } from "./publish";

export type Motion = {
  forward: boolean;
  back: boolean;
  left: boolean;
  right: boolean;
  fire: boolean;
};

const IDLE: Motion = {
  forward: false,
  back: false,
  left: false,
  right: false,
  fire: false,
};

export function twistFromMotion(motion: Motion): Twist {
  const linearX = (motion.forward ? 1 : 0) + (motion.back ? -1 : 0);
  const angularZ = (motion.left ? 1 : 0) + (motion.right ? -1 : 0);
  return {
    linear: { x: linearX, y: 0, z: 0 },
    angular: { x: 0, y: 0, z: angularZ },
  };
}

export function buttonsFromMotion(motion: Motion): Buttons {
  return { fire: motion.fire, use: false, weapon: null };
}

export function motionActive(motion: Motion): boolean {
  return motion.forward || motion.back || motion.left || motion.right || motion.fire;
}

type Field = keyof Motion;
export type MotionListener = (motion: Motion) => void;

const KEY_HUD_FIELDS: { field: Field; label: string }[] = [
  { field: "forward", label: "W" },
  { field: "left", label: "A" },
  { field: "back", label: "S" },
  { field: "right", label: "D" },
  { field: "fire", label: "Space" },
];

/**
 * WASD tank controls + Space fire. setKeybindings only reports presses inside
 * the iframe, so a short hold timeout plus parent keyup gives stop-on-release.
 */
export class HoldController {
  private motion: Motion = { ...IDLE };
  private lastSeen: Record<Field, number> = {
    forward: 0,
    back: 0,
    left: 0,
    right: 0,
    fire: 0,
  };
  private timer: number | undefined;
  private lastTwist = JSON.stringify(ZERO_TWIST);
  private lastFire = false;
  private listeners: MotionListener[] = [];

  constructor(private readonly publisher: ClientPublisher) {}

  subscribe(onMotion: MotionListener): () => void {
    this.listeners.push(onMotion);
    onMotion({ ...this.motion });
    return () => {
      this.listeners = this.listeners.filter((listener) => listener !== onMotion);
    };
  }

  press(field: Field): void {
    this.motion[field] = true;
    this.lastSeen[field] = Date.now();
    this.ensureTimer();
    this.flush(true);
  }

  release(field: Field): void {
    this.motion[field] = false;
    this.flush(true);
    if (!motionActive(this.motion)) {
      this.stopTimer();
    }
  }

  releaseAll(): void {
    this.motion = { ...IDLE };
    this.flush(true);
    this.stopTimer();
  }

  start(): void {
    if (typeof window === "undefined") {
      return;
    }
    window.addEventListener("keyup", this.onWindowKeyUp);
    window.addEventListener("blur", this.onBlur);
  }

  stop(): void {
    if (typeof window === "undefined") {
      return;
    }
    window.removeEventListener("keyup", this.onWindowKeyUp);
    window.removeEventListener("blur", this.onBlur);
    this.releaseAll();
  }

  private onWindowKeyUp = (event: KeyboardEvent): void => {
    const field = fieldFromCode(event.code);
    if (field) {
      this.release(field);
    }
  };

  private onBlur = (): void => {
    this.releaseAll();
  };

  private ensureTimer(): void {
    if (this.timer !== undefined || typeof window === "undefined") {
      return;
    }
    const period = 1000 / TICK_HZ;
    this.timer = window.setInterval(() => {
      const now = Date.now();
      (Object.keys(this.lastSeen) as Field[]).forEach((field) => {
        if (this.motion[field] && now - this.lastSeen[field] > HOLD_TIMEOUT_MS) {
          this.motion[field] = false;
        }
      });
      this.flush(false);
      if (!motionActive(this.motion)) {
        this.stopTimer();
      }
    }, period);
  }

  private stopTimer(): void {
    if (this.timer !== undefined) {
      window.clearInterval(this.timer);
      this.timer = undefined;
    }
  }

  private flush(force: boolean): void {
    const twist = twistFromMotion(this.motion);
    const twistJson = JSON.stringify(twist);
    if (force || twistJson !== this.lastTwist) {
      this.publisher.publishTwist(twist);
      this.lastTwist = twistJson;
    } else if (motionActive(this.motion) && (this.motion.forward || this.motion.back || this.motion.left || this.motion.right)) {
      this.publisher.publishTwist(twist);
    }
    if (force || this.motion.fire !== this.lastFire) {
      this.publisher.publishButtons(buttonsFromMotion(this.motion));
      this.lastFire = this.motion.fire;
    }
    const snapshot = { ...this.motion };
    for (const onMotion of this.listeners) {
      onMotion(snapshot);
    }
  }
}

export function bindKeyHud(hold: HoldController): void {
  const root = document.getElementById("key-hud");
  if (!root) {
    return;
  }
  const keys = new Map<Field, HTMLElement>();
  KEY_HUD_FIELDS.forEach(({ field }) => {
    const el = root.querySelector<HTMLElement>(`[data-key="${field}"]`);
    if (el) {
      keys.set(field, el);
    }
  });
  hold.subscribe((motion) => {
    keys.forEach((el, field) => {
      const on = motion[field];
      el.classList.toggle("pressed", on);
      el.setAttribute("aria-pressed", on ? "true" : "false");
    });
  });
}

function fieldFromCode(code: string): Field | undefined {
  switch (code) {
    case "KeyW":
      return "forward";
    case "KeyS":
      return "back";
    case "KeyA":
      return "left";
    case "KeyD":
      return "right";
    case "Space":
      return "fire";
    default:
      return undefined;
  }
}

export function doomKeybindings(hold: HoldController): Keybinding[] {
  return [
    { key: "KeyW", handler: () => hold.press("forward") },
    { key: "KeyA", handler: () => hold.press("left") },
    { key: "KeyS", handler: () => hold.press("back") },
    { key: "KeyD", handler: () => hold.press("right") },
    { key: "Space", handler: () => hold.press("fire") },
    { key: " ", command: "noop" },
  ];
}
