"use client";

import * as React from "react";
import { cn } from "@/lib/utils";
import { Input } from "@/components/ui/input";

interface InlineInputProps {
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
  className?: string;
  inputClassName?: string;
  displayClassName?: string;
  emptyText?: string;
  disabled?: boolean;
}

/**
 * InlineInput - A text input that switches between view and edit modes.
 * Click to edit, blur to save.
 */
export const InlineInput = React.forwardRef<HTMLInputElement, InlineInputProps>(
  (
    {
      value,
      onChange,
      placeholder = "Click to edit...",
      className,
      inputClassName,
      displayClassName,
      emptyText = "Not set",
      disabled = false,
    },
    ref
  ) => {
    const [isEditing, setIsEditing] = React.useState(false);
    const [localValue, setLocalValue] = React.useState(value);
    const inputRef = React.useRef<HTMLInputElement>(null);

    // Combine refs
    React.useImperativeHandle(ref, () => inputRef.current!);

    // Sync local value when prop changes
    React.useEffect(() => {
      setLocalValue(value);
    }, [value]);

    // Focus input when entering edit mode
    React.useEffect(() => {
      if (isEditing && inputRef.current) {
        inputRef.current.focus();
        inputRef.current.select();
      }
    }, [isEditing]);

    const handleBlur = () => {
      setIsEditing(false);
      if (localValue !== value) {
        onChange(localValue);
      }
    };

    const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
      if (e.key === "Enter") {
        e.preventDefault();
        inputRef.current?.blur();
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
        <Input
          ref={inputRef}
          type="text"
          value={localValue}
          onChange={(e) => setLocalValue(e.target.value)}
          onBlur={handleBlur}
          onKeyDown={handleKeyDown}
          placeholder={placeholder}
          className={cn("h-7 text-sm", inputClassName, className)}
          disabled={disabled}
        />
      );
    }

    return (
      <div
        onClick={handleClick}
        className={cn(
          "min-h-[28px] px-3 py-1 rounded-md text-sm cursor-pointer transition-colors",
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

InlineInput.displayName = "InlineInput";
