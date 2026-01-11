import { RoadmapCard } from "@/components/learn/roadmap-card";

const ROADMAPS = [
  {
    title: "DeepSeek 零基础部署指南",
    description: "从本地环境搭建到 API 调用，带你快速上手这款国产最强 AI。",
    level: "入门" as const,
    duration: "2 小时",
    tags: ["DeepSeek", "本地部署", "Python"],
    slug: "deepseek-guide",
  },
  {
    title: "提示词工程大师之路",
    description: "系统学习 Prompt Engineering 的核心技巧，提高 AI 生成质量。",
    level: "中级" as const,
    duration: "5 小时",
    tags: ["提示词工程", "LLM", "提问技巧"],
    slug: "prompt-master",
  },
  {
    title: "AI 绘画实战：Midjourney + Stable Diffusion",
    description: "掌握顶级 AI 绘图工具，从关键词描写到模型微调全流程。",
    level: "进阶" as const,
    duration: "10 小时",
    tags: ["AI 绘画", "MJ", "SD", "创意设计"],
    slug: "ai-art-mastery",
  },
];

export default function RoadmapsPage() {
  return (
    <div className="container mx-auto px-4 py-12">
      <div className="max-w-4xl mx-auto text-center mb-16">
        <h1 className="text-4xl md:text-5xl font-bold mb-6 bg-gradient-to-r from-indigo-400 to-purple-400 bg-clip-text text-transparent">
          AI 学习路径图
        </h1>
        <p className="text-xl text-slate-400">
          结构化的学习流程，助你从 AI 小白成长为各领域的专家。
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
        {ROADMAPS.map((r, idx) => (
          <RoadmapCard key={idx} {...r} />
        ))}
      </div>
    </div>
  );
}
