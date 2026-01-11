# C4 Code Level: Agent UI Components

## Overview

- **Name:** Agent UI Components
- **Description:** React/TypeScript components for displaying and interacting with AI agent workflows, including agent discovery cards, real-time chat interfaces, and execution progress tracking
- **Location:** `/home/dislove/document/ai 导航/ainav-web/src/components/agents/`
- **Language:** TypeScript 5.x with React 19
- **Purpose:** Provide production-grade UI components for agent workflow management, user interaction via chat, and real-time execution monitoring

## Code Elements

### React Components

#### 1. AgentCard Component
- **File:** `agent-card.tsx` (195 lines)
- **Type:** Functional React Component (Client-side)
- **Purpose:** Display agent workflow metadata in a gallery/list view with interactive actions
- **Props Interface:**
  ```typescript
  interface AgentCardProps {
    workflow: AgentWorkflow;      // Agent workflow to display
    onFork?: () => void;          // Callback when fork action succeeds
    onStar?: () => void;          // Callback when star action succeeds
    onChat?: () => void;          // Callback to open chat overlay
  }
  ```

**Key Functions:**
- `handleStar(e: React.MouseEvent): Promise<void>` (lines 39-62)
  - Executes POST request to `/v1/workflows/{id}/star`
  - Updates star_count state and displays success toast
  - Error handling with user-friendly toast messages (Chinese localized)

- `handleFork(e: React.MouseEvent): Promise<void>` (lines 64-86)
  - Executes POST request to `/v1/workflows/{id}/fork`
  - Creates copy of workflow for current user
  - Success message guides users to Agent Studio for optimization

**State Management:**
- `stars: number` - Current star count (useState)
- `isStarred: boolean` - UI state for starred visual feedback (useState)

**Renders:**
- Card wrapper with hover effects and backdrop blur
- Workflow icon (Bot icon from lucide-react)
- Public/private badges
- Metadata: name, description, star count, fork count, run count, updated date
- Action buttons: Clone, Chat, Star, Fork

**Dependencies:**
- UI Components: Card, Badge, Button (shadcn/ui)
- Icons: Bot, Star, GitFork, Play, MessageSquare, Clock (lucide-react)
- Types: AgentWorkflow from `@/lib/types`
- Utilities: cn() for class name merging, toast() for notifications (sonner)
- Next.js: Link component (unused in current implementation)

**API Endpoints:**
- `POST /{NEXT_PUBLIC_AGENT_API_URL}/v1/workflows/{id}/star` - Star workflow
- `POST /{NEXT_PUBLIC_AGENT_API_URL}/v1/workflows/{id}/fork` - Fork workflow
- Default API URL: `http://localhost:8005`

---

#### 2. ChatOverlay Component
- **File:** `chat-overlay.tsx` (208 lines)
- **Type:** Functional React Component (Client-side Modal)
- **Purpose:** Full-screen chat interface for real-time conversation with agent workflows
- **Props Interface:**
  ```typescript
  interface ChatOverlayProps {
    agent: AgentWorkflow | null;    // Selected agent for chat session
    isOpen: boolean;                // Controls overlay visibility
    onClose: () => void;            // Callback to close overlay
  }
  ```

**Internal Types:**
- `Message` interface (lines 11-14):
  ```typescript
  interface Message {
    role: "user" | "assistant";     // Message sender
    content: string;                // Message text content
  }
  ```

**Key Functions:**
- `handleSend(): Promise<void>` (lines 53-90)
  - Validates input and agent existence
  - Builds user message and updates chat UI optimistically
  - POSTs to `/v1/workflows/{agent.id}/chat` with message payload
  - Handles streaming/polling response from agent
  - Error handling with fallback assistant message (Chinese)
  - Sets loading state during API call

**State Management:**
- `messages: Message[]` - Chat conversation history (useState)
- `input: string` - Current input text (useState)
- `isLoading: boolean` - Request pending state (useState)
- `scrollRef` - Reference to scroll container (useRef)

**Lifecycle Effects:**
- `useEffect` (lines 34-45): Initializes with agent greeting message when opened
- `useEffect` (lines 47-51): Auto-scrolls to bottom on new messages

