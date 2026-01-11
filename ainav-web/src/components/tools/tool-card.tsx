import { Tool } from "@/lib/types";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Star, Zap } from "lucide-react";
import { PricingBadge } from "./pricing-badge";
import { AccessBadge } from "./access-badge";
import Image from "next/image";
import Link from "next/link";

interface ToolCardProps {
  tool: Tool;
}

export function ToolCard({ tool }: ToolCardProps) {
  return (
    <Link href={`/tools/${tool.slug}`}>
      <Card className="group overflow-hidden border-none glass hover:shadow-2xl transition-all duration-500 rounded-3xl h-full flex flex-col">
        <div className="relative aspect-video overflow-hidden">
          {tool.logo_url ? (
            <Image
              src={tool.logo_url}
              alt={`${tool.name} - AI 工具图标`}
              fill
              className="object-cover group-hover:scale-110 transition-transform duration-700"
            />
          ) : (
            <div
              className="w-full h-full bg-secondary/50 flex items-center justify-center group-hover:scale-110 transition-transform duration-700"
              role="presentation"
              aria-hidden="true"
            >
              <span className="text-4xl font-bold opacity-10">
                {tool.name[0]}
              </span>
            </div>
          )}
          <div className="absolute top-3 left-3 flex flex-col gap-2">
            {/* Skills badge - indicates tool can be used in Agent workflows */}
            {tool.has_api && (
              <Badge
                className="bg-gradient-to-r from-violet-500 to-purple-600 text-white border-0 shadow-lg"
                aria-label="此工具支持 Agent Skills 集成"
              >
                <Zap className="w-3 h-3 mr-1" aria-hidden="true" />
                <span lang="en">Skills</span>
              </Badge>
            )}
          </div>
          <div className="absolute top-3 right-3 flex flex-col gap-2">
            <AccessBadge
              isAccessible={tool.is_china_accessible}
              requiresVpn={tool.requires_vpn}
              className="backdrop-blur-md"
            />
            {tool.pricing_type && (
              <PricingBadge
                type={tool.pricing_type}
                className="backdrop-blur-md"
              />
            )}
          </div>
        </div>

        <CardContent className="p-6 flex-1 flex flex-col">
          <div className="flex items-center justify-between mb-3">
            <h3 className="text-xl font-bold group-hover:text-primary transition-colors">
              {tool.name}
            </h3>
            <div
              className="flex items-center gap-1 text-amber-500"
              role="img"
              aria-label={`评分 ${tool.avg_rating.toFixed(1)} 分（满分 5 分）`}
            >
              <Star className="w-4 h-4 fill-current" aria-hidden="true" />
              <span className="text-sm font-semibold">
                {tool.avg_rating.toFixed(1)}
              </span>
            </div>
          </div>

          <p className="text-muted-foreground text-sm line-clamp-2 mb-4 flex-1">
            {tool.description}
          </p>

          <div className="flex flex-wrap gap-2 mt-auto">
            {tool.category && (
              <span className="text-[10px] uppercase tracking-wider font-bold text-muted-foreground/50 border border-muted-foreground/20 rounded-full px-2 py-0.5">
                {tool.category.name}
              </span>
            )}
            {tool.scenarios.slice(0, 2).map((s) => (
              <span
                key={s.id}
                className="text-[10px] uppercase tracking-wider font-bold text-primary/50 bg-primary/5 rounded-full px-2 py-0.5"
              >
                {s.name}
              </span>
            ))}
          </div>
        </CardContent>
      </Card>
    </Link>
  );
}
