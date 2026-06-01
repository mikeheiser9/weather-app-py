"use client";

import type { HealthResponse } from "@/lib/types";

interface HealthDotProps {
  health: HealthResponse | null;
}

function color(status: string | undefined): string {
  if (status === "ok") {
    return "#7ec96d";
  }
  if (status === "degraded") {
    return "var(--color-amber)";
  }
  return "var(--color-rose)";
}

function label(health: HealthResponse | null): string {
  if (!health) {
    return "Service unreachable";
  }
  if (health.status === "ok") {
    return "All systems healthy";
  }
  if (health.status === "degraded") {
    return "Running degraded";
  }
  return "Service down";
}

export function HealthDot({ health }: HealthDotProps): React.ReactElement {
  const detail = health
    ? `Redis ${health.redis.status} · Mongo ${health.mongo.status} · Upstream ${health.upstream.status}`
    : "No response from the API";

  return (
    <div className="flex flex-row items-center gap-2" title={detail}>
      <span
        className="inline-block h-2 w-2 rounded-full"
        style={{ backgroundColor: color(health?.status), boxShadow: `0 0 8px ${color(health?.status)}` }}
      />
      <span className="text-[0.72rem] text-[var(--color-text-dim)]">{label(health)}</span>
    </div>
  );
}
