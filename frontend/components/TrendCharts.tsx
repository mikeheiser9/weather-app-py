"use client";

import {
  Area,
  AreaChart,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import { hourFromTime } from "@/lib/format";
import type { WeatherResponse } from "@/lib/types";

interface TrendChartsProps {
  weather: WeatherResponse;
}

interface Point {
  t: string;
  temp: number | null;
  precip: number | null;
}

const axisStyle = { fill: "var(--color-text-faint)", fontSize: 11 } as const;

function ChartCard({
  title,
  unit,
  children,
}: {
  title: string;
  unit: string;
  children: React.ReactElement;
}): React.ReactElement {
  return (
    <div className="frost flex flex-1 flex-col gap-3 rounded-[var(--radius-panel)] p-5">
      <div className="flex flex-row items-baseline justify-between">
        <span className="tracked-label">{title}</span>
        <span className="text-[0.7rem] text-[var(--color-text-faint)]">{unit}</span>
      </div>
      <div className="h-[170px] w-full">
        <ResponsiveContainer width="100%" height="100%">
          {children}
        </ResponsiveContainer>
      </div>
    </div>
  );
}

export function TrendCharts({ weather }: TrendChartsProps): React.ReactElement {
  const data: Point[] = weather.hourly.map((p) => ({
    t: hourFromTime(p.time),
    temp: p.temperature,
    precip: p.precipitation_probability,
  }));

  return (
    <section className="flex flex-row gap-4 max-ipad:flex-col">
      <ChartCard title="Temperature trend" unit={weather.unit_labels.temperature}>
        <LineChart data={data} margin={{ top: 6, right: 8, bottom: 0, left: -18 }}>
          <XAxis dataKey="t" tick={axisStyle} tickLine={false} axisLine={false} interval={3} />
          <YAxis tick={axisStyle} tickLine={false} axisLine={false} width={36} />
          <Tooltip
            contentStyle={{
              background: "var(--color-panel-solid)",
              border: "1px solid var(--color-border-strong)",
              borderRadius: 12,
              color: "var(--color-text)",
              fontSize: 12,
            }}
            cursor={{ stroke: "var(--color-border-strong)" }}
          />
          <Line
            type="monotone"
            dataKey="temp"
            stroke="var(--color-amber)"
            strokeWidth={2}
            dot={false}
            connectNulls
          />
        </LineChart>
      </ChartCard>

      <ChartCard title="Precipitation chance" unit="%">
        <AreaChart data={data} margin={{ top: 6, right: 8, bottom: 0, left: -18 }}>
          <defs>
            <linearGradient id="precipFill" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="var(--color-rose)" stopOpacity={0.45} />
              <stop offset="100%" stopColor="var(--color-rose)" stopOpacity={0.02} />
            </linearGradient>
          </defs>
          <XAxis dataKey="t" tick={axisStyle} tickLine={false} axisLine={false} interval={3} />
          <YAxis tick={axisStyle} tickLine={false} axisLine={false} width={36} domain={[0, 100]} />
          <Tooltip
            contentStyle={{
              background: "var(--color-panel-solid)",
              border: "1px solid var(--color-border-strong)",
              borderRadius: 12,
              color: "var(--color-text)",
              fontSize: 12,
            }}
            cursor={{ stroke: "var(--color-border-strong)" }}
          />
          <Area
            type="monotone"
            dataKey="precip"
            stroke="var(--color-rose)"
            strokeWidth={2}
            fill="url(#precipFill)"
            connectNulls
          />
        </AreaChart>
      </ChartCard>
    </section>
  );
}
