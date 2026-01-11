"use client";

import { useCallback, useState } from "react";
import { ReactFlowProvider } from "@xyflow/react";
import { DndContext, DragEndEvent } from "@dnd-kit/core";
import { AgentCanvas } from "@/components/studio/agent-canvas";
import { NodePalette } from "@/components/studio/node-palette";
import { ToolsSidebar } from "@/components/studio/tools-sidebar";
import { PropertiesPanel } from "@/components/studio/properties-panel";
import { StudioHeader } from "@/components/studio/studio-header";
import { VibeBuilder } from "@/components/studio/vibe-builder";
import { useFlowStore } from "@/stores/flowStore";
import { toast } from "sonner";

/**
 * Agent Studio - Visual workflow builder for creating AI agents.
 *
 * Layout:
 * - Left sidebar: Node palette (triggers, LLM, output) and tools with Skills
 * - Center: React Flow canvas for building workflows
 * - Right sidebar: Properties panel for selected node
 */
export default function StudioPage() {
  const {
    workflowName,
    setWorkflowName,
    getWorkflowJSON,
    execution,
    setExecutionState,
    resetExecution,
    nodes,
    selectedNodeId,
    undo,
    redo,
    canUndo,
    canRedo,
    autoLayout,
  } = useFlowStore();

  const selectedNode = nodes.find((n) => n.id === selectedNodeId) || null;

  // Save workflow
  const handleSave = useCallback(async () => {
    const workflow = getWorkflowJSON();

    if (workflow.nodes.length === 0) {
      toast.error("工作流是空的", { description: "请添加一些节点后再保存" });
      return;
    }

    console.log("Saving workflow:", { name: workflowName, ...workflow });
    toast.success("保存成功", { description: "工作流已保存" });
  }, [workflowName, getWorkflowJSON]);

  // Run workflow with SSE streaming
  const handleRun = useCallback(async () => {
    const workflow = getWorkflowJSON();
    const {
      setExecutionState,
      appendNodeContent,
      updateNodeData,
      setAnimatingEdge,
    } = useFlowStore.getState();

    if (workflow.nodes.length === 0) {
      toast.error("工作流是空的", { description: "请添加一些节点后再运行" });
      return;
    }

    setExecutionState({ isRunning: true, error: undefined });

    // Find LLM and Output nodes to update their state
    const llmNode = workflow.nodes.find((n) => n.type === "llm");
    const outputNode = workflow.nodes.find((n) => n.type === "output");

    if (llmNode) {
      updateNodeData(llmNode.id, { status: "thinking", content: "" });
    }

    try {
      const baseUrl =
        process.env.NEXT_PUBLIC_AGENT_API_URL || "http://localhost:8000";
      const response = await fetch(
        `${baseUrl}/api/v1/chat/temp-workflow/stream`,
        {
          method: "POST", // Note: Backend usually expects POST for starting a stream with body
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            message: { content: "Execute workflow" },
            workflow_id: "temp-workflow",
          }),
        }
      );

      if (!response.ok) throw new Error("Failed to connect to stream");

      const reader = response.body?.getReader();
      const decoder = new TextDecoder();

      if (!reader) throw new Error("No response body");

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value);
        const lines = chunk.split("\n");

        for (const line of lines) {
          if (!line.startsWith("data: ")) continue;

          try {
            const event = JSON.parse(line.slice(6));

            if (event.type === "token" && llmNode) {
              appendNodeContent(llmNode.id, event.content);
              setAnimatingEdge(null, true); // Animate all edges for now to show flow
            } else if (event.type === "status") {
              if (llmNode) updateNodeData(llmNode.id, { status: event.status });
            } else if (event.type === "final" && outputNode) {
              updateNodeData(outputNode.id, {
                result: event.content,
                status: "completed",
              });
              setAnimatingEdge(null, false);
            }
          } catch (e) {
            console.error("Error parsing SSE event:", e);
          }
        }
      }

      setExecutionState({ isRunning: false });
      toast.success("执行完成");
    } catch (error) {
      const message = error instanceof Error ? error.message : "未知错误";
      toast.error("运行失败", { description: message });
      setExecutionState({ isRunning: false, error: message });
      setAnimatingEdge(null, false);
    }
  }, [getWorkflowJSON]);

  const handleDragEnd = useCallback((event: DragEndEvent) => {
    // Drag end is handled by the canvas component
  }, []);

  return (
    <DndContext onDragEnd={handleDragEnd}>
      <ReactFlowProvider>
        <div className="h-screen flex flex-col bg-background">
          {/* Header with save/run actions */}
          <StudioHeader
            workflowName={workflowName}
            onNameChange={setWorkflowName}
            onSave={handleSave}
            onRun={handleRun}
            onUndo={undo}
            onRedo={redo}
            onLayout={autoLayout}
            canUndo={canUndo}
            canRedo={canRedo}
            isSaving={false}
            isRunning={execution.isRunning}
          />

          <div className="flex-1 flex overflow-hidden">
            {/* Left Sidebar: Node Palette & Tools */}
            <aside className="w-80 border-r bg-background/95 backdrop-blur-sm flex flex-col overflow-hidden">
              <NodePalette />
              <div className="flex-1 overflow-hidden">
                <ToolsSidebar />
              </div>
            </aside>

            {/* Center: Canvas */}
            <main className="flex-1 relative">
              <AgentCanvas />
              <VibeBuilder />
            </main>

            {/* Right Sidebar: Properties Panel */}
            <aside className="w-80 border-l bg-background/95 backdrop-blur-sm overflow-y-auto">
              <PropertiesPanel selectedNode={selectedNode} />
            </aside>
          </div>
        </div>
      </ReactFlowProvider>
    </DndContext>
  );
}
