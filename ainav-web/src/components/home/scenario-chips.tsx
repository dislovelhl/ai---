"use client";

import { Button } from "@/components/ui/button";
import {
  Sparkles,
  FileText,
  Code,
  Image as ImageIcon,
  Video,
} from "lucide-react";
import Link from "next/link";
import { useRouter } from "next/navigation";

export const SCENARIOS = [
  { id: "writing", label: "写作助手", icon: FileText, color: "text-blue-500" },
  { id: "coding", label: "代码编程", icon: Code, color: "text-purple-500" },
  { id: "image", label: "图像生成", icon: ImageIcon, color: "text-pink-500" },
  { id: "video", label: "视频制作", icon: Video, color: "text-orange-500" },
  { id: "ppt", label: "PPT生成", icon: Sparkles, color: "text-yellow-500" },
];

export function ScenarioChips() {
  const router = useRouter();

  return (
    <div className="flex flex-wrap justify-center gap-3 mt-8 animate-in fade-in slide-in-from-bottom-8 duration-700 delay-200">
      {SCENARIOS.map((scenario) => (
        <Button
          key={scenario.id}
          variant="outline"
          size="sm"
          className="rounded-full h-9 px-4 border-dashed border-border hover:border-solid hover:border-primary/50 hover:bg-primary/5 transition-all group"
          onClick={() => router.push(`/tools?scenario=${scenario.id}`)}
        >
          <scenario.icon
            className={`w-4 h-4 mr-2 ${scenario.color} group-hover:scale-110 transition-transform`}
          />
          <span className="text-muted-foreground group-hover:text-foreground">
            {scenario.label}
          </span>
        </Button>
      ))}
    </div>
  );
}
