"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Navbar } from "@/components/layout/navbar";
import { Footer } from "@/components/layout/footer";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { register } from "@/lib/api";
import { toast } from "sonner";
import { useRouter } from "next/navigation";

export default function RegisterPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [username, setUsername] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const router = useRouter();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    try {
      await register({ email, password, username });
      toast.success("注册成功，请登录");
      router.push("/login");
    } catch (error) {
      toast.error("注册失败，邮箱可能已被占用");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col min-h-screen">
      <Navbar />
      <main className="flex-1 flex items-center justify-center p-6 bg-grid">
        <Card className="w-full max-w-md shadow-2xl border-none glass-dark text-white overflow-hidden">
          <CardHeader className="space-y-1 pb-8 text-center">
            <div className="mx-auto w-12 h-12 rounded-xl bg-primary flex items-center justify-center mb-4">
              <span className="text-2xl font-bold">A</span>
            </div>
            <CardTitle className="text-2xl font-bold">加入我们</CardTitle>
            <CardDescription className="text-gray-400">
              开启您的 AI 探索之旅，收藏并分享顶尖工具
            </CardDescription>
          </CardHeader>
          <form onSubmit={handleSubmit}>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="username" className="text-sm font-medium ml-1">
                  用户名
                </Label>
                <Input
                  id="username"
                  placeholder="ai_explorer"
                  required
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  className="bg-white/5 border-white/10 rounded-xl h-11 focus:ring-primary"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="email" className="text-sm font-medium ml-1">
                  邮箱
                </Label>
                <Input
                  id="email"
                  type="email"
                  placeholder="name@example.com"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="bg-white/5 border-white/10 rounded-xl h-11 focus:ring-primary"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="password">密码</Label>
                <Input
                  id="password"
                  type="password"
                  required
                  placeholder="至少 6 位字符"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="bg-white/5 border-white/10 rounded-xl h-11 focus:ring-primary"
                />
              </div>
            </CardContent>
            <CardFooter className="flex flex-col gap-4 mt-6">
              <Button
                className="w-full h-11 rounded-xl font-bold text-lg"
                disabled={isLoading}
              >
                {isLoading ? "正在注册..." : "立即注册"}
              </Button>
              <p className="text-center text-sm text-gray-400">
                已有账号？{" "}
                <a href="/login" className="text-primary hover:underline">
                  返回登录
                </a>
              </p>
            </CardFooter>
          </form>
        </Card>
      </main>
      <Footer />
    </div>
  );
}
