import { aqiBand, formatNumber } from "@/lib/format";
import type { AirQuality } from "@/lib/types";

interface AirQualityCardProps {
  airQuality: AirQuality | null;
}

export function AirQualityCard({ airQuality }: AirQualityCardProps): React.ReactElement | null {
  if (!airQuality) {
    return null;
  }
  const band = aqiBand(airQuality.us_aqi);
  const pollutants: { label: string; value: string }[] = [
    { label: "PM2.5", value: formatNumber(airQuality.pm2_5, 1) },
    { label: "PM10", value: formatNumber(airQuality.pm10, 1) },
    { label: "Ozone", value: formatNumber(airQuality.ozone, 0) },
    { label: "NO2", value: formatNumber(airQuality.nitrogen_dioxide, 0) },
  ];

  return (
    <section className="frost flex flex-col gap-4 rounded-[var(--radius-panel)] p-5">
      <span className="tracked-label">Air quality</span>
      <div className="flex flex-row items-end gap-3">
        <span className="text-[3rem] font-extralight leading-none text-[var(--color-text)]">
          {airQuality.us_aqi ?? "--"}
        </span>
        <div className="flex flex-col pb-1">
          <span className="text-[0.7rem] text-[var(--color-text-faint)]">US AQI</span>
          <span className="text-[0.9rem] font-medium" style={{ color: band.color }}>
            {band.label}
          </span>
        </div>
      </div>
      <div className="flex flex-row flex-wrap gap-2">
        {pollutants.map((p) => (
          <div
            key={p.label}
            className="flex flex-1 flex-col gap-1 rounded-[var(--radius-card)] border border-[var(--color-border)] bg-[var(--color-ink-2)] px-3 py-2"
          >
            <span className="text-[0.66rem] uppercase tracking-wider text-[var(--color-text-faint)]">
              {p.label}
            </span>
            <span className="text-[0.92rem] font-light text-[var(--color-text)]">{p.value}</span>
          </div>
        ))}
      </div>
    </section>
  );
}
