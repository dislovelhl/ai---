"use client";

import React, { memo } from "react";
import { Handle, Position, NodeProps } from "@xyflow/react";
import { Shuffle } from "lucide-react";
import { useFlowStore } from "@/stores/flowStore";
import { cn } from "@/lib/utils";
import { NodeStatusIndicator, type NodeStatus } from "../node-status-indicator";
import {
  InlineSelect,
  InlineInput,
  type InlineSelectOption,
} from "../inline-editors";

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

// Transform type options for InlineSelect
const TRANSFORM_TYPE_OPTIONS: InlineSelectOption[] = [
  { value: "passthrough", label: "透传 (Passthrough)" },
  { value: "extract", label: "提取 (Extract)" },
  { value: "template", label: "模板 (Template)" },
  { value: "json_parse", label: "JSON 解析 (Parse)" },
  { value: "json_stringify", label: "序列化 (Stringify)" },
  { value: "array_join", label: "合并 (Join)" },
];

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
  const updateNodeData = useFlowStore((state) => state.updateNodeData);
  const collaborators = Object.values(liveUsers).filter(
    (u) => u.activeNodeId === id
  );

  // Disable editing when node is processing
  const isProcessing =
    nodeData.status === "running" || nodeData.status === "pending";

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

      {/* Data input handle with visual indicator */}
      <div className="absolute -left-2 top-1/2 -translate-y-1/2 group">
        <Handle
          type="target"
          position={Position.Left}
          id="input"
          className="!static !transform-none !w-4 !h-4 !bg-background !border-2 !border-blue-500 !rounded-full hover:!border-blue-600 transition-all hover:!scale-110"
          title="Data input: Raw data to transform"
        />
        {/* Outer glow ring */}
        <div className="absolute inset-0 -z-10 w-4 h-4 rounded-full bg-blue-500/30 group-hover:bg-blue-500/50 transition-colors" />
        {/* Pulsing indicator ring on hover */}
        <div className="absolute -inset-1 -z-20 w-6 h-6 -left-1 -top-1 rounded-full border-2 border-blue-400/50 opacity-0 group-hover:opacity-100 group-hover:animate-ping transition-opacity" />
      </div>

      <div className="p-4 space-y-3">
        {/* Transform Type Selection */}
        <div className="space-y-1">
          <div className="flex items-center justify-between gap-2">
            <span className="text-[10px] text-muted-foreground font-medium">
              Type:
            </span>
            <InlineSelect
              value={transformType}
              onChange={(value) =>
                updateNodeData(id, { transform_type: value })
              }
              options={TRANSFORM_TYPE_OPTIONS}
              placeholder="Select transform type..."
              className="flex-1"
              selectClassName="text-[10px]"
              displayClassName="text-[10px] bg-muted/50 hover:bg-muted"
              disabled={isProcessing}
            />
          </div>
        </div>

        {/* Field Path Input (for extract and template types) */}
        {(transformType === "extract" || transformType === "template") && (
          <div className="space-y-1">
            <div className="text-[10px] text-muted-foreground font-medium">
              {transformType === "extract" ? "Field Path:" : "Template:"}
            </div>
            <InlineInput
              value={
                transformType === "extract"
                  ? nodeData.field || ""
                  : nodeData.template || ""
              }
              onChange={(value) =>
                updateNodeData(
                  id,
                  transformType === "extract"
                    ? { field: value }
                    : { template: value }
                )
              }
              placeholder={
                transformType === "extract"
                  ? "e.g., data.user.name"
                  : "e.g., Hello {{name}}"
              }
              className="w-full"
              inputClassName="text-xs font-mono"
              displayClassName="text-xs bg-muted/50 hover:bg-muted min-h-[28px] font-mono"
              emptyText={
                transformType === "extract"
                  ? "Click to add field path..."
                  : "Click to add template..."
              }
              disabled={isProcessing}
            />
          </div>
        )}

        {/* Error Display */}
        {nodeData.error && (
          <div className="text-[10px] text-red-500 bg-red-50 dark:bg-red-950/30 p-2 rounded">
            {nodeData.error}
          </div>
        )}
      </div>

      {/* Transformed data output handle with visual indicator */}
      <div className="absolute -right-2 top-1/2 -translate-y-1/2 group">
        <Handle
          type="source"
          position={Position.Right}
          id="output"
          className="!static !transform-none !w-4 !h-4 !bg-background !border-2 !border-yellow-500 !rounded-full hover:!border-yellow-600 transition-all hover:!scale-110"
          title="Transformed output: Processed data"
        />
        {/* Outer glow ring */}
        <div className="absolute inset-0 -z-10 w-4 h-4 rounded-full bg-yellow-500/30 group-hover:bg-yellow-500/50 transition-colors" />
        {/* Pulsing indicator ring on hover */}
        <div className="absolute -inset-1 -z-20 w-6 h-6 -left-1 -top-1 rounded-full border-2 border-yellow-400/50 opacity-0 group-hover:opacity-100 group-hover:animate-ping transition-opacity" />
      </div>
    </div>
  );
});
