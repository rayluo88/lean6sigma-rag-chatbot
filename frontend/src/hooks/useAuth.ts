/**
 * Authentication hook for managing user authentication state.
 * 
 * This hook provides:
 * - Authentication state management
 * - Login/Logout functionality
 * - Token management
 * - User profile information
 */

import create from 'zustand';
import { persist } from 'zustand/middleware';

interface User {
  id: number;
  email: string;
  full_name?: string;
}

interface AuthState {
  token: string | null;
  user: User | null;
  isAuthenticated: boolean;
  login: (token: string, user: User) => void;
  logout: () => void;
}

const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      token: null,
      user: null,
      isAuthenticated: false,
      login: (token: string, user: User) =>
        set({ token, user, isAuthenticated: true }),
      logout: () => set({ token: null, user: null, isAuthenticated: false }),
    }),
    {
      name: 'auth-storage', // name of the item in localStorage
    }
  )
);

export const useAuth = () => {
  const { token, user, isAuthenticated, login, logout } = useAuthStore();

  return {
    token,
    user,
    isAuthenticated,
    login,
    logout,
  };
}; 