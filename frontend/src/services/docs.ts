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

const api = axios.create({
  baseURL: `${API_URL}/api/v1/docs`,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const listDocuments = async (): Promise<Document[]> => {
  try {
    const response = await api.get<Document[]>('/list');
    return response.data;
  } catch (error) {
    console.error('Error fetching documents:', error);
    throw new Error('Failed to fetch documents');
  }
};

export const getDocumentContent = async (path: string): Promise<DocumentContent> => {
  try {
    const response = await api.get<DocumentContent>(`/content/${path}`);
    return response.data;
  } catch (error) {
    console.error('Error fetching document content:', error);
    throw new Error('Failed to fetch document content');
  }
}; 