"""Deterministic bounded agent execution with intent-based tool selection."""
import json
import time
from typing import Any, Dict, List, Optional

import structlog

from app.core.config import settings
from app.ai.agent.intent import classify_intent, INTENT_ACTION, INTENT_MULTI_STEP
from app.ai.agent.planner import create_plan
from app.ai.agent import activity as act
from app.ai.agent.explainability import explain_candidate, compare_candidates
from app.ai.orchestrator import AIOrchestrator

logger = structlog.get_logger(__name__)


class AgentExecutionContext:
    def __init__(self, job_id: str, job_description: str, job_title: str, request: str, session_state: Dict[str, Any]):
        self.job_id = job_id
        self.job_description = job_description
        self.job_title = job_title
        self.request = request
        self.session_state = session_state
        self.events: List[Dict[str, Any]] = []
        self.errors: List[str] = []
        self.tool_call_count = 0
        self.retrieved_candidates: List[Dict[str, Any]] = []
        self.ranked_candidates: List[Dict[str, Any]] = []
        self.comparison: Optional[Dict[str, Any]] = None
        self.explanation: Optional[Dict[str, Any]] = None
        self.recommendation: Optional[Dict[str, Any]] = None
        self.proposed_action: Optional[Dict[str, Any]] = None
        self.job_context: Optional[Dict[str, Any]] = None
        self.metrics: Dict[str, Any] = {}


def _get_job_context(ctx: AgentExecutionContext) -> Dict[str, Any]:
    from app.ai.feature_extraction import COMMON_SKILLS

    jd_lower = ctx.job_description.lower()
    required_skills = sorted({s for s in COMMON_SKILLS if s in jd_lower})
    return {
        "job_id": ctx.job_id,
        "title": ctx.job_title,
        "description": ctx.job_description,
        "required_skills": required_skills,
        "candidate_count": len(ctx.ranked_candidates) or len(ctx.retrieved_candidates),
    }


def _run_retrieval(ctx: AgentExecutionContext, top_k: int = 20) -> List[Dict[str, Any]]:
    from app.ai.agent.tools import retrieve_candidates_tool

    t0 = time.perf_counter()
    result = retrieve_candidates_tool.invoke({"job_description": ctx.job_description, "top_k": top_k})
    ctx.metrics["retrieval_latency_ms"] = round((time.perf_counter() - t0) * 1000, 2)
    ctx.retrieved_candidates = result
    ctx.events.append(act.event_candidates_retrieved(len(result)))
    return result


def _run_ranking_pipeline(ctx: AgentExecutionContext, top_k: int = 20) -> List[Dict[str, Any]]:
    t0 = time.perf_counter()
    orchestrator = AIOrchestrator()
    result = orchestrator.process_job(ctx.job_id, ctx.job_description, top_k=top_k)
    ctx.metrics["ranking_latency_ms"] = round((time.perf_counter() - t0) * 1000, 2)
    ctx.metrics["phase_timings"] = result.get("phase_timings", {})
    ctx.metrics["total_pipeline_latency_ms"] = result.get("total_time_ms", 0)
    if result.get("errors"):
        ctx.errors.extend(result["errors"])
    ranked = result.get("results", [])
    ctx.ranked_candidates = ranked
    ctx.events.append(act.event_ranking_completed(len(ranked)))
    return ranked


def _run_compare(ctx: AgentExecutionContext, top_n: int = 3) -> Dict[str, Any]:
    candidates = ctx.ranked_candidates or ctx.session_state.get("last_ranked_candidates") or []
    comparison = compare_candidates(candidates, top_n=top_n)
    ctx.comparison = comparison
    ctx.events.append(act.event_comparison_completed(comparison.get("candidates_compared", 0)))
    if comparison.get("recommended_candidate_id"):
        top = comparison["comparisons"][0] if comparison.get("comparisons") else {}
        ctx.recommendation = {
            "candidate_id": comparison["recommended_candidate_id"],
            "name": top.get("name"),
            "score": top.get("final_score"),
            "summary": comparison.get("recommendation", ""),
        }
        ctx.events.append(
            act.event_recommendation_generated(
                comparison["recommended_candidate_id"],
                top.get("final_score", 0),
            )
        )
    return comparison


