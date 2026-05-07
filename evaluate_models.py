import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    classification_report,
    confusion_matrix,
    f1_score,
    mean_absolute_error,
    mean_squared_error,
    precision_score,
    recall_score,
    roc_auc_score,
    r2_score,
)
from sklearn.model_selection import train_test_split

from models.fraud_detection import FraudDetector
from models.premium_model import PremiumModel
from models.predictive_risk_model import DEFAULT_PREDICTIVE_FEATURES, PredictiveRiskModel


def generate_premium_dataset(n_samples: int = 600, seed: int = 42):
    rng = np.random.default_rng(seed)
    weather_risk = np.clip(rng.normal(0.35, 0.22, n_samples), 0.0, 1.0)
    location_risk = np.clip(rng.beta(2.0, 3.5, n_samples), 0.0, 1.0)
    work_pattern_risk = np.clip(rng.normal(0.45, 0.18, n_samples), 0.0, 1.0)
    historical_risk = np.clip(rng.beta(2.0, 4.0, n_samples), 0.0, 1.0)
    aqi_risk = np.clip(rng.normal(0.3, 0.25, n_samples), 0.0, 1.0)
    area_risk = np.clip(rng.normal(0.4, 0.3, n_samples), 0.0, 1.0)

    seasonality = np.clip(
        np.sin(np.linspace(0, 2 * np.pi, n_samples)) * 0.25 + rng.normal(0.0, 0.08, n_samples),
        0.0,
        1.0,
    )
    volatility = np.clip(np.abs(rng.normal(0.18, 0.10, n_samples)) + 0.05, 0.0, 1.0)
    claim_history = np.clip(rng.beta(1.5, 2.0, n_samples), 0.0, 1.0)
    driver_score = np.clip(rng.normal(0.7, 0.15, n_samples), 0.0, 1.0)
    interaction = np.clip(weather_risk * historical_risk + area_risk * aqi_risk, 0.0, 1.0)

    X = np.vstack(
        [
            weather_risk,
            location_risk,
            work_pattern_risk,
            historical_risk,
            aqi_risk,
            area_risk,
            seasonality,
            volatility,
            claim_history,
            driver_score,
        ]
    ).T

    y = (
        0.20 * weather_risk
        + 0.17 * location_risk
        + 0.14 * work_pattern_risk
        + 0.13 * historical_risk
        + 0.09 * aqi_risk
        + 0.08 * area_risk
        + 0.12 * interaction
        + 0.10 * seasonality
        + 0.05 * volatility
        + rng.normal(0.0, 0.05 + 0.01 * np.abs(interaction - 0.5), n_samples)
    )
    y = np.clip(y, 0.0, 1.0)
    return X, y


