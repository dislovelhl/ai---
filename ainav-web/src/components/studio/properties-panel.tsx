"use client";

import { AppNode } from "@/stores/flowStore";
import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  MessageSquare,
  Brain,
  Zap,
  ArrowRightCircle,
  Shuffle,
} from "lucide-react";

interface PropertiesPanelProps {
  selectedNode: AppNode | null;
}

/**
 * PropertiesPanel - Right sidebar for editing selected node properties.
 */
export function PropertiesPanel({ selectedNode }: PropertiesPanelProps) {
  if (!selectedNode) {
    return (
      <div className="p-6 h-full flex flex-col items-center justify-center text-center text-muted-foreground">
        <div className="w-12 h-12 rounded-full bg-muted/50 flex items-center justify-center mb-4">
          <MessageSquare className="w-6 h-6" />
        </div>
        <p className="text-sm">选择一个节点查看其属性</p>
        <p className="text-xs mt-1">点击画布上的节点进行编辑</p>
      </div>
    );
  }

  const nodeTypeInfo = getNodeTypeInfo(selectedNode.type);

  return (
    <div className="p-4 space-y-6">
      {/* Node Type Header */}
      <div className="flex items-center gap-3 pb-4 border-b">
        <div
          className={`w-10 h-10 rounded-lg bg-gradient-to-br ${nodeTypeInfo.color} flex items-center justify-center text-white shadow-md`}
        >
          {nodeTypeInfo.icon}
        </div>
        <div>
          <h3 className="font-semibold">{nodeTypeInfo.label}</h3>
          <p className="text-xs text-muted-foreground">{selectedNode.id}</p>
        </div>
      </div>

      {/* Common Properties */}
      <div className="space-y-4">
        <div className="space-y-2">
          <Label htmlFor="node-label">节点标签</Label>
          <Input
            id="node-label"
            placeholder="给节点起个名字..."
            defaultValue={(selectedNode.data as any)?.label || ""}
          />
        </div>
      </div>

      {/* Type-specific Properties */}
      {selectedNode.type === "input" && (
        <InputNodeProperties node={selectedNode} />
      )}
      {selectedNode.type === "llm" && <LLMNodeProperties node={selectedNode} />}
      {selectedNode.type === "skill" && (
        <SkillNodeProperties node={selectedNode} />
      )}
      {selectedNode.type === "output" && (
        <OutputNodeProperties node={selectedNode} />
      )}
      {selectedNode.type === "transform" && (
        <TransformNodeProperties node={selectedNode} />
      )}
    </div>
  );
}

// Node type info helper
function getNodeTypeInfo(type: string) {
  const types: Record<
    string,
    { label: string; color: string; icon: React.ReactNode }
  > = {
    input: {
      label: "输入节点",
      color: "from-green-500 to-emerald-600",
      icon: <MessageSquare className="w-5 h-5" />,
    },
    llm: {
      label: "LLM 节点",
      color: "from-violet-500 to-purple-600",
      icon: <Brain className="w-5 h-5" />,
    },
    skill: {
      label: "技能节点",
      color: "from-orange-500 to-amber-600",
      icon: <Zap className="w-5 h-5" />,
    },
    output: {
      label: "输出节点",
      color: "from-blue-500 to-cyan-600",
      icon: <ArrowRightCircle className="w-5 h-5" />,
    },
    transform: {
      label: "转换节点",
      color: "from-yellow-500 to-amber-500",
      icon: <Shuffle className="w-5 h-5" />,
    },
  };

  return (
    types[type] || {
      label: type,
      color: "from-gray-500 to-gray-600",
      icon: null,
    }
  );
}

// Type-specific property editors
function InputNodeProperties({ node }: { node: AppNode }) {
  return (
    <div className="space-y-4">
      <div className="space-y-2">
        <Label>输入类型</Label>
        <Select defaultValue="text">
          <SelectTrigger>
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="text">文本</SelectItem>
            <SelectItem value="number">数字</SelectItem>
            <SelectItem value="json">JSON 对象</SelectItem>
            <SelectItem value="file">文件</SelectItem>
          </SelectContent>
        </Select>
      </div>
      <div className="space-y-2">
        <Label>默认值</Label>
        <Input placeholder="输入默认值..." />
      </div>
    </div>
  );
}