def _run_explain(ctx: AgentExecutionContext) -> Dict[str, Any]:
    candidates = ctx.ranked_candidates or ctx.session_state.get("last_ranked_candidates") or []
    if not candidates:
        return {}
    top = sorted(candidates, key=lambda c: c.get("final_score", 0), reverse=True)[0]
    explanation = explain_candidate(top, rank_position=1)
    ctx.explanation = explanation
    ctx.recommendation = {
        "candidate_id": explanation["candidate_id"],
        "name": explanation["name"],
        "score": explanation["overall_score"],
        "summary": explanation["why_ranked"],
        "matched_skills": explanation["matched_skills"],
        "missing_skills": explanation["missing_skills"],
    }
    ctx.events.append(
        act.event_recommendation_generated(explanation["candidate_id"], explanation["overall_score"])
    )
    return explanation


def _run_propose_action(ctx: AgentExecutionContext) -> Dict[str, Any]:
    from app.ai.agent.tools import propose_action_tool

    candidates = ctx.ranked_candidates or ctx.session_state.get("last_ranked_candidates") or []
    if not candidates:
        ctx.errors.append("No ranked candidates available to propose an action.")
        return {}

    top = sorted(candidates, key=lambda c: c.get("final_score", 0), reverse=True)[0]
    exp = explain_candidate(top, rank_position=1)
    recipient = exp.get("email") or f"candidate-{str(exp.get('candidate_id', ''))[:8]}@example.com"
    job_title = ctx.job_title or "the open role"
    payload = {
        "recipient": recipient,
        "subject": f"Opportunity: {job_title}",
        "body": (
            f"Hello {exp.get('name', 'Candidate')},\n\n"
            f"We reviewed your profile for our {job_title} position and would like to connect.\n"
            f"Your profile scored {exp.get('overall_score', 0):.1f} in our deterministic ranking pipeline.\n\n"
            f"Best regards,\nTalentMind Recruiting Team"
        ),
    }
    result_msg = propose_action_tool.invoke({
        "action_type": "EMAIL_CANDIDATE",
        "target_id": str(exp.get("candidate_id")),
        "reason": f"Top ranked candidate (score {exp.get('overall_score', 0):.1f}) for {job_title}",
        "payload": payload,
        "job_id": ctx.job_id,
    })
    proposed = {
        "action_type": "EMAIL_CANDIDATE",
        "target_id": str(exp.get("candidate_id")),
        "status": "PENDING_APPROVAL",
        "payload": payload,
        "message": result_msg,
    }
    ctx.proposed_action = proposed
    ctx.events.append(act.event_action_proposed("EMAIL_CANDIDATE"))
    ctx.events.append(act.event_waiting_approval())
    return proposed


