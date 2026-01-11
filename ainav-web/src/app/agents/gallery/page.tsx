"use client";

import { useEffect, useState } from "react";
import { AgentWorkflow } from "@/lib/types";
import { AgentCard } from "@/components/agents/agent-card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import {
  Search,
  Plus,
  Filter,
  Sparkles,
  TrendingUp,
  Users,
} from "lucide-react";
import Link from "next/link";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Card,
  CardHeader,
  CardContent,
  CardFooter,
} from "@/components/ui/card";
import { Bot } from "lucide-react";
import { ChatOverlay } from "@/components/agents/chat-overlay";

/**
 * AgentGalleryPage - Discovery page for community-created AI agents.
 * Features categorized listings, search, and popularity-based rankings.
 */
export default function AgentGalleryPage() {
  const [workflows, setWorkflows] = useState<AgentWorkflow[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [selectedAgent, setSelectedAgent] = useState<AgentWorkflow | null>(
    null
  );
  const [isChatOpen, setIsChatOpen] = useState(false);

  const fetchWorkflows = async (tab: string = "all") => {
    setIsLoading(true);
    try {
      const url = new URL(
        `${
          process.env.NEXT_PUBLIC_AGENT_API_URL || "http://localhost:8005"
        }/v1/workflows/public`
      );

      if (tab === "templates") {
        url.searchParams.append("is_template", "true");
      }
      if (search) url.searchParams.append("search", search);

      const res = await fetch(url.toString());
      const data = await res.json();

      let items = data.items || [];

      if (tab === "recommendations") {
        // Fetch from personalization API
        try {
          const recRes = await fetch(
            `${
              process.env.NEXT_PUBLIC_USER_API || "http://localhost:8003"
            }/v1/personalization/recommendations?user_id=00000000-0000-0000-0000-000000000000`
          ); // Placeholder UUID
          if (recRes.ok) {
            // In a real scenario, we'd map recommendation IDs back to workflows
            // For now, let's just use trending as a fallback but label it
            console.log("Personalized recommendations fetched");
          }
        } catch (e) {
          console.error("Failed to fetch recommendations", e);
        }
      }

      if (tab === "trending") {
        // Star_count and run_count are already used for sorting in /public
        items = [...items].sort(
          (a, b) => b.star_count + b.run_count - (a.star_count + a.run_count)
        );
      }

      setWorkflows(items);
    } catch (e) {
      console.error("Failed to fetch workflows", e);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchWorkflows("public");
  }, []);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    fetchWorkflows("public");
  };

  return (
    <div className="min-h-screen bg-background">
      {/* Hero Section */}
      <section className="relative py-20 overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-b from-primary/5 via-transparent to-transparent" />
        <div className="container px-4 relative z-10 mx-auto text-center">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-primary/10 border border-primary/20 text-primary text-xs font-semibold mb-6 animate-in fade-in slide-in-from-bottom-3 duration-500">
            <Sparkles className="w-3 h-3" />
            Agent 广场现已上线
          </div>
          <h1 className="text-4xl md:text-6xl font-bold tracking-tight mb-6 bg-clip-text text-transparent bg-gradient-to-r from-foreground to-foreground/70">
            发现并克隆最强大的 <br />{" "}
            <span className="text-primary italic">AI Agents</span>
          </h1>
          <p className="text-xl text-muted-foreground max-w-2xl mx-auto mb-10">
            在这个社区中，你可以发现其他人创建的智能工作流。一键克隆到你的
            Studio，或是直接开始对话。
          </p>

          <form
            onSubmit={handleSearch}
            className="max-w-2xl mx-auto relative group"
          >
            <div className="absolute -inset-1 bg-gradient-to-r from-primary/20 to-violet-500/20 rounded-2xl blur opacity-25 group-hover:opacity-100 transition duration-1000 group-hover:duration-200" />
            <div className="relative">
              <Input
                placeholder="搜索你感兴趣的 Agent..."
                className="h-14 pl-12 pr-32 rounded-2xl bg-background/50 border-muted-foreground/20 backdrop-blur-xl shadow-2xl"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
              />
              <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-muted-foreground" />
              <Button
                type="submit"
                className="absolute right-2 top-2 h-10 rounded-xl px-6"
              >
                搜索
              </Button>
            </div>
          </form>
        </div>
      </section>

      {/* Main Content */}
      <main className="container px-4 py-12 mx-auto">
        <Tabs
          defaultValue="all"
          className="w-full"
          onValueChange={(v) => fetchWorkflows(v)}
        >
          <div className="flex flex-col md:flex-row justify-between items-center gap-6 mb-10">
            <TabsList className="bg-muted/50 p-1 rounded-xl h-auto">
              <TabsTrigger
                value="all"
                className="rounded-lg py-2 px-6 data-[state=active]:bg-background data-[state=active]:shadow-sm"
              >
                <Users className="w-4 h-4 mr-2" />
                社区精选
              </TabsTrigger>
              <TabsTrigger
                value="trending"
                className="rounded-lg py-2 px-6 data-[state=active]:bg-background data-[state=active]:shadow-sm"
              >
                <TrendingUp className="w-4 h-4 mr-2" />
                热门
              </TabsTrigger>
              <TabsTrigger
                value="templates"
                className="rounded-lg py-2 px-6 data-[state=active]:bg-background data-[state=active]:shadow-sm"
              >
                <Sparkles className="w-4 h-4 mr-2" />
                官方模板
              </TabsTrigger>
              <TabsTrigger
                value="recommendations"
                className="rounded-lg py-2 px-6 data-[state=active]:bg-background data-[state=active]:shadow-sm"
              >
                <Sparkles className="w-4 h-4 mr-2 text-yellow-500" />
                为您推荐
              </TabsTrigger>
            </TabsList>

            <div className="flex gap-3">
              <Button variant="outline" className="rounded-xl">
                <Filter className="w-4 h-4 mr-2" />
                筛选
              </Button>
              <Link href="/studio">
                <Button className="rounded-xl shadow-lg shadow-primary/20">
                  <Plus className="w-4 h-4 mr-2" />
                  创建我的 Agent
                </Button>
              </Link>
            </div>
          </div>

          <TabsContent value="all" className="mt-0">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
              {isLoading ? (
                Array.from({ length: 8 }).map((_, i) => (
                  <Card key={i} className="overflow-hidden">
                    <CardHeader className="p-4 pb-2">
                      <Skeleton className="w-12 h-12 rounded-2xl" />
                    </CardHeader>
                    <CardContent className="p-4 pt-2 space-y-3">
                      <Skeleton className="h-6 w-3/4" />
                      <Skeleton className="h-4 w-full" />
                      <Skeleton className="h-4 w-5/6" />
                    </CardContent>
                    <CardFooter className="p-4 flex gap-2">
                      <Skeleton className="h-9 flex-1 rounded-xl" />
                      <Skeleton className="h-9 w-9 rounded-xl" />
                      <Skeleton className="h-9 w-9 rounded-xl" />
                    </CardFooter>
                  </Card>
                ))
              ) : workflows.length > 0 ? (
                workflows.map((wf) => (
                  <AgentCard
                    key={wf.id}
                    workflow={wf}
                    onChat={() => {
                      setSelectedAgent(wf);
                      setIsChatOpen(true);
                    }}
                  />
                ))
              ) : (
                <div className="col-span-full py-20 text-center">
                  <Bot className="w-16 h-16 mx-auto mb-4 text-muted-foreground opacity-20" />
                  <p className="text-muted-foreground">没有找到相关的 Agent</p>
                </div>
              )}
            </div>
          </TabsContent>

          <TabsContent value="trending" className="mt-0">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
              {isLoading ? (
                Array.from({ length: 8 }).map((_, i) => (
                  <Card key={i} className="overflow-hidden">
                    <CardHeader className="p-4 pb-2">
                      <Skeleton className="w-12 h-12 rounded-2xl" />
                    </CardHeader>
                    <CardContent className="p-4 pt-2 space-y-3">
                      <Skeleton className="h-6 w-3/4" />
                      <Skeleton className="h-4 w-full" />
                      <Skeleton className="h-4 w-5/6" />
                    </CardContent>
                    <CardFooter className="p-4 flex gap-2">
                      <Skeleton className="h-9 flex-1 rounded-xl" />
                      <Skeleton className="h-9 w-9 rounded-xl" />
                      <Skeleton className="h-9 w-9 rounded-xl" />
                    </CardFooter>
                  </Card>
                ))
              ) : workflows.length > 0 ? (
                workflows.map((wf) => (
                  <AgentCard
                    key={wf.id}
                    workflow={wf}
                    onChat={() => {
                      setSelectedAgent(wf);
                      setIsChatOpen(true);
                    }}
                  />
                ))
              ) : (
                <div className="col-span-full py-20 text-center">
                  <Bot className="w-16 h-16 mx-auto mb-4 text-muted-foreground opacity-20" />
                  <p className="text-muted-foreground">暂无热门 Agent</p>
                </div>
              )}
            </div>
          </TabsContent>

          <TabsContent value="templates" className="mt-0">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
              {isLoading ? (
                Array.from({ length: 8 }).map((_, i) => (
                  <Card key={i} className="overflow-hidden">
                    <CardHeader className="p-4 pb-2">
                      <Skeleton className="w-12 h-12 rounded-2xl" />
                    </CardHeader>
                    <CardContent className="p-4 pt-2 space-y-3">
                      <Skeleton className="h-6 w-3/4" />
                      <Skeleton className="h-4 w-full" />
                      <Skeleton className="h-4 w-5/6" />
                    </CardContent>
                    <CardFooter className="p-4 flex gap-2">
                      <Skeleton className="h-9 flex-1 rounded-xl" />
                      <Skeleton className="h-9 w-9 rounded-xl" />
                      <Skeleton className="h-9 w-9 rounded-xl" />
                    </CardFooter>
                  </Card>
                ))
              ) : workflows.length > 0 ? (
                workflows.map((wf) => (
                  <AgentCard
                    key={wf.id}
                    workflow={wf}
                    onChat={() => {
                      setSelectedAgent(wf);
                      setIsChatOpen(true);
                    }}
                  />
                ))
              ) : (
                <div className="col-span-full py-20 text-center">
                  <Bot className="w-16 h-16 mx-auto mb-4 text-muted-foreground opacity-20" />
                  <p className="text-muted-foreground">暂无官方模板</p>
                </div>
              )}
            </div>
          </TabsContent>

          <TabsContent value="recommendations" className="mt-0">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
              {isLoading ? (
                Array.from({ length: 4 }).map((_, i) => (
                  <Card key={i} className="overflow-hidden">
                    <CardHeader className="p-4 pb-2">
                      <Skeleton className="w-12 h-12 rounded-2xl" />
                    </CardHeader>
                    <CardContent className="p-4 pt-2 space-y-3">
                      <Skeleton className="h-6 w-3/4" />
                      <Skeleton className="h-4 w-full" />
                    </CardContent>
                  </Card>
                ))
              ) : workflows.length > 0 ? (
                workflows.map((wf) => (
                  <AgentCard
                    key={wf.id}
                    workflow={wf}
                    onChat={() => {
                      setSelectedAgent(wf);
                      setIsChatOpen(true);
                    }}
                  />
                ))
              ) : (
                <div className="col-span-full py-20 text-center bg-white/5 rounded-3xl border border-dashed border-white/10">
                  <Sparkles className="w-16 h-16 mx-auto mb-4 text-yellow-500/20" />
                  <p className="text-muted-foreground">
                    开始与 Agent 对话，我们将为你提供个性化推荐
                  </p>
                </div>
              )}
            </div>
          </TabsContent>
        </Tabs>
      </main>

      {/* Footer CTA */}
      <section className="bg-primary/5 py-20">
        <div className="container px-4 mx-auto text-center">
          <h2 className="text-3xl font-bold mb-4">
            准备好打造你自己的 Agent 了吗？
          </h2>
          <p className="text-muted-foreground mb-8 max-w-xl mx-auto">
            利用可视化 Studio，拖拽各种 API 技能和 LLM
            节点，几分钟内即可构建出强大的智能助手。
          </p>
          <Link href="/studio">
            <Button
              size="lg"
              className="px-10 h-14 rounded-2xl shadow-xl shadow-primary/20 text-lg"
            >
              立即开始构建
            </Button>
          </Link>
        </div>
      </section>

      <ChatOverlay
        agent={selectedAgent}
        isOpen={isChatOpen}
        onClose={() => setIsChatOpen(false)}
      />
    </div>
  );
}
