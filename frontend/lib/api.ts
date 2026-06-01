/**
 * Thin API client for the weather proxy backend. The base URL comes from
 * NEXT_PUBLIC_API_BASE_URL; the backend host is never hardcoded in components.
 */

import { getClientId } from "@/lib/clientId";
import type {
  ApiErrorBody,
  Favorite,
  FavoriteCreate,
  HealthResponse,
  HistoryItem,
  ResolvedLocation,
  Units,
  WeatherResponse,
} from "@/lib/types";

const BASE_URL = (process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000").replace(
  /\/$/,
  "",
);

export class ApiError extends Error {
  readonly status: number;
  readonly code: string;

  constructor(status: number, code: string, message: string) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.code = code;
  }
}

async function request<T>(
  path: string,
  options: { method?: string; body?: unknown; withClientId?: boolean } = {},
): Promise<T> {
  const headers: Record<string, string> = {};
  if (options.body !== undefined) {
    headers["Content-Type"] = "application/json";
  }
  if (options.withClientId) {
    headers["X-Client-Id"] = getClientId();
  }

  let response: Response;
  try {
    response = await fetch(`${BASE_URL}${path}`, {
      method: options.method ?? "GET",
      headers,
      body: options.body !== undefined ? JSON.stringify(options.body) : undefined,
      cache: "no-store",
    });
  } catch {
    throw new ApiError(0, "network_error", "Could not reach the weather service.");
  }

  if (response.status === 204) {
    return undefined as T;
  }

  let payload: unknown = null;
  const text = await response.text();
  if (text) {
    try {
      payload = JSON.parse(text);
    } catch {
      payload = null;
    }
  }

  if (!response.ok) {
    const body = payload as ApiErrorBody | null;
    const code = body?.error?.code ?? "error";
    const message = body?.error?.message ?? "Something went wrong.";
    throw new ApiError(response.status, code, message);
  }

  return payload as T;
}

export interface WeatherQuery {
  city?: string;
  lat?: number;
  lon?: number;
  name?: string;
  units: Units;
}

export function fetchWeather(query: WeatherQuery): Promise<WeatherResponse> {
  const params = new URLSearchParams();
  if (query.city) {
    params.set("city", query.city);
  }
  if (query.lat !== undefined && query.lon !== undefined) {
    params.set("lat", String(query.lat));
    params.set("lon", String(query.lon));
  }
  if (query.name) {
    params.set("name", query.name);
  }
  params.set("units", query.units);
  return request<WeatherResponse>(`/weather?${params.toString()}`, { withClientId: true });
}

export function fetchHealth(): Promise<HealthResponse> {
  return request<HealthResponse>("/health");
}

export function searchLocations(query: string, count = 5): Promise<ResolvedLocation[]> {
  const params = new URLSearchParams({ q: query, count: String(count) });
  return request<ResolvedLocation[]>(`/geocode?${params.toString()}`);
}

export function fetchFavorites(): Promise<Favorite[]> {
  return request<Favorite[]>("/favorites", { withClientId: true });
}

export function createFavorite(data: FavoriteCreate): Promise<Favorite> {
  return request<Favorite>("/favorites", {
    method: "POST",
    body: data,
    withClientId: true,
  });
}

export function deleteFavorite(id: string): Promise<void> {
  return request<void>(`/favorites/${encodeURIComponent(id)}`, {
    method: "DELETE",
    withClientId: true,
  });
}

export function fetchHistory(): Promise<HistoryItem[]> {
  return request<HistoryItem[]>("/history", { withClientId: true });
}
