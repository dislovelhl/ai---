"use client";

import React, { useState, useCallback } from "react";
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import {
  oneDark,
  oneLight,
} from "react-syntax-highlighter/dist/esm/styles/prism";
import { Check, Copy } from "lucide-react";
import { cn } from "@/lib/utils";

interface CodeBlockProps {
  code: string;
  language?: string;
  showLineNumbers?: boolean;
  maxHeight?: number;
  className?: string;
}

// Auto-detect language from code content
function detectLanguage(code: string): string {
  const trimmed = code.trim();

  // JSON detection
  if (
    (trimmed.startsWith("{") && trimmed.endsWith("}")) ||
    (trimmed.startsWith("[") && trimmed.endsWith("]"))
  ) {
    try {
      JSON.parse(trimmed);
      return "json";
    } catch {
      // Not valid JSON
    }
  }

  // Python detection
  if (
    /^(import |from |def |class |if __name__|print\(|async def )/.test(trimmed)
  ) {
    return "python";
  }

  // JavaScript/TypeScript detection
  if (
    /^(const |let |var |function |import |export |class |async )/.test(trimmed)
  ) {
    return "javascript";
  }

  // HTML detection
  if (/^<(!DOCTYPE|html|head|body|div|span|p|a |script|style)/i.test(trimmed)) {
    return "html";
  }

  // CSS detection
  if (/^(\.|#|@media|@keyframes|body|html|\*)\s*{/.test(trimmed)) {
    return "css";
  }

  // SQL detection
  if (/^(SELECT|INSERT|UPDATE|DELETE|CREATE|DROP|ALTER)\s/i.test(trimmed)) {
    return "sql";
  }

  // Bash/Shell detection
  if (
    /^#!/.test(trimmed) ||
    /^(sudo|apt|npm|yarn|pip|curl|wget)\s/.test(trimmed)
  ) {
    return "bash";
  }

  // Default to plaintext
  return "text";
}

/**
 * CodeBlock - Syntax-highlighted code display with copy functionality.
 * Supports auto-language detection, dark/light themes, and line numbers.
 */
export function CodeBlock({
  code,
  language,
  showLineNumbers = false,
  maxHeight = 300,
  className,
}: CodeBlockProps) {
  const [copied, setCopied] = useState(false);

  const detectedLanguage = language || detectLanguage(code);

  const handleCopy = useCallback(async () => {
    try {
      await navigator.clipboard.writeText(code);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error("Failed to copy:", err);
    }
  }, [code]);

  // Use dark theme by default (can be enhanced with next-themes later)
  const isDark =
    typeof window !== "undefined" &&
    document.documentElement.classList.contains("dark");

  return (
    <div
      className={cn(
        "relative group rounded-lg overflow-hidden border border-border/50",
        className
      )}
    >
      {/* Language badge & copy button */}
      <div className="absolute top-2 right-2 flex items-center gap-2 z-10">
        <span className="text-[10px] font-mono uppercase px-1.5 py-0.5 rounded bg-muted/80 text-muted-foreground">
          {detectedLanguage}
        </span>
        <button
          onClick={handleCopy}
          className="p-1.5 rounded bg-muted/80 hover:bg-muted text-muted-foreground hover:text-foreground transition-colors opacity-0 group-hover:opacity-100"
          title="Copy code"
        >
          {copied ? (
            <Check className="w-3.5 h-3.5 text-green-500" />
          ) : (
            <Copy className="w-3.5 h-3.5" />
          )}
        </button>
      </div>

      {/* Syntax highlighted code */}
      <SyntaxHighlighter
        language={detectedLanguage}
        style={isDark ? oneDark : oneLight}
        showLineNumbers={showLineNumbers}
        customStyle={{
          margin: 0,
          padding: "1rem",
          fontSize: "0.75rem",
          maxHeight: `${maxHeight}px`,
          overflow: "auto",
          background: "transparent",
        }}
        codeTagProps={{
          style: {
            fontFamily:
              'ui-monospace, SFMono-Regular, "SF Mono", Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace',
          },
        }}
      >
        {code}
      </SyntaxHighlighter>
    </div>
  );
}

/**
 * InlineCode - Simple inline code styling
 */
export function InlineCode({
  children,
  className,
}: {
  children: React.ReactNode;
  className?: string;
}) {
  return (
    <code
      className={cn(
        "px-1.5 py-0.5 rounded bg-muted text-[0.875em] font-mono",
        className
      )}
    >
      {children}
    </code>
  );
}
