import { Tool } from "@/lib/types";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Star } from "lucide-react";
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
              alt={tool.name}
              fill
              className="object-cover group-hover:scale-110 transition-transform duration-700"
            />
          ) : (
            <div className="w-full h-full bg-secondary/50 flex items-center justify-center group-hover:scale-110 transition-transform duration-700">
              <span className="text-4xl font-bold opacity-10">
                {tool.name[0]}
              </span>
            </div>
          )}
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
            <div className="flex items-center gap-1 text-amber-500">
              <Star className="w-4 h-4 fill-current" />
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