**Renders:**
- Fixed position overlay (right side, full height)
- Header with agent icon, name, and close button
- ScrollArea with message list
  - User messages: right-aligned, primary color background
  - Assistant messages: left-aligned, dimmed background
  - Loading spinner while agent thinks
  - Icons: Bot for assistant, User for user
- Input section with:
  - Quick suggestion buttons (3 pre-written questions)
  - Input field with gradient focus effect
  - Send button
  - Attribution: "Powered by DeepSeek-V3 Engine"

**Configuration:**
- Fixed width: full width on mobile, 450px on desktop (sm breakpoint)
- Suggestions array (hardcoded Chinese questions):
  - "这个 Agent 能做什么？" (What can this agent do?)
  - "如何克隆并运行？" (How to clone and run?)
  - "它支持哪些模型？" (Which models does it support?)

**API Endpoint:**
- `POST /{NEXT_PUBLIC_AGENT_API_URL}/v1/workflows/{agent.id}/chat`
- Request: `{ message: string }`
- Response: `{ response: string }`

**Dependencies:**
- React Hooks: useState, useEffect, useRef
- UI Components: Button, Input, ScrollArea (shadcn/ui)
- Icons: X, Send, Bot, User, Sparkles, Loader2 (lucide-react)
- Types: AgentWorkflow from `@/lib/types`
- Utilities: cn() for conditional styling

---

#### 3. ExecutionStatus Component
- **File:** `execution-status.tsx` (300 lines)
- **Type:** Functional React Component (Status Display)
- **Purpose:** Display real-time execution status, progress, logs, and results for agent workflow runs
- **Props Interface:**
  ```typescript
  interface ExecutionStatusProps {
    executionId: string;           // ID of execution to monitor
    showDetails?: boolean;         // Show execution log details (default: true)
    onComplete?: (execution: AgentExecution) => void; // Callback when execution finishes
  }
  ```

**Constants:**
- `STATUS_CONFIG` object (lines 41-78) - Maps execution status to UI configuration:
  ```typescript
  {
    pending:  { icon: Clock,       color: "text-yellow-500",  label: "等待中" },
    running:  { icon: Loader2,     color: "text-blue-500",    label: "执行中", animate: true },
    completed:{ icon: CheckCircle2, color: "text-green-500",   label: "已完成" },
    failed:   { icon: XCircle,     color: "text-red-500",     label: "失败" },
    cancelled:{ icon: Square,      color: "text-gray-500",    label: "已取消" }
  }
  ```

**Key Functions:**
- `formatDuration(start: string, end?: string): string` (lines 139-147)
  - Calculates elapsed time between timestamps
  - Returns formatted string: "Xms", "X.Xs", or "XmYs"
  - Used for duration display in UI

- `handleCancel(): void` (lines 133-137)
  - Validates execution state (running/pending only)
  - Triggers `cancelMutation.mutate(executionId)`
  - Uses useCancelExecution hook for API call

**State Management:**
- `isExpanded: boolean` - Controls collapsible logs section (useState)

**Data Computations:**
- Progress percentage calculated from execution logs:
  - `totalSteps = logs.length`
  - `completedSteps = logs.filter(log => log.status === "completed").length`
  - `progress = (completedSteps / totalSteps) * 100`

**Hooks Used:**
- `useExecution(executionId)` - Fetches/polls execution data
  - Refetches every 2 seconds while running/pending
  - Returns: `{ data: AgentExecution, isLoading, error }`
- `useCancelExecution()` - Mutation for canceling execution
  - Returns: `{ mutate, isPending }`

**Renders:**
- Card component with status header
  - Status icon with appropriate color and animation
  - Status label and description (Chinese)
  - Duration badge (right side)
  - Cancel button (conditionally shown)
- Progress bar (only shown while running)
- Collapsible execution log details:
  - List of node execution steps
  - Status icon per step (CheckCircle2, XCircle, Loader2, Clock)
  - Node ID and type badge
  - Output/error message display
  - Timestamp for each step
- Output result section (if completed with data)
  - Green background, styled code block
  - JSON pretty-printed if object
- Error message section (if failed)
  - Red background, error text display

**Loading States:**
- Initial: Loading spinner centered in card
- Error: Alert icon with "无法加载执行状态" message
- Active: Full status display with dynamic updates

