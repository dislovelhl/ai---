import { create } from "zustand";
import { persist } from "zustand/middleware";
import {
  Connection,
  Edge,
  Node,
  addEdge,
  OnNodesChange,
  OnEdgesChange,
  OnConnect,
  applyNodeChanges,
  applyEdgeChanges,
  NodeChange,
  EdgeChange,
} from "@xyflow/react";
import { getLayoutedElements } from "@/lib/layout";
import * as Y from "yjs";
import { Awareness } from "y-protocols/awareness";
import { WebsocketProvider } from "y-websocket";
import { WebrtcProvider } from "y-webrtc";

const yDoc = new Y.Doc();
const yNodes = yDoc.getMap<any>("nodes");
const yEdges = yDoc.getMap<any>("edges");
const undoManager = new Y.UndoManager([yNodes, yEdges]);

// Awareness for cursors and presence
const awareness = new Awareness(yDoc);

let webrtcProvider: WebrtcProvider | null = null;
let websocketProvider: WebsocketProvider | null = null;

const setupProviders = (roomId: string) => {
  if (webrtcProvider) webrtcProvider.destroy();
  if (websocketProvider) websocketProvider.destroy();

  // WebRTC for low-latency P2P
  // Disabling for now as no signaling server is available on port 4444
  /*
  webrtcProvider = new WebrtcProvider(roomId, yDoc, {
    signaling: ["ws://localhost:4444"], // Local signaling server
    awareness,
  });
  */

  // Centralized WebSocket for robustness
  // Correctly target agent_service on port 8005
  websocketProvider = new WebsocketProvider(
    "ws://localhost:8005/v1/collaboration",
    roomId,
    yDoc,
    { awareness }
  );

  return { webrtcProvider, websocketProvider };
};

// Initial setup
setupProviders("ainav-studio-default");

export interface UserPresence {
  id: number;
  name: string;
  color: string;
  cursor?: { x: number; y: number };
  activeNodeId?: string;
}

// Connection types for workflow edges
export type ConnectionType = "data" | "control" | "error";

// Visual configuration for each connection type
export interface ConnectionTypeStyle {
  color: string; // HSL color value
  strokeWidth: number;
  strokeDasharray?: string; // CSS stroke-dasharray value (e.g., "5,5" for dashed)
  animationColor: string; // Color for the animated packet
  label?: string; // Optional default label
  description: string; // Description for tooltips
}

// Connection type visual styles configuration
export const CONNECTION_TYPE_STYLES: Record<
  ConnectionType,
  ConnectionTypeStyle
> = {
  data: {
    color: "hsl(217, 91%, 60%)", // Blue - primary data flow
    strokeWidth: 2,
    strokeDasharray: undefined, // Solid line
    animationColor: "hsl(217, 91%, 60%)",
    label: "Data",
    description: "Transfers data between nodes (text, JSON, numbers, etc.)",
  },
  control: {
    color: "hsl(142, 71%, 45%)", // Green - control flow
    strokeWidth: 2,
    strokeDasharray: "8,4", // Dashed line
    animationColor: "hsl(142, 71%, 45%)",
    label: "Control",
    description: "Controls execution flow (triggers, conditions, loops)",
  },
  error: {
    color: "hsl(0, 84%, 60%)", // Red - error handling
    strokeWidth: 2,
    strokeDasharray: "4,4", // Dotted line
    animationColor: "hsl(0, 84%, 60%)",
    label: "Error",
    description: "Handles errors and exceptions from upstream nodes",
  },
};

// Helper function to get connection type from edge data or default to 'data'
export function getConnectionType(
  edgeData?: Record<string, unknown>
): ConnectionType {
  const type = edgeData?.connectionType as ConnectionType | undefined;
  return type && ["data", "control", "error"].includes(type) ? type : "data";
}

// Helper function to get connection style by type
export function getConnectionStyle(
  connectionType: ConnectionType
): ConnectionTypeStyle {
  return CONNECTION_TYPE_STYLES[connectionType];
}

