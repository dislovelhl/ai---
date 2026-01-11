"use client";

import * as React from "react";
import { cn } from "@/lib/utils";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { ChevronDown } from "lucide-react";

export interface InlineSelectOption {
  value: string;
  label: string;
}

interface InlineSelectProps {
  value: string;
  onChange: (value: string) => void;
  options: InlineSelectOption[];
  placeholder?: string;
  className?: string;
  selectClassName?: string;
  displayClassName?: string;
  emptyText?: string;
  disabled?: boolean;
}

/**
 * InlineSelect - A select dropdown that switches between view and edit modes.
 * Click to open dropdown, selection auto-saves.
 */
export const InlineSelect = React.forwardRef<HTMLButtonElement, InlineSelectProps>(
  (
    {
      value,
      onChange,
      options,
      placeholder = "Select...",
      className,
      selectClassName,
      displayClassName,
      emptyText = "Not set",
      disabled = false,
    },
    ref
  ) => {
    const [isOpen, setIsOpen] = React.useState(false);

    const selectedOption = options.find((opt) => opt.value === value);
    const displayText = selectedOption?.label || emptyText;

    const handleValueChange = (newValue: string) => {
      onChange(newValue);
      setIsOpen(false);
    };

    const handleClick = () => {
      if (!disabled) {
        setIsOpen(true);
      }
    };

    if (isOpen) {
      return (
        <Select
          value={value}
          onValueChange={handleValueChange}
          open={isOpen}
          onOpenChange={setIsOpen}
        >
          <SelectTrigger
            ref={ref}
            className={cn("h-7 text-sm", selectClassName, className)}
            disabled={disabled}
          >
            <SelectValue placeholder={placeholder} />
          </SelectTrigger>
          <SelectContent>
            {options.map((option) => (
              <SelectItem key={option.value} value={option.value}>
                {option.label}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      );
    }

    return (
      <div
        onClick={handleClick}
        className={cn(
          "min-h-[28px] px-3 py-1 rounded-md text-sm cursor-pointer transition-colors",
          "hover:bg-muted/50 border border-transparent hover:border-border",
          "flex items-center justify-between gap-2",
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
        <span className="flex-1">{displayText}</span>
        <ChevronDown className="h-3 w-3 opacity-50 flex-shrink-0" />
      </div>
    );
  }
);

InlineSelect.displayName = "InlineSelect";
