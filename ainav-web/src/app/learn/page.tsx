import Link from "next/link";
import { BookOpen, Map, MessageSquare, ArrowRight } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
} from "@/components/ui/card";

export default function LearnCenterPage() {
  const sections = [
    {
      title: "提示词库",
      description: "精品 Prompt 集合，涵盖学术、开发、设计等多场景。",
      icon: <MessageSquare className="w-8 h-8 text-blue-400" />,
      href: "/learn/prompts",
      color: "blue",
    },
    {
      title: "学习路径图",
      description: "结构化的 AI 技能进阶地图，从零开始掌握前沿技术。",
      icon: <Map className="w-8 h-8 text-indigo-400" />,
      href: "/learn/roadmaps",
      color: "indigo",
    },
  ];

  return (
    <div className="container mx-auto px-4 py-16">
      <div className="max-w-4xl mx-auto text-center mb-20">
        <h1 className="text-5xl font-extrabold mb-6 tracking-tight">
          AI <span className="text-primary">学习中心</span>
        </h1>
        <p className="text-xl text-slate-400">
          不仅是工具导航，更是你的 AI 进化基地。
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-12 max-w-5xl mx-auto">
        {sections.map((section) => (
          <Link key={section.href} href={section.href}>
            <Card className="h-full bg-slate-900/40 border-slate-800 hover:border-primary/50 transition-all duration-500 hover:-translate-y-2 group cursor-pointer">
              <CardHeader className="pt-10">
                <div className="mb-4 inline-block p-4 bg-slate-950 rounded-2xl border border-slate-800 group-hover:scale-110 transition-transform duration-500">
                  {section.icon}
                </div>
                <CardTitle className="text-3xl mb-4 group-hover:text-primary transition-colors">
                  {section.title}
                </CardTitle>
                <CardDescription className="text-lg text-slate-400 leading-relaxed">
                  {section.description}
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="flex items-center text-primary font-semibold group-hover:gap-3 transition-all">
                  预览内容 <ArrowRight className="w-5 h-5 ml-2" />
                </div>
              </CardContent>
            </Card>
          </Link>
        ))}
      </div>

      <div className="mt-24 p-12 bg-gradient-to-br from-primary/10 to-transparent rounded-3xl border border-primary/20 text-center max-w-4xl mx-auto">
        <BookOpen className="w-12 h-12 text-primary mx-auto mb-6" />
        <h2 className="text-3xl font-bold mb-4">更多内容正在筹备中</h2>
        <p className="text-slate-400 mb-8 max-w-lg mx-auto">
          我们将持续更新深度教程、行业案例及 AI
          趋势分析，助你始终走在技术最前沿。
        </p>
        <Button size="lg" variant="outline" className="rounded-full px-8">
          订阅更新
        </Button>
      </div>
    </div>
  );
}
