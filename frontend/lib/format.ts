/** Small presentation helpers. No business logic lives here. */

import type { ResolvedLocation } from "@/lib/types";

export function formatTemp(value: number | null | undefined): string {
  if (value === null || value === undefined) {
    return "--";
  }
  return String(Math.round(value));
}

export function formatNumber(value: number | null | undefined, digits = 0): string {
  if (value === null || value === undefined) {
    return "--";
  }
  return value.toFixed(digits);
}

export function locationLabel(location: ResolvedLocation): string {
  const parts = [location.name];
  if (location.admin1 && location.admin1 !== location.name) {
    parts.push(location.admin1);
  }
  if (location.country) {
    parts.push(location.country);
  }
  return parts.join(", ");
}

export function shortLocationLabel(location: ResolvedLocation): string {
  if (location.country_code) {
    return `${location.name}, ${location.country_code}`;
  }
  return location.name;
}

const WEEKDAY = new Intl.DateTimeFormat("en-US", { weekday: "short" });
const HOUR = new Intl.DateTimeFormat("en-US", { hour: "numeric" });

export function weekdayFromDate(isoDate: string): string {
  const date = new Date(`${isoDate}T00:00:00`);
  if (Number.isNaN(date.getTime())) {
    return isoDate;
  }
  return WEEKDAY.format(date);
}

export function hourFromTime(isoTime: string): string {
  const date = new Date(isoTime);
  if (Number.isNaN(date.getTime())) {
    return isoTime;
  }
  return HOUR.format(date);
}

export function aqiBand(aqi: number | null | undefined): { label: string; color: string } {
  if (aqi === null || aqi === undefined) {
    return { label: "Unknown", color: "var(--color-text-dim)" };
  }
  if (aqi <= 50) {
    return { label: "Good", color: "#7ec96d" };
  }
  if (aqi <= 100) {
    return { label: "Moderate", color: "var(--color-amber)" };
  }
  if (aqi <= 150) {
    return { label: "Sensitive", color: "#f0884a" };
  }
  if (aqi <= 200) {
    return { label: "Unhealthy", color: "var(--color-rose)" };
  }
  if (aqi <= 300) {
    return { label: "Very unhealthy", color: "#c061d6" };
  }
  return { label: "Hazardous", color: "#d65b5b" };
}
