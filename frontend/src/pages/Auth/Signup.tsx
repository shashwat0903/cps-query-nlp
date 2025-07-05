import React, { useState } from 'react';
import {
  Box,
  Button,
  Container,
  IconButton,
  InputAdornment,
  Paper,
  Snackbar,
  TextField,
  Typography,
  Alert,
  CircularProgress,
  Divider,
  MenuItem
} from '@mui/material';
import { Visibility, VisibilityOff } from '@mui/icons-material';
import { useForm } from 'react-hook-form';
import { useNavigate } from 'react-router-dom';
import { z } from 'zod';
import { zodResolver } from '@hookform/resolvers/zod';
import { motion } from 'framer-motion';
import GoogleIcon from '@mui/icons-material/Google';
// Firebase auth no longer used directly here
import { useAuth } from '../../contexts/AuthContext';
import Lottie from 'lottie-react';
import aiAnimation from '../../assets/ai-lottie.json';
import { userAPI } from '../../services/api';
import { localStorageAuth } from '../../services/localStorageAuth';

// Zod schema
const SignupSchema = z.object({
  email: z.string().email({ message: 'Enter a valid email address' }),
  password: z.string().min(6, { message: 'Minimum 6 characters required' }),
  confirmPassword: z.string().min(6, { message: 'Please confirm your password' }),
  fullName: z.string().min(2, { message: 'Full name is required' }),
  skillLevel: z.enum(['beginner', 'intermediate', 'advanced'], { message: 'Please select a skill level' }),
  university: z.string().optional(),
  degree: z.string().optional(),
  year: z.string().optional(),
}).refine((data) => data.password === data.confirmPassword, {
  path: ['confirmPassword'],
  message: "Passwords don't match",
});

type SignupFormData = z.infer<typeof SignupSchema>;

