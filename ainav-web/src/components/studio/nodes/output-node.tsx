"use client";

import React, { memo } from "react";
import { Handle, Position, NodeProps } from "@xyflow/react";
import { ArrowRightCircle } from "lucide-react";
import ReactMarkdown from "react-markdown";
import { useFlowStore } from "@/stores/flowStore";
import { cn } from "@/lib/utils";
import { CodeBlock } from "../code-block";
import { NodeStatusIndicator, type NodeStatus } from "../node-status-indicator";

interface OutputNodeData {
  label?: string;
  format?: "text" | "json" | "markdown" | "code";
  result?: string;
  status?: "idle" | "completed" | "error" | "pending" | "running";
  error?: string;
  isPreview?: boolean;
  codeLanguage?: string;
}

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
          <div className="text-[10px] bg-white/20 px-1.5 py-0.5 rounded font-mono uppercase">
            {nodeData.format || "Auto"}
          </div>
        </div>
      </div>

      {/* Input handle */}
      <Handle
        type="target"
        position={Position.Left}
        className="!w-3 !h-3 !bg-background !border-2 !border-blue-600 !-left-1.5"
      />

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
