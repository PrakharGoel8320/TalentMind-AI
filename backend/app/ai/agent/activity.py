"""Safe structured activity events for the agent UI (no chain-of-thought)."""
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
import uuid


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def make_event(event_type: str, message: str, **details: Any) -> Dict[str, Any]:
    return {
        "id": str(uuid.uuid4()),
        "type": event_type,
        "message": message,
        "timestamp": _now_iso(),
        **details,
    }


def event_request_received(request: str) -> Dict[str, Any]:
    return make_event("request_received", f'Request received: "{request[:120]}"', request=request)


def event_intent_identified(intent: str) -> Dict[str, Any]:
    return make_event("intent_identified", f"Intent identified: {intent}", intent=intent)


def event_tool_selected(tool: str) -> Dict[str, Any]:
    return make_event("tool_selected", f"Tool selected: {tool}", tool=tool)


def event_tool_completed(tool: str, status: str = "success", **details: Any) -> Dict[str, Any]:
    return make_event("tool_completed", f"Tool completed: {tool}", tool=tool, status=status, **details)


def event_candidates_retrieved(count: int) -> Dict[str, Any]:
    return make_event("candidates_retrieved", f"FAISS retrieved {count} candidates", count=count)


def event_ranking_completed(count: int) -> Dict[str, Any]:
    return make_event("ranking_completed", f"Deterministic ranking completed for {count} candidates", count=count)


def event_comparison_completed(count: int) -> Dict[str, Any]:
    return make_event("comparison_completed", f"Top {count} candidates compared", count=count)


def event_recommendation_generated(candidate_id: str, score: float) -> Dict[str, Any]:
    return make_event(
        "recommendation_generated",
        f"Recommendation generated for candidate {candidate_id[:8]}",
        candidate_id=candidate_id,
        score=score,
    )


def event_action_proposed(action_type: str) -> Dict[str, Any]:
    return make_event("action_proposed", f"Action proposed: {action_type}", action_type=action_type)


def event_waiting_approval() -> Dict[str, Any]:
    return make_event("waiting_for_approval", "Waiting for human approval")


def event_job_context_loaded(title: str) -> Dict[str, Any]:
    return make_event("job_context_loaded", f"Job context loaded: {title}", job_title=title)


def append_events(events: List[Dict[str, Any]], new_events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return events + new_events
