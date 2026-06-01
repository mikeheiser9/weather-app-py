/**
 * Category to visual mapping. The WMO code to category mapping is owned by the
 * backend (single source of truth) and surfaced on every response; here we map
 * that category to a committed background image plus a gradient fallback so the
 * UI never re-derives weather codes and never calls a runtime image API.
 */

import type { ConditionCategory } from "@/lib/types";

interface CategoryVisual {
  label: string;
  /** Dark gradient shown behind (and as fallback for) the static image. */
  gradient: string;
}

const VISUALS: Record<ConditionCategory, CategoryVisual> = {
  clear: {
    label: "Clear",
    gradient: "linear-gradient(150deg, #1b1733 0%, #4a3a5c 48%, #b9772f 100%)",
  },
  cloudy: {
    label: "Cloudy",
    gradient: "linear-gradient(150deg, #14161c 0%, #2c313c 52%, #565d6b 100%)",
  },
  fog: {
    label: "Fog",
    gradient: "linear-gradient(150deg, #15171b 0%, #353a40 55%, #5d646b 100%)",
  },
  drizzle: {
    label: "Drizzle",
    gradient: "linear-gradient(150deg, #11161d 0%, #25323f 55%, #3f5566 100%)",
  },
  rain: {
    label: "Rain",
    gradient: "linear-gradient(150deg, #0d1418 0%, #18313a 55%, #2b5160 100%)",
  },
  snow: {
    label: "Snow",
    gradient: "linear-gradient(150deg, #161a1f 0%, #36414c 55%, #6f7d8a 100%)",
  },
  thunderstorm: {
    label: "Thunderstorm",
    gradient: "linear-gradient(150deg, #0b0a12 0%, #241d33 52%, #4a3a63 100%)",
  },
};

export function categoryLabel(category: ConditionCategory): string {
  return VISUALS[category].label;
}

export function categoryGradient(category: ConditionCategory): string {
  return VISUALS[category].gradient;
}

export function categoryBackground(category: ConditionCategory): string {
  return `/backgrounds/${category}.jpg`;
}
