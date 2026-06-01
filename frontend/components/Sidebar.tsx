"use client";

import { FavoritesList } from "@/components/FavoritesList";
import { Footer } from "@/components/Footer";
import { HealthDot } from "@/components/HealthDot";
import { HistoryList } from "@/components/HistoryList";
import { SearchBar } from "@/components/SearchBar";
import type { Favorite, HealthResponse, HistoryItem, ResolvedLocation } from "@/lib/types";

interface SidebarProps {
  health: HealthResponse | null;
  healthLoading: boolean;
  busy: boolean;
  favorites: Favorite[];
  history: HistoryItem[];
  onSearch: (city: string) => void;
  onSelectLocation: (location: ResolvedLocation) => void;
  onUseLocation: () => void;
  onSelectFavorite: (favorite: Favorite) => void;
  onRemoveFavorite: (id: string) => void;
  onSelectHistory: (item: HistoryItem) => void;
}

export function Sidebar({
  health,
  healthLoading,
  busy,
  favorites,
  history,
  onSearch,
  onSelectLocation,
  onUseLocation,
  onSelectFavorite,
  onRemoveFavorite,
  onSelectHistory,
}: SidebarProps): React.ReactElement {
  return (
    <aside className="frost flex w-[340px] shrink-0 flex-col gap-6 rounded-[var(--radius-panel)] p-6 max-ipad:w-full">
      <div className="flex flex-col gap-3">
        <div className="flex flex-row items-center justify-between">
          <h1 className="text-[1.05rem] font-semibold tracking-tight text-[var(--color-text)]">
            Weather<span className="text-[var(--color-amber)]">Proxy</span>
          </h1>
        </div>
        <HealthDot health={health} loading={healthLoading} />
      </div>

      <SearchBar
        onSearch={onSearch}
        onSelectLocation={onSelectLocation}
        onUseLocation={onUseLocation}
        busy={busy}
      />

      <FavoritesList
        favorites={favorites}
        onSelect={onSelectFavorite}
        onRemove={onRemoveFavorite}
      />

      <HistoryList history={history} onSelect={onSelectHistory} />

      <div className="mt-auto">
        <Footer />
      </div>
    </aside>
  );
}
