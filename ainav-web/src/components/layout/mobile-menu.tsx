"use client";

import { useState, useEffect, useRef } from "react";
import Link from "next/link";
import { useRouter, usePathname } from "next/navigation";
import { useAuth } from "@/stores/authStore";
import { Button } from "@/components/ui/button";
import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
  SheetTrigger,
} from "@/components/ui/sheet";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Separator } from "@/components/ui/separator";
import {
  Menu,
  Bot,
  Wrench,
  Lightbulb,
  GraduationCap,
  Sparkles,
  User,
  Workflow,
  History,
  Settings,
  LogOut,
  LogIn,
  UserPlus,
  Home,
  X,
} from "lucide-react";
import { cn } from "@/lib/utils";

const NAV_ITEMS = [
  { href: "/", label: "首页", icon: Home },
  { href: "/tools", label: "工具库", icon: Wrench },
  { href: "/scenarios", label: "应用场景", icon: Lightbulb },
  { href: "/agents/gallery", label: "Agent 广场", icon: Bot, highlight: true },
  { href: "/studio", label: "Studio", icon: Sparkles },
  { href: "/learn", label: "学习中心", icon: GraduationCap },
];

const USER_MENU_ITEMS = [
  { href: "/dashboard", label: "个人中心", icon: User },
  { href: "/dashboard/workflows", label: "我的 Agent", icon: Workflow },
  { href: "/dashboard/executions", label: "执行历史", icon: History },
  { href: "/dashboard/settings", label: "设置", icon: Settings },
];

