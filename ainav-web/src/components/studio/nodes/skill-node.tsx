"use client";

import React, { memo } from "react";
import { Handle, Position, NodeProps } from "@xyflow/react";
import { Zap } from "lucide-react";
import { Tool, Skill } from "@/lib/types";
import { useFlowStore } from "@/stores/flowStore";
import { cn } from "@/lib/utils";
import { NodeStatusIndicator, type NodeStatus } from "../node-status-indicator";

interface SkillNodeData {
  label?: string;
  tool?: Tool;
  skill?: Skill;
  isPreview?: boolean;
  status?: "idle" | "pending" | "running" | "completed" | "error";
  error?: string;
}

/**
 * SkillNode - Calls an external API (tool skill).
 * Connects to third-party services with status indicators.
 */
export const SkillNode = memo(function SkillNode({
  data,
  selected,
  id,
}: NodeProps) {
  const nodeData = data as SkillNodeData;
  const skill = nodeData.skill;
  const tool = nodeData.tool;
  const liveUsers = useFlowStore((state) => state.liveUsers);
  const collaborators = Object.values(liveUsers).filter(
    (u) => u.activeNodeId === id
  );

  const isPreview = nodeData.isPreview;
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
        "relative min-w-[240px] rounded-xl border-2 bg-background shadow-lg transition-all duration-300",
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
      <div className="bg-gradient-to-r from-orange-500 to-amber-500 px-4 py-2 text-white rounded-t-[10px] flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Zap className="w-4 h-4" />
          <span className="font-bold text-xs uppercase tracking-wider">
            {nodeData.label || skill?.name || "技能"}
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
        className="!w-3 !h-3 !bg-white !border-2 !border-orange-600 !-left-1.5"
      />

      <div className="px-4 py-3">
        {tool && <div className="text-xs opacity-80 mb-2">{tool.name}</div>}

        {nodeData.error && (
          <div className="text-[10px] text-red-500 bg-red-50 dark:bg-red-950/30 p-2 rounded mb-2">
            {nodeData.error}
          </div>
        )}

        {skill ? (
          <div className="flex items-center gap-2 text-[10px]">
            <span className="px-1.5 py-0.5 rounded bg-orange-100 dark:bg-orange-900/30 text-orange-700 dark:text-orange-300 font-medium">
              {skill.http_method}
            </span>
            <span className="truncate max-w-[100px] text-muted-foreground">
              {skill.api_endpoint?.split("/").pop()}
            </span>
          </div>
        ) : (
          <div className="text-xs bg-muted/50 rounded-lg px-2 py-1.5 text-center text-muted-foreground">
            拖拽工具到此处
          </div>
        )}
      </div>

      {/* Output handle */}
      <Handle
        type="source"
        position={Position.Right}
        className="!w-3 !h-3 !bg-white !border-2 !border-amber-600 !-right-1.5"
      />
    </div>
  );
});