function LLMNodeProperties({ node }: { node: AppNode }) {
  return (
    <div className="space-y-4">
      <div className="space-y-2">
        <Label>模型</Label>
        <Select defaultValue="deepseek-chat">
          <SelectTrigger>
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="deepseek-chat">DeepSeek Chat</SelectItem>
            <SelectItem value="deepseek-coder">DeepSeek Coder</SelectItem>
          </SelectContent>
        </Select>
      </div>
      <div className="space-y-2">
        <Label>系统提示词</Label>
        <Textarea
          placeholder="你是一个有帮助的助手..."
          rows={3}
          className="resize-none"
        />
      </div>
      <div className="space-y-2">
        <Label>用户提示词模板</Label>
        <Textarea
          placeholder="使用 {{input}} 引用输入数据..."
          rows={4}
          className="resize-none font-mono text-sm"
        />
        <p className="text-[10px] text-muted-foreground">
          支持变量: {"{{input}}"}, {"{{field.name}}"}
        </p>
      </div>
      <div className="space-y-2">
        <Label>温度 (0-2)</Label>
        <Input type="number" min="0" max="2" step="0.1" defaultValue="0.7" />
      </div>
    </div>
  );
}

function SkillNodeProperties({ node }: { node: AppNode }) {
  const skill = (node.data as any)?.skill;

  return (
    <div className="space-y-4">
      {skill ? (
        <>
          <div className="p-3 rounded-lg bg-muted/50 space-y-2">
            <p className="font-medium text-sm">{skill.name}</p>
            <p className="text-xs text-muted-foreground">{skill.description}</p>
            <div className="flex gap-2 text-[10px]">
              <span className="px-2 py-0.5 rounded bg-primary/10 text-primary">
                {skill.http_method}
              </span>
              <span className="px-2 py-0.5 rounded bg-muted">
                {skill.auth_type}
              </span>
            </div>
          </div>
          <div className="space-y-2">
            <Label>输入映射</Label>
            <Textarea
              placeholder="JSON 格式的参数映射..."
              rows={4}
              className="resize-none font-mono text-sm"
            />
          </div>
        </>
      ) : (
        <div className="text-center py-4 text-muted-foreground text-sm">
          请从左侧拖拽一个工具到此节点
        </div>
      )}
    </div>
  );
}

function OutputNodeProperties({ node }: { node: AppNode }) {
  return (
    <div className="space-y-4">
      <div className="space-y-2">
        <Label>输出格式</Label>
        <Select defaultValue="auto">
          <SelectTrigger>
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="auto">自动</SelectItem>
            <SelectItem value="text">纯文本</SelectItem>
            <SelectItem value="json">JSON</SelectItem>
            <SelectItem value="markdown">Markdown</SelectItem>
          </SelectContent>
        </Select>
      </div>
    </div>
  );
}

function TransformNodeProperties({ node }: { node: AppNode }) {
  return (
    <div className="space-y-4">
      <div className="space-y-2">
        <Label>转换类型</Label>
        <Select defaultValue="extract">
          <SelectTrigger>
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="passthrough">透传</SelectItem>
            <SelectItem value="extract">提取字段</SelectItem>
            <SelectItem value="template">模板</SelectItem>
            <SelectItem value="json_parse">JSON 解析</SelectItem>
            <SelectItem value="json_stringify">JSON 序列化</SelectItem>
            <SelectItem value="array_join">数组合并</SelectItem>
          </SelectContent>
        </Select>
      </div>
      <div className="space-y-2">
        <Label>字段路径</Label>
        <Input
          placeholder="data.results.0.name"
          className="font-mono text-sm"
        />
        <p className="text-[10px] text-muted-foreground">
          使用点号访问嵌套字段
        </p>
      </div>
    </div>
  );
}
