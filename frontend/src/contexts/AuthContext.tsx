// src/contexts/AuthContext.tsx
import React, { createContext, useContext, useEffect, useState, useCallback } from "react";
import { type User, onAuthStateChanged } from "firebase/auth";
import { auth } from "../firebase/config";
import { userAPI, type UserProfile, type ChatMessage } from "../services/api";

interface AuthContextType {
  user: User | null;
  userProfile: UserProfile | null;
  chatHistory: ChatMessage[];
  loading: boolean;
  loginWithProfile: (userData: User | UserProfile) => Promise<void>;
  signupWithProfile: (userData: User | UserProfile, additionalData?: any) => Promise<void>;
  logout: () => Promise<void>;
  refreshProfile: () => Promise<void>;
  updateUserProfile: (profileData: Partial<UserProfile>) => Promise<void>;
  exportUserData: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType>({ 
  user: null,
  userProfile: null,
  chatHistory: [],
  loading: false,
  loginWithProfile: async () => {},
  signupWithProfile: async () => {},
  logout: async () => {},
  refreshProfile: async () => {},
  updateUserProfile: async () => {},
  exportUserData: async () => {}
});

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [userProfile, setUserProfile] = useState<UserProfile | null>(null);
  const [chatHistory, setChatHistory] = useState<ChatMessage[]>([]);
  const [loading, setLoading] = useState(true); // Start with loading true

