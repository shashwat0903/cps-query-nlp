import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000, // 30 seconds timeout
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add response interceptor for better error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.code === 'ECONNABORTED') {
      console.error('Request timeout');
      return Promise.reject(new Error('Request timed out. Please try again.'));
    }
    if (error.response?.status >= 500) {
      console.error('Server error:', error.response?.data);
      return Promise.reject(new Error('Server error. Please try again later.'));
    }
    return Promise.reject(error);
  }
);

// Interfaces for types
export interface AnalyzeResponse {
  video?: {
    title: string;
    url: string;
  };
  concepts: {
    name: string;
    confidence: number;
  }[];
}

export interface FeedbackData {
  userId: string;
  query: string;
  feedback: string;
}

export interface QueryHistoryItem {
  query: string;
  timestamp: string;
  result?: AnalyzeResponse;
}

// User and Authentication interfaces
export interface UserProfile {
  user_id: string;
  email: string;
  full_name: string;
  skill_level: string;
  completed_topics: string[];
  known_concepts?: string[]; // Added to match localStorageAuth
  is_active?: boolean; // Added to match localStorageAuth
  created_at?: string; // Added to match localStorageAuth
  statistics: {
    total_queries: number;
    topics_completed: number;
    total_study_time: number;
    streak_days?: number;
    sessions_completed?: number;
  };
  profile_data: {
    university: string;
    degree: string;
    year: string;
    interests: string[];
    programming_languages: string[];
    goals?: string[];
  };
}

export interface ChatMessage {
  _id: string;
  user_id: string;
  message: string;
  response: string;
  timestamp: string;
  analysis?: any;
}

export interface LoginResponse {
  success: boolean;
  message: string;
  user: UserProfile | null;
  chat_history: ChatMessage[];
}

// Analyze student query
export const analyzeQuery = async (query: string): Promise<AnalyzeResponse> => {
  try {
    const response = await api.post<AnalyzeResponse>('/api/analyze', { query });
    return response.data;
  } catch (error) {
    console.error('API Error:', error);
    throw error;
  }
};

// Submit user feedback
export const submitFeedback = async (feedbackData: FeedbackData): Promise<{ success: boolean; message: string }> => {
  try {
    const response = await api.post('/api/feedback', feedbackData);
    return response.data;
  } catch (error) {
    console.error('Feedback submission error:', error);
    throw error;
  }
};

// Get query history for a specific user
export const getQueryHistory = async (userId: string): Promise<QueryHistoryItem[]> => {
  try {
    const response = await api.get<QueryHistoryItem[]>(`/api/history/${userId}`);
    return response.data;
  } catch (error) {
    console.error('History fetch error:', error);
    throw error;
  }
};

// User API functions
export const userAPI = {
  // Signup new user with email and password
  signup: async (email: string, password: string, fullName: string, skillLevel: string = 'beginner', profileData: any = {}): Promise<LoginResponse> => {
    try {
      console.log('🔄 API: Attempting signup with email:', email);
      const response = await api.post('/api/user/signup', {
        email,
        password,
        full_name: fullName,
        skill_level: skillLevel,
        profile_data: profileData
      });
      console.log('✅ API: Signup response received:', response.status);
      return response.data;
    } catch (error: any) {
      console.error('❌ API: Signup failed:', error);
      return {
        success: false,
        message: error.response?.data?.message || 'Signup failed. Server error or network issue.',
        user: null,
        chat_history: []
      };
    }
  },

  // Login user with email and password
  login: async (email: string, password: string): Promise<LoginResponse> => {
    try {
      console.log('🔄 API: Attempting login with email:', email);
      const response = await api.post('/api/user/login', {
        email,
        password
      });
      console.log('✅ API: Login response received:', response.status);
      return response.data;
    } catch (error: any) {
      console.error('❌ API: Login failed:', error);
      return {
        success: false,
        message: error.response?.data?.message || 'Login failed. Server error or network issue.',
        user: null,
        chat_history: []
      };
    }
  },

  // Get user profile
  getProfile: async (userId: string): Promise<{ success: boolean; user?: UserProfile; message?: string }> => {
    try {
      const response = await api.get(`/api/user/${userId}/profile`);
      return response.data;
    } catch (error: any) {
      console.error('Get profile failed:', error);
      return {
        success: false,
        message: error.response?.data?.message || 'Failed to get profile'
      };
    }
  },

  // Get chat history
  getChatHistory: async (userId: string, limit: number = 20): Promise<{ success: boolean; chat_history: ChatMessage[]; total_messages?: number; message?: string }> => {
    try {
      console.log('🔄 API: Fetching chat history for user:', userId, 'limit:', limit);
      const response = await api.get(`/api/user/${userId}/chat-history?limit=${limit}`);
      console.log('✅ API: Chat history response received:', response.status);
      
      if (response.data.chat_history?.length) {
        console.log(`✅ API: Retrieved ${response.data.chat_history.length} chat messages`);
      } else {
        console.log('⚠️ API: No chat history found or empty array returned');
      }
      
      return response.data;
    } catch (error: any) {
      console.error('❌ API: Get chat history failed:', error);
      return {
        success: false,
        chat_history: [],
        message: error.response?.data?.message || 'Failed to get chat history'
      };
    }
  },

  // Update user profile
  updateProfile: async (userId: string, profileData: Partial<UserProfile>): Promise<{ success: boolean; user?: UserProfile; message?: string }> => {
    try {
      const response = await api.put(`/api/user/${userId}/profile`, profileData);
      return response.data;
    } catch (error: any) {
      console.error('Update profile failed:', error);
      return {
        success: false,
        message: error.response?.data?.message || 'Failed to update profile'
      };
    }
  },

  // Send chat message
  sendMessage: async (message: string, userId: string, chatHistory: ChatMessage[] = []): Promise<{
    response: string;
    videos: any[];
    analysis: any;
    error?: string;
  }> => {
    try {
      const response = await api.post('/api/chat', {
        message,
        user_id: userId,
        chat_history: chatHistory
      });
      return response.data;
    } catch (error: any) {
      console.error('Send message failed:', error);
      return {
        response: 'Sorry, an error occurred while processing your request.',
        videos: [],
        analysis: {},
        error: error.response?.data?.message || 'Failed to send message'
      };
    }
  },

  // Export user data as JSON
  exportUserData: async (userId: string): Promise<{ success: boolean; data?: any; message?: string }> => {
    try {
      const response = await api.get(`/api/user/${userId}/export`);
      
      if (response.data.success && response.data.data) {
        // Create and download JSON file
        const dataStr = JSON.stringify(response.data.data, null, 2);
        const dataBlob = new Blob([dataStr], { type: 'application/json' });
        const url = URL.createObjectURL(dataBlob);
        const link = document.createElement('a');
        link.href = url;
        link.download = `user_data_${userId}_${new Date().toISOString().split('T')[0]}.json`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(url);
      }

      return response.data;
    } catch (error: any) {
      console.error('Export user data failed:', error);
      return {
        success: false,
        message: error.response?.data?.message || 'Failed to export data'
      };
    }
  }
};