**Conditional Rendering:**
- Progress bar: Only shown if `isRunning`
- Logs section: Only shown if `showDetails && logs.length > 0`
- Cancel button: Only shown if `canCancel` (running/pending)
- Output section: Only shown if `status === "completed" && output_data`
- Error section: Only shown if `status === "failed" && error_message`

**Types Used:**
- `AgentExecution` interface with fields:
  - `status`: "pending" | "running" | "completed" | "failed" | "cancelled"
  - `execution_log`: Array of step logs with node_id, node_type, status, output, error, timestamp
  - `output_data`: unknown (stringified or JSON)
  - `error_message`: string
  - `created_at`, `completed_at`: ISO timestamps

---

#### 4. ExecutionStatusBadge Component (Sub-component)
- **File:** `execution-status.tsx` (lines 303-322)
- **Type:** Functional React Component (Compact Status Display)
- **Purpose:** Compact badge display for execution status in lists/tables
- **Props Interface:**
  ```typescript
  interface ExecutionStatusBadgeProps {
    status: string;  // Execution status code
  }
  ```

**Renders:**
- Badge with status icon and label text
- Color-coded by status (yellow/blue/green/red/gray)
- Animated spin icon for running status

---

#### 5. RunWorkflowButton Component
- **File:** `execution-status.tsx` (lines 333-374)
- **Type:** Functional React Component (Action Button)
- **Purpose:** Button to execute a workflow with optional input parameters
- **Props Interface:**
  ```typescript
  interface RunWorkflowButtonProps {
    workflowId: string;              // Target workflow ID
    input?: Record<string, unknown>; // Input parameters for workflow
    onExecutionStart?: (executionId: string) => void; // Callback with execution ID
    disabled?: boolean;              // Disable button
    className?: string;              // Tailwind classes
  }
  ```

**Key Functions:**
- `handleRun(): Promise<void>` (lines 342-353)
  - Dynamic import of `runWorkflow` from `@/lib/api`
  - Executes workflow with provided input
  - Calls `onExecutionStart` callback with execution ID
  - Error logging on failure

**State Management:**
- `isRunning: boolean` - Button loading state (useState)

**Renders:**
- Button with:
  - Play icon + "运行" text when idle
  - Spinner + "启动中..." text while running
  - Disabled state during execution
  - Custom className support

---

## Dependencies

### Internal Dependencies

**Type Definitions (ainav-web/src/lib/types.ts):**
- `AgentWorkflow` - Workflow metadata and configuration
- `AgentExecution` - Execution status, logs, and results
- `NodeExecutionLog` - Individual step execution details
- `ReactFlowGraph` - Workflow graph structure
- `ReactFlowNode` - Node definition in workflow
- `ReactFlowEdge` - Edge connection between nodes

**API Hooks (ainav-web/src/hooks/useAgentApi.ts):**
- `useExecution(id)` - Query hook for execution details with auto-refetch
- `useCancelExecution()` - Mutation hook for canceling execution
- `useRunWorkflow()` - Mutation hook for starting workflow execution

**API Module (ainav-web/src/lib/api.ts):**
- `runWorkflow(workflowId, input)` - Execute workflow
- `getExecution(id)` - Fetch execution details
- `cancelExecution(id)` - Cancel running execution
- `chatWithAgent(workflowId, message, sessionId?)` - Send chat message

**UI Components (shadcn/ui):**
- `Card` (CardHeader, CardContent, CardFooter, CardTitle, CardDescription)
- `Badge` - Status badges with variants
- `Button` - Styled buttons with variants and sizes
- `Input` - Text input field
- `Progress` - Progress bar for execution progress
- `ScrollArea` - Scrollable container
- `Collapsible` (CollapsibleContent, CollapsibleTrigger) - Expandable sections

**Icon Library (lucide-react):**
- Bot, User, Sparkles, Loader2, X, Send, Star, GitFork, Play, MessageSquare, Clock
- CheckCircle2, XCircle, Square, AlertCircle, ChevronUp, ChevronDown

**Utilities:**
- `cn()` from `@/lib/utils` - Class name merging (clsx alternative)
- `toast()` from "sonner" - Toast notifications (async, non-blocking)
- Next.js `Link` component - Client-side navigation

### External Dependencies

**React Ecosystem:**
- `react` (19.x) - UI framework
- `react-dom` - DOM rendering
- `@tanstack/react-query` (5.x) - Data fetching/caching
  - `useQuery`, `useMutation`, `useQueryClient`
  - Automatic cache invalidation and optimistic updates

