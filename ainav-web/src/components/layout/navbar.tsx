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
      <div className="container mx-auto flex h-16 items-center justify-between gap-2 px-3 sm:gap-4 sm:px-4 md:gap-6">
        {/* Logo Section - shrink-0 to prevent compression */}
        <Link href="/" className="flex items-center space-x-2 shrink-0 -ml-1 sm:ml-0">
          <div className="w-8 h-8 sm:w-9 sm:h-9 rounded-lg bg-primary flex items-center justify-center">
            <span className="text-primary-foreground font-bold text-lg sm:text-xl">
              A
            </span>
          </div>
          <span className="hidden font-bold sm:inline-block text-xl tracking-tight">
            AI<span className="text-primary">导航</span>
          </span>
        </Link>

        {/* Desktop Navigation - hidden on mobile/tablet */}
        <nav className="hidden lg:flex items-center space-x-4 xl:space-x-6 text-sm font-medium">
          <Link
            href="/tools"
            className="transition-colors hover:text-primary px-2 py-1"
          >
            工具库
          </Link>
          <Link
            href="/scenarios"
            className="transition-colors hover:text-primary px-2 py-1"
          >
            应用场景
          </Link>
          <Link
            href="/agents/gallery"
            className="transition-colors hover:text-primary flex items-center gap-1 font-bold text-primary px-2 py-1"
          >
            <Bot className="w-4 h-4" />
            Agent 广场
          </Link>
          <Link
            href="/studio"
            className="transition-colors hover:text-primary px-2 py-1"
          >
            Studio
          </Link>
          <Link
            href="/learn"
            className="transition-colors hover:text-primary px-2 py-1"
          >
            学习中心
          </Link>
        </nav>

        {/* Search Bar - hidden on small mobile, visible md+ */}
        <div className="hidden md:flex flex-1 justify-center px-2 max-w-lg">
          <SearchBar />
        </div>

        {/* Right Section - Auth & Mobile Menu */}
        <div className="flex items-center gap-2 sm:gap-3 shrink-0">
          {isLoading ? (
            <div className="w-9 h-9 sm:w-10 sm:h-10 rounded-full bg-muted animate-pulse" />
          ) : isAuthenticated && user ? (
            <div className="hidden sm:flex items-center gap-2 lg:gap-3">
              <Link href="/studio">
                <Button
                  variant="outline"
                  size="sm"
                  className="gap-2 h-10 min-h-[44px] px-3 sm:px-4"
                >
                  <Workflow className="h-4 w-4" />
                  <span className="hidden lg:inline">创建 Agent</span>
                  <span className="lg:hidden">创建</span>
                </Button>
              </Link>
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button
                    variant="ghost"
                    className="relative h-11 w-11 min-h-[44px] min-w-[44px] rounded-full p-0"
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
                <Button
                  variant="ghost"
                  className="hidden lg:flex h-10 min-h-[44px] px-4"
                >
                  登录
                </Button>
              </Link>
              <Link href="/register">
                <Button className="rounded-full h-10 min-h-[44px] px-4 sm:px-6">
                  注册
                </Button>
              </Link>
            </div>
          )}
          <MobileMenu />
        </div>
      </div>
    </header>
  );
}
