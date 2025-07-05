import React, { useState } from 'react';
import {
  Box,
  Button,
  Card,
  CardContent,
  TextField,
  Typography,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Chip,
  Grid,
  Autocomplete
} from '@mui/material';
import { useAuth } from '../contexts/AuthContext';

const SKILL_LEVELS = ['beginner', 'intermediate', 'advanced'];
const PROGRAMMING_LANGUAGES = [
  'Python', 'JavaScript', 'Java', 'C++', 'C', 'C#', 'Go', 'Rust', 'Ruby', 'PHP'
];
const INTERESTS = [
  'Data Structures', 'Algorithms', 'Web Development', 'Mobile Development',
  'Machine Learning', 'AI', 'Databases', 'DevOps', 'Cybersecurity', 'Game Development'
];

const UserProfileForm: React.FC = () => {
  const { userProfile, updateUserProfile, exportUserData } = useAuth();
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    full_name: userProfile?.full_name || '',
    skill_level: userProfile?.skill_level || 'beginner',
    university: userProfile?.profile_data?.university || '',
    degree: userProfile?.profile_data?.degree || '',
    year: userProfile?.profile_data?.year || '',
    programming_languages: userProfile?.profile_data?.programming_languages || [],
    interests: userProfile?.profile_data?.interests || [],
    goals: userProfile?.profile_data?.goals || []
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    
    try {
      await updateUserProfile({
        full_name: formData.full_name,
        skill_level: formData.skill_level,
        profile_data: {
          university: formData.university,
          degree: formData.degree,
          year: formData.year,
          programming_languages: formData.programming_languages,
          interests: formData.interests,
          goals: formData.goals
        }
      });
      alert('Profile updated successfully!');
    } catch (error) {
      alert('Failed to update profile. Please try again.');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const handleExportData = async () => {
    try {
      await exportUserData();
    } catch (error) {
      alert('Failed to export data. Please try again.');
      console.error(error);
    }
  };

  return (
    <Card sx={{ maxWidth: 800, mx: 'auto', mt: 4 }}>
      <CardContent>
        <Typography variant="h5" gutterBottom>
          User Profile
        </Typography>
        
        <Box component="form" onSubmit={handleSubmit} sx={{ mt: 2 }}>
          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Full Name"
                value={formData.full_name}
                onChange={(e) => setFormData({ ...formData, full_name: e.target.value })}
                required
              />
            </Grid>
            
            <Grid item xs={12} md={6}>
              <FormControl fullWidth required>
                <InputLabel>Skill Level</InputLabel>
                <Select
                  value={formData.skill_level}
                  onChange={(e) => setFormData({ ...formData, skill_level: e.target.value })}
                  label="Skill Level"
                >
                  {SKILL_LEVELS.map((level) => (
                    <MenuItem key={level} value={level}>
                      {level.charAt(0).toUpperCase() + level.slice(1)}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>

            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="University"
                value={formData.university}
                onChange={(e) => setFormData({ ...formData, university: e.target.value })}
              />
            </Grid>

            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Degree"
                value={formData.degree}
                onChange={(e) => setFormData({ ...formData, degree: e.target.value })}
              />
            </Grid>

            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Year of Study"
                value={formData.year}
                onChange={(e) => setFormData({ ...formData, year: e.target.value })}
              />
            </Grid>

            <Grid item xs={12}>
              <Autocomplete
                multiple
                options={PROGRAMMING_LANGUAGES}
                value={formData.programming_languages}
                onChange={(_, newValue) => setFormData({ ...formData, programming_languages: newValue })}
                renderTags={(value, getTagProps) =>
                  value.map((option, index) => (
                    <Chip variant="outlined" label={option} {...getTagProps({ index })} />
                  ))
                }
                renderInput={(params) => (
                  <TextField
                    {...params}
                    label="Programming Languages"
                    placeholder="Select languages you know"
                  />
                )}
              />
            </Grid>

            <Grid item xs={12}>
              <Autocomplete
                multiple
                options={INTERESTS}
                value={formData.interests}
                onChange={(_, newValue) => setFormData({ ...formData, interests: newValue })}
                renderTags={(value, getTagProps) =>
                  value.map((option, index) => (
                    <Chip variant="outlined" label={option} {...getTagProps({ index })} />
                  ))
                }
                renderInput={(params) => (
                  <TextField
                    {...params}
                    label="Areas of Interest"
                    placeholder="Select your interests"
                  />
                )}
              />
            </Grid>

            <Grid item xs={12}>
              <Box sx={{ display: 'flex', gap: 2, mt: 3 }}>
                <Button
                  type="submit"
                  variant="contained"
                  disabled={loading}
                  sx={{ flex: 1 }}
                >
                  {loading ? 'Updating...' : 'Update Profile'}
                </Button>
                
                <Button
                  type="button"
                  variant="outlined"
                  onClick={handleExportData}
                  sx={{ flex: 1 }}
                >
                  Export My Data
                </Button>
              </Box>
            </Grid>
          </Grid>
        </Box>

        {userProfile && (
          <Box sx={{ mt: 4, p: 2, bgcolor: 'grey.50', borderRadius: 1 }}>
            <Typography variant="h6" gutterBottom>
              Current Statistics
            </Typography>
            <Typography variant="body2">
              Total Queries: {userProfile.statistics?.total_queries || 0}
            </Typography>
            <Typography variant="body2">
              Topics Completed: {userProfile.statistics?.topics_completed || 0}
            </Typography>
            <Typography variant="body2">
              Study Time: {userProfile.statistics?.total_study_time || 0} minutes
            </Typography>
          </Box>
        )}
      </CardContent>
    </Card>
  );
};

export default UserProfileForm;
