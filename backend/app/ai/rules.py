import logging
from typing import Dict, Any, Tuple

from app.ai.fusion.config import config

logger = logging.getLogger(__name__)


class RuleEngine:
    """
    Deterministic rule engine to detect honeypot candidates and keyword stuffers.
    Reads thresholds and penalties from fusion config.
    """

    def __init__(self):
        self.business_rules = config.get("business_rules", {})
        self.rules = config.get("rules", {})

    def detect_honeypot(self, candidate: Dict[str, Any]) -> bool:
        return bool(candidate.get("honeypot_triggered", False))

    def detect_keyword_stuffer(self, candidate: Dict[str, Any]) -> bool:
        return bool(candidate.get("keyword_stuffer_flag", False))

    def apply_rules(self, candidate: Dict[str, Any], current_score: float) -> Tuple[float, list]:
        flags = []
        score = current_score

        ce_score = candidate.get("cross_encoder_score", candidate.get("semantic_score", 0.0))
        skill_score = candidate.get("skill_match_score", 0.0)
        disparity_threshold = self.rules.get("keyword_stuffer_threshold_disparity", 40.0)

        if self.detect_honeypot(candidate):
            honeypot_penalty = self.rules.get("honeypot_penalty", 100.0)
            score -= honeypot_penalty
            flags.append("HONEYPOT_DETECTED")
            logger.warning("Honeypot detected for candidate %s", candidate.get("candidate_id"))

        elif abs(ce_score - skill_score) > disparity_threshold or self.detect_keyword_stuffer(candidate):
            keyword_stuffer_penalty = self.rules.get("keyword_stuffer_penalty", 20.0)
            score -= keyword_stuffer_penalty
            flags.append("KEYWORD_STUFFER")
            logger.warning("Keyword stuffer suspected for candidate %s", candidate.get("candidate_id"))

        return score, flags
