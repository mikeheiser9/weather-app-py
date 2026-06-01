import { DropletIcon, ThermometerIcon, WindIcon } from "@/components/icons";
import { formatNumber, formatTemp } from "@/lib/format";
import type { WeatherResponse } from "@/lib/types";

interface MetricsRowProps {
  weather: WeatherResponse;
}

interface Metric {
  icon: React.ReactElement;
  label: string;
  value: string;
}

export function MetricsRow({ weather }: MetricsRowProps): React.ReactElement {
  const { current, unit_labels } = weather;
  const metrics: Metric[] = [
    {
      icon: <DropletIcon size={18} />,
      label: "Humidity",
      value: current.relative_humidity === null ? "--" : `${current.relative_humidity}%`,
    },
    {
      icon: <WindIcon size={18} />,
      label: "Wind",
      value: `${formatNumber(current.wind_speed)} ${unit_labels.wind_speed}`,
    },
    {
      icon: <ThermometerIcon size={18} />,
      label: "Precip",
      value: `${formatNumber(current.precipitation, 1)} ${unit_labels.precipitation}`,
    },
    {
      icon: <ThermometerIcon size={18} />,
      label: "Feels like",
      value: `${formatTemp(current.apparent_temperature)}${unit_labels.temperature}`,
    },
  ];

  return (
    <div className="flex flex-row gap-3 max-small:flex-wrap">
      {metrics.map((m) => (
        <div
          key={m.label}
          className="frost flex flex-1 flex-col gap-2 rounded-[var(--radius-card)] p-4 max-small:min-w-[45%]"
        >
          <span className="text-[var(--color-amber-soft)]">{m.icon}</span>
          <span className="tracked-label">{m.label}</span>
          <span className="text-[1.1rem] font-light text-[var(--color-text)]">{m.value}</span>
        </div>
      ))}
    </div>
  );
}
