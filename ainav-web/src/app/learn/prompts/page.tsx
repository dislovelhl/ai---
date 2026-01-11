import { PromptCard } from "@/components/learn/prompt-card";

const PROMPTS = [
  {
    title: "学术论文深度润色",
    description: "将学术论文的草稿转化为高质量、专业且符合顶级期刊风格的表达。",
    category: "学术/科研",
    prompt:
      "你是一位资深的学术期刊编辑。请对以下段落进行深度润色：1. 增强学术严谨性；2. 优化句式结构，使其更加简洁有力；3. 纠正潜在的语法错误；4. 确保专业术语使用精准。请以中英双语形式提供改进建议及理由。\n\n待润色内容：[在此处输入内容]",
  },
  {
    title: "多端代码架构设计",
    description: "根据功能需求，生成符合现代架构规范的前后端代码结构建议。",
    category: "开发/工程",
    prompt:
      "你是一位高级系统架构师。请为以下需求设计一个基于 TypeScript 和 NestJS 的微服务架构方案：\n需求描述：[具体功能需求]\n请提供：1. 核心模块划分；2. 关键实体模型定义；3. API接口设计规范；4. 数据库索引优化建议。",
  },
  {
    title: "深度内容营销脚本",
    description: "为社交媒体平台（如小红书、抖音）生成具有爆款潜质的内容脚本。",
    category: "营销/自媒体",
    prompt:
      "你是一位拥有百万粉丝的自媒体博主。请为[主题]撰写一个时长为60秒的短视频脚本：\n1. 黄金3秒钩子开头；2. 核心价值点拆解；3. 强互动的结尾CTA（呼吁行动）。风格要求：[如：幽默、专业、治愈]。",
  },
  {
    title: "复杂逻辑代码重构",
    description: "对嵌套深、逻辑混杂的代码进行清晰化、模块化重构。",
    category: "开发/工程",
    prompt:
      "你是一位代码重构大师。请对以下逻辑复杂的函数进行重构：1. 识别并提取冗余代码；2. 引入适当的设计模式；3. 提高代码的可读性和可维护性。请提供重构后的代码以及重构思路。\n\n源码：[在此处输入代码]",
  },
];

export default function PromptLibraryPage() {
  return (
    <div className="container mx-auto px-4 py-12">
      <div className="max-w-4xl mx-auto text-center mb-16">
        <h1 className="text-4xl md:text-5xl font-bold mb-6 bg-gradient-to-r from-blue-400 to-indigo-400 bg-clip-text text-transparent">
          Prompt 提示词库
        </h1>
        <p className="text-xl text-slate-400">
          精心筛选的各领域优质提示词，助力你与 AI 进行更深度的对话。
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-2 gap-8">
        {PROMPTS.map((p, idx) => (
          <PromptCard key={idx} {...p} />
        ))}
      </div>
    </div>
  );
}