// Helper function to determine connection type from handle IDs
export function determineConnectionType(
  sourceHandleId: string | null | undefined,
  targetHandleId: string | null | undefined
): ConnectionType {
  // Handle IDs can be: "data", "control", "error"
  // If no handle ID specified, default to "data"

  const sourceType = sourceHandleId as ConnectionType | null | undefined;
  const targetType = targetHandleId as ConnectionType | null | undefined;

  // Error handles take precedence (error handling flow)
  if (sourceType === "error" || targetType === "error") {
    return "error";
  }

  // Control handles for execution flow
  if (sourceType === "control" || targetType === "control") {
    return "control";
  }

  // Default to data flow
  return "data";
}

// Helper function to validate if a connection is allowed
export function isValidConnection(
  connection: Connection,
  nodes: AppNode[]
): boolean {
  // Prevent self-connections
  if (connection.source === connection.target) {
    return false;
  }

  // Get source and target nodes
  const sourceNode = nodes.find((n) => n.id === connection.source);
  const targetNode = nodes.find((n) => n.id === connection.target);

  if (!sourceNode || !targetNode) {
    return false;
  }

  // Determine connection type
  const connectionType = determineConnectionType(
    connection.sourceHandle,
    connection.targetHandle
  );

  // Validate based on connection type
  switch (connectionType) {
    case "data":
      // Data connections are generally allowed between all node types
      return true;

    case "control":
      // Control connections should connect execution flow
      // For now, allow all but could be restricted based on node types
      return true;

    case "error":
      // Error connections should only connect to error-handling nodes
      // For now, allow all but could validate target node supports error handling
      return true;

    default:
      return true;
  }
}

// Node data types - must extend Record<string, unknown> for React Flow
export interface BaseNodeData extends Record<string, unknown> {
  label?: string;
}

export interface InputNodeData extends BaseNodeData {
  inputType?: "text" | "number" | "json" | "file";
  default?: string;
}

export interface LLMNodeData extends BaseNodeData {
  model?: string;
  prompt?: string;
  system_prompt?: string;
  temperature?: number;
  json_output?: boolean;
  // Runtime state
  status?:
    | "idle"
    | "pending"
    | "thinking"
    | "streaming"
    | "completed"
    | "error";
  content?: string;
  token_count?: number;
  isPreview?: boolean;
}

export interface SkillNodeData extends BaseNodeData {
  tool?: {
    id: string;
    name: string;
    logo_url?: string;
  };
  skill?: {
    id: string;
    name: string;
    api_endpoint?: string;
    http_method?: string;
    input_schema?: Record<string, unknown>;
    auth_type?: string;
  };
}

export interface TransformNodeData extends BaseNodeData {
  transform_type?:
    | "passthrough"
    | "extract"
    | "template"
    | "json_parse"
    | "json_stringify"
    | "array_join";
  field?: string;
  template?: string;
  separator?: string;
}

export interface OutputNodeData extends BaseNodeData {
  format?: "auto" | "text" | "json" | "markdown";
}

export type NodeData = BaseNodeData &
  Partial<InputNodeData> &
  Partial<LLMNodeData> &
  Partial<SkillNodeData> &
  Partial<TransformNodeData> &
  Partial<OutputNodeData>;

export type AppNode = Node<NodeData, string>;

// Execution state
export interface ExecutionState {
  isRunning: boolean;
  currentNodeId?: string;
  results: Record<string, unknown>;
  error?: string;
}

// Store interface
interface FlowState {
  // Flow data
  nodes: AppNode[];
  edges: Edge[];

  // Selected node for properties panel
  selectedNodeId: string | null;
  hoveredEdgeId: string | null;

  // Workflow metadata

  workflowName: string;
  workflowId?: string;
  isDirty: boolean;

  // History status
  canUndo: boolean;
  canRedo: boolean;

  // Execution state
  execution: ExecutionState;

  // Preview state (for Ghost nodes)
  preview: {
    nodes: AppNode[];
    edges: Edge[];
    isVisible: boolean;
  };

  // Node/Edge change handlers
  onNodesChange: OnNodesChange;
  onEdgesChange: OnEdgesChange;
  onConnect: OnConnect;
  isValidConnection: (connection: Connection) => boolean;

  // Actions
  addNode: (
    type: string,
    position: { x: number; y: number },
    data?: Partial<NodeData>
  ) => void;
  updateNodeData: (nodeId: string, data: Partial<NodeData>) => void;
  appendNodeContent: (nodeId: string, content: string) => void;
  updateEdgeData: (edgeId: string, data: Record<string, unknown>) => void;
  setAnimatingEdge: (edgeId: string | null, isAnimating: boolean) => void;
  deleteNode: (nodeId: string) => void;
  selectNode: (nodeId: string | null) => void;
  setHoveredEdge: (edgeId: string | null) => void;
  showInsertionPreview: (edgeId: string | null) => void;

