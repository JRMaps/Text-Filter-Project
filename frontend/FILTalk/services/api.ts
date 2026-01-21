import AsyncStorage from '@react-native-async-storage/async-storage';

// Change this to your backend URL
// For Android emulator: http://10.0.2.2:8000
// For iOS simulator: http://localhost:8000
// For physical device: use your computer's local IP (e.g., http://192.168.1.x:8000)
const API_BASE_URL = 'http://10.0.2.2:8000/api';

// Token storage keys
const TOKEN_KEY = 'auth_token';

// Helper to get stored token
export const getToken = async (): Promise<string | null> => {
  try {
    return await AsyncStorage.getItem(TOKEN_KEY);
  } catch {
    return null;
  }
};

// Helper to store token
export const setToken = async (token: string): Promise<void> => {
  await AsyncStorage.setItem(TOKEN_KEY, token);
};

// Helper to remove token (logout)
export const removeToken = async (): Promise<void> => {
  await AsyncStorage.removeItem(TOKEN_KEY);
};

// Generic fetch wrapper with auth
const fetchWithAuth = async (
  endpoint: string,
  options: RequestInit = {}
): Promise<Response> => {
  const token = await getToken();
  
  const headers: HeadersInit = {
    'Content-Type': 'application/json',
    ...options.headers,
  };

  if (token) {
    (headers as Record<string, string>)['Authorization'] = `Bearer ${token}`;
  }

  return fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    headers,
  });
};

// ============ AUTH API ============

export interface RegisterData {
  fullname: string;
  username: string;
  email?: string;
  phone_number?: string;
  password: string;
}

export interface LoginData {
  email?: string;
  phone_number?: string;
  password: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
}

export const authApi = {
  register: async (data: RegisterData) => {
    const response = await fetchWithAuth('/auth/register', {
      method: 'POST',
      body: JSON.stringify(data),
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Registration failed');
    }
    
    return response.json();
  },

  login: async (data: LoginData): Promise<AuthResponse> => {
    const response = await fetchWithAuth('/auth/login', {
      method: 'POST',
      body: JSON.stringify(data),
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Login failed');
    }
    
    const result: AuthResponse = await response.json();
    // Token storage is handled by AuthContext.login()
    return result;
  },

  logout: async () => {
    await removeToken();
  },

  requestPasswordReset: async (email?: string, phone_number?: string) => {
    const response = await fetchWithAuth('/auth/forgot-password', {
      method: 'POST',
      body: JSON.stringify({ email, phone_number }),
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to send OTP');
    }
    
    return response.json();
  },

  verifyOTP: async (email: string | undefined, phone_number: string | undefined, otp: string) => {
    const response = await fetchWithAuth('/auth/verify-otp', {
      method: 'POST',
      body: JSON.stringify({ email, phone_number, otp }),
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'OTP verification failed');
    }
    
    return response.json();
  },

  resetPassword: async (email: string | undefined, phone_number: string | undefined, otp: string, new_password: string) => {
    const response = await fetchWithAuth('/auth/reset-password', {
      method: 'POST',
      body: JSON.stringify({ email, phone_number, otp, new_password }),
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Password reset failed');
    }
    
    return response.json();
  },
};

// ============ USER API ============

export interface User {
  id: number;
  username: string;
  email?: string;
  phone_number?: string;
  active_status?: boolean;
}

export const userApi = {
  getCurrentUser: async (): Promise<User> => {
    const response = await fetchWithAuth('/users/me');
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to get user');
    }
    
    return response.json();
  },

  updateUser: async (data: Partial<User>) => {
    const response = await fetchWithAuth('/users/me', {
      method: 'PUT',
      body: JSON.stringify(data),
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to update user');
    }
    
    return response.json();
  },

  searchUsers: async (query: string): Promise<User[]> => {
    const response = await fetchWithAuth(`/users/search?query=${encodeURIComponent(query)}`);
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Search failed');
    }
    
    return response.json();
  },
};

// ============ CONTACTS API ============

export interface Contact {
  id: number;
  user_id: number;
  contact_id: number;
  status: 'PENDING' | 'ACCEPTED' | 'BLOCKED';
  contact_user?: User;
}

export const contactsApi = {
  getContacts: async (): Promise<Contact[]> => {
    const response = await fetchWithAuth('/contacts');
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to get contacts');
    }
    
    return response.json();
  },

  addContact: async (contactId: number) => {
    const response = await fetchWithAuth('/contacts/add', {
      method: 'POST',
      body: JSON.stringify({ contact_id: contactId }),
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to add contact');
    }
    
    return response.json();
  },

  acceptContact: async (contactId: number) => {
    const response = await fetchWithAuth(`/contacts/${contactId}/accept`, {
      method: 'PUT',
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to accept contact');
    }
    
    return response.json();
  },

  blockContact: async (contactId: number) => {
    const response = await fetchWithAuth(`/contacts/${contactId}/block`, {
      method: 'PUT',
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to block contact');
    }
    
    return response.json();
  },

  removeContact: async (contactId: number) => {
    const response = await fetchWithAuth(`/contacts/${contactId}`, {
      method: 'DELETE',
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to remove contact');
    }
    
    return response.json();
  },
};

// ============ CONVERSATIONS API ============

export interface Message {
  id: number;
  conversation_id: number;
  sender_id: number;
  content: string;
  moderation_status: 'ALLOWED' | 'MASKED' | 'BLOCKED' | 'FLAGGED';
  severity_score?: number;
  timestamp: string;
}

export interface Conversation {
  id: number;
  type: 'PRIVATE' | 'GROUP';
  group_name?: string;
  participants: User[];
  last_message?: Message;
  updated_at: string;
}

export const conversationsApi = {
  getConversations: async (): Promise<Conversation[]> => {
    const response = await fetchWithAuth('/conversations');
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to get conversations');
    }
    
    return response.json();
  },

  getConversation: async (conversationId: number): Promise<Conversation> => {
    const response = await fetchWithAuth(`/conversations/${conversationId}`);
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to get conversation');
    }
    
    return response.json();
  },

  getMessages: async (conversationId: number): Promise<Message[]> => {
    const response = await fetchWithAuth(`/conversations/${conversationId}/messages`);
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to get messages');
    }
    
    return response.json();
  },

  createPrivateConversation: async (participantId: number) => {
    const response = await fetchWithAuth('/conversations/private', {
      method: 'POST',
      body: JSON.stringify({ participant_id: participantId }),
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to create conversation');
    }
    
    return response.json();
  },

  createGroupConversation: async (name: string, participantIds: number[]) => {
    const response = await fetchWithAuth('/conversations/group', {
      method: 'POST',
      body: JSON.stringify({ group_name: name, participant_ids: participantIds }),
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to create group');
    }
    
    return response.json();
  },
};

// ============ MESSAGES API ============

export const messagesApi = {
  sendMessage: async (conversationId: number, content: string): Promise<Message> => {
    const response = await fetchWithAuth('/messages/send_message', {
      method: 'POST',
      body: JSON.stringify({ 
        conversation_id: conversationId, 
        content 
      }),
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to send message');
    }
    
    return response.json();
  },
};

export default {
  auth: authApi,
  user: userApi,
  contacts: contactsApi,
  conversations: conversationsApi,
  messages: messagesApi,
};
