"use client";

import React, { useState, useEffect } from "react";

interface SboButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  onConfirm: () => void;
  confirmLabel?: string;
  variant?: "primary" | "danger" | "secondary";
  children: React.ReactNode;
  timeoutMs?: number;
}

export function SboButton({
  onConfirm,
  confirmLabel,
  variant = "primary",
  children,
  timeoutMs = 4000,
  className = "",
  disabled,
  ...rest
}: SboButtonProps) {
  const [isArmed, setIsArmed] = useState(false);

  useEffect(() => {
    if (!isArmed) return;
    const timer = setTimeout(() => {
      setIsArmed(false);
    }, timeoutMs);
    return () => clearTimeout(timer);
  }, [isArmed, timeoutMs]);

  const handleClick = (e: React.MouseEvent<HTMLButtonElement>) => {
    if (disabled) return;
    if (!isArmed) {
      setIsArmed(true);
    } else {
      setIsArmed(false);
      onConfirm();
    }
  };

  const getVariantStyles = () => {
    if (isArmed) {
      return "bg-[#D32F2F] hover:bg-[#B71C1C] text-white border-[#FF5252] shadow-[0_0_10px_rgba(211,47,47,0.4)] animate-pulse";
    }

    switch (variant) {
      case "danger":
        return "bg-[#383838] hover:bg-[#4A1E1E] text-[#D32F2F] border-[#D32F2F]/60";
      case "secondary":
        return "bg-[#383838] hover:bg-[#424242] text-[#E0E0E0] border-[#555555]";
      case "primary":
      default:
        return "bg-[#00838F] hover:bg-[#0097A7] text-white border-[#00ACC1]";
    }
  };

  const defaultConfirmText = confirmLabel || `Confirm ${typeof children === "string" ? children : "Action"}?`;

  return (
    <button
      type="button"
      onClick={handleClick}
      disabled={disabled}
      className={`inline-flex items-center justify-center gap-2 px-4 py-2 rounded font-mono text-xs font-semibold uppercase tracking-wider border transition-all duration-150 disabled:opacity-50 disabled:cursor-not-allowed ${getVariantStyles()} ${className}`}
      {...rest}
    >
      {isArmed ? (
        <>
          <span className="w-2 h-2 rounded-full bg-white animate-ping" />
          {defaultConfirmText}
        </>
      ) : (
        children
      )}
    </button>
  );
}