  // Presence actions
  liveUsers: Record<number, UserPresence>;
  setPresence: (presence: Partial<UserPresence>) => void;

  // Workflow actions

  setWorkflowName: (name: string) => void;
  loadWorkflow: (workflow: {
    nodes: AppNode[];
    edges: Edge[];
    name?: string;
    id?: string;
  }) => void;
  clearWorkflow: () => void;
  getWorkflowJSON: () => { nodes: AppNode[]; edges: Edge[] };

  // Preview actions
  setPreview: (nodes: AppNode[], edges: Edge[]) => void;
  commitPreview: () => void;
  clearPreview: () => void;

  // History actions
  undo: () => void;
  redo: () => void;

  // Execution actions
  setExecutionState: (state: Partial<ExecutionState>) => void;
  resetExecution: () => void;
  autoLayout: (direction?: "LR" | "TB") => void;
}

// Default node data by type
const defaultNodeData: Record<string, Partial<NodeData>> = {
  input: { label: "输入", inputType: "text" },
  llm: {
    label: "LLM Core",
    model: "deepseek-chat",
    temperature: 0.7,
    status: "idle",
  },
  skill: { label: "技能" },
  transform: { label: "转换", transform_type: "passthrough" },
  output: { label: "输出", format: "auto", status: "idle" },
};

