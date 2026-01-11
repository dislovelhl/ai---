# C4 Code Level: Frontend Custom React Hooks

## Overview

- **Name:** Frontend Custom React Hooks
- **Description:** Reusable React hooks providing authentication guards, API interactions with agent workflows, and TanStack Query cache management for the AI Navigation platform frontend
- **Location:** `/home/dislove/document/ai 导航/ainav-web/src/hooks/`
- **Language:** TypeScript
- **Purpose:** Centralize React hook logic for authentication protection, agent service API integration, and efficient data fetching/caching patterns across the frontend application
- **Framework:** React 19 with TanStack Query (React Query) and Zustand for state management

---

## Code Elements

### Authentication Guard Hook

#### `useRequireAuth(redirectTo?: string): { user: User | null; isLoading: boolean; isAuthenticated: boolean }`

- **Description:** Guard hook that protects routes by requiring authentication. Automatically redirects unauthenticated users to login page.
- **Location:** `/home/dislove/document/ai 导航/ainav-web/src/hooks/useRequireAuth.ts:7-18`
- **Parameters:**
  - `redirectTo` (string, optional): URL path to redirect unauthenticated users. Default: `/login`
- **Return Type:**
  ```typescript
  {
    user: User | null;              // Current authenticated user or null
    isLoading: boolean;             // Loading state during auth check
    isAuthenticated: boolean;       // Auth status flag
  }
  ```
- **Behavior:**
  - Uses `useEffect` to monitor authentication state changes
  - Triggers redirect when `isLoading` transitions to `false` AND user is not authenticated
  - Returns current auth state for component rendering
- **Dependencies:**
  - React: `useEffect` hook
  - Next.js: `useRouter` from `next/navigation` (client-side navigation)
  - Zustand Store: `useAuthStore()` (reads user, isLoading, isAuthenticated)

---

### Agent Service API Hooks

#### Query Key Hierarchy

**Object:** `agentKeys` - Hierarchical query key factory for TanStack Query cache management

- **Location:** `/home/dislove/document/ai 导航/ainav-web/src/hooks/useAgentApi.ts:35-71`
- **Structure:**
  ```typescript
  agentKeys.all                           // Root: ["agent"]
  agentKeys.skills()                      // Skills collection
  agentKeys.skillsList(params?)           // Skills list with optional tool_id filter
  agentKeys.skill(id: string)             // Single skill by ID
  agentKeys.workflows()                   // Workflows collection
  agentKeys.workflowsList(params?)        // Paginated workflows list
  agentKeys.workflowsMy()                 // User's workflows
  agentKeys.workflowsPublic()             // Public/template workflows
  agentKeys.workflow(id: string)          // Single workflow by ID
  agentKeys.workflowBySlug(slug: string)  // Single workflow by slug
  agentKeys.executions()                  // Executions collection
  agentKeys.executionsList(workflowId, params?) // Workflow executions
  agentKeys.executionsMy(params?)         // User's executions
  agentKeys.execution(id: string)         // Single execution by ID
  agentKeys.sessions()                    // Chat sessions collection
  agentKeys.sessionsMy()                  // User's sessions
  agentKeys.sessionHistory(sessionId)     // Session chat history
  ```
- **Purpose:** Provides consistent, hierarchical cache key generation following TanStack Query best practices

---

#### Skill Query Hooks

**`useSkills(params?, options?): UseQueryResult<Skill[], Error>`**

- **Description:** Fetch all skills, optionally filtered by tool
- **Location:** `/home/dislove/document/ai 导航/ainav-web/src/hooks/useAgentApi.ts:80-90`
- **Parameters:**
  - `params` (optional): `{ tool_id?: string }`
  - `options` (optional): TanStack Query UseQueryOptions (excluding queryKey, queryFn)
- **Cache Settings:**
  - Stale time: 5 minutes
  - Query key: `agentKeys.skillsList(params)`
- **API Endpoint:** `GET /skills` (Agent Service)
- **Dependencies:** `useQuery`, `@/lib/api.getSkills()`

**`useSkill(id: string, options?): UseQueryResult<Skill, Error>`**