**UI Framework:**
- `@radix-ui/*` - Headless UI components (underlying shadcn/ui)
  - Button, Card, Badge, Input, Collapsible, etc.

**Styling:**
- `tailwindcss` (4.x) - Utility-first CSS framework
- `class-variance-authority` - Component variant patterns

**Environment:**
- `next` (16.x) - Server/client boundary, routing
- `typescript` (5.x) - Type safety

**API & Network:**
- Native `fetch` API - HTTP requests to Agent Service
- JSON serialization/deserialization

---

## Relationships

### Component Hierarchy

```
├── AgentCard (Gallery/List display)
│   └── Props: workflow, onFork, onStar, onChat
│       └── Callbacks typically connected to parent
│
├── ChatOverlay (Modal conversation interface)
│   └── Props: agent, isOpen, onClose
│       └── Overlays on top of other UI
│
├── ExecutionStatus (Detailed execution view)
│   ├── ExecutionStatusBadge (Compact version)
│   └── RunWorkflowButton (Companion action button)
│
└── RunWorkflowButton (Standalone workflow execution)
    └── Props: workflowId, input, onExecutionStart, disabled, className
```

### State Flow & Data Updates

```
User Action (UI)
    │
    ├─→ AgentCard.handleStar()
    │   └─→ POST /workflows/{id}/star
    │       └─→ Update star_count state
    │           └─→ toast.success() notification
    │
    ├─→ AgentCard.handleFork()
    │   └─→ POST /workflows/{id}/fork
    │       └─→ onFork() callback
    │           └─→ Parent handles navigation/refetch
    │
    ├─→ ChatOverlay.handleSend()
    │   └─→ POST /workflows/{id}/chat { message }
    │       └─→ setMessages([...prev, assistant_response])
    │           └─→ Auto-scroll to bottom
    │
    ├─→ ExecutionStatus (via useExecution hook)
    │   └─→ Auto-refetch every 2s while running
    │       └─→ Update UI with latest status/logs
    │           └─→ Call onComplete() when done
    │
    └─→ RunWorkflowButton.handleRun()
        └─→ POST /workflows/{id}/execute { input }
            └─→ onExecutionStart(execution.id) callback
                └─→ Parent component displays ExecutionStatus
```

### Real-Time Updates

**Execution Monitoring:**
- `useExecution()` hook implements intelligent polling
- Poll interval: 2000ms (2 seconds) while status is "running" or "pending"
- Stops polling when execution completes, fails, or is cancelled
- Re-polling triggered by React Query's smart refetch strategy

**Chat Interface:**
- Synchronous request-response model (no WebSocket)
- User message added optimistically to UI
- Loading spinner shown while awaiting agent response
- Assistant message appended to history on response

**Agent Service Communication:**
- Base URL configurable via `NEXT_PUBLIC_AGENT_API_URL` environment variable
- Defaults to `http://localhost:8005` for local development
- All endpoints under `/v1/` prefix
- JSON request/response bodies

---

## Architecture Patterns

### State Management Pattern

The components use **React Hooks** for local state with **TanStack React Query** for server state:

**Client State (useState):**
- AgentCard: `stars`, `isStarred` - UI-only state
- ChatOverlay: `messages`, `input`, `isLoading` - Conversation state
- ExecutionStatus: `isExpanded` - UI toggle state
- RunWorkflowButton: `isRunning` - Loading indicator

**Server State (useQuery/useMutation):**
- Execution data fetched via `useExecution()` with auto-polling
- Mutations handled via `useCancelExecution()` with optimistic updates
- Cache keys from `agentKeys` hierarchy enable fine-grained invalidation

### Component Lifecycle Pattern

**AgentCard:**
- Render-only component with event handlers
- No lifecycle hooks (stateless display logic)
- Side effects: API calls in event handlers

**ChatOverlay:**
- Initialize: Set greeting message when opened
- Active: Handle message submission and scroll
- Cleanup: Implicitly via conditional rendering (isOpen check)

**ExecutionStatus:**
- Mount: Fetch execution data and start polling
- Active: Refetch every 2s while running, call onComplete when done
- Unmount: Cleanup via React Query automatically

### Error Handling Patterns

**API Error Handling:**

