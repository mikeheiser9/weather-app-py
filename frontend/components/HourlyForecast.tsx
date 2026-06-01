import { ConditionGlyph } from "@/components/icons";
import { formatTemp, hourFromTime } from "@/lib/format";
import type { HourlyPoint, UnitLabels } from "@/lib/types";

interface HourlyForecastProps {
  hourly: HourlyPoint[];
  unitLabels: UnitLabels;
}

export function HourlyForecast({ hourly, unitLabels }: HourlyForecastProps): React.ReactElement {
  return (
    <section className="frost flex flex-col gap-4 rounded-[var(--radius-panel)] p-5">
      <span className="tracked-label">Next 24 hours</span>
      <div className="flex flex-row gap-2 overflow-x-auto pb-1">
        {hourly.map((point, index) => (
          <div
            key={point.time}
            className="flex min-w-[64px] flex-col items-center gap-2 rounded-[var(--radius-card)] border border-[var(--color-border)] bg-[var(--color-ink-2)] px-2 py-3"
          >
            <span className="text-[0.72rem] text-[var(--color-text-dim)]">
              {index === 0 ? "Now" : hourFromTime(point.time)}
            </span>
            <span className="text-[var(--color-amber-soft)]">
              <ConditionGlyph category={point.condition_category} size={18} />
            </span>
            <span className="text-[0.92rem] font-light text-[var(--color-text)]">
              {formatTemp(point.temperature)}
              {unitLabels.temperature}
            </span>
            <span className="text-[0.68rem] text-[var(--color-text-faint)]">
              {point.precipitation_probability === null
                ? "--"
                : `${point.precipitation_probability}%`}
            </span>
          </div>
        ))}
      </div>
    </section>
  );
}
