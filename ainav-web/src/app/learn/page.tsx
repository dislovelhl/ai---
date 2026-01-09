"use client";

import { Navbar } from "@/components/layout/navbar";
import { Footer } from "@/components/layout/footer";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  CardDescription,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import {
  BookOpen,
  Map,
  Lightbulb,
  ArrowRight,
  GraduationCap,
  Code2,
  Palette,
  Video,
} from "lucide-react";
import Link from "next/link";

const LEARNING_PATHS = [
  {
    title: "AI 绘画进阶之路",
    description: "从 Midjourney 基础到 Stable Diffusion 高级部署与模型训练。",
    icon: Palette,
    color: "blue",
    level: "入门 to 进阶",
    steps: 12,
  },
  {
    title: "AI 编程提效指南",
    description: "掌握 Cursor, GitHub Copilot 等工具，让编程效率提升 10 倍。",
    icon: Code2,
    color: "emerald",
    level: "进阶",
    steps: 8,
  },
  {
    title: "AI 视频创作全流程",
    description: "使用 Runway, Pika, Sora 等工具打造好莱坞级别的 AI 视频。",
    icon: Video,
    color: "purple",
    level: "入门",
    steps: 6,
  },
];

export default function LearnPage() {
  return (
    <div className="flex flex-col min-h-screen">
      <Navbar />
      <main className="flex-1 py-16 bg-grid relative">
        <div className="absolute inset-0 bg-gradient-to-b from-background via-background/90 to-background pointer-events-none" />

        <div className="container relative mx-auto px-4 max-w-6xl">
          <header className="text-center mb-16 space-y-4">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-primary/10 text-primary text-xs font-medium mb-4">
              <GraduationCap className="h-4 w-4" />
              <span>AI 学习中心</span>
            </div>
            <h1 className="text-5xl md:text-7xl font-black tracking-tight">
              系统化 <span className="text-gradient">玩转 AI</span>
            </h1>
            <p className="max-w-2xl mx-auto text-xl text-muted-foreground leading-relaxed">
              从零开始，手把手带你掌握最前沿的 AI 工具，跨越技术鸿沟，成就 AI
              极客。
            </p>
          </header>

          <section className="space-y-8 mb-24">
            <div className="flex items-end justify-between">
              <div>
                <h2 className="text-3xl font-bold flex items-center gap-3">
                  <Map className="text-primary" /> 精选学习路径
                </h2>
                <p className="text-muted-foreground mt-2">
                  由社区专家精心编排的系统化教程
                </p>
              </div>
            </div>

            <div className="grid md:grid-cols-3 gap-8">
              {LEARNING_PATHS.map((path, i) => (
                <Card
                  key={i}
                  className="group glass border-2 rounded-[2.5rem] overflow-hidden hover:shadow-2xl transition-all duration-500 hover:-translate-y-2"
                >
                  <CardHeader className="p-8 pb-0">
                    <div
                      className={`w-14 h-14 rounded-2xl bg-${path.color}-500/10 flex items-center justify-center mb-6 group-hover:scale-110 transition-transform`}
                    >
                      <path.icon className={`h-8 w-8 text-${path.color}-500`} />
                    </div>
                    <CardTitle className="text-2xl font-bold mb-2 group-hover:text-primary transition-colors">
                      {path.title}
                    </CardTitle>
                    <CardDescription className="text-base line-clamp-3 min-h-[4.5rem]">
                      {path.description}
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="p-8 pt-6 space-y-6">
                    <div className="flex items-center justify-between text-sm">
                      <Badge variant="secondary" className="bg-secondary/50">
                        {path.level}
                      </Badge>
                      <span className="text-muted-foreground font-medium">
                        {path.steps} 章节
                      </span>
                    </div>
                    <Button
                      className="w-full h-12 rounded-xl group/btn"
                      variant="outline"
                    >
                      开始学习{" "}
                      <ArrowRight className="ml-2 w-4 h-4 group-hover/btn:translate-x-1 transition-transform" />
                    </Button>
                  </CardContent>
                </Card>
              ))}
            </div>
          </section>

          <section className="relative p-12 md:p-20 rounded-[3rem] overflow-hidden glass border-2 text-center">
            <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-transparent via-primary to-transparent opacity-20" />

            <Lightbulb className="w-16 h-16 text-primary mx-auto mb-8 animate-pulse" />
            <h2 className="text-4xl font-bold mb-6">
              更多精彩，由于您的加入而更近一步
            </h2>
            <p className="text-xl text-muted-foreground max-w-3xl mx-auto mb-10 leading-relaxed">
              我们正在筹备 <b>提示词黑客 (Prompt Hacking)</b>、
              <b>LLM 应用开发</b> 以及 <b>AI 变现案例库</b> 等深度内容。
              订阅我们的通讯，第一时间获取更新。
            </p>
            <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
              <Input
                placeholder="输入您的邮箱"
                className="max-w-xs h-14 rounded-2xl glass border-2 text-lg"
              />
              <Button
                size="lg"
                className="h-14 px-10 rounded-2xl text-lg font-bold"
              >
                立即订阅
              </Button>
            </div>
          </section>
        </div>
      </main>
      <Footer />
    </div>
  );
}
