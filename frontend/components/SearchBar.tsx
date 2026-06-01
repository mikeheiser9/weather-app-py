"use client";

import { useEffect, useRef, useState } from "react";

import { LocationIcon, SearchIcon } from "@/components/icons";
import { searchLocations } from "@/lib/api";
import { locationLabel } from "@/lib/format";
import type { ResolvedLocation } from "@/lib/types";

interface SearchBarProps {
  onSearch: (city: string) => void;
  onSelectLocation: (location: ResolvedLocation) => void;
  onUseLocation: () => void;
  busy: boolean;
}

const DEBOUNCE_MS = 250;
const MIN_CHARS = 2;

export function SearchBar({
  onSearch,
  onSelectLocation,
  onUseLocation,
  busy,
}: SearchBarProps): React.ReactElement {
  const [value, setValue] = useState("");
  const [suggestions, setSuggestions] = useState<ResolvedLocation[]>([]);
  const [open, setOpen] = useState(false);
  const [activeIndex, setActiveIndex] = useState(-1);
  const blurTimer = useRef<number | null>(null);

  useEffect(() => {
    const query = value.trim();
    if (query.length < MIN_CHARS) {
      setSuggestions([]);
      setOpen(false);
      return;
    }
    let cancelled = false;
    const id = window.setTimeout(() => {
      void searchLocations(query)
        .then((results) => {
          if (!cancelled) {
            setSuggestions(results);
            setOpen(results.length > 0);
            setActiveIndex(-1);
          }
        })
        .catch(() => {
          if (!cancelled) {
            setSuggestions([]);
            setOpen(false);
          }
        });
    }, DEBOUNCE_MS);
    return () => {
      cancelled = true;
      window.clearTimeout(id);
    };
  }, [value]);

  const reset = (): void => {
    setValue("");
    setSuggestions([]);
    setOpen(false);
    setActiveIndex(-1);
  };

  const selectLocation = (location: ResolvedLocation): void => {
    onSelectLocation(location);
    reset();
  };

  const submit = (e: React.FormEvent): void => {
    e.preventDefault();
    const trimmed = value.trim();
    if (trimmed) {
      onSearch(trimmed);
      reset();
    }
  };

  const onKeyDown = (e: React.KeyboardEvent<HTMLInputElement>): void => {
    if (e.key === "ArrowDown") {
      e.preventDefault();
      if (suggestions.length > 0) {
        setOpen(true);
        setActiveIndex((prev) => Math.min(prev + 1, suggestions.length - 1));
      }
    } else if (e.key === "ArrowUp") {
      e.preventDefault();
      setActiveIndex((prev) => Math.max(prev - 1, 0));
    } else if (e.key === "Enter") {
      if (open && activeIndex >= 0 && suggestions[activeIndex]) {
        e.preventDefault();
        selectLocation(suggestions[activeIndex]);
      }
    } else if (e.key === "Escape") {
      setOpen(false);
      setActiveIndex(-1);
    }
  };

  return (
    <form onSubmit={submit} className="flex flex-col gap-2">
      <div className="relative">
        <div className="flex flex-row items-center gap-2 rounded-[var(--radius-card)] border border-[var(--color-border)] bg-[var(--color-ink-2)] px-3 py-2.5">
          <SearchIcon className="shrink-0 text-[var(--color-text-dim)]" />
          <input
            type="text"
            value={value}
            onChange={(e) => setValue(e.target.value)}
            onKeyDown={onKeyDown}
            onFocus={() => suggestions.length > 0 && setOpen(true)}
            onBlur={() => {
              blurTimer.current = window.setTimeout(() => setOpen(false), 150);
            }}
            placeholder="Search a city"
            aria-label="Search a city"
            autoComplete="off"
            role="combobox"
            aria-expanded={open}
            aria-controls="city-suggestions"
            className="w-full bg-transparent text-[0.95rem] text-[var(--color-text)] outline-none placeholder:text-[var(--color-text-faint)]"
          />
        </div>

        {open && suggestions.length > 0 && (
          <ul
            id="city-suggestions"
            role="listbox"
            className="absolute left-0 right-0 top-full z-30 mt-1.5 flex max-h-72 flex-col overflow-y-auto rounded-[var(--radius-card)] border border-[var(--color-border-strong)] bg-[var(--color-panel-solid)] p-1 shadow-[0_18px_40px_rgba(0,0,0,0.5)]"
          >
            {suggestions.map((location, index) => (
              <li key={`${location.name}-${location.latitude}-${location.longitude}`}>
                <button
                  type="button"
                  role="option"
                  aria-selected={index === activeIndex}
                  onMouseEnter={() => setActiveIndex(index)}
                  onMouseDown={(e) => {
                    e.preventDefault();
                    if (blurTimer.current) {
                      window.clearTimeout(blurTimer.current);
                    }
                    selectLocation(location);
                  }}
                  className={`flex w-full flex-col gap-0.5 rounded-[calc(var(--radius-card)-4px)] px-3 py-2 text-left transition-colors ${
                    index === activeIndex ? "bg-[var(--color-ink-2)]" : ""
                  }`}
                >
                  <span className="truncate text-[0.88rem] text-[var(--color-text)]">
                    {location.name}
                  </span>
                  <span className="truncate text-[0.72rem] text-[var(--color-text-faint)]">
                    {locationLabel(location)}
                  </span>
                </button>
              </li>
            ))}
          </ul>
        )}
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
