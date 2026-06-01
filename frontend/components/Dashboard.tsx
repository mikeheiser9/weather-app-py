"use client";

import { AirQualityCard } from "@/components/AirQualityCard";
import { CurrentHero } from "@/components/CurrentHero";
import { DailyForecast } from "@/components/DailyForecast";
import { HourlyForecast } from "@/components/HourlyForecast";
import { MetricsRow } from "@/components/MetricsRow";
import { Sidebar } from "@/components/Sidebar";
import { ThemeToggle, UnitToggle } from "@/components/Toggles";
import { TrendCharts } from "@/components/TrendCharts";
import { useHealth } from "@/hooks/useHealth";
import { useTheme } from "@/hooks/useTheme";
import { useWeatherApp } from "@/hooks/useWeatherApp";

export function Dashboard(): React.ReactElement {
  const app = useWeatherApp();
  const { health, loading: healthLoading } = useHealth();
  const { theme, toggleTheme } = useTheme();
  const busy = app.status === "loading";

  return (
    <div className="relative z-10 mx-auto flex min-h-screen w-full max-w-[1500px] flex-row gap-5 p-5 max-ipad:flex-col max-small:p-3">
      <Sidebar
        health={health}
        healthLoading={healthLoading}
        busy={busy}
        favorites={app.favorites}
        history={app.history}
        onSearch={app.search}
        onSelectLocation={(loc) => app.searchByCoords(loc.latitude, loc.longitude)}
        onUseLocation={app.useMyLocation}
        onSelectFavorite={(fav) => app.searchByCoords(fav.location.latitude, fav.location.longitude)}
        onRemoveFavorite={app.removeFavorite}
        onSelectHistory={(item) =>
          app.searchByCoords(item.location.latitude, item.location.longitude)
        }
      />

      <main className="flex min-w-0 flex-1 flex-col gap-5">
        <div className="flex flex-row items-center justify-end gap-3">
          <UnitToggle units={app.units} onToggle={app.toggleUnits} />
          <ThemeToggle theme={theme} onToggle={toggleTheme} />
        </div>

        {app.status === "error" && !app.weather ? (
          <div className="frost flex flex-1 flex-col items-center justify-center gap-4 rounded-[var(--radius-panel)] p-10 text-center">
            <p className="text-[1.05rem] text-[var(--color-text)]">{app.error}</p>
            <button
              type="button"
              onClick={app.retry}
              className="rounded-[var(--radius-card)] bg-[var(--color-amber)] px-4 py-2 text-[0.85rem] font-semibold text-[#1a1304]"
            >
              Try again
            </button>
          </div>
        ) : app.weather ? (
          <div
            className={`flex flex-col gap-5 transition-opacity ${busy ? "opacity-60" : "opacity-100"}`}
          >
            <CurrentHero
              weather={app.weather}
              currentFavorite={app.currentFavorite}
              onAddFavorite={app.addFavorite}
              onRemoveFavorite={app.removeFavorite}
            />
            <MetricsRow weather={app.weather} />
            <DailyForecast daily={app.weather.daily} unitLabels={app.weather.unit_labels} />
            <TrendCharts weather={app.weather} />
            <HourlyForecast hourly={app.weather.hourly} unitLabels={app.weather.unit_labels} />
            <AirQualityCard airQuality={app.weather.air_quality} />
          </div>
        ) : (
          <div className="frost flex flex-1 items-center justify-center rounded-[var(--radius-panel)] p-10">
            <span className="tracked-label animate-pulse">Loading weather</span>
          </div>
        )}
      </main>
    </div>
  );
}
