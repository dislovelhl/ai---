"use client";

import { useState } from "react";
import { useQuery, useMutation } from "@tanstack/react-query";
import { getCategories, createTool } from "@/lib/api";
import { Navbar } from "@/components/layout/navbar";
import { Footer } from "@/components/layout/footer";
import { Button } from "@/components/ui/button";
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
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  CardDescription,
} from "@/components/ui/card";
import { Loader2, Send, CheckCircle2, AlertCircle } from "lucide-react";
import { useRouter } from "next/navigation";

export default function SubmitToolPage() {
  const router = useRouter();
  const [submitted, setSubmitted] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const { data: categories, isLoading: catsLoading } = useQuery({
    queryKey: ["categories"],
    queryFn: getCategories,
  });

  const mutation = useMutation({
    mutationFn: createTool,
    onSuccess: () => {
      setSubmitted(true);
      setTimeout(() => {
        router.push("/tools");
      }, 3000);
    },
    onError: (err: any) => {
      setError(err.message || "提交失败，请稍后重试。");
    },
  });

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setError(null);
    const formData = new FormData(e.currentTarget);

    const name = formData.get("name") as string;
    const url = formData.get("url") as string;
    const description = formData.get("description") as string;
    const category_id = formData.get("category_id") as string;

    if (!name || !url || !category_id) {
      setError("请填写所有必填字段。");
      return;
    }

    // Simple slugify
    const slug = name
      .toLowerCase()
      .replace(/[^\w\s-]/g, "")
      .replace(/[\s_-]+/g, "-")
      .replace(/^-+|-+$/g, "");

    mutation.mutate({
      name,
      slug,
      url,
      description,
      category_id,
      scenario_ids: [], // Start with empty scenarios
    });
  };

  if (submitted) {
    return (
      <div className="flex flex-col min-h-screen">
        <Navbar />
        <main className="flex-1 flex items-center justify-center p-4">
          <Card className="max-w-md w-full glass border-2 rounded-[2rem] text-center p-8">
            <CheckCircle2 className="w-16 h-16 text-emerald-500 mx-auto mb-6" />
            <CardTitle className="text-3xl font-black mb-4">
              提交成功！
            </CardTitle>
            <CardDescription className="text-lg">
              感谢您的分享！我们的管理员将尽快审核并完善该工具的信息。
              <br />
              即将跳转回工具列表...
            </CardDescription>
          </Card>
        </main>
        <Footer />
      </div>
    );
  }

  return (
    <div className="flex flex-col min-h-screen">
      <Navbar />
      <main className="flex-1 py-12 px-4">
        <div className="max-w-2xl mx-auto">
          <header className="text-center mb-12">
            <h1 className="text-4xl font-black tracking-tight mb-4">
              分享 AI 工具
            </h1>
            <p className="text-muted-foreground text-lg">
              发现了好用的 AI 工具？分享给社区，让更多人受益。
            </p>
          </header>

          <Card className="glass border-2 rounded-[3rem] overflow-hidden shadow-2xl">
            <CardHeader className="p-8 md:p-10 border-b border-primary/5">
              <CardTitle>工具基本信息</CardTitle>
              <CardDescription>
                我们将自动抓取并补充该工具的详细描述与截图。
              </CardDescription>
            </CardHeader>
            <CardContent className="p-8 md:p-10">
              <form onSubmit={handleSubmit} className="space-y-8">
                <div className="space-y-2">
                  <label className="text-sm font-bold ml-1">工具名称 *</label>
                  <Input
                    name="name"
                    placeholder="例如：ChatGPT"
                    required
                    className="h-14 rounded-2xl glass border-2 focus:border-primary transition-all text-lg"
                  />
                </div>

                <div className="space-y-2">
                  <label className="text-sm font-bold ml-1">官网链接 *</label>
                  <Input
                    name="url"
                    type="url"
                    placeholder="https://example.com"
                    required
                    className="h-14 rounded-2xl glass border-2 focus:border-primary transition-all text-lg"
                  />
                </div>

                <div className="space-y-2">
                  <label className="text-sm font-bold ml-1">所属分类 *</label>
                  <Select name="category_id" required>
                    <SelectTrigger className="h-14 rounded-2xl glass border-2 focus:border-primary transition-all text-lg">
                      <SelectValue placeholder="请选择一个分类" />
                    </SelectTrigger>
                    <SelectContent className="rounded-2xl glass border-2">
                      {catsLoading ? (
                        <div className="p-4 flex justify-center">
                          <Loader2 className="w-6 h-6 animate-spin text-primary" />
                        </div>
                      ) : (
                        categories?.map((cat) => (
                          <SelectItem
                            key={cat.id}
                            value={cat.id}
                            className="rounded-xl focus:bg-primary/10"
                          >
                            {cat.name}
                          </SelectItem>
                        ))
                      )}
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2">
                  <label className="text-sm font-bold ml-1">简短描述</label>
                  <Textarea
                    name="description"
                    placeholder="简单介绍一下这个工具的主要功能..."
                    className="min-h-32 rounded-2xl glass border-2 focus:border-primary transition-all text-lg"
                  />
                </div>

                {error && (
                  <div className="flex items-center gap-2 p-4 bg-destructive/10 text-destructive rounded-2xl border border-destructive/20 animate-in fade-in slide-in-from-top-2">
                    <AlertCircle className="w-5 h-5 flex-shrink-0" />
                    <p className="font-medium">{error}</p>
                  </div>
                )}

                <Button
                  type="submit"
                  size="lg"
                  disabled={mutation.isPending}
                  className="w-full h-16 rounded-[2rem] text-xl font-black shadow-xl shadow-primary/20 hover:scale-[1.02] transition-all"
                >
                  {mutation.isPending ? (
                    <>
                      正在提交...{" "}
                      <Loader2 className="ml-2 w-6 h-6 animate-spin" />
                    </>
                  ) : (
                    <>
                      提交审核 <Send className="ml-2 w-6 h-6" />
                    </>
                  )}
                </Button>
              </form>
            </CardContent>
          </Card>
        </div>
      </main>
      <Footer />
    </div>
  );
}
