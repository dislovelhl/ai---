"use client";

import { Tool } from "@/lib/types";
import { AgentWorkflow } from "@/lib/types";
import {
  Card,
  CardContent,
  CardFooter,
  CardHeader,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Bot, Star, GitFork, Play, MessageSquare, Clock } from "lucide-react";
import Link from "next/link";
import { cn } from "@/lib/utils";
import { toast } from "sonner";
import { useState } from "react";

interface AgentCardProps {
  workflow: AgentWorkflow;
  onFork?: () => void;
  onStar?: () => void;
  onChat?: () => void;
}

/**
 * AgentCard - Card component for the Agent Gallery.
 * Displays agent metadata, stats, and actions (Run, Chat, Fork, Star).
 */
export function AgentCard({
  workflow,
  onFork,
  onStar,
  onChat,
}: AgentCardProps) {
  const [stars, setStars] = useState(workflow.star_count);
  const [isStarred, setIsStarred] = useState(false);

  const handleStar = async (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();

    try {
      const res = await fetch(
        `${
          process.env.NEXT_PUBLIC_AGENT_API_URL || "http://localhost:8005"
        }/v1/workflows/${workflow.id}/star`,
        {
          method: "POST",
        }
      );
      if (res.ok) {
        const data = await res.json();
        setStars(data.star_count);
        setIsStarred(true);
        toast.success("已点赞");
        if (onStar) onStar();
      }
    } catch (e) {
      toast.error("操作失败");
    }
  };

  const handleFork = async (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();

    try {
      const res = await fetch(
        `${
          process.env.NEXT_PUBLIC_AGENT_API_URL || "http://localhost:8005"
        }/v1/workflows/${workflow.id}/fork`,
        {
          method: "POST",
        }
      );
      if (res.ok) {
        toast.success("已成功复制到你的工作台", {
          description: "你可以在 Agent Studio 中优化它",
        });
        if (onFork) onFork();
      }
    } catch (e) {
      toast.error("复制失败");
    }
  };

  return (
    <Card className="group overflow-hidden border-muted/50 hover:border-primary/50 transition-all duration-300 hover:shadow-2xl hover:shadow-primary/5 bg-card/50 backdrop-blur-sm">
      <CardHeader className="p-4 pb-2">
        <div className="flex justify-between items-start">
          <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-primary/20 to-primary/5 flex items-center justify-center border border-primary/10 group-hover:scale-110 transition-transform duration-300">
            <Bot className="w-6 h-6 text-primary" />
          </div>
          <div className="flex flex-col items-end gap-1">
            <Badge variant="secondary" className="text-[10px] py-0 h-5">
              Agent
            </Badge>
            {workflow.is_public && (
              <Badge
                variant="outline"
                className="text-[10px] py-0 h-5 border-green-500/20 text-green-500 bg-green-500/5"
              >
                公开
              </Badge>
            )}
          </div>
        </div>
      </CardHeader>

      <CardContent className="p-4 pt-2">
        <h3 className="font-bold text-lg line-clamp-1 group-hover:text-primary transition-colors">
          {workflow.name_zh || workflow.name}
        </h3>
        <p className="text-sm text-muted-foreground line-clamp-2 mt-2 h-10 leading-relaxed">
          {workflow.description ||
            "一个高效的智能 Agent 工作流，旨在帮助你自动化日常任务。"}
        </p>

        <div className="flex items-center gap-4 mt-6 text-[10px] text-muted-foreground" aria-label="统计数据">
          <div className="flex items-center gap-1" title={`${stars} 个点赞`}>
            <Star
              className={cn(
                "w-3 h-3",
                isStarred && "fill-yellow-500 text-yellow-500"
              )}
              aria-hidden="true"
            />
            <span aria-label={`${stars} 个点赞`}>{stars}</span>
          </div>
          <div className="flex items-center gap-1" title={`${workflow.fork_count} 次克隆`}>
            <GitFork className="w-3 h-3" aria-hidden="true" />
            <span aria-label={`${workflow.fork_count} 次克隆`}>{workflow.fork_count}</span>
          </div>
          <div className="flex items-center gap-1" title={`${workflow.run_count} 次运行`}>
            <Play className="w-3 h-3" aria-hidden="true" />
            <span aria-label={`${workflow.run_count} 次运行`}>{workflow.run_count}</span>
          </div>
          <div className="ml-auto flex items-center gap-1" title={`更新于 ${new Date(workflow.updated_at).toLocaleDateString()}`}>
            <Clock className="w-3 h-3" aria-hidden="true" />
            <span>{new Date(workflow.updated_at).toLocaleDateString()}</span>
          </div>
        </div>
      </CardContent>

      <CardFooter className="p-4 pt-0 gap-2">
        <Button
          size="sm"
          variant="outline"
          className="rounded-full h-8 px-4 text-xs font-medium border-white/5 hover:bg-white/5 hover:border-white/10"
          onClick={(e) => {
            e.stopPropagation();
            onFork?.();
          }}
          aria-label={`克隆 ${workflow.name_zh || workflow.name}`}
        >
          <GitFork className="w-3.5 h-3.5 mr-1.5" aria-hidden="true" />
          克隆
        </Button>
        <Button
          size="sm"
          className="rounded-full h-8 px-4 text-xs font-medium shadow-[0_4px_12px_rgba(59,130,246,0.3)]"
          onClick={(e) => {
            e.stopPropagation();
            onChat?.();
          }}
          aria-label={`与 ${workflow.name_zh || workflow.name} 对话`}
        >
          <MessageSquare className="w-3.5 h-3.5 mr-1.5" aria-hidden="true" />
          对话
        </Button>
        <div className="flex gap-2" role="group" aria-label="快捷操作">
          <Button
            variant="ghost"
            size="icon"
            className="h-9 w-9 rounded-xl hover:bg-yellow-500/10 hover:text-yellow-500"
            onClick={handleStar}
            aria-label={isStarred ? "取消点赞" : "点赞"}
            aria-pressed={isStarred}
          >
            <Star
              className={cn(
                "w-4 h-4",
                isStarred && "fill-yellow-500 text-yellow-500"
              )}
              aria-hidden="true"
            />
          </Button>
          <Button
            variant="ghost"
            size="icon"
            className="h-9 w-9 rounded-xl hover:bg-blue-500/10 hover:text-blue-500"
            onClick={handleFork}
            aria-label="克隆到我的工作台"
          >
            <GitFork className="w-4 h-4" aria-hidden="true" />
          </Button>
        </div>
      </CardFooter>
    </Card>
  );
}
