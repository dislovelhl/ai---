/**
 * React Query hooks for Agent Service API
 *
 * Provides type-safe hooks for skills, workflows, executions, and chat operations
 * with automatic cache invalidation and optimistic updates.
 */

import {
  useQuery,
  useMutation,
  useQueryClient,
  UseQueryOptions,
  UseMutationOptions,
} from "@tanstack/react-query";
import * as api from "@/lib/api";
import type {
  Skill,
  AgentWorkflow,
  AgentExecution,
  WorkflowListResponse,
  WorkflowCreate,
  WorkflowUpdate,
  ChatResponse,
  ChatMessage,
  VersionHistoryEntry,
  VersionComparison,
} from "@/lib/types";

// =============================================================================
// QUERY KEYS
// =============================================================================

/**
 * Hierarchical query keys for cache management
 * Following TanStack Query best practices for key organization
 */
export const agentKeys = {
  // Root key for all agent-related queries
  all: ["agent"] as const,

  // Skills
  skills: () => [...agentKeys.all, "skills"] as const,
  skillsList: (params?: { tool_id?: string }) =>
    [...agentKeys.skills(), "list", params] as const,
  skill: (id: string) => [...agentKeys.skills(), "detail", id] as const,

  // Workflows
  workflows: () => [...agentKeys.all, "workflows"] as const,
  workflowsList: (params?: { page?: number; limit?: number }) =>
    [...agentKeys.workflows(), "list", params] as const,
  workflowsMy: () => [...agentKeys.workflows(), "my"] as const,
  workflowsPublic: () => [...agentKeys.workflows(), "public"] as const,
  workflow: (id: string) => [...agentKeys.workflows(), "detail", id] as const,
  workflowBySlug: (slug: string) =>
    [...agentKeys.workflows(), "slug", slug] as const,

  // Executions
  executions: () => [...agentKeys.all, "executions"] as const,
  executionsList: (
    workflowId: string,
    params?: { page?: number; limit?: number }
  ) => [...agentKeys.executions(), "workflow", workflowId, params] as const,
  executionsMy: (params?: { page?: number; limit?: number; status?: string }) =>
    [...agentKeys.executions(), "my", params] as const,
  execution: (id: string) =>
    [...agentKeys.executions(), "detail", id] as const,

  // Chat/Sessions
  sessions: () => [...agentKeys.all, "sessions"] as const,
  sessionsMy: () => [...agentKeys.sessions(), "my"] as const,
  sessionHistory: (sessionId: string) =>
    [...agentKeys.sessions(), "history", sessionId] as const,

  // Versions
  versions: () => [...agentKeys.all, "versions"] as const,
  workflowVersions: (workflowId: string) =>
    [...agentKeys.versions(), "workflow", workflowId] as const,
  versionComparison: (workflowId: string, v1: number, v2: number) =>
    [...agentKeys.versions(), "comparison", workflowId, v1, v2] as const,
};

// =============================================================================
// SKILL HOOKS
// =============================================================================

/**
 * Fetch all skills, optionally filtered by tool
 */
export function useSkills(
  params?: { tool_id?: string },
  options?: Omit<UseQueryOptions<Skill[], Error>, "queryKey" | "queryFn">
) {
  return useQuery({
    queryKey: agentKeys.skillsList(params),
    queryFn: () => api.getSkills(params),
    staleTime: 5 * 60 * 1000, // 5 minutes
    ...options,
  });
}

/**
 * Fetch a single skill by ID
 */
export function useSkill(
  id: string,
  options?: Omit<UseQueryOptions<Skill, Error>, "queryKey" | "queryFn">
) {
  return useQuery({
    queryKey: agentKeys.skill(id),
    queryFn: () => api.getSkillById(id),
    enabled: !!id,
    staleTime: 5 * 60 * 1000,
    ...options,
  });
}

// =============================================================================
// WORKFLOW HOOKS - QUERIES
// =============================================================================

/**
 * Fetch paginated list of workflows
 */
export function useWorkflows(
  params?: { page?: number; limit?: number },
  options?: Omit<
    UseQueryOptions<WorkflowListResponse, Error>,
    "queryKey" | "queryFn"
  >
) {
  return useQuery({
    queryKey: agentKeys.workflowsList(params),
    queryFn: () => api.getWorkflows(params),
    staleTime: 2 * 60 * 1000, // 2 minutes
    ...options,
  });
}