AgentCard:
```typescript
try {
  const res = await fetch(...);
  if (res.ok) {
    // success path
  }
} catch (e) {
  toast.error("操作失败");
}
```

ChatOverlay:
```typescript
try {
  const response = await fetch(...);
  if (response.ok) {
    // success path
  } else {
    throw new Error("Failed to get response");
  }
} catch (error) {
  // Append error message to chat
  setMessages(prev => [...prev, {
    role: "assistant",
    content: "抱歉，我现在无法响应。请稍后再试。"
  }]);
}
```

ExecutionStatus:
```typescript
const { data: execution, isLoading, error } = useExecution(executionId);

if (isLoading) {
  return <LoadingCard />;
}

if (error || !execution) {
  return <ErrorCard />;
}
```

### Localization Pattern

All Chinese text strings are hardcoded in components (not extracted to i18n):
- Toast messages: "已点赞", "操作失败", "已成功复制到你的工作台"
- UI labels: "对话", "克隆", "执行中", "错误信息", "输出结果"
- Placeholders: "输入你的问题..."
- Status descriptions: "等待中", "执行中", "已完成", "失败", "已取消"

**Future improvement:** Extract to i18n system for multi-language support

---

## API Integration

### Agent Service Endpoints Used

**Workflow Management:**
- `POST /v1/workflows/{id}/star` - Add star to workflow
  - No request body
  - Response: `{ star_count: number }`

- `POST /v1/workflows/{id}/fork` - Create workflow copy
  - No request body
  - Response: `AgentWorkflow` object

**Chat:**
- `POST /v1/workflows/{id}/chat` - Send chat message to agent
  - Request: `{ message: string }`
  - Response: `{ response: string }`

**Execution:**
- `GET /v1/executions/{id}` - Fetch execution details (via useExecution)
  - Response: `AgentExecution` object with execution_log array

- `POST /v1/workflows/{id}/execute` - Start workflow execution
  - Request: `ExecutionCreate` with input_data and trigger metadata
  - Response: `AgentExecution` object with id

- `POST /v1/executions/{id}/cancel` - Cancel running execution
  - No request body
  - Response: void

### Environment Configuration

```env
# Agent Service base URL (defaults to http://localhost:8005)
NEXT_PUBLIC_AGENT_API_URL=http://agent-service:8005

# Frontend URLs for other services (used in api.ts)
NEXT_PUBLIC_API_URL=http://localhost:8001/v1
NEXT_PUBLIC_SEARCH_API=http://localhost:8002/v1
NEXT_PUBLIC_USER_API=http://localhost:8003/v1
```

---

## Component Dependencies Map

```mermaid
---
title: Code Diagram for Agent UI Components
---
classDiagram
    namespace Components {
        class AgentCard {
            +workflow: AgentWorkflow
            +onFork?: function
            +onStar?: function
            +onChat?: function
            +handleStar() Promise
            +handleFork() Promise
        }

        class ChatOverlay {
            +agent: AgentWorkflow | null
            +isOpen: boolean
            +onClose: function
            +messages: Message[]
            +input: string
            +isLoading: boolean
            +handleSend() Promise
            +scrollRef: RefObject
        }

        class ExecutionStatus {
            +executionId: string
            +showDetails?: boolean
            +onComplete?: function
            +isExpanded: boolean
            +handleCancel() void
            +formatDuration() string
        }

        class ExecutionStatusBadge {
            +status: string
        }

        class RunWorkflowButton {
            +workflowId: string
            +input?: Record
            +onExecutionStart?: function
            +disabled?: boolean
            +className?: string
            +isRunning: boolean
            +handleRun() Promise
        }
    }

    namespace Types {
        class AgentWorkflow {
            +id: string
            +user_id: string
            +name: string
            +name_zh?: string
            +slug: string
            +description?: string
            +graph_json: ReactFlowGraph
            +trigger_type: string
            +is_public: boolean
            +fork_count: number
            +run_count: number
            +star_count: number
            +created_at: string
            +updated_at: string
        }

        class AgentExecution {
            +id: string
            +workflow_id: string
            +status: string
            +execution_log?: NodeExecutionLog[]
            +output_data?: unknown
            +error_message?: string
            +created_at: string
            +updated_at: string
        }

        class NodeExecutionLog {
            +node_id: string
            +node_type: string
            +status: string
            +output_data?: unknown
            +error_message?: string
            +timestamp: string
        }
    }

    namespace Hooks {
        class useExecution {
            +id: string
            +returns: UseQueryResult
        }

        class useCancelExecution {
            +returns: UseMutationResult
        }

        class useRunWorkflow {
            +returns: UseMutationResult
        }
    }

    namespace API {
        class AgentServiceAPI {
            +POST /workflows/{id}/star
            +POST /workflows/{id}/fork
            +POST /workflows/{id}/chat
            +GET /executions/{id}
            +POST /workflows/{id}/execute
            +POST /executions/{id}/cancel
        }
    }

    AgentCard --> AgentWorkflow : uses
    AgentCard --> AgentServiceAPI : calls

    ChatOverlay --> AgentWorkflow : uses
    ChatOverlay --> AgentServiceAPI : calls

    ExecutionStatus --> AgentExecution : uses
    ExecutionStatus --> NodeExecutionLog : displays
    ExecutionStatus --> useExecution : uses hook
    ExecutionStatus --> useCancelExecution : uses hook

    ExecutionStatusBadge --> ExecutionStatus : sub-component

    RunWorkflowButton --> useRunWorkflow : uses hook
    RunWorkflowButton --> AgentServiceAPI : calls

    useExecution --> AgentServiceAPI : queries
    useCancelExecution --> AgentServiceAPI : mutates
    useRunWorkflow --> AgentServiceAPI : mutates
```