def generate_predictive_dataset(n_samples: int = 800, seed: int = 42):
    rng = np.random.default_rng(seed)
    regimes = rng.choice([0, 1, 2], size=n_samples, p=[0.40, 0.35, 0.25])

    rain_intensity = np.zeros(n_samples)
    temperature_change = np.zeros(n_samples)
    aqi = np.zeros(n_samples)
    historic_disruption_rate = np.zeros(n_samples)
    zone_risk = np.zeros(n_samples)
    trigger_count_last_24h = np.zeros(n_samples)
    humidity = np.zeros(n_samples)
    storm_trend = np.zeros(n_samples)
    pressure_change = np.zeros(n_samples)
    forecast_confidence = np.zeros(n_samples)

    storm_mask = regimes == 0
    dry_mask = regimes == 1
    mixed_mask = regimes == 2

    rain_intensity[storm_mask] = np.clip(rng.normal(0.65, 0.16, storm_mask.sum()), 0.4, 1.0)
    temperature_change[storm_mask] = np.clip(rng.normal(0.28, 0.12, storm_mask.sum()), 0.1, 0.6)
    aqi[storm_mask] = np.clip(rng.normal(0.55, 0.18, storm_mask.sum()), 0.2, 1.0)
    historic_disruption_rate[storm_mask] = np.clip(rng.normal(0.38, 0.18, storm_mask.sum()), 0.1, 1.0)
    zone_risk[storm_mask] = np.clip(rng.normal(0.58, 0.20, storm_mask.sum()), 0.2, 1.0)
    trigger_count_last_24h[storm_mask] = np.clip(rng.poisson(2.0, storm_mask.sum()) / 5.0, 0.0, 1.0)
    humidity[storm_mask] = np.clip(rng.normal(0.75, 0.15, storm_mask.sum()), 0.35, 1.0)
    storm_trend[storm_mask] = np.clip(rng.normal(0.72, 0.16, storm_mask.sum()), 0.2, 1.0)
    pressure_change[storm_mask] = np.clip(rng.normal(0.22, 0.12, storm_mask.sum()), 0.05, 0.72)
    forecast_confidence[storm_mask] = np.clip(rng.normal(0.30, 0.12, storm_mask.sum()), 0.05, 0.65)

    rain_intensity[dry_mask] = np.clip(rng.normal(0.12, 0.08, dry_mask.sum()), 0.0, 0.35)
    temperature_change[dry_mask] = np.clip(rng.normal(0.18, 0.10, dry_mask.sum()), 0.0, 0.4)
    aqi[dry_mask] = np.clip(rng.normal(0.22, 0.10, dry_mask.sum()), 0.0, 0.45)
    historic_disruption_rate[dry_mask] = np.clip(rng.normal(0.20, 0.12, dry_mask.sum()), 0.0, 0.45)
    zone_risk[dry_mask] = np.clip(rng.normal(0.28, 0.14, dry_mask.sum()), 0.0, 0.5)
    trigger_count_last_24h[dry_mask] = np.clip(rng.poisson(0.8, dry_mask.sum()) / 5.0, 0.0, 1.0)
    humidity[dry_mask] = np.clip(rng.normal(0.28, 0.12, dry_mask.sum()), 0.0, 0.45)
    storm_trend[dry_mask] = np.clip(rng.normal(0.12, 0.08, dry_mask.sum()), 0.0, 0.3)
    pressure_change[dry_mask] = np.clip(rng.normal(0.06, 0.05, dry_mask.sum()), 0.0, 0.20)
    forecast_confidence[dry_mask] = np.clip(rng.normal(0.70, 0.10, dry_mask.sum()), 0.40, 1.0)

    rain_intensity[mixed_mask] = np.clip(rng.normal(0.42, 0.20, mixed_mask.sum()), 0.0, 1.0)
    temperature_change[mixed_mask] = np.clip(rng.normal(0.24, 0.14, mixed_mask.sum()), 0.0, 1.0)
    aqi[mixed_mask] = np.clip(rng.normal(0.36, 0.22, mixed_mask.sum()), 0.0, 1.0)
    historic_disruption_rate[mixed_mask] = np.clip(rng.normal(0.30, 0.20, mixed_mask.sum()), 0.0, 1.0)
    zone_risk[mixed_mask] = np.clip(rng.normal(0.46, 0.24, mixed_mask.sum()), 0.0, 1.0)
    trigger_count_last_24h[mixed_mask] = np.clip(rng.poisson(1.4, mixed_mask.sum()) / 5.0, 0.0, 1.0)
    humidity[mixed_mask] = np.clip(rng.normal(0.50, 0.22, mixed_mask.sum()), 0.0, 1.0)
    storm_trend[mixed_mask] = np.clip(rng.normal(0.35, 0.20, mixed_mask.sum()), 0.0, 1.0)
    pressure_change[mixed_mask] = np.clip(rng.normal(0.14, 0.08, mixed_mask.sum()), 0.0, 0.45)
    forecast_confidence[mixed_mask] = np.clip(rng.normal(0.50, 0.18, mixed_mask.sum()), 0.15, 0.85)

    X = np.vstack(
        [
            rain_intensity,
            temperature_change,
            aqi,
            historic_disruption_rate,
            zone_risk,
            trigger_count_last_24h,
            humidity,
            storm_trend,
            pressure_change,
            forecast_confidence,
        ]
    ).T

    severe_risk = (storm_trend > 0.60) & (humidity > 0.65)
    hidden_risk = (aqi > 0.65) & (zone_risk > 0.55)
    confidence_penalty = (forecast_confidence < 0.35) & (temperature_change > 0.40)
    safe_mode = (aqi < 0.25) & (temperature_change < 0.18) & (trigger_count_last_24h < 0.20)
    low_risk_override = (rain_intensity > 0.55) & (humidity < 0.30) & (zone_risk < 0.30)
    strong_risk = (rain_intensity > 0.65) & (zone_risk > 0.60) & (trigger_count_last_24h > 0.35)

    base_score = (
        0.9 * rain_intensity
        + 0.7 * temperature_change
        + 0.8 * aqi
        + 1.4 * historic_disruption_rate
        + 0.9 * zone_risk
        + 0.7 * trigger_count_last_24h
        + 1.2 * storm_trend
        - 0.9 * humidity
        + 0.4 * pressure_change
        - 0.8 * forecast_confidence
    )

    rule_signal = (
        2.2 * severe_risk.astype(float)
        + 1.8 * hidden_risk.astype(float)
        + 1.6 * confidence_penalty.astype(float)
        + 2.4 * strong_risk.astype(float)
        - 2.9 * safe_mode.astype(float)
        - 2.2 * low_risk_override.astype(float)
    )

    logits = base_score + rule_signal + rng.normal(0.0, 1.0, n_samples)
    probs = 1.0 / (1.0 + np.exp(-logits))
    threshold = np.quantile(probs, 0.50)
    y = (probs > threshold).astype(int)
    label_noise = rng.random(n_samples)
    y = np.where(label_noise < 0.12, 1 - y, y)
    return X, y


