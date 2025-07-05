// src/services/localStorageAuth.ts
// This is a fallback authentication service that uses localStorage when the backend is unavailable

import type { LoginResponse, UserProfile } from './api';
import bcrypt from 'bcryptjs';

// Define the local storage keys
const USERS_KEY = 'local_users';
const CURRENT_USER_KEY = 'current_user';
const CHAT_HISTORY_KEY = 'chat_history';

// Initialize local storage with default data if needed
const initializeLocalStorage = () => {
  if (!localStorage.getItem(USERS_KEY)) {
    localStorage.setItem(USERS_KEY, JSON.stringify([]));
  }
};

// Get all users from localStorage
const getUsers = (): UserProfile[] => {
  initializeLocalStorage();
  const usersJson = localStorage.getItem(USERS_KEY) || '[]';
  return JSON.parse(usersJson);
};

// Save users to localStorage
const saveUsers = (users: UserProfile[]) => {
  localStorage.setItem(USERS_KEY, JSON.stringify(users));
};

// Find user by email
const findUserByEmail = (email: string): UserProfile | undefined => {
  const users = getUsers();
  return users.find(user => user.email === email);
};

// Local storage authentication service
export const localStorageAuth = {
  // Signup with localStorage
  signup: async (email: string, password: string, fullName: string, skillLevel: string = 'beginner', profileData: any = {}): Promise<LoginResponse> => {
    try {
      // Check if user already exists
      if (findUserByEmail(email)) {
        return {
          success: false,
          message: 'User with this email already exists',
          user: null,
          chat_history: []
        };
      }

      // Hash the password for security (even in localStorage)
      const hashedPassword = await bcrypt.hash(password, 10);
      
      // Create user ID from email (similar to backend)
      const userId = email.replace('@', '_').replace(/\./g, '_');
      
      // Create a new user
      const newUser = {
        user_id: userId,
        email: email,
        full_name: fullName,
        skill_level: skillLevel,
        completed_topics: [],
        known_concepts: [],
        is_active: true,
        created_at: new Date().toISOString(),          statistics: {
            total_queries: 0,
            topics_completed: 0,
            total_study_time: 0,
            streak_days: 0,
            sessions_completed: 0
          } as any,
        profile_data: {
          ...profileData,
          university: profileData.university || '',
          degree: profileData.degree || '',
          year: profileData.year || '',
          interests: profileData.interests || [],
          programming_languages: profileData.programming_languages || [],
          goals: profileData.goals || []
        },
        // Add password for local verification only (this field doesn't exist in the UserProfile type)
        password: hashedPassword
      } as any;
      
      // Save the user
      const users = getUsers();
      users.push(newUser);
      saveUsers(users);
      
      // Set current user
      const userWithoutPassword = { ...newUser };
      delete (userWithoutPassword as any).password;
      localStorage.setItem(CURRENT_USER_KEY, JSON.stringify(userWithoutPassword));
      localStorage.setItem(CHAT_HISTORY_KEY, JSON.stringify([]));
      
      return {
        success: true,
        message: 'Signup successful',
        user: userWithoutPassword,
        chat_history: []
      };
    } catch (error) {
      console.error('Local storage signup error:', error);
      return {
        success: false,
        message: 'Signup failed',
        user: null,
        chat_history: []
      };
    }
  },
  
  // Login with localStorage
  login: async (email: string, password: string): Promise<LoginResponse> => {
    try {
      // Get user from localStorage
      const user = findUserByEmail(email) as UserProfile & { password?: string };
      
      if (!user) {
        return {
          success: false,
          message: 'User not found',
          user: null,
          chat_history: []
        };
      }
      
      // Verify password if it exists
      if (user.password) {
        const isPasswordValid = await bcrypt.compare(password, user.password);
        if (!isPasswordValid) {
          return {
            success: false,
            message: 'Invalid password',
            user: null,
            chat_history: []
          };
        }
      }
      
      // Remove password before returning
      const userWithoutPassword = { ...user };
      delete userWithoutPassword.password;
      
      // Set current user in localStorage
      localStorage.setItem(CURRENT_USER_KEY, JSON.stringify(userWithoutPassword));
      
      // Get or create empty chat history
      let chatHistory = [];
      const savedChatHistory = localStorage.getItem(`chat_history_${user.user_id}`);
      if (savedChatHistory) {
        chatHistory = JSON.parse(savedChatHistory);
      } else {
        localStorage.setItem(`chat_history_${user.user_id}`, JSON.stringify([]));
      }
      
      return {
        success: true,
        message: 'Login successful',
        user: userWithoutPassword,
        chat_history: chatHistory
      };
    } catch (error) {
      console.error('Local storage login error:', error);
      return {
        success: false,
        message: 'Login failed',
        user: null,
        chat_history: []
      };
    }
  },
  
  // Google login/signup
  googleAuth: async (name: string, email: string): Promise<LoginResponse> => {
    try {
      // Check if user exists
      let user = findUserByEmail(email) as UserProfile;
      
      if (!user) {
        // Create new user for Google sign-in
        const userId = email.replace('@', '_').replace(/\./g, '_');
        user = {
          user_id: userId,
          email: email,
          full_name: name || email.split('@')[0],
          skill_level: 'beginner',
          completed_topics: [],
          known_concepts: [],
          is_active: true,
          created_at: new Date().toISOString(),
          statistics: {
            total_queries: 0,
            topics_completed: 0,
            total_study_time: 0,
            streak_days: 0,
            sessions_completed: 0
            // last_active is not in the type definition but the backend uses it
          } as any,
          profile_data: {
            university: '',
            degree: '',
            year: '',
            interests: [],
            programming_languages: [],
            goals: []
          }
        };
        
        // Save the new user
        const users = getUsers();
        users.push(user);
        saveUsers(users);
      }
      
      // Set current user
      localStorage.setItem(CURRENT_USER_KEY, JSON.stringify(user));
      
      // Get or create empty chat history
      let chatHistory = [];
      const savedChatHistory = localStorage.getItem(`chat_history_${user.user_id}`);
      if (savedChatHistory) {
        chatHistory = JSON.parse(savedChatHistory);
      } else {
        localStorage.setItem(`chat_history_${user.user_id}`, JSON.stringify([]));
      }
      
      return {
        success: true,
        message: 'Login successful',
        user: user,
        chat_history: chatHistory
      };
    } catch (error) {
      console.error('Local storage Google auth error:', error);
      return {
        success: false,
        message: 'Authentication failed',
        user: null,
        chat_history: []
      };
    }
  }
};