---

## Key Data Flows

### Chat Flow (User Perspective)

```
1. User clicks "对话" button on AgentCard
   ↓
2. ChatOverlay opens with initial greeting message
   └─ "你好！我是 {agent.name_zh}..."
   ↓
3. User types question in input field
   ↓
4. User presses Enter or clicks Send button
   ↓
5. ChatOverlay.handleSend() executes:
   a) Validates input is not empty and agent exists
   b) Creates user Message object
   c) setMessages([...prev, userMessage]) - optimistic update
   d) Clears input field
   e) Sets isLoading = true
   f) POST /v1/workflows/{agent.id}/chat with user message
   ↓
6. Agent Service processes message via DeepSeek-V3
   ↓
7. ChatOverlay receives response:
   a) Parses JSON response: { response: string }
   b) Creates assistant Message object
   c) setMessages([...prev, assistantMessage])
   d) Sets isLoading = false
   e) Auto-scrolls to bottom
   ↓
8. Loop back to step 3 for next message
```

### Execution Tracking Flow

```
1. User clicks "运行" via RunWorkflowButton
   ↓
2. RunWorkflowButton.handleRun() executes:
   a) setIsRunning = true
   b) Import runWorkflow function dynamically
   c) POST /v1/workflows/{id}/execute with input
   d) Receive AgentExecution object
   e) Call onExecutionStart(execution.id) callback
   f) Parent component displays ExecutionStatus
   ↓
3. ExecutionStatus component mounts with executionId:
   a) useExecution hook triggers query
   b) GET /v1/executions/{executionId}
   c) Sets refetchInterval to 2000ms (status check)
   ↓
4. Real-time polling loop while executing:
   a) Every 2 seconds: fetch latest execution state
   b) Agent Service returns:
      - status: "pending" | "running" | "completed" | "failed"
      - execution_log: Array of step results
      - output_data (when completed)
      - error_message (if failed)
   c) ExecutionStatus re-renders with latest data
   d) Progress bar updates: (completedSteps / totalSteps) * 100
   e) Log entries expand as steps complete
   ↓
5. Execution completes (status = "completed" | "failed"):
   a) React Query stops polling
   b) ExecutionStatus detects completion via useEffect
   c) Calls onComplete(execution) callback
   d) Displays final output or error message
   e) User can inspect full execution logs
```

### Star/Fork Flow

```
AgentCard.handleStar():
  ↓
User clicks star icon
  ↓
e.stopPropagation() + e.preventDefault()
  ↓
POST /v1/workflows/{workflow.id}/star
  ↓
Response: { star_count: number }
  ↓
setStars(data.star_count) - optimistic update
setIsStarred(true) - visual feedback
toast.success("已点赞")
onStar?.() - parent callback
  ↓
FALLBACK: catch block
  ↓
toast.error("操作失败")


AgentCard.handleFork():
  ↓
User clicks fork icon
  ↓
e.stopPropagation() + e.preventDefault()
  ↓
POST /v1/workflows/{workflow.id}/fork
  ↓
Response: (forked AgentWorkflow)
  ↓
toast.success("已成功复制到你的工作台", {
  description: "你可以在 Agent Studio 中优化它"
})
onFork?.() - parent callback (usually navigates to studio)
  ↓
FALLBACK: catch block
  ↓
toast.error("复制失败")
```

