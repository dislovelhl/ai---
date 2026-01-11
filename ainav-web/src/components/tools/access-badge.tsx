"use client"

import { Badge } from "@/components/ui/badge";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import { Globe, ShieldCheck, AlertTriangle } from "lucide-react";
import { cn } from "@/lib/utils";

interface AccessBadgeProps {
  isAccessible: boolean;
  requiresVpn: boolean;
  className?: string;
}

export function AccessBadge({
  isAccessible,
  requiresVpn,
  className,
}: AccessBadgeProps) {
  if (isAccessible && !requiresVpn) {
    return (
      <TooltipProvider>
        <Tooltip>
          <TooltipTrigger asChild>
            <Badge
              variant="outline"
              className={cn(
                "text-xs bg-emerald-500/10 text-emerald-600 hover:bg-emerald-500/20 border-emerald-500/20 dark:text-emerald-400 px-2 py-0.5 cursor-help",
                className
              )}
            >
              <Globe className="h-3 w-3 mr-1" />
              国内直连
            </Badge>
          </TooltipTrigger>
          <TooltipContent>
            <p>可在中国境内无需VPN直接访问</p>
          </TooltipContent>
        </Tooltip>
      </TooltipProvider>
    );
  }

  if (requiresVpn) {
    return (
      <TooltipProvider>
        <Tooltip>
          <TooltipTrigger asChild>
            <Badge
              variant="outline"
              className={cn(
                "text-xs bg-amber-500/10 text-amber-600 hover:bg-amber-500/20 border-amber-500/20 dark:text-amber-400 px-2 py-0.5 cursor-help",
                className
              )}
            >
              <ShieldCheck className="h-3 w-3 mr-1" />
              需要VPN
            </Badge>
          </TooltipTrigger>
          <TooltipContent>
            <p>需要使用VPN才能在中国访问</p>
          </TooltipContent>
        </Tooltip>
      </TooltipProvider>
    );
  }

  return (
    <TooltipProvider>
      <Tooltip>
        <TooltipTrigger asChild>
          <Badge
            variant="outline"
            className={cn(
              "text-xs bg-zinc-500/10 text-zinc-600 hover:bg-zinc-500/20 border-zinc-500/20 dark:text-zinc-400 px-2 py-0.5 cursor-help",
              className
            )}
          >
            <AlertTriangle className="h-3 w-3 mr-1" />
            访问受限
          </Badge>
        </TooltipTrigger>
        <TooltipContent>
          <p>在中国境内无法访问</p>
        </TooltipContent>
      </Tooltip>
    </TooltipProvider>
  );
}