- **Description:** Fetch a single skill by ID
- **Location:** `/home/dislove/document/ai 导航/ainav-web/src/hooks/useAgentApi.ts:95-106`
- **Parameters:**
  - `id` (string): Skill ID
  - `options` (optional): TanStack Query options
- **Cache Settings:**
  - Stale time: 5 minutes
  - Enabled: Only when `id` is truthy
  - Query key: `agentKeys.skill(id)`
- **API Endpoint:** `GET /skills/{id}`
- **Dependencies:** `useQuery`, `@/lib/api.getSkillById()`

---

#### Workflow Query Hooks

**`useWorkflows(params?, options?): UseQueryResult<WorkflowListResponse, Error>`**

- **Description:** Fetch paginated list of workflows
- **Location:** `/home/dislove/document/ai 导航/ainav-web/src/hooks/useAgentApi.ts:115-128`
- **Parameters:**
  - `params` (optional): `{ page?: number; limit?: number }`
  - `options` (optional): TanStack Query options
- **Cache Settings:**
  - Stale time: 2 minutes
  - Query key: `agentKeys.workflowsList(params)`
- **API Endpoint:** `GET /workflows`

**`useMyWorkflows(options?): UseQueryResult<AgentWorkflow[], Error>`**

- **Description:** Fetch workflows owned by the current user
- **Location:** `/home/dislove/document/ai 导航/ainav-web/src/hooks/useAgentApi.ts:133-142`
- **Cache Settings:**
  - Stale time: 1 minute
  - Query key: `agentKeys.workflowsMy()`
- **API Endpoint:** `GET /workflows/me` (requires authentication)

**`usePublicWorkflows(options?): UseQueryResult<AgentWorkflow[], Error>`**

- **Description:** Fetch public workflows for discovery and use as templates
- **Location:** `/home/dislove/document/ai 导航/ainav-web/src/hooks/useAgentApi.ts:147-156`
- **Cache Settings:**
  - Stale time: 5 minutes
  - Query key: `agentKeys.workflowsPublic()`
- **API Endpoint:** `GET /workflows/public`

**`useWorkflow(id: string, options?): UseQueryResult<AgentWorkflow, Error>`**

- **Description:** Fetch a single workflow by ID
- **Location:** `/home/dislove/document/ai 导航/ainav-web/src/hooks/useAgentApi.ts:161-172`
- **Parameters:**
  - `id` (string): Workflow ID
- **Cache Settings:**
  - Stale time: 1 minute
  - Enabled: Only when `id` is truthy
  - Query key: `agentKeys.workflow(id)`
- **API Endpoint:** `GET /workflows/{id}`

**`useWorkflowBySlug(slug: string, options?): UseQueryResult<AgentWorkflow, Error>`**

- **Description:** Fetch a workflow by its URL slug
- **Location:** `/home/dislove/document/ai 导航/ainav-web/src/hooks/useAgentApi.ts:177-188`
- **Parameters:**
  - `slug` (string): Workflow slug identifier
- **Cache Settings:**
  - Stale time: 1 minute
  - Enabled: Only when `slug` is truthy
  - Query key: `agentKeys.workflowBySlug(slug)`
- **API Endpoint:** `GET /workflows/slug/{slug}`

---

#### Workflow Mutation Hooks

**`useCreateWorkflow(options?): UseMutationResult<AgentWorkflow, Error, WorkflowCreate>`**

- **Description:** Create a new workflow
- **Location:** `/home/dislove/document/ai 导航/ainav-web/src/hooks/useAgentApi.ts:197-218`
- **Parameters:**
  - `options` (optional): UseMutationOptions (excluding mutationFn)
- **API Endpoint:** `POST /workflows` (requires authentication)
- **On Success Actions:**
  - Invalidates `agentKeys.workflows()` to refresh lists
  - Caches new workflow by ID: `setQueryData(agentKeys.workflow(data.id), data)`
  - Caches new workflow by slug: `setQueryData(agentKeys.workflowBySlug(data.slug), data)`
- **Dependencies:** `useMutation`, `useQueryClient`, `@/lib/api.createWorkflow()`

**`useUpdateWorkflow(options?): UseMutationResult<AgentWorkflow, Error, { id: string; data: WorkflowUpdate }>`**

