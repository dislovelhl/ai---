"use client";

import React, { memo } from "react";
import { Handle, Position, NodeProps } from "@xyflow/react";
import { Terminal } from "lucide-react";
import { useFlowStore } from "@/stores/flowStore";
import { cn } from "@/lib/utils";
import { NodeStatusIndicator, type NodeStatus } from "../node-status-indicator";
import {
  InlineSelect,
  InlineInput,
  type InlineSelectOption,
} from "../inline-editors";

interface InputNodeData {
  label?: string;
  inputType?: "text" | "number" | "json" | "file";
  default?: string;
  isPreview?: boolean;
  status?: "idle" | "ready" | "pending" | "completed";
  value?: string;
}

// Input type options
const INPUT_TYPE_OPTIONS: InlineSelectOption[] = [
  { value: "text", label: "Text" },
  { value: "number", label: "Number" },
  { value: "json", label: "JSON" },
  { value: "file", label: "File" },
];

/**
 * InputNode - Starting point of a workflow.
 * Receives user input or default values with status indicator.
 */
export const InputNode = memo(function InputNode({
  data,
  selected,
  id,
}: NodeProps) {
  const nodeData = data as InputNodeData;
  const liveUsers = useFlowStore((state) => state.liveUsers);
  const updateNodeData = useFlowStore((state) => state.updateNodeData);
  const collaborators = Object.values(liveUsers).filter(
    (u) => u.activeNodeId === id
  );

  // Disable editing when node is processing
  const isProcessing =
    nodeData.status === "pending" || nodeData.status === "completed";

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

  // Determine display status
  const displayStatus: NodeStatus = (() => {
    if (nodeData.status === "completed" || nodeData.value) return "completed";
    if (nodeData.status === "pending") return "pending";
    if (nodeData.status === "ready") return "idle";
    return "idle";
  })();

  return (
    <div
      className={cn(
        "relative min-w-[200px] rounded-xl border-2 bg-background shadow-lg transition-all duration-300",
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
      <div className="bg-emerald-600 px-4 py-2 text-white rounded-t-[10px] flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Terminal className="w-4 h-4" />
          <span className="font-bold text-xs uppercase tracking-wider">
            {nodeData.label || "Input"}
          </span>
        </div>
        <NodeStatusIndicator
          status={displayStatus}
          size="sm"
          className="[&_svg]:text-white/80 [&_div]:bg-white/20"
        />
      </div>

      <div className="p-4 space-y-3">
        {/* Input Type Selection */}
        <div className="space-y-1">
          <div className="flex items-center justify-between gap-2">
            <span className="text-[10px] text-muted-foreground font-medium">
              Type:
            </span>
            <InlineSelect
              value={nodeData.inputType || "text"}
              onChange={(value) =>
                updateNodeData(id, {
                  inputType: value as "text" | "number" | "json" | "file",
                })
              }
              options={INPUT_TYPE_OPTIONS}
              placeholder="Select type..."
              className="flex-1"
              selectClassName="text-[10px]"
              displayClassName="text-[10px] bg-muted/50 hover:bg-muted"
              disabled={isProcessing}
            />
          </div>
        </div>

        {/* Default Value Input */}
        <div className="space-y-1">
          <div className="text-[10px] text-muted-foreground font-medium">
            Default Value:
          </div>
          <InlineInput
            value={nodeData.default || ""}
            onChange={(value) => updateNodeData(id, { default: value })}
            placeholder={
              nodeData.inputType === "json"
                ? '{"key": "value"}'
                : "Enter default value..."
            }
            className="w-full"
            inputClassName="text-xs"
            displayClassName="text-xs bg-muted/50 hover:bg-muted min-h-[28px]"
            emptyText="Click to add default..."
            disabled={isProcessing}
          />
        </div>

        {/* Current Value Display */}
        {nodeData.value && (
          <div className="pt-2 border-t">
            <div className="text-[10px] text-muted-foreground font-medium mb-1">
              Current Value:
            </div>
            <div className="text-xs bg-emerald-50 dark:bg-emerald-950/30 p-2 rounded border border-emerald-200 dark:border-emerald-800 truncate max-w-[180px]">
              {nodeData.value}
            </div>
          </div>
        )}
      </div>

      {/* Data output handle with visual indicator */}
      <div className="absolute -right-2 top-1/2 -translate-y-1/2 group">
        <Handle
          type="source"
          position={Position.Right}
          id="data"
          className="!static !transform-none !w-4 !h-4 !bg-background !border-2 !border-blue-500 !rounded-full hover:!border-blue-600 transition-all hover:!scale-110"
          title="Data output: Text, JSON, or numbers"
        />
        {/* Outer glow ring */}
        <div className="absolute inset-0 -z-10 w-4 h-4 rounded-full bg-blue-500/30 group-hover:bg-blue-500/50 transition-colors" />
        {/* Pulsing indicator ring on hover */}
        <div className="absolute -inset-1 -z-20 w-6 h-6 -left-1 -top-1 rounded-full border-2 border-blue-400/50 opacity-0 group-hover:opacity-100 group-hover:animate-ping transition-opacity" />
      </div>
    </div>
  );
});
