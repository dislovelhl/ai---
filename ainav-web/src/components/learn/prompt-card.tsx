"use client";

import { useState } from "react";
import { Copy, Check, MessageSquare } from "lucide-react";
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

interface PromptProps {
  title: string;
  description: string;
  prompt: string;
  category: string;
  author?: string;
}

export function PromptCard({
  title,
  description,
  prompt,
  category,
  author = "System",
}: PromptProps) {
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    navigator.clipboard.writeText(prompt);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <Card className="flex flex-col h-full bg-slate-900/50 border-slate-800 hover:border-blue-500/50 transition-all duration-300 group">
      <CardHeader>
        <div className="flex justify-between items-start gap-2 mb-2">
          <Badge
            variant="secondary"
            className="bg-blue-500/10 text-blue-400 border-none"
          >
            {category}
          </Badge>
          <span className="text-xs text-slate-500 flex items-center gap-1">
            <MessageSquare className="w-3 h-3" /> {author}
          </span>
        </div>
        <CardTitle className="text-xl group-hover:text-blue-400 transition-colors">
          {title}
        </CardTitle>
        <CardDescription className="text-slate-400 line-clamp-2">
          {description}
        </CardDescription>
      </CardHeader>
      <CardContent className="flex-grow">
        <div className="bg-slate-950 p-4 rounded-lg text-sm font-mono text-slate-300 line-clamp-4 relative">
          {prompt}
          <div className="absolute inset-x-0 bottom-0 h-8 bg-gradient-to-t from-slate-950 to-transparent" />
        </div>
      </CardContent>
      <CardFooter>
        <Button
          variant="outline"
          className="w-full gap-2 border-slate-700 hover:bg-blue-500 hover:text-white"
          onClick={handleCopy}
        >
          {copied ? (
            <>
              <Check className="w-4 h-4" /> 已复制
            </>
          ) : (
            <>
              <Copy className="w-4 h-4" /> 复制提示词
            </>
          )}
        </Button>
      </CardFooter>
    </Card>
  );
}
