"use client";

import React, { memo } from "react";
import { Handle, Position, NodeProps } from "@xyflow/react";
import { ArrowRightCircle } from "lucide-react";
import ReactMarkdown from "react-markdown";
import { useFlowStore } from "@/stores/flowStore";
import { cn } from "@/lib/utils";
import { CodeBlock } from "../code-block";
import { NodeStatusIndicator, type NodeStatus } from "../node-status-indicator";
import {
  InlineSelect,
  type InlineSelectOption,
} from "../inline-editors";

interface OutputNodeData {
  label?: string;
  format?: "text" | "json" | "markdown" | "code";
  result?: string;
  status?: "idle" | "completed" | "error" | "pending" | "running";
  error?: string;
  isPreview?: boolean;
  codeLanguage?: string;
}

// Output format options
const OUTPUT_FORMAT_OPTIONS: InlineSelectOption[] = [
  { value: "text", label: "Text" },
  { value: "json", label: "JSON" },
  { value: "markdown", label: "Markdown" },
  { value: "code", label: "Code" },
];

/**
 * OutputNode - Endpoint of a workflow.
 * Returns the final result with syntax highlighting and markdown support.
 */
export const OutputNode = memo(function OutputNode({
  data,
  selected,
  id,
}: NodeProps) {
  const nodeData = data as OutputNodeData;
  const isPreview = nodeData.isPreview;

  const liveUsers = useFlowStore((state) => state.liveUsers);
  const updateNodeData = useFlowStore((state) => state.updateNodeData);
  const collaborators = Object.values(liveUsers).filter(
    (u) => u.activeNodeId === id
  );

  // Disable editing when node is processing
  const isProcessing =
    nodeData.status === "pending" ||
    nodeData.status === "running" ||
    nodeData.status === "completed";

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

  // Determine display status for indicator
  const displayStatus: NodeStatus =
    nodeData.status === "error"
      ? "error"
      : nodeData.status === "completed" || nodeData.result
      ? "completed"
      : nodeData.status === "running"
      ? "running"
      : nodeData.status === "pending"
      ? "pending"
      : "idle";

  return (
    <div
      className={cn(
        "relative min-w-[280px] rounded-xl border-2 bg-background shadow-lg transition-all duration-300",
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
      <div className="bg-gradient-to-r from-blue-600 to-cyan-600 px-4 py-2 text-white flex items-center justify-between rounded-t-[10px]">
        <div className="flex items-center gap-2">
          <ArrowRightCircle className="w-4 h-4" />
          <span className="font-bold text-xs uppercase tracking-wider">
            {nodeData.label || "Output Result"}
          </span>
        </div>
        <div className="flex items-center gap-2">
          <NodeStatusIndicator
            status={displayStatus}
            size="sm"
            className="[&_svg]:text-white/80 [&_div]:bg-white/20"
          />
          <InlineSelect
            value={nodeData.format || "text"}
            onChange={(value) =>
              updateNodeData(id, {
                format: value as "text" | "json" | "markdown" | "code",
              })
            }
            options={OUTPUT_FORMAT_OPTIONS}
            placeholder="Select format..."
            className="min-w-[80px]"
            selectClassName="text-[10px] h-6"
            displayClassName="text-[10px] bg-white/20 hover:bg-white/30 px-1.5 py-0.5 min-h-[22px] font-mono uppercase border-white/20"
            disabled={isProcessing}
          />
        </div>
      </div>

      {/* Final result input handle with visual indicator */}
      <div className="absolute -left-2 top-1/2 -translate-y-1/2 group">
        <Handle
          type="target"
          position={Position.Left}
          id="input"
          className="!static !transform-none !w-4 !h-4 !bg-background !border-2 !border-blue-500 !rounded-full hover:!border-blue-600 transition-all hover:!scale-110"
          title="Final result input: Any data type"
        />
        {/* Outer glow ring */}
        <div className="absolute inset-0 -z-10 w-4 h-4 rounded-full bg-blue-500/30 group-hover:bg-blue-500/50 transition-colors" />
        {/* Pulsing indicator ring on hover */}
        <div className="absolute -inset-1 -z-20 w-6 h-6 -left-1 -top-1 rounded-full border-2 border-blue-400/50 opacity-0 group-hover:opacity-100 group-hover:animate-ping transition-opacity" />
      </div>

      <div className="p-4">
        {nodeData.status === "error" ? (
          <div className="bg-destructive/10 text-destructive text-xs p-3 rounded-lg border border-destructive/20">
            <strong>Error:</strong> {nodeData.error || "Execution failed"}
          </div>
        ) : nodeData.result ? (
          <div className="max-h-[300px] overflow-y-auto">
            {nodeData.format === "json" || nodeData.format === "code" ? (
              <CodeBlock
                code={
                  typeof nodeData.result === "string"
                    ? nodeData.result
                    : JSON.stringify(nodeData.result, null, 2)
                }
                language={
                  nodeData.format === "json" ? "json" : nodeData.codeLanguage
                }
                maxHeight={280}
              />
            ) : nodeData.format === "markdown" || !nodeData.format ? (
              <div className="prose prose-sm dark:prose-invert max-w-none">
                <ReactMarkdown
                  components={{
                    // Custom code block rendering with syntax highlighting
                    code({ node, className, children, ...props }) {
                      const match = /language-(\w+)/.exec(className || "");
                      const isInline = !match && !className;
                      const code = String(children).replace(/\n$/, "");

                      if (isInline) {
                        return (
                          <code
                            className="px-1.5 py-0.5 rounded bg-muted text-[0.875em] font-mono"
                            {...props}
                          >
                            {children}
                          </code>
                        );
                      }

                      return (
                        <CodeBlock
                          code={code}
                          language={match ? match[1] : undefined}
                          className="my-3"
                        />
                      );
                    },
                    // Enhanced pre handling
                    pre({ children }) {
                      return <>{children}</>;
                    },
                  }}
                >
                  {nodeData.result}
                </ReactMarkdown>
              </div>
            ) : (
              <div className="text-sm whitespace-pre-wrap leading-relaxed">
                {nodeData.result}
              </div>
            )}
          </div>
        ) : displayStatus === "running" || displayStatus === "pending" ? (
          <div className="flex flex-col items-center justify-center py-8">
            <NodeStatusIndicator status={displayStatus} size="lg" showLabel />
          </div>
        ) : (
          <div className="flex flex-col items-center justify-center py-8 opacity-30 grayscale">
            <ArrowRightCircle className="w-8 h-8 mb-2" />
            <span className="text-xs">等待输出结果</span>
          </div>
        )}
      </div>
    </div>
  );
});