/**
 * Fetch workflows owned by the current user
 */
export function useMyWorkflows(
  options?: Omit<UseQueryOptions<AgentWorkflow[], Error>, "queryKey" | "queryFn">
) {
  return useQuery({
    queryKey: agentKeys.workflowsMy(),
    queryFn: () => api.getMyWorkflows(),
    staleTime: 1 * 60 * 1000, // 1 minute
    ...options,
  });
}

/**
 * Fetch public workflows (for discovery/templates)
 */
export function usePublicWorkflows(
  options?: Omit<UseQueryOptions<AgentWorkflow[], Error>, "queryKey" | "queryFn">
) {
  return useQuery({
    queryKey: agentKeys.workflowsPublic(),
    queryFn: () => api.getPublicWorkflows(),
    staleTime: 5 * 60 * 1000,
    ...options,
  });
}

/**
 * Fetch a single workflow by ID
 */
export function useWorkflow(
  id: string,
  options?: Omit<UseQueryOptions<AgentWorkflow, Error>, "queryKey" | "queryFn">
) {
  return useQuery({
    queryKey: agentKeys.workflow(id),
    queryFn: () => api.getWorkflowById(id),
    enabled: !!id,
    staleTime: 1 * 60 * 1000,
    ...options,
  });
}

/**
 * Fetch a single workflow by slug
 */
export function useWorkflowBySlug(
  slug: string,
  options?: Omit<UseQueryOptions<AgentWorkflow, Error>, "queryKey" | "queryFn">
) {
  return useQuery({
    queryKey: agentKeys.workflowBySlug(slug),
    queryFn: () => api.getWorkflowBySlug(slug),
    enabled: !!slug,
    staleTime: 1 * 60 * 1000,
    ...options,
  });
}

// =============================================================================
// WORKFLOW HOOKS - MUTATIONS
// =============================================================================

/**
 * Create a new workflow
 */
export function useCreateWorkflow(
  options?: Omit<
    UseMutationOptions<AgentWorkflow, Error, WorkflowCreate>,
    "mutationFn"
  >
) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: api.createWorkflow,
    onSuccess: (data, variables, context) => {
      // Invalidate workflow lists
      queryClient.invalidateQueries({ queryKey: agentKeys.workflows() });
      // Add the new workflow to cache
      queryClient.setQueryData(agentKeys.workflow(data.id), data);
      queryClient.setQueryData(agentKeys.workflowBySlug(data.slug), data);

      options?.onSuccess?.(data, variables, context);
    },
    ...options,
  });
}

/**
 * Update an existing workflow
 */
export function useUpdateWorkflow(
  options?: Omit<
    UseMutationOptions<
      AgentWorkflow,
      Error,
      { id: string; data: WorkflowUpdate }
    >,
    "mutationFn"
  >
) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }) => api.updateWorkflow(id, data),
    onSuccess: (data, variables, context) => {
      // Update the workflow in cache
      queryClient.setQueryData(agentKeys.workflow(data.id), data);
      queryClient.setQueryData(agentKeys.workflowBySlug(data.slug), data);
      // Invalidate lists to refresh
      queryClient.invalidateQueries({
        queryKey: agentKeys.workflowsList(),
      });
      queryClient.invalidateQueries({
        queryKey: agentKeys.workflowsMy(),
      });

      options?.onSuccess?.(data, variables, context);
    },
    ...options,
  });
}

/**
 * Delete a workflow
 */
export function useDeleteWorkflow(
  options?: Omit<UseMutationOptions<void, Error, string>, "mutationFn">
) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: api.deleteWorkflow,
    onSuccess: (data, workflowId, context) => {
      // Remove from cache
      queryClient.removeQueries({
        queryKey: agentKeys.workflow(workflowId),
      });
      // Invalidate lists
      queryClient.invalidateQueries({
        queryKey: agentKeys.workflows(),
      });

      options?.onSuccess?.(data, workflowId, context);
    },
    ...options,
  });
}

/**
 * Fork an existing workflow (creates a copy for the current user)
 */
