'use client';

import { useRequireAuth } from '@/hooks/useRequireAuth';

interface ProtectedRouteProps {
  children: React.ReactNode;
  redirectTo?: string;
  loadingComponent?: React.ReactNode;
}

export function ProtectedRoute({
  children,
  redirectTo = '/login',
  loadingComponent,
}: ProtectedRouteProps) {
  const { isLoading, isAuthenticated } = useRequireAuth(redirectTo);

  if (isLoading) {
    return (
      loadingComponent ?? (
        <div className="flex items-center justify-center min-h-screen">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
        </div>
      )
    );
  }

  if (!isAuthenticated) {
    return null; // Will redirect via useRequireAuth
  }

  return <>{children}</>;
}
