"use client";

import React, { memo } from "react";
import { Handle, Position, NodeProps } from "@xyflow/react";
import { Brain, Sparkles } from "lucide-react";
import { useFlowStore, type LLMNodeData } from "@/stores/flowStore";
import { cn } from "@/lib/utils";
import { NodeStatusIndicator, type NodeStatus } from "../node-status-indicator";

/**
 * LLMNode - Calls DeepSeek LLM for text generation.
 * The "brain" of the workflow with rich status indicators.
 */
export const LLMNode = memo(function LLMNode({
  data,
  selected,
  id,
}: NodeProps) {
  const nodeData = data as LLMNodeData;
  const isProcessing =
    nodeData.status === "thinking" || nodeData.status === "streaming";
  const liveUsers = useFlowStore((state) => state.liveUsers);

  // Find collaborators selecting this node
  const collaborators = Object.values(liveUsers).filter(
    (u) => u.activeNodeId === id
  );

  const [isJustConverted, setIsJustConverted] = React.useState(false);
  const prevIsPreview = React.useRef(nodeData.isPreview);

  React.useEffect(() => {
    if (prevIsPreview.current && !nodeData.isPreview) {
      setIsJustConverted(true);
      const timer = setTimeout(() => setIsJustConverted(false), 600);
      return () => clearTimeout(timer);
    }
    prevIsPreview.current = nodeData.isPreview;
  }, [nodeData.isPreview]);

  // Map node status to indicator status
  const displayStatus: NodeStatus = (() => {
    if (nodeData.status === "error") return "error";
    if (nodeData.status === "thinking") return "thinking";
    if (nodeData.status === "streaming") return "streaming";
    if (nodeData.status === "completed" || nodeData.content) return "completed";
    if (nodeData.status === "pending") return "pending";
    return "idle";
  })();

  return (
    <div
      className={cn(
        "relative min-w-[280px] rounded-xl border-2 bg-background shadow-2xl transition-all duration-300",
        selected
          ? "border-primary ring-4 ring-primary/20 scale-[1.02]"
          : "border-border",
        nodeData.isPreview &&
          "opacity-50 grayscale border-dashed border-primary/50",
        collaborators.length > 0 && "ring-4 ring-offset-2",
        isJustConverted && "animate-node-convert"
      )}
      style={
        collaborators.length > 0
          ? { borderStyle: "solid", borderColor: collaborators[0].color }
          : {}
      }
    >
      {/* Collaborator Indicators */}
      {collaborators.length > 0 && (
        <div className="absolute -top-6 right-0 flex -space-x-2">
          {collaborators.map((u) => (
            <div
              key={u.id}
              className="px-1.5 py-0.5 rounded text-[8px] font-bold text-white shadow-sm border border-white"
              style={{ backgroundColor: u.color }}
            >
              {u.name}
            </div>
          ))}
        </div>
      )}

      {/* Header */}
      <div className="bg-gradient-to-r from-violet-600 to-purple-600 px-4 py-2 text-white flex items-center justify-between rounded-t-[10px]">
        <div className="flex items-center gap-2">
          <Brain className={`w-4 h-4 ${isProcessing ? "animate-pulse" : ""}`} />
          <span className="font-bold text-xs uppercase tracking-wider">
            {nodeData.label || "LLM Core"}
          </span>
        </div>
        <div className="flex items-center gap-2">
          <NodeStatusIndicator
            status={displayStatus}
            size="sm"
            className="[&_svg]:text-white/80 [&_div]:bg-white/20"
          />
          {isProcessing && (
            <Sparkles className="w-4 h-4 text-yellow-300 animate-spin-slow" />
          )}
        </div>
      </div>

      {/* Data input handle with visual indicator */}
      <div className="absolute -left-2 top-1/2 -translate-y-1/2 group">
        <Handle
          type="target"
          position={Position.Left}
          id="data"
          className="!static !transform-none !w-4 !h-4 !bg-background !border-2 !border-blue-500 !rounded-full hover:!border-blue-600 transition-all hover:!scale-110"
          title="Data input: Text, JSON, or numbers"
        />
        {/* Outer glow ring */}
        <div className="absolute inset-0 -z-10 w-4 h-4 rounded-full bg-blue-500/30 group-hover:bg-blue-500/50 transition-colors" />
        {/* Pulsing indicator ring on hover */}
        <div className="absolute -inset-1 -z-20 w-6 h-6 -left-1 -top-1 rounded-full border-2 border-blue-400/50 opacity-0 group-hover:opacity-100 group-hover:animate-ping transition-opacity" />
      </div>

      <div className="p-4 space-y-3">
        {/* Model Info */}
        <div className="flex items-center justify-between text-[10px] text-muted-foreground bg-muted/50 px-2 py-1 rounded">
          <span className="font-medium underline decoration-violet-500/50">
            {nodeData.model || "deepseek-chat"}
          </span>
          {nodeData.token_count && <span>{nodeData.token_count} tokens</span>}
        </div>

        {/* Streaming/Content Area */}
        <div className="min-h-[60px] max-h-[200px] overflow-y-auto bg-muted/30 rounded-lg p-3 text-sm font-sans leading-relaxed selection:bg-violet-200">
          {nodeData.content ? (
            <div className="whitespace-pre-wrap">{nodeData.content}</div>
          ) : isProcessing ? (
            <div className="flex flex-col gap-2">
              <div className="h-2 w-full bg-violet-200 animate-pulse rounded" />
              <div className="h-2 w-3/4 bg-violet-200 animate-pulse rounded" />
            </div>
          ) : (
            <span className="text-muted-foreground italic text-xs">
              等待输入...
            </span>
          )}
          {nodeData.status === "streaming" && (
            <span className="inline-block w-1.5 h-4 ml-1 bg-violet-500 animate-pulse align-middle" />
          )}
        </div>

        {nodeData.prompt && (
          <div className="text-[10px] text-muted-foreground italic line-clamp-1 border-t pt-2 mt-2">
            &quot;{nodeData.prompt}&quot;
          </div>
        )}
      </div>

      {/* Text output handle with visual indicator */}
      <div className="absolute -right-2 top-1/2 -translate-y-1/2 group">
        <Handle
          type="source"
          position={Position.Right}
          id="output"
          className="!static !transform-none !w-4 !h-4 !bg-background !border-2 !border-purple-500 !rounded-full hover:!border-purple-600 transition-all hover:!scale-110"
          title="Text output: Generated AI response"
        />
        {/* Outer glow ring */}
        <div className="absolute inset-0 -z-10 w-4 h-4 rounded-full bg-purple-500/30 group-hover:bg-purple-500/50 transition-colors" />
        {/* Pulsing indicator ring on hover */}
        <div className="absolute -inset-1 -z-20 w-6 h-6 -left-1 -top-1 rounded-full border-2 border-purple-400/50 opacity-0 group-hover:opacity-100 group-hover:animate-ping transition-opacity" />
      </div>
    </div>
  );
});