export function useForkWorkflow(
  options?: Omit<UseMutationOptions<AgentWorkflow, Error, string>, "mutationFn">
) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: api.forkWorkflow,
    onSuccess: (data, originalId, context) => {
      // Add forked workflow to cache
      queryClient.setQueryData(agentKeys.workflow(data.id), data);
      // Invalidate user's workflows list
      queryClient.invalidateQueries({
        queryKey: agentKeys.workflowsMy(),
      });
      // Invalidate original workflow to update fork count
      queryClient.invalidateQueries({
        queryKey: agentKeys.workflow(originalId),
      });

      options?.onSuccess?.(data, originalId, context);
    },
    ...options,
  });
}

/**
 * Star/favorite a workflow
 */
export function useStarWorkflow(
  options?: Omit<UseMutationOptions<void, Error, string>, "mutationFn">
) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: api.starWorkflow,
    onMutate: async (workflowId) => {
      // Cancel any outgoing refetches
      await queryClient.cancelQueries({
        queryKey: agentKeys.workflow(workflowId),
      });

      // Snapshot the previous value
      const previousWorkflow = queryClient.getQueryData<AgentWorkflow>(
        agentKeys.workflow(workflowId)
      );

      // Optimistically update star count
      if (previousWorkflow) {
        queryClient.setQueryData(agentKeys.workflow(workflowId), {
          ...previousWorkflow,
          star_count: previousWorkflow.star_count + 1,
        });
      }

      return { previousWorkflow };
    },
    onError: (err, workflowId, context) => {
      // Rollback on error
      if (context?.previousWorkflow) {
        queryClient.setQueryData(
          agentKeys.workflow(workflowId),
          context.previousWorkflow
        );
      }
    },
    onSettled: (data, error, workflowId) => {
      // Refetch to ensure consistency
      queryClient.invalidateQueries({
        queryKey: agentKeys.workflow(workflowId),
      });
    },
    ...options,
  });
}

/**
 * Unstar/unfavorite a workflow
 */
export function useUnstarWorkflow(
  options?: Omit<UseMutationOptions<void, Error, string>, "mutationFn">
) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: api.unstarWorkflow,
    onMutate: async (workflowId) => {
      await queryClient.cancelQueries({
        queryKey: agentKeys.workflow(workflowId),
      });

      const previousWorkflow = queryClient.getQueryData<AgentWorkflow>(
        agentKeys.workflow(workflowId)
      );

      if (previousWorkflow) {
        queryClient.setQueryData(agentKeys.workflow(workflowId), {
          ...previousWorkflow,
          star_count: Math.max(0, previousWorkflow.star_count - 1),
        });
      }

      return { previousWorkflow };
    },
    onError: (err, workflowId, context) => {
      if (context?.previousWorkflow) {
        queryClient.setQueryData(
          agentKeys.workflow(workflowId),
          context.previousWorkflow
        );
      }
    },
    onSettled: (data, error, workflowId) => {
      queryClient.invalidateQueries({
        queryKey: agentKeys.workflow(workflowId),
      });
    },
    ...options,
  });
}

// =============================================================================
// EXECUTION HOOKS
// =============================================================================

/**
 * Run a workflow with the given input
 */
export function useRunWorkflow(
  options?: Omit<
    UseMutationOptions<
      AgentExecution,
      Error,
      { workflowId: string; input: Record<string, unknown> }
    >,
    "mutationFn"
  >
) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ workflowId, input }) => api.runWorkflow(workflowId, input),
    onSuccess: (data, variables, context) => {
      // Add execution to cache
      queryClient.setQueryData(agentKeys.execution(data.id), data);
      // Invalidate execution lists
      queryClient.invalidateQueries({
        queryKey: agentKeys.executionsList(variables.workflowId),
      });
      queryClient.invalidateQueries({
        queryKey: agentKeys.executionsMy(),
      });
      // Invalidate workflow to update run_count
      queryClient.invalidateQueries({
        queryKey: agentKeys.workflow(variables.workflowId),
      });

      options?.onSuccess?.(data, variables, context);
    },
    ...options,
  });
}

/**
 * Fetch execution details by ID
 */
