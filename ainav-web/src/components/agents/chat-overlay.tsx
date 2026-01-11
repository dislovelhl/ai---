"use client";

import { useState, useEffect, useRef } from "react";
import { X, Send, Bot, User, Sparkles, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { ScrollArea } from "@/components/ui/scroll-area";
import { AgentWorkflow } from "@/lib/types";
import { cn } from "@/lib/utils";

interface Message {
  role: "user" | "assistant";
  content: string;
}

interface ChatOverlayProps {
  agent: AgentWorkflow | null;
  isOpen: boolean;
  onClose: () => void;
}

export function ChatOverlay({ agent, isOpen, onClose }: ChatOverlayProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);

  const suggestions = [
    "这个 Agent 能做什么？",
    "如何克隆并运行？",
    "它支持哪些模型？",
  ];

  useEffect(() => {
    if (isOpen && agent) {
      setMessages([
        {
          role: "assistant",
          content: `你好！我是 ${
            agent.name_zh || agent.name
          }。我是专门为您设计的智能助手。你可以问我关于我的功能或如何使用我。`,
        },
      ]);
    }
  }, [isOpen, agent]);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim() || !agent) return;

    const userMessage: Message = { role: "user", content: input };
    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setIsLoading(true);

    try {
      const response = await fetch(
        `${
          process.env.NEXT_PUBLIC_AGENT_API_URL || "http://localhost:8005"
        }/v1/workflows/${agent.id}/chat`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ message: input }),
        }
      );

      if (response.ok) {
        const data = await response.json();
        setMessages((prev) => [
          ...prev,
          { role: "assistant", content: data.response },
        ]);
      } else {
        throw new Error("Failed to get response");
      }
    } catch (error) {
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: "抱歉，我现在无法响应。请稍后再试。" },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  if (!isOpen || !agent) return null;

  return (
    <div className="fixed inset-y-0 right-0 w-full sm:w-[450px] bg-slate-950/95 backdrop-blur-2xl border-l border-white/10 shadow-2xl z-[100] animate-in slide-in-from-right duration-500 flex flex-col">
      {/* Header */}
      <div className="p-6 border-b border-white/5 flex items-center justify-between bg-white/5">
        <div className="flex items-center gap-4">
          <div className="w-10 h-10 rounded-xl bg-primary/20 flex items-center justify-center text-primary border border-primary/20">
            <Bot className="w-6 h-6" />
          </div>
          <div>
            <h3 className="font-bold text-lg">{agent.name_zh || agent.name}</h3>
            <p className="text-xs text-slate-400">正在与 Agent 对话</p>
          </div>
        </div>
        <Button
          variant="ghost"
          size="icon"
          onClick={onClose}
          className="hover:bg-white/10"
        >
          <X className="w-5 h-5" />
        </Button>
      </div>

      {/* Messages */}
      <ScrollArea className="flex-1 p-6 space-y-6" viewportRef={scrollRef}>
        <div className="space-y-6">
          {messages.map((msg, i) => (
            <div
              key={i}
              className={cn(
                "flex gap-4 max-w-[85%]",
                msg.role === "user" ? "ml-auto flex-row-reverse" : "mr-auto"
              )}
            >
              <div
                className={cn(
                  "w-8 h-8 rounded-lg flex items-center justify-center shrink-0",
                  msg.role === "assistant"
                    ? "bg-primary/20 text-primary border border-primary/10"
                    : "bg-slate-800 text-slate-400"
                )}
              >
                {msg.role === "assistant" ? (
                  <Bot className="w-4 h-4" />
                ) : (
                  <User className="w-4 h-4" />
                )}
              </div>
              <div
                className={cn(
                  "p-4 rounded-2xl text-sm leading-relaxed",
                  msg.role === "assistant"
                    ? "bg-white/5 border border-white/5 text-slate-200"
                    : "bg-primary text-white shadow-lg shadow-primary/20"
                )}
              >
                {msg.content}
              </div>
            </div>
          ))}
          {isLoading && (
            <div className="flex gap-4 mr-auto animate-pulse">
              <div className="w-8 h-8 rounded-lg bg-primary/20 flex items-center justify-center border border-primary/10">
                <Loader2 className="w-4 h-4 text-primary animate-spin" />
              </div>
              <div className="p-4 rounded-2xl bg-white/5 border border-white/5 text-slate-500 italic text-xs">
                Agent 正在思考中...
              </div>
            </div>
          )}
        </div>
      </ScrollArea>

      {/* Input */}
      <div className="p-6 border-t border-white/5 bg-white/5">
        <div className="flex flex-wrap gap-2 mb-4">
          {suggestions.map((s) => (
            <button
              key={s}
              onClick={() => {
                setInput(s);
              }}
              className="text-[10px] px-3 py-1.5 rounded-full bg-white/5 border border-white/10 text-slate-400 hover:bg-primary/20 hover:text-primary transition-colors"
            >
              {s}
            </button>
          ))}
        </div>
        <div className="relative group">
          <div className="absolute -inset-1 bg-gradient-to-r from-primary/20 to-purple-500/20 rounded-xl blur opacity-25 group-focus-within:opacity-100 transition duration-1000" />
          <div className="relative flex gap-2">
            <Input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="输入你的问题..."
              className="h-12 bg-slate-900 border-white/10 rounded-xl focus-visible:ring-primary/50"
              onKeyDown={(e) => e.key === "Enter" && handleSend()}
            />
            <Button
              size="icon"
              className="h-12 w-12 rounded-xl shrink-0"
              onClick={handleSend}
              disabled={isLoading}
            >
              <Send className="w-5 h-5" />
            </Button>
          </div>
        </div>
        <p className="mt-4 text-[10px] text-center text-slate-500 flex items-center justify-center gap-1">
          <Sparkles className="w-3 h-3" /> Powered by DeepSeek-V3 Engine
        </p>
      </div>
    </div>
  );
}
