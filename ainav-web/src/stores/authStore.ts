import { create } from "zustand";
import { persist, createJSONStorage } from "zustand/middleware";

// =============================================================================
// TYPES
// =============================================================================

export interface User {
  id: string;
  email: string;
  username: string;
  phone?: string;
  is_active: boolean;
  is_superuser: boolean;
  created_at: string;
  updated_at: string;
}

export interface RegisterData {
  email: string;
  username: string;
  password: string;
  phone?: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  expires_in?: number;
}

export interface JWTPayload {
  sub: string; // user_id
  email?: string;
  username?: string;
  exp: number;
  iat?: number;
}

interface AuthState {
  // State
  user: User | null;
  token: string | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  error: string | null;
  tokenExpiry: number | null;

  // Actions
  login: (email: string, password: string) => Promise<void>;
  register: (userData: RegisterData) => Promise<void>;
  logout: () => void;
  checkAuth: () => Promise<void>;
  clearError: () => void;
  updateUser: (data: Partial<User>) => Promise<void>;
  refreshToken: () => Promise<void>;
  setLoading: (loading: boolean) => void;
}

// =============================================================================
// API CONFIGURATION
// =============================================================================

const USER_API =
  process.env.NEXT_PUBLIC_USER_API || "http://localhost:8003/v1";

// =============================================================================
// UTILITY FUNCTIONS
// =============================================================================

/**
 * Decode JWT token payload without verification
 * Note: Verification should be done server-side
 */
function decodeJWT(token: string): JWTPayload | null {
  try {
    const parts = token.split(".");
    if (parts.length !== 3) return null;

    const payload = parts[1];
    // Handle Base64URL encoding
    const base64 = payload.replace(/-/g, "+").replace(/_/g, "/");
    const jsonPayload = decodeURIComponent(
      atob(base64)
        .split("")
        .map((c) => "%" + ("00" + c.charCodeAt(0).toString(16)).slice(-2))
        .join("")
    );

    return JSON.parse(jsonPayload);
  } catch {
    return null;
  }
}

/**
 * Check if JWT token is expired
 */
function isTokenExpired(token: string): boolean {
  const payload = decodeJWT(token);
  if (!payload || !payload.exp) return true;

  // Add 30 second buffer before expiry
  const now = Math.floor(Date.now() / 1000);
  return payload.exp < now + 30;
}

/**
 * Get auth header for API calls
 */
export function getAuthHeader(): Record<string, string> {
  if (typeof window === "undefined") return {};

  const stored = localStorage.getItem("auth-storage");
  if (!stored) return {};

  try {
    const { state } = JSON.parse(stored);
    if (state?.token) {
      return { Authorization: `Bearer ${state.token}` };
    }
  } catch {
    return {};
  }

  return {};
}

/**
 * Fetch with auth header
 */
async function authFetch<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const url = `${USER_API}${endpoint}`;
  const headers = {
    "Content-Type": "application/json",
    ...getAuthHeader(),
    ...options.headers,
  };

  const response = await fetch(url, {
    ...options,
    headers,
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(error.detail || `API Error: ${response.status}`);
  }

  // Handle empty responses
  const text = await response.text();
  if (!text) return {} as T;

  return JSON.parse(text);
}

