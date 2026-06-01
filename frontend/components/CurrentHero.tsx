"use client";

import { useState } from "react";

import { ConditionGlyph, StarIcon } from "@/components/icons";
import { formatTemp, locationLabel } from "@/lib/format";
import type { Favorite, WeatherResponse } from "@/lib/types";
import { categoryBackground, categoryGradient, categoryLabel } from "@/lib/wmo";

interface CurrentHeroProps {
  weather: WeatherResponse;
  currentFavorite: Favorite | null;
  onAddFavorite: () => void;
  onRemoveFavorite: (id: string) => void;
}

export function CurrentHero({
  weather,
  currentFavorite,
  onAddFavorite,
  onRemoveFavorite,
}: CurrentHeroProps): React.ReactElement {
  const [imageOk, setImageOk] = useState(true);
  const category = weather.condition_category;
  const isFavorite = currentFavorite !== null;

  const toggleFavorite = (): void => {
    if (currentFavorite) {
      onRemoveFavorite(currentFavorite.id);
    } else {
      onAddFavorite();
    }
  };

  return (
    <section
      className="relative flex min-h-[340px] flex-col justify-between overflow-hidden rounded-[var(--radius-panel)] border border-[var(--color-border)] p-7 max-small:min-h-[280px] max-small:p-5"
      style={{ background: categoryGradient(category) }}
    >
      {imageOk && (
        // eslint-disable-next-line @next/next/no-img-element
        <img
          src={categoryBackground(category)}
          alt=""
          aria-hidden
          onError={() => setImageOk(false)}
          className="absolute inset-0 h-full w-full object-cover"
        />
      )}
      <div
        className="absolute inset-0"
        style={{
          background:
            "linear-gradient(165deg, var(--color-scrim) 0%, rgba(8,8,10,0.35) 45%, var(--color-scrim) 100%)",
        }}
      />

      <div className="relative flex flex-row items-start justify-between gap-4">
        <div className="flex flex-col gap-1">
          <span className="tracked-label text-[#f4f1ea]/70">Now</span>
          <h2 className="text-[1.35rem] font-medium leading-tight text-[#f6f3ec]">
            {locationLabel(weather.location)}
          </h2>
        </div>
        <div className="flex flex-row items-center gap-2">
          {weather.cache && (
            <span className="rounded-full border border-white/20 px-2.5 py-1 text-[0.62rem] uppercase tracking-wider text-[#f4f1ea]/80">
              Cached
            </span>
          )}
          <button
            type="button"
            onClick={toggleFavorite}
            aria-label={isFavorite ? "Remove from favorites" : "Add to favorites"}
            title={isFavorite ? "Remove from favorites" : "Add to favorites"}
            className="flex h-9 w-9 items-center justify-center rounded-full border border-white/20 bg-black/25 text-[var(--color-amber)] transition-transform hover:scale-105"
          >
            <StarIcon filled={isFavorite} size={18} />
          </button>
        </div>
      </div>

      <div className="relative flex flex-row items-end justify-between gap-4 max-small:flex-col max-small:items-start">
        <div className="flex flex-col">
          <div className="flex flex-row items-start">
            <span className="text-[7rem] font-extralight leading-[0.85] tracking-tight text-[#f8f5ee] max-small:text-[5rem]">
              {formatTemp(weather.current.temperature)}
            </span>
            <span className="mt-3 text-[2rem] font-light text-[#f8f5ee]/80">
              {weather.unit_labels.temperature}
            </span>
          </div>
          <div className="mt-2 flex flex-row items-center gap-2 text-[#f4f1ea]/85">
            <ConditionGlyph category={category} size={20} />
            <span className="text-[1rem]">{categoryLabel(category)}</span>
          </div>
        </div>
        <div className="flex flex-col items-end gap-0.5 text-right max-small:items-start max-small:text-left">
          <span className="tracked-label text-[#f4f1ea]/60">Feels like</span>
          <span className="text-[1.5rem] font-light text-[#f6f3ec]">
            {formatTemp(weather.current.apparent_temperature)}
            {weather.unit_labels.temperature}
          </span>
        </div>
      </div>
    </section>
  );
}
