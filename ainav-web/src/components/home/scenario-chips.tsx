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
    <div className="flex flex-wrap justify-center gap-2 sm:gap-3 mt-6 sm:mt-8 px-2 animate-in fade-in slide-in-from-bottom-8 duration-700 delay-200">
      {SCENARIOS.map((scenario) => (
        <Button
          key={scenario.id}
          variant="outline"
          size="sm"
          className="rounded-full min-h-[44px] h-11 px-4 sm:px-5 border-dashed border-border hover:border-solid hover:border-primary/50 hover:bg-primary/5 active:scale-[0.98] transition-all group touch-manipulation"
          onClick={() => router.push(`/tools?scenario=${scenario.id}`)}
          aria-label={`查看${scenario.label}相关工具`}
        >
          <scenario.icon
            className={`w-4 h-4 sm:w-4.5 sm:h-4.5 mr-1.5 sm:mr-2 ${scenario.color} group-hover:scale-110 transition-transform shrink-0`}
          />
          <span className="text-sm sm:text-base text-muted-foreground group-hover:text-foreground whitespace-nowrap">
            {scenario.label}
          </span>
        </Button>
      ))}
    </div>
  );
}