- **Description:** Update an existing workflow
- **Location:** `/home/dislove/document/ai 导航/ainav-web/src/hooks/useAgentApi.ts:223-253`
- **API Endpoint:** `PUT /workflows/{id}` (requires authentication)
- **On Success Actions:**
  - Updates workflow in cache by ID and slug
  - Invalidates workflow list caches to ensure consistency
  - Triggers refetch of `workflowsList()` and `workflowsMy()`

**`useDeleteWorkflow(options?): UseMutationResult<void, Error, string>`**

- **Description:** Delete a workflow by ID
- **Location:** `/home/dislove/document/ai 导航/ainav-web/src/hooks/useAgentApi.ts:258-279`
- **API Endpoint:** `DELETE /workflows/{id}` (requires authentication)
- **On Success Actions:**
  - Removes workflow from cache
  - Invalidates all workflow lists to sync deletion

**`useForkWorkflow(options?): UseMutationResult<AgentWorkflow, Error, string>`**

- **Description:** Create a copy of an existing workflow for the current user
- **Location:** `/home/dislove/document/ai 导航/ainav-web/src/hooks/useAgentApi.ts:284-307`
- **Parameters:**
  - Input: `string` (original workflow ID)
  - Returns: `AgentWorkflow` (newly forked workflow)
- **API Endpoint:** `POST /workflows/{id}/fork` (requires authentication)
- **On Success Actions:**
  - Caches forked workflow
  - Invalidates user's workflows to show the fork
  - Invalidates original workflow to update fork count

**`useStarWorkflow(options?): UseMutationResult<void, Error, string>`**

- **Description:** Mark a workflow as favorite/starred
- **Location:** `/home/dislove/document/ai 导航/ainav-web/src/hooks/useAgentApi.ts:312-357`
- **API Endpoint:** `POST /workflows/{id}/star` (requires authentication)
- **Cache Strategy:** Optimistic Update
  - On mutation: Cancels pending queries and snapshots previous state
  - Updates cache immediately with incremented `star_count`
  - On error: Rolls back to previous state
  - On settle: Invalidates workflow to ensure consistency

**`useUnstarWorkflow(options?): UseMutationResult<void, Error, string>`**

- **Description:** Remove workflow from favorites
- **Location:** `/home/dislove/document/ai 导航/ainav-web/src/hooks/useAgentApi.ts:362-402`
- **API Endpoint:** `DELETE /workflows/{id}/star` (requires authentication)
- **Cache Strategy:** Optimistic Update (decrements star_count)

---

#### Execution Query Hooks

**`useExecution(id: string, options?): UseQueryResult<AgentExecution, Error>`**

- **Description:** Fetch execution details by ID with adaptive polling
- **Location:** `/home/dislove/document/ai 导航/ainav-web/src/hooks/useAgentApi.ts:449-470`
- **Parameters:**
  - `id` (string): Execution ID
- **Cache Settings:**
  - Enabled: Only when `id` is truthy
  - Polling Strategy:
    - If status is "running" or "pending": Refetch every 2 seconds
    - Otherwise: No polling (refetchInterval = false)
- **API Endpoint:** `GET /executions/{id}` (requires authentication)
- **Purpose:** Real-time execution status tracking during workflow runs

**`useExecutions(workflowId: string, params?, options?): UseQueryResult<AgentExecution[], Error>`**

- **Description:** Fetch all executions for a specific workflow
- **Location:** `/home/dislove/document/ai 导航/ainav-web/src/hooks/useAgentApi.ts:475-490`
- **Parameters:**
  - `workflowId` (string): Workflow ID
  - `params` (optional): `{ page?: number; limit?: number }`
- **Cache Settings:**
  - Stale time: 30 seconds
  - Enabled: Only when `workflowId` is truthy
  - Query key: `agentKeys.executionsList(workflowId, params)`
- **API Endpoint:** `GET /executions/workflows/{workflowId}`

**`useMyExecutions(params?, options?): UseQueryResult<AgentExecution[], Error>`**

- **Description:** Fetch all executions for the current user
- **Location:** `/home/dislove/document/ai 导航/ainav-web/src/hooks/useAgentApi.ts:531-544`
- **Parameters:**
  - `params` (optional): `{ page?: number; limit?: number; status?: string }`
