import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import { Toaster } from "@/components/ui/sonner";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "AI 导航 - 发现最好的 AI 工具",
  description: "汇集全球顶尖 AI 工具、教程与变现案例，助你开启 AI 时代。",
};

import { Providers } from "@/components/providers/index";

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="zh-CN" suppressHydrationWarning>
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased min-h-screen bg-background text-foreground`}
      >
        <Providers>
          <div className="relative flex min-h-screen flex-col">{children}</div>
          <Toaster />
        </Providers>
      </body>
    </html>
  );
}
