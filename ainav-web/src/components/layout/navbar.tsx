import { Button } from "@/components/ui/button";
import { Menu } from "lucide-react";
import Link from "next/link";
import { SearchBar } from "./search-bar";

export function Navbar() {
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
              href="/learn"
              className="transition-colors hover:text-primary"
            >
              学习中心
            </Link>
            <Link
              href="/submit"
              className="transition-colors hover:text-primary font-bold text-primary/80"
            >
              分享工具
            </Link>
          </nav>
        </div>

        <div className="flex-1 flex justify-center px-4 max-w-lg">
          <SearchBar />
        </div>

        <div className="flex items-center gap-4 shrink-0">
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
          <Button variant="ghost" size="icon" className="md:hidden">
            <Menu className="h-6 w-6" />
          </Button>
        </div>
      </div>
    </header>
  );
}
