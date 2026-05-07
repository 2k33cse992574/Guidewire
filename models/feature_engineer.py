from typing import Dict


def compute_weekly_income(avg_daily_income: float, active_days_per_week: int) -> float:
    return round(max(0.0, avg_daily_income) * max(0, active_days_per_week), 2)


def compute_hourly_income(weekly_income: float, total_working_hours: float) -> float:
    return round(weekly_income / max(1.0, total_working_hours), 2)


def build_premium_features(raw_data: Dict[str, float]) -> Dict[str, float]:
    return {
        "weather_risk": float(raw_data.get("weather_risk", 0.0)),
        "location_risk": float(raw_data.get("location_risk", 0.0)),
        "work_pattern_risk": float(raw_data.get("work_pattern_risk", 0.0)),
        "historical_risk": float(raw_data.get("historical_risk", 0.0)),
        "aqi_risk": float(raw_data.get("aqi_risk", 0.0)),
        "area_risk": float(raw_data.get("area_risk", 0.0)),
    }


def weather_risk_from_forecast(rainfall_mm: float, temperature_c: float, heat_index: float) -> float:
    score = 0.0
    if rainfall_mm >= 50:
        score += 0.35
    if temperature_c >= 42 or heat_index >= 45:
        score += 0.35
    return min(1.0, score + 0.15)


def pollution_risk(aqi: float) -> float:
    return min(1.0, max(0.0, aqi / 500.0))


def area_risk_from_zone(score: float) -> float:
    return min(1.0, max(0.0, score))


def work_pattern_risk(peak_hours: float, total_hours: float) -> float:
    if total_hours <= 0:
        return 0.0
    return min(1.0, peak_hours / total_hours)
