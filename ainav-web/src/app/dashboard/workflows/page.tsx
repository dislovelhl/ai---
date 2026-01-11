"use client";

import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useRequireAuth } from "@/hooks/useRequireAuth";
import {
  useMyWorkflows,
  useDeleteWorkflow,
} from "@/hooks/useAgentApi";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
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
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog";
import {
  Workflow,
  Plus,
  Search,
  MoreVertical,
  Edit,
  Trash2,
  Copy,
  Eye,
  Play,
  Star,
  Globe,
  Lock,
  ArrowLeft,
  Loader2,
} from "lucide-react";
import { toast } from "sonner";

export default function MyWorkflowsPage() {
  const { isLoading: authLoading } = useRequireAuth();
  const { data: workflows, isLoading } = useMyWorkflows();
  const deleteWorkflow = useDeleteWorkflow();
  const router = useRouter();

  const [searchQuery, setSearchQuery] = useState("");
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [workflowToDelete, setWorkflowToDelete] = useState<string | null>(null);

  if (authLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
      </div>
    );
  }

  const filteredWorkflows = workflows?.filter(
    (w) =>
      w.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      w.description?.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const handleDelete = async () => {
    if (!workflowToDelete) return;

    try {
      await deleteWorkflow.mutateAsync(workflowToDelete);
      toast.success("工作流已删除");
    } catch {
      toast.error("删除失败");
    } finally {
      setDeleteDialogOpen(false);
      setWorkflowToDelete(null);
    }
  };

  const confirmDelete = (id: string) => {
    setWorkflowToDelete(id);
    setDeleteDialogOpen(true);
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
          <h1 className="text-2xl font-bold">我的 Agent</h1>
          <p className="text-muted-foreground">管理您创建的所有工作流</p>
        </div>
        <Button asChild>
          <Link href="/studio">
            <Plus className="mr-2 h-4 w-4" />
            创建新 Agent
          </Link>
        </Button>
      </div>

      {/* Search */}
      <div className="relative mb-6">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
        <Input
          placeholder="搜索工作流..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="pl-10"
        />
      </div>

      {/* Workflows Grid */}
      {isLoading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {[1, 2, 3, 4, 5, 6].map((i) => (
            <Card key={i}>
              <CardHeader>
                <Skeleton className="h-6 w-3/4" />
                <Skeleton className="h-4 w-full" />
              </CardHeader>
              <CardContent>
                <Skeleton className="h-20 w-full" />
              </CardContent>
            </Card>
          ))}
        </div>
      ) : filteredWorkflows && filteredWorkflows.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filteredWorkflows.map((workflow) => (
            <Card key={workflow.id} className="group hover:shadow-md transition-shadow">
              <CardHeader className="pb-3">
                <div className="flex items-start justify-between">
                  <div className="flex items-center gap-2">
                    <div className="p-2 rounded-lg bg-primary/10">
                      <Workflow className="h-4 w-4 text-primary" />
                    </div>
                    <div>
                      <CardTitle className="text-base line-clamp-1">
                        {workflow.name}
                      </CardTitle>
                      <div className="flex items-center gap-2 mt-1">
                        {workflow.is_public ? (
                          <Badge variant="secondary" className="text-xs gap-1">
                            <Globe className="h-3 w-3" />
                            公开
                          </Badge>
                        ) : (
                          <Badge variant="outline" className="text-xs gap-1">
                            <Lock className="h-3 w-3" />
                            私有
                          </Badge>
                        )}
                        <Badge variant="outline" className="text-xs">
                          v{workflow.version}
                        </Badge>
                      </div>
                    </div>
                  </div>
                  <DropdownMenu>
                    <DropdownMenuTrigger asChild>
                      <Button
                        variant="ghost"
                        size="icon"
                        className="opacity-0 group-hover:opacity-100 transition-opacity"
                      >
                        <MoreVertical className="h-4 w-4" />
                      </Button>
                    </DropdownMenuTrigger>
                    <DropdownMenuContent align="end">
                      <DropdownMenuItem
                        onClick={() => router.push(`/studio?id=${workflow.id}`)}
                      >
                        <Edit className="mr-2 h-4 w-4" />
                        编辑
                      </DropdownMenuItem>
                      <DropdownMenuItem
                        onClick={() => router.push(`/agents/${workflow.id}`)}
                      >
                        <Eye className="mr-2 h-4 w-4" />
                        查看
                      </DropdownMenuItem>
                      <DropdownMenuItem
                        onClick={() => router.push(`/agents/${workflow.id}/chat`)}
                      >
                        <Play className="mr-2 h-4 w-4" />
                        运行
                      </DropdownMenuItem>
                      <DropdownMenuSeparator />
                      <DropdownMenuItem>
                        <Copy className="mr-2 h-4 w-4" />
                        复制
                      </DropdownMenuItem>
                      <DropdownMenuSeparator />
                      <DropdownMenuItem
                        onClick={() => confirmDelete(workflow.id)}
                        className="text-destructive focus:text-destructive"
                      >
                        <Trash2 className="mr-2 h-4 w-4" />
                        删除
                      </DropdownMenuItem>
                    </DropdownMenuContent>
                  </DropdownMenu>
                </div>
              </CardHeader>
              <CardContent>
                <CardDescription className="line-clamp-2 mb-4">
                  {workflow.description || "暂无描述"}
                </CardDescription>
                <div className="flex items-center justify-between text-xs text-muted-foreground">
                  <div className="flex items-center gap-3">
                    <span className="flex items-center gap-1">
                      <Play className="h-3 w-3" />
                      {workflow.run_count || 0} 次运行
                    </span>
                    <span className="flex items-center gap-1">
                      <Star className="h-3 w-3" />
                      {workflow.star_count || 0}
                    </span>
                  </div>
                  <span>
                    {new Date(workflow.updated_at).toLocaleDateString("zh-CN")}
                  </span>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      ) : (
        <Card>
          <CardContent className="flex flex-col items-center justify-center py-16">
            <Workflow className="h-16 w-16 text-muted-foreground mb-4" />
            <h3 className="text-lg font-medium mb-2">
              {searchQuery ? "没有找到匹配的工作流" : "还没有创建任何 Agent"}
            </h3>
            <p className="text-muted-foreground mb-6 text-center max-w-sm">
              {searchQuery
                ? "尝试使用不同的关键词搜索"
                : "创建您的第一个 Agent 工作流，开始自动化您的任务"}
            </p>
            {!searchQuery && (
              <Button asChild>
                <Link href="/studio">
                  <Plus className="mr-2 h-4 w-4" />
                  创建第一个 Agent
                </Link>
              </Button>
            )}
          </CardContent>
        </Card>
      )}

      {/* Delete Confirmation Dialog */}
      <AlertDialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>确认删除</AlertDialogTitle>
            <AlertDialogDescription>
              此操作将永久删除该工作流及其所有执行历史。此操作无法撤销。
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>取消</AlertDialogCancel>
            <AlertDialogAction
              onClick={handleDelete}
              className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
            >
              {deleteWorkflow.isPending ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                "删除"
              )}
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
}
