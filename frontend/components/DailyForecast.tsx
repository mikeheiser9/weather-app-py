import { ConditionGlyph } from "@/components/icons";
import { formatTemp, weekdayFromDate } from "@/lib/format";
import type { DailyPoint, UnitLabels } from "@/lib/types";

interface DailyForecastProps {
  daily: DailyPoint[];
  unitLabels: UnitLabels;
}

export function DailyForecast({ daily, unitLabels }: DailyForecastProps): React.ReactElement {
  return (
    <section className="frost flex flex-col gap-4 rounded-[var(--radius-panel)] p-5">
      <span className="tracked-label">7 day forecast</span>
      <div className="flex flex-row gap-2.5 max-tablet-lg:flex-wrap">
        {daily.map((day, index) => (
          <div
            key={day.date}
            className="flex flex-1 flex-col items-center gap-2.5 rounded-[var(--radius-card)] border border-[var(--color-border)] bg-[var(--color-ink-2)] py-4 max-tablet-lg:min-w-[30%]"
          >
            <span className="text-[0.78rem] text-[var(--color-text-dim)]">
              {index === 0 ? "Today" : weekdayFromDate(day.date)}
            </span>
            <span className="text-[var(--color-amber-soft)]">
              <ConditionGlyph category={day.condition_category} size={22} />
            </span>
            <div className="flex flex-col items-center">
              <span className="text-[1.05rem] font-light text-[var(--color-text)]">
                {formatTemp(day.temperature_max)}
                {unitLabels.temperature}
              </span>
              <span className="text-[0.82rem] text-[var(--color-text-faint)]">
                {formatTemp(day.temperature_min)}
                {unitLabels.temperature}
              </span>
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}
