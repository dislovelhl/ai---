"use client";

import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Navbar } from "@/components/layout/navbar";
import { Footer } from "@/components/layout/footer";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Separator } from "@/components/ui/separator";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { useAuth } from "@/stores/authStore";
import { toast } from "sonner";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { Github, Loader2 } from "lucide-react";

const USER_API = process.env.NEXT_PUBLIC_USER_API || "http://localhost:8003/v1";

export default function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [oauthLoading, setOauthLoading] = useState<string | null>(null);
  const { login, isLoading, isAuthenticated, error, clearError } = useAuth();
  const router = useRouter();

  const handleGitHubLogin = async () => {
    setOauthLoading("github");
    try {
      const response = await fetch(`${USER_API}/oauth/github/authorize`);
      if (!response.ok) {
        throw new Error("GitHub 登录暂不可用");
      }
      const data = await response.json();
      // Redirect to GitHub authorization page
      window.location.href = data.authorize_url;
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "GitHub 登录失败");
      setOauthLoading(null);
    }
  };

  const handleWeChatLogin = async () => {
    setOauthLoading("wechat");
    try {
      const response = await fetch(`${USER_API}/oauth/wechat/authorize`);
      if (!response.ok) {
        throw new Error("微信登录暂不可用");
      }
      const data = await response.json();
      window.location.href = data.authorize_url;
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "微信登录失败");
      setOauthLoading(null);
    }
  };

  // Redirect if already authenticated
  useEffect(() => {
    if (isAuthenticated) {
      router.push("/dashboard");
    }
  }, [isAuthenticated, router]);

  // Show error toast when error changes
  useEffect(() => {
    if (error) {
      toast.error(error);
      clearError();
    }
  }, [error, clearError]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await login(email, password);
      toast.success("登录成功");
      router.push("/dashboard");
    } catch {
      // Error is handled by the store and displayed via toast
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
            <CardTitle className="text-2xl font-bold">欢迎回来</CardTitle>
            <CardDescription className="text-gray-400">
              输入您的账号信息以访问个人中心
            </CardDescription>
          </CardHeader>
          <form onSubmit={handleSubmit}>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="email" className="text-sm font-medium ml-1">
                  邮箱 <span aria-hidden="true" className="text-destructive">*</span>
                </Label>
                <Input
                  id="email"
                  type="email"
                  placeholder="name@example.com"
                  required
                  aria-required="true"
                  aria-describedby="email-hint"
                  autoComplete="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="bg-white/5 border-white/10 rounded-xl h-11 focus:ring-primary"
                />
                <span id="email-hint" className="sr-only">
                  请输入您的注册邮箱地址
                </span>
              </div>
              <div className="space-y-2">
                <div className="flex items-center justify-between ml-1">
                  <Label htmlFor="password">
                    密码 <span aria-hidden="true" className="text-destructive">*</span>
                  </Label>
                  <Link href="/forgot-password" className="text-xs text-primary hover:underline">
                    忘记密码？
                  </Link>
                </div>
                <Input
                  id="password"
                  type="password"
                  required
                  aria-required="true"
                  autoComplete="current-password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="bg-white/5 border-white/10 rounded-xl h-11 focus:ring-primary"
                />
              </div>
            </CardContent>
            <CardFooter className="flex flex-col gap-4 mt-6">
              <Button
                className="w-full h-11 rounded-xl font-bold text-lg"
                disabled={isLoading || oauthLoading !== null}
              >
                {isLoading ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    登录中...
                  </>
                ) : (
                  "登录"
                )}
              </Button>

              <div className="relative w-full">
                <div className="absolute inset-0 flex items-center">
                  <Separator className="w-full bg-white/10" />
                </div>
                <div className="relative flex justify-center text-xs uppercase">
                  <span className="bg-transparent px-2 text-gray-500">
                    或使用以下方式登录
                  </span>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3 w-full" role="group" aria-label="社交登录方式">
                <Button
                  type="button"
                  variant="outline"
                  className="h-11 rounded-xl bg-white/5 border-white/10 hover:bg-white/10"
                  onClick={handleGitHubLogin}
                  disabled={oauthLoading !== null || isLoading}
                  aria-label="使用 GitHub 账号登录"
                >
                  {oauthLoading === "github" ? (
                    <>
                      <Loader2 className="h-5 w-5 animate-spin" aria-hidden="true" />
                      <span className="sr-only">正在连接 GitHub...</span>
                    </>
                  ) : (
                    <>
                      <Github className="mr-2 h-5 w-5" aria-hidden="true" />
                      GitHub
                    </>
                  )}
                </Button>
                <Button
                  type="button"
                  variant="outline"
                  className="h-11 rounded-xl bg-white/5 border-white/10 hover:bg-white/10"
                  onClick={handleWeChatLogin}
                  disabled={oauthLoading !== null || isLoading}
                  aria-label="使用微信账号登录"
                >
                  {oauthLoading === "wechat" ? (
                    <>
                      <Loader2 className="h-5 w-5 animate-spin" aria-hidden="true" />
                      <span className="sr-only">正在连接微信...</span>
                    </>
                  ) : (
                    <>
                      <svg
                        className="mr-2 h-5 w-5"
                        viewBox="0 0 24 24"
                        fill="currentColor"
                        aria-hidden="true"
                      >
                        <path d="M8.691 2.188C3.891 2.188 0 5.476 0 9.53c0 2.212 1.17 4.203 3.002 5.55a.59.59 0 0 1 .213.665l-.39 1.48c-.019.07-.048.141-.048.213 0 .163.13.295.29.295a.326.326 0 0 0 .167-.054l1.903-1.114a.864.864 0 0 1 .717-.098 10.16 10.16 0 0 0 2.837.403c.276 0 .543-.027.811-.05-.857-2.578.157-4.972 1.932-6.446 1.703-1.415 3.882-1.98 5.853-1.838-.576-3.583-4.196-6.348-8.596-6.348zM5.785 5.991c.642 0 1.162.529 1.162 1.18a1.17 1.17 0 0 1-1.162 1.178A1.17 1.17 0 0 1 4.623 7.17c0-.651.52-1.18 1.162-1.18zm5.813 0c.642 0 1.162.529 1.162 1.18a1.17 1.17 0 0 1-1.162 1.178 1.17 1.17 0 0 1-1.162-1.178c0-.651.52-1.18 1.162-1.18zm5.34 2.867c-1.797-.052-3.746.512-5.28 1.786-1.72 1.428-2.687 3.72-1.78 6.22.942 2.453 3.666 4.229 6.884 4.229.826 0 1.622-.12 2.361-.336a.722.722 0 0 1 .598.082l1.584.926a.272.272 0 0 0 .14.047c.134 0 .24-.111.24-.247 0-.06-.023-.12-.038-.177l-.327-1.233a.582.582 0 0 1-.023-.156.49.49 0 0 1 .201-.398C23.024 18.48 24 16.82 24 14.98c0-3.21-2.931-5.837-6.656-6.088V8.89c-.135-.012-.27-.027-.407-.032zM13.087 12.2c.535 0 .969.44.969.983a.976.976 0 0 1-.969.983.976.976 0 0 1-.969-.983c0-.542.434-.983.97-.983zm4.844 0c.535 0 .969.44.969.983a.976.976 0 0 1-.969.983.976.976 0 0 1-.969-.983c0-.542.434-.983.97-.983z" />
                      </svg>
                      微信
                    </>
                  )}
                </Button>
              </div>

              <p className="text-center text-sm text-gray-400">
                还没有账号？{" "}
                <Link href="/register" className="text-primary hover:underline">
                  立即注册
                </Link>
              </p>
            </CardFooter>
          </form>
        </Card>
      </main>
      <Footer />
    </div>
  );
}
