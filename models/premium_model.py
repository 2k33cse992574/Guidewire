import numpy as np
from sklearn.linear_model import LinearRegression

try:
    import xgboost as xgb
except ImportError:  # pragma: no cover
    xgb = None

DEFAULT_FEATURE_ORDER = [
    "weather_risk",
    "location_risk",
    "work_pattern_risk",
    "historical_risk",
    "aqi_risk",
    "area_risk",
    "seasonality",
    "volatility",
    "claim_history",
    "driver_score",
]

DEFAULT_WEIGHTS = {
    "weather_risk": 0.18,
    "location_risk": 0.15,
    "work_pattern_risk": 0.15,
    "historical_risk": 0.12,
    "aqi_risk": 0.08,
    "area_risk": 0.07,
    "seasonality": 0.05,
    "volatility": 0.04,
    "claim_history": 0.10,
    "driver_score": 0.06,
}

INTERACTION_PAIRS = [
    (0, 3),  # weather_risk * historical_risk
    (1, 5),  # location_risk * area_risk
    (2, 4),  # work_pattern_risk * aqi_risk
    (6, 7),  # seasonality * volatility
    (8, 9),  # claim_history * driver_score
    (0, 8),  # weather_risk * claim_history
    (3, 9),  # historical_risk * driver_score
]


class PremiumModel:
    """Dynamic weekly premium model for GigShield."""

    def __init__(self, model_type: str = "xgboost"):
        self.model_type = model_type.lower()
        self.model = None
        self.is_trained = False
        self._build_model()

    def _build_model(self):
        if self.model_type == "xgboost" and xgb is not None:
            self.model = xgb.XGBRegressor(
                objective="reg:squarederror",
                n_estimators=120,
                max_depth=4,
                learning_rate=0.08,
                subsample=0.85,
                colsample_bytree=0.80,
                random_state=42,
            )
        else:
            self.model_type = "linear"
            self.model = LinearRegression()

    @property
    def feature_names(self):
        return DEFAULT_FEATURE_ORDER.copy()

    @staticmethod
    def _expand_features(X: np.ndarray) -> np.ndarray:
        if X.ndim == 1:
            X = X.reshape(1, -1)
        interaction_cols = np.column_stack(
            [X[:, a] * X[:, b] for a, b in INTERACTION_PAIRS]
        )
        return np.hstack([X, interaction_cols])

    def fit(self, X: np.ndarray, y: np.ndarray) -> None:
        if self.model_type == "xgboost":
            X_transformed = self._expand_features(X)
            self.model.fit(X_transformed, y)
        else:
            self.model.fit(X, y)
        self.is_trained = True

    def predict_risk(self, features: dict) -> float:
        vector = self._build_feature_vector(features)
        if self.is_trained:
            if self.model_type == "xgboost":
                vector = self._expand_features(vector)
            score = float(self.model.predict(vector.reshape(1, -1))[0])
        else:
            score = self._weighted_risk_score(features)
        return float(np.clip(score, 0.0, 1.0))

    def risk_score(self, features: dict) -> float:
        """Return continuous risk score for premium adjustment."""
        return self.predict_risk(features)

    def compute_weekly_premium(self, weekly_income: float, risk_score: float) -> float:
        return float(max(0.0, weekly_income * risk_score * 0.05))

    def _weighted_risk_score(self, features: dict) -> float:
        score = 0.0
        for name, weight in DEFAULT_WEIGHTS.items():
            score += float(features.get(name, 0.0)) * weight
        return score

    def _build_feature_vector(self, features: dict) -> np.ndarray:
        return np.asarray([float(features.get(name, 0.0)) for name in DEFAULT_FEATURE_ORDER], dtype=float)

    @staticmethod
    def sample_training_data() -> tuple[np.ndarray, np.ndarray]:
        X = np.array(
            [
                [0.1, 0.1, 0.1, 0.05, 0.1, 0.1, 0.12, 0.08, 0.0, 0.9],
                [0.4, 0.2, 0.3, 0.2, 0.3, 0.3, 0.18, 0.14, 0.1, 0.8],
                [0.7, 0.6, 0.5, 0.5, 0.6, 0.5, 0.35, 0.22, 0.3, 0.6],
                [0.9, 0.8, 0.7, 0.8, 0.8, 0.7, 0.45, 0.30, 0.6, 0.4],
                [0.2, 0.4, 0.2, 0.1, 0.2, 0.2, 0.08, 0.10, 0.05, 0.85],
                [0.6, 0.5, 0.4, 0.4, 0.5, 0.4, 0.25, 0.18, 0.4, 0.5],
            ],
            dtype=float,
        )
        y = np.array(
            [
                0.12,
                0.28,
                0.52,
                0.83,
                0.21,
                0.48,
            ],
            dtype=float,
        )
        return X, y


if __name__ == "__main__":
    model = PremiumModel(model_type="linear")
    X, y = model.sample_training_data()
    model.fit(X, y)
    features = {
        "weather_risk": 0.7,
        "location_risk": 0.8,
        "work_pattern_risk": 0.5,
        "historical_risk": 0.6,
        "aqi_risk": 0.4,
        "area_risk": 0.7,
        "seasonality": 0.3,
        "volatility": 0.15,
    }
    print("Risk score:", model.predict_risk(features))
