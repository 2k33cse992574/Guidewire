from typing import Dict

from models.fraud_detection import FraudDetector
from models.trigger_validation import validate_trigger
from services.trigger_engine import evaluate_triggers, select_primary_trigger
from services.validation import has_duplicate_claim, is_policy_active, record_claim


def calculate_payout(trigger_result: Dict[str, any], user_profile: Dict[str, any]) -> float:
    daily_income = float(trigger_result.get("daily_income", 0.0) or user_profile.get("daily_income", 0.0))
    hourly_income = float(user_profile.get("hourly_income", 0.0))
    payout_rate = float(trigger_result.get("payout_rate", 0.0))

    if trigger_result["trigger_name"] in {"flood", "curfew"}:
        return max(0.0, daily_income * payout_rate)
    return max(0.0, float(trigger_result.get("affected_hours", 0.0)) * hourly_income * payout_rate)


def simulate_payment(amount: float, user_id: str, payment_method: str = "UPI") -> Dict[str, str]:
    return {
        "status": "success",
        "payment_method": payment_method,
        "amount": f"{amount:.2f}",
        "transaction_id": f"TX-{user_id}-{int(amount * 100)}",
    }


def process_claim(
    trigger_data: Dict[str, any],
    user_profile: Dict[str, any],
    area_risk: float,
    fraud_detector: FraudDetector,
    payment_method: str = "UPI",
    claim_day: str = "today",
) -> Dict[str, any]:
    if not is_policy_active(user_profile):
        return {
            "claim_status": "rejected",
            "reason": "Policy inactive",
        }

    active_triggers = evaluate_triggers(trigger_data, user_profile.get("zone", ""))
    if not active_triggers:
        return {
            "claim_status": "rejected",
            "reason": "No active parametric trigger",
        }

    primary_trigger = select_primary_trigger(active_triggers)
    if not primary_trigger:
        return {
            "claim_status": "rejected",
            "reason": "Unable to select primary trigger",
        }

    if has_duplicate_claim(user_profile, primary_trigger["trigger_name"], claim_day):
        return {
            "claim_status": "rejected",
            "reason": "Duplicate claim detected",
            "trigger_name": primary_trigger["trigger_name"],
        }

    validation_payload = dict(trigger_data)
    validation_payload["trigger_active"] = True
    validation_payload["affected_zone"] = primary_trigger.get("affected_zone", trigger_data.get("affected_zone", ""))

    validation_result = validate_trigger(
        trigger_data=validation_payload,
        user_zone=user_profile.get("zone", ""),
        area_risk=area_risk,
        registered_city=user_profile.get("registered_city", ""),
    )

    if not validation_result["impact_valid"]:
        return {
            "claim_status": "rejected",
            "reason": "Validation failed",
            "validation": validation_result,
        }

    claim_features = {
        "location_mismatch": 0.0 if validation_result["location_valid"] else 1.0,
        "movement_anomaly": 0.0 if validation_result["movement_valid"] else 1.0,
        "activity_mismatch": 0.0 if validation_result["activity_valid"] else 1.0,
        "claim_frequency": float(user_profile.get("claim_frequency", 0.0)),
        "device_behavior_anomaly": float(user_profile.get("device_behavior_anomaly", 0.0)),
    }

    fraud_score = fraud_detector.score_claim(claim_features)
    decision = fraud_detector.decision(fraud_score)

    if decision == "reject":
        record_claim(user_profile, {"trigger_name": primary_trigger["trigger_name"], "claim_status": "rejected"}, claim_day)
        return {
            "claim_status": "rejected",
            "reason": "Fraud score too high",
            "fraud_score": fraud_score,
            "decision": decision,
            "validation": validation_result,
            "trigger_name": primary_trigger["trigger_name"],
        }

    payout_amount = calculate_payout(primary_trigger, user_profile)
    payment_result = simulate_payment(payout_amount, user_profile.get("user_id", "unknown"), payment_method)

    claim_result = {
        "claim_status": "approved" if decision == "approve" else "soft_flagged",
        "fraud_score": fraud_score,
        "decision": decision,
        "payout_amount": payout_amount,
        "payment_result": payment_result,
        "validation": validation_result,
        "trigger_name": primary_trigger["trigger_name"],
        "trigger_details": primary_trigger,
    }
    record_claim(user_profile, claim_result, claim_day)
    return claim_result
