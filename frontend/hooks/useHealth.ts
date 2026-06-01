"use client";

import { useEffect, useState } from "react";

import { fetchHealth } from "@/lib/api";
import type { HealthResponse } from "@/lib/types";

const POLL_MS = 30_000;

/** Polls /health so the sidebar can show an honest service status dot. */
export function useHealth(): HealthResponse | null {
  const [health, setHealth] = useState<HealthResponse | null>(null);

  useEffect(() => {
    let active = true;

    const load = async (): Promise<void> => {
      try {
        const result = await fetchHealth();
        if (active) {
          setHealth(result);
        }
      } catch {
        if (active) {
          setHealth(null);
        }
      }
    };

    void load();
    const timer = window.setInterval(() => void load(), POLL_MS);
    return () => {
      active = false;
      window.clearInterval(timer);
    };
  }, []);

  return health;
}
