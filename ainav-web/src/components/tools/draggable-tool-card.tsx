"use client";

import { useDraggable } from "@dnd-kit/core";
import { Tool } from "@/lib/types";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { GripVertical, Zap } from "lucide-react";
import Image from "next/image";

interface DraggableToolCardProps {
  tool: Tool;
}

/**
 * DraggableToolCard - A compact, draggable version of ToolCard for the Agent Studio.
 * Users can drag this onto the canvas to create a Skill node.
 */
export function DraggableToolCard({ tool }: DraggableToolCardProps) {
  const { attributes, listeners, setNodeRef, transform, isDragging } =
    useDraggable({
      id: tool.id,
      data: {
        type: "tool",
        tool: tool,
        skills: tool.skills || [],
      },
    });

  const style = transform
    ? { transform: `translate3d(${transform.x}px, ${transform.y}px, 0)` }
    : undefined;

  return (
    <div
      ref={setNodeRef}
      style={style}
      className={`relative transition-opacity ${
        isDragging ? "opacity-50 z-50" : ""
      }`}
    >
      <Card className="group overflow-hidden border border-border/50 hover:border-primary/50 bg-background/80 backdrop-blur-sm rounded-xl transition-all duration-300 hover:shadow-lg">
        <div className="p-3 flex items-center gap-3">
          {/* Drag Handle */}
          <div
            {...listeners}
            {...attributes}
            className="cursor-grab active:cursor-grabbing p-1 rounded hover:bg-muted/50 transition-colors"
          >
            <GripVertical className="w-4 h-4 text-muted-foreground" />
          </div>

          {/* Tool Logo */}
          <div className="relative w-10 h-10 rounded-lg overflow-hidden flex-shrink-0 bg-muted/30">
            {tool.logo_url ? (
              <Image
                src={tool.logo_url}
                alt={tool.name}
                fill
                className="object-cover"
              />
            ) : (
              <div className="w-full h-full flex items-center justify-center">
                <span className="text-lg font-bold text-muted-foreground/50">
                  {tool.name[0]}
                </span>
              </div>
            )}
          </div>

          {/* Tool Info */}
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2">
              <h4 className="font-semibold text-sm truncate">{tool.name}</h4>
              {tool.has_api && (
                <Badge
                  variant="secondary"
                  className="text-[10px] px-1.5 py-0 bg-violet-500/10 text-violet-600 border-violet-500/20"
                >
                  <Zap className="w-2.5 h-2.5 mr-0.5" />
                  {tool.skills?.length || 0}
                </Badge>
              )}
            </div>
            <p className="text-xs text-muted-foreground truncate">
              {tool.description?.slice(0, 60) || "No description"}
              {tool.description && tool.description.length > 60 ? "..." : ""}
            </p>
          </div>
        </div>

        {/* Skill list preview on hover */}
        {tool.skills && tool.skills.length > 0 && (
          <div className="border-t border-border/50 px-3 py-2 bg-muted/30 opacity-0 group-hover:opacity-100 transition-opacity">
            <p className="text-[10px] uppercase tracking-wider text-muted-foreground mb-1">
              Available Skills
            </p>
            <div className="flex flex-wrap gap-1">
              {tool.skills.slice(0, 3).map((skill) => (
                <span
                  key={skill.id}
                  className="text-[10px] px-1.5 py-0.5 rounded bg-background border border-border/50"
                >
                  {skill.name}
                </span>
              ))}
              {tool.skills.length > 3 && (
                <span className="text-[10px] text-muted-foreground">
                  +{tool.skills.length - 3} more
                </span>
              )}
            </div>
          </div>
        )}
      </Card>
    </div>
  );
}
