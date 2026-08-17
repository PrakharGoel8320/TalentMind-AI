import logging
from typing import Dict, Any, List

from app.ai.behavioral.engine import BehavioralEngine

logger = logging.getLogger(__name__)


class BehavioralService:
    def __init__(self):
        self.engine = BehavioralEngine()

    def _extract_behavioral_features(self, candidate: Dict[str, Any]) -> Dict[str, Any]:
        features = {}
        behavioral_data = candidate.get("behavioral_metrics", candidate)

        if "recruiter_response_rate" in behavioral_data:
            features["recruiter_response_rate"] = behavioral_data["recruiter_response_rate"]

        if "last_active_days_ago" in behavioral_data:
            features["last_active_days_ago"] = behavioral_data["last_active_days_ago"]

        if "interview_completion_rate" in behavioral_data:
            features["interview_completion_rate"] = behavioral_data["interview_completion_rate"]

        if "github_activity_score" in behavioral_data:
            features["github_activity_score"] = behavioral_data["github_activity_score"]

        if "open_to_work" in behavioral_data:
            features["open_to_work"] = behavioral_data["open_to_work"]

        if "profile_completeness" in behavioral_data:
            features["profile_completeness"] = behavioral_data["profile_completeness"]

        return features

    def score_candidates(self, candidates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        if not candidates:
            return []

        for cand in candidates:
            features = self._extract_behavioral_features(cand)
            score, confidence = self.engine.compute_score(features)
            cand["behavioral_score"] = score
            cand["behavioral_confidence"] = confidence

        return candidates
