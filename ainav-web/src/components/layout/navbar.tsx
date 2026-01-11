"use client";

import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Bot, User, Settings, LogOut, Workflow, History } from "lucide-react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { SearchBar } from "./search-bar";
import { MobileMenu } from "./mobile-menu";
import { useAuth } from "@/stores/authStore";

export function Navbar() {
  const { user, isAuthenticated, isLoading, logout } = useAuth();
  const router = useRouter();

  const handleLogout = () => {
    logout();
    router.push("/");
  };

  const getInitials = (name: string) => {
    return name
      .split(" ")
      .map((n) => n[0])
      .join("")
      .toUpperCase()
      .slice(0, 2);
  };

  return (
    <header className="sticky top-0 z-50 w-full glass border-b">
      <div className="container mx-auto flex h-16 items-center justify-between px-4">
        <div className="flex items-center gap-6">
          <Link href="/" className="flex items-center space-x-2 shrink-0">
            <div className="w-8 h-8 rounded-lg bg-primary flex items-center justify-center">
              <span className="text-primary-foreground font-bold text-lg">
                A
              </span>
            </div>
            <span className="hidden font-bold sm:inline-block text-xl tracking-tight">
              AI<span className="text-primary">导航</span>
            </span>
          </Link>
          <nav className="hidden md:flex items-center space-x-6 text-sm font-medium">
            <Link
              href="/tools"
              className="transition-colors hover:text-primary"
            >
              工具库
            </Link>
            <Link
              href="/scenarios"
              className="transition-colors hover:text-primary"
            >
              应用场景
            </Link>
            <Link
              href="/agents/gallery"
              className="transition-colors hover:text-primary flex items-center gap-1 font-bold text-primary"
            >
              <Bot className="w-4 h-4" />
              Agent 广场
            </Link>
            <Link
              href="/studio"
              className="transition-colors hover:text-primary"
            >
              Studio
            </Link>
            <Link
              href="/learn"
              className="transition-colors hover:text-primary"
            >
              学习中心
            </Link>
          </nav>
        </div>

        <div className="flex-1 flex justify-center px-4 max-w-lg">
          <SearchBar />
        </div>

        <div className="flex items-center gap-4 shrink-0">
          {isLoading ? (
            <div className="w-8 h-8 rounded-full bg-muted animate-pulse" />
          ) : isAuthenticated && user ? (
            <div className="hidden sm:flex items-center gap-3">
              <Link href="/studio">
                <Button variant="outline" size="sm" className="gap-2">
                  <Workflow className="h-4 w-4" />
                  创建 Agent
                </Button>
              </Link>
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button
                    variant="ghost"
                    className="relative h-9 w-9 rounded-full"
                    aria-label={`用户菜单: ${user.username}`}
                    aria-haspopup="menu"
                  >
                    <Avatar className="h-9 w-9">
                      <AvatarFallback className="bg-primary text-primary-foreground">
                        {getInitials(user.username)}
                      </AvatarFallback>
                    </Avatar>
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent className="w-56" align="end" forceMount>
                  <DropdownMenuLabel className="font-normal">
                    <div className="flex flex-col space-y-1">
                      <p className="text-sm font-medium leading-none">
                        {user.username}
                      </p>
                      <p className="text-xs leading-none text-muted-foreground">
                        {user.email}
                      </p>
                    </div>
                  </DropdownMenuLabel>
                  <DropdownMenuSeparator />
                  <DropdownMenuItem asChild>
                    <Link href="/dashboard" className="cursor-pointer">
                      <User className="mr-2 h-4 w-4" />
                      个人中心
                    </Link>
                  </DropdownMenuItem>
                  <DropdownMenuItem asChild>
                    <Link href="/dashboard/workflows" className="cursor-pointer">
                      <Workflow className="mr-2 h-4 w-4" />
                      我的 Agent
                    </Link>
                  </DropdownMenuItem>
                  <DropdownMenuItem asChild>
                    <Link href="/dashboard/executions" className="cursor-pointer">
                      <History className="mr-2 h-4 w-4" />
                      执行历史
                    </Link>
                  </DropdownMenuItem>
                  <DropdownMenuItem asChild>
                    <Link href="/dashboard/settings" className="cursor-pointer">
                      <Settings className="mr-2 h-4 w-4" />
                      设置
                    </Link>
                  </DropdownMenuItem>
                  <DropdownMenuSeparator />
                  <DropdownMenuItem
                    onClick={handleLogout}
                    className="cursor-pointer text-destructive focus:text-destructive"
                  >
                    <LogOut className="mr-2 h-4 w-4" />
                    退出登录
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            </div>
          ) : (
            <div className="hidden sm:flex items-center gap-2">
              <Link href="/login">
                <Button variant="ghost" className="hidden lg:flex">
                  登录
                </Button>
              </Link>
              <Link href="/register">
                <Button className="rounded-full px-6">注册</Button>
              </Link>
            </div>
          )}
          <MobileMenu />
        </div>
      </div>
    </header>
  );
}
