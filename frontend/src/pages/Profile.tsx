/**
 * Profile page component for the Lean Six Sigma RAG Chatbot.
 * 
 * Features:
 * - Display user information
 * - Update profile settings
 * - Change password
 * - View usage statistics
 */

import { useState } from 'react';
import {
  Box,
  Paper,
  Typography,
  TextField,
  Button,
  Grid,
  Alert,
  CircularProgress,
  Divider,
  Card,
  CardContent,
  Stack,
} from '@mui/material';
import {
  Person as PersonIcon,
  QueryStats as StatsIcon,
  VpnKey as KeyIcon,
} from '@mui/icons-material';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { getProfile, updateProfile, changePassword, Profile } from '../services/profile';
import { useAuth } from '../hooks/useAuth';

interface PasswordForm {
  current_password: string;
  new_password: string;
  confirm_password: string;
}

export default function ProfilePage() {
  const { user } = useAuth();
  const queryClient = useQueryClient();
  const [passwordForm, setPasswordForm] = useState<PasswordForm>({
    current_password: '',
    new_password: '',
    confirm_password: '',
  });

  // Fetch profile data
  const { data: profile, isLoading: isLoadingProfile } = useQuery({
    queryKey: ['profile'],
    queryFn: getProfile,
  });

  // Update profile mutation
  const updateProfileMutation = useMutation({
    mutationFn: updateProfile,
    onSuccess: (data) => {
      queryClient.setQueryData(['profile'], data);
    },
  });

  // Change password mutation
  const changePasswordMutation = useMutation({
    mutationFn: changePassword,
    onSuccess: () => {
      setPasswordForm({
        current_password: '',
        new_password: '',
        confirm_password: '',
      });
    },
  });

  const handleProfileUpdate = async (e: React.FormEvent) => {
    e.preventDefault();
    const formData = new FormData(e.target as HTMLFormElement);
    const full_name = formData.get('full_name') as string;

    if (full_name !== profile?.full_name) {
      updateProfileMutation.mutate({ full_name });
    }
  };

  const handlePasswordChange = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (passwordForm.new_password !== passwordForm.confirm_password) {
      return; // Add error handling for password mismatch
    }

    changePasswordMutation.mutate({
      current_password: passwordForm.current_password,
      new_password: passwordForm.new_password,
    });
  };

  if (isLoadingProfile) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box sx={{ maxWidth: 800, mx: 'auto', p: 3 }}>
      <Typography variant="h4" gutterBottom sx={{ mb: 4 }}>
        Profile Settings
      </Typography>

      <Grid container spacing={4}>
        {/* Profile Information */}
        <Grid item xs={12}>
          <Paper sx={{ p: 3 }}>
            <Stack direction="row" spacing={2} alignItems="center" sx={{ mb: 3 }}>
              <PersonIcon color="primary" />
              <Typography variant="h6">Profile Information</Typography>
            </Stack>

            <form onSubmit={handleProfileUpdate}>
              <Grid container spacing={3}>
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    label="Email"
                    value={profile?.email}
                    disabled
                  />
                </Grid>
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    name="full_name"
                    label="Full Name"
                    defaultValue={profile?.full_name}
                  />
                </Grid>
                <Grid item xs={12}>
                  <Button
                    type="submit"
                    variant="contained"
                    disabled={updateProfileMutation.isPending}
                  >
                    {updateProfileMutation.isPending ? (
                      <CircularProgress size={24} />
                    ) : (
                      'Update Profile'
                    )}
                  </Button>
                </Grid>
              </Grid>
            </form>

            {updateProfileMutation.isError && (
              <Alert severity="error" sx={{ mt: 2 }}>
                {updateProfileMutation.error.message}
              </Alert>
            )}

            {updateProfileMutation.isSuccess && (
              <Alert severity="success" sx={{ mt: 2 }}>
                Profile updated successfully
              </Alert>
            )}
          </Paper>
        </Grid>

        {/* Usage Statistics */}
        <Grid item xs={12}>
          <Paper sx={{ p: 3 }}>
            <Stack direction="row" spacing={2} alignItems="center" sx={{ mb: 3 }}>
              <StatsIcon color="primary" />
              <Typography variant="h6">Usage Statistics</Typography>
            </Stack>

            <Grid container spacing={3}>
              <Grid item xs={12} sm={6}>
                <Card>
                  <CardContent>
                    <Typography color="text.secondary" gutterBottom>
                      Total Queries
                    </Typography>
                    <Typography variant="h4">
                      {profile?.queries_count || 0}
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
              <Grid item xs={12} sm={6}>
                <Card>
                  <CardContent>
                    <Typography color="text.secondary" gutterBottom>
                      Last Query
                    </Typography>
                    <Typography variant="body1">
                      {profile?.last_query_time
                        ? new Date(profile.last_query_time).toLocaleString()
                        : 'No queries yet'}
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
            </Grid>
          </Paper>
        </Grid>

        {/* Change Password */}
        <Grid item xs={12}>
          <Paper sx={{ p: 3 }}>
            <Stack direction="row" spacing={2} alignItems="center" sx={{ mb: 3 }}>
              <KeyIcon color="primary" />
              <Typography variant="h6">Change Password</Typography>
            </Stack>

            <form onSubmit={handlePasswordChange}>
              <Grid container spacing={3}>
                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    type="password"
                    label="Current Password"
                    value={passwordForm.current_password}
                    onChange={(e) =>
                      setPasswordForm((prev) => ({
                        ...prev,
                        current_password: e.target.value,
                      }))
                    }
                  />
                </Grid>
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    type="password"
                    label="New Password"
                    value={passwordForm.new_password}
                    onChange={(e) =>
                      setPasswordForm((prev) => ({
                        ...prev,
                        new_password: e.target.value,
                      }))
                    }
                  />
                </Grid>
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    type="password"
                    label="Confirm New Password"
                    value={passwordForm.confirm_password}
                    onChange={(e) =>
                      setPasswordForm((prev) => ({
                        ...prev,
                        confirm_password: e.target.value,
                      }))
                    }
                    error={
                      passwordForm.confirm_password !== '' &&
                      passwordForm.new_password !== passwordForm.confirm_password
                    }
                    helperText={
                      passwordForm.confirm_password !== '' &&
                      passwordForm.new_password !== passwordForm.confirm_password
                        ? 'Passwords do not match'
                        : ''
                    }
                  />
                </Grid>
                <Grid item xs={12}>
                  <Button
                    type="submit"
                    variant="contained"
                    disabled={
                      changePasswordMutation.isPending ||
                      !passwordForm.current_password ||
                      !passwordForm.new_password ||
                      !passwordForm.confirm_password ||
                      passwordForm.new_password !== passwordForm.confirm_password
                    }
                  >
                    {changePasswordMutation.isPending ? (
                      <CircularProgress size={24} />
                    ) : (
                      'Change Password'
                    )}
                  </Button>
                </Grid>
              </Grid>
            </form>

            {changePasswordMutation.isError && (
              <Alert severity="error" sx={{ mt: 2 }}>
                {changePasswordMutation.error.message}
              </Alert>
            )}

            {changePasswordMutation.isSuccess && (
              <Alert severity="success" sx={{ mt: 2 }}>
                Password changed successfully
              </Alert>
            )}
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
} 