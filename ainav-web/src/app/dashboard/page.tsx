"use client";

import { useEffect } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useAuth } from "@/stores/authStore";
import {
  useMyWorkflows,
  useMyExecutions,
  useMySessions,
} from "@/hooks/useAgentApi";
import { useUserUsage } from "@/hooks/useUserApi";
import { UsageStats } from "@/components/dashboard/UsageStats";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Workflow,
  History,
  MessageSquare,
  Plus,
  ArrowRight,
  Settings,
  Clock,
  CheckCircle2,
  XCircle,
  Loader2,
} from "lucide-react";

export default function DashboardPage() {
  const { user, isAuthenticated, isLoading: authLoading } = useAuth();
  const router = useRouter();

  const { data: workflows, isLoading: workflowsLoading } = useMyWorkflows();
  const { data: executions, isLoading: executionsLoading } = useMyExecutions({
    limit: 5,
  });
  const { data: sessions, isLoading: sessionsLoading } = useMySessions();
  const { data: usageStats, isLoading: usageLoading } = useUserUsage();

  useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      router.push("/login");
    }
  }, [authLoading, isAuthenticated, router]);

  if (authLoading || !isAuthenticated) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
      </div>
    );
  }

  const getExecutionStatusIcon = (status: string) => {
    switch (status) {
      case "completed":
        return <CheckCircle2 className="h-4 w-4 text-green-500" />;
      case "failed":
        return <XCircle className="h-4 w-4 text-red-500" />;
      case "running":
        return <Loader2 className="h-4 w-4 text-blue-500 animate-spin" />;
      default:
        return <Clock className="h-4 w-4 text-yellow-500" />;
    }
  };

  return (
    <div className="container mx-auto py-8 px-4 max-w-7xl">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 mb-8">
        <div>
          <h1 className="text-3xl font-bold">
            欢迎回来，{user?.username}
          </h1>
          <p className="text-muted-foreground mt-1">
            管理您的 Agent 工作流和执行历史
          </p>
        </div>
        <div className="flex gap-3">
          <Button variant="outline" asChild>
            <Link href="/dashboard/settings">
              <Settings className="mr-2 h-4 w-4" />
              设置
            </Link>
          </Button>
          <Button asChild>
            <Link href="/studio">
              <Plus className="mr-2 h-4 w-4" />
              创建 Agent
            </Link>
          </Button>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              我的 Agent
            </CardTitle>
            <Workflow className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">
              {workflowsLoading ? (
                <Skeleton className="h-9 w-12" />
              ) : (
                workflows?.length || 0
              )}
            </div>
            <p className="text-xs text-muted-foreground mt-1">
              已创建的工作流
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              执行次数
            </CardTitle>
            <History className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">
              {executionsLoading ? (
                <Skeleton className="h-9 w-12" />
              ) : (
                executions?.length || 0
              )}
            </div>
            <p className="text-xs text-muted-foreground mt-1">
              最近执行记录
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              对话会话
            </CardTitle>
            <MessageSquare className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">
              {sessionsLoading ? (
                <Skeleton className="h-9 w-12" />
              ) : (
                sessions?.length || 0
              )}
            </div>
            <p className="text-xs text-muted-foreground mt-1">
              活跃的 Agent 会话
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Usage Stats */}
      <div className="mb-8">
        <UsageStats
          data={usageStats || {
            limit: 0,
            used: 0,
            remaining: 0,
            reset_at: new Date().toISOString(),
            reset_at_timestamp: Date.now() / 1000,
            tier: "free",
            window_seconds: 86400
          }}
          isLoading={usageLoading}
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* My Workflows */}
        <Card>
          <CardHeader className="flex flex-row items-center justify-between">
            <div>
              <CardTitle>我的 Agent</CardTitle>
              <CardDescription>您创建的工作流</CardDescription>
            </div>
            <Button variant="ghost" size="sm" asChild>
              <Link href="/dashboard/workflows">
                查看全部
                <ArrowRight className="ml-2 h-4 w-4" />
              </Link>
            </Button>
          </CardHeader>
          <CardContent>
            {workflowsLoading ? (
              <div className="space-y-3">
                {[1, 2, 3].map((i) => (
                  <Skeleton key={i} className="h-16 w-full" />
                ))}
              </div>
            ) : workflows && workflows.length > 0 ? (
              <div className="space-y-3">
                {workflows.slice(0, 5).map((workflow) => (
                  <Link
                    key={workflow.id}
                    href={`/studio?id=${workflow.id}`}
                    className="flex items-center justify-between p-3 rounded-lg border hover:bg-muted/50 transition-colors"
                  >
                    <div className="flex items-center gap-3">
                      <div className="p-2 rounded-lg bg-primary/10">
                        <Workflow className="h-4 w-4 text-primary" />
                      </div>
                      <div>
                        <p className="font-medium">{workflow.name}</p>
                        <p className="text-xs text-muted-foreground">
                          {workflow.description || "暂无描述"}
                        </p>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      {workflow.is_public && (
                        <Badge variant="secondary">公开</Badge>
                      )}
                      <Badge variant="outline">v{workflow.version}</Badge>
                    </div>
                  </Link>
                ))}
              </div>
            ) : (
              <div className="text-center py-8">
                <Workflow className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
                <p className="text-muted-foreground mb-4">
                  还没有创建任何 Agent
                </p>
                <Button asChild>
                  <Link href="/studio">
                    <Plus className="mr-2 h-4 w-4" />
                    创建第一个 Agent
                  </Link>
                </Button>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Recent Executions */}
        <Card>
          <CardHeader className="flex flex-row items-center justify-between">
            <div>
              <CardTitle>执行历史</CardTitle>
              <CardDescription>最近的工作流执行</CardDescription>
            </div>
            <Button variant="ghost" size="sm" asChild>
              <Link href="/dashboard/executions">
                查看全部
                <ArrowRight className="ml-2 h-4 w-4" />
              </Link>
            </Button>
          </CardHeader>
          <CardContent>
            {executionsLoading ? (
              <div className="space-y-3">
                {[1, 2, 3].map((i) => (
                  <Skeleton key={i} className="h-16 w-full" />
                ))}
              </div>
            ) : executions && executions.length > 0 ? (
              <div className="space-y-3">
                {executions.slice(0, 5).map((execution) => (
                  <div
                    key={execution.id}
                    className="flex items-center justify-between p-3 rounded-lg border"
                  >
                    <div className="flex items-center gap-3">
                      {getExecutionStatusIcon(execution.status)}
                      <div>
                        <p className="font-medium text-sm">
                          执行 #{execution.id.slice(0, 8)}
                        </p>
                        <p className="text-xs text-muted-foreground">
                          {new Date(execution.created_at).toLocaleString(
                            "zh-CN"
                          )}
                        </p>
                      </div>
                    </div>
                    <Badge
                      variant={
                        execution.status === "completed"
                          ? "default"
                          : execution.status === "failed"
                          ? "destructive"
                          : "secondary"
                      }
                    >
                      {execution.status === "completed"
                        ? "成功"
                        : execution.status === "failed"
                        ? "失败"
                        : execution.status === "running"
                        ? "运行中"
                        : "等待中"}
                    </Badge>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-8">
                <History className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
                <p className="text-muted-foreground">
                  还没有执行记录
                </p>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
