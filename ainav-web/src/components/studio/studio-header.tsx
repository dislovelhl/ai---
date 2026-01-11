"use client";

import { useState, useCallback } from "react";
import {
  Save,
  Play,
  Settings,
  ChevronLeft,
  MoreHorizontal,
  Undo,
  Redo,
  LayoutGrid,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import Link from "next/link";

interface StudioHeaderProps {
  workflowName: string;
  onNameChange: (name: string) => void;
  onSave?: () => void;
  onRun?: () => void;
  onUndo?: () => void;
  onRedo?: () => void;
  onLayout?: () => void;
  canUndo?: boolean;
  canRedo?: boolean;
  isSaving?: boolean;
  isRunning?: boolean;
}

/**
 * StudioHeader - Top header for Agent Studio with save/run actions.
 */
export function StudioHeader({
  workflowName,
  onNameChange,
  onSave,
  onRun,
  onUndo,
  onRedo,
  onLayout,
  canUndo = false,
  canRedo = false,
  isSaving = false,
  isRunning = false,
}: StudioHeaderProps) {
  const [isEditing, setIsEditing] = useState(false);
  const [editValue, setEditValue] = useState(workflowName);

  const handleEditStart = useCallback(() => {
    setEditValue(workflowName);
    setIsEditing(true);
  }, [workflowName]);

  const handleEditEnd = useCallback(() => {
    if (editValue.trim()) {
      onNameChange(editValue.trim());
    }
    setIsEditing(false);
  }, [editValue, onNameChange]);

  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent) => {
      if (e.key === "Enter") {
        handleEditEnd();
      } else if (e.key === "Escape") {
        setIsEditing(false);
      }
    },
    [handleEditEnd]
  );

  return (
    <header className="h-14 border-b bg-background/95 backdrop-blur-sm flex items-center justify-between px-4">
      {/* Left side: Back + Name */}
      <div className="flex items-center gap-3">
        <Link href="/">
          <Button variant="ghost" size="icon" className="h-8 w-8">
            <ChevronLeft className="w-4 h-4" />
          </Button>
        </Link>

        <div className="flex items-center gap-2">
          <span className="text-2xl">🤖</span>
          {isEditing ? (
            <Input
              value={editValue}
              onChange={(e) => setEditValue(e.target.value)}
              onBlur={handleEditEnd}
              onKeyDown={handleKeyDown}
              autoFocus
              className="h-8 w-48 text-lg font-semibold"
            />
          ) : (
            <button
              onClick={handleEditStart}
              className="text-lg font-semibold hover:text-primary transition-colors"
            >
              {workflowName}
            </button>
          )}
        </div>
      </div>

      {/* Center: Status indicator */}
      <div className="flex items-center gap-4">
        <div className="flex items-center gap-2 bg-muted/50 px-3 py-1 rounded-full border border-border/50 backdrop-blur-sm">
          <div className="relative">
            <span className="flex h-2 w-2 rounded-full bg-green-500" />
            <span className="absolute inset-0 h-2 w-2 rounded-full bg-green-500 animate-ping opacity-75" />
          </div>
          <span className="text-[10px] font-medium uppercase tracking-wider text-muted-foreground">
            Live Collaboration
          </span>
        </div>

        <div className="flex -space-x-2">
          {[1, 2].map((i) => (
            <div
              key={i}
              className="w-6 h-6 rounded-full border-2 border-background bg-gradient-to-br from-violet-500 to-purple-500 flex items-center justify-center text-[10px] text-white font-bold"
            >
              {String.fromCharCode(64 + i)}
            </div>
          ))}
          <div className="w-6 h-6 rounded-full border-2 border-background bg-muted flex items-center justify-center text-[10px] text-muted-foreground">
            +1
          </div>
        </div>
      </div>

      {/* Right side: Actions */}
      <div className="flex items-center gap-2">
        <div className="flex items-center gap-1 mr-2 px-1 border-r pr-3">
          <Button
            variant="ghost"
            size="icon"
            className="h-8 w-8"
            onClick={onUndo}
            disabled={!canUndo}
            title="Undo (Ctrl+Z)"
          >
            <Undo className="w-4 h-4" />
          </Button>
          <Button
            variant="ghost"
            size="icon"
            className="h-8 w-8"
            onClick={onRedo}
            disabled={!canRedo}
            title="Redo (Ctrl+Shift+Z)"
          >
            <Redo className="w-4 h-4" />
          </Button>
        </div>

        <Button
          variant="outline"
          size="sm"
          onClick={onLayout}
          className="mr-2"
          title="Auto Layout (Dagre)"
        >
          <LayoutGrid className="w-4 h-4 mr-2" />
          布局
        </Button>

        <Button
          variant="outline"
          size="sm"
          onClick={onSave}
          disabled={isSaving}
        >
          <Save className="w-4 h-4 mr-2" />
          {isSaving ? "保存中..." : "保存"}
        </Button>

        <Button
          size="sm"
          onClick={onRun}
          disabled={isRunning}
          className="bg-gradient-to-r from-violet-500 to-purple-600 hover:from-violet-600 hover:to-purple-700"
        >
          <Play className="w-4 h-4 mr-2" />
          {isRunning ? "运行中..." : "运行"}
        </Button>

        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="ghost" size="icon" className="h-8 w-8">
              <MoreHorizontal className="w-4 h-4" />
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end">
            <DropdownMenuItem>
              <Settings className="w-4 h-4 mr-2" />
              工作流设置
            </DropdownMenuItem>
            <DropdownMenuItem>导出 JSON</DropdownMenuItem>
            <DropdownMenuItem>复制工作流</DropdownMenuItem>
            <DropdownMenuItem className="text-destructive">
              删除工作流
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>
    </header>
  );
}
