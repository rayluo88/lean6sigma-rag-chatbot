/**
 * Chat service for the Lean Six Sigma RAG Chatbot.
 * 
 * This service handles:
 * - Sending chat messages
 * - Retrieving chat history
 * - Query limit tracking
 */

import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL;

export interface ChatMessage {
  query: string;
}

export interface ChatHistoryItem {
  id: number;
  query: string;
  response: string;
  created_at: string;
}

export interface ChatResponse {
  response: string;
  history_id: number;
  remaining_queries: {
    daily_queries_remaining: number;
    daily_queries_limit: number;
    last_query_time: string | null;
  };
}

// Create axios instance with base URL
const api = axios.create({
  baseURL: `${API_URL}/api/v1/chat`,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Handle API errors
const handleApiError = (error: any) => {
  if (error.response) {
    if (error.response.status === 429) {
      throw new Error('Daily query limit exceeded. Please try again tomorrow.');
    }
    throw new Error(error.response.data.detail || 'Failed to send message');
  } else if (error.request) {
    throw new Error('No response from server. Please check your connection.');
  } else {
    throw new Error('Error setting up request. Please try again.');
  }
};

// Add auth token to requests
export const setAuthToken = (token: string | null) => {
  if (token) {
    api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
  } else {
    delete api.defaults.headers.common['Authorization'];
  }
};

export const sendMessage = async (message: ChatMessage): Promise<ChatResponse> => {
  try {
    const response = await api.post<ChatResponse>('/chat', message);
    return response.data;
  } catch (error) {
    handleApiError(error);
    throw error;
  }
};

export const getChatHistory = async (): Promise<ChatHistoryItem[]> => {
  try {
    const response = await api.get<ChatHistoryItem[]>('/history');
    return response.data;
  } catch (error) {
    handleApiError(error);
    throw error;
  }
};

export const getRemainingQueries = async (): Promise<ChatResponse['remaining_queries']> => {
  try {
    const response = await api.get<ChatResponse['remaining_queries']>('/remaining');
    return response.data;
  } catch (error) {
    handleApiError(error);
    throw error;
  }
}; 