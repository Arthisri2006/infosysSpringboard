"use client";

import { useEffect } from "react";

export function vibrate(pattern: number | number[] = 10) {
  if (typeof navigator !== "undefined" && "vibrate" in navigator) navigator.vibrate(pattern);
}

export function HapticFeedback() {
  useEffect(() => {
    const press = (event: PointerEvent) => {
      const target = event.target as HTMLElement | null;
      if (target?.closest("button:not(:disabled), a[href], label[for]")) vibrate(8);
    };
    document.addEventListener("pointerdown", press, { passive: true });
    return () => document.removeEventListener("pointerdown", press);
  }, []);
  return null;
}