def find_best_threshold(probabilities, y_true, num_points: int = 101):
    best_f1 = -1.0
    best_threshold = 0.5
    for threshold in np.linspace(0.05, 0.95, num_points):
        preds = (probabilities >= threshold).astype(int)
        score = f1_score(y_true, preds)
        if score > best_f1:
            best_f1 = score
            best_threshold = float(threshold)
    return best_threshold, best_f1


def generate_fraud_dataset(n_samples: int = 600, seed: int = 42):
    rng = np.random.default_rng(seed)
    segments = rng.choice([0, 1, 2], size=n_samples, p=[0.55, 0.30, 0.15])

    records = []
    labels = []
    for segment in segments:
        if segment == 0:
            location_mismatch = rng.choice([0.0, 1.0], p=[0.78, 0.22])
            movement_anomaly = rng.choice([0.0, 1.0], p=[0.74, 0.26])
            activity_mismatch = rng.choice([0.0, 1.0], p=[0.80, 0.20])
            claim_frequency = np.clip(rng.beta(2.0, 4.5), 0.0, 1.0)
            device_behavior_anomaly = np.clip(rng.beta(2.0, 4.5), 0.0, 1.0)
            policy_age = np.clip(rng.normal(0.45, 0.20), 0.0, 1.0)
            time_since_last_claim = np.clip(rng.normal(0.45, 0.20), 0.0, 1.0)
            claim_amount_ratio = np.clip(rng.normal(0.20, 0.12), 0.0, 1.0)
            channel_risk = np.clip(rng.normal(0.18, 0.12), 0.0, 1.0)
            claim_frequency_last_7_days = np.clip(rng.beta(1.5, 3.0), 0.0, 1.0)
            avg_claim_amount_deviation = np.clip(rng.normal(0.0, 0.15), 0.0, 1.0)
        elif segment == 1:
            location_mismatch = rng.choice([0.0, 1.0], p=[0.55, 0.45])
            movement_anomaly = rng.choice([0.0, 1.0], p=[0.50, 0.50])
            activity_mismatch = rng.choice([0.0, 1.0], p=[0.60, 0.40])
            claim_frequency = np.clip(0.2 + rng.beta(1.5, 3.0), 0.0, 1.0)
            device_behavior_anomaly = np.clip(0.25 + rng.beta(1.5, 3.0), 0.0, 1.0)
            policy_age = np.clip(rng.normal(0.35, 0.18), 0.0, 1.0)
            time_since_last_claim = np.clip(rng.normal(0.30, 0.18), 0.0, 1.0)
            claim_amount_ratio = np.clip(rng.normal(0.35, 0.18), 0.0, 1.0)
            channel_risk = np.clip(rng.normal(0.40, 0.20), 0.0, 1.0)
            claim_frequency_last_7_days = np.clip(rng.beta(2.0, 2.0), 0.0, 1.0)
            avg_claim_amount_deviation = np.clip(rng.normal(0.1, 0.15), 0.0, 1.0)
        else:
            location_mismatch = rng.choice([0.0, 1.0], p=[0.42, 0.58])
            movement_anomaly = rng.choice([0.0, 1.0], p=[0.30, 0.70])
            activity_mismatch = rng.choice([0.0, 1.0], p=[0.48, 0.52])
            claim_frequency = np.clip(0.4 + rng.beta(1.2, 2.5), 0.0, 1.0)
            device_behavior_anomaly = np.clip(0.4 + rng.beta(1.2, 2.5), 0.0, 1.0)
            policy_age = np.clip(rng.normal(0.25, 0.14), 0.0, 1.0)
            time_since_last_claim = np.clip(rng.normal(0.25, 0.16), 0.0, 1.0)
            claim_amount_ratio = np.clip(rng.normal(0.48, 0.20), 0.0, 1.0)
            channel_risk = np.clip(rng.normal(0.56, 0.20), 0.0, 1.0)
            claim_frequency_last_7_days = np.clip(rng.beta(2.5, 1.5), 0.0, 1.0)
            avg_claim_amount_deviation = np.clip(rng.normal(0.2, 0.15), 0.0, 1.0)

        base_score = (
            0.22 * location_mismatch
            + 0.22 * movement_anomaly
            + 0.18 * activity_mismatch
            + 0.12 * claim_frequency
            + 0.11 * device_behavior_anomaly
            + 0.07 * policy_age
            + 0.04 * claim_amount_ratio
            + 0.04 * channel_risk
        )
        noise = rng.normal(0.0, 0.14 if segment == 2 else 0.10)
        true_score = np.clip(base_score + noise, 0.0, 1.0)
        if rng.random() < 0.3:
            true_score += rng.normal(0, 0.2)
        true_score = np.clip(true_score, 0.0, 1.0)
        if true_score >= 0.68:
            label = "reject"
        elif true_score >= 0.35:
            label = "soft_flag"
        else:
            label = "approve"

        if rng.random() < 0.08:
            label = "reject" if label == "approve" else "approve" if label == "reject" else label

        records.append(
            {
                "location_mismatch": float(location_mismatch),
                "movement_anomaly": float(movement_anomaly),
                "activity_mismatch": float(activity_mismatch),
                "claim_frequency": float(claim_frequency),
                "device_behavior_anomaly": float(device_behavior_anomaly),
                "policy_age": float(policy_age),
                "time_since_last_claim": float(time_since_last_claim),
                "claim_amount_ratio": float(claim_amount_ratio),
                "channel_risk": float(channel_risk),
                "claim_frequency_last_7_days": float(claim_frequency_last_7_days),
                "avg_claim_amount_deviation": float(avg_claim_amount_deviation),
            }
        )
        labels.append(label)

    return records, np.array(labels, dtype=object)


