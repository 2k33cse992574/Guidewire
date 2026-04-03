from typing import Dict, List


def is_policy_active(user_profile: Dict[str, any]) -> bool:
    return str(user_profile.get("policy_status", "inactive")).lower() == "active"


def has_duplicate_claim(user_profile: Dict[str, any], trigger_name: str, claim_day: str) -> bool:
    claims: List[Dict[str, any]] = user_profile.get("recent_claims", [])
    return any(
        claim.get("trigger_name") == trigger_name and claim.get("claim_day") == claim_day
        for claim in claims
    )


def record_claim(user_profile: Dict[str, any], claim_result: Dict[str, any], claim_day: str) -> None:
    claims: List[Dict[str, any]] = user_profile.setdefault("recent_claims", [])
    claims.append({
        "trigger_name": claim_result.get("trigger_name", "unknown"),
        "claim_day": claim_day,
        "status": claim_result.get("claim_status", "unknown"),
    })
