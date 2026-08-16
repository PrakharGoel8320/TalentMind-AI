"""Deterministic intent classification for recruiter requests."""
import re
from typing import List


INTENT_RETRIEVAL = "retrieval"
INTENT_RANKING = "ranking"
INTENT_EXPLANATION = "explanation"
INTENT_COMPARISON = "comparison"
INTENT_ACTION = "action"
INTENT_MULTI_STEP = "multi_step"
INTENT_GENERAL = "general"


def classify_intent(request: str) -> str:
    text = (request or "").lower()

    has_action = bool(re.search(r"\b(email|contact|reach out|send|message|invite|prepare an email|draft)\b", text))
    has_compare = bool(re.search(r"\b(compare|comparison|top three|top 3|versus|vs\.?)\b", text))
    has_explain = bool(re.search(r"\b(why|explain|reason|ranked above|ranked #|how come)\b", text))
    has_rank = bool(re.search(r"\b(rank|ranking|best candidate|strongest|top candidate|score)\b", text))
    has_retrieve = bool(re.search(r"\b(find|search|retrieve|look for|candidates for)\b", text))

    if has_action and (has_compare or has_rank or has_retrieve):
        return INTENT_MULTI_STEP
    if has_action:
        return INTENT_ACTION
    if has_compare:
        return INTENT_COMPARISON
    if has_explain:
        return INTENT_EXPLANATION
    if has_rank:
        return INTENT_RANKING
    if has_retrieve:
        return INTENT_RETRIEVAL
    return INTENT_GENERAL
