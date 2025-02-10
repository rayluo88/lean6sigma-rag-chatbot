import { describe, it, expect, beforeAll, beforeEach } from 'vitest';
import { sendMessage, getRemainingQueries, getChatHistory } from '../chat';
import { loginUser, registerUser } from '../auth';
import {
  TEST_USER,
  TEST_CHAT_MESSAGE,
  clearAuthToken,
  checkApiHealth,
  validateChatResponse,
} from '../../utils/test-utils';

describe('Chat Service Integration Tests', () => {
  let testUser: typeof TEST_USER;

  beforeAll(async () => {
    // Check if API is available
    const isHealthy = await checkApiHealth();
    if (!isHealthy) {
      throw new Error('API is not available. Please start the backend server.');
    }

    // Create a unique test user for all chat tests
    testUser = {
      ...TEST_USER,
      email: `chat_test_${Date.now()}@example.com`,
    };
    await registerUser(testUser);
  });

  beforeEach(async () => {
    clearAuthToken();
    // Login before each test to get a fresh token
    const authResponse = await loginUser({
      email: testUser.email,
      password: testUser.password,
    });
    expect(authResponse.access_token).toBeTruthy();
    // Add a small delay to ensure token is set
    await new Promise(resolve => setTimeout(resolve, 100));
  });

  it('should send a message and get a response', async () => {
    const response = await sendMessage(TEST_CHAT_MESSAGE);
    expect(validateChatResponse(response)).toBe(true);
    expect(response.response).toBeTruthy();
    expect(response.remaining_queries).toBeDefined();
    expect(response.history_id).toBeDefined();
  });

  it('should get chat history', async () => {
    // First send a message
    await sendMessage(TEST_CHAT_MESSAGE);
    
    // Then get history
    const history = await getChatHistory();
    expect(Array.isArray(history)).toBe(true);
    if (history.length > 0) {
      const lastMessage = history[0];
      expect(lastMessage.id).toBeDefined();
      expect(lastMessage.query).toBe(TEST_CHAT_MESSAGE.query);
      expect(lastMessage.response).toBeTruthy();
      expect(lastMessage.created_at).toBeTruthy();
    }
  });

  it('should get remaining queries', async () => {
    const response = await getRemainingQueries();
    expect(response.daily_queries_remaining).toBeDefined();
    expect(response.daily_queries_limit).toBeDefined();
    expect(typeof response.daily_queries_remaining).toBe('number');
    expect(typeof response.daily_queries_limit).toBe('number');
  });

  it('should fail without authentication', async () => {
    clearAuthToken();
    await expect(sendMessage(TEST_CHAT_MESSAGE)).rejects.toThrow();
    await expect(getChatHistory()).rejects.toThrow();
  });

  it('should handle empty queries', async () => {
    await expect(
      sendMessage({ query: '' })
    ).rejects.toThrow();
  });

  it('should track remaining queries after sending messages', async () => {
    const initialQueries = await getRemainingQueries();
    await sendMessage(TEST_CHAT_MESSAGE);
    const remainingQueries = await getRemainingQueries();
    expect(remainingQueries.daily_queries_remaining).toBe(
      initialQueries.daily_queries_remaining - 1
    );
  });

  it('should maintain chat history order', async () => {
    // Send multiple messages
    const messages = [
      { query: 'First message' },
      { query: 'Second message' },
      { query: 'Third message' },
    ];
    
    for (const msg of messages) {
      await sendMessage(msg);
    }
    
    // Get history and verify order
    const history = await getChatHistory();
    expect(history.length).toBeGreaterThanOrEqual(messages.length);
    
    // History should be in reverse chronological order
    for (let i = 0; i < messages.length; i++) {
      expect(history[i].query).toBe(messages[messages.length - 1 - i].query);
    }
  });
}); 