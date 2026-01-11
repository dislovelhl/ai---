'use client';

import { useEffect } from 'react';
import { useAuthStore, setupTokenRefresh } from '@/stores/authStore';

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const { checkAuth } = useAuthStore();

  useEffect(() => {
    // Check authentication status on mount
    checkAuth();

    // Setup automatic token refresh
    const cleanup = setupTokenRefresh();

    return () => {
      cleanup();
    };
  }, [checkAuth]);

  // Optionally show loading state during initial auth check
  // For now, we render children immediately to avoid flash
  return <>{children}</>;
}
