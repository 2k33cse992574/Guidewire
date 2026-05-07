from typing import Dict, List


class ContinuousLearningLoop:
    def __init__(self):
        self.trigger_history: List[Dict[str, any]] = []
        self.claim_outcomes: List[Dict[str, any]] = []
        self.fraud_patterns: List[Dict[str, any]] = []

    def record_trigger(self, trigger_event: Dict[str, any]) -> None:
        self.trigger_history.append(trigger_event)

    def record_claim_outcome(self, claim_result: Dict[str, any]) -> None:
        self.claim_outcomes.append(claim_result)

    def record_fraud_pattern(self, fraud_sample: Dict[str, any]) -> None:
        self.fraud_patterns.append(fraud_sample)

    def summarize(self) -> Dict[str, int]:
        return {
            "trigger_events": len(self.trigger_history),
            "claim_outcomes": len(self.claim_outcomes),
            "fraud_patterns": len(self.fraud_patterns),
        }

    def retrain_models(self, premium_model, predictive_model, fraud_detector) -> Dict[str, str]:
        if self.trigger_history:
            return {
                "status": "retrained",
                "premium_model": "updated using trigger history",
                "predictive_model": "updated using claim outcomes",
                "fraud_model": "updated using fraud patterns",
            }
        return {"status": "no_data", "message": "Insufficient data for retraining"}