def predictive_baseline(x_test, y_test):
    always_positive = np.ones_like(y_test)
    always_negative = np.zeros_like(y_test)
    simple_rule = np.where(
        (x_test[:, 0] >= 0.60)
        | (x_test[:, 2] >= 0.65)
        | (x_test[:, 3] >= 0.55)
        | (x_test[:, 9] <= 0.30),
        1,
        0,
    )
    print("Predictive baselines")
    print("  positive rate in test set:", np.mean(y_test))
    print("  always-positive accuracy:", accuracy_score(y_test, always_positive))
    print("  always-negative accuracy:", accuracy_score(y_test, always_negative))
    print("  simple rule accuracy:", accuracy_score(y_test, simple_rule))
    print("  simple rule precision:", precision_score(y_test, simple_rule, zero_division=0))
    print("  simple rule recall:", recall_score(y_test, simple_rule, zero_division=0))
    print("  simple rule F1:", f1_score(y_test, simple_rule, zero_division=0))
    print()


def fraud_feature_matrix(records, detector: FraudDetector):
    features = []
    for rec in records:
        rule_score = (
            0.25 * rec["location_mismatch"]
            + 0.25 * rec["movement_anomaly"]
            + 0.20 * rec["activity_mismatch"]
            + 0.12 * rec["claim_frequency"]
            + 0.10 * rec["device_behavior_anomaly"]
            + 0.04 * rec["policy_age"]
            + 0.03 * rec["claim_amount_ratio"]
            + 0.01 * rec["channel_risk"]
            + 0.08 * rec["claim_frequency_last_7_days"]
            + 0.06 * rec["avg_claim_amount_deviation"]
        )
        anomaly_score = 0.0
        if detector.is_trained:
            anomaly_score = detector.score_claim(rec) - rule_score * 0.65
        features.append(
            [
                rec["location_mismatch"],
                rec["movement_anomaly"],
                rec["activity_mismatch"],
                rec["claim_frequency"],
                rec["device_behavior_anomaly"],
                rec["policy_age"],
                rec["time_since_last_claim"],
                rec["claim_amount_ratio"],
                rec["channel_risk"],
                rec["claim_frequency_last_7_days"],
                rec["avg_claim_amount_deviation"],
                rule_score,
                anomaly_score,
            ]
        )
    return np.asarray(features, dtype=float)


