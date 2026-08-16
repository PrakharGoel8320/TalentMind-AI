from typing import TypedDict, Annotated, Sequence, Any, List, Dict, Optional
from langchain_core.messages import BaseMessage
import operator


class AgentState(TypedDict):
    job_id: str
    job_description: str
    job_title: str
    recruiter_request: str
    messages: Annotated[Sequence[BaseMessage], operator.add]
    intent: str
    activity_events: List[Dict[str, Any]]
    retrieved_candidates: List[Dict[str, Any]]
    ranked_candidates: List[Dict[str, Any]]
    final_ranking: List[Dict[str, Any]]
    recommendation: Optional[Dict[str, Any]]
    proposed_action: Optional[Dict[str, Any]]
    explanation: str
    status: str
    errors: List[str]
    tool_call_count: int