export const useFlowStore = create<FlowState>((set, get) => ({
  // Initial state
  nodes: [],
  edges: [],
  selectedNodeId: null,
  hoveredEdgeId: null,
  workflowName: "未命名工作流",

  isDirty: false,
  canUndo: false,
  canRedo: false,
  liveUsers: {},
  execution: {
    isRunning: false,
    results: {},
  },

  preview: {
    nodes: [],
    edges: [],
    isVisible: false,
  },

  // ... (keeping other actions)

  // Preview actions
  setPreview: (nodes, edges) => {
    set({
      preview: {
        nodes,
        edges,
        isVisible: true,
      },
    });
  },

  commitPreview: () => {
    const { nodes: previewNodes, edges: previewEdges } = get().preview;
    set({
      nodes: previewNodes,
      edges: previewEdges,
      preview: { nodes: [], edges: [], isVisible: false },
      isDirty: true,
    });
  },

  clearPreview: () => {
    set({
      preview: { nodes: [], edges: [], isVisible: false },
    });
  },

  // History actions
  undo: () => {
    undoManager.undo();
  },
  redo: () => {
    undoManager.redo();
  },

  // Node changes
  onNodesChange: (changes: NodeChange[]) => {
    const nodes = get().nodes;
    const nextNodes = applyNodeChanges(changes, nodes);
    set({ nodes: nextNodes, isDirty: true });

    // Sync to Yjs
    changes.forEach((change) => {
      if (change.type === "remove") {
        yNodes.delete(change.id);
      } else {
        const node = nextNodes.find((n) => n.id === change.id);
        if (node) {
          yNodes.set(node.id, node);
        }
      }
    });
  },

  // Edge changes
  onEdgesChange: (changes: EdgeChange[]) => {
    const edges = get().edges;
    const nextEdges = applyEdgeChanges(changes, edges);
    set({ edges: nextEdges, isDirty: true });

    // Sync to Yjs
    changes.forEach((change) => {
      if (change.type === "remove") {
        yEdges.delete(change.id);
      } else {
        const edge = nextEdges.find((e) => e.id === change.id);
        if (edge) {
          yEdges.set(edge.id, edge);
        }
      }
    });
  },

  // Validate connection
  isValidConnection: (connection: Connection) => {
    const nodes = get().nodes;
    return isValidConnection(connection, nodes);
  },

  // Connect nodes
  onConnect: (connection: Connection) => {
    const nodes = get().nodes;
    const edges = get().edges;

    // Validate connection
    if (!isValidConnection(connection, nodes)) {
      return;
    }

    // Determine connection type from handles
    const connectionType = determineConnectionType(
      connection.sourceHandle,
      connection.targetHandle
    );

    const nextEdges = addEdge(
      {
        ...connection,
        type: "animated",
        data: {
          isAnimating: false,
          connectionType,
        },
      },
      edges
    );
    set({ edges: nextEdges, isDirty: true });

    // Sync to Yjs
    nextEdges.forEach((edge) => {
      yEdges.set(edge.id, edge);
    });
  },

  // Add new node
  addNode: (type, position, data = {}) => {
    const newNode: AppNode = {
      id: `${type}-${Date.now()}`,
      type,
      position,
      data: {
        ...defaultNodeData[type],
        ...data,
      },
    };
    set({
      nodes: [...get().nodes, newNode],
      isDirty: true,
    });
  },

  // Update node data
  updateNodeData: (nodeId, data) => {
    set({
      nodes: get().nodes.map((node) =>
        node.id === nodeId ? { ...node, data: { ...node.data, ...data } } : node
      ),
    });
  },

  // Append content to node (for streaming)
  appendNodeContent: (nodeId, content) => {
    set({
      nodes: get().nodes.map((node) =>
        node.id === nodeId
          ? {
              ...node,
              data: {
                ...node.data,
                content: (node.data.content || "") + content,
                status: "streaming",
              },
            }
          : node
      ),
    });
  },

  // Update edge data
  updateEdgeData: (edgeId, data) => {
    set({
      edges: get().edges.map((edge) =>
        edge.id === edgeId ? { ...edge, data: { ...edge.data, ...data } } : edge
      ),
    });
  },

  // Set animating edge
  setAnimatingEdge: (edgeId, isAnimating) => {
    set({
      edges: get().edges.map((edge) =>
        edgeId === null || edge.id === edgeId
          ? { ...edge, data: { ...edge.data, isAnimating } }
          : edge
      ),
    });
  },

  // Delete node
  deleteNode: (nodeId) => {
    const currentNodes = get().nodes;
    const currentEdges = get().edges;

    const nextNodes = currentNodes.filter((n) => n.id !== nodeId);
    const edgesToRemove = currentEdges.filter(
      (e) => e.source === nodeId || e.target === nodeId
    );
    const nextEdges = currentEdges.filter(
      (e) => e.source !== nodeId && e.target !== nodeId
    );

    set({
      nodes: nextNodes,
      edges: nextEdges,
      selectedNodeId:
        get().selectedNodeId === nodeId ? null : get().selectedNodeId,
      isDirty: true,
    });

    // Sync to Yjs
    yDoc.transact(() => {
      yNodes.delete(nodeId);
      edgesToRemove.forEach((edge) => yEdges.delete(edge.id));
    });
  },

  // Select node
  selectNode: (nodeId) => {
    set({ selectedNodeId: nodeId });
  },

  // Set hovered edge
  setHoveredEdge: (edgeId) => {
    set({ hoveredEdgeId: edgeId });
  },

  // Show insertion preview on edge
  showInsertionPreview: (edgeId) => {
    if (!edgeId) {
      get().clearPreview();
      return;
    }

    const { nodes, edges } = get();
    const edge = edges.find((e) => e.id === edgeId);
    if (!edge) return;

    const sourceNode = nodes.find((n) => n.id === edge.source);
    const targetNode = nodes.find((n) => n.id === edge.target);

    if (!sourceNode || !targetNode) return;

    // Calculate midpoint
    const midX = (sourceNode.position.x + targetNode.position.x) / 2;
    const midY = (sourceNode.position.y + targetNode.position.y) / 2;

    const ghostNodeId = `ghost-${Date.now()}`;
    const previewNode: AppNode = {
      id: ghostNodeId,
      type: "llm",
      position: { x: midX, y: midY },
      data: {
        ...defaultNodeData.llm,
        label: "AI Suggestion",
        isPreview: true,
      },
    };

    const previewEdges: Edge[] = [
      {
        id: `preview-e1-${edgeId}`,
        source: edge.source,
        target: ghostNodeId,
        type: "animated",
        animated: true,
        style: { strokeDasharray: "5,5", opacity: 0.5 },
      },
      {
        id: `preview-e2-${edgeId}`,
        source: ghostNodeId,
        target: edge.target,
        type: "animated",
        animated: true,
        style: { strokeDasharray: "5,5", opacity: 0.5 },
      },
    ];

    set({
      preview: {
        nodes: [...nodes, previewNode],
        edges: [...edges.filter((e) => e.id !== edgeId), ...previewEdges],
        isVisible: true,
      },
    });
  },

  // Presence implementation
  setPresence: (partialPresence) => {
    const currentState = awareness.getLocalState() as UserPresence;
    awareness.setLocalState({
      ...currentState,
      ...partialPresence,
    });
  },

  // Set workflow name
  setWorkflowName: (name) => {
    set({ workflowName: name, isDirty: true });
  },

  // Load workflow
  loadWorkflow: (workflow) => {
    set({
      nodes: workflow.nodes,
      edges: workflow.edges,
      workflowName: workflow.name || "未命名工作流",
      workflowId: workflow.id,
      isDirty: false,
      selectedNodeId: null,
    });

    // Sync to Yjs
    yDoc.transact(() => {
      yNodes.clear();
      workflow.nodes.forEach((node) => yNodes.set(node.id, node));
      yEdges.clear();
      workflow.edges.forEach((edge) => yEdges.set(edge.id, edge));
    });
  },

  // Clear workflow
  clearWorkflow: () => {
    set({
      nodes: [],
      edges: [],
      workflowName: "未命名工作流",
      workflowId: undefined,
      isDirty: false,
      selectedNodeId: null,
      execution: { isRunning: false, results: {} },
    });

    // Sync to Yjs
    yDoc.transact(() => {
      yNodes.clear();
      yEdges.clear();
    });
  },

  // Get workflow as JSON (for API)
  getWorkflowJSON: () => {
    const { nodes, edges } = get();
    return { nodes, edges };
  },

  // Execution state
  setExecutionState: (state) => {
    set({
      execution: { ...get().execution, ...state },
    });
  },

  resetExecution: () => {
    set({
      execution: { isRunning: false, results: {} },
    });
  },
  autoLayout: (direction = "LR") => {
    const { nodes, edges } = get();
    const { nodes: layoutedNodes, edges: layoutedEdges } = getLayoutedElements(
      nodes,
      edges,
      direction
    );

    set({ nodes: layoutedNodes, edges: layoutedEdges, isDirty: true });

    // Sync to Yjs
    yDoc.transact(() => {
      layoutedNodes.forEach((node) => {
        yNodes.set(node.id, node);
      });
    });
  },
}));

