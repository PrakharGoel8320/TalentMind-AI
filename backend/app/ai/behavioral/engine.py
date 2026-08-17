import logging
from typing import Dict, Any, Tuple

from app.ai.behavioral.config import config

logger = logging.getLogger(__name__)


class BehavioralEngine:
    """
    Deterministic scoring engine for behavioral signals.
    Reads weights and calibration from config.json.
    """

    def __init__(self):
        self.weights = config.get("weights", {})
        self.calibration = config.get("calibration", {})
        self.final_scale = config.get("engine", {}).get("final_scale", 100)

    def _normalize_score(self, value: float, cal: dict) -> float:
        min_val = cal.get("min", 0.0)
        max_val = cal.get("max", 1.0)
        if max_val == min_val:
            return 0.0
        return max(0.0, min(1.0, (float(value) - min_val) / (max_val - min_val)))

    def _normalize_percentage(self, value: float, cal: dict) -> float:
        return max(0.0, min(1.0, float(value) / 100.0))

    def _normalize_boolean(self, value: bool, cal: dict) -> float:
        return 1.0 if value else 0.0

    def compute_score(self, features: Dict[str, Any]) -> Tuple[float, float]:
        total_score = 0.0
        valid_features_count = 0
        total_expected_features = max(1, len(self.weights))

        if "recruiter_response_rate" in features:
            val = self._normalize_percentage(
                features["recruiter_response_rate"],
                self.calibration.get("recruiter_response_rate", {})
            )
            total_score += val * self.weights.get("recruiter_response_rate", 0)
            valid_features_count += 1

        if "last_active_days_ago" in features:
            # Lower is better — invert: 0 days = 1.0, >=90 days = 0.0
            raw = features["last_active_days_ago"]
            cal = self.calibration.get("last_active_days_ago", {"max": 90})
            normalized = max(0.0, 1.0 - float(raw) / cal.get("max", 90))
            total_score += normalized * self.weights.get("last_active_days_ago", 0)
            valid_features_count += 1

        if "interview_completion_rate" in features:
            val = self._normalize_percentage(
                features["interview_completion_rate"],
                self.calibration.get("interview_completion_rate", {})
            )
            total_score += val * self.weights.get("interview_completion_rate", 0)
            valid_features_count += 1

        if "github_activity_score" in features:
            val = self._normalize_score(
                features["github_activity_score"],
                self.calibration.get("github_activity", {})
            )
            total_score += val * self.weights.get("github_activity", 0)
            valid_features_count += 1

        if "open_to_work" in features:
            val = self._normalize_boolean(
                features["open_to_work"],
                self.calibration.get("open_to_work_flag", {})
            )
            total_score += val * self.weights.get("open_to_work_flag", 0)
            valid_features_count += 1

        if "profile_completeness" in features:
            val = self._normalize_percentage(
                features["profile_completeness"],
                self.calibration.get("profile_completeness", {})
            )
            total_score += val * self.weights.get("profile_completeness", 0)
            valid_features_count += 1

        confidence_ratio = valid_features_count / max(total_expected_features, 1)
        confidence = confidence_ratio * self.final_scale
        behavior_score = total_score * self.final_scale

        min_conf = config.get("engine", {}).get("min_confidence_threshold", 30)
        if confidence < min_conf:
            logger.warning(f"Low behavioral confidence ({confidence:.2f}%). Missing key features.")

        return round(behavior_score, 2), round(confidence, 2)
