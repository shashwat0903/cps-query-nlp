import { zodResolver } from '@hookform/resolvers/zod';
import { Visibility, VisibilityOff } from '@mui/icons-material';
import {
  Alert,
  Box,
  Button,
  CircularProgress,
  Container,
  Divider,
  IconButton,
  InputAdornment,
  Link,
  Paper,
  Snackbar,
  TextField,
  Typography
} from '@mui/material';
import { motion } from 'framer-motion';
import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { useNavigate } from 'react-router-dom';
import { z } from 'zod';
import GoogleIcon from '@mui/icons-material/Google';
import Lottie from 'lottie-react';
import aiAnimation from '../../assets/ai-lottie.json';
import { signInWithPopup, GoogleAuthProvider } from 'firebase/auth';
import { auth } from '../../firebase/config';
import { useAuth } from '../../contexts/AuthContext';
import { userAPI } from '../../services/api';
import { localStorageAuth } from '../../services/localStorageAuth';

const LoginSchema = z.object({
  email: z.string().email({ message: 'Enter a valid email address' }),
  password: z.string().min(6, { message: 'Minimum 6 characters required' }),
});

type LoginFormData = z.infer<typeof LoginSchema>;

const Login: React.FC = () => {
  const navigate = useNavigate();
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [snackbarOpen, setSnackbarOpen] = useState(false);
  const [snackbarMsg, setSnackbarMsg] = useState('');
  const [snackbarSeverity, setSnackbarSeverity] = useState<'success' | 'error'>('success');

  const {
    register,
    handleSubmit,
    formState: { errors, isDirty, isValid },
  } = useForm<LoginFormData>({
    resolver: zodResolver(LoginSchema),
    mode: 'onChange',
  });

  // Use the auth context
  const { loginWithProfile, refreshProfile } = useAuth();
  
  const onSubmit = async (data: LoginFormData) => {
    setLoading(true);
    try {
      console.log('Attempting login with:', data.email);
      
      try {
        // First try backend API 
        console.log('🔄 Trying backend login API...');
        const loginResponse = await userAPI.login(data.email, data.password);
        console.log('✅ Backend login response:', loginResponse);
        console.log('✅ Full login response data:', JSON.stringify(loginResponse, null, 2));
        
        if (loginResponse.success && loginResponse.user) {
          console.log('✅ Login successful, user found:', loginResponse.user.email);
          console.log('✅ User ID:', loginResponse.user.user_id);
          console.log('✅ Full user object:', JSON.stringify(loginResponse.user, null, 2));
          console.log('✅ Chat history received with login response:', loginResponse.chat_history?.length || 0, 'messages');
          
          // Save credentials for future access
          localStorage.setItem('userId', loginResponse.user.user_id);
          localStorage.setItem('userEmail', loginResponse.user.email);
          
          // Save user data to localStorage for offline access
          localStorage.setItem('userProfile', JSON.stringify(loginResponse.user));
          localStorage.setItem('chatHistory', JSON.stringify(loginResponse.chat_history || []));
          
          // Update AuthContext with the user profile and chat history
          console.log('🔄 Updating auth context with user profile...');
          const profileData = {
            ...loginResponse.user,
            chat_history: loginResponse.chat_history || []
          };
          await loginWithProfile(profileData);
          
          // Refresh profile to ensure we have the latest data from the backend
          console.log('🔄 Refreshing user profile to get latest data...');
          await refreshProfile();
          
          console.log('✅ Profile refreshed, chat history length:', loginResponse.chat_history?.length || 0);
          
          // Set a dummy Firebase user object to satisfy AuthGuard
          // AuthGuard checks for user, not userProfile
          localStorage.setItem('firebaseUser', JSON.stringify({
            uid: loginResponse.user.user_id,
            email: loginResponse.user.email,
            displayName: loginResponse.user.full_name
          }));
          
          setSnackbarMsg('Login successful! Redirecting...');
          setSnackbarSeverity('success');
          setSnackbarOpen(true);
          
          // Directly navigate without setTimeout to avoid refresh issues
          console.log('🔄 Directly navigating to /chat...');
          window.location.href = '/chat'; // Force a full navigation instead of React Router
          return;
        } else {
          console.warn('❌ Backend login failed:', loginResponse.message);
          throw new Error(loginResponse.message || 'Login failed');
        }
      } catch (apiError) {
        console.warn('❌ Backend API error, falling back to localStorage auth:', apiError);
      }
      
      // If backend fails, fall back to localStorage
      console.log('🔄 Trying localStorage login fallback...');
      const localLoginResponse = await localStorageAuth.login(data.email, data.password);
      console.log('✅ localStorage login response:', localLoginResponse);
      
      if (localLoginResponse.success && localLoginResponse.user) {
        console.log('✅ localStorage login successful, user:', localLoginResponse.user.email);
        
        // Update AuthContext with the local user profile
        console.log('🔄 Updating auth context with localStorage user profile...');
        await loginWithProfile(localLoginResponse.user);
        
        // Set dummy Firebase user for AuthGuard
        localStorage.setItem('firebaseUser', JSON.stringify({
          uid: localLoginResponse.user.user_id || localLoginResponse.user.email,
          email: localLoginResponse.user.email,
          displayName: localLoginResponse.user.full_name || localLoginResponse.user.email
        }));
        
        setSnackbarMsg('Login successful (local mode)! Redirecting...');
        setSnackbarSeverity('success');
        setSnackbarOpen(true);
        
        // Directly navigate without setTimeout to avoid refresh issues
        console.log('🔄 Directly navigating to /chat from localStorage login...');
        window.location.href = '/chat'; // Force a full navigation instead of React Router
      } else {
        console.error('❌ localStorage login failed:', localLoginResponse.message);
        throw new Error(localLoginResponse.message || 'Login failed.');
      }
    } catch (error: any) {
      console.error('❌ Login error:', error);
      let errorMessage = error.message || 'Login failed. Please try again.';
      if (error.code === 'auth/user-not-found') {
        errorMessage = 'No account found with this email address.';
      } else if (error.code === 'auth/wrong-password') {
        errorMessage = 'Incorrect password.';
      } else if (error.code === 'auth/invalid-email') {
        errorMessage = 'Invalid email address.';
      }
      setSnackbarMsg(errorMessage);
      setSnackbarSeverity('error');
      setSnackbarOpen(true);
    } finally {
      setLoading(false);
    }
  };

  // Firebase-based Google login
  const handleGoogleLogin = async () => {
    setLoading(true);
    try {
      console.log('🔄 Starting Google login process...');
      // Use Firebase's signInWithPopup instead of the backend route
      const provider = new GoogleAuthProvider();
      const result = await signInWithPopup(auth, provider);
      
      // The signed-in user info
      const firebaseUser = result.user;
      console.log('✅ Google auth successful, user:', firebaseUser.email);
      
      try {
        // Try backend first
        console.log('🔄 Updating auth context with Google user...');
        await loginWithProfile(firebaseUser);
        console.log('✅ Auth context updated with Google user');
      } catch (apiError) {
        console.warn('❌ Backend API unavailable for Google login, using localStorage fallback:', apiError);
        
        // Fallback to localStorage auth for Google login
        console.log('🔄 Trying localStorage fallback for Google login...');
        const response = await localStorageAuth.googleAuth(
          firebaseUser.displayName || 'User',
          firebaseUser.email || 'unknown@example.com'
        );
        console.log('✅ localStorage Google auth response:', response);
        
        if (!response.success) {
          console.error('❌ localStorage Google auth failed:', response.message);
          throw new Error(response.message || 'Google login failed');
        }
      }
      
      // Redirect to chat
      console.log('✅ Google login completed successfully, redirecting to chat...');
      setSnackbarMsg('Google login successful! Redirecting...');
      setSnackbarSeverity('success');
      setSnackbarOpen(true);
      
      // Directly navigate without setTimeout
      console.log('🔄 Directly navigating to /chat from Google login...');
      window.location.href = '/chat'; // Force a full navigation instead of React Router
    } catch (error: any) {
      console.error('❌ Google login error:', error);
      setSnackbarMsg('Google login failed: ' + (error.message || 'Unknown error'));
      setSnackbarSeverity('error');
      setSnackbarOpen(true);
    } finally {
      setLoading(false);
    }
  };

  const handleSnackbarClose = () => {
    setSnackbarOpen(false);
  };

  return (
    <Box
      sx={{
        minHeight: '100vh',
        background: 'linear-gradient(120deg, #1976d2 0%, #42a5f5 60%, #26c6da 100%)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        px: 2,
        position: 'relative',
        overflow: 'hidden',
      }}
    >
      <Box sx={{ position: 'absolute', top: -100, left: -150, width: 400, height: 400, bgcolor: '#42a5f5', opacity: 0.1, borderRadius: '50%', zIndex: 0 }} />
      <Box sx={{ position: 'absolute', bottom: -120, right: -180, width: 450, height: 450, bgcolor: '#26c6da', opacity: 0.08, borderRadius: '50%', zIndex: 0 }} />

      <Container maxWidth="sm" sx={{ position: 'relative', zIndex: 1 }}>
        <motion.div initial={{ opacity: 0, y: 50 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.6 }}>
          <Paper elevation={12} sx={{
            p: { xs: 3, sm: 4 }, borderRadius: 4,
            background: 'rgba(255, 255, 255, 0.95)',
            backdropFilter: 'blur(20px)',
            border: '1px solid rgba(255, 255, 255, 0.2)',
          }}>
            <Box sx={{ textAlign: 'center', mb: 4 }}>
              <Box sx={{ width: 80, height: 80, margin: '0 auto', mb: 2 }}>
                <Lottie animationData={aiAnimation} style={{ width: 80, height: 80 }} loop />
              </Box>
              <Typography variant="h4" sx={{
                fontWeight: 700,
                background: 'linear-gradient(45deg, #1976d2, #26c6da)',
                backgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
                mb: 1,
              }}>Welcome Back!</Typography>
              <Typography variant="subtitle1" sx={{ color: '#666', mb: 3 }}>
                Continue your DSA learning journey with your AI buddy
              </Typography>
            </Box>

            {/* ✅ Only 1 Google button with correct styling */}
            <motion.div whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }} style={{ marginBottom: 16 }}>
              <Button
                fullWidth
                variant="contained"
                startIcon={<GoogleIcon />}
                onClick={handleGoogleLogin}
                sx={{
                  background: 'linear-gradient(to right, #4285F4, #34A853)',
                  color: 'white',
                  textTransform: 'none',
                  py: 1.5,
                  fontWeight: 600,
                  mb: 2,
                  borderRadius: 3,
                  boxShadow: '0 4px 16px rgba(66, 133, 244, 0.3)',
                  '&:hover': {
                    background: 'linear-gradient(to right, #3367d6, #2c8e4e)',
                    transform: 'translateY(-2px)',
                    boxShadow: '0 8px 24px rgba(66, 133, 244, 0.4)',
                  },
                  transition: 'all 0.2s',
                }}
              >
                Sign in with Google
              </Button>
            </motion.div>

            <Divider sx={{ my: 3, color: '#ccc' }}>
              <Typography variant="body2" sx={{ color: '#666', px: 2 }}>
                or continue with email
              </Typography>
            </Divider>

            <form onSubmit={handleSubmit(onSubmit)} noValidate>
              <TextField label="Email Address" fullWidth autoComplete="email" margin="normal"
                {...register('email')} error={!!errors.email} helperText={errors.email?.message} />

              <TextField label="Password" type={showPassword ? 'text' : 'password'} fullWidth autoComplete="current-password" margin="normal"
                {...register('password')} error={!!errors.password} helperText={errors.password?.message}
                InputProps={{
                  endAdornment: (
                    <InputAdornment position="end">
                      <IconButton onClick={() => setShowPassword((prev) => !prev)} edge="end">
                        {showPassword ? <VisibilityOff /> : <Visibility />}
                      </IconButton>
                    </InputAdornment>
                  ),
                }} />

              <Box mt={1} mb={3} textAlign="right">
                <Link href="#" underline="hover" variant="body2" sx={{ color: '#1976d2', fontWeight: 500 }}>
                  Forgot password?
                </Link>
              </Box>

              <Button type="submit" variant="contained" fullWidth size="large"
                disabled={!isDirty || !isValid || loading}
                startIcon={loading ? <CircularProgress size={20} color="inherit" /> : null}
                sx={{
                  mb: 3,
                  bgcolor: '#26c6da',
                  fontWeight: 600,
                  py: 1.5,
                  borderRadius: 3,
                  '&:hover': {
                    bgcolor: '#1976d2',
                  },
                }}
              >
                {loading ? 'Logging in...' : 'Login'}
              </Button>

              <Typography variant="body2" align="center" sx={{ color: '#666' }}>
                Don't have an account?{' '}
                <Button variant="text" size="small" onClick={() => navigate('/signup')} sx={{ color: '#1976d2', fontWeight: 600 }}>
                  Sign Up
                </Button>
              </Typography>
            </form>

            <Snackbar open={snackbarOpen} autoHideDuration={2500} onClose={handleSnackbarClose}
              anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}>
              <Alert severity={snackbarSeverity} onClose={handleSnackbarClose} sx={{ width: '100%' }}>
                {snackbarMsg}
              </Alert>
            </Snackbar>
          </Paper>
        </motion.div>
      </Container>
    </Box>
  );
};

export default Login;
