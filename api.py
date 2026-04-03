import os
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import uvicorn

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

# Initialize FastAPI
app = FastAPI(title="DeliveryProtect API")

# Setup Global Models (similar to main.py demo script)
user_profile = sample_user_profile()
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

global_claims = {
    "rain": 0,
    "traffic": 0,
    "outage": 0
}
payouts = {
    "rain": 1000,
    "traffic": 800,
    "outage": 1200
}

class TriggerRequest(BaseModel):
    type: str

class MetricsRequest(BaseModel):
    plan: dict
    user: dict

@app.post("/api/metrics")
async def get_metrics(req: MetricsRequest):
    # Compute dynamic risk
    # Map frontend claim counts loosely to scenario risks
    weather_r = min(1.0, 0.2 + global_claims["rain"] * 0.3)
    traffic_r = min(1.0, 0.1 + global_claims["traffic"] * 0.2)
    outage_r = min(1.0, 0.05 + global_claims["outage"] * 0.4)
    
    features = build_premium_features({
        "weather_risk": weather_r,
        "location_risk": traffic_r,
        "work_pattern_risk": outage_r,
        "historical_risk": 0.1,
        "aqi_risk": 0.2,
        "area_risk": 0.1,
    })
    
    risk_score = premium_model.predict_risk(features)
    # The models give a probability (e.g. 0.0-1.0), let's scale to 0-100 for the UI
    ui_risk_score = min(100, max(0, int(risk_score * 100)))

    # Risk level string
    if ui_risk_score >= 75:
        risk_level = "High"
    elif ui_risk_score >= 50:
        risk_level = "Medium"
    else:
        risk_level = "Low"

    total_claims = global_claims["rain"] + global_claims["traffic"] + global_claims["outage"]
    total_saved = (global_claims["rain"] * payouts["rain"] + 
                   global_claims["traffic"] * payouts["traffic"] + 
                   global_claims["outage"] * payouts["outage"])

    coverage_limit = max(1, req.plan.get("coverage", 2500) * 2) # Example scaling from frontend
    coverage_used = min(100, int((total_saved / coverage_limit) * 100))

    return {
        "claims": global_claims,
        "totalClaims": total_claims,
        "totalSaved": total_saved,
        "riskScore": ui_risk_score,
        "coverageUsed": coverage_used,
        "riskLevel": risk_level,
    }

@app.post("/api/trigger")
async def trigger_claim(req: TriggerRequest):
    ctype = req.type
    if ctype in global_claims:
        global_claims[ctype] += 1
        
    # Map to scenario
    scenario = {
        "scenario_name": f"{ctype.capitalize()} Disruption",
        "weather_risk": 0.8 if ctype == "rain" else 0.1,
        "location_risk": 0.8 if ctype == "traffic" else 0.1,
        "work_pattern_risk": 0.8 if ctype == "outage" else 0.1,
        "historical_risk": 0.1,
        "aqi_risk": 0.1,
        "area_risk": 0.1,
        "event_date": "today"
    }

    # Process workflow
    features = build_premium_features(scenario)
    claim_result = process_claim(
        trigger_data=scenario,
        user_profile=user_profile,
        area_risk=features["area_risk"],
        fraud_detector=fraud_detector,
        claim_day=scenario.get("event_date", "today"),
    )

    learning_loop.record_trigger(scenario)
    learning_loop.record_claim_outcome(claim_result)
    
    return {"status": "success", "claim_result": claim_result, "payout": payouts.get(ctype, 0)}

@app.post("/api/reset")
async def reset_state():
    global global_claims
    global_claims = {"rain": 0, "traffic": 0, "outage": 0}
    return {"status": "reset"}

front_path = os.path.join(os.path.dirname(__file__), "frontend", "Delivery-Partner-Insurance-Plateform")
app.mount("/", StaticFiles(directory=front_path, html=True), name="static")

if __name__ == "__main__":
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)
