"""
Business Impact Simulation for GigShield ML System

Simulates the real-world impact of ML-driven decisions:
- Fraud reduction percentage
- Manual review workload reduction
- Revenue impact from premium adjustments
- Overall system ROI
"""

from typing import Dict, List, Tuple
import numpy as np
from models.fraud_detection import FraudDetector
from models.predictive_risk_model import PredictiveRiskModel
from models.premium_model import PremiumModel


class BusinessSimulator:
    """Simulates business impact of ML decisions."""

    def __init__(self, fraud_model: FraudDetector, predictive_model: PredictiveRiskModel, premium_model: PremiumModel):
        self.fraud_model = fraud_model
        self.predictive_model = predictive_model
        self.premium_model = premium_model

    def simulate_fraud_impact(self, claims: List[Dict[str, float]], labels: List[str]) -> Dict[str, float]:
        """Simulate fraud detection impact."""
        decisions = [self.fraud_model.decision(claim) for claim in claims]
        
        # Calculate metrics
        total_claims = len(claims)
        rejected = decisions.count("reject")
        soft_flagged = decisions.count("soft_flag")
        approved = decisions.count("approve")
        
        # True fraud rates
        true_fraud = sum(1 for label in labels if label in ["reject", "soft_flag", "approve"] and label != "approve")
        fraud_rejected = sum(1 for d, l in zip(decisions, labels) if d == "reject" and l == "reject")
        fraud_soft = sum(1 for d, l in zip(decisions, labels) if d == "soft_flag" and l in ["reject", "soft_flag"])
        
        fraud_recall = fraud_rejected / true_fraud if true_fraud > 0 else 0
        soft_flag_recall = fraud_soft / true_fraud if true_fraud > 0 else 0
        
        # Business impact
        fraud_prevention_rate = (fraud_rejected + 0.5 * fraud_soft) / true_fraud if true_fraud > 0 else 0
        manual_review_load = (rejected + soft_flagged) / total_claims
        automation_rate = approved / total_claims
        
        return {
            "total_claims": total_claims,
            "rejected": rejected,
            "soft_flagged": soft_flagged,
            "approved": approved,
            "fraud_recall": fraud_recall,
            "soft_flag_recall": soft_flag_recall,
            "fraud_prevention_rate": fraud_prevention_rate,
            "manual_review_load": manual_review_load,
            "automation_rate": automation_rate,
        }

    def simulate_predictive_impact(self, scenarios: List[Dict[str, float]], actual_disruptions: List[int]) -> Dict[str, float]:
        """Simulate predictive model impact on response planning."""
        predictions = [self.predictive_model.is_disruption_expected(scenario) for scenario in scenarios]
        
        true_positives = sum(1 for p, a in zip(predictions, actual_disruptions) if p and a)
        false_positives = sum(1 for p, a in zip(predictions, actual_disruptions) if p and not a)
        true_negatives = sum(1 for p, a in zip(predictions, actual_disruptions) if not p and not a)
        false_negatives = sum(1 for p, a in zip(predictions, actual_disruptions) if not p and a)
        
        precision = true_positives / (true_positives + false_positives) if (true_positives + false_positives) > 0 else 0
        recall = true_positives / (true_positives + false_negatives) if (true_positives + false_negatives) > 0 else 0
        
        # Business impact: early response saves costs
        early_response_savings = true_positives * 0.3  # Assume 30% cost savings per correct prediction
        false_alarm_costs = false_positives * 0.1  # Assume 10% cost per false alarm
        missed_opportunity_costs = false_negatives * 0.5  # Assume 50% cost per missed disruption
        
        net_savings = early_response_savings - false_alarm_costs - missed_opportunity_costs
        
        return {
            "precision": precision,
            "recall": recall,
            "true_positives": true_positives,
            "false_positives": false_positives,
            "net_savings": net_savings,
        }

    def simulate_premium_impact(self, policies: List[Dict[str, float]], weekly_incomes: List[float]) -> Dict[str, float]:
        """Simulate premium model impact on revenue."""
        premiums = []
        for policy, income in zip(policies, weekly_incomes):
            risk = self.premium_model.risk_score(policy)
            premium = self.premium_model.compute_weekly_premium(income, risk)
            premiums.append(premium)
        
        total_premium = sum(premiums)
        avg_premium = np.mean(premiums)
        premium_variability = np.std(premiums) / avg_premium if avg_premium > 0 else 0
        
        # Business impact: risk-adjusted pricing
        base_premium_rate = 0.025  # Assume 2.5% of income without risk adjustment
        base_total = sum(income * base_premium_rate for income in weekly_incomes)
        risk_adjusted_total = total_premium
        
        revenue_impact = risk_adjusted_total - base_total
        
        return {
            "total_premium_revenue": total_premium,
            "avg_weekly_premium": avg_premium,
            "premium_variability": premium_variability,
            "revenue_vs_base": revenue_impact,
            "revenue_growth_pct": (revenue_impact / base_total) * 100 if base_total > 0 else 0,
        }

    def overall_system_roi(self, fraud_impact: Dict, predictive_impact: Dict, premium_impact: Dict) -> Dict[str, float]:
        """Calculate overall system ROI."""
        # Simplified ROI calculation
        fraud_savings = fraud_impact["fraud_prevention_rate"] * 1000  # Assume $1000 per prevented fraud
        predictive_savings = predictive_impact["net_savings"] * 500  # Scale savings
        premium_revenue = premium_impact["revenue_vs_base"]
        
        total_benefits = fraud_savings + predictive_savings + premium_revenue
        total_costs = 50  # Assume $50/month for ML system
        
        roi = (total_benefits - total_costs) / total_costs if total_costs > 0 else 0
        
        return {
            "fraud_savings": fraud_savings,
            "predictive_savings": predictive_savings,
            "premium_revenue": premium_revenue,
            "total_benefits": total_benefits,
            "total_costs": total_costs,
            "roi": roi,
            "roi_pct": roi * 100,
        }


