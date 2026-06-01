"use client";

import { MoonIcon, SunIcon } from "@/components/icons";
import type { Units } from "@/lib/types";

interface UnitToggleProps {
  units: Units;
  onToggle: () => void;
}

export function UnitToggle({ units, onToggle }: UnitToggleProps): React.ReactElement {
  return (
    <div className="flex flex-row items-center rounded-full border border-[var(--color-border)] bg-[var(--color-ink-2)] p-0.5">
      <button
        type="button"
        onClick={() => units !== "metric" && onToggle()}
        className={`rounded-full px-3 py-1 text-[0.74rem] font-semibold transition-colors ${
          units === "metric"
            ? "bg-[var(--color-amber)] text-[#1a1304]"
            : "text-[var(--color-text-dim)]"
        }`}
        aria-pressed={units === "metric"}
      >
        °C
      </button>
      <button
        type="button"
        onClick={() => units !== "imperial" && onToggle()}
        className={`rounded-full px-3 py-1 text-[0.74rem] font-semibold transition-colors ${
          units === "imperial"
            ? "bg-[var(--color-amber)] text-[#1a1304]"
            : "text-[var(--color-text-dim)]"
        }`}
        aria-pressed={units === "imperial"}
      >
        °F
      </button>
    </div>
  );
}

interface ThemeToggleProps {
  theme: "dark" | "light";
  onToggle: () => void;
}

export function ThemeToggle({ theme, onToggle }: ThemeToggleProps): React.ReactElement {
  return (
    <button
      type="button"
      onClick={onToggle}
      aria-label={theme === "dark" ? "Switch to light theme" : "Switch to dark theme"}
      title={theme === "dark" ? "Switch to light theme" : "Switch to dark theme"}
      className="flex h-8 w-8 items-center justify-center rounded-full border border-[var(--color-border)] bg-[var(--color-ink-2)] text-[var(--color-text-dim)] transition-colors hover:text-[var(--color-text)]"
    >
      {theme === "dark" ? <MoonIcon size={16} /> : <SunIcon size={16} />}
    </button>
  );
}
