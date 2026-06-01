/** TypeScript mirrors of the backend's normalized API contract. */

export type Units = "metric" | "imperial";

export type ConditionCategory =
  | "clear"
  | "cloudy"
  | "fog"
  | "drizzle"
  | "rain"
  | "snow"
  | "thunderstorm";

export interface ResolvedLocation {
  name: string;
  admin1: string | null;
  country: string | null;
  country_code: string | null;
  latitude: number;
  longitude: number;
  timezone: string | null;
}

export interface CurrentConditions {
  time: string;
  temperature: number | null;
  apparent_temperature: number | null;
  relative_humidity: number | null;
  is_day: boolean | null;
  precipitation: number | null;
  weather_code: number | null;
  condition_category: ConditionCategory;
  wind_speed: number | null;
  wind_direction: number | null;
}

export interface HourlyPoint {
  time: string;
  temperature: number | null;
  precipitation_probability: number | null;
  weather_code: number | null;
  condition_category: ConditionCategory;
}

export interface DailyPoint {
  date: string;
  weather_code: number | null;
  condition_category: ConditionCategory;
  temperature_max: number | null;
  temperature_min: number | null;
  precipitation_sum: number | null;
  sunrise: string | null;
  sunset: string | null;
}

export interface AirQualityPoint {
  time: string;
  us_aqi: number | null;
}

export interface AirQuality {
  time: string | null;
  us_aqi: number | null;
  pm10: number | null;
  pm2_5: number | null;
  carbon_monoxide: number | null;
  nitrogen_dioxide: number | null;
  ozone: number | null;
  hourly: AirQualityPoint[];
}

export interface UnitLabels {
  temperature: string;
  wind_speed: string;
  precipitation: string;
}

export interface WeatherResponse {
  location: ResolvedLocation;
  units: Units;
  unit_labels: UnitLabels;
  condition_category: ConditionCategory;
  current: CurrentConditions;
  hourly: HourlyPoint[];
  daily: DailyPoint[];
  air_quality: AirQuality | null;
  cache: boolean;
  fetched_at: string;
}

export interface Favorite {
  id: string;
  query: string;
  location: ResolvedLocation;
  created_at: string;
}

export interface FavoriteCreate {
  query: string;
  location: ResolvedLocation;
}

export interface HistoryItem {
  query: string;
  location: ResolvedLocation;
  units: Units;
  searched_at: string;
}

export type DependencyStatusValue = "ok" | "degraded" | "down";

export interface DependencyHealth {
  status: DependencyStatusValue;
  detail: string | null;
}

export interface HealthResponse {
  status: DependencyStatusValue;
  redis: DependencyHealth;
  mongo: DependencyHealth;
  upstream: DependencyHealth;
  breakers: Record<string, string>;
}

export interface ApiErrorBody {
  error: { code: string; message: string };
}
