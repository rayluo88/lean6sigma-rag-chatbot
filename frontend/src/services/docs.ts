/**
 * Documentation service for the Lean Six Sigma RAG Chatbot.
 * 
 * This service handles:
 * - Fetching documentation list
 * - Fetching document content
 * - Error handling
 */

import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL;

export interface Document {
  path: string;
  title: string;
  category: string;
  subcategory: string;
  tags: string[];
  last_updated: string;
}

export interface DocumentContent {
  metadata: {
    title: string;
    category: string;
    subcategory: string;
    tags: string[];
    last_updated: string;
  };
  content: string;
  html_content: string;
}

// Create axios instance with base URL
const api = axios.create({
  baseURL: `${API_URL}/api/v1/docs`,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Handle API errors
const handleApiError = (error: any) => {
  if (error.response) {
    if (error.response.status === 404) {
      throw new Error('Document not found');
    }
    throw new Error(error.response.data.detail || 'Failed to fetch documentation');
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

export const listDocuments = async (): Promise<Document[]> => {
  try {
    const response = await api.get<Document[]>('/list');
    return response.data;
  } catch (error) {
    handleApiError(error);
    throw error;
  }
};

export const getDocumentContent = async (path: string): Promise<DocumentContent> => {
  try {
    const response = await api.get<DocumentContent>(`/content/${path}`);
    return response.data;
  } catch (error) {
    handleApiError(error);
    throw error;
  }
}; 