import { beforeAll } from 'vitest';
import { checkApiHealth } from '../utils/test-utils';

// Mock localStorage for Node.js environment
class LocalStorageMock implements Storage {
  private store: { [key: string]: string };
  [name: string]: any;

  constructor() {
    this.store = {};
  }

  get length(): number {
    return Object.keys(this.store).length;
  }

  clear() {
    this.store = {};
  }

  getItem(key: string) {
    return this.store[key] || null;
  }

  setItem(key: string, value: string) {
    this.store[key] = String(value);
  }

  removeItem(key: string) {
    delete this.store[key];
  }

  key(n: number): string | null {
    const keys = Object.keys(this.store);
    return keys[n] || null;
  }
}

// Set up global mocks
global.localStorage = new LocalStorageMock();

// Global setup for all tests
beforeAll(async () => {
  // Ensure API is available before running tests
  const isHealthy = await checkApiHealth();
  if (!isHealthy) {
    throw new Error(
      'API is not available. Please ensure the backend server is running at ' +
        process.env.VITE_API_URL
    );
  }
}); 