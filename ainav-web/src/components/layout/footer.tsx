import Link from "next/link";
import { Github, Twitter, Mail } from "lucide-react";
import { cn } from "@/lib/utils";

export function Footer() {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="w-full bg-secondary/30 border-t">
      <div className="container mx-auto py-8 sm:py-10 md:py-12 px-4 sm:px-6">
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-8 sm:gap-6 md:gap-8">
          {/* Brand Section */}
          <div className="col-span-1 sm:col-span-2 space-y-4">
            <Link
              href="/"
              className={cn(
                "inline-flex items-center space-x-2 min-h-[44px]",
                "transition-all duration-200 ease-out",
                "focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2 rounded",
                "active:scale-[0.98]"
              )}
            >
              <div className="w-7 h-7 sm:w-8 sm:h-8 rounded-lg bg-primary flex items-center justify-center shrink-0">
                <span className="text-primary-foreground font-bold text-sm sm:text-base">
                  A
                </span>
              </div>
              <span className="font-bold text-lg sm:text-xl tracking-tight">AI导航</span>
            </Link>
            <p className="text-muted-foreground text-sm sm:text-base max-w-sm leading-relaxed">
              汇集全球顶尖 AI
              工具、教程与变现案例。我们致力于帮助每个人在这个人工智能时代找到最适合自己的工具,提升效率,创造价值。
            </p>
            {/* Social Links - touch-friendly */}
            <div className="flex gap-2 sm:gap-3 pt-2">
              <Link
                href="#"
                className={cn(
                  "inline-flex items-center justify-center w-11 h-11 min-w-[44px] min-h-[44px] rounded-lg",
                  "text-muted-foreground hover:text-primary hover:bg-muted",
                  "transition-all duration-200 ease-out",
                  "focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2",
                  "active:scale-[0.98]"
                )}
                aria-label="Twitter"
              >
                <Twitter className="h-5 w-5 sm:h-6 sm:w-6" aria-hidden="true" />
              </Link>
              <Link
                href="#"
                className={cn(
                  "inline-flex items-center justify-center w-11 h-11 min-w-[44px] min-h-[44px] rounded-lg",
                  "text-muted-foreground hover:text-primary hover:bg-muted",
                  "transition-all duration-200 ease-out",
                  "focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2",
                  "active:scale-[0.98]"
                )}
                aria-label="GitHub"
              >
                <Github className="h-5 w-5 sm:h-6 sm:w-6" aria-hidden="true" />
              </Link>
              <Link
                href="#"
                className={cn(
                  "inline-flex items-center justify-center w-11 h-11 min-w-[44px] min-h-[44px] rounded-lg",
                  "text-muted-foreground hover:text-primary hover:bg-muted",
                  "transition-all duration-200 ease-out",
                  "focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2",
                  "active:scale-[0.98]"
                )}
                aria-label="Email"
              >
                <Mail className="h-5 w-5 sm:h-6 sm:w-6" aria-hidden="true" />
              </Link>
            </div>
          </div>

          {/* Resources Column */}
          <div className="space-y-3 sm:space-y-4">
            <h3 className="font-semibold text-sm sm:text-base uppercase tracking-wider">
              资源
            </h3>
            <ul className="space-y-1" role="list">
              <li>
                <Link
                  href="/tools"
                  className={cn(
                    "inline-block py-2 sm:py-2.5 text-sm sm:text-base min-h-[44px] flex items-center",
                    "text-muted-foreground hover:text-primary",
                    "transition-all duration-200 ease-out",
                    "focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2 rounded",
                    "active:scale-[0.98]"
                  )}
                >
                  工具库
                </Link>
              </li>
              <li>
                <Link
                  href="/scenarios"
                  className={cn(
                    "inline-block py-2 sm:py-2.5 text-sm sm:text-base min-h-[44px] flex items-center",
                    "text-muted-foreground hover:text-primary",
                    "transition-all duration-200 ease-out",
                    "focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2 rounded",
                    "active:scale-[0.98]"
                  )}
                >
                  应用场景
                </Link>
              </li>
              <li>
                <Link
                  href="/submit"
                  className={cn(
                    "inline-block py-2 sm:py-2.5 text-sm sm:text-base min-h-[44px] flex items-center",
                    "text-muted-foreground hover:text-primary",
                    "transition-all duration-200 ease-out",
                    "focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2 rounded",
                    "active:scale-[0.98]"
                  )}
                >
                  提交工具
                </Link>
              </li>
              <li>
                <Link
                  href="/api"
                  className={cn(
                    "inline-block py-2 sm:py-2.5 text-sm sm:text-base min-h-[44px] flex items-center",
                    "text-muted-foreground hover:text-primary",
                    "transition-all duration-200 ease-out",
                    "focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2 rounded",
                    "active:scale-[0.98]"
                  )}
                >
                  API 开发
                </Link>
              </li>
            </ul>
          </div>

          {/* About Column */}
          <div className="space-y-3 sm:space-y-4">
            <h3 className="font-semibold text-sm sm:text-base uppercase tracking-wider">
              关于
            </h3>
            <ul className="space-y-1" role="list">
              <li>
                <Link
                  href="/about"
                  className={cn(
                    "inline-block py-2 sm:py-2.5 text-sm sm:text-base min-h-[44px] flex items-center",
                    "text-muted-foreground hover:text-primary",
                    "transition-all duration-200 ease-out",
                    "focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2 rounded",
                    "active:scale-[0.98]"
                  )}
                >
                  关于我们
                </Link>
              </li>
              <li>
                <Link
                  href="/privacy"
                  className={cn(
                    "inline-block py-2 sm:py-2.5 text-sm sm:text-base min-h-[44px] flex items-center",
                    "text-muted-foreground hover:text-primary",
                    "transition-all duration-200 ease-out",
                    "focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2 rounded",
                    "active:scale-[0.98]"
                  )}
                >
                  隐私政策
                </Link>
              </li>
              <li>
                <Link
                  href="/terms"
                  className={cn(
                    "inline-block py-2 sm:py-2.5 text-sm sm:text-base min-h-[44px] flex items-center",
                    "text-muted-foreground hover:text-primary",
                    "transition-all duration-200 ease-out",
                    "focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2 rounded",
                    "active:scale-[0.98]"
                  )}
                >
                  服务条款
                </Link>
              </li>
              <li>
                <Link
                  href="/contact"
                  className={cn(
                    "inline-block py-2 sm:py-2.5 text-sm sm:text-base min-h-[44px] flex items-center",
                    "text-muted-foreground hover:text-primary",
                    "transition-all duration-200 ease-out",
                    "focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2 rounded",
                    "active:scale-[0.98]"
                  )}
                >
                  建议反馈
                </Link>
              </li>
            </ul>
          </div>
        </div>

        {/* Bottom Section */}
        <div className="mt-8 sm:mt-10 md:mt-12 pt-6 sm:pt-8 border-t flex flex-col md:flex-row justify-between items-center gap-3 sm:gap-4 text-xs sm:text-sm text-muted-foreground">
          <p className="text-center md:text-left">
            © {currentYear} AI导航 (ACGS). All rights reserved.
          </p>
          <div className="flex flex-col sm:flex-row items-center gap-3 sm:gap-6">
            <Link
              href="#"
              className={cn(
                "inline-flex items-center min-h-[44px] px-2 py-2 rounded",
                "hover:text-primary transition-all duration-200 ease-out",
                "focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2",
                "active:scale-[0.98]"
              )}
            >
              京ICP备XXXXXXXX号
            </Link>
            <p className="py-2">Made with ❤️ by DeepSeek</p>
          </div>
        </div>
      </div>
    </footer>
  );
}
