"use client";

import { ClockIcon } from "@/components/icons";
import { shortLocationLabel } from "@/lib/format";
import type { HistoryItem } from "@/lib/types";

interface HistoryListProps {
  history: HistoryItem[];
  onSelect: (item: HistoryItem) => void;
}

export function HistoryList({ history, onSelect }: HistoryListProps): React.ReactElement {
  return (
    <div className="flex flex-col gap-2">
      <span className="tracked-label">Recent searches</span>
      {history.length === 0 ? (
        <p className="text-[0.78rem] text-[var(--color-text-faint)]">No searches yet.</p>
      ) : (
        <ul className="flex flex-col gap-1.5">
          {history.slice(0, 8).map((item, index) => (
            <li key={`${item.query}-${index}`}>
              <button
                type="button"
                onClick={() => onSelect(item)}
                className="flex w-full flex-row items-center gap-2 rounded-[var(--radius-card)] px-3 py-2 text-left transition-colors hover:bg-[var(--color-ink-2)]"
              >
                <span className="text-[var(--color-text-faint)]">
                  <ClockIcon size={14} />
                </span>
                <span className="flex-1 truncate text-[0.84rem] text-[var(--color-text-dim)]">
                  {shortLocationLabel(item.location)}
                </span>
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