---

## Performance Characteristics

### Rendering Performance

**AgentCard:**
- Pure component (no complex calculations)
- Memoization candidate for gallery with 50+ items
- CSS-based hover effects (hardware accelerated)
- Card hover animation: 300ms transition duration

**ChatOverlay:**
- Messages array grows with conversation
- Consider virtual scrolling for 100+ message conversations
- Current: ScrollArea with auto-scroll (acceptable for typical sessions)

**ExecutionStatus:**
- Polling every 2s during execution
- Execution log could grow large (100+ steps)
- Collapsible section prevents rendering all logs initially
- Consider pagination for executions with 1000+ steps

### Network Performance

**AgentCard Actions:**
- Star/Fork: 1 HTTP request each (usually <100ms)
- No data loading overhead

**ChatOverlay:**
- 1 HTTP POST per message
- Typical response time: 2-5 seconds (agent inference)
- No caching (each message is unique)

**ExecutionStatus:**
- 1 HTTP GET every 2 seconds while running
- Typical execution duration: 10 seconds - 10 minutes
- Polling generates 5-300 requests per execution
- Could be optimized with WebSocket connection

---

## Notes

### Known Limitations

1. **No WebSocket:** Chat and execution updates use HTTP polling
   - Suitable for current load but will limit real-time responsiveness at scale
   - Future: Consider switching to WebSocket for <1s latency

2. **No Message Persistence:** Chat messages stored only in component state
   - Closing overlay loses conversation history
   - Reload page loses all chat history
   - Solution: Store in sessionStorage or database

3. **Hardcoded Localization:** All Chinese text embedded in components
   - No i18n system for multi-language support
   - Solution: Extract to i18n library (next-intl, i18next)

4. **No Optimistic Updates for Execution:** Can't predict execution time
   - Execution status always pulled from server
   - Chat messages are optimistic (better UX)

5. **Limited Error Recovery:** Generic error messages to users
   - No retry logic for failed API requests
   - Solution: Implement exponential backoff in useCancelExecution

### Accessibility (a11y)

**Good:**
- Semantic HTML with Button and Input components
- Icon labels ("对话", "克隆") in buttons
- Status descriptions for screen readers

**Could Improve:**
- Add aria-labels for icon-only buttons (star icon)
- Add aria-live="polite" for real-time status updates
- Add keyboard navigation for chat suggestions
- Better color contrast on loading spinner (blue on slate)

### Security Considerations

**Current:**
- API endpoints called directly from browser (no CORS proxy)
- Authentication assumed to be handled at API level
- No input sanitization (XSS risk if API returns untrusted content)

**Recommendations:**
- API should validate/sanitize agent responses before sending to frontend
- Implement Content Security Policy headers
- Use DOMPurify if parsing HTML in agent responses
- Add rate limiting on star/fork actions (already rate-limited on backend)

### Browser Compatibility

**Target:** Modern browsers with ES2020+ support
- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

**Requirements:**
- ES Modules
- Fetch API
- IntersectionObserver (ScrollArea)
- ResizeObserver (Collapsible)

---

## File References

| File | Lines | Purpose |
|------|-------|---------|
| `agent-card.tsx` | 195 | Agent workflow display card with star/fork actions |
| `chat-overlay.tsx` | 208 | Full-screen chat interface for agent interaction |
| `execution-status.tsx` | 300 | Real-time execution monitoring with progress & logs |

## Related Files in Codebase

- `/ainav-web/src/lib/types.ts` - Type definitions (AgentWorkflow, AgentExecution)
- `/ainav-web/src/lib/api.ts` - API client functions
- `/ainav-web/src/hooks/useAgentApi.ts` - React Query hooks with cache management
- `/ainav-web/src/components/ui/*` - shadcn/ui component library
- `/ainav-backend/services/agent_service/` - Backend API implementation

