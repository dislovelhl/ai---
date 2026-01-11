"use client";

import { useEffect } from "react";
import { AgentExecution } from "@/lib/types";
import { useExecution, useCancelExecution } from "@/hooks/useAgentApi";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from "@/components/ui/collapsible";
import {
  CheckCircle2,
  XCircle,
  Loader2,
  Clock,
  ChevronDown,
  ChevronUp,
  Square,
  Play,
  AlertCircle,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { useState } from "react";

interface ExecutionStatusProps {
  executionId: string;
  showDetails?: boolean;
  onComplete?: (execution: AgentExecution) => void;
}

const STATUS_CONFIG = {
  pending: {
    icon: Clock,
    color: "text-yellow-500",
    bgColor: "bg-yellow-500/10",
    label: "等待中",
    description: "任务正在排队等待执行",
  },
  running: {
    icon: Loader2,
    color: "text-blue-500",
    bgColor: "bg-blue-500/10",
    label: "执行中",
    description: "任务正在执行",
    animate: true,
  },
  completed: {
    icon: CheckCircle2,
    color: "text-green-500",
    bgColor: "bg-green-500/10",
    label: "已完成",
    description: "任务执行成功",
  },
  failed: {
    icon: XCircle,
    color: "text-red-500",
    bgColor: "bg-red-500/10",
    label: "失败",
    description: "任务执行失败",
  },
  cancelled: {
    icon: Square,
    color: "text-gray-500",
    bgColor: "bg-gray-500/10",
    label: "已取消",
    description: "任务已被取消",
  },
};

export function ExecutionStatus({
  executionId,
  showDetails = true,
  onComplete,
}: ExecutionStatusProps) {
  const { data: execution, isLoading, error } = useExecution(executionId);
  const cancelMutation = useCancelExecution();
  const [isExpanded, setIsExpanded] = useState(false);

  useEffect(() => {
    if (
      execution &&
      (execution.status === "completed" || execution.status === "failed")
    ) {
      onComplete?.(execution);
    }
  }, [execution, onComplete]);

  if (isLoading) {
    return (
      <Card>
        <CardContent className="flex items-center justify-center py-8">
          <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
        </CardContent>
      </Card>
    );
  }

  if (error || !execution) {
    return (
      <Card>
        <CardContent className="flex items-center justify-center py-8 text-destructive">
          <AlertCircle className="h-5 w-5 mr-2" />
          无法加载执行状态
        </CardContent>
      </Card>
    );
  }

  const status = STATUS_CONFIG[execution.status as keyof typeof STATUS_CONFIG];
  const StatusIcon = status?.icon || AlertCircle;
  const isRunning = execution.status === "running";
  const canCancel = isRunning || execution.status === "pending";

  // Calculate progress based on execution logs
  const logs = execution.execution_log || [];
  const totalSteps = logs.length;
  const completedSteps = logs.filter(
    (log: { status?: string }) => log.status === "completed"
  ).length;
  const progress =
    totalSteps > 0 ? Math.round((completedSteps / totalSteps) * 100) : 0;

  const handleCancel = () => {
    if (canCancel) {
      cancelMutation.mutate(executionId);
    }
  };

  const formatDuration = (start: string, end?: string) => {
    const startTime = new Date(start).getTime();
    const endTime = end ? new Date(end).getTime() : Date.now();
    const duration = endTime - startTime;

    if (duration < 1000) return `${duration}ms`;
    if (duration < 60000) return `${(duration / 1000).toFixed(1)}s`;
    return `${Math.floor(duration / 60000)}m ${Math.floor((duration % 60000) / 1000)}s`;
  };

  return (
    <Card>
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className={cn("p-2 rounded-full", status?.bgColor)}>
              <StatusIcon
                className={cn(
                  "h-5 w-5",
                  status?.color,
                  status?.animate && "animate-spin"
                )}
              />
            </div>
            <div>
              <CardTitle className="text-lg">{status?.label}</CardTitle>
              <CardDescription>{status?.description}</CardDescription>
            </div>
          </div>
          <div className="flex items-center gap-2">
            {canCancel && (
              <Button
                variant="destructive"
                size="sm"
                onClick={handleCancel}
                disabled={cancelMutation.isPending}
              >
                {cancelMutation.isPending ? (
                  <Loader2 className="h-4 w-4 animate-spin" />
                ) : (
                  <Square className="h-4 w-4" />
                )}
                <span className="ml-2">取消</span>
              </Button>
            )}
            <Badge variant="outline">
              {formatDuration(execution.created_at, execution.completed_at)}
            </Badge>
          </div>
        </div>
      </CardHeader>

      <CardContent className="space-y-4">
        {isRunning && (
          <div className="space-y-2">
            <div className="flex justify-between text-sm">
              <span className="text-muted-foreground">进度</span>
              <span className="font-medium">{progress}%</span>
            </div>
            <Progress value={progress} className="h-2" />
          </div>
        )}

        {showDetails && logs.length > 0 && (
          <Collapsible open={isExpanded} onOpenChange={setIsExpanded}>
            <CollapsibleTrigger asChild>
              <Button variant="ghost" className="w-full justify-between">
                <span>执行日志 ({logs.length} 步)</span>
                {isExpanded ? (
                  <ChevronUp className="h-4 w-4" />
                ) : (
                  <ChevronDown className="h-4 w-4" />
                )}
              </Button>
            </CollapsibleTrigger>
            <CollapsibleContent className="mt-2">
              <div className="space-y-2 max-h-64 overflow-y-auto">
                {logs.map(
                  (
                    log: {
                      node_id?: string;
                      node_type?: string;
                      status?: string;
                      output?: unknown;
                      error?: string;
                      timestamp?: string;
                    },
                    index: number
                  ) => (
                    <div
                      key={index}
                      className="flex items-start gap-3 p-3 rounded-lg bg-muted/50 text-sm"
                    >
                      <div className="flex-shrink-0 mt-0.5">
                        {log.status === "completed" ? (
                          <CheckCircle2 className="h-4 w-4 text-green-500" />
                        ) : log.status === "failed" ? (
                          <XCircle className="h-4 w-4 text-red-500" />
                        ) : log.status === "running" ? (
                          <Loader2 className="h-4 w-4 text-blue-500 animate-spin" />
                        ) : (
                          <Clock className="h-4 w-4 text-muted-foreground" />
                        )}
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2">
                          <span className="font-medium">{log.node_id}</span>
                          <Badge variant="secondary" className="text-xs">
                            {log.node_type}
                          </Badge>
                        </div>
                        {log.output && (
                          <pre className="mt-1 text-xs text-muted-foreground overflow-x-auto">
                            {typeof log.output === "string"
                              ? log.output
                              : JSON.stringify(log.output, null, 2)}
                          </pre>
                        )}
                        {log.error && (
                          <p className="mt-1 text-xs text-destructive">
                            {log.error}
                          </p>
                        )}
                      </div>
                      {log.timestamp && (
                        <span className="text-xs text-muted-foreground flex-shrink-0">
                          {new Date(log.timestamp).toLocaleTimeString()}
                        </span>
                      )}
                    </div>
                  )
                )}
              </div>
            </CollapsibleContent>
          </Collapsible>
        )}

        {execution.status === "completed" && execution.output_data && (
          <div className="p-4 rounded-lg bg-green-500/10 border border-green-500/20">
            <h4 className="font-medium text-green-700 dark:text-green-400 mb-2">
              输出结果
            </h4>
            <pre className="text-sm overflow-x-auto">
              {typeof execution.output_data === "string"
                ? execution.output_data
                : JSON.stringify(execution.output_data, null, 2)}
            </pre>
          </div>
        )}

        {execution.status === "failed" && execution.error_message && (
          <div className="p-4 rounded-lg bg-red-500/10 border border-red-500/20">
            <h4 className="font-medium text-red-700 dark:text-red-400 mb-2">
              错误信息
            </h4>
            <p className="text-sm">{execution.error_message}</p>
          </div>
        )}
      </CardContent>
    </Card>
  );
}

// Compact version for lists
export function ExecutionStatusBadge({
  status,
}: {
  status: string;
}) {
  const config = STATUS_CONFIG[status as keyof typeof STATUS_CONFIG];
  const StatusIcon = config?.icon || AlertCircle;

  return (
    <Badge
      variant="outline"
      className={cn("gap-1", config?.color)}
    >
      <StatusIcon
        className={cn("h-3 w-3", config?.animate && "animate-spin")}
      />
      {config?.label || status}
    </Badge>
  );
}

// Run workflow button with execution tracking
interface RunWorkflowButtonProps {
  workflowId: string;
  input?: Record<string, unknown>;
  onExecutionStart?: (executionId: string) => void;
  disabled?: boolean;
  className?: string;
}

export function RunWorkflowButton({
  workflowId,
  input = {},
  onExecutionStart,
  disabled,
  className,
}: RunWorkflowButtonProps) {
  const [isRunning, setIsRunning] = useState(false);

  const handleRun = async () => {
    setIsRunning(true);
    try {
      const { runWorkflow } = await import("@/lib/api");
      const execution = await runWorkflow(workflowId, input);
      onExecutionStart?.(execution.id);
    } catch (error) {
      console.error("Failed to run workflow:", error);
    } finally {
      setIsRunning(false);
    }
  };

  return (
    <Button
      onClick={handleRun}
      disabled={disabled || isRunning}
      className={className}
    >
      {isRunning ? (
        <>
          <Loader2 className="mr-2 h-4 w-4 animate-spin" />
          启动中...
        </>
      ) : (
        <>
          <Play className="mr-2 h-4 w-4" />
          运行
        </>
      )}
    </Button>
  );
}
