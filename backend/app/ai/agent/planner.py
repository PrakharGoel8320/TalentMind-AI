"""Maps recruiter intent to a bounded tool execution plan."""
from typing import Any, Dict, List, Optional

from app.ai.agent.intent import (
    INTENT_ACTION,
    INTENT_COMPARISON,
    INTENT_EXPLANATION,
    INTENT_GENERAL,
    INTENT_MULTI_STEP,
    INTENT_RANKING,
    INTENT_RETRIEVAL,
)


def create_plan(intent: str, session_state: Optional[Dict[str, Any]] = None) -> List[str]:
    """
    Return an ordered list of tool names to execute.
    Uses session context to skip redundant steps when possible.
    """
    session_state = session_state or {}
    has_ranked = bool(session_state.get("last_ranked_candidates"))

    if intent == INTENT_RETRIEVAL:
        return ["get_job_context_tool", "retrieve_candidates_tool"]

    if intent == INTENT_RANKING:
        if has_ranked:
            return ["get_job_context_tool", "explain_candidate_tool"]
        return ["get_job_context_tool", "retrieve_candidates_tool", "rank_candidates_pipeline_tool"]

    if intent == INTENT_EXPLANATION:
        if has_ranked:
            return ["get_job_context_tool", "explain_candidate_tool"]
        return ["get_job_context_tool", "retrieve_candidates_tool", "rank_candidates_pipeline_tool", "explain_candidate_tool"]

    if intent == INTENT_COMPARISON:
        if has_ranked:
            return ["get_job_context_tool", "compare_candidates_tool"]
        return [
            "get_job_context_tool",
            "retrieve_candidates_tool",
            "rank_candidates_pipeline_tool",
            "compare_candidates_tool",
        ]

    if intent == INTENT_ACTION:
        if has_ranked:
            return ["get_job_context_tool", "explain_candidate_tool", "propose_action_tool"]
        return [
            "get_job_context_tool",
            "retrieve_candidates_tool",
            "rank_candidates_pipeline_tool",
            "explain_candidate_tool",
            "propose_action_tool",
        ]

    if intent == INTENT_MULTI_STEP:
        return [
            "get_job_context_tool",
            "retrieve_candidates_tool",
            "rank_candidates_pipeline_tool",
            "compare_candidates_tool",
            "explain_candidate_tool",
            "propose_action_tool",
        ]

    # general / fallback
    if has_ranked:
        return ["get_job_context_tool", "compare_candidates_tool", "explain_candidate_tool"]
    return ["get_job_context_tool", "retrieve_candidates_tool", "rank_candidates_pipeline_tool", "explain_candidate_tool"]
