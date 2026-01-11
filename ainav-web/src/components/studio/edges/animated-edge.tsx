"use client";

import React from "react";
import {
  BaseEdge,
  EdgeProps,
  getBezierPath,
  EdgeLabelRenderer,
} from "@xyflow/react";
import { Plus } from "lucide-react";
import { useFlowStore } from "@/stores/flowStore";

/**
 * AnimatedEdge - Custom edge with a "Packet" animation effect and hover detection.
 */
export function AnimatedEdge({
  id,
  sourceX,
  sourceY,
  targetX,
  targetY,
  sourcePosition,
  targetPosition,
  style = {},
  markerEnd,
  data,
}: EdgeProps) {
  const setHoveredEdge = useFlowStore((state) => state.setHoveredEdge);
  const showInsertionPreview = useFlowStore(
    (state) => state.showInsertionPreview
  );
  const commitPreview = useFlowStore((state) => state.commitPreview);
  const clearPreview = useFlowStore((state) => state.clearPreview);
  const isHovered = useFlowStore((state) => state.hoveredEdgeId === id);

  const [edgePath, labelX, labelY] = getBezierPath({
    sourceX,
    sourceY,
    sourcePosition,
    targetX,
    targetY,
    targetPosition,
  });

  const isAnimating = data?.isAnimating ?? false;

  return (
    <>
      <path
        d={edgePath}
        fill="none"
        stroke="transparent"
        strokeWidth={20}
        className="react-flow__edge-interaction"
        onMouseEnter={() => setHoveredEdge(id)}
        onMouseLeave={() => setHoveredEdge(null)}
        style={{ cursor: "pointer" }}
      />
      <BaseEdge
        path={edgePath}
        markerEnd={markerEnd}
        style={{
          ...style,
          strokeWidth: isHovered ? 3 : 2,
          stroke: isHovered
            ? "hsl(var(--primary))"
            : isAnimating
            ? "hsl(var(--primary))"
            : "hsl(var(--muted-foreground) / 0.3)",
          transition: "all 0.3s ease",
          filter: isHovered
            ? "drop-shadow(0 0 4px hsl(var(--primary) / 0.5))"
            : "none",
        }}
      />

      {isAnimating && (
        <g style={{ willChange: "transform" }}>
          <defs>
            <filter
              id={`glow-${id}`}
              x="-50%"
              y="-50%"
              width="200%"
              height="200%"
            >
              <feGaussianBlur stdDeviation="2" result="coloredBlur" />
              <feMerge>
                <feMergeNode in="coloredBlur" />
                <feMergeNode in="SourceGraphic" />
              </feMerge>
            </filter>
          </defs>
          <circle
            r="5"
            fill="hsl(var(--primary))"
            filter={`url(#glow-${id})`}
            style={{ willChange: "transform" }}
          >
            <animateMotion
              dur="1.2s"
              repeatCount="indefinite"
              path={edgePath}
              calcMode="linear"
            />
          </circle>
        </g>
      )}

      {(data?.label || isHovered) && (
        <EdgeLabelRenderer>
          <div
            style={{
              position: "absolute",
              transform: `translate(-50%, -50%) translate(${labelX}px,${labelY}px)`,
              pointerEvents: "all",
            }}
            className="flex flex-col items-center gap-2"
          >
            {isHovered && (
              <button
                className="w-6 h-6 rounded-full bg-primary text-primary-foreground shadow-lg flex items-center justify-center hover:scale-110 active:scale-95 transition-all duration-200 group"
                onClick={(e) => {
                  e.stopPropagation();
                  commitPreview();
                  setHoveredEdge(null);
                }}
                onMouseEnter={() => showInsertionPreview(id)}
                onMouseLeave={() => clearPreview()}
              >
                <Plus className="w-4 h-4" />
              </button>
            )}

            {data?.label && (
              <div className="bg-background/80 backdrop-blur-sm px-2 py-0.5 rounded border border-border shadow-sm text-[10px] font-bold text-muted-foreground whitespace-nowrap">
                {data.label}
              </div>
            )}
          </div>
        </EdgeLabelRenderer>
      )}
    </>
  );
}