  const fetchProfileAndHistory = useCallback(async (userId: string) => {
    try {
      setLoading(true);
      const [profileRes, chatRes] = await Promise.all([
        userAPI.getProfile(userId),
        userAPI.getChatHistory(userId, 20)
      ]);
      if (profileRes.success && profileRes.user) {
        setUserProfile(profileRes.user);
        localStorage.setItem('userProfile', JSON.stringify(profileRes.user));
      }
      if (chatRes.success && chatRes.chat_history) {
        setChatHistory(chatRes.chat_history);
        localStorage.setItem('chatHistory', JSON.stringify(chatRes.chat_history));
      }
    } catch (err) {
      console.error('Failed to fetch profile or chat history:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  const loginWithProfile = useCallback(async (userData: any) => {
    try {
      setLoading(true);
      console.log('🔄 AuthContext: loginWithProfile called with userData:', userData);
      
      // Handle both Firebase User and our own User object
      const isFirebaseUser = userData.uid && !userData.user_id;
      const userId = isFirebaseUser 
        ? (userData.email || 'default') 
        : (userData.user_id || userData._id || userData.email || 'default');
      
      console.log('🔄 AuthContext: Setting userId to:', userId);
      localStorage.setItem('userId', userId);
      
      if (isFirebaseUser) {
        // It's a Firebase user, we need to call the backend login
        console.log('🔄 AuthContext: Firebase user detected, calling backend login');
        const loginResponse = await userAPI.login(userData.email || '', userData.uid);
        console.log('✅ AuthContext: Backend login response:', loginResponse);
        
        if (loginResponse.success && loginResponse.user) {
          console.log('✅ AuthContext: User profile received from backend:', loginResponse.user);
          console.log('✅ AuthContext: Chat history received from backend:', loginResponse.chat_history?.length || 0, 'messages');
          
          setUserProfile(loginResponse.user);
          setChatHistory(loginResponse.chat_history || []);
          
          localStorage.setItem('userProfile', JSON.stringify(loginResponse.user));
          localStorage.setItem('chatHistory', JSON.stringify(loginResponse.chat_history || []));
          console.log('✅ AuthContext: Updated user profile and chat history from Firebase login');
        } else {
          console.warn('⚠️ AuthContext: Firebase login response unsuccessful');
        }
      } else {
        // It's our own user object, use it directly
        console.log('🔄 AuthContext: Custom user detected, setting directly');
        setUserProfile(userData);
        if (userData.chat_history) {
          setChatHistory(userData.chat_history);
          localStorage.setItem('chatHistory', JSON.stringify(userData.chat_history));
        }
        localStorage.setItem('userProfile', JSON.stringify(userData));
        
        // Still fetch the latest profile and chat history
        console.log('🔄 AuthContext: Fetching latest profile and chat history');
        await fetchProfileAndHistory(userId);
      }
    } catch (error) {
      console.error('❌ AuthContext: Login error:', error);
      localStorage.removeItem('userProfile');
      localStorage.removeItem('chatHistory');
      localStorage.removeItem('userId');
    } finally {
      setLoading(false);
    }
  }, [fetchProfileAndHistory]);

  const signupWithProfile = useCallback(async (userData: User | UserProfile, additionalData: any = {}) => {
    try {
      setLoading(true);
      console.log('🔄 AuthContext: signupWithProfile called with userData:', userData);
      
      // Check if we're dealing with a Firebase User or our own UserProfile
      const isFirebaseUser = 'uid' in userData && !('user_id' in userData);
      
      if (isFirebaseUser) {
        const firebaseUser = userData as User;
        const userId = firebaseUser.email?.replace('@', '_').replace(/\./g, '_') || 'default';
        console.log('🔄 AuthContext: Firebase user detected, calling signup API');
        
        const signupResponse = await userAPI.signup(
          firebaseUser.email || '',
          firebaseUser.uid, // Use Firebase UID as password
          firebaseUser.displayName || 'User',
          additionalData.skillLevel || 'beginner',
          additionalData
        );
        
        console.log('✅ AuthContext: Signup API response:', signupResponse);
        
        if (signupResponse.success && signupResponse.user) {
          setUserProfile(signupResponse.user);
          setChatHistory(signupResponse.chat_history || []);
          
          localStorage.setItem('userId', signupResponse.user.user_id || userId);
          localStorage.setItem('userProfile', JSON.stringify(signupResponse.user));
          localStorage.setItem('chatHistory', JSON.stringify(signupResponse.chat_history || []));
          
          console.log('✅ AuthContext: Updated user profile from signup response');
          
          // Also fetch the latest data
          await fetchProfileAndHistory(signupResponse.user.user_id || userId);
        } else {
          console.warn('⚠️ AuthContext: Signup API response unsuccessful');
          localStorage.removeItem('userProfile');
          localStorage.removeItem('chatHistory');
          localStorage.removeItem('userId');
        }
      } else {
        // It's already our user profile object
        const userProfile = userData as UserProfile;
        console.log('🔄 AuthContext: UserProfile detected, setting directly');
        
        setUserProfile(userProfile);
        if ('chat_history' in userData) {
          setChatHistory((userData as any).chat_history || []);
        }
        
        localStorage.setItem('userId', userProfile.user_id || userProfile.email);
        localStorage.setItem('userProfile', JSON.stringify(userProfile));
        
        // Also fetch the latest data
        await fetchProfileAndHistory(userProfile.user_id || userProfile.email);
      }
    } catch (error) {
      console.error('❌ AuthContext: Signup error:', error);
    } finally {
      setLoading(false);
    }
  }, [fetchProfileAndHistory]);

  const logout = useCallback(async () => {
    try {
      setLoading(true);
      await auth.signOut();
      setUser(null);
      setUserProfile(null);
      setChatHistory([]);
      
      localStorage.removeItem('userProfile');
      localStorage.removeItem('chatHistory');
      localStorage.removeItem('userId');
    } catch (error) {
      console.error('❌ Logout error:', error);
    } finally {
      setLoading(false);
    }
  }, []);

  const refreshProfile = useCallback(async () => {
    const userId = localStorage.getItem('userId');
    if (!userId) {
      console.warn('⚠️ AuthContext: Cannot refresh profile, no userId found');
      return;
    }

    try {
      setLoading(true);
      console.log('🔄 AuthContext: Refreshing profile for userId:', userId);
      
      // Fetch both profile and chat history in parallel
      const [profileResponse, chatHistoryResponse] = await Promise.all([
        userAPI.getProfile(userId),
        userAPI.getChatHistory(userId, 50)
      ]);
      
      console.log('✅ AuthContext: Profile refresh responses received');
      console.log('Profile response:', profileResponse);
      console.log('Chat history response:', chatHistoryResponse);
      
      // Update profile if successful
      if (profileResponse.success && profileResponse.user) {
        console.log('✅ AuthContext: User profile data received:', profileResponse.user);
        console.log('✅ AuthContext: User ID in profile:', profileResponse.user.user_id);
        
        // Make sure userId is properly stored and the same everywhere
        if (profileResponse.user.user_id && profileResponse.user.user_id !== userId) {
          console.log('⚠️ AuthContext: User ID in profile differs from stored ID, updating local storage');
          localStorage.setItem('userId', profileResponse.user.user_id);
        }
        
        setUserProfile(profileResponse.user);
        localStorage.setItem('userProfile', JSON.stringify(profileResponse.user));
        console.log('✅ AuthContext: User profile updated successfully');
      } else {
        console.warn('⚠️ AuthContext: Failed to get user profile:', profileResponse.message);
      }
      
      // Update chat history if successful
      if (chatHistoryResponse.success && chatHistoryResponse.chat_history) {
        console.log('✅ AuthContext: Chat history content sample:', 
          JSON.stringify(chatHistoryResponse.chat_history.slice(0, 2), null, 2));
        setChatHistory(chatHistoryResponse.chat_history);
        localStorage.setItem('chatHistory', JSON.stringify(chatHistoryResponse.chat_history));
        console.log('✅ AuthContext: Chat history updated successfully with', 
          chatHistoryResponse.chat_history.length, 'messages');
      } else {
        console.warn('⚠️ AuthContext: Failed to get chat history:', chatHistoryResponse.message);
      }
    } catch (error) {
      console.error('❌ AuthContext: Refresh profile error:', error);
    } finally {
      setLoading(false);
    }
  }, []);

  const updateUserProfile = useCallback(async (profileData: Partial<UserProfile>) => {
    const userId = localStorage.getItem('userId');
    if (!userId || !userProfile) return;

    try {
      setLoading(true);
      const updateResponse = await userAPI.updateProfile(userId, profileData);
      
      if (updateResponse.success && updateResponse.user) {
        const updatedProfile = updateResponse.user;
        setUserProfile(updatedProfile);
        localStorage.setItem('userProfile', JSON.stringify(updatedProfile));
        console.log('✅ Profile updated successfully');
      }
    } catch (error) {
      console.error('❌ Profile update error:', error);
    } finally {
      setLoading(false);
    }
  }, [userProfile]);

  const exportUserData = useCallback(async () => {
    const userId = localStorage.getItem('userId');
    if (!userId) return;

    try {
      setLoading(true);
      await userAPI.exportUserData(userId);
      console.log('✅ User data exported successfully');
    } catch (error) {
      console.error('❌ Export data error:', error);
    } finally {
      setLoading(false);
    }
  }, []);

  // Effect for handling auth state changes from Firebase
  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, async (firebaseUser) => {
      if (firebaseUser) {
        setUser(firebaseUser);
        // If we don't have a profile yet, fetch it.
        if (!userProfile) {
          await loginWithProfile(firebaseUser);
        }
      } else {
        setUser(null);
        setUserProfile(null);
        setChatHistory([]);
        setLoading(false); // Stop loading on logout
      }
    });

    return unsubscribe;
  }, [loginWithProfile, userProfile]);

  // Effect for loading initial state from localStorage
  useEffect(() => {
    const savedProfile = localStorage.getItem('userProfile');
    const savedChatHistory = localStorage.getItem('chatHistory');
    
    if (savedProfile) {
      setUserProfile(JSON.parse(savedProfile));
    }
    if (savedChatHistory) {
      setChatHistory(JSON.parse(savedChatHistory));
    }
    setLoading(false); // Initial load done
  }, []);

  return (
    <AuthContext.Provider 
      value={{ 
        user, 
        userProfile, 
        chatHistory, 
        loading, 
        loginWithProfile, 
        signupWithProfile,
        logout, 
        refreshProfile, 
        updateUserProfile,
        exportUserData
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);
