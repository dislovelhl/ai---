"use client";

import { useCallback, useRef, DragEvent, useMemo } from "react";
import {
  ReactFlow,
  Background,
  Controls,
  MiniMap,
  Panel,
  BackgroundVariant,
  Node,
  DefaultEdgeOptions,
  useReactFlow,
} from "@xyflow/react";
import { useEffect } from "react";
import "@xyflow/react/dist/style.css";
import { useDroppable } from "@dnd-kit/core";
import { MousePointer2 } from "lucide-react";

import { useFlowStore } from "@/stores/flowStore";
import { InputNode } from "./nodes/input-node";
import { LLMNode } from "./nodes/llm-node";
import { SkillNode } from "./nodes/skill-node";
import { OutputNode } from "./nodes/output-node";
import { TransformNode } from "./nodes/transform-node";
import { AnimatedEdge } from "./edges/animated-edge";

// Register custom node types
const nodeTypes = {
  input: InputNode,
  llm: LLMNode,
  skill: SkillNode,
  output: OutputNode,
  transform: TransformNode,
};

// Register custom edge types
const edgeTypes = {
  animated: AnimatedEdge,
};

const defaultEdgeOptions: DefaultEdgeOptions = {
  type: "animated",
};

/**
 * AgentCanvas - React Flow canvas for building agent workflows.
 * Supports drag-and-drop node creation and visual wiring.
 * Uses Zustand store for state management.
 */
export function AgentCanvas() {
  const reactFlowWrapper = useRef<HTMLDivElement>(null);

  // Get state and actions from Zustand store
  const {
    nodes: regularNodes,
    edges: regularEdges,
    onNodesChange,
    onEdgesChange,
    onConnect,
    isValidConnection,
    selectNode,
    addNode,
    preview,
    liveUsers,
    setPresence,
  } = useFlowStore();

  const { nodes, edges } = useMemo(() => {
    if (preview.isVisible) {
      return { nodes: preview.nodes, edges: preview.edges };
    }
    return { nodes: regularNodes, edges: regularEdges };
  }, [preview, regularNodes, regularEdges]);

  const { fitView } = useReactFlow();

  const handlePointerMove = useCallback(
    (e: React.PointerEvent) => {
      const rect = reactFlowWrapper.current?.getBoundingClientRect();
      if (rect) {
        setPresence({
          cursor: {
            x: e.clientX - rect.left,
            y: e.clientY - rect.top,
          },
        });
      }
    },
    [setPresence]
  );

  // Automatically fit view when nodes change (e.g. after AI generation)
  useEffect(() => {
    if (nodes.length > 0) {
      fitView({ padding: 0.2, duration: 800 });
    }
  }, [nodes.length, fitView]);

  // Setup as drop target
  const { setNodeRef, isOver } = useDroppable({
    id: "agent-canvas",
  });

  // Handle node selection
  const handleNodeClick = useCallback(
    (_: React.MouseEvent, node: Node) => {
      selectNode(node.id);
      setPresence({ activeNodeId: node.id });
    },
    [selectNode, setPresence]
  );

  // Handle canvas click (deselect)
  const handlePaneClick = useCallback(() => {
    selectNode(null);
    setPresence({ activeNodeId: undefined });
  }, [selectNode, setPresence]);

  // Handle drop from sidebar
  const handleDrop = useCallback(
    (event: DragEvent) => {
      event.preventDefault();

      const dataStr = event.dataTransfer.getData("application/reactflow");
      if (!dataStr) return;

      const data = JSON.parse(dataStr);
      const bounds = reactFlowWrapper.current?.getBoundingClientRect();

      if (!bounds) return;

      // Calculate position relative to canvas
      const position = {
        x: event.clientX - bounds.left - 100,
        y: event.clientY - bounds.top - 50,
      };

      addNode(data.type, position, data.data || {});
    },
    [addNode]
  );

  const handleDragOver = useCallback((event: DragEvent) => {
    event.preventDefault();
    event.dataTransfer.dropEffect = "move";
  }, []);

  return (
    <div
      ref={(node) => {
        setNodeRef(node);
        (reactFlowWrapper as any).current = node;
      }}
      className={`w-full h-full relative transition-colors ${
        isOver ? "bg-primary/5" : ""
      }`}
      onPointerMove={handlePointerMove}
      onMouseLeave={() => setPresence({ cursor: undefined })}
      onDrop={handleDrop}
      onDragOver={handleDragOver}
    >
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onConnect={onConnect}
        isValidConnection={isValidConnection}
        onNodeClick={handleNodeClick}
        onPaneClick={handlePaneClick}
        nodeTypes={nodeTypes}
        edgeTypes={edgeTypes}
        defaultEdgeOptions={defaultEdgeOptions}
        fitView
        className="bg-dot-pattern"
      >
        <Background variant={BackgroundVariant.Dots} gap={12} size={1} />
        <Controls />
        <MiniMap
          className="bg-background/80 backdrop-blur-sm border rounded-lg shadow-lg"
          nodeColor={(node) => {
            switch (node.type) {
              case "input":
                return "#22c55e";
              case "llm":
                return "#8b5cf6";
              case "skill":
                return "#f97316";
              case "output":
                return "#3b82f6";
              case "transform":
                return "#eab308";
              default:
                return "#6b7280";
            }
          }}
          maskColor="rgba(0, 0, 0, 0.1)"
        />

        {/* Empty state */}
        {nodes.length === 0 && (
          <Panel position="top-center" className="mt-20">
            <div className="text-center p-8 rounded-2xl bg-muted/50 backdrop-blur-sm border border-dashed border-muted-foreground/30">
              <div className="text-4xl mb-4">🤖</div>
              <h3 className="text-lg font-semibold mb-2">开始构建你的 Agent</h3>
              <p className="text-sm text-muted-foreground max-w-md">
                从左侧拖拽节点到画布上，连接它们创建工作流。
                <br />
                使用输入节点开始，LLM 节点进行处理，输出节点结束。
              </p>
            </div>
          </Panel>
        )}
      </ReactFlow>

      {/* Collaborator Cursors Overlay */}
      <div className="absolute inset-0 pointer-events-none overflow-hidden z-[9999]">
        {Object.entries(liveUsers).map(([clientId, presence]) => {
          if (!presence?.cursor) return null;
          return (
            <div
              key={clientId}
              className="absolute transition-all duration-300 ease-out will-change-transform"
              style={{
                left: presence.cursor.x,
                top: presence.cursor.y,
              }}
            >
              <MousePointer2
                className="w-4 h-4 -translate-x-1 -translate-y-1"
                style={{
                  fill: presence.color,
                  stroke: "white",
                  strokeWidth: 2,
                  color: presence.color,
                }}
              />
              <div
                className="ml-3 px-1.5 py-0.5 rounded text-[10px] font-bold text-white shadow-md backdrop-blur-sm whitespace-nowrap animate-in fade-in zoom-in duration-300"
                style={{ backgroundColor: presence.color }}
              >
                {presence.name}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
