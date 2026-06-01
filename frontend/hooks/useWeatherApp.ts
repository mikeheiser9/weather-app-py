"use client";

import { useCallback, useEffect, useRef, useState } from "react";

import {
  ApiError,
  type WeatherQuery,
  createFavorite,
  deleteFavorite,
  fetchFavorites,
  fetchHistory,
  fetchWeather,
} from "@/lib/api";
import type { Favorite, HistoryItem, ResolvedLocation, Units, WeatherResponse } from "@/lib/types";

const UNITS_KEY = "wp-units";
const DEFAULT_CITY = process.env.NEXT_PUBLIC_DEFAULT_CITY ?? "Tel Aviv";

export type AppStatus = "idle" | "loading" | "ready" | "error";

function readStoredUnits(): Units {
  if (typeof window === "undefined") {
    return "metric";
  }
  return window.localStorage.getItem(UNITS_KEY) === "imperial" ? "imperial" : "metric";
}

function sameLocation(a: WeatherResponse, lat: number, lon: number): boolean {
  return (
    Math.abs(a.location.latitude - lat) < 0.05 && Math.abs(a.location.longitude - lon) < 0.05
  );
}

export interface WeatherApp {
  weather: WeatherResponse | null;
  status: AppStatus;
  error: string | null;
  units: Units;
  favorites: Favorite[];
  history: HistoryItem[];
  currentFavorite: Favorite | null;
  search: (city: string) => void;
  searchByCoords: (lat: number, lon: number) => void;
  searchByLocation: (location: ResolvedLocation) => void;
  useMyLocation: () => void;
  toggleUnits: () => void;
  addFavorite: () => void;
  removeFavorite: (id: string) => void;
  retry: () => void;
}

export function useWeatherApp(): WeatherApp {
  const [weather, setWeather] = useState<WeatherResponse | null>(null);
  const [status, setStatus] = useState<AppStatus>("idle");
  const [error, setError] = useState<string | null>(null);
  const [units, setUnits] = useState<Units>("metric");
  const [favorites, setFavorites] = useState<Favorite[]>([]);
  const [history, setHistory] = useState<HistoryItem[]>([]);

  const lastQuery = useRef<WeatherQuery | null>(null);
  const lastKnownLocation = useRef<ResolvedLocation | null>(null);

  const refreshFavorites = useCallback(async (): Promise<void> => {
    try {
      setFavorites(await fetchFavorites());
    } catch {
      setFavorites([]);
    }
  }, []);

  const refreshHistory = useCallback(async (): Promise<void> => {
    try {
      setHistory(await fetchHistory());
    } catch {
      setHistory([]);
    }
  }, []);

  const runQuery = useCallback(
    async (query: WeatherQuery, knownLocation: ResolvedLocation | null = null): Promise<void> => {
      lastQuery.current = query;
      lastKnownLocation.current = knownLocation;
      setStatus("loading");
      setError(null);
      try {
        const data = await fetchWeather(query);
        // When a place was picked from search, favorites, or history, we already
        // know its full label; keep it rather than the backend's coordinate stub.
        setWeather(knownLocation ? { ...data, location: knownLocation } : data);
        setStatus("ready");
        void refreshHistory();
      } catch (e) {
        setStatus("error");
        setError(e instanceof ApiError ? e.message : "Unexpected error.");
      }
    },
    [refreshHistory],
  );

  const search = useCallback(
    (city: string): void => {
      const trimmed = city.trim();
      if (trimmed) {
        void runQuery({ city: trimmed, units });
      }
    },
    [runQuery, units],
  );

  const searchByCoords = useCallback(
    (lat: number, lon: number): void => {
      void runQuery({ lat, lon, units });
    },
    [runQuery, units],
  );

  const searchByLocation = useCallback(
    (location: ResolvedLocation): void => {
      void runQuery(
        { lat: location.latitude, lon: location.longitude, name: location.name, units },
        location,
      );
    },
    [runQuery, units],
  );

  const useMyLocation = useCallback((): void => {
    if (typeof navigator === "undefined" || !navigator.geolocation) {
      search(DEFAULT_CITY);
      return;
    }
    navigator.geolocation.getCurrentPosition(
      (pos) => searchByCoords(pos.coords.latitude, pos.coords.longitude),
      () => search(DEFAULT_CITY),
      { timeout: 8000 },
    );
  }, [search, searchByCoords]);

  const toggleUnits = useCallback((): void => {
    setUnits((prev) => {
      const next: Units = prev === "metric" ? "imperial" : "metric";
      window.localStorage.setItem(UNITS_KEY, next);
      if (lastQuery.current) {
        void runQuery({ ...lastQuery.current, units: next }, lastKnownLocation.current);
      }
      return next;
    });
  }, [runQuery]);

  const addFavorite = useCallback((): void => {
    if (!weather) {
      return;
    }
    const query = lastQuery.current?.city ?? weather.location.name;
    void (async () => {
      try {
        await createFavorite({ query, location: weather.location });
        await refreshFavorites();
      } catch {
        /* surfaced via health/status; ignore optimistic failure */
      }
    })();
  }, [weather, refreshFavorites]);

  const removeFavorite = useCallback(
    (id: string): void => {
      void (async () => {
        try {
          await deleteFavorite(id);
          await refreshFavorites();
        } catch {
          /* ignore */
        }
      })();
    },
    [refreshFavorites],
  );

  const retry = useCallback((): void => {
    if (lastQuery.current) {
      void runQuery(lastQuery.current, lastKnownLocation.current);
    } else {
      search(DEFAULT_CITY);
    }
  }, [runQuery, search]);

  useEffect(() => {
    const stored = readStoredUnits();
    setUnits(stored);
    void refreshFavorites();
    void refreshHistory();

    const startCity = (): void => {
      void runQuery({ city: DEFAULT_CITY, units: stored });
    };
    if (typeof navigator !== "undefined" && navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (pos) => void runQuery({ lat: pos.coords.latitude, lon: pos.coords.longitude, units: stored }),
        startCity,
        { timeout: 8000 },
      );
    } else {
      startCity();
    }
    // Run once on mount; helpers are stable enough for the initial bootstrap.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const currentFavorite =
    weather === null
      ? null
      : (favorites.find((f) =>
          sameLocation(weather, f.location.latitude, f.location.longitude),
        ) ?? null);

  return {
    weather,
    status,
    error,
    units,
    favorites,
    history,
    currentFavorite,
    search,
    searchByCoords,
    searchByLocation,
    useMyLocation,
    toggleUnits,
    addFavorite,
    removeFavorite,
    retry,
  };
}
