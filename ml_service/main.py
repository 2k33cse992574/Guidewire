import pprint

from data.simulated_data import sample_scenario_events, sample_user_profile
from models.fraud_detection import FraudDetector
from models.feature_engineer import (
    build_premium_features,
    compute_hourly_income,
    compute_weekly_income,
)
from models.predictive_risk_model import PredictiveRiskModel
from models.premium_model import PremiumModel
from services.continuous_learning import ContinuousLearningLoop
from services.payout_workflow import process_claim


def run_demo() -> None:
    user_profile = sample_user_profile()
    scenarios = sample_scenario_events()
    user_profile["weekly_income"] = compute_weekly_income(user_profile["daily_income"], user_profile["active_days_per_week"])
    user_profile["hourly_income"] = compute_hourly_income(user_profile["weekly_income"], user_profile["total_working_hours"])

    premium_model = PremiumModel(model_type="linear")
    predictive_model = PredictiveRiskModel()
    fraud_detector = FraudDetector()
    learning_loop = ContinuousLearningLoop()

    X_risk, y_risk = premium_model.sample_training_data()
    premium_model.fit(X_risk, y_risk)

    X_predict, y_predict = predictive_model.sample_training_data()
    predictive_model.fit(X_predict, y_predict)

    fraud_X = FraudDetector.sample_training_data()
    fraud_detector.fit(fraud_X)

    results = []
    for scenario in scenarios:
        features = build_premium_features({
            "weather_risk": scenario.get("weather_risk", 0.0),
            "location_risk": scenario.get("location_risk", 0.0),
            "work_pattern_risk": scenario.get("work_pattern_risk", 0.0),
            "historical_risk": scenario.get("historical_risk", 0.0),
            "aqi_risk": scenario.get("aqi_risk", 0.0),
            "area_risk": scenario.get("area_risk", 0.0),
        })
        risk_score = premium_model.predict_risk(features)
        premium = premium_model.compute_weekly_premium(user_profile["weekly_income"], risk_score)

        probability = predictive_model.predict_probability({
            "rain_intensity": scenario.get("rain_intensity", 0.0),
            "temperature_change": scenario.get("temperature_change", 0.0),
            "aqi": scenario.get("aqi", 0.0),
            "historic_disruption_rate": scenario.get("historic_disruption_rate", 0.0),
            "zone_risk": scenario.get("zone_risk", 0.0),
            "trigger_count_last_24h": scenario.get("trigger_count_last_24h", 0.0),
        })

        claim_result = process_claim(
            trigger_data=scenario,
            user_profile=user_profile,
            area_risk=features["area_risk"],
            fraud_detector=fraud_detector,
            claim_day=scenario.get("event_date", "today"),
        )

        learning_loop.record_trigger(scenario)
        learning_loop.record_claim_outcome(claim_result)
        if claim_result.get("fraud_score", 0.0) > 0.7:
            learning_loop.record_fraud_pattern({
                "trigger_name": claim_result.get("trigger_name"),
                "fraud_score": claim_result.get("fraud_score"),
            })

        results.append({
            "scenario": scenario["scenario_name"],
            "risk_score": round(risk_score, 3),
            "weekly_premium": round(premium, 2),
            "predictive_probability": round(probability, 3),
            "claim_result": claim_result,
        })

    print("=== GigShield README-Aligned Demo ===")
    pprint.pprint({
        "user_profile": user_profile,
        "scenario_results": results,
        "learning_summary": learning_loop.summarize(),
    })


if __name__ == "__main__":
    run_demo()