- **Cache Settings:**
  - Stale time: 30 seconds
  - Query key: `agentKeys.executionsMy(params)`
- **API Endpoint:** `GET /executions/me` (requires authentication)

---

#### Execution Mutation Hooks

**`useRunWorkflow(options?): UseMutationResult<AgentExecution, Error, { workflowId: string; input: Record<string, unknown> }>`**

- **Description:** Execute/run a workflow with input data
- **Location:** `/home/dislove/document/ai 导航/ainav-web/src/hooks/useAgentApi.ts:411-444`
- **Parameters:**
  - Input: `{ workflowId: string; input: Record<string, unknown> }`
  - Returns: `AgentExecution` (execution record with status and logs)
- **API Endpoint:** `POST /executions/workflows/{workflowId}/run` (requires authentication)
- **On Success Actions:**
  - Caches new execution
  - Invalidates execution lists for the workflow
  - Invalidates user's executions list
  - Invalidates workflow to update `run_count`

**`useCancelExecution(options?): UseMutationResult<void, Error, string>`**

- **Description:** Cancel a running workflow execution
- **Location:** `/home/dislove/document/ai 导航/ainav-web/src/hooks/useAgentApi.ts:495-526`
- **Parameters:**
  - Input: `string` (execution ID)
- **API Endpoint:** `POST /executions/{id}/cancel` (requires authentication)
- **On Success Actions:**
  - Updates execution status in cache to "cancelled"
  - Invalidates execution and user's executions to sync cancellation

---

#### Chat Query Hooks

**`useSessionHistory(sessionId: string, options?): UseQueryResult<ChatMessage[], Error>`**

- **Description:** Fetch chat message history for a session
- **Location:** `/home/dislove/document/ai 导航/ainav-web/src/hooks/useAgentApi.ts:596-607`
- **Parameters:**
  - `sessionId` (string): Chat session ID
- **Cache Settings:**
  - Stale time: 30 seconds
  - Enabled: Only when `sessionId` is truthy
  - Query key: `agentKeys.sessionHistory(sessionId)`
- **API Endpoint:** `GET /agents/sessions/{sessionId}/history` (requires authentication)

**`useMySessions(options?): UseQueryResult<SessionInfo[], Error>`**

- **Description:** Fetch all active chat sessions for the current user
- **Location:** `/home/dislove/document/ai 导航/ainav-web/src/hooks/useAgentApi.ts:638-647`
- **Cache Settings:**
  - Stale time: 1 minute
  - Query key: `agentKeys.sessionsMy()`
- **API Endpoint:** `GET /agents/sessions/me` (requires authentication)
- **Returns:** Array of `SessionInfo` with session metadata

**Type:** `SessionInfo`
- **Location:** `/home/dislove/document/ai 导航/ainav-web/src/hooks/useAgentApi.ts:551-557`
- **Properties:**
  ```typescript
  interface SessionInfo {
    session_id: string;
    workflow_id: string;
    created_at: string;
    last_message_at: string;
    message_count: number;
  }
  ```

---

#### Chat Mutation Hooks

**`useChatWithAgent(options?): UseMutationResult<ChatResponse, Error, { workflowId: string; message: string; sessionId?: string }>`**

- **Description:** Send a chat message to an agent workflow
- **Location:** `/home/dislove/document/ai 导航/ainav-web/src/hooks/useAgentApi.ts:562-591`
- **Parameters:**
  - `workflowId` (string): Workflow ID to chat with
  - `message` (string): User message content
  - `sessionId` (string, optional): Existing session ID to continue conversation
- **API Endpoint:** `POST /agents/{workflowId}/chat` (requires authentication)
- **On Success Actions:**
  - Invalidates session history to show new message
  - Invalidates user's sessions list to update metadata
- **Returns:** `ChatResponse` containing session_id, message, workflow_id, tokens_used

**`useClearSession(options?): UseMutationResult<void, Error, string>`**

- **Description:** Clear all chat history for a session
- **Location:** `/home/dislove/document/ai 导航/ainav-web/src/hooks/useAgentApi.ts:612-633`
- **Parameters:**
  - Input: `string` (session ID)