export function MobileMenu() {
  const [open, setOpen] = useState(false);
  const [isAnimating, setIsAnimating] = useState(false);
  const { user, isAuthenticated, logout } = useAuth();
  const router = useRouter();
  const pathname = usePathname();
  const firstNavItemRef = useRef<HTMLButtonElement>(null);

  // Trigger stagger animation when menu opens
  useEffect(() => {
    if (open) {
      setIsAnimating(true);
      // Focus first nav item for keyboard accessibility
      setTimeout(() => {
        firstNavItemRef.current?.focus();
      }, 100);
    } else {
      setIsAnimating(false);
    }
  }, [open]);

  const handleLogout = () => {
    logout();
    setOpen(false);
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

  const handleNavigation = (href: string) => {
    setOpen(false);
    router.push(href);
  };

  const handleKeyDown = (
    e: React.KeyboardEvent,
    callback: () => void
  ) => {
    if (e.key === "Enter" || e.key === " ") {
      e.preventDefault();
      callback();
    }
  };

  return (
    <Sheet open={open} onOpenChange={setOpen}>
      <SheetTrigger asChild>
        <Button
          variant="ghost"
          size="icon"
          className="lg:hidden h-11 w-11 min-h-[44px] min-w-[44px]"
          aria-label="打开菜单"
        >
          <Menu className="h-6 w-6" />
          <span className="sr-only">打开菜单</span>
        </Button>
      </SheetTrigger>
      <SheetContent
        side="right"
        className="w-[300px] sm:w-[350px] p-0"
        aria-label="主菜单"
      >
        <SheetHeader className="p-4 pb-3 border-b">
          <div className="flex items-center justify-between">
            <SheetTitle className="flex items-center gap-2">
              <div className="w-8 h-8 rounded-lg bg-primary flex items-center justify-center shrink-0">
                <span className="text-primary-foreground font-bold">A</span>
              </div>
              <span>
                AI<span className="text-primary">导航</span>
              </span>
            </SheetTitle>
          </div>
        </SheetHeader>

        <div className="flex flex-col h-[calc(100vh-65px)]">
          {/* User Section */}
          {isAuthenticated && user ? (
            <div className="p-4 bg-muted/30">
              <div className="flex items-center gap-3">
                <Avatar className="h-12 w-12">
                  <AvatarFallback className="bg-primary text-primary-foreground text-lg">
                    {getInitials(user.username)}
                  </AvatarFallback>
                </Avatar>
                <div className="flex-1 min-w-0">
                  <p className="font-medium truncate">{user.username}</p>
                  <p className="text-sm text-muted-foreground truncate">
                    {user.email}
                  </p>
                </div>
              </div>
            </div>
          ) : (
            <div className="p-4 bg-muted/30">
              <div className="flex gap-2">
                <Button
                  variant="outline"
                  className={cn(
                    "flex-1 h-11 min-h-[44px]",
                    "transition-all duration-200 ease-out",
                    "focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2",
                    "active:scale-[0.98]"
                  )}
                  onClick={() => handleNavigation("/login")}
                  onKeyDown={(e) => handleKeyDown(e, () => handleNavigation("/login"))}
                  aria-label="登录"
                >
                  <LogIn className="mr-2 h-4 w-4" aria-hidden="true" />
                  登录
                </Button>
                <Button
                  className={cn(
                    "flex-1 h-11 min-h-[44px]",
                    "transition-all duration-200 ease-out",
                    "focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2",
                    "active:scale-[0.98]"
                  )}
                  onClick={() => handleNavigation("/register")}
                  onKeyDown={(e) => handleKeyDown(e, () => handleNavigation("/register"))}
                  aria-label="注册"
                >
                  <UserPlus className="mr-2 h-4 w-4" aria-hidden="true" />
                  注册
                </Button>
              </div>
            </div>
          )}

          {/* Navigation */}
          <nav
            className="flex-1 overflow-y-auto py-4"
            aria-label="主导航"
            role="navigation"
          >
            <div className="px-2 space-y-1">
              {NAV_ITEMS.map((item, index) => {
                const Icon = item.icon;
                const isActive = pathname === item.href;

                return (
                  <button
                    key={item.href}
                    ref={index === 0 ? firstNavItemRef : null}
                    onClick={() => handleNavigation(item.href)}
                    onKeyDown={(e) => handleKeyDown(e, () => handleNavigation(item.href))}
                    className={cn(
                      "w-full flex items-center gap-3 px-4 py-3.5 rounded-lg text-left min-h-[44px]",
                      "transition-all duration-200 ease-out",
                      "focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2",
                      "active:scale-[0.98]",
                      isActive
                        ? "bg-primary text-primary-foreground shadow-sm"
                        : "hover:bg-muted active:bg-muted/80",
                      item.highlight && !isActive && "text-primary font-medium",
                      // Stagger animation
                      isAnimating && "animate-in slide-in-from-right fade-in",
                      isAnimating && `duration-300 delay-${index * 50}`
                    )}
                    style={
                      isAnimating
                        ? { animationDelay: `${index * 50}ms` }
                        : undefined
                    }
                    aria-current={isActive ? "page" : undefined}
                  >
                    <Icon className="h-5 w-5 shrink-0" aria-hidden="true" />
                    <span className="flex-1">{item.label}</span>
                    {item.highlight && (
                      <span className="ml-auto text-xs bg-primary/20 text-primary px-2 py-1 rounded-full shrink-0">
                        热门
                      </span>
                    )}
                  </button>
                );
              })}
            </div>

            {/* User Menu Items */}
            {isAuthenticated && (
              <>
                <Separator className="my-4" />
                <div className="px-2 space-y-1">
                  <p className="px-4 py-2 text-xs font-medium text-muted-foreground uppercase tracking-wider">
                    个人中心
                  </p>
                  {USER_MENU_ITEMS.map((item, index) => {
                    const Icon = item.icon;
                    const isActive = pathname === item.href;
                    // Continue stagger animation from nav items
                    const delayIndex = NAV_ITEMS.length + index;

                    return (
                      <button
                        key={item.href}
                        onClick={() => handleNavigation(item.href)}
                        onKeyDown={(e) => handleKeyDown(e, () => handleNavigation(item.href))}
                        className={cn(
                          "w-full flex items-center gap-3 px-4 py-3.5 rounded-lg text-left min-h-[44px]",
                          "transition-all duration-200 ease-out",
                          "focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2",
                          "active:scale-[0.98]",
                          isActive
                            ? "bg-primary text-primary-foreground shadow-sm"
                            : "hover:bg-muted active:bg-muted/80",
                          // Stagger animation
                          isAnimating && "animate-in slide-in-from-right fade-in",
                          isAnimating && `duration-300 delay-${delayIndex * 50}`
                        )}
                        style={
                          isAnimating
                            ? { animationDelay: `${delayIndex * 50}ms` }
                            : undefined
                        }
                        aria-current={isActive ? "page" : undefined}
                      >
                        <Icon className="h-5 w-5 shrink-0" aria-hidden="true" />
                        <span className="flex-1">{item.label}</span>
                      </button>
                    );
                  })}
                </div>
              </>
            )}
          </nav>

          {/* Footer */}
          {isAuthenticated && (
            <div className="p-4 border-t">
              <Button
                variant="ghost"
                className={cn(
                  "w-full justify-start text-destructive hover:text-destructive hover:bg-destructive/10 h-11 min-h-[44px]",
                  "transition-all duration-200 ease-out",
                  "focus:outline-none focus:ring-2 focus:ring-destructive focus:ring-offset-2",
                  "active:scale-[0.98]"
                )}
                onClick={handleLogout}
                onKeyDown={(e) => handleKeyDown(e, handleLogout)}
                aria-label="退出登录"
              >
                <LogOut className="mr-2 h-5 w-5" aria-hidden="true" />
                退出登录
              </Button>
            </div>
          )}
        </div>
      </SheetContent>
    </Sheet>
  );
}
