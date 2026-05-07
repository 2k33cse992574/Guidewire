from typing import Dict, List, Optional


TRIGGER_NAMES = ["rain", "heat", "aqi", "flood", "curfew"]


def check_rain_trigger(external: Dict[str, float], user_zone: str) -> Dict[str, any]:
    rainfall_3h = float(external.get("rainfall_3h_mm", 0.0))
    rainfall_rate = float(external.get("rainfall_rate_mm_h", 0.0))
    visibility_km = float(external.get("visibility_km", 99.0))
    affected_zone = external.get("affected_zone", "")
    active = (rainfall_3h >= 50 or rainfall_rate >= 20) and visibility_km < 1.0 and affected_zone == user_zone
    return {
        "trigger_name": "rain",
        "trigger_active": active,
        "affected_zone": affected_zone,
        "payout_rate": 0.7,
        "affected_hours": float(external.get("affected_hours", 4.0)) if active else 0.0,
        "daily_income": float(external.get("daily_income", 0.0)),
    }


def check_heat_trigger(external: Dict[str, float], user_zone: str) -> Dict[str, any]:
    temperature = float(external.get("temperature_c", 0.0))
    heat_index = float(external.get("heat_index", 0.0))
    duration_hours = float(external.get("duration_hours", 0.0))
    affected_zone = external.get("affected_zone", "")
    active = temperature >= 42 and heat_index >= 45 and duration_hours >= 2 and affected_zone == user_zone
    return {
        "trigger_name": "heat",
        "trigger_active": active,
        "affected_zone": affected_zone,
        "payout_rate": 0.5,
        "affected_hours": float(external.get("inactive_hours", 2.0)) if active else 0.0,
        "daily_income": float(external.get("daily_income", 0.0)),
    }


def check_aqi_trigger(external: Dict[str, float], user_zone: str) -> Dict[str, any]:
    aqi = float(external.get("aqi", 0.0))
    duration_hours = float(external.get("duration_hours", 0.0))
    affected_zone = external.get("affected_zone", "")
    active = aqi >= 300 and duration_hours >= 4 and affected_zone == user_zone
    return {
        "trigger_name": "aqi",
        "trigger_active": active,
        "affected_zone": affected_zone,
        "payout_rate": 0.4,
        "affected_hours": float(external.get("affected_hours", 4.0)) if active else 0.0,
        "daily_income": float(external.get("daily_income", 0.0)),
    }


def check_flood_trigger(external: Dict[str, float], user_zone: str) -> Dict[str, any]:
    rainfall_day = float(external.get("rainfall_day_mm", 0.0))
    area_risk_score = float(external.get("area_risk_score", 0.0))
    flood_probability = float(external.get("flood_probability", 0.0))
    affected_zone = external.get("affected_zone", "")
    active = ((rainfall_day > 100 and area_risk_score > 0.7) or flood_probability > 0.7) and affected_zone == user_zone
    return {
        "trigger_name": "flood",
        "trigger_active": active,
        "affected_zone": affected_zone,
        "payout_rate": 0.8,
        "affected_hours": 0.0,
        "daily_income": float(external.get("daily_income", 0.0)),
    }


def check_curfew_trigger(external: Dict[str, str], user_zone: str) -> Dict[str, any]:
    zone_status = external.get("zone_status", "").lower()
    affected_zone = external.get("affected_zone", "")
    active = zone_status in {"restricted", "curfew"} and affected_zone == user_zone
    return {
        "trigger_name": "curfew",
        "trigger_active": active,
        "affected_zone": affected_zone,
        "payout_rate": 0.9,
        "affected_hours": 0.0,
        "daily_income": float(external.get("daily_income", 0.0)),
    }


def evaluate_triggers(external: Dict[str, any], user_zone: str) -> List[Dict[str, any]]:
    candidates = []
    candidates.append(check_rain_trigger(external, user_zone))
    candidates.append(check_heat_trigger(external, user_zone))
    candidates.append(check_aqi_trigger(external, user_zone))
    candidates.append(check_flood_trigger(external, user_zone))
    candidates.append(check_curfew_trigger(external, user_zone))
    return [trigger for trigger in candidates if trigger["trigger_active"]]


def select_primary_trigger(active_triggers: List[Dict[str, any]]) -> Optional[Dict[str, any]]:
    if not active_triggers:
        return None
    # Prioritize highest impact trigger.
    priority = {"curfew": 5, "flood": 4, "rain": 3, "heat": 2, "aqi": 1}
    return max(active_triggers, key=lambda t: priority.get(t["trigger_name"], 0))
