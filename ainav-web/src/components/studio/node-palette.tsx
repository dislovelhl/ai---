"use client";

import { DragEvent } from "react";
import {
  MessageSquare,
  Brain,
  ArrowRightCircle,
  Shuffle,
  Zap,
} from "lucide-react";

interface NodeTypeConfig {
  type: string;
  label: string;
  labelZh: string;
  icon: React.ReactNode;
  color: string;
  description: string;
}

const nodeTypes: NodeTypeConfig[] = [
  {
    type: "input",
    label: "Input",
    labelZh: "输入",
    icon: <MessageSquare className="w-4 h-4" />,
    color: "from-green-500 to-emerald-600",
    description: "工作流的起点，接收用户输入",
  },
  {
    type: "llm",
    label: "LLM",
    labelZh: "大模型",
    icon: <Brain className="w-4 h-4" />,
    color: "from-violet-500 to-purple-600",
    description: "调用 DeepSeek 进行文本处理",
  },
  {
    type: "skill",
    label: "Skill",
    labelZh: "技能",
    icon: <Zap className="w-4 h-4" />,
    color: "from-orange-500 to-amber-600",
    description: "调用工具 API 执行操作",
  },
  {
    type: "transform",
    label: "Transform",
    labelZh: "转换",
    icon: <Shuffle className="w-4 h-4" />,
    color: "from-yellow-500 to-amber-500",
    description: "数据格式转换和处理",
  },
  {
    type: "output",
    label: "Output",
    labelZh: "输出",
    icon: <ArrowRightCircle className="w-4 h-4" />,
    color: "from-blue-500 to-cyan-600",
    description: "工作流的终点，返回结果",
  },
];

/**
 * NodePalette - Sidebar component showing available node types.
 * Users can drag nodes from here onto the canvas.
 */
export function NodePalette() {
  const onDragStart = (event: DragEvent, nodeType: string) => {
    event.dataTransfer.setData(
      "application/reactflow",
      JSON.stringify({
        type: nodeType,
        data: {},
      })
    );
    event.dataTransfer.effectAllowed = "move";
  };

  return (
    <div className="p-4 border-b">
      <h3 className="text-sm font-semibold text-muted-foreground mb-3 uppercase tracking-wider">
        节点类型
      </h3>
      <div className="grid grid-cols-2 gap-2">
        {nodeTypes.map((node) => (
          <div
            key={node.type}
            draggable
            onDragStart={(e) => onDragStart(e, node.type)}
            className="group cursor-grab active:cursor-grabbing"
          >
            <div
              className={`
                p-3 rounded-xl border border-border/50 
                bg-gradient-to-br ${node.color} bg-opacity-10
                hover:border-primary/50 hover:shadow-lg
                transition-all duration-200
                flex flex-col items-center gap-1.5
              `}
            >
              <div
                className={`
                  w-8 h-8 rounded-lg bg-gradient-to-br ${node.color}
                  flex items-center justify-center text-white shadow-md
                `}
              >
                {node.icon}
              </div>
              <span className="text-xs font-medium">{node.labelZh}</span>
            </div>
          </div>
        ))}
      </div>

      <p className="text-[10px] text-muted-foreground mt-3 text-center">
        拖拽节点到画布上
      </p>
    </div>
  );
}
