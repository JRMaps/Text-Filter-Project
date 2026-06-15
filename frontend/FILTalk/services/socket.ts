import Constants from "expo-constants";
import { Platform } from "react-native";

let socket: WebSocket | null = null;
type MessageCallback = (message: any) => void;
let messageListeners: MessageCallback[] = [];

// HELPER: Strips http, https, ws, wss from the start of a string
const stripProtocol = (url: string): string => {
  return url.replace(/^(http|https|ws|wss):\/\//, "").replace(/\/$/, "");
};

const getSocketUrl = (): string => {
  let host = "192.168.254.119:8000"; // Default to your known working IP

  // 1. Try .env first
  if (process.env.EXPO_PUBLIC_API_URL) {
    host = stripProtocol(process.env.EXPO_PUBLIC_API_URL.trim());
  }
  // 2. Try Expo Device IP (Physical Device)
  else {
    const hostUri = Constants.expoConfig?.hostUri || Constants.hostUri;
    if (hostUri) {
      host = hostUri.split(":")[0] + ":8000";
    }
  }

  return `ws://${host}/ws`;
};

export const connectSocket = (token: string) => {
  // 1. Safety Check
  if (!token || token === "dev-token") {
    console.log("[WebSocket] Skipped connection: Invalid token");
    return;
  }

  // 2. Prevent duplicate connections
  if (
    socket &&
    (socket.readyState === WebSocket.OPEN ||
      socket.readyState === WebSocket.CONNECTING)
  ) {
    console.log("[WebSocket] Already connected.");
    return;
  }

  const url = `${getSocketUrl()}?token=${token}`;
  console.log("[WebSocket] Connecting to:", url);

  try {
    socket = new WebSocket(url);

    socket.onopen = () => {
      console.log("[WebSocket] Connected successfully!");
    };

    socket.onmessage = (e) => {
      try {
        const data = JSON.parse(e.data);
        console.log("[WebSocket] Received:", data); // Debug log to see event types
        messageListeners.forEach((listener) => listener(data));
      } catch (err) {
        console.log("[WebSocket] Parse error:", err);
      }
    };

    socket.onerror = (e: any) => {
      console.log("[WebSocket] Error:", e.message);
    };

    socket.onclose = () => {
      console.log("[WebSocket] Connection closed");
      socket = null;
    };
  } catch (err) {
    console.log("[WebSocket] Init error:", err);
  }
};

export const onMessageReceived = (callback: MessageCallback) => {
  messageListeners.push(callback);
  // Return a cleanup function
  return () => {
    messageListeners = messageListeners.filter((l) => l !== callback);
  };
};

export const sendMessage = (message: any) => {
  if (socket?.readyState === WebSocket.OPEN) {
    socket.send(JSON.stringify(message));
  } else {
    console.warn("[WebSocket] Not connected. Message dropped:", message);
  }
};

export const disconnectSocket = () => {
  if (socket) {
    socket.close();
    socket = null;
    messageListeners = [];
  }
};
