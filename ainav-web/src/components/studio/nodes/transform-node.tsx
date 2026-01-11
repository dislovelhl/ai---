"use client";

import React, { memo } from "react";
import { Handle, Position, NodeProps } from "@xyflow/react";
import { Shuffle } from "lucide-react";
import { useFlowStore } from "@/stores/flowStore";
import { cn } from "@/lib/utils";
import { NodeStatusIndicator, type NodeStatus } from "../node-status-indicator";

interface TransformNodeData {
  label?: string;
  transform_type?: string;
  field?: string;
  template?: string;
  isPreview?: boolean;
  status?: "idle" | "pending" | "running" | "completed" | "error";
  error?: string;
}

const transformLabels: Record<string, string> = {
  passthrough: "透传",
  extract: "提取",
  template: "模板",
  json_parse: "JSON 解析",
  json_stringify: "序列化",
  array_join: "合并",
};

/**
 * TransformNode - Data transformation and processing.
 * Extracts fields, applies templates, parses JSON, etc.
 */
export const TransformNode = memo(function TransformNode({
  data,
  selected,
  id,
}: NodeProps) {
  const nodeData = data as TransformNodeData;
  const transformType = nodeData.transform_type || "passthrough";
  const isPreview = nodeData.isPreview;

  const liveUsers = useFlowStore((state) => state.liveUsers);
  const collaborators = Object.values(liveUsers).filter(
    (u) => u.activeNodeId === id
  );

  const [isJustConverted, setIsJustConverted] = React.useState(false);
  const prevIsPreview = React.useRef(isPreview);

  React.useEffect(() => {
    if (prevIsPreview.current && !isPreview) {
      setIsJustConverted(true);
      const timer = setTimeout(() => setIsJustConverted(false), 600);
      return () => clearTimeout(timer);
    }
    prevIsPreview.current = isPreview;
  }, [isPreview]);

  // Determine display status
  const displayStatus: NodeStatus = (() => {
    if (nodeData.status === "error") return "error";
    if (nodeData.status === "running") return "running";
    if (nodeData.status === "completed") return "completed";
    if (nodeData.status === "pending") return "pending";
    return "idle";
  })();

  return (
    <div
      className={cn(
        "relative min-w-[220px] rounded-xl border-2 bg-background shadow-lg transition-all duration-300",
        selected
          ? "border-primary ring-4 ring-primary/20 scale-[1.02]"
          : "border-border",
        isPreview && "opacity-50 grayscale border-dashed border-primary/50",
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
        <div className="absolute -top-6 right-0 flex -space-x-1">
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
      <div className="bg-gradient-to-r from-yellow-500 to-amber-500 px-4 py-2 text-white rounded-t-[10px] flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Shuffle className="w-4 h-4" />
          <span className="font-bold text-xs uppercase tracking-wider">
            {nodeData.label || "转换"}
          </span>
        </div>
        <NodeStatusIndicator
          status={displayStatus}
          size="sm"
          className="[&_svg]:text-white/80 [&_div]:bg-white/20"
        />
      </div>

      {/* Input handle */}
      <Handle
        type="target"
        position={Position.Left}
        className="!w-3 !h-3 !bg-white !border-2 !border-yellow-600 !-left-1.5"
      />

      <div className="px-4 py-3">
        <div className="text-xs text-muted-foreground mb-1">
          {transformLabels[transformType] || transformType}
        </div>

        {nodeData.error && (
          <div className="text-[10px] text-red-500 bg-red-50 dark:bg-red-950/30 p-2 rounded mb-2">
            {nodeData.error}
          </div>
        )}

        {nodeData.field && (
          <div className="text-[10px] bg-muted/50 rounded px-1.5 py-0.5 font-mono text-muted-foreground">
            {nodeData.field}
          </div>
        )}

        {nodeData.template && (
          <div className="text-[10px] bg-muted/50 rounded px-1.5 py-0.5 mt-1 font-mono text-muted-foreground truncate max-w-[180px]">
            {nodeData.template}
          </div>
        )}
      </div>

      {/* Output handle */}
      <Handle
        type="source"
        position={Position.Right}
        className="!w-3 !h-3 !bg-white !border-2 !border-amber-500 !-right-1.5"
      />
    </div>
  );
});
