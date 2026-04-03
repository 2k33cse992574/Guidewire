#!/usr/bin/env python3
"""
GigShield AI Risk Scoring Demo
Shows the new risk scoring layer and explainability features.
"""

import numpy as np
from models.premium_model import PremiumModel
from models.predictive_risk_model import PredictiveRiskModel
from models.fraud_detection import FraudDetector
from evaluate_models import generate_premium_dataset, generate_predictive_dataset, generate_fraud_dataset

def demo_risk_scoring():
    print("🚀 GigShield AI Risk Scoring Demo")
    print("=" * 50)

    # Train models
    print("\n📊 Training Models...")

    # Premium Model
    premium_model = PremiumModel()
    X_premium, y_premium = generate_premium_dataset(n_samples=100, seed=42)
    premium_model.fit(X_premium, y_premium)

    # Predictive Model
    predictive_model = PredictiveRiskModel(model_type="stacked")
    X_pred, y_pred = generate_predictive_dataset(n_samples=200, seed=42)
    predictive_model.fit(X_pred, y_pred)

    # Fraud Model
    fraud_model = FraudDetector()
    records_fraud, labels_fraud = generate_fraud_dataset(n_samples=200, seed=42)
    X_fraud = np.array([
        [
            rec["location_mismatch"], rec["movement_anomaly"], rec["activity_mismatch"],
            rec["claim_frequency"], rec["device_behavior_anomaly"], rec["policy_age"],
            rec["time_since_last_claim"], rec["claim_amount_ratio"], rec["channel_risk"]
        ]
        for rec in records_fraud
    ], dtype=float)
    fraud_model.fit(X_fraud, labels_fraud)

    print("✅ Models trained successfully")

    # Demo risk scoring
    print("\n🎯 Risk Scoring Examples")
    print("-" * 30)

    # Sample inputs
    premium_features = {
        "weather_risk": 0.8, "location_risk": 0.6, "work_pattern_risk": 0.7,
        "historical_risk": 0.5, "aqi_risk": 0.4, "area_risk": 0.3,
        "seasonality": 0.2, "volatility": 0.1, "claim_history": 0.4, "driver_score": 0.8
    }

    predictive_features = {
        "rain_intensity": 0.9, "temperature_change": 0.7, "aqi": 0.8,
        "historic_disruption_rate": 0.6, "zone_risk": 0.5, "trigger_count_last_24h": 0.4,
        "humidity": 0.3, "storm_trend": 0.8, "pressure_change": -0.2, "forecast_confidence": 0.1
    }

    fraud_claim = {
        "location_mismatch": True, "movement_anomaly": False, "activity_mismatch": True,
        "claim_frequency": 0.8, "device_behavior_anomaly": 0.6, "policy_age": 0.3,
        "time_since_last_claim": 0.1, "claim_amount_ratio": 0.7, "channel_risk": 0.5
    }

    # Premium Risk Score
    premium_risk = premium_model.risk_score(premium_features)
    weekly_income = 1000.0
    premium = premium_model.compute_weekly_premium(weekly_income, premium_risk)

    print("Premium Risk Score: {:.3f}".format(premium_risk))
    print("Weekly Premium for $1000 income: ${:.2f}".format(premium))
    print("Risk-adjusted premium: ${:.2f}".format(premium))

    # Predictive Risk Score
    predictive_risk = predictive_model.risk_score(predictive_features)
    print("Predictive Risk Score: {:.3f}".format(predictive_risk))

    # Fraud Decision
    fraud_decision = fraud_model.decision(fraud_claim)
    fraud_explanation = fraud_model.explain_claim(fraud_claim)
    print("Fraud Decision: {}".format(fraud_decision))
    print("Fraud Risk Score: {:.3f}".format(fraud_explanation["fraud_probability"]))
    print("Severity Score: {:.3f}".format(fraud_explanation["severity_score"]))

    # Explainability Demo
    print("\n🔍 Explainability Demo")
    print("-" * 25)

    pred_explanation = predictive_model.explain_prediction(predictive_features)
    print("Predictive Model Explanation:")
    if "stacked_importances" in pred_explanation:
        print("  Top features:", list(pred_explanation["stacked_importances"].keys())[:3])
    elif "feature_importances" in pred_explanation:
        top_features = sorted(pred_explanation["feature_importances"].items(), key=lambda x: x[1], reverse=True)[:3]
        print("  Top features:", [f"{k}: {v:.3f}" for k, v in top_features])

    print("\nFraud Model Explanation:")
    print("  Rule Score: {:.3f}".format(fraud_explanation["rule_score"]))
    print("  Anomaly Score: {:.3f}".format(fraud_explanation["anomaly_score"]))
    print("  Thresholds - Reject: {:.2f}, Soft Flag: {:.2f}".format(
        fraud_explanation["threshold_reject"], fraud_explanation["threshold_soft_flag"]))

    # Decision Ranking Demo
    print("\n📈 Decision Ranking Demo (Top 10% Risk → Reject)")
    print("-" * 45)

    # Generate sample claims and rank by risk
    sample_claims = []
    for i in range(20):
        claim = {
            "location_mismatch": np.random.random() > 0.8,
            "movement_anomaly": np.random.random() > 0.7,
            "activity_mismatch": np.random.random() > 0.6,
            "claim_frequency": np.random.random(),
            "device_behavior_anomaly": np.random.random(),
            "policy_age": np.random.random(),
            "time_since_last_claim": np.random.random(),
            "claim_amount_ratio": np.random.random(),
            "channel_risk": np.random.random()
        }
        risk = fraud_model.score_claim(claim)
        sample_claims.append((risk, claim))

    # Sort by risk (highest first)
    sample_claims.sort(key=lambda x: x[0], reverse=True)

    print("Top 10% highest risk claims would be REJECTED:")
    for i, (risk, claim) in enumerate(sample_claims[:2]):  # Top 10% of 20 = 2
        decision = fraud_model.decision(claim)
        print("  Claim {}: Risk {:.3f} → {}".format(i+1, risk, decision))

    print("\n✅ Demo Complete")
    print("This shows the shift from classification to risk-based ranking decisions.")

if __name__ == "__main__":
    demo_risk_scoring()