const Signup: React.FC = () => {
  const navigate = useNavigate();
  const { signupWithProfile, refreshProfile } = useAuth();
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [snackbarOpen, setSnackbarOpen] = useState(false);
  const [snackbarMsg, setSnackbarMsg] = useState('');
  const [snackbarSeverity, setSnackbarSeverity] = useState<'success' | 'error'>('success');

  const {
    register,
    handleSubmit,
    formState: { errors, isDirty, isValid },
  } = useForm<SignupFormData>({
    resolver: zodResolver(SignupSchema),
    mode: 'onChange',
  });

  const onSubmit = async (data: SignupFormData) => {
    setLoading(true);
    try {
      console.log('🔄 Creating user account directly in backend...');
      
      // Skip Firebase user creation and use the API directly
      
      // Prepare additional profile data
      const additionalData = {
        university: data.university || '',
        degree: data.degree || '',
        year: data.year || '',
        interests: [],
        programming_languages: [],
        goals: []
      };
      
      console.log('🔄 Creating user profile...');
      
      let signupResponse;
      
      try {
        // Try backend first
        console.log('🔄 Attempting signup with backend API...', data.email);
        signupResponse = await userAPI.signup(
          data.email,
          data.password,
          data.fullName,
          data.skillLevel,
          additionalData
        );
        console.log('✅ Backend signup response:', signupResponse);
        
        if (!signupResponse.success) {
          console.error('❌ Backend signup failed:', signupResponse.message);
          throw new Error(signupResponse.message || 'Signup failed on backend');
        }
      } catch (apiError) {
        console.warn('❌ Backend API unavailable or signup failed, falling back to localStorage:', apiError);
        // Fall back to localStorage if backend fails
        console.log('🔄 Attempting signup with localStorage...');
        signupResponse = await localStorageAuth.signup(
          data.email,
          data.password,
          data.fullName,
          data.skillLevel,
          additionalData
        );
        console.log('✅ localStorage signup response:', signupResponse);
        
        if (!signupResponse.success) {
          console.error('❌ localStorage signup failed:', signupResponse.message);
          throw new Error(signupResponse.message || 'Signup failed on localStorage');
        }
      }
      
      if (signupResponse.success && signupResponse.user) {
        console.log('✅ Signup successful:', signupResponse.user.full_name);
        
        // Important: Update auth context with the new user profile
        if (signupResponse.user) {
          // Create a User object structure that AuthContext expects
          console.log('🔄 Creating Firebase-compatible user object...');
          const fakeFirebaseUser = {
            email: signupResponse.user.email,
            displayName: signupResponse.user.full_name,
            uid: signupResponse.user.user_id
          } as any;
          
          // Use signupWithProfile to properly update the auth context
          console.log('🔄 Updating auth context with new user profile...');
          await signupWithProfile(fakeFirebaseUser, {
            skillLevel: signupResponse.user.skill_level,
            ...additionalData
          });
          
          // Refresh profile to ensure we have the latest data
          console.log('🔄 Refreshing profile to get latest data...');
          await refreshProfile();
          console.log('✅ Profile refreshed');
          
          // Save user data to localStorage for offline access
          console.log('🔄 Saving user data to localStorage...');
          localStorage.setItem('userProfile', JSON.stringify(signupResponse.user));
          localStorage.setItem('chatHistory', JSON.stringify(signupResponse.chat_history || []));
          localStorage.setItem('userId', signupResponse.user.user_id);
        }
        
        setSnackbarMsg('Signup successful! Redirecting to chat...');
        setSnackbarSeverity('success');
        setSnackbarOpen(true);

        // Navigate to chat after successful signup
        setTimeout(() => {
          navigate('/chat');
        }, 1500);
      } else {
        throw new Error(signupResponse.message || 'Signup failed');
      }
      
    } catch (error: any) {
      console.error('❌ Signup error:', error);
      let errorMessage = error.message || 'Signup failed. Please try again.';
      
      // Provide more specific error messages based on common issues
      if (errorMessage.includes('already exists')) {
        errorMessage = 'An account with this email already exists. Please log in instead.';
      } else if (errorMessage.includes('network') || errorMessage.includes('timeout')) {
        errorMessage = 'Network error. Please check your connection and try again.';
      } else if (errorMessage.includes('password')) {
        errorMessage = 'Password error: ' + errorMessage;
      }
      
      setSnackbarMsg(errorMessage);
      setSnackbarSeverity('error');
      setSnackbarOpen(true);
    } finally {
      setLoading(false);
    }
  };

  const handleSnackbarClose = () => {
    setSnackbarOpen(false);
  };

  const handleGoogleSignup = async () => {
    // For now, redirect to Google login page which will handle the signup process
    navigate('/google-login');
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
      {/* Decorative background shapes */}
      <Box sx={{
        position: 'absolute',
        top: -100,
        left: -150,
        width: 400,
        height: 400,
        bgcolor: '#42a5f5',
        opacity: 0.1,
        borderRadius: '50%',
        zIndex: 0,
      }} />
      <Box sx={{
        position: 'absolute',
        bottom: -120,
        right: -180,
        width: 450,
        height: 450,
        bgcolor: '#26c6da',
        opacity: 0.08,
        borderRadius: '50%',
        zIndex: 0,
      }} />

      <Container maxWidth="sm" sx={{ position: 'relative', zIndex: 1 }}>
        <motion.div
          initial={{ opacity: 0, y: 50 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
        >
          <Paper 
            elevation={12} 
            sx={{ 
              p: { xs: 3, sm: 4 }, 
              borderRadius: 4,
              background: 'rgba(255, 255, 255, 0.95)',
              backdropFilter: 'blur(20px)',
              border: '1px solid rgba(255, 255, 255, 0.2)',
            }}
          >
            {/* Header with Mascot */}
            <Box sx={{ textAlign: 'center', mb: 4 }}>
              <Box sx={{ width: 80, height: 80, margin: '0 auto', mb: 2 }}>
                <Lottie 
                  animationData={aiAnimation} 
                  style={{ width: 80, height: 80 }} 
                  loop 
                />
              </Box>
              <Typography 
                variant="h4" 
                sx={{ 
                  fontWeight: 700,
                  background: 'linear-gradient(45deg, #1976d2, #26c6da)',
                  backgroundClip: 'text',
                  WebkitBackgroundClip: 'text',
                  WebkitTextFillColor: 'transparent',
                  mb: 1,
                }}
              >
                Join Your AI Buddy!
              </Typography>
              <Typography variant="subtitle1" sx={{ color: '#666', mb: 3 }}>
                Start your personalized DSA learning journey today
              </Typography>
            </Box>

            {/* Google Sign-In */}
            <motion.div
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              style={{ marginBottom: 16 }}
            >
              <Button
                fullWidth
                variant="contained"
                startIcon={<GoogleIcon />}
                onClick={handleGoogleSignup}
                sx={{
                  background: 'linear-gradient(to right, #4285F4, #34A853)',
                  color: 'white',
                  textTransform: 'none',
                  py: 1.5,
                  fontWeight: 600,
                  mb: 3,
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
                Sign up with Google
              </Button>
            </motion.div>

            <Divider sx={{ mb: 3, color: '#ccc' }}>
              <Typography variant="body2" sx={{ color: '#666', px: 2 }}>
                or create account with email
              </Typography>
            </Divider>

            <form onSubmit={handleSubmit(onSubmit)} noValidate>
              <TextField
                label="Email Address"
                fullWidth
                margin="normal"
                {...register('email')}
                error={!!errors.email}
                helperText={errors.email?.message}
                sx={{
                  '& .MuiOutlinedInput-root': {
                    borderRadius: 2,
                    '&:hover fieldset': {
                      borderColor: '#42a5f5',
                    },
                    '&.Mui-focused fieldset': {
                      borderColor: '#1976d2',
                    },
                  },
                }}
              />
              <TextField
                label="Password"
                type={showPassword ? 'text' : 'password'}
                fullWidth
                margin="normal"
                {...register('password')}
                error={!!errors.password}
                helperText={errors.password?.message}
                InputProps={{
                  endAdornment: (
                    <InputAdornment position="end">
                      <IconButton 
                        onClick={() => setShowPassword((prev) => !prev)}
                        sx={{ color: '#666' }}
                      >
                        {showPassword ? <VisibilityOff /> : <Visibility />}
                      </IconButton>
                    </InputAdornment>
                  ),
                }}
                sx={{
                  '& .MuiOutlinedInput-root': {
                    borderRadius: 2,
                    '&:hover fieldset': {
                      borderColor: '#42a5f5',
                    },
                    '&.Mui-focused fieldset': {
                      borderColor: '#1976d2',
                    },
                  },
                }}
              />
              <TextField
                label="Confirm Password"
                type={showConfirmPassword ? 'text' : 'password'}
                fullWidth
                margin="normal"
                {...register('confirmPassword')}
                error={!!errors.confirmPassword}
                helperText={errors.confirmPassword?.message}
                InputProps={{
                  endAdornment: (
                    <InputAdornment position="end">
                      <IconButton 
                        onClick={() => setShowConfirmPassword((prev) => !prev)}
                        sx={{ color: '#666' }}
                      >
                        {showConfirmPassword ? <VisibilityOff /> : <Visibility />}
                      </IconButton>
                    </InputAdornment>
                  ),
                }}
                sx={{
                  '& .MuiOutlinedInput-root': {
                    borderRadius: 2,
                    '&:hover fieldset': {
                      borderColor: '#42a5f5',
                    },
                    '&.Mui-focused fieldset': {
                      borderColor: '#1976d2',
                    },
                  },
                }}
              />
              
              <TextField
                label="Full Name"
                fullWidth
                margin="normal"
                {...register('fullName')}
                error={!!errors.fullName}
                helperText={errors.fullName?.message}
                sx={{
                  '& .MuiOutlinedInput-root': {
                    borderRadius: 2,
                    '&:hover fieldset': {
                      borderColor: '#42a5f5',
                    },
                    '&.Mui-focused fieldset': {
                      borderColor: '#1976d2',
                    },
                  },
                }}
              />
              
              <TextField
                label="Skill Level"
                select
                fullWidth
                margin="normal"
                {...register('skillLevel')}
                error={!!errors.skillLevel}
                helperText={errors.skillLevel?.message}
                sx={{
                  '& .MuiOutlinedInput-root': {
                    borderRadius: 2,
                    '&:hover fieldset': {
                      borderColor: '#42a5f5',
                    },
                    '&.Mui-focused fieldset': {
                      borderColor: '#1976d2',
                    },
                  },
                }}
              >
                <MenuItem value="beginner">Beginner</MenuItem>
                <MenuItem value="intermediate">Intermediate</MenuItem>
                <MenuItem value="advanced">Advanced</MenuItem>
              </TextField>
              
              <TextField
                label="University (Optional)"
                fullWidth
                margin="normal"
                {...register('university')}
                error={!!errors.university}
                helperText={errors.university?.message}
                sx={{
                  '& .MuiOutlinedInput-root': {
                    borderRadius: 2,
                    '&:hover fieldset': {
                      borderColor: '#42a5f5',
                    },
                    '&.Mui-focused fieldset': {
                      borderColor: '#1976d2',
                    },
                  },
                }}
              />
              
              <TextField
                label="Degree (Optional)"
                fullWidth
                margin="normal"
                {...register('degree')}
                error={!!errors.degree}
                helperText={errors.degree?.message}
                sx={{
                  '& .MuiOutlinedInput-root': {
                    borderRadius: 2,
                    '&:hover fieldset': {
                      borderColor: '#42a5f5',
                    },
                    '&.Mui-focused fieldset': {
                      borderColor: '#1976d2',
                    },
                  },
                }}
              />
              
              <TextField
                label="Year (Optional)"
                fullWidth
                margin="normal"
                {...register('year')}
                error={!!errors.year}
                helperText={errors.year?.message}
                sx={{
                  '& .MuiOutlinedInput-root': {
                    borderRadius: 2,
                    '&:hover fieldset': {
                      borderColor: '#42a5f5',
                    },
                    '&.Mui-focused fieldset': {
                      borderColor: '#1976d2',
                    },
                  },
                }}
              />
              
              <Button
                type="submit"
                variant="contained"
                fullWidth
                size="large"
                sx={{ 
                  mt: 3, 
                  mb: 3,
                  bgcolor: '#26c6da',
                  color: '#fff',
                  fontWeight: 600,
                  py: 1.5,
                  borderRadius: 3,
                  boxShadow: '0 4px 16px rgba(38, 198, 218, 0.3)',
                  '&:hover': {
                    bgcolor: '#1976d2',
                    transform: 'translateY(-2px)',
                    boxShadow: '0 8px 24px rgba(25, 118, 210, 0.4)',
                  },
                  '&:disabled': {
                    bgcolor: '#ccc',
                    transform: 'none',
                    boxShadow: 'none',
                  },
                  transition: 'all 0.2s',
                }}
                disabled={!isDirty || !isValid || loading}
                startIcon={loading ? <CircularProgress size={20} /> : null}
              >
                {loading ? 'Creating Account...' : 'Create Account'}
              </Button>
            </form>

            <Typography variant="body2" align="center" sx={{ color: '#666' }}>
              Already have an account?{' '}
              <Button 
                variant="text" 
                onClick={() => navigate('/login')}
                sx={{ 
                  color: '#1976d2',
                  fontWeight: 600,
                  textTransform: 'none',
                  '&:hover': {
                    color: '#26c6da',
                    background: 'rgba(25, 118, 210, 0.1)',
                  },
                }}
              >
                Log In
              </Button>
            </Typography>

            <Snackbar
              open={snackbarOpen}
              autoHideDuration={2500}
              onClose={handleSnackbarClose}
              anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
            >
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

export default Signup;