def train_fraud_classifier(train_records, train_labels, detector: FraudDetector):
    X_train = fraud_feature_matrix(train_records, detector)
    clf = RandomForestClassifier(
        n_estimators=150,
        max_depth=6,
        class_weight="balanced",
        random_state=42,
    )
    clf.fit(X_train, train_labels)
    return clf


def fraud_rule_baseline(records):
    y_pred = []
    for rec in records:
        score = (
            0.25 * rec["location_mismatch"]
            + 0.25 * rec["movement_anomaly"]
            + 0.20 * rec["activity_mismatch"]
            + 0.12 * rec["claim_frequency"]
            + 0.10 * rec["device_behavior_anomaly"]
            + 0.04 * rec["policy_age"]
            + 0.03 * rec["claim_amount_ratio"]
            + 0.01 * rec["channel_risk"]
        )
        if score >= 0.70:
            y_pred.append("reject")
        elif score >= 0.38:
            y_pred.append("soft_flag")
        else:
            y_pred.append("approve")
    return y_pred


def evaluate_premium_model():
    X, y = generate_premium_dataset(n_samples=600, seed=101)
    x_train, x_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    linear_model = PremiumModel(model_type="linear")
    linear_model.fit(x_train, y_train)
    linear_pred = linear_model.model.predict(x_test)

    print("Premium model evaluation")
    print("-- Linear regression --")
    print("MAE:", mean_absolute_error(y_test, linear_pred))
    print("RMSE:", np.sqrt(mean_squared_error(y_test, linear_pred)))
    print("R2:", r2_score(y_test, linear_pred))
    print()

    if hasattr(PremiumModel, "_build_model"):
        xgb_model = PremiumModel(model_type="xgboost")
        xgb_model.fit(x_train, y_train)
        xgb_pred = xgb_model.model.predict(xgb_model._expand_features(x_test))
        print("-- XGBoost regression --")
        print("MAE:", mean_absolute_error(y_test, xgb_pred))
        print("RMSE:", np.sqrt(mean_squared_error(y_test, xgb_pred)))
        print("R2:", r2_score(y_test, xgb_pred))
        print()


