"use client";

import { Map, ArrowRight, Clock, Star } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
  CardFooter,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import Link from "next/link";

interface RoadmapProps {
  title: string;
  description: string;
  level: "入门" | "中级" | "进阶";
  duration: string;
  tags: string[];
  slug: string;
}

export function RoadmapCard({
  title,
  description,
  level,
  duration,
  tags,
  slug,
}: RoadmapProps) {
  const levelColor = {
    入门: "bg-green-500/10 text-green-400",
    中级: "bg-blue-500/10 text-blue-400",
    进阶: "bg-purple-500/10 text-purple-400",
  }[level];

  return (
    <Card className="flex flex-col h-full bg-slate-900/50 border-slate-800 hover:border-indigo-500/50 transition-all duration-300 group">
      <CardHeader>
        <div className="flex justify-between items-start mb-4">
          <div className="p-2 bg-indigo-500/10 rounded-lg text-indigo-400">
            <Map className="w-6 h-6" />
          </div>
          <Badge className={levelColor + " border-none"}>{level}</Badge>
        </div>
        <CardTitle className="text-2xl group-hover:text-indigo-400 transition-colors">
          {title}
        </CardTitle>
        <CardDescription className="text-slate-400 mt-2">
          {description}
        </CardDescription>
      </CardHeader>
      <CardContent className="flex-grow">
        <div className="flex flex-wrap gap-2 mb-4">
          {tags.map((tag) => (
            <Badge
              key={tag}
              variant="outline"
              className="text-[10px] border-slate-700 text-slate-500"
            >
              {tag}
            </Badge>
          ))}
        </div>
        <div className="flex items-center gap-4 text-sm text-slate-500">
          <span className="flex items-center gap-1">
            <Clock className="w-4 h-4" /> {duration}
          </span>
          <span className="flex items-center gap-1">
            <Star className="w-4 h-4" /> 优质推荐
          </span>
        </div>
      </CardContent>
      <CardFooter>
        <Button
          asChild
          className="w-full gap-2 bg-indigo-600 hover:bg-indigo-500 text-white"
        >
          <Link href={`/learn/roadmaps/${slug}`}>
            开始学习 <ArrowRight className="w-4 h-4" />
          </Link>
        </Button>
      </CardFooter>
    </Card>
  );
}