def run_business_simulation():
    """Demo business simulation."""
    # Initialize models
    fraud_model = FraudDetector()
    predictive_model = PredictiveRiskModel(model_type="stacked")
    premium_model = PremiumModel(model_type="xgboost")
    
    # Train models with sample data
    X_fraud = fraud_model.sample_training_data()
    labels = ["approve", "approve", "soft_flag", "reject", "reject", "reject"]
    fraud_model.fit(X_fraud, labels)
    
    X_pred, y_pred = predictive_model.sample_training_data()
    predictive_model.fit(X_pred, y_pred)
    
    X_prem, y_prem = premium_model.sample_training_data()
    premium_model.fit(X_prem, y_prem)
    
    simulator = BusinessSimulator(fraud_model, predictive_model, premium_model)
    
    # Simulate fraud impact
    test_claims = [
        {"location_mismatch": False, "movement_anomaly": False, "activity_mismatch": False, "claim_frequency": 0.1, "device_behavior_anomaly": 0.0, "policy_age": 0.5, "time_since_last_claim": 0.8, "claim_amount_ratio": 0.1, "channel_risk": 0.1},
        {"location_mismatch": True, "movement_anomaly": True, "activity_mismatch": True, "claim_frequency": 0.8, "device_behavior_anomaly": 0.9, "policy_age": 0.1, "time_since_last_claim": 0.1, "claim_amount_ratio": 0.8, "channel_risk": 0.9},
    ]
    test_labels = ["approve", "reject"]
    fraud_impact = simulator.simulate_fraud_impact(test_claims, test_labels)
    
    # Simulate predictive impact
    test_scenarios = [{"rain_intensity": 0.8, "temperature_change": 0.3, "aqi": 0.7, "historic_disruption_rate": 0.6, "zone_risk": 0.8, "trigger_count_last_24h": 0.5, "humidity": 0.7, "storm_trend": 0.6, "pressure_change": 0.4, "forecast_confidence": 0.3}]
    actual_disruptions = [1]
    predictive_impact = simulator.simulate_predictive_impact(test_scenarios, actual_disruptions)
    
    # Simulate premium impact
    test_policies = [{"weather_risk": 0.7, "location_risk": 0.8, "work_pattern_risk": 0.5, "historical_risk": 0.6, "aqi_risk": 0.4, "area_risk": 0.7, "seasonality": 0.3, "volatility": 0.15}]
    weekly_incomes = [1000]
    premium_impact = simulator.simulate_premium_impact(test_policies, weekly_incomes)
    
    overall_roi = simulator.overall_system_roi(fraud_impact, predictive_impact, premium_impact)
    
    print("=== Business Impact Simulation ===")
    print("(Synthetic, upper-bound numbers; not production-cast predictions)")
    print(f"Fraud Prevention Rate (simulated): {fraud_impact['fraud_prevention_rate']:.1%}")
    print(f"Manual Review Load: {fraud_impact['manual_review_load']:.1%}")
    print(f"Predictive Net Savings (simulated): ${predictive_impact['net_savings']:.2f}")
    print(f"Premium Revenue Impact (simulated): ${premium_impact['revenue_vs_base']:.2f}")
    print(f"Overall ROI (simulated): {overall_roi['roi_pct']:.1f}%")


if __name__ == "__main__":
    run_business_simulation()