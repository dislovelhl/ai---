"use client";

import React from "react";
import { Check, X, Loader2, Clock, Circle } from "lucide-react";
import { cn } from "@/lib/utils";

export type NodeStatus =
  | "idle"
  | "pending"
  | "running"
  | "streaming"
  | "thinking"
  | "completed"
  | "error";

interface NodeStatusIndicatorProps {
  status: NodeStatus;
  size?: "sm" | "md" | "lg";
  showLabel?: boolean;
  className?: string;
}

const statusConfig: Record<
  NodeStatus,
  {
    icon: React.ElementType;
    color: string;
    bgColor: string;
    animate?: string;
    label: string;
  }
> = {
  idle: {
    icon: Circle,
    color: "text-muted-foreground",
    bgColor: "bg-muted",
    label: "空闲",
  },
  pending: {
    icon: Clock,
    color: "text-yellow-500",
    bgColor: "bg-yellow-500/10",
    animate: "animate-pulse",
    label: "等待中",
  },
  running: {
    icon: Loader2,
    color: "text-blue-500",
    bgColor: "bg-blue-500/10",
    animate: "animate-spin",
    label: "运行中",
  },
  streaming: {
    icon: Loader2,
    color: "text-violet-500",
    bgColor: "bg-violet-500/10",
    animate: "animate-spin",
    label: "流式输出",
  },
  thinking: {
    icon: Loader2,
    color: "text-purple-500",
    bgColor: "bg-purple-500/10",
    animate: "animate-spin",
    label: "思考中",
  },
  completed: {
    icon: Check,
    color: "text-green-500",
    bgColor: "bg-green-500/10",
    label: "完成",
  },
  error: {
    icon: X,
    color: "text-red-500",
    bgColor: "bg-red-500/10",
    label: "错误",
  },
};

const sizeConfig = {
  sm: {
    container: "w-4 h-4",
    icon: "w-2.5 h-2.5",
    label: "text-[9px]",
  },
  md: {
    container: "w-5 h-5",
    icon: "w-3 h-3",
    label: "text-[10px]",
  },
  lg: {
    container: "w-6 h-6",
    icon: "w-4 h-4",
    label: "text-xs",
  },
};

/**
 * NodeStatusIndicator - Visual indicator for node execution status.
 * Shows different icons and colors based on status.
 */
export function NodeStatusIndicator({
  status,
  size = "md",
  showLabel = false,
  className,
}: NodeStatusIndicatorProps) {
  const config = statusConfig[status];
  const sizes = sizeConfig[size];
  const Icon = config.icon;

  return (
    <div className={cn("flex items-center gap-1.5", className)}>
      <div
        className={cn(
          "flex items-center justify-center rounded-full",
          sizes.container,
          config.bgColor
        )}
      >
        <Icon className={cn(sizes.icon, config.color, config.animate)} />
      </div>
      {showLabel && (
        <span className={cn(sizes.label, config.color, "font-medium")}>
          {config.label}
        </span>
      )}
    </div>
  );
}

/**
 * NodeStatusBadge - A more prominent status badge with label
 */
export function NodeStatusBadge({
  status,
  className,
}: {
  status: NodeStatus;
  className?: string;
}) {
  const config = statusConfig[status];
  const Icon = config.icon;

  return (
    <div
      className={cn(
        "inline-flex items-center gap-1 px-1.5 py-0.5 rounded text-[10px] font-medium",
        config.bgColor,
        config.color,
        className
      )}
    >
      <Icon className={cn("w-3 h-3", config.animate)} />
      <span>{config.label}</span>
    </div>
  );
}
