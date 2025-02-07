import { describe, it, expect, beforeAll, afterEach } from 'vitest';
import { loginUser, registerUser } from '../auth';
import { TEST_USER, clearAuthToken, checkApiHealth, validateAuthResponse } from '../../utils/test-utils';

describe('Auth Service Integration Tests', () => {
  beforeAll(async () => {
    // Check if API is available
    const isHealthy = await checkApiHealth();
    if (!isHealthy) {
      throw new Error('API is not available. Please start the backend server.');
    }
  });

  afterEach(() => {
    clearAuthToken();
  });

  it('should register a new user', async () => {
    const uniqueUser = {
      ...TEST_USER,
      email: `test${Date.now()}@example.com`,
    };

    const response = await registerUser(uniqueUser);
    expect(validateAuthResponse(response)).toBe(true);
    expect(response.user.email).toBe(uniqueUser.email);
    expect(response.user.full_name).toBe(uniqueUser.full_name);
  });

  it('should login an existing user', async () => {
    // First register a new user
    const uniqueUser = {
      ...TEST_USER,
      email: `test${Date.now()}@example.com`,
    };
    await registerUser(uniqueUser);

    // Then try to login
    const response = await loginUser({
      email: uniqueUser.email,
      password: uniqueUser.password,
    });
    expect(validateAuthResponse(response)).toBe(true);
    expect(response.user.email).toBe(uniqueUser.email);
  });

  it('should fail with invalid credentials', async () => {
    // First register a new user
    const uniqueUser = {
      ...TEST_USER,
      email: `test${Date.now()}@example.com`,
    };
    await registerUser(uniqueUser);

    // Then try to login with wrong password
    await expect(
      loginUser({
        email: uniqueUser.email,
        password: 'wrongpassword',
      })
    ).rejects.toThrow();
  });

  it('should fail registering with existing email', async () => {
    // First register a user
    const uniqueUser = {
      ...TEST_USER,
      email: `test${Date.now()}@example.com`,
    };
    await registerUser(uniqueUser);

    // Try to register again with same email
    await expect(registerUser(uniqueUser)).rejects.toThrow();
  });
}); 