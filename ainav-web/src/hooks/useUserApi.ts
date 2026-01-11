/**
 * React Query hooks for User Service API
 *
 * Provides type-safe hooks for user profile and usage statistics
 * with automatic cache management.
 */

import {
  useQuery,
  UseQueryOptions,
} from "@tanstack/react-query";
import * as api from "@/lib/api";
import type { UsageStats } from "@/lib/types";

// =============================================================================
// QUERY KEYS
// =============================================================================

/**
 * Hierarchical query keys for cache management
 * Following TanStack Query best practices for key organization
 */
export const userKeys = {
  // Root key for all user-related queries
  all: ["user"] as const,

  // Usage stats
  usage: () => [...userKeys.all, "usage"] as const,
};

// =============================================================================
// USAGE STATS HOOKS
// =============================================================================

/**
 * Fetch current user's execution usage statistics
 * Returns quota information, used count, remaining count, and reset time
 */
export function useUserUsage(
  options?: Omit<UseQueryOptions<UsageStats, Error>, "queryKey" | "queryFn">
) {
  return useQuery({
    queryKey: userKeys.usage(),
    queryFn: () => api.getUserUsage(),
    staleTime: 30 * 1000, // 30 seconds - refresh frequently for accurate quota display
    refetchOnWindowFocus: true, // Refetch when user returns to tab
    ...options,
  });
}
