"use client";

import { useState } from "react";
import { Sparkles, Loader2, Send } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { useFlowStore } from "@/stores/flowStore";
import { toast } from "sonner";

export function VibeBuilder() {
  const [prompt, setPrompt] = useState("");
  const [isGenerating, setIsGenerating] = useState(false);
  const { setPreview, commitPreview, clearPreview, preview, workflowName } =
    useFlowStore();

  const handleGenerate = async () => {
    if (!prompt.trim()) return;

    setIsGenerating(true);
    try {
      const { nodes, edges } = useFlowStore.getState();
      const baseUrl =
        process.env.NEXT_PUBLIC_AGENT_API_URL || "http://localhost:8000";

      const response = await fetch(`${baseUrl}/api/v1/workflows/generate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          prompt,
          current_graph: nodes.length > 0 ? { nodes, edges } : null,
        }),
      });

      if (!response.ok) throw new Error("生成失败");

      const data = await response.json();

      // Mark these nodes as previews
      const previewNodes = data.nodes.map((node: any, index: number) => ({
        ...node,
        position: node.position || { x: index * 300, y: 150 },
        data: { ...node.data, isPreview: true },
      }));

      const previewEdges = data.edges.map((edge: any) => ({
        ...edge,
        animated: true,
        style: {
          stroke: "#8b5cf6",
          strokeWidth: 2,
          opacity: 0.6,
          strokeDasharray: "5,5",
        },
      }));

      setPreview(previewNodes, previewEdges);

      toast.info(nodes.length > 0 ? "已发现优化方案" : "工作流草图已就绪", {
        description: "请查看预览并决定是否应用",
      });
      setPrompt("");
    } catch (error) {
      toast.error("生成失败", {
        description: error instanceof Error ? error.message : "请稍后再试",
      });
    } finally {
      setIsGenerating(false);
    }
  };

  if (preview.isVisible) {
    return (
      <div className="absolute bottom-6 left-1/2 -translate-x-1/2 z-50 w-full max-w-md px-4">
        <div className="bg-background/90 backdrop-blur-xl border border-primary/30 shadow-2xl rounded-2xl p-4 flex flex-col gap-4 ring-1 ring-white/20 animate-in fade-in slide-in-from-bottom-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-violet-500/20 flex items-center justify-center text-violet-500">
              <Sparkles className="w-5 h-5 animate-pulse" />
            </div>
            <div>
              <h4 className="text-sm font-semibold">确认 AI 建议?</h4>
              <p className="text-xs text-muted-foreground">
                您可以预览即将发生的更改
              </p>
            </div>
          </div>
          <div className="flex gap-2">
            <Button
              variant="outline"
              className="flex-1 rounded-xl"
              onClick={clearPreview}
            >
              放弃更改
            </Button>
            <Button
              className="flex-1 rounded-xl bg-gradient-to-r from-violet-500 to-purple-600 hover:from-violet-600 hover:to-purple-700"
              onClick={commitPreview}
            >
              应用建议
            </Button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="absolute bottom-6 left-1/2 -translate-x-1/2 z-50 w-full max-w-xl px-4">
      <div className="bg-background/80 backdrop-blur-md border border-primary/20 shadow-2xl rounded-2xl p-2 flex items-center gap-2 ring-1 ring-white/10">
        <div className="flex items-center justify-center w-10 h-10 rounded-xl bg-gradient-to-br from-violet-500 to-purple-600 text-white shadow-lg shrink-0">
          <Sparkles
            className={`w-5 h-5 ${isGenerating ? "animate-pulse" : ""}`}
          />
        </div>

        <Input
          placeholder="描述你想要构建的工作流... (例如: 研究报告生成助手)"
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleGenerate()}
          className="flex-1 border-none bg-transparent focus-visible:ring-0 text-sm h-10"
          disabled={isGenerating}
        />

        <Button
          onClick={handleGenerate}
          disabled={!prompt.trim() || isGenerating}
          size="sm"
          className="rounded-xl h-10 px-4 bg-gradient-to-r from-violet-500 to-purple-600 hover:from-violet-600 hover:to-purple-700 shadow-md group"
        >
          {isGenerating ? (
            <Loader2 className="w-4 h-4 animate-spin" />
          ) : (
            <>
              <span className="mr-2">生成</span>
              <Send className="w-3.5 h-3.5 group-hover:translate-x-0.5 group-hover:-translate-y-0.5 transition-transform" />
            </>
          )}
        </Button>
      </div>
    </div>
  );
}
