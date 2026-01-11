"use client";

import { useState } from "react";
import Link from "next/link";
import { useRequireAuth } from "@/hooks/useRequireAuth";
import { useMyExecutions } from "@/hooks/useAgentApi";
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
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import {
  History,
  ArrowLeft,
  Loader2,
  CheckCircle2,
  XCircle,
  Clock,
  Square,
  ExternalLink,
  Filter,
} from "lucide-react";

const STATUS_CONFIG = {
  pending: {
    icon: Clock,
    color: "text-yellow-500",
    label: "等待中",
    variant: "secondary" as const,
  },
  running: {
    icon: Loader2,
    color: "text-blue-500",
    label: "执行中",
    variant: "default" as const,
    animate: true,
  },
  completed: {
    icon: CheckCircle2,
    color: "text-green-500",
    label: "成功",
    variant: "default" as const,
  },
  failed: {
    icon: XCircle,
    color: "text-red-500",
    label: "失败",
    variant: "destructive" as const,
  },
  cancelled: {
    icon: Square,
    color: "text-gray-500",
    label: "已取消",
    variant: "secondary" as const,
  },
};

export default function ExecutionsPage() {
  const { isLoading: authLoading } = useRequireAuth();
  const [statusFilter, setStatusFilter] = useState<string>("all");
  const [page, setPage] = useState(1);
  const limit = 20;

  const { data: executions, isLoading } = useMyExecutions({
    page,
    limit,
    status: statusFilter !== "all" ? statusFilter : undefined,
  });

  if (authLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
      </div>
    );
  }

  const formatDuration = (start: string, end?: string) => {
    const startTime = new Date(start).getTime();
    const endTime = end ? new Date(end).getTime() : Date.now();
    const duration = endTime - startTime;

    if (duration < 1000) return `${duration}ms`;
    if (duration < 60000) return `${(duration / 1000).toFixed(1)}s`;
    return `${Math.floor(duration / 60000)}m ${Math.floor((duration % 60000) / 1000)}s`;
  };

  return (
    <div className="container mx-auto py-8 px-4 max-w-6xl">
      {/* Header */}
      <div className="flex items-center gap-4 mb-6">
        <Button variant="ghost" size="icon" asChild>
          <Link href="/dashboard">
            <ArrowLeft className="h-5 w-5" />
          </Link>
        </Button>
        <div className="flex-1">
          <h1 className="text-2xl font-bold">执行历史</h1>
          <p className="text-muted-foreground">查看所有工作流的执行记录</p>
        </div>
      </div>

      {/* Filters */}
      <div className="flex items-center gap-4 mb-6">
        <div className="flex items-center gap-2">
          <Filter className="h-4 w-4 text-muted-foreground" />
          <span className="text-sm text-muted-foreground">状态筛选：</span>
        </div>
        <Select value={statusFilter} onValueChange={setStatusFilter}>
          <SelectTrigger className="w-32">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">全部</SelectItem>
            <SelectItem value="completed">成功</SelectItem>
            <SelectItem value="failed">失败</SelectItem>
            <SelectItem value="running">执行中</SelectItem>
            <SelectItem value="pending">等待中</SelectItem>
            <SelectItem value="cancelled">已取消</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {/* Executions Table */}
      <Card>
        <CardHeader>
          <CardTitle>执行记录</CardTitle>
          <CardDescription>
            共 {executions?.length || 0} 条记录
          </CardDescription>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="space-y-4">
              {[1, 2, 3, 4, 5].map((i) => (
                <Skeleton key={i} className="h-16 w-full" />
              ))}
            </div>
          ) : executions && executions.length > 0 ? (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>执行 ID</TableHead>
                  <TableHead>状态</TableHead>
                  <TableHead>耗时</TableHead>
                  <TableHead>开始时间</TableHead>
                  <TableHead className="text-right">操作</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {executions.map((execution) => {
                  const status =
                    STATUS_CONFIG[
                      execution.status as keyof typeof STATUS_CONFIG
                    ];
                  const StatusIcon = status?.icon || Clock;

                  return (
                    <TableRow key={execution.id}>
                      <TableCell className="font-mono text-sm">
                        {execution.id.slice(0, 8)}...
                      </TableCell>
                      <TableCell>
                        <Badge variant={status?.variant} className="gap-1">
                          <StatusIcon
                            className={`h-3 w-3 ${status?.color} ${
                              status?.animate ? "animate-spin" : ""
                            }`}
                          />
                          {status?.label}
                        </Badge>
                      </TableCell>
                      <TableCell className="text-muted-foreground">
                        {formatDuration(
                          execution.created_at,
                          execution.completed_at
                        )}
                      </TableCell>
                      <TableCell className="text-muted-foreground">
                        {new Date(execution.created_at).toLocaleString("zh-CN")}
                      </TableCell>
                      <TableCell className="text-right">
                        <Button variant="ghost" size="sm" asChild>
                          <Link href={`/dashboard/executions/${execution.id}`}>
                            <ExternalLink className="h-4 w-4" />
                          </Link>
                        </Button>
                      </TableCell>
                    </TableRow>
                  );
                })}
              </TableBody>
            </Table>
          ) : (
            <div className="flex flex-col items-center justify-center py-16">
              <History className="h-16 w-16 text-muted-foreground mb-4" />
              <h3 className="text-lg font-medium mb-2">暂无执行记录</h3>
              <p className="text-muted-foreground mb-6 text-center max-w-sm">
                运行您的 Agent 工作流后，执行记录将显示在这里
              </p>
              <Button asChild>
                <Link href="/agents/gallery">浏览 Agent 广场</Link>
              </Button>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Pagination */}
      {executions && executions.length >= limit && (
        <div className="flex justify-center gap-2 mt-6">
          <Button
            variant="outline"
            disabled={page === 1}
            onClick={() => setPage((p) => Math.max(1, p - 1))}
          >
            上一页
          </Button>
          <Button variant="outline" disabled>
            第 {page} 页
          </Button>
          <Button
            variant="outline"
            onClick={() => setPage((p) => p + 1)}
          >
            下一页
          </Button>
        </div>
      )}
    </div>
  );
}
