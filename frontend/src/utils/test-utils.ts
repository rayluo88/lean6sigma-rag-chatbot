/**
 * Test utilities for API integration testing
 */

import { setAuthToken } from '../services/auth';
import { ChatMessage } from '../services/chat';

export const TEST_USER = {
  email: 'test@example.com',
  password: 'testpassword123',
  full_name: 'Test User',
};

export const TEST_CHAT_MESSAGE: ChatMessage = {
  query: 'What is Six Sigma?',
};

export const clearAuthToken = () => {
  setAuthToken(null);
  localStorage.clear();
};

export const delay = (ms: number) => new Promise(resolve => setTimeout(resolve, ms));

export const checkApiHealth = async () => {
  try {
    const response = await fetch(`${import.meta.env.VITE_API_URL}/health`);
    const data = await response.json();
    return data.status === 'healthy';
  } catch (error) {
    return false;
  }
};

export const validateAuthResponse = (response: any) => {
  const requiredFields = ['access_token', 'token_type', 'user'];
  return requiredFields.every(field => field in response);
};

export const validateChatResponse = (response: any) => {
  const requiredFields = ['response', 'remaining_queries'];
  return requiredFields.every(field => field in response);
}; 