export function useExecution(
  id: string,
  options?: Omit<
    UseQueryOptions<AgentExecution, Error>,
    "queryKey" | "queryFn"
  >
) {
  return useQuery({
    queryKey: agentKeys.execution(id),
    queryFn: () => api.getExecution(id),
    enabled: !!id,
    // For running executions, refetch frequently
    refetchInterval: (query) => {
      const data = query.state.data;
      if (data?.status === "running" || data?.status === "pending") {
        return 2000; // 2 seconds
      }
      return false;
    },
    ...options,
  });
}

/**
 * Fetch all executions for a workflow
 */
export function useExecutions(
  workflowId: string,
  params?: { page?: number; limit?: number },
  options?: Omit<
    UseQueryOptions<AgentExecution[], Error>,
    "queryKey" | "queryFn"
  >
) {
  return useQuery({
    queryKey: agentKeys.executionsList(workflowId, params),
    queryFn: () => api.getExecutions(workflowId, params),
    enabled: !!workflowId,
    staleTime: 30 * 1000, // 30 seconds
    ...options,
  });
}

/**
 * Cancel a running execution
 */
export function useCancelExecution(
  options?: Omit<UseMutationOptions<void, Error, string>, "mutationFn">
) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: api.cancelExecution,
    onSuccess: (data, executionId, context) => {
      // Update execution status in cache
      queryClient.setQueryData<AgentExecution | undefined>(
        agentKeys.execution(executionId),
        (old) =>
          old
            ? {
                ...old,
                status: "cancelled",
              }
            : undefined
      );
      // Invalidate to refetch
      queryClient.invalidateQueries({
        queryKey: agentKeys.execution(executionId),
      });
      queryClient.invalidateQueries({
        queryKey: agentKeys.executionsMy(),
      });

      options?.onSuccess?.(data, executionId, context);
    },
    ...options,
  });
}

/**
 * Fetch executions for the current user
 */
export function useMyExecutions(
  params?: { page?: number; limit?: number; status?: string },
  options?: Omit<
    UseQueryOptions<AgentExecution[], Error>,
    "queryKey" | "queryFn"
  >
) {
  return useQuery({
    queryKey: agentKeys.executionsMy(params),
    queryFn: () => api.getMyExecutions(params),
    staleTime: 30 * 1000,
    ...options,
  });
}

// =============================================================================
// CHAT HOOKS
// =============================================================================

/** Session info type from API */
export interface SessionInfo {
  session_id: string;
  workflow_id: string;
  created_at: string;
  last_message_at: string;
  message_count: number;
}

/**
 * Send a chat message to an agent workflow
 */
export function useChatWithAgent(
  options?: Omit<
    UseMutationOptions<
      ChatResponse,
      Error,
      { workflowId: string; message: string; sessionId?: string }
    >,
    "mutationFn"
  >
) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ workflowId, message, sessionId }) =>
      api.chatWithAgent(workflowId, message, sessionId),
    onSuccess: (data, variables, context) => {
      // Invalidate session history to include new message
      queryClient.invalidateQueries({
        queryKey: agentKeys.sessionHistory(data.session_id),
      });
      // Invalidate user's sessions list
      queryClient.invalidateQueries({
        queryKey: agentKeys.sessionsMy(),
      });

      options?.onSuccess?.(data, variables, context);
    },
    ...options,
  });
}

/**
 * Get chat session history
 */
export function useSessionHistory(
  sessionId: string,
  options?: Omit<UseQueryOptions<ChatMessage[], Error>, "queryKey" | "queryFn">
) {
  return useQuery({
    queryKey: agentKeys.sessionHistory(sessionId),
    queryFn: () => api.getSessionHistory(sessionId),
    enabled: !!sessionId,
    staleTime: 30 * 1000,
    ...options,
  });
}

/**
 * Clear chat session history
 */
export function useClearSession(
  options?: Omit<UseMutationOptions<void, Error, string>, "mutationFn">
) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: api.clearSessionHistory,
    onSuccess: (data, sessionId, context) => {
      // Remove session history from cache
      queryClient.removeQueries({
        queryKey: agentKeys.sessionHistory(sessionId),
      });
      // Invalidate sessions list
      queryClient.invalidateQueries({
        queryKey: agentKeys.sessionsMy(),
      });

      options?.onSuccess?.(data, sessionId, context);
    },
    ...options,
  });
}