// =============================================================================
// AUTH STORE
// =============================================================================

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      // Initial state
      user: null,
      token: null,
      isLoading: false,
      isAuthenticated: false,
      error: null,
      tokenExpiry: null,

      // Set loading state
      setLoading: (loading: boolean) => {
        set({ isLoading: loading });
      },

      // Login action
      login: async (email: string, password: string) => {
        set({ isLoading: true, error: null });

        try {
          // OAuth2 password flow uses FormData
          const formData = new FormData();
          formData.append("username", email);
          formData.append("password", password);

          const response = await fetch(`${USER_API}/auth/login`, {
            method: "POST",
            body: formData,
          });

          if (!response.ok) {
            const error = await response.json().catch(() => ({}));
            throw new Error(error.detail || "登录失败");
          }

          const data: LoginResponse = await response.json();
          const payload = decodeJWT(data.access_token);

          if (!payload) {
            throw new Error("无效的认证令牌");
          }

          // Fetch user profile with the new token
          const userResponse = await fetch(`${USER_API}/users/me`, {
            headers: {
              Authorization: `Bearer ${data.access_token}`,
            },
          });

          let user: User | null = null;
          if (userResponse.ok) {
            user = await userResponse.json();
          } else {
            // Construct minimal user from JWT if profile fetch fails
            user = {
              id: payload.sub,
              email: payload.email || email,
              username: payload.username || email.split("@")[0],
              is_active: true,
              is_superuser: false,
              created_at: new Date().toISOString(),
              updated_at: new Date().toISOString(),
            };
          }

          set({
            token: data.access_token,
            user,
            isAuthenticated: true,
            isLoading: false,
            error: null,
            tokenExpiry: payload.exp,
          });
        } catch (error) {
          set({
            isLoading: false,
            error: error instanceof Error ? error.message : "登录失败",
            isAuthenticated: false,
            user: null,
            token: null,
          });
          throw error;
        }
      },

      // Register action
      register: async (userData: RegisterData) => {
        set({ isLoading: true, error: null });

        try {
          const response = await fetch(`${USER_API}/auth/register`, {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
            },
            body: JSON.stringify(userData),
          });

          if (!response.ok) {
            const error = await response.json().catch(() => ({}));
            throw new Error(error.detail || "注册失败");
          }

          const user: User = await response.json();

          // Auto-login after registration
          await get().login(userData.email, userData.password);
        } catch (error) {
          set({
            isLoading: false,
            error: error instanceof Error ? error.message : "注册失败",
          });
          throw error;
        }
      },

      // Logout action
      logout: () => {
        set({
          user: null,
          token: null,
          isAuthenticated: false,
          error: null,
          tokenExpiry: null,
          isLoading: false,
        });

        // Clear any other auth-related storage
        if (typeof window !== "undefined") {
          localStorage.removeItem("auth-storage");
        }
      },

      // Check auth status on app load
      checkAuth: async () => {
        const { token } = get();

        if (!token) {
          set({ isAuthenticated: false, user: null });
          return;
        }

        // Check if token is expired
        if (isTokenExpired(token)) {
          // Try to refresh token
          try {
            await get().refreshToken();
          } catch {
            get().logout();
            return;
          }
        }

        // Validate token by fetching user profile
        set({ isLoading: true });

        try {
          const user = await authFetch<User>("/users/me");
          set({
            user,
            isAuthenticated: true,
            isLoading: false,
            error: null,
          });
        } catch (error) {
          // Token invalid, logout
          get().logout();
        }
      },

      // Clear error
      clearError: () => {
        set({ error: null });
      },

      // Update user profile
      updateUser: async (data: Partial<User>) => {
        set({ isLoading: true, error: null });

        try {
          const updatedUser = await authFetch<User>("/users/me", {
            method: "PATCH",
            body: JSON.stringify(data),
          });

          set({
            user: updatedUser,
            isLoading: false,
          });
        } catch (error) {
          set({
            isLoading: false,
            error: error instanceof Error ? error.message : "更新用户信息失败",
          });
          throw error;
        }
      },

      // Refresh token
      refreshToken: async () => {
        const { token } = get();
        if (!token) {
          throw new Error("No token to refresh");
        }

        try {
          const response = await fetch(`${USER_API}/auth/refresh`, {
            method: "POST",
            headers: {
              Authorization: `Bearer ${token}`,
            },
          });

          if (!response.ok) {
            throw new Error("Token refresh failed");
          }

          const data: LoginResponse = await response.json();
          const payload = decodeJWT(data.access_token);

          if (!payload) {
            throw new Error("Invalid refresh token response");
          }

          set({
            token: data.access_token,
            tokenExpiry: payload.exp,
          });
        } catch (error) {
          // If refresh fails, logout
          get().logout();
          throw error;
        }
      },
    }),
    {
      name: "auth-storage",
      storage: createJSONStorage(() => localStorage),
      // Only persist token and user - other state should be ephemeral
      partialize: (state) => ({
        token: state.token,
        user: state.user,
        tokenExpiry: state.tokenExpiry,
      }),
      // Rehydrate auth state on load
      onRehydrateStorage: () => (state) => {
        if (state?.token) {
          // Set isAuthenticated based on token presence
          state.isAuthenticated = !isTokenExpired(state.token);
          if (!state.isAuthenticated) {
            // Token expired, clear state
            state.token = null;
            state.user = null;
            state.tokenExpiry = null;
          }
        }
      },
    }
  )
);

// =============================================================================
// HOOKS & UTILITIES
// =============================================================================

/**
 * Custom hook for auth - provides a cleaner API for components
 */
export function useAuth() {
  const store = useAuthStore();

  return {
    // State
    user: store.user,
    token: store.token,
    isLoading: store.isLoading,
    isAuthenticated: store.isAuthenticated,
    error: store.error,

    // Actions
    login: store.login,
    register: store.register,
    logout: store.logout,
    checkAuth: store.checkAuth,
    clearError: store.clearError,
    updateUser: store.updateUser,

    // Computed
    isAdmin: store.user?.is_superuser ?? false,
  };
}

/**
 * Create an authenticated fetch function
 * Automatically includes auth headers and handles token refresh
 */
export function createAuthenticatedFetch() {
  return async <T>(
    url: string,
    options: RequestInit = {}
  ): Promise<T> => {
    const state = useAuthStore.getState();

    // Check if token needs refresh
    if (state.token && isTokenExpired(state.token)) {
      try {
        await state.refreshToken();
      } catch {
        state.logout();
        throw new Error("Session expired. Please login again.");
      }
    }

    const headers = {
      "Content-Type": "application/json",
      ...getAuthHeader(),
      ...options.headers,
    };

    const response = await fetch(url, {
      ...options,
      headers,
    });

    // Handle 401 Unauthorized
    if (response.status === 401) {
      state.logout();
      throw new Error("Session expired. Please login again.");
    }

    if (!response.ok) {
      const error = await response.json().catch(() => ({}));
      throw new Error(error.detail || `API Error: ${response.status}`);
    }

    const text = await response.text();
    if (!text) return {} as T;

    return JSON.parse(text);
  };
}

/**
 * Token refresh interval setup
 * Call this once in your app initialization to set up auto-refresh
 */
export function setupTokenRefresh(intervalMs: number = 5 * 60 * 1000) {
  if (typeof window === "undefined") return () => {};

  const intervalId = setInterval(async () => {
    const state = useAuthStore.getState();
    if (state.token && state.tokenExpiry) {
      const now = Math.floor(Date.now() / 1000);
      const timeUntilExpiry = state.tokenExpiry - now;

      // Refresh if less than 5 minutes until expiry
      if (timeUntilExpiry < 300 && timeUntilExpiry > 0) {
        try {
          await state.refreshToken();
        } catch {
          // Refresh failed, user will need to login again
          console.warn("Token refresh failed");
        }
      }
    }
  }, intervalMs);

  return () => clearInterval(intervalId);
}

// =============================================================================
// EXPORTS
// =============================================================================

export type { AuthState, User, RegisterData, LoginResponse, JWTPayload };
