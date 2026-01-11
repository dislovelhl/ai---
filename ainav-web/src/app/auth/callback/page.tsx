"use client";

import { useEffect, useState, Suspense } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import { useAuthStore } from "@/stores/authStore";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Loader2, CheckCircle2, XCircle, Github } from "lucide-react";
import Link from "next/link";

function OAuthCallbackContent() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const { checkAuth } = useAuthStore();

  const [status, setStatus] = useState<"loading" | "success" | "error">(
    "loading"
  );
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const token = searchParams.get("token");
  const provider = searchParams.get("provider");
  const error = searchParams.get("error");

  useEffect(() => {
    const handleCallback = async () => {
      if (error) {
        setStatus("error");
        setErrorMessage(decodeURIComponent(error));
        return;
      }

      if (!token) {
        setStatus("error");
        setErrorMessage("未收到认证令牌");
        return;
      }

      try {
        // Store the token
        localStorage.setItem("access_token", token);

        // Also update the auth store (it uses 'auth-storage' key)
        const authData = {
          state: {
            token,
            isAuthenticated: true,
          },
        };
        localStorage.setItem("auth-storage", JSON.stringify(authData));

        // Verify the token and fetch user data
        await checkAuth();

        setStatus("success");

        // Redirect to dashboard after a short delay
        setTimeout(() => {
          router.push("/dashboard");
        }, 1500);
      } catch (err) {
        setStatus("error");
        setErrorMessage("认证失败，请重试");
      }
    };

    handleCallback();
  }, [token, provider, error, checkAuth, router]);

  const getProviderName = () => {
    switch (provider) {
      case "github":
        return "GitHub";
      case "wechat":
        return "微信";
      default:
        return "第三方";
    }
  };

  const getProviderIcon = () => {
    switch (provider) {
      case "github":
        return <Github className="h-8 w-8" />;
      default:
        return null;
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-b from-background to-muted/20 p-4">
      <Card className="w-full max-w-md">
        <CardHeader className="text-center">
          {status === "loading" && (
            <>
              <div className="mx-auto mb-4">{getProviderIcon()}</div>
              <CardTitle className="text-2xl">正在登录</CardTitle>
              <CardDescription>
                正在通过 {getProviderName()} 完成认证...
              </CardDescription>
            </>
          )}

          {status === "success" && (
            <>
              <div className="mx-auto w-12 h-12 rounded-full bg-green-100 dark:bg-green-900/20 flex items-center justify-center mb-4">
                <CheckCircle2 className="h-6 w-6 text-green-600" />
              </div>
              <CardTitle className="text-2xl">登录成功</CardTitle>
              <CardDescription>
                已通过 {getProviderName()} 登录，正在跳转...
              </CardDescription>
            </>
          )}

          {status === "error" && (
            <>
              <div className="mx-auto w-12 h-12 rounded-full bg-red-100 dark:bg-red-900/20 flex items-center justify-center mb-4">
                <XCircle className="h-6 w-6 text-red-600" />
              </div>
              <CardTitle className="text-2xl">登录失败</CardTitle>
              <CardDescription>{errorMessage}</CardDescription>
            </>
          )}
        </CardHeader>

        <CardContent className="flex flex-col items-center gap-4">
          {status === "loading" && (
            <Loader2 className="h-8 w-8 animate-spin text-primary" />
          )}

          {status === "error" && (
            <div className="flex gap-3">
              <Button variant="outline" asChild>
                <Link href="/login">返回登录</Link>
              </Button>
              <Button asChild>
                <Link href="/">返回首页</Link>
              </Button>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}

export default function OAuthCallbackPage() {
  return (
    <Suspense
      fallback={
        <div className="min-h-screen flex items-center justify-center">
          <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
        </div>
      }
    >
      <OAuthCallbackContent />
    </Suspense>
  );
}