def evaluate_predictive_model():
    X, y = generate_predictive_dataset(n_samples=1200, seed=202)
    x_train, x_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    logistic = PredictiveRiskModel(model_type="logistic")
    logistic.fit(x_train, y_train)
    log_pred = logistic.model.predict(logistic.scaler.transform(x_test))
    log_probs = logistic.model.predict_proba(logistic.scaler.transform(x_test))[:, 1]

    rf = PredictiveRiskModel(model_type="rf")
    rf.fit(x_train, y_train)
    rf_pred = rf.predict(x_test)
    rf_probs = rf.predict_proba_array(x_test)[:, 1]

    xgb_model = None
    xgb_pred = None
    xgb_probs = None
    if hasattr(PredictiveRiskModel, "__post_init__"):
        xgb_model = PredictiveRiskModel(model_type="xgb")
        xgb_model.fit(x_train, y_train)
        xgb_pred = xgb_model.predict(x_test)
        xgb_probs = xgb_model.predict_proba_array(x_test)[:, 1]

    stacked_model = None
    stacked_pred = None
    stacked_probs = None
    if hasattr(PredictiveRiskModel, "__post_init__"):
        stacked_model = PredictiveRiskModel(model_type="stacked")
        stacked_model.fit(x_train, y_train)
        stacked_probs = stacked_model.predict_proba_array(x_test)[:, 0]
        stacked_pred = (stacked_probs >= stacked_model.threshold).astype(int)

    print("Predictive risk model evaluation")
    log_best_threshold, log_best_f1 = find_best_threshold(log_probs, y_test)
    print("-- Logistic regression --")
    print("Accuracy:", accuracy_score(y_test, log_pred))
    print("Precision:", precision_score(y_test, log_pred, zero_division=0))
    print("Recall:", recall_score(y_test, log_pred, zero_division=0))
    print("F1:", f1_score(y_test, log_pred, zero_division=0))
    print("ROC-AUC:", roc_auc_score(y_test, log_probs))
    print("PR-AUC:", average_precision_score(y_test, log_probs))
    print("Best logistic threshold:", log_best_threshold, "F1:", log_best_f1)
    print("Confusion matrix:", confusion_matrix(y_test, log_pred).tolist())
    print("Logistic coefficients:", dict(zip(DEFAULT_PREDICTIVE_FEATURES, logistic.model.estimator.coef_[0].tolist())))
    print()

    print("-- Random forest --")
    print("Accuracy:", accuracy_score(y_test, rf_pred))
    print("Precision:", precision_score(y_test, rf_pred, zero_division=0))
    print("Recall:", recall_score(y_test, rf_pred, zero_division=0))
    print("F1:", f1_score(y_test, rf_pred, zero_division=0))
    print("ROC-AUC:", roc_auc_score(y_test, rf_probs))
    print("PR-AUC:", average_precision_score(y_test, rf_probs))
    print("Confusion matrix:", confusion_matrix(y_test, rf_pred).tolist())
    if rf.feature_importances is not None:
        print("Feature importances:", rf.feature_importances)
    print()

    if xgb_pred is not None:
        xgb_best_threshold, xgb_best_f1 = find_best_threshold(xgb_probs, y_test)
        print("-- XGBoost --")
        print("Accuracy:", accuracy_score(y_test, xgb_pred))
        print("Precision:", precision_score(y_test, xgb_pred, zero_division=0))
        print("Recall:", recall_score(y_test, xgb_pred, zero_division=0))
        print("F1:", f1_score(y_test, xgb_pred, zero_division=0))
        print("ROC-AUC:", roc_auc_score(y_test, xgb_probs))
        print("PR-AUC:", average_precision_score(y_test, xgb_probs))
        print("Best XGBoost threshold:", xgb_best_threshold, "F1:", xgb_best_f1)
        print("Confusion matrix:", confusion_matrix(y_test, xgb_pred).tolist())
        if hasattr(xgb_model.model, "feature_importances_"):
            print("Feature importances:", dict(zip(xgb_model.feature_names, xgb_model.model.feature_importances_)))
        print()

    if stacked_pred is not None:
        stacked_best_threshold, stacked_best_f1 = find_best_threshold(stacked_probs, y_test)
        print("-- Stacked ensemble --")
        print("Accuracy:", accuracy_score(y_test, stacked_pred))
        print("Precision:", precision_score(y_test, stacked_pred, zero_division=0))
        print("Recall:", recall_score(y_test, stacked_pred, zero_division=0))
        print("F1:", f1_score(y_test, stacked_pred, zero_division=0))
        print("ROC-AUC:", roc_auc_score(y_test, stacked_probs))
        print("PR-AUC:", average_precision_score(y_test, stacked_probs))
        print("Best stacked threshold:", stacked_best_threshold, "F1:", stacked_best_f1)
        print("Confusion matrix:", confusion_matrix(y_test, stacked_pred).tolist())
        if stacked_model.feature_importances is not None:
            print("Stacked model importances:", stacked_model.feature_importances)
        print()

    predictive_baseline(x_test, y_test)
    print()


