import { Badge } from "@/components/ui/badge";
import { Gift, Coins, CreditCard, FlaskConical, Github } from "lucide-react";
import { cn } from "@/lib/utils";

export type PricingType =
  | "free"
  | "freemium"
  | "paid"
  | "beta_free"
  | "open_source";

const pricingConfig: Record<
  PricingType,
  {
    label: string;
    icon: React.ComponentType<{ className?: string }>;
    className: string;
  }
> = {
  free: {
    label: "完全免费",
    icon: Gift,
    className:
      "bg-green-500/10 text-green-600 hover:bg-green-500/20 border-green-500/20 dark:text-green-400",
  },
  freemium: {
    label: "免费额度",
    icon: Coins,
    className:
      "bg-blue-500/10 text-blue-600 hover:bg-blue-500/20 border-blue-500/20 dark:text-blue-400",
  },
  paid: {
    label: "付费",
    icon: CreditCard,
    className:
      "bg-orange-500/10 text-orange-600 hover:bg-orange-500/20 border-orange-500/20 dark:text-orange-400",
  },
  beta_free: {
    label: "公测免费",
    icon: FlaskConical,
    className:
      "bg-purple-500/10 text-purple-600 hover:bg-purple-500/20 border-purple-500/20 dark:text-purple-400",
  },
  open_source: {
    label: "开源",
    icon: Github,
    className:
      "bg-zinc-500/10 text-zinc-600 hover:bg-zinc-500/20 border-zinc-500/20 dark:text-zinc-400",
  },
};

interface PricingBadgeProps {
  type?: PricingType | string;
  showIcon?: boolean;
  className?: string;
}

export function PricingBadge({
  type = "free",
  showIcon = true,
  className,
}: PricingBadgeProps) {
  // Handle string types from API that might not precisely match
  const normalizedType = (type as PricingType) || "free";
  const config = pricingConfig[normalizedType] || pricingConfig.free;
  const Icon = config.icon;

  return (
    <Badge
      variant="outline"
      className={cn(
        "text-xs font-medium px-2 py-0.5",
        config.className,
        className
      )}
    >
      {showIcon && <Icon className="h-3 w-3 mr-1" />}
      {config.label}
    </Badge>
  );
}