// Sync Yjs -> Zustand (Observers)
yNodes.observe((event) => {
  if (event.transaction.local) return;
  const nodes = Array.from(yNodes.values()) as AppNode[];
  useFlowStore.setState({ nodes });
});

yEdges.observe((event) => {
  if (event.transaction.local) return;
  const edges = Array.from(yEdges.values()) as Edge[];
  useFlowStore.setState({ edges });
});

// History Tracking
const updateHistoryStatus = () => {
  useFlowStore.setState({
    canUndo: undoManager.undoStack.length > 0,
    canRedo: undoManager.redoStack.length > 0,
  });
};

undoManager.on("stack-item-added", updateHistoryStatus);
undoManager.on("stack-item-popped", updateHistoryStatus);
undoManager.on("stack-cleared", updateHistoryStatus);

// Presence Initialization & Sync
const COLORS = [
  "#ef4444",
  "#3b82f6",
  "#10b981",
  "#f59e0b",
  "#8b5cf6",
  "#ec4899",
];

const getStoredIdentity = () => {
  if (typeof window === "undefined") return null;
  const stored = localStorage.getItem("ainav-studio-identity");
  if (stored) {
    try {
      return JSON.parse(stored);
    } catch (e) {
      return null;
    }
  }
  return null;
};

const identity = getStoredIdentity() || {
  id: Math.random().toString(36).substring(7),
  name: `Agent-${Math.random().toString(36).substring(7)}`,
  color: COLORS[Math.floor(Math.random() * COLORS.length)],
};

if (typeof window !== "undefined") {
  localStorage.setItem("ainav-studio-identity", JSON.stringify(identity));
}

awareness.setLocalState(identity);

awareness.on("change", () => {
  const states = Array.from(awareness.getStates().entries());
  const liveUsers: Record<number, UserPresence> = {};

  states.forEach(([clientId, state]) => {
    if (clientId !== yDoc.clientID) {
      liveUsers[clientId] = state as UserPresence;
    }
  });

  useFlowStore.setState({ liveUsers });
});
