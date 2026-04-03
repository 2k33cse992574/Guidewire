from dataclasses import dataclass
from typing import Dict, List, Optional

import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.calibration import CalibratedClassifierCV

try:
    import xgboost as xgb
except ImportError:  # pragma: no cover
    xgb = None

DEFAULT_PREDICTIVE_FEATURES = [
    "rain_intensity",
    "temperature_change",
    "aqi",
    "historic_disruption_rate",
    "zone_risk",
    "trigger_count_last_24h",
    "humidity",
    "storm_trend",
    "pressure_change",
    "forecast_confidence",
]

DEFAULT_INTERACTION_NAMES = [
    "rain_zone",
    "humidity_storm",
    "aqi_temp",
    "zone_trigger",
    "pressure_confidence",
]


@dataclass
class PredictiveRiskModel:
    """Predictive risk model for 24–72 hour disruption probability."""

    model_type: str = "logistic"
    solver: str = "liblinear"
    threshold: float = 0.5
    model: Optional[object] = None
    scaler: StandardScaler = StandardScaler()
    is_trained: bool = False
    use_interactions: bool = False

    interaction_feature_names: List[str] = None
    base_models: Optional[List[object]] = None

    def __post_init__(self):
        self.model_type = self.model_type.lower()
        self.use_interactions = self.model_type in {"rf", "xgb", "stacked"}
        self.interaction_feature_names = DEFAULT_INTERACTION_NAMES.copy()

        if self.model_type == "rf":
            self.model = RandomForestClassifier(
                n_estimators=220,
                max_depth=10,
                class_weight="balanced",
                random_state=42,
            )
        elif self.model_type == "xgb" and xgb is not None:
            self.model = xgb.XGBClassifier(
                objective="binary:logistic",
                n_estimators=260,
                max_depth=8,
                learning_rate=0.05,
                subsample=0.80,
                colsample_bytree=0.78,
                eval_metric="logloss",
                random_state=42,
            )
        elif self.model_type == "stacked" and xgb is not None:
            self.base_models = [
                LogisticRegression(solver=self.solver, max_iter=1000, class_weight="balanced"),
                RandomForestClassifier(n_estimators=180, max_depth=8, class_weight="balanced", random_state=42),
                xgb.XGBClassifier(
                    objective="binary:logistic",
                    n_estimators=180,
                    max_depth=7,
                    learning_rate=0.06,
                    subsample=0.78,
                    colsample_bytree=0.75,
                    eval_metric="logloss",
                    random_state=42,
                ),
            ]
            self.model = None
        else:
            self.model_type = "logistic"
            self.model = LogisticRegression(
                solver=self.solver,
                max_iter=1000,
                class_weight="balanced",
            )

    @property
    def feature_names(self) -> List[str]:
        names = DEFAULT_PREDICTIVE_FEATURES.copy()
        if self.use_interactions:
            names += self.interaction_feature_names
        return names

    @staticmethod
    def _expand_features(X: np.ndarray) -> np.ndarray:
        if X.ndim == 1:
            X = X.reshape(1, -1)
        interaction_cols = np.column_stack(
            [
                X[:, 0] * X[:, 4],
                X[:, 6] * X[:, 7],
                X[:, 2] * X[:, 1],
                X[:, 4] * X[:, 5],
                X[:, 8] * X[:, 9],
            ]
        )
        return np.hstack([X, interaction_cols])

    def fit(self, X: np.ndarray, y: np.ndarray) -> None:
        if self.model_type == "logistic":
            X_scaled = self.scaler.fit_transform(X)
            self.model.fit(X_scaled, y)
            # Calibrate probabilities
            self.model = CalibratedClassifierCV(self.model, method='isotonic', cv='prefit')
            self.model.fit(X_scaled, y)
        elif self.model_type == "stacked" and self.base_models is not None:
            expanded = self._expand_features(X)
            for base in self.base_models:
                if isinstance(base, LogisticRegression):
                    base.fit(self.scaler.fit_transform(X), y)
                    base = CalibratedClassifierCV(base, method='isotonic', cv='prefit')
                    base.fit(self.scaler.transform(X), y)
                else:
                    base.fit(expanded, y)
                    base = CalibratedClassifierCV(base, method='isotonic', cv='prefit')
                    base.fit(expanded, y)
        else:
            X_transformed = self._expand_features(X)
            self.model.fit(X_transformed, y)
            # Calibrate probabilities
            self.model = CalibratedClassifierCV(self.model, method='isotonic', cv='prefit')
            self.model.fit(X_transformed, y)
        self.is_trained = True

    def predict(self, X: np.ndarray) -> np.ndarray:
        if self.model_type == "logistic":
            return self.model.predict(self.scaler.transform(X))
        if self.model_type == "stacked" and self.base_models is not None:
            return (self.predict_proba_array(X) >= self.threshold).astype(int)
        return self.model.predict(self._expand_features(X))

    def predict_proba_array(self, X: np.ndarray) -> np.ndarray:
        if self.model_type == "logistic":
            return self.model.predict_proba(self.scaler.transform(X))
        if self.model_type == "stacked" and self.base_models is not None:
            expanded = self._expand_features(X)
            probs = []
            for base in self.base_models:
                if isinstance(base, LogisticRegression):
                    probs.append(base.predict_proba(self.scaler.transform(X))[:, 1])
                else:
                    probs.append(base.predict_proba(expanded)[:, 1])
            return np.vstack(probs).mean(axis=0).reshape(-1, 1)
        return self.model.predict_proba(self._expand_features(X))

    def predict_probability(self, features: Dict[str, float]) -> float:
        vector = self._build_feature_vector(features).reshape(1, -1)
        if self.is_trained:
            if self.model_type == "logistic":
                scaled = self.scaler.transform(vector)
                score = float(self.model.predict_proba(scaled)[0][1])
            elif self.model_type == "stacked" and self.base_models is not None:
                score = float(self.predict_proba_array(vector)[0][0])
            else:
                vector = self._expand_features(vector)
                score = float(self.model.predict_proba(vector)[0][1])
        else:
            score = self._fallback_probability(features)
        return max(0.0, min(1.0, score))

    def risk_score(self, features: Dict[str, float]) -> float:
        """Return continuous risk score (0-1) for ranking, not classification."""
        return self.predict_probability(features)

    def explain_prediction(self, features: Dict[str, float]) -> Dict[str, object]:
        """Explain the risk prediction with feature contributions."""
        vector = self._build_feature_vector(features).reshape(1, -1)
        explanation = {
            "risk_score": self.risk_score(features),
            "model_type": self.model_type,
        }
        if self.is_trained and self.model_type == "stacked" and self.base_models is not None:
            explanation["stacked_importances"] = self.feature_importances
        elif self.is_trained and hasattr(self.model, "feature_importances_"):
            explanation["feature_importances"] = {
                name: float(imp) for name, imp in zip(self.feature_names, self.model.feature_importances_)
            }
        elif self.is_trained and hasattr(self.model, "coef_"):
            explanation["coefficients"] = {
                name: float(coef) for name, coef in zip(DEFAULT_PREDICTIVE_FEATURES, self.model.coef_[0])
            }
        return explanation

    @property
    def feature_importances(self) -> Optional[dict]:
        if self.is_trained and self.model_type == "stacked" and self.base_models is not None:
            importances = {}
            for base in self.base_models:
                if hasattr(base, "coef_"):
                    contributions = {
                        name: float(coef * 1.0)
                        for name, coef in zip(DEFAULT_PREDICTIVE_FEATURES, base.coef_[0])
                    }
                    importances["logistic_coefficients"] = contributions
                elif hasattr(base, "feature_importances_"):
                    importances[type(base).__name__] = {
                        name: float(value)
                        for name, value in zip(self.feature_names, base.feature_importances_)
                    }
            return importances
        if self.is_trained and hasattr(self.model, "feature_importances_"):
            return {
                name: float(importance)
                for name, importance in zip(self.feature_names, self.model.feature_importances_)
            }
        return None

    def feature_contributions(self, features: Dict[str, float]) -> Optional[Dict[str, float]]:
        if not self.is_trained:
            return None
        vector = self._build_feature_vector(features).reshape(1, -1)
        if self.model_type == "logistic":
            scaled = self.scaler.transform(vector)[0]
            coefs = self.model.coef_[0]
            contributions = {
                name: float(coef * value)
                for name, value, coef in zip(DEFAULT_PREDICTIVE_FEATURES, scaled, coefs)
            }
            contributions["intercept"] = float(self.model.intercept_[0])
            return contributions
        if self.model_type == "stacked" and self.base_models is not None:
            contributions = {}
            contributions["stacked_base_models"] = self.feature_importances
            return contributions
        if hasattr(self.model, "feature_importances_"):
            return {
                name: float(importance)
                for name, importance in zip(self.feature_names, self.model.feature_importances_)
            }
        return None

    def explain_prediction(self, features: Dict[str, float]) -> Dict[str, object]:
        explanation = {
            "score": self.predict_probability(features),
            "decision": self.is_disruption_expected(features),
            "threshold": self.threshold,
            "model_type": self.model_type,
        }
        contributions = self.feature_contributions(features)
        if contributions is not None:
            explanation["feature_contributions"] = contributions
        return explanation

    def is_disruption_expected(self, features: Dict[str, float], threshold: Optional[float] = None) -> bool:
        score = self.predict_probability(features)
        return score >= (threshold if threshold is not None else self.threshold)

    @staticmethod
    def _build_feature_vector(features: Dict[str, float]) -> np.ndarray:
        return np.asarray([float(features.get(name, 0.0)) for name in DEFAULT_PREDICTIVE_FEATURES], dtype=float)

    @staticmethod
    def _fallback_probability(features: Dict[str, float]) -> float:
        weights = {
            "rain_intensity": 0.25,
            "temperature_change": 0.12,
            "aqi": 0.15,
            "historic_disruption_rate": 0.30,
            "zone_risk": 0.10,
            "trigger_count_last_24h": 0.05,
            "humidity": -0.02,
            "storm_trend": 0.03,
            "pressure_change": 0.02,
            "forecast_confidence": -0.05,
        }
        score = 0.0
        total = 0.0
        for name, weight in weights.items():
            score += float(features.get(name, 0.0)) * weight
            total += abs(weight)
        return score / total if total > 0 else 0.0

    @staticmethod
    def sample_training_data() -> (np.ndarray, np.ndarray):
        X = np.array(
            [
                [0.2, 0.05, 0.1, 0.1, 0.2, 0.0, 0.4, 0.2, 0.08, 0.8],
                [0.4, 0.15, 0.2, 0.2, 0.4, 0.1, 0.5, 0.3, 0.12, 0.7],
                [0.6, 0.2, 0.4, 0.4, 0.6, 0.2, 0.6, 0.4, 0.18, 0.55],
                [0.8, 0.3, 0.7, 0.7, 0.8, 0.4, 0.7, 0.5, 0.25, 0.35],
                [0.9, 0.4, 0.8, 0.8, 0.9, 0.6, 0.8, 0.6, 0.30, 0.20],
            ],
            dtype=float,
        )
        y = np.array([0, 0, 1, 1, 1], dtype=int)
        return X, y