- **API Endpoint:** `DELETE /agents/sessions/{sessionId}` (requires authentication)
- **On Success Actions:**
  - Removes session history from cache
  - Invalidates user's sessions list

---

#### Utility/Prefetch Hooks

**`usePrefetchWorkflow(): (id: string) => void`**

- **Description:** Prefetch a workflow by ID to improve perceived performance on hover/navigation
- **Location:** `/home/dislove/document/ai 导航/ainav-web/src/hooks/useAgentApi.ts:656-666`
- **Returns:** Function that accepts workflow ID
- **Cache Settings:**
  - Stale time: 1 minute
  - Typical usage: Call on link hover before navigation

**`usePrefetchWorkflowBySlug(): (slug: string) => void`**

- **Description:** Prefetch a workflow by slug
- **Location:** `/home/dislove/document/ai 导航/ainav-web/src/hooks/useAgentApi.ts:671-681`
- **Returns:** Function that accepts workflow slug

**`useInvalidateAgentQueries(): () => void`**

- **Description:** Invalidate all agent-related queries to force refetch
- **Location:** `/home/dislove/document/ai 导航/ainav-web/src/hooks/useAgentApi.ts:686-692`
- **Purpose:** Typically used on logout or when auth state changes
- **Effect:** Triggers refetch of all queries under `agentKeys.all`

**`useResetAgentQueries(): () => void`**

- **Description:** Reset and remove all agent-related queries from cache
- **Location:** `/home/dislove/document/ai 导航/ainav-web/src/hooks/useAgentApi.ts:697-703`
- **Purpose:** Complete cleanup of agent data, useful for logout
- **Effect:** Removes all agent data from cache without refetching

---

### Module Exports

**Location:** `/home/dislove/document/ai 导航/ainav-web/src/hooks/index.ts:1-2`

```typescript
export { useRequireAuth } from './useRequireAuth';
// Note: useAgentApi hooks are imported directly from './useAgentApi'
```

---

## Dependencies

### Internal Dependencies

**React Hooks:**
- `useState` - State management (used in auth store)
- `useEffect` - Side effects (useRequireAuth)
- `useRouter` - Navigation (Next.js client-side routing)
- `useQuery` - Data fetching with caching (TanStack Query)
- `useMutation` - Mutation handling (TanStack Query)
- `useQueryClient` - Cache management (TanStack Query)

**State Management:**
- `useAuthStore()` from `@/stores/authStore` - Authentication state (Zustand)
  - Provides: `user`, `isLoading`, `isAuthenticated`
  - Actions: `login()`, `logout()`, `checkAuth()`, `refreshToken()`

**API Client:**
- `@/lib/api` - API function exports for all endpoints
  - Skills: `getSkills()`, `getSkillById()`
  - Workflows: `getWorkflows()`, `getMyWorkflows()`, `getPublicWorkflows()`, `getWorkflowById()`, `getWorkflowBySlug()`, `createWorkflow()`, `updateWorkflow()`, `deleteWorkflow()`, `forkWorkflow()`, `starWorkflow()`, `unstarWorkflow()`
  - Executions: `runWorkflow()`, `getExecution()`, `getExecutions()`, `getMyExecutions()`, `cancelExecution()`
  - Chat: `chatWithAgent()`, `getSessionHistory()`, `clearSessionHistory()`, `getMySessions()`

**Type Definitions:**
- `@/lib/types` - TypeScript interfaces
  - Agent types: `Skill`, `AgentWorkflow`, `AgentExecution`, `WorkflowListResponse`, `WorkflowCreate`, `WorkflowUpdate`, `ChatResponse`, `ChatMessage`

### External Dependencies

**NPM Packages:**
- `@tanstack/react-query` - Server state management and data fetching
  - Used: `useQuery`, `useMutation`, `useQueryClient`, `UseQueryOptions`, `UseMutationOptions`
  - Version: Latest (React Query v5+)
- `next/navigation` - Next.js App Router navigation
  - Used: `useRouter()` hook
- `zustand` - Client state management (in authStore)
- `react` - Core React library (hooks)

---

## Relationships

