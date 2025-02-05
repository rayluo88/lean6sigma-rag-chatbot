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

export interface ChatResponse {
  response: string;
  remaining_queries: {
    daily_queries_remaining: number;
    daily_queries_limit: number;
    last_query_time: string;
  };
}

const api = axios.create({
  baseURL: `${API_URL}/api/v1/chat`,
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

export const sendMessage = async (message: ChatMessage): Promise<ChatResponse> => {
  try {
    const response = await api.post<ChatResponse>('/chat', message);
    return response.data;
  } catch (error: any) {
    if (error.response?.status === 429) {
      throw new Error('Daily query limit exceeded. Please try again tomorrow.');
    }
    throw new Error('Failed to send message. Please try again.');
  }
};

export const getRemainingQueries = async (): Promise<ChatResponse['remaining_queries']> => {
  try {
    const response = await api.get<ChatResponse['remaining_queries']>('/remaining');
    return response.data;
  } catch (error) {
    console.error('Error fetching remaining queries:', error);
    throw new Error('Failed to fetch remaining queries');
  }
}; 