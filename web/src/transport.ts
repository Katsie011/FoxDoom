import type { ParentTransportFactory } from "@foxglove/embed";
import type { ClientPublisher } from "./publish";

/**
 * Parent-owned Foxglove WebSocket: the host opens the socket so the iframe
 * never has to guess CORS. WASD publish rides the same connection via ClientPublisher.
 */
export function createDoomTransport(publisher: ClientPublisher): ParentTransportFactory {
  return ({ url, protocols, onOpen, onMessage, onError, onClose }) => {
    const socket = new WebSocket(url, [...protocols]);
    socket.binaryType = "arraybuffer";
    socket.onopen = () => {
      onOpen(socket.protocol);
      publisher.attach((frame) => {
        if (socket.readyState === WebSocket.OPEN) {
          socket.send(frame);
        }
      });
    };
    socket.onmessage = (event: MessageEvent<string | ArrayBuffer>) => {
      onMessage(event.data);
    };
    socket.onerror = () => {
      onError(new Error(`WebSocket connection failed: ${url}`));
    };
    socket.onclose = (event) => {
      publisher.detach();
      onClose({ code: event.code, reason: event.reason, wasClean: event.wasClean });
    };
    return {
      send: (frame) => {
        if (socket.readyState === WebSocket.OPEN) {
          socket.send(frame);
        }
      },
      close: () => {
        publisher.detach();
        if (socket.readyState === WebSocket.OPEN || socket.readyState === WebSocket.CONNECTING) {
          socket.close();
        }
      },
    };
  };
}

export type LiveDataSource = {
  type: "live";
  protocol: "foxglove-websocket";
  url: string;
  transport?: ParentTransportFactory;
};

export function parentOwnedLiveSource(
  url: string,
  transport: ParentTransportFactory,
): LiveDataSource {
  return {
    type: "live",
    protocol: "foxglove-websocket",
    url,
    transport,
  };
}

export function iframeOwnedLiveSource(url: string): LiveDataSource {
  return {
    type: "live",
    protocol: "foxglove-websocket",
    url,
  };
}