/**
 * Get active chat sessions for the current user
 */
export function useMySessions(
  options?: Omit<UseQueryOptions<SessionInfo[], Error>, "queryKey" | "queryFn">
) {
  return useQuery({
    queryKey: agentKeys.sessionsMy(),
    queryFn: () => api.getMySessions(),
    staleTime: 1 * 60 * 1000, // 1 minute
    ...options,
  });
}

// =============================================================================
// VERSION HISTORY HOOKS
// =============================================================================

/**
 * Fetch version history for a workflow
 */
export function useWorkflowVersions(
  workflowId: string,
  options?: Omit<
    UseQueryOptions<
      { workflow_id: string; current_version: number; history: VersionHistoryEntry[] },
      Error
    >,
    "queryKey" | "queryFn"
  >
) {
  return useQuery({
    queryKey: agentKeys.workflowVersions(workflowId),
    queryFn: () => api.getWorkflowVersions(workflowId),
    enabled: !!workflowId,
    staleTime: 1 * 60 * 1000, // 1 minute
    ...options,
  });
}

/**
 * Compare two versions of a workflow
 */
export function useCompareVersions(
  workflowId: string,
  v1: number,
  v2: number,
  options?: Omit<
    UseQueryOptions<VersionComparison, Error>,
    "queryKey" | "queryFn"
  >
) {
  return useQuery({
    queryKey: agentKeys.versionComparison(workflowId, v1, v2),
    queryFn: () => api.compareWorkflowVersions(workflowId, v1, v2),
    enabled: !!workflowId && v1 !== undefined && v2 !== undefined,
    staleTime: 5 * 60 * 1000, // 5 minutes - comparisons don't change
    ...options,
  });
}

/**
 * Revert a workflow to a previous version
 * Creates a new version entry documenting the revert operation
 */
export function useRevertVersion(
  options?: Omit<
    UseMutationOptions<
      AgentWorkflow,
      Error,
      { workflowId: string; targetVersion: number }
    >,
    "mutationFn"
  >
) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ workflowId, targetVersion }) =>
      api.revertWorkflowVersion(workflowId, targetVersion),
    onSuccess: (data, variables, context) => {
      // Update the workflow in cache with new version
      queryClient.setQueryData(agentKeys.workflow(data.id), data);
      queryClient.setQueryData(agentKeys.workflowBySlug(data.slug), data);

      // Invalidate version history to show the new revert version
      queryClient.invalidateQueries({
        queryKey: agentKeys.workflowVersions(variables.workflowId),
      });

      // Invalidate workflow lists to refresh version numbers
      queryClient.invalidateQueries({
        queryKey: agentKeys.workflowsList(),
      });
      queryClient.invalidateQueries({
        queryKey: agentKeys.workflowsMy(),
      });

      options?.onSuccess?.(data, variables, context);
    },
    ...options,
  });
}

// =============================================================================
// UTILITY HOOKS
// =============================================================================

/**
 * Prefetch a workflow by ID (useful for hover states or navigation)
 */
export function usePrefetchWorkflow() {
  const queryClient = useQueryClient();

  return (id: string) => {
    queryClient.prefetchQuery({
      queryKey: agentKeys.workflow(id),
      queryFn: () => api.getWorkflowById(id),
      staleTime: 1 * 60 * 1000,
    });
  };
}

/**
 * Prefetch a workflow by slug
 */
export function usePrefetchWorkflowBySlug() {
  const queryClient = useQueryClient();

  return (slug: string) => {
    queryClient.prefetchQuery({
      queryKey: agentKeys.workflowBySlug(slug),
      queryFn: () => api.getWorkflowBySlug(slug),
      staleTime: 1 * 60 * 1000,
    });
  };
}

/**
 * Invalidate all agent-related queries (useful after logout)
 */
export function useInvalidateAgentQueries() {
  const queryClient = useQueryClient();

  return () => {
    queryClient.invalidateQueries({ queryKey: agentKeys.all });
  };
}

/**
 * Reset all agent-related queries (removes from cache)
 */
export function useResetAgentQueries() {
  const queryClient = useQueryClient();

  return () => {
    queryClient.resetQueries({ queryKey: agentKeys.all });
  };
}
