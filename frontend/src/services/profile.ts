/**
 * Profile service for the Lean Six Sigma RAG Chatbot.
 * 
 * This service handles:
 * - Fetching user profile
 * - Updating profile information
 * - Changing password
 * - Fetching usage statistics
 */

import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL;

export interface Profile {
  id: number;
  email: string;
  full_name: string;
  created_at: string;
  queries_count: number;
  last_query_time: string;
}

export interface UpdateProfileData {
  full_name?: string;
}

export interface ChangePasswordData {
  current_password: string;
  new_password: string;
}

const api = axios.create({
  baseURL: `${API_URL}/api/v1/profile`,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth token to requests
export const setAuthToken = (token: string | null) => {
  if (token) {
    api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
  } else {
    delete api.defaults.headers.common['Authorization'];
  }
};

export const getProfile = async (): Promise<Profile> => {
  try {
    const response = await api.get<Profile>('/me');
    return response.data;
  } catch (error) {
    console.error('Error fetching profile:', error);
    throw new Error('Failed to fetch profile');
  }
};

export const updateProfile = async (data: UpdateProfileData): Promise<Profile> => {
  try {
    const response = await api.patch<Profile>('/me', data);
    return response.data;
  } catch (error) {
    console.error('Error updating profile:', error);
    throw new Error('Failed to update profile');
  }
};

export const changePassword = async (data: ChangePasswordData): Promise<void> => {
  try {
    await api.post('/change-password', data);
  } catch (error: any) {
    if (error.response?.status === 400) {
      throw new Error('Current password is incorrect');
    }
    throw new Error('Failed to change password');
  }
}; 