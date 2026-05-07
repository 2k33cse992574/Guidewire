from typing import Dict, Optional


def validate_location_signals(signals: Dict[str, str], registered_city: str) -> bool:
    gps = signals.get("gps_location", "")
    network = signals.get("network_location", "")
    ip = signals.get("ip_location", "")

    if not gps or not network or not ip:
        return False

    gps_matches_network = gps == network
    ip_matches_city = registered_city.lower() in ip.lower()
    return gps_matches_network and ip_matches_city


def validate_movement(activity: Dict[str, float], speed_threshold: float = 2.0, stationary_minutes_threshold: int = 30) -> bool:
    average_speed = activity.get("average_speed_kmh", 0.0)
    stationary_minutes = activity.get("stationary_minutes", 0)
    if average_speed < speed_threshold and stationary_minutes >= stationary_minutes_threshold:
        return False
    return True


def validate_activity_logs(activity: Dict[str, int]) -> bool:
    deliveries = activity.get("deliveries_during_window", 0)
    active_sessions = activity.get("active_sessions_during_window", 0)
    return deliveries > 0 or active_sessions > 0


def validate_trigger(
    trigger_data: Dict[str, any],
    user_zone: str,
    area_risk: float,
    registered_city: str,
) -> Dict[str, any]:
    trigger_active = bool(trigger_data.get("trigger_active", False))
    if not trigger_active:
        return {
            "trigger_active": False,
            "impact_valid": False,
            "reason": "No active trigger detected",
        }

    in_zone = trigger_data.get("affected_zone") == user_zone
    location_valid = validate_location_signals(trigger_data.get("location_signals", {}), registered_city)
    movement_valid = validate_movement(trigger_data.get("movement", {}))
    activity_valid = validate_activity_logs(trigger_data.get("activity", {}))
    area_risk_valid = area_risk >= 0.2

    impact_valid = in_zone and location_valid and movement_valid and activity_valid and area_risk_valid
    reasons = []
    if not in_zone:
        reasons.append("User not in affected zone")
    if not location_valid:
        reasons.append("Location signal mismatch")
    if not movement_valid:
        reasons.append("Low movement during disruption window")
    if not activity_valid:
        reasons.append("No delivery activity during disruption window")
    if not area_risk_valid:
        reasons.append("Area risk is too low for this trigger")

    return {
        "trigger_active": True,
        "impact_valid": impact_valid,
        "in_zone": in_zone,
        "location_valid": location_valid,
        "movement_valid": movement_valid,
        "activity_valid": activity_valid,
        "area_risk_valid": area_risk_valid,
        "reasons": reasons,
    }
