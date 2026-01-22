import AsyncStorage from "@react-native-async-storage/async-storage";
import Constants from "expo-constants";
import { Platform } from "react-native";
import { router } from "expo-router";

// ============ CONFIGURATION ============

const resolveApiOrigin = (): string => {
  const myComputerIp = "192.168.254.201";
  const hostUri = Constants.expoConfig?.hostUri || Constants.hostUri;
  if (typeof hostUri === "string" && hostUri.length > 0) {
    const host = hostUri.split(":")[0];
    return `http://${host}:8000`;
  }
  return Platform.OS === "android" || Platform.OS === "ios"
    ? `http://${myComputerIp}:8000`
    : "http://localhost:8000";
};

const API_BASE_URL = `${resolveApiOrigin()}/api`;
const TOKEN_KEY = "auth_token";

// ============ HELPERS ============

export const getToken = async (): Promise<string | null> => {
  try {
    const token = await AsyncStorage.getItem(TOKEN_KEY);
    return token ? token.replace(/["\n\r]/g, "").trim() : null;
  } catch {
    return null;
  }
};

export const setToken = async (token: string): Promise<void> => {
  await AsyncStorage.setItem(TOKEN_KEY, token);
};

export const removeToken = async (): Promise<void> => {
  await AsyncStorage.removeItem(TOKEN_KEY);
};

const forceLogout = async () => {
  console.warn("[AUTH] Session expired (401). Logging out...");
  await removeToken();
  router.replace("/login");
};

const fetchWithAuth = async (
  endpoint: string,
  options: RequestInit = {},
): Promise<Response> => {
  const publicRoutes = [
    "/auth/login",
    "/auth/register",
    "/auth/forgot-password-otp",
    "/auth/verify-otp",
    "/auth/reset-password-otp",
  ];

  const isPublicRoute = publicRoutes.some((route) =>
    endpoint.startsWith(route),
  );

  let token = null;
  if (!isPublicRoute) {
    token = await getToken();
  }

  const headers: HeadersInit = {
    "Content-Type": "application/json",
    ...options.headers,
  };

  if (token) {
    (headers as Record<string, string>)["Authorization"] = `Bearer ${token}`;
  }

  const url = `${API_BASE_URL}${endpoint}`;
  const response = await fetch(url, { ...options, headers });

  if (response.status === 401 && !isPublicRoute) {
    await forceLogout();
    return new Response(JSON.stringify({ detail: "Session expired" }), {
      status: 401,
    });
  }

  return response;
};

// ============ INTERFACES ============

export interface User {
  id: number;
  username: string;
  email?: string;
  phone_number?: string;
  active_status?: boolean;
}

export interface Contact {
  id: number;
  contact_id: number;
  status: "pending" | "accepted" | "blocked";
  contact: User;
}

// Added Message Interface
export interface Message {
  id: number;
  conversation_id: number;
  sender_id: number;
  content: string;
  moderation_status: string;
  created_at: string;
  masked_words?: string[];
}

export interface Conversation {
  id: number;
  type: "private" | "group";
  group_name?: string;
  updated_at: string;
  participants: User[];
  last_message?: {
    content: string;
    moderation_status: string;
    created_at: string;
    masked_words?: string[];
  };
  // Added optional messages array for full conversation history
  messages?: Message[];
}

// ============ API MODULES ============

export const authApi = {
  register: async (data: any) => {
    const response = await fetchWithAuth("/auth/register", {
      method: "POST",
      body: JSON.stringify(data),
    });
    if (!response.ok)
      throw new Error((await response.json()).detail || "Registration failed");
    return response.json();
  },
  login: async (data: any) => {
    const response = await fetchWithAuth("/auth/login", {
      method: "POST",
      body: JSON.stringify(data),
    });
    if (!response.ok)
      throw new Error((await response.json()).detail || "Login failed");
    const result = await response.json();
    if (result.access_token) await setToken(result.access_token);
    return result;
  },
  logout: async () => {
    await removeToken();
  },
};

export const userApi = {
  getById: async (id: number): Promise<User> => {
    const response = await fetchWithAuth(`/users/${id}`);
    if (!response.ok) throw new Error(`User load failed: ${response.status}`);
    return response.json();
  },
  getCurrentUser: async (): Promise<User> => {
    const response = await fetchWithAuth("/users/profile");
    return response.json();
  },
  searchUsers: async (username: string): Promise<User[]> => {
    const response = await fetchWithAuth(
      `/users/search?username=${encodeURIComponent(username)}`,
    );
    return response.json();
  },
};

export const contactsApi = {
  getAll: (status?: string) => contactsApi.getContacts(status),

  getContacts: async (status?: string): Promise<Contact[]> => {
    const url = status
      ? `/contacts/contact-list?status=${status}`
      : "/contacts/contact-list";
    const response = await fetchWithAuth(url);
    if (!response.ok) {
      return [];
    }
    return response.json();
  },
  addContact: async (contactId: number) => {
    const response = await fetchWithAuth("/contacts/send_request", {
      method: "POST",
      body: JSON.stringify({ contact_id: contactId }),
    });
    return response.json();
  },
};

export const conversationsApi = {
  getAll: () => conversationsApi.getConversations(),

  getConversations: async (): Promise<Conversation[]> => {
    try {
      const response = await fetchWithAuth("/conversations");
      if (!response.ok) return [];
      return response.json();
    } catch (err) {
      console.error("[API] Network Error in getConversations", err);
      return [];
    }
  },

  getConversation: async (id: number): Promise<Conversation> => {
    const response = await fetchWithAuth(`/conversations/${id}`);
    if (!response.ok) throw new Error("Failed to fetch history");
    return response.json();
  },

  createPrivateConversation: async (
    receiverId: number,
  ): Promise<Conversation> => {
    const response = await fetchWithAuth("/conversations/private", {
      method: "POST",
      body: JSON.stringify({ receiver_id: receiverId }),
    });
    if (!response.ok) throw new Error("Could not start conversation");
    return response.json();
  },
};

export const messagesApi = {
  sendMessage: async (
    content: string,
    conversationId?: number,
    receiverId?: number,
  ) => {
    const response = await fetchWithAuth("/messages/send_message", {
      method: "POST",
      body: JSON.stringify({
        content,
        conversation_id: conversationId,
        receiver_id: receiverId,
      }),
    });
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || "Failed to send message");
    }
    return response.json(); // Returns a Message object
  },
};

export default {
  auth: authApi,
  user: userApi,
  users: userApi,
  contacts: contactsApi,
  conversations: conversationsApi,
  messages: messagesApi,
};
