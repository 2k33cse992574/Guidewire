from dataclasses import dataclass
from typing import Dict, List, Optional

import numpy as np
from sklearn.ensemble import IsolationForest, RandomForestClassifier
from sklearn.metrics import precision_score, recall_score
from sklearn.calibration import CalibratedClassifierCV

try:
    import xgboost as xgb
except ImportError:
    xgb = None


@dataclass
class FraudDetector:
    """Two-stage fraud detector: detect fraud → rank severity with gradient boosting."""

    location_weight: float = 0.22
    movement_weight: float = 0.22
    activity_weight: float = 0.18
    frequency_weight: float = 0.16
    device_weight: float = 0.12
    threshold_stage1: float = 0.35
    threshold_reject: float = 0.65
    threshold_soft_flag: float = 0.40
    stage1_model: Optional[RandomForestClassifier] = None
    stage2_ranker: Optional[object] = None  # XGBoost or fallback
    model: Optional[IsolationForest] = None
    is_trained: bool = False

    def __post_init__(self):
        self.model = IsolationForest(n_estimators=200, contamination=0.10, random_state=42)

    @staticmethod
    def _claim_vector(claim: Dict[str, float]) -> np.ndarray:
        return np.asarray(
            [
                1.0 if claim.get("location_mismatch", False) else 0.0,
                1.0 if claim.get("movement_anomaly", False) else 0.0,
                1.0 if claim.get("activity_mismatch", False) else 0.0,
                float(claim.get("claim_frequency", 0.0)),
                float(claim.get("device_behavior_anomaly", 0.0)),
                float(claim.get("policy_age", 0.0)),
                float(claim.get("time_since_last_claim", 0.0)),
                float(claim.get("claim_amount_ratio", 0.0)),
                float(claim.get("channel_risk", 0.0)),
            ],
            dtype=float,
        )

    def fit(self, X: np.ndarray, labels: Optional[np.ndarray] = None) -> None:
        self.model.fit(X)
        if labels is not None:
            labels = np.asarray(labels, dtype=object)
            fraud_binary = np.where(labels == "approve", 0, 1)
            rule_scores = self._rule_scores_from_matrix(X)
            anomaly_scores = self._anomaly_scores_from_matrix(X)
            meta_features = np.column_stack([X, rule_scores, anomaly_scores])

            # Stage 1: Detect fraud vs non-fraud
            self.stage1_model = RandomForestClassifier(
                n_estimators=160,
                max_depth=8,
                class_weight="balanced",
                random_state=42,
            )
            self.stage1_model.fit(meta_features, fraud_binary)
            
            # Calibrate probabilities for better ranking
            self.stage1_model = CalibratedClassifierCV(
                self.stage1_model, method='isotonic', cv='prefit'
            )
            self.stage1_model.fit(meta_features, fraud_binary)

            # Stage 2: Rank severity among frauds using ranking model
            fraud_mask = fraud_binary == 1
            if fraud_mask.sum() > 1:
                fraud_labels = labels[fraud_mask]
                severity_binary = np.where(fraud_labels == "reject", 1, 0)
                fraud_meta = meta_features[fraud_mask]
                stage1_probs = self.stage1_model.predict_proba(fraud_meta)[:, 1]
                rule_scores_fraud = rule_scores[fraud_mask]
                anomaly_scores_fraud = anomaly_scores[fraud_mask]
                ranking_features = np.column_stack([
                    stage1_probs, rule_scores_fraud, anomaly_scores_fraud
                ])
                
                if xgb is not None:
                    base_ranker = xgb.XGBClassifier(
                        objective="binary:logistic",
                        n_estimators=100,
                        max_depth=4,
                        learning_rate=0.1,
                        random_state=42,
                    )
                else:
                    base_ranker = RandomForestClassifier(
                        n_estimators=100, max_depth=4, random_state=42
                    )

                base_ranker.fit(ranking_features, severity_binary)
                try:
                    calibrated = CalibratedClassifierCV(base_ranker, method='isotonic', cv='prefit')
                    calibrated.fit(ranking_features, severity_binary)
                    self.stage2_ranker = calibrated
                except Exception:
                    # Fallback to non-calibrated stage2 ranker
                    self.stage2_ranker = base_ranker

            self._calibrate_thresholds_on_ranker(ranking_features, severity_binary)

            self._calibrate_stage1_threshold(meta_features, fraud_binary)

        self.is_trained = True

    def _calibrate_stage1_threshold(self, meta_features: np.ndarray, fraud_binary: np.ndarray) -> None:
        if self.stage1_model is None or not hasattr(self.stage1_model, "predict_proba"):
            return

        proba = self.stage1_model.predict_proba(meta_features)[:, 1]
        best_score = -1.0
        best_threshold = self.threshold_stage1
        for threshold in np.linspace(0.10, 0.80, 15):
            preds = (proba >= threshold).astype(int)
            recall = recall_score(fraud_binary, preds, zero_division=0)
            precision = precision_score(fraud_binary, preds, zero_division=0)
            score = recall + 0.2 * precision
            if score > best_score:
                best_score = score
                best_threshold = float(threshold)
        self.threshold_stage1 = best_threshold

    def _calibrate_thresholds_on_ranker(self, ranking_features: np.ndarray, severity_binary: np.ndarray) -> None:
        """Calibrate stage 2 thresholds using ranker probabilities, prioritizing recall."""
        if self.stage2_ranker is None or severity_binary.sum() < 2:
            return

        ranker_probs = self.stage2_ranker.predict_proba(ranking_features)[:, 1]

        # Find reject threshold prioritizing recall (target >= 0.67 if possible)
        best_reject = 0.55
        best_score = -1.0
        best_precision = 0.0

        for reject_th in np.linspace(0.05, 0.85, 33):
            reject_preds = (ranker_probs >= reject_th).astype(int)
            if reject_preds.sum() < 1:
                continue
            recall_r = recall_score(severity_binary, reject_preds, zero_division=0)
            precision_r = precision_score(severity_binary, reject_preds, zero_division=0)
            if recall_r > best_score or (recall_r == best_score and precision_r > best_precision):
                best_score = recall_r
                best_precision = precision_r
                best_reject = float(reject_th)

        if best_score < 0.67:
            # relax threshold to encourage more recall when not achievable
            for reject_th in np.linspace(0.05, 0.50, 46):
                reject_preds = (ranker_probs >= reject_th).astype(int)
                recall_r = recall_score(severity_binary, reject_preds, zero_division=0)
                if recall_r > best_score:
                    best_score = recall_r
                    best_reject = float(reject_th)

        self.threshold_reject = best_reject
        self.threshold_soft_flag = max(0.15, min(0.35, self.threshold_reject - 0.20))

        # Force a floor for reject threshold for safety and consistent baseline behavior
        self.threshold_reject = max(0.35, self.threshold_reject)

    def _rule_scores_from_matrix(self, X: np.ndarray) -> np.ndarray:
        return (
            X[:, 0] * self.location_weight
            + X[:, 1] * self.movement_weight
            + X[:, 2] * self.activity_weight
            + X[:, 3] * self.frequency_weight
            + X[:, 4] * self.device_weight
        )

    def _anomaly_scores_from_matrix(self, X: np.ndarray) -> np.ndarray:
        raw_scores = self.model.score_samples(X)
        return 1.0 / (1.0 + np.exp(raw_scores * 3.5))

    def score_claim(self, claim: Dict[str, float]) -> float:
        if not self.is_trained or self.stage1_model is None:
            return self._rule_only_score(claim)

        vector = self._claim_vector(claim).reshape(1, -1)
        rule_score = self._rule_scores_from_matrix(vector)[0]
        anomaly_score = self._anomaly_scores_from_matrix(vector)[0]
        meta_features = np.column_stack([vector, [rule_score], [anomaly_score]])
        fraud_probability = float(self.stage1_model.predict_proba(meta_features)[0][1])
        return max(0.0, min(1.0, fraud_probability))

    def _get_severity_score(self, claim: Dict[str, float]) -> float:
        """Get continuous risk score for severity ranking using ranker."""
        if self.stage2_ranker is None:
            # Fallback to rule + anomaly
            vector = self._claim_vector(claim).reshape(1, -1)
            rule_score = self._rule_scores_from_matrix(vector)[0]
            anomaly_score = self._anomaly_scores_from_matrix(vector)[0]
            return 0.6 * rule_score + 0.4 * anomaly_score
        
        vector = self._claim_vector(claim).reshape(1, -1)
        rule_score = self._rule_scores_from_matrix(vector)[0]
        anomaly_score = self._anomaly_scores_from_matrix(vector)[0]

        # Fall back to rule+anomaly if ranker missing
        fallback = max(0.0, min(1.0, 0.6 * rule_score + 0.4 * anomaly_score))

        if self.stage2_ranker is None:
            return fallback

        meta_features = np.column_stack([vector, [rule_score], [anomaly_score]])
        # stage1_prob should be calibrated
        stage1_prob = self.stage1_model.predict_proba(meta_features)[0][1]
        ranking_features = np.array([[stage1_prob, rule_score, anomaly_score]])

        try:
            ranker_score = float(self.stage2_ranker.predict_proba(ranking_features)[0][1])
        except Exception:
            ranker_score = fallback

        # Blend ranker and heuristic for robustness
        severity_score = 0.7 * ranker_score + 0.3 * fallback
        return float(np.clip(severity_score, 0.0, 1.0))

    def _rule_only_score(self, claim: Dict[str, float]) -> float:
        vector = self._claim_vector(claim)
        score = (
            vector[0] * self.location_weight
            + vector[1] * self.movement_weight
            + vector[2] * self.activity_weight
            + vector[3] * self.frequency_weight
            + vector[4] * self.device_weight
        )
        return float(np.clip(score, 0.0, 1.0))

    def decision(self, claim: Dict[str, float]) -> str:
        """
        Two-stage risk-based decision:
        1. Detect: Is this fraud or not?
        2. Rank: If fraud, how severe? Apply thresholds.
        """
        vector = self._claim_vector(claim).reshape(1, -1)
        rule_score = self._rule_scores_from_matrix(vector)[0]
        anomaly_score = self._anomaly_scores_from_matrix(vector)[0]
        meta_features = np.column_stack([vector, [rule_score], [anomaly_score]])

        if self.stage1_model is None or not self.is_trained:
            if self._rule_only_score(claim) >= 0.65:
                return "reject"
            if self._rule_only_score(claim) >= 0.36:
                return "soft_flag"
            return "approve"

        # Stage 1: Detect fraud
        fraud_probability = float(self.stage1_model.predict_proba(meta_features)[0][1])
        if fraud_probability < self.threshold_stage1:
            return "approve"

        # Stage 2: Rank severity among detected frauds using continuous score
        severity_score = self._get_severity_score(claim)
        if severity_score >= self.threshold_reject:
            return "reject"
        elif severity_score >= self.threshold_soft_flag:
            return "soft_flag"
        else:
            return "approve"

    def explain_claim(self, claim: Dict[str, float]) -> Dict[str, object]:
        vector = self._claim_vector(claim).reshape(1, -1)
        rule_score = self._rule_scores_from_matrix(vector)[0]
        anomaly_score = self._anomaly_scores_from_matrix(vector)[0]
        meta_features = np.column_stack([vector, [rule_score], [anomaly_score]])
        decision = self.decision(claim)

        explanation = {
            "rule_score": float(rule_score),
            "anomaly_score": float(anomaly_score),
            "fraud_probability": float(self.score_claim(claim)),
            "severity_score": float(self._get_severity_score(claim)),
            "decision": decision,
            "stage1_threshold": self.threshold_stage1,
            "threshold_reject": self.threshold_reject,
            "threshold_soft_flag": self.threshold_soft_flag,
        }
        if self.stage1_model is not None:
            explanation["stage1_class_probs"] = {
                str(cls): float(prob) for cls, prob in zip(
                    self.stage1_model.classes_,
                    self.stage1_model.predict_proba(meta_features)[0],
                )
            }
        return explanation

    @property
    def stage1_feature_importances(self) -> Optional[List[float]]:
        if self.stage1_model is not None and hasattr(self.stage1_model, "feature_importances_"):
            return self.stage1_model.feature_importances_.tolist()
        return None

    @staticmethod
    def sample_training_data() -> np.ndarray:
        return np.array(
            [
                [0.0, 0.0, 0.0, 0.1, 0.0, 0.2, 0.6, 0.12, 0.2],
                [0.0, 0.0, 0.0, 0.2, 0.0, 0.1, 0.3, 0.08, 0.1],
                [1.0, 0.0, 0.0, 0.4, 0.2, 0.5, 0.1, 0.25, 0.6],
                [0.0, 1.0, 0.0, 0.3, 0.1, 0.2, 0.4, 0.18, 0.4],
                [0.0, 0.0, 1.0, 0.5, 0.2, 0.4, 0.2, 0.22, 0.5],
                [1.0, 1.0, 1.0, 0.7, 0.5, 0.8, 0.05, 0.35, 0.8],
            ],
            dtype=float,
        )
