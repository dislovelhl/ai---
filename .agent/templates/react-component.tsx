/**
 * React Component Template
 * Usage: /gen component <ComponentName>
 */

import { cn } from "@/lib/utils"
import { forwardRef } from "react"

// =============================================================================
// Types
// =============================================================================

interface __COMPONENT_NAME__Props extends React.HTMLAttributes<HTMLDivElement> {
  /**
   * Component-specific props go here
   */
  variant?: "default" | "outline" | "ghost"
  size?: "sm" | "md" | "lg"
}

// =============================================================================
// Component
// =============================================================================

const __COMPONENT_NAME__ = forwardRef<HTMLDivElement, __COMPONENT_NAME__Props>(
  ({ className, variant = "default", size = "md", children, ...props }, ref) => {
    return (
      <div
        ref={ref}
        className={cn(
          // Base styles
          "rounded-lg transition-colors",
          // Variant styles
          {
            default: "bg-background border",
            outline: "border-2 border-primary",
            ghost: "hover:bg-accent",
          }[variant],
          // Size styles
          {
            sm: "p-2 text-sm",
            md: "p-4 text-base",
            lg: "p-6 text-lg",
          }[size],
          className
        )}
        {...props}
      >
        {children}
      </div>
    )
  }
)

__COMPONENT_NAME__.displayName = "__COMPONENT_NAME__"

export { __COMPONENT_NAME__ }
export type { __COMPONENT_NAME__Props }