```mermaid
---
title: Code Diagram for Frontend Custom Hooks
---
classDiagram
    namespace "Authentication" {
        class useRequireAuth {
            <<hook>>
            -redirectTo: string
            +user: User
            +isLoading: boolean
            +isAuthenticated: boolean
            -useEffect
            -useRouter
        }
    }

    namespace "Cache Keys" {
        class agentKeys {
            <<factory>>
            +all: const
            +skills(): key
            +skillsList(params): key
            +skill(id): key
            +workflows(): key
            +workflowsList(params): key
            +workflowsMy(): key
            +workflowsPublic(): key
            +workflow(id): key
            +workflowBySlug(slug): key
            +executions(): key
            +executionsList(workflowId, params): key
            +executionsMy(params): key
            +execution(id): key
            +sessions(): key
            +sessionsMy(): key
            +sessionHistory(sessionId): key
        }
    }

    namespace "Skill Queries" {
        class useSkills {
            <<hook>>
            +params?: {tool_id}
            +returns: UseQueryResult~Skill[], Error~
        }
        class useSkill {
            <<hook>>
            +id: string
            +returns: UseQueryResult~Skill, Error~
        }
    }

    namespace "Workflow Queries" {
        class useWorkflows {
            <<hook>>
            +params?: {page, limit}
            +returns: UseQueryResult~WorkflowListResponse, Error~
        }
        class useMyWorkflows {
            <<hook>>
            +returns: UseQueryResult~AgentWorkflow[], Error~
        }
        class usePublicWorkflows {
            <<hook>>
            +returns: UseQueryResult~AgentWorkflow[], Error~
        }
        class useWorkflow {
            <<hook>>
            +id: string
            +returns: UseQueryResult~AgentWorkflow, Error~
        }
        class useWorkflowBySlug {
            <<hook>>
            +slug: string
            +returns: UseQueryResult~AgentWorkflow, Error~
        }
    }

    namespace "Workflow Mutations" {
        class useCreateWorkflow {
            <<hook>>
            +returns: UseMutationResult~AgentWorkflow, Error, WorkflowCreate~
            +onSuccess: invalidates + sets cache
        }
        class useUpdateWorkflow {
            <<hook>>
            +returns: UseMutationResult~AgentWorkflow, Error, {id, data}~
            +onSuccess: updates cache + invalidates lists
        }
        class useDeleteWorkflow {
            <<hook>>
            +returns: UseMutationResult~void, Error, string~
            +onSuccess: removes from cache
        }
        class useForkWorkflow {
            <<hook>>
            +returns: UseMutationResult~AgentWorkflow, Error, string~
            +onSuccess: caches fork + updates counts
        }
        class useStarWorkflow {
            <<hook>>
            +returns: UseMutationResult~void, Error, string~
            +onMutate: optimistic update
            +onError: rollback
        }
        class useUnstarWorkflow {
            <<hook>>
            +returns: UseMutationResult~void, Error, string~
            +onMutate: optimistic decrement
            +onError: rollback
        }
    }

    namespace "Execution Queries" {
        class useExecution {
            <<hook>>
            +id: string
            +returns: UseQueryResult~AgentExecution, Error~
            +refetchInterval: adaptive polling
        }
        class useExecutions {
            <<hook>>
            +workflowId: string
            +returns: UseQueryResult~AgentExecution[], Error~
        }
        class useMyExecutions {
            <<hook>>
            +returns: UseQueryResult~AgentExecution[], Error~
        }
    }

    namespace "Execution Mutations" {
        class useRunWorkflow {
            <<hook>>
            +returns: UseMutationResult~AgentExecution, Error, {workflowId, input}~
            +onSuccess: caches + invalidates
        }
        class useCancelExecution {
            <<hook>>
            +returns: UseMutationResult~void, Error, string~
            +onSuccess: updates status in cache
        }
    }

    namespace "Chat Queries" {
        class useSessionHistory {
            <<hook>>
            +sessionId: string
            +returns: UseQueryResult~ChatMessage[], Error~
        }
        class useMySessions {
            <<hook>>
            +returns: UseQueryResult~SessionInfo[], Error~
        }
    }

    namespace "Chat Mutations" {
        class useChatWithAgent {
            <<hook>>
            +returns: UseMutationResult~ChatResponse, Error, {workflowId, message, sessionId}~
            +onSuccess: invalidates history + sessions
        }
        class useClearSession {
            <<hook>>
            +returns: UseMutationResult~void, Error, string~
            +onSuccess: removes from cache
        }
    }

    namespace "Utilities" {
        class usePrefetchWorkflow {
            <<hook>>
            +returns: (id) => void
            +purpose: performance optimization
        }
        class usePrefetchWorkflowBySlug {
            <<hook>>
            +returns: (slug) => void
            +purpose: performance optimization
        }
        class useInvalidateAgentQueries {
            <<hook>>
            +returns: () => void
            +purpose: force refetch all
        }
        class useResetAgentQueries {
            <<hook>>
            +returns: () => void
            +purpose: clear all cache
        }
    }

    namespace "External State" {
        class useAuthStore {
            <<store>>
            +user: User
            +token: string
            +isLoading: boolean
            +isAuthenticated: boolean
            +login(): void
            +logout(): void
            +checkAuth(): void
        }
        class useQueryClient {
            <<tanstack>>
            +invalidateQueries(): void
            +setQueryData(): void
            +removeQueries(): void
            +prefetchQuery(): void
            +resetQueries(): void
        }
    }

    namespace "API Endpoints" {
        class APISkills {
            <<api>>
            +GET /skills
            +GET /skills/{id}
        }
        class APIWorkflows {
            <<api>>
            +GET /workflows
            +GET /workflows/me
            +GET /workflows/public
            +GET /workflows/{id}
            +GET /workflows/slug/{slug}
            +POST /workflows
            +PUT /workflows/{id}
            +DELETE /workflows/{id}
            +POST /workflows/{id}/fork
            +POST /workflows/{id}/star
            +DELETE /workflows/{id}/star
        }
        class APIExecutions {
            <<api>>
            +POST /executions/workflows/{id}/run
            +GET /executions/{id}
            +GET /executions/workflows/{id}
            +GET /executions/me
            +POST /executions/{id}/cancel
        }
        class APIChat {
            <<api>>
            +POST /agents/{id}/chat
            +GET /agents/sessions/{id}/history
            +DELETE /agents/sessions/{id}
            +GET /agents/sessions/me
        }
    }

    %% Query relationships
    useSkills --> agentKeys: uses skillsList
    useSkill --> agentKeys: uses skill

    useWorkflows --> agentKeys: uses workflowsList
    useMyWorkflows --> agentKeys: uses workflowsMy
    usePublicWorkflows --> agentKeys: uses workflowsPublic
    useWorkflow --> agentKeys: uses workflow
    useWorkflowBySlug --> agentKeys: uses workflowBySlug

    useExecution --> agentKeys: uses execution
    useExecutions --> agentKeys: uses executionsList
    useMyExecutions --> agentKeys: uses executionsMy

    useSessionHistory --> agentKeys: uses sessionHistory
    useMySessions --> agentKeys: uses sessionsMy

    %% Mutation relationships
    useCreateWorkflow --> useQueryClient: cache management
    useUpdateWorkflow --> useQueryClient: cache management
    useDeleteWorkflow --> useQueryClient: cache management
    useForkWorkflow --> useQueryClient: cache management
    useStarWorkflow --> useQueryClient: optimistic update
    useUnstarWorkflow --> useQueryClient: optimistic update

    useRunWorkflow --> useQueryClient: cache management
    useCancelExecution --> useQueryClient: cache management

    useChatWithAgent --> useQueryClient: cache management
    useClearSession --> useQueryClient: cache management

    %% Prefetch utilities
    usePrefetchWorkflow --> useQueryClient: prefetchQuery
    usePrefetchWorkflowBySlug --> useQueryClient: prefetchQuery

    %% Invalidation utilities
    useInvalidateAgentQueries --> useQueryClient: invalidate
    useResetAgentQueries --> useQueryClient: reset

    %% Auth hook
    useRequireAuth --> useAuthStore: reads state
    useRequireAuth --> useRouter: navigation

    %% API connections
    useSkills --> APISkills: calls
    useSkill --> APISkills: calls

    useWorkflows --> APIWorkflows: calls
    useMyWorkflows --> APIWorkflows: calls
    usePublicWorkflows --> APIWorkflows: calls
    useWorkflow --> APIWorkflows: calls
    useWorkflowBySlug --> APIWorkflows: calls

    useCreateWorkflow --> APIWorkflows: calls
    useUpdateWorkflow --> APIWorkflows: calls
    useDeleteWorkflow --> APIWorkflows: calls
    useForkWorkflow --> APIWorkflows: calls
    useStarWorkflow --> APIWorkflows: calls
    useUnstarWorkflow --> APIWorkflows: calls

    useRunWorkflow --> APIExecutions: calls
    useExecution --> APIExecutions: calls
    useExecutions --> APIExecutions: calls
    useMyExecutions --> APIExecutions: calls
    useCancelExecution --> APIExecutions: calls

    useChatWithAgent --> APIChat: calls
    useSessionHistory --> APIChat: calls
    useClearSession --> APIChat: calls
    useMySessions --> APIChat: calls
```

