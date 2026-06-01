import type { ConditionCategory } from "@/lib/types";

interface IconProps {
  size?: number;
  className?: string;
}

const base = (size: number): React.SVGProps<SVGSVGElement> => ({
  width: size,
  height: size,
  viewBox: "0 0 24 24",
  fill: "none",
  stroke: "currentColor",
  strokeWidth: 1.6,
  strokeLinecap: "round" as const,
  strokeLinejoin: "round" as const,
});

export function SearchIcon({ size = 18, className }: IconProps): React.ReactElement {
  return (
    <svg {...base(size)} className={className} aria-hidden>
      <circle cx="11" cy="11" r="7" />
      <path d="m20 20-3.2-3.2" />
    </svg>
  );
}

export function LocationIcon({ size = 18, className }: IconProps): React.ReactElement {
  return (
    <svg {...base(size)} className={className} aria-hidden>
      <path d="M12 21s-6-5.2-6-10a6 6 0 0 1 12 0c0 4.8-6 10-6 10Z" />
      <circle cx="12" cy="11" r="2.2" />
    </svg>
  );
}

export function StarIcon({
  size = 18,
  className,
  filled = false,
}: IconProps & { filled?: boolean }): React.ReactElement {
  return (
    <svg {...base(size)} className={className} fill={filled ? "currentColor" : "none"} aria-hidden>
      <path d="M12 3.5l2.6 5.3 5.9.9-4.3 4.1 1 5.8L12 17.9 6.8 19.6l1-5.8L3.5 9.7l5.9-.9L12 3.5Z" />
    </svg>
  );
}

export function SunIcon({ size = 18, className }: IconProps): React.ReactElement {
  return (
    <svg {...base(size)} className={className} aria-hidden>
      <circle cx="12" cy="12" r="4" />
      <path d="M12 2v2M12 20v2M2 12h2M20 12h2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M19.1 4.9l-1.4 1.4M6.3 17.7l-1.4 1.4" />
    </svg>
  );
}

export function MoonIcon({ size = 18, className }: IconProps): React.ReactElement {
  return (
    <svg {...base(size)} className={className} aria-hidden>
      <path d="M20 14.5A8 8 0 1 1 9.5 4a6.5 6.5 0 0 0 10.5 10.5Z" />
    </svg>
  );
}

export function DropletIcon({ size = 18, className }: IconProps): React.ReactElement {
  return (
    <svg {...base(size)} className={className} aria-hidden>
      <path d="M12 3.5s5 5.4 5 9.2a5 5 0 0 1-10 0C7 8.9 12 3.5 12 3.5Z" />
    </svg>
  );
}

export function WindIcon({ size = 18, className }: IconProps): React.ReactElement {
  return (
    <svg {...base(size)} className={className} aria-hidden>
      <path d="M3 8h11a2.5 2.5 0 1 0-2.5-2.5M3 16h14a2.5 2.5 0 1 1-2.5 2.5M3 12h8" />
    </svg>
  );
}

export function ThermometerIcon({ size = 18, className }: IconProps): React.ReactElement {
  return (
    <svg {...base(size)} className={className} aria-hidden>
      <path d="M14 14.8V5a2 2 0 1 0-4 0v9.8a4 4 0 1 0 4 0Z" />
    </svg>
  );
}

export function TrashIcon({ size = 16, className }: IconProps): React.ReactElement {
  return (
    <svg {...base(size)} className={className} aria-hidden>
      <path d="M4 7h16M9 7V5a1 1 0 0 1 1-1h4a1 1 0 0 1 1 1v2M6 7l1 13h10l1-13" />
    </svg>
  );
}

export function ClockIcon({ size = 16, className }: IconProps): React.ReactElement {
  return (
    <svg {...base(size)} className={className} aria-hidden>
      <circle cx="12" cy="12" r="8.5" />
      <path d="M12 7.5V12l3 1.8" />
    </svg>
  );
}

export function ConditionGlyph({
  category,
  size = 18,
  className,
}: { category: ConditionCategory } & IconProps): React.ReactElement {
  const p = base(size);
  switch (category) {
    case "clear":
      return <SunIcon size={size} className={className} />;
    case "thunderstorm":
      return (
        <svg {...p} className={className} aria-hidden>
          <path d="M6 16a4 4 0 0 1 .5-8 5.5 5.5 0 0 1 10.6 1.3A3.5 3.5 0 0 1 17 16" />
          <path d="m12 13-2 3.5h3L11 20" />
        </svg>
      );
    case "snow":
      return (
        <svg {...p} className={className} aria-hidden>
          <path d="M6 15a4 4 0 0 1 .5-8 5.5 5.5 0 0 1 10.6 1.3A3.5 3.5 0 0 1 17 15" />
          <path d="M9 18.5h.01M12 20h.01M15 18.5h.01" />
        </svg>
      );
    case "rain":
    case "drizzle":
      return (
        <svg {...p} className={className} aria-hidden>
          <path d="M6 14a4 4 0 0 1 .5-8 5.5 5.5 0 0 1 10.6 1.3A3.5 3.5 0 0 1 17 14" />
          <path d="M9 17.5l-1 2M12 17.5l-1 2M15 17.5l-1 2" />
        </svg>
      );
    case "fog":
      return (
        <svg {...p} className={className} aria-hidden>
          <path d="M5 10a4 4 0 0 1 .5-8 5.5 5.5 0 0 1 10.6 1.3A3.5 3.5 0 0 1 16 10" />
          <path d="M4 14h16M6 18h13" />
        </svg>
      );
    case "cloudy":
    default:
      return (
        <svg {...p} className={className} aria-hidden>
          <path d="M7 18a4.5 4.5 0 0 1 .6-9 6 6 0 0 1 11.4 1.6A4 4 0 0 1 18 18Z" />
        </svg>
      );
  }
}