def evaluate_fraud_model():
    records, labels = generate_fraud_dataset(n_samples=600, seed=303)
    train_records, test_records, train_labels, test_labels = train_test_split(
        records,
        labels,
        test_size=0.2,
        random_state=42,
        stratify=labels,
    )

    model = FraudDetector()
    X_train = np.array(
        [
            [
                rec["location_mismatch"],
                rec["movement_anomaly"],
                rec["activity_mismatch"],
                rec["claim_frequency"],
                rec["device_behavior_anomaly"],
                rec["policy_age"],
                rec["time_since_last_claim"],
                rec["claim_amount_ratio"],
                rec["channel_risk"],
            ]
            for rec in train_records
        ],
        dtype=float,
    )
    model.fit(X_train, train_labels)

    stage1_labels = np.where(test_labels == "approve", 0, 1)
    stage1_probs = np.array([model.score_claim(rec) for rec in test_records])
    stage1_preds = (stage1_probs >= model.threshold_stage1).astype(int)

    print("Fraud detection evaluation")
    print("-- Stage 1 fraud vs non-fraud --")
    print("Accuracy:", accuracy_score(stage1_labels, stage1_preds))
    print("Precision:", precision_score(stage1_labels, stage1_preds, zero_division=0))
    print("Recall:", recall_score(stage1_labels, stage1_preds, zero_division=0))
    print("F1:", f1_score(stage1_labels, stage1_preds, zero_division=0))
    print("Stage 1 threshold:", model.threshold_stage1)
    print()

    y_pred = [model.decision(rec) for rec in test_records]
    # Top-k reject rule: reject top 10% highest risk scores
    risk_scores = np.array([model.score_claim(rec) for rec in test_records])
    top_k = int(0.1 * len(risk_scores))
    reject_indices = np.argsort(risk_scores)[-top_k:]
    for i in reject_indices:
        y_pred[i] = "reject"
    print("-- Full two-stage decisioning (with top-10% reject rule) --")
    print("Confusion matrix:", confusion_matrix(test_labels, y_pred, labels=["approve", "soft_flag", "reject"]))
    print(
        classification_report(
            test_labels,
            y_pred,
            labels=["approve", "soft_flag", "reject"],
            zero_division=0,
        )
    )
    if model.stage1_feature_importances is not None:
        print("Stage 1 importances:", model.stage1_feature_importances)
    print()

    # Failure Mode Analysis
    y_true_binary = np.where(test_labels == "approve", 0, 1)  # 1 = fraud (reject/soft_flag), 0 = approve
    risk_scores = stage1_probs
    y_pred_binary = stage1_preds  # 1 = flagged as fraud, 0 = approved
    threshold_reject = model.threshold_stage1

    # 1. Worst-Case Errors (Top False Negatives)
    fn_mask = (y_true_binary == 1) & (y_pred_binary == 0)
    fn_scores = risk_scores[fn_mask]

    print("\n[Failure Analysis] Worst False Negatives:")
    if len(fn_scores) > 0:
        worst_fn_indices = np.argsort(fn_scores)[:10]  # lowest risk scores among missed frauds
        for i, idx in enumerate(worst_fn_indices):
            actual_idx = np.where(fn_mask)[0][idx]
            print(f"Index {actual_idx} | Risk Score: {fn_scores[idx]:.3f}")
    else:
        print("No false negatives found")

    # 2. Threshold Sensitivity
    thresholds = [threshold_reject - 0.05, threshold_reject, threshold_reject + 0.05]
    print("\n[Threshold Sensitivity Analysis]")
    for t in thresholds:
        preds = (risk_scores >= t).astype(int)
        recall = recall_score(y_true_binary, preds, zero_division=0)
        precision = precision_score(y_true_binary, preds, zero_division=0)
        print(f"Threshold {t:.2f} | Recall: {recall:.3f} | Precision: {precision:.3f}")

    # 3. Segment-Based Error Analysis
    low = risk_scores < 0.3
    mid = (risk_scores >= 0.3) & (risk_scores < 0.7)
    high = risk_scores >= 0.7

    def segment_eval(mask, name):
        if np.sum(mask) == 0:
            return
        acc = accuracy_score(y_true_binary[mask], y_pred_binary[mask])
        print(f"{name} Segment Accuracy: {acc:.3f}")

    print("\n[Segment Analysis]")
    segment_eval(low, "Low Risk")
    segment_eval(mid, "Mid Risk")
    segment_eval(high, "High Risk")

    print()

    clf = train_fraud_classifier(train_records, train_labels, model)
    X_test = fraud_feature_matrix(test_records, model)
    clf_pred = clf.predict(X_test)
    print("Supervised fraud classifier confusion matrix:")
    print(confusion_matrix(test_labels, clf_pred, labels=["approve", "soft_flag", "reject"]))
    print("Supervised fraud classifier classification report:")
    print(
        classification_report(
            test_labels,
            clf_pred,
            labels=["approve", "soft_flag", "reject"],
            zero_division=0,
        )
    )
    if hasattr(clf, "feature_importances_"):
        print("Fraud classifier importances:", clf.feature_importances_.tolist())
    print()

    baseline_pred = fraud_rule_baseline(test_records)
    print("Fraud rule-only baseline")
    print("Confusion matrix:")
    print(confusion_matrix(test_labels, baseline_pred, labels=["approve", "soft_flag", "reject"]))
    print("Classification report:")
    print(
        classification_report(
            test_labels,
            baseline_pred,
            labels=["approve", "soft_flag", "reject"],
            zero_division=0,
        )
    )
    print()


if __name__ == "__main__":
    evaluate_premium_model()
    evaluate_predictive_model()
    evaluate_fraud_model()
