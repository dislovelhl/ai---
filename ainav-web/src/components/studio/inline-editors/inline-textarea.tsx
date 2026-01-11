"use client";

import * as React from "react";
import { cn } from "@/lib/utils";
import { Textarea } from "@/components/ui/textarea";

interface InlineTextareaProps {
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
  className?: string;
  textareaClassName?: string;
  displayClassName?: string;
  emptyText?: string;
  disabled?: boolean;
  rows?: number;
  maxRows?: number;
}

/**
 * InlineTextarea - A multi-line text input that switches between view and edit modes.
 * Click to edit, blur to save. Supports Ctrl+Enter to save, Escape to cancel.
 */
export const InlineTextarea = React.forwardRef<
  HTMLTextAreaElement,
  InlineTextareaProps
>(
  (
    {
      value,
      onChange,
      placeholder = "Click to edit...",
      className,
      textareaClassName,
      displayClassName,
      emptyText = "Not set",
      disabled = false,
      rows = 3,
      maxRows = 10,
    },
    ref
  ) => {
    const [isEditing, setIsEditing] = React.useState(false);
    const [localValue, setLocalValue] = React.useState(value);
    const textareaRef = React.useRef<HTMLTextAreaElement>(null);

    // Combine refs
    React.useImperativeHandle(ref, () => textareaRef.current!);

    // Sync local value when prop changes
    React.useEffect(() => {
      setLocalValue(value);
    }, [value]);

    // Focus textarea when entering edit mode
    React.useEffect(() => {
      if (isEditing && textareaRef.current) {
        textareaRef.current.focus();
        // Move cursor to end
        const length = textareaRef.current.value.length;
        textareaRef.current.setSelectionRange(length, length);
      }
    }, [isEditing]);

    const handleBlur = () => {
      setIsEditing(false);
      if (localValue !== value) {
        onChange(localValue);
      }
    };

    const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
      if (e.key === "Enter" && (e.ctrlKey || e.metaKey)) {
        e.preventDefault();
        textareaRef.current?.blur();
      } else if (e.key === "Escape") {
        e.preventDefault();
        setLocalValue(value); // Reset to original value
        setIsEditing(false);
      }
    };

    const handleClick = () => {
      if (!disabled) {
        setIsEditing(true);
      }
    };

    if (isEditing) {
      return (
        <Textarea
          ref={textareaRef}
          value={localValue}
          onChange={(e) => setLocalValue(e.target.value)}
          onBlur={handleBlur}
          onKeyDown={handleKeyDown}
          placeholder={placeholder}
          rows={rows}
          className={cn(
            "text-sm resize-none",
            textareaClassName,
            className
          )}
          style={{ maxHeight: `${maxRows * 1.5}rem` }}
          disabled={disabled}
        />
      );
    }

    return (
      <div
        onClick={handleClick}
        className={cn(
          "min-h-[60px] px-3 py-2 rounded-md text-sm cursor-pointer transition-colors whitespace-pre-wrap",
          "hover:bg-muted/50 border border-transparent hover:border-border",
          disabled && "opacity-50 cursor-not-allowed hover:bg-transparent hover:border-transparent",
          !value && "text-muted-foreground italic",
          displayClassName,
          className
        )}
        role="button"
        tabIndex={disabled ? -1 : 0}
        onKeyDown={(e) => {
          if (e.key === "Enter" || e.key === " ") {
            e.preventDefault();
            handleClick();
          }
        }}
      >
        {value || emptyText}
      </div>
    );
  }
);

InlineTextarea.displayName = "InlineTextarea";
