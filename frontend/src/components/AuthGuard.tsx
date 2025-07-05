import React, { useEffect, useState } from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { CircularProgress, Box, Typography } from '@mui/material';

interface AuthGuardProps {
  children: React.ReactNode;
}

export const AuthGuard: React.FC<AuthGuardProps> = ({ children }) => {
  const { user, userProfile, loading } = useAuth();
  const location = useLocation();
  const [isCheckingAuth, setIsCheckingAuth] = useState(true);
  
  useEffect(() => {
    console.log('🔄 AuthGuard: Checking authentication status');
    console.log('🔄 AuthGuard: user:', user);
    console.log('🔄 AuthGuard: userProfile:', userProfile);
    console.log('🔄 AuthGuard: loading:', loading);
    
    // Check localStorage for user info as a fallback
    const hasStoredUser = localStorage.getItem('userProfile') || localStorage.getItem('firebaseUser');
    console.log('🔄 AuthGuard: hasStoredUser:', !!hasStoredUser);
    
    // Wait a bit to make sure auth state is loaded
    const timer = setTimeout(() => {
      setIsCheckingAuth(false);
    }, 1000);
    
    return () => clearTimeout(timer);
  }, [user, userProfile, loading]);

  if (loading || isCheckingAuth) {
    return (
      <Box sx={{ 
        display: 'flex', 
        flexDirection: 'column',
        justifyContent: 'center', 
        alignItems: 'center', 
        height: '100vh' 
      }}>
        <CircularProgress size={40} />
        <Typography variant="body1" sx={{ mt: 2 }}>
          Checking authentication status...
        </Typography>
      </Box>
    );
  }

  if (!user) {
    console.log('❌ AuthGuard: No user found, redirecting to login');
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  console.log('✅ AuthGuard: User authenticated, rendering protected content');
  return <>{children}</>;
};

export default AuthGuard;
