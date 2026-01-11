"use client";

import { useState, useRef, useEffect } from "react";
import { useParams, useRouter } from "next/navigation";
import { Send, Loader2, Bot, User, Trash2, ArrowLeft } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card } from "@/components/ui/card";
import { ScrollArea } from "@/components/ui/scroll-area";
import { toast } from "sonner";
import { cn } from "@/lib/utils";

interface Message {
  role: "user" | "assistant";
  content: string;
  timestamp: string;
}

/**
 * AgentChatPage - Real-time chat interface for interacting with an AI agent.
 * Supports session management, RAG-enhanced responses, and dynamic tool use feedback.
 */
export default function AgentChatPage() {
  const params = useParams();
  const router = useRouter();
  const id = params.id as string;

  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState<string | null>(null);

  const scrollRef = useRef<HTMLDivElement>(null);

  // Load history if any
  useEffect(() => {
    const fetchHistory = async () => {
      if (!sessionId) return;
      try {
        const res = await fetch(
          `${
            process.env.NEXT_PUBLIC_AGENT_API_URL || "http://localhost:8005"
          }/v1/agents/${id}/history/${sessionId}`
        );
        const data = await res.json();
        if (data.history) setMessages(data.history);
      } catch (e) {
        console.error("Failed to fetch history", e);
      }
    };
    fetchHistory();
  }, [id, sessionId]);

  // Scroll to bottom on new messages
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages, isLoading]);

  const handleSend = async () => {
    if (!input.trim() || isLoading) return;

    const userMsg = input.trim();
    setInput("");

    const newMessage: Message = {
      role: "user",
      content: userMsg,
      timestamp: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, newMessage]);
    setIsLoading(true);

    try {
      const response = await fetch(
        `${
          process.env.NEXT_PUBLIC_AGENT_API_URL || "http://localhost:8005"
        }/v1/agents/${id}/chat`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            content: userMsg,
            session_id: sessionId,
          }),
        }
      );

      if (!response.ok) throw new Error("Failed to get response");

      const data = await response.json();

      if (!sessionId) setSessionId(data.session_id);

      const assistantMsg: Message = {
        role: "assistant",
        content: data.response,
        timestamp: new Date().toISOString(),
      };

      setMessages((prev) => [...prev, assistantMsg]);
    } catch (error) {
      toast.error("发送失败", { description: "无法连接到 Agent 服务" });
      console.error(error);
    } finally {
      setIsLoading(false);
    }
  };

  const clearSession = async () => {
    if (!sessionId) return;
    try {
      await fetch(
        `${
          process.env.NEXT_PUBLIC_AGENT_API_URL || "http://localhost:8005"
        }/v1/agents/${id}/session/${sessionId}`,
        {
          method: "DELETE",
        }
      );
      setMessages([]);
      setSessionId(null);
      toast.success("会话已清除");
    } catch (e) {
      toast.error("清除会话失败");
    }
  };

  return (
    <div className="flex flex-col h-screen bg-background text-foreground">
      {/* Header */}
      <header className="h-16 border-b flex items-center justify-between px-6 bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60 z-10">
        <div className="flex items-center gap-4">
          <Button variant="ghost" size="icon" onClick={() => router.back()}>
            <ArrowLeft className="w-5 h-5" />
          </Button>
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center border border-primary/20">
              <Bot className="w-6 h-6 text-primary" />
            </div>
            <div>
              <h1 className="font-semibold">智能 Agent 对话</h1>
              <p className="text-[10px] text-muted-foreground flex items-center gap-1">
                <span className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
                就绪
              </p>
            </div>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={clearSession}
            disabled={!sessionId}
          >
            <Trash2 className="w-4 h-4 mr-2" />
            清除会话
          </Button>
        </div>
      </header>

      {/* Chat Area */}
      <main className="flex-1 overflow-hidden relative flex flex-col items-center">
        <ScrollArea ref={scrollRef} className="w-full flex-1 p-4 md:p-8">
          <div className="max-w-4xl mx-auto space-y-6 pb-20">
            {messages.length === 0 && !isLoading && (
              <div className="flex flex-col items-center justify-center py-20 text-center opacity-50">
                <Bot className="w-16 h-16 mb-4 text-primary" />
                <h2 className="text-xl font-medium">你好！我是你的智能助手</h2>
                <p className="text-sm max-w-sm mt-2">
                  你可以问我任何问题，我会根据我的技能和知识库为你提供帮助。
                </p>
              </div>
            )}

            {messages.map((msg, i) => (
              <div
                key={i}
                className={cn(
                  "flex gap-4 p-4 rounded-2xl transition-all animate-in fade-in slide-in-from-bottom-2",
                  msg.role === "assistant"
                    ? "bg-muted/30 border border-muted"
                    : "bg-primary/5 ml-auto flex-row-reverse"
                )}
              >
                <div
                  className={cn(
                    "w-8 h-8 rounded-full flex items-center justify-center shrink-0 border",
                    msg.role === "assistant"
                      ? "bg-primary/10 text-primary border-primary/20"
                      : "bg-user/10 border-foreground/10"
                  )}
                >
                  {msg.role === "assistant" ? (
                    <Bot className="w-4 h-4" />
                  ) : (
                    <User className="w-4 h-4" />
                  )}
                </div>
                <div className="flex-1 space-y-1">
                  <p className="text-sm leading-relaxed whitespace-pre-wrap">
                    {msg.content}
                  </p>
                  <p className="text-[10px] opacity-40">
                    {new Date(msg.timestamp).toLocaleTimeString()}
                  </p>
                </div>
              </div>
            ))}

            {isLoading && (
              <div className="flex gap-4 p-4 rounded-2xl bg-muted/30 border border-muted animate-pulse">
                <div className="w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center shrink-0">
                  <Bot className="w-4 h-4 text-primary" />
                </div>
                <div className="flex-1 py-2">
                  <div className="h-4 bg-muted-foreground/10 rounded w-1/4 mb-2" />
                  <div className="h-4 bg-muted-foreground/10 rounded w-3/4" />
                </div>
              </div>
            )}
          </div>
        </ScrollArea>

        {/* Input Area */}
        <div className="absolute bottom-0 left-0 right-0 p-4 md:p-8 bg-gradient-to-t from-background via-background to-transparent pointer-events-none">
          <div className="max-w-4xl mx-auto pointer-events-auto">
            <Card className="p-1 px-2 border shadow-2xl flex items-center gap-2 bg-background/80 backdrop-blur">
              <Input
                placeholder="在此输入你的问题..."
                className="border-0 focus-visible:ring-0 shadow-none h-12"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && handleSend()}
              />
              <Button
                size="icon"
                className="h-10 w-10 shrink-0"
                onClick={handleSend}
                disabled={isLoading || !input.trim()}
              >
                {isLoading ? (
                  <Loader2 className="w-5 h-5 animate-spin" />
                ) : (
                  <Send className="w-5 h-5" />
                )}
              </Button>
            </Card>
            <p className="text-center text-[10px] text-muted-foreground mt-2">
              DeepSeek AI 强力驱动 · 按 Enter 发送
            </p>
          </div>
        </div>
      </main>
    </div>
  );
}