def execute_planned_workflow(
    job_id: str,
    job_description: str,
    job_title: str,
    request: str,
    session_state: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Deterministic intent-based agent workflow with bounded tool execution.
    Used for mock LLM mode and as the reliable demo path.
    """
    session_state = session_state or {}
    ctx = AgentExecutionContext(job_id, job_description, job_title, request, session_state)

    t_start = time.perf_counter()
    intent = classify_intent(request)
    plan = create_plan(intent, session_state)

    ctx.events.append(act.event_request_received(request))
    ctx.events.append(act.event_intent_identified(intent))

    tool_handlers = {
        "get_job_context_tool": lambda: _get_job_context(ctx),
        "retrieve_candidates_tool": lambda: _run_retrieval(ctx),
        "rank_candidates_pipeline_tool": lambda: _run_ranking_pipeline(ctx),
        "compare_candidates_tool": lambda: _run_compare(ctx),
        "explain_candidate_tool": lambda: _run_explain(ctx),
        "propose_action_tool": lambda: _run_propose_action(ctx),
    }

    max_steps = settings.MAX_AGENT_STEPS
    for tool_name in plan[:max_steps]:
        if ctx.tool_call_count >= max_steps:
            ctx.errors.append(f"Maximum agent steps ({max_steps}) reached.")
            break

        handler = tool_handlers.get(tool_name)
        if not handler:
            continue

        ctx.events.append(act.event_tool_selected(tool_name))
        t0 = time.perf_counter()
        try:
            result = handler()
            duration_ms = round((time.perf_counter() - t0) * 1000, 2)
            ctx.tool_call_count += 1

            detail: Dict[str, Any] = {"duration_ms": duration_ms}
            if tool_name == "get_job_context_tool":
                ctx.job_context = result
                ctx.events.append(act.event_job_context_loaded(result.get("title", "Job")))
                detail["required_skills"] = len(result.get("required_skills", []))
            elif tool_name == "retrieve_candidates_tool":
                detail["result_count"] = len(result) if isinstance(result, list) else 0
            elif tool_name == "rank_candidates_pipeline_tool":
                detail["result_count"] = len(result) if isinstance(result, list) else 0
            elif tool_name == "compare_candidates_tool":
                detail["result_count"] = result.get("candidates_compared", 0) if isinstance(result, dict) else 0

            ctx.events.append(act.event_tool_completed(tool_name, status="success", **detail))
            logger.info("tool_execution", tool=tool_name, status="success", duration_ms=duration_ms, **detail)
        except Exception as e:
            ctx.errors.append(f"{tool_name} failed: {str(e)}")
            ctx.events.append(act.event_tool_completed(tool_name, status="error", error=str(e)))
            logger.error("tool_execution", tool=tool_name, status="error", error=str(e))

    ctx.metrics["agent_execution_time_ms"] = round((time.perf_counter() - t_start) * 1000, 2)
    ctx.metrics["agent_tool_calls"] = ctx.tool_call_count
    ctx.metrics["intent"] = intent

    # Build human-readable explanation from structured results
    explanation_text = _build_explanation_text(ctx, intent)

    status = "completed"
    if ctx.proposed_action:
        status = "proposed_action"
    if ctx.errors:
        status = "error" if not ctx.ranked_candidates and not ctx.recommendation else "completed_with_errors"

    return {
        "job_id": job_id,
        "status": status,
        "intent": intent,
        "explanation": explanation_text,
        "candidates": ctx.ranked_candidates or ctx.retrieved_candidates,
        "activity": ctx.events,
        "recommendation": ctx.recommendation,
        "comparison": ctx.comparison,
        "explanation_detail": ctx.explanation,
        "proposed_action": ctx.proposed_action,
        "errors": ctx.errors,
        "metrics": ctx.metrics,
        "session_state_updates": {
            "job_id": job_id,
            "last_intent": intent,
            "last_candidate_ids": [c.get("candidate_id") for c in (ctx.ranked_candidates or ctx.retrieved_candidates)],
            "last_ranked_candidates": ctx.ranked_candidates[:10] if ctx.ranked_candidates else session_state.get("last_ranked_candidates", [])[:10],
            "last_analysis": explanation_text[:500],
            "conversation_summary": request[:200],
        },
    }


def _build_explanation_text(ctx: AgentExecutionContext, intent: str) -> str:
    parts: List[str] = []
    if ctx.job_context:
        parts.append(f"**Job:** {ctx.job_context.get('title', 'Unknown')}")
        skills = ctx.job_context.get("required_skills") or []
        if skills:
            parts.append(f"**Required skills detected:** {', '.join(skills[:8])}")

    if ctx.ranked_candidates:
        parts.append(f"**Ranked {len(ctx.ranked_candidates)} candidates** using the deterministic pipeline (FAISS → features → cross-encoder → behavioral → fusion).")

    if ctx.recommendation:
        rec = ctx.recommendation
        parts.append(
            f"\n**Recommended Candidate:** {rec.get('name', 'Unknown')}\n"
            f"**Score:** {rec.get('score', 0):.1f}\n"
            f"**Why:** {rec.get('summary', 'Top pipeline score.')}"
        )
        if rec.get("matched_skills"):
            parts.append(f"**Matched skills:** {', '.join(rec['matched_skills'][:6])}")
        if rec.get("missing_skills"):
            parts.append(f"**Missing skills:** {', '.join(rec['missing_skills'][:4])}")

    if ctx.comparison and ctx.comparison.get("comparisons"):
        parts.append("\n**Comparison (top candidates):**")
        for c in ctx.comparison["comparisons"]:
            parts.append(
                f"- {c['name']}: final {c['final_score']:.1f} | skill {c['skill_match_score']:.1f} | "
                f"semantic {c['semantic_relevance']:.1f} | exp {c['experience_score']:.1f} | "
                f"behavior {c['behavioral_score']:.1f}"
            )
        if ctx.comparison.get("recommendation"):
            parts.append(f"\n{ctx.comparison['recommendation']}")

    if ctx.proposed_action:
        pa = ctx.proposed_action
        parts.append(
            f"\n**Proposed Action:** {pa['action_type']} → {pa['payload'].get('recipient')}\n"
            f"Status: **PENDING_APPROVAL** — review in the Approvals queue."
        )

    if ctx.errors:
        parts.append("\n**Warnings:** " + "; ".join(ctx.errors))

    if not parts:
        parts.append("Request processed. No candidates were retrieved — ensure candidates exist and FAISS index is populated.")

    return "\n".join(parts)
