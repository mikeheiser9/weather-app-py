"use client";

import { StarIcon, TrashIcon } from "@/components/icons";
import { shortLocationLabel } from "@/lib/format";
import type { Favorite } from "@/lib/types";

interface FavoritesListProps {
  favorites: Favorite[];
  onSelect: (favorite: Favorite) => void;
  onRemove: (id: string) => void;
}

export function FavoritesList({
  favorites,
  onSelect,
  onRemove,
}: FavoritesListProps): React.ReactElement {
  return (
    <div className="flex flex-col gap-2">
      <span className="tracked-label">Favorites</span>
      {favorites.length === 0 ? (
        <p className="text-[0.78rem] text-[var(--color-text-faint)]">
          Star a city to pin it here.
        </p>
      ) : (
        <ul className="flex flex-col gap-1.5">
          {favorites.map((fav) => (
            <li
              key={fav.id}
              className="flex flex-row items-center gap-2 rounded-[var(--radius-card)] border border-[var(--color-border)] bg-[var(--color-ink-2)] px-3 py-2"
            >
              <span className="text-[var(--color-amber)]">
                <StarIcon filled size={15} />
              </span>
              <button
                type="button"
                onClick={() => onSelect(fav)}
                className="flex-1 truncate text-left text-[0.86rem] text-[var(--color-text)] transition-colors hover:text-[var(--color-amber-soft)]"
                title={shortLocationLabel(fav.location)}
              >
                {shortLocationLabel(fav.location)}
              </button>
              <button
                type="button"
                onClick={() => onRemove(fav.id)}
                aria-label={`Remove ${fav.location.name} from favorites`}
                className="text-[var(--color-text-faint)] transition-colors hover:text-[var(--color-rose)]"
              >
                <TrashIcon size={15} />
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
