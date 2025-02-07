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
import { setAuthToken as setChatAuthToken } from './chat';
import { setAuthToken as setDocsAuthToken } from './docs';
import { setAuthToken as setProfileAuthToken } from './profile';

const API_URL = import.meta.env.VITE_API_URL;
console.log('API_URL:', API_URL);

interface LoginCredentials {
  email: string;
  password: string;
}

interface RegisterData extends LoginCredentials {
  full_name: string;
}

interface RegisterResponse {
  id: number;
  email: string;
  full_name: string;
}

interface LoginResponse {
  access_token: string;
  token_type: string;
}

interface AuthResponse {
  access_token: string;
  token_type: string;
  user: {
    id: number;
    email: string;
    full_name: string;
  };
}

// Create axios instance with base URL
const api = axios.create({
  baseURL: `${API_URL}/api/v1/auth`,
  headers: {
    'Content-Type': 'application/json',
  },
});

console.log('Axios baseURL:', api.defaults.baseURL);

// Handle API errors
const handleApiError = (error: any) => {
  console.error('API Error:', error);
  if (error.response) {
    // The request was made and the server responded with a status code
    // that falls out of the range of 2xx
    throw new Error(error.response.data.detail || 'An error occurred');
  } else if (error.request) {
    // The request was made but no response was received
    console.error('Request error:', error.request);
    throw new Error('No response from server. Please check your connection.');
  } else {
    // Something happened in setting up the request that triggered an Error
    console.error('Setup error:', error.message);
    throw new Error('Error setting up request. Please try again.');
  }
};

export const registerUser = async (data: RegisterData): Promise<AuthResponse> => {
  try {
    console.log('Registering user with data:', data);
    console.log('Request URL:', `${API_URL}/api/v1/auth/register`);
    const registerResponse = await api.post<RegisterResponse>('/register', data);
    console.log('Register response data:', registerResponse.data);
    
    // After successful registration, login to get the token
    const loginResponse = await api.post<LoginResponse>('/login', {
      email: data.email,
      password: data.password,
    });
    console.log('Login response data:', loginResponse.data);
    
    const authResponse = {
      access_token: loginResponse.data.access_token,
      token_type: loginResponse.data.token_type,
      user: {
        id: registerResponse.data.id,
        email: registerResponse.data.email,
        full_name: registerResponse.data.full_name,
      },
    };
    
    // Store the token for subsequent requests
    setAuthToken(authResponse.access_token);
    return authResponse;
  } catch (error) {
    handleApiError(error);
    throw error;
  }
};

export const loginUser = async (credentials: LoginCredentials): Promise<AuthResponse> => {
  try {
    // Get the token
    const loginResponse = await api.post<LoginResponse>('/login', credentials);
    console.log('Login response data:', loginResponse.data);
    
    // For login, we'll use the email from credentials and set a default id
    // since we don't have a /me endpoint yet
    const authResponse = {
      access_token: loginResponse.data.access_token,
      token_type: loginResponse.data.token_type,
      user: {
        id: 0, // We don't have this information from login response
        email: credentials.email,
        full_name: '', // We don't have this information from login response
      },
    };
    
    // Store the token for subsequent requests
    setAuthToken(authResponse.access_token);
    return authResponse;
  } catch (error) {
    handleApiError(error);
    throw error;
  }
};

// Add auth token to all subsequent requests across all services
export const setAuthToken = (token: string | null) => {
  if (token) {
    api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
    setChatAuthToken(token);
    setDocsAuthToken(token);
    setProfileAuthToken(token);
  } else {
    delete api.defaults.headers.common['Authorization'];
    setChatAuthToken(null);
    setDocsAuthToken(null); 
    setProfileAuthToken(null);
  }
}; 