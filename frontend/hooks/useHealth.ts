"use client";

import { useEffect, useState } from "react";

import { fetchHealth } from "@/lib/api";
import type { HealthResponse } from "@/lib/types";

const POLL_OK_MS = 30_000;
const POLL_RETRY_MS = 5_000;

export interface HealthState {
  health: HealthResponse | null;
  loading: boolean;
}

/**
 * Polls /health for an honest service-status dot. The interval is adaptive: a
 * failed poll retries quickly so a transient first-poll failure does not leave
 * the dot stuck for the full success interval.
 */
export function useHealth(): HealthState {
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let active = true;
    let timer = 0;

    const schedule = (delay: number): void => {
      timer = window.setTimeout(() => void load(), delay);
    };

    const load = async (): Promise<void> => {
      try {
        const result = await fetchHealth();
        if (!active) {
          return;
        }
        setHealth(result);
        schedule(POLL_OK_MS);
      } catch {
        if (!active) {
          return;
        }
        setHealth(null);
        schedule(POLL_RETRY_MS);
      } finally {
        if (active) {
          setLoading(false);
        }
      }
    };

    void load();
    return () => {
      active = false;
      window.clearTimeout(timer);
    };
  }, []);

  return { health, loading };
}