### Hook Usage Patterns

1. **Query Hooks (Data Fetching)**
   - Wrap query hooks with conditional rendering based on `isLoading` and `isError`
   - Use data from hook return for rendering
   - Queries automatically refetch on:
     - Component mount (initial fetch)
     - Window refocus (if staleTime exceeded)
     - Manual invalidation (post-mutation)

2. **Mutation Hooks (State Changes)**
   - Call `mutate()` or `mutateAsync()` returned from hook
   - Handle loading state with `isPending`
   - Handle errors with `error`
   - `onSuccess` callbacks automatically update cache
   - Star/Unstar hooks use optimistic updates for instant feedback

3. **Optimistic Updates**
   - `useStarWorkflow` and `useUnstarWorkflow` update cache immediately
   - If server request fails, cache is rolled back to previous state
   - User sees instant UI feedback before server confirms

4. **Authentication Guard**
   - Wrap protected pages/routes with `useRequireAuth()`
   - Returns early if user not authenticated
   - Automatically redirects to login (customizable path)

5. **Polling Strategy**
   - `useExecution` polls every 2 seconds while status is "running" or "pending"
   - Stops polling automatically when execution completes
   - Reduces server load for completed executions

---

## Cache Management Strategy

### Stale Times

| Hook Family | Stale Time | Rationale |
|---|---|---|
| Skills | 5 min | Skills rarely change; good for performance |
| Workflows (paginated) | 2 min | List may change from user actions |
| Workflows (user's) | 1 min | User expects near-real-time of their changes |
| Workflows (public) | 5 min | Public content stable; rarely changes |
| Workflows (single) | 1 min | Detail page should reflect updates |
| Executions | 30 sec | Execution status must be current for monitoring |
| Chat History | 30 sec | Messages should appear quickly in conversation |
| Sessions | 1 min | Session list updates less frequently |

### Cache Invalidation Triggers

- **Workflow mutations:** Invalidate `workflowsList()` and `workflowsMy()` to refresh lists
- **Execution start:** Invalidate user's executions and workflow execution counts
- **Logout:** `useInvalidateAgentQueries()` clears all agent data
- **Chat message:** Invalidate session history and sessions list
- **Star/Unstar:** Invalidate workflow after optimistic update settles

---

## Type Safety

All hooks are fully typed with TypeScript:

- **Query hooks:** Generic `UseQueryResult<T, Error>` with specific data types
- **Mutation hooks:** Generic `UseMutationResult<TData, TError, TVariables>` with input/output types
- **API parameters:** Strict interfaces for pagination, filtering, etc.
- **Return types:** Complete type definitions from `@/lib/types`

---

## Notes

- All agent service API calls require authentication (Bearer token from `useAuthStore`)
- Hooks use Next.js App Router `useRouter` from `next/navigation` (not `next/router`)
- TanStack Query v5+ supports suspense (not currently used in these hooks)
- Offline support via TanStack Query's built-in persistence can be added
- Query keys are immutable tuples for type-safe cache access
- Cache strategy prioritizes responsiveness over consistency (eventual consistency model)
- Hooks are composable and can be combined in custom hooks for specific use cases
