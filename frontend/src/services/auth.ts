/**
 * Authentication service for the Lean Six Sigma RAG Chatbot.
 * 
 * This service handles:
 * - User login
 * - User registration
 * - API error handling
 * - Token management
 */

import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL;

interface LoginCredentials {
  email: string;
  password: string;
}

interface RegisterData extends LoginCredentials {
  full_name: string;
}

interface AuthResponse {
  access_token: string;
  user: {
    id: number;
    email: string;
    full_name?: string;
  };
}

// Create axios instance with base URL
const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Handle API errors
const handleApiError = (error: any) => {
  if (error.response) {
    // The request was made and the server responded with a status code
    // that falls out of the range of 2xx
    throw new Error(error.response.data.detail || 'An error occurred');
  } else if (error.request) {
    // The request was made but no response was received
    throw new Error('No response from server');
  } else {
    // Something happened in setting up the request that triggered an Error
    throw new Error('Error setting up request');
  }
};

export const loginUser = async (credentials: LoginCredentials): Promise<AuthResponse> => {
  try {
    const response = await api.post<AuthResponse>('/api/v1/auth/login', credentials);
    return response.data;
  } catch (error) {
    handleApiError(error);
    throw error; // TypeScript needs this
  }
};

export const registerUser = async (data: RegisterData): Promise<AuthResponse> => {
  try {
    const response = await api.post<AuthResponse>('/api/v1/auth/register', data);
    return response.data;
  } catch (error) {
    handleApiError(error);
    throw error;
  }
};

// Add auth token to all subsequent requests
export const setAuthToken = (token: string | null) => {
  if (token) {
    api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
  } else {
    delete api.defaults.headers.common['Authorization'];
  }
}; 