"use client";

import { useState } from "react";

import { LocationIcon, SearchIcon } from "@/components/icons";

interface SearchBarProps {
  onSearch: (city: string) => void;
  onUseLocation: () => void;
  busy: boolean;
}

export function SearchBar({ onSearch, onUseLocation, busy }: SearchBarProps): React.ReactElement {
  const [value, setValue] = useState("");

  const submit = (e: React.FormEvent): void => {
    e.preventDefault();
    if (value.trim()) {
      onSearch(value);
      setValue("");
    }
  };

  return (
    <form onSubmit={submit} className="flex flex-col gap-2">
      <div className="flex flex-row items-center gap-2 rounded-[var(--radius-card)] border border-[var(--color-border)] bg-[var(--color-ink-2)] px-3 py-2.5">
        <SearchIcon className="shrink-0 text-[var(--color-text-dim)]" />
        <input
          type="text"
          value={value}
          onChange={(e) => setValue(e.target.value)}
          placeholder="Search a city"
          aria-label="Search a city"
          className="w-full bg-transparent text-[0.95rem] text-[var(--color-text)] outline-none placeholder:text-[var(--color-text-faint)]"
        />
      </div>
      <div className="flex flex-row gap-2">
        <button
          type="submit"
          disabled={busy || !value.trim()}
          className="flex flex-1 items-center justify-center rounded-[var(--radius-card)] bg-[var(--color-amber)] px-3 py-2 text-[0.82rem] font-semibold tracking-wide text-[#1a1304] transition-opacity disabled:opacity-40"
        >
          Search
        </button>
        <button
          type="button"
          onClick={onUseLocation}
          disabled={busy}
          aria-label="Use my location"
          title="Use my location"
          className="flex items-center justify-center rounded-[var(--radius-card)] border border-[var(--color-border)] px-3 py-2 text-[var(--color-text-dim)] transition-colors hover:text-[var(--color-text)] disabled:opacity-40"
        >
          <LocationIcon />
        </button>
      </div>
    </form>
  );
}
