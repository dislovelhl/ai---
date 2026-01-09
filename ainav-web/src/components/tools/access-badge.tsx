import { Badge } from "@/components/ui/badge";
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
      <Badge
        variant="outline"
        className={cn(
          "text-xs bg-emerald-500/10 text-emerald-600 hover:bg-emerald-500/20 border-emerald-500/20 dark:text-emerald-400 px-2 py-0.5",
          className
        )}
      >
        <Globe className="h-3 w-3 mr-1" />
        国内直连
      </Badge>
    );
  }

  if (requiresVpn) {
    return (
      <Badge
        variant="outline"
        className={cn(
          "text-xs bg-amber-500/10 text-amber-600 hover:bg-amber-500/20 border-amber-500/20 dark:text-amber-400 px-2 py-0.5",
          className
        )}
      >
        <ShieldCheck className="h-3 w-3 mr-1" />
        需要VPN
      </Badge>
    );
  }

  return (
    <Badge
      variant="outline"
      className={cn(
        "text-xs bg-zinc-500/10 text-zinc-600 hover:bg-zinc-500/20 border-zinc-500/20 dark:text-zinc-400 px-2 py-0.5",
        className
      )}
    >
      <AlertTriangle className="h-3 w-3 mr-1" />
      访问受限
    </Badge>
  );
}
