import asyncio
import logging
from typing import List, Dict, Any
from langchain_core.tools import tool

from app.ai.retrieval.service import RetrievalService
from app.ai.feature_extraction import FeatureExtractionService
from app.ai.ranking.service import RankingService
from app.ai.behavioral.service import BehavioralService
from app.ai.fusion.service import FusionService
from app.ai.rules import RuleEngine
from app.ai.agent.explainability import explain_candidate, compare_candidates
from app.database.session import AsyncSessionLocal
from sqlalchemy import select, func
from app.models.candidate import Candidate
from app.models.job import Job

logger = logging.getLogger(__name__)

# Initialize singletons for tools
_retrieval_service = None
_feature_extractor = None
_ranking_service = None
_behavioral_service = None
_fusion_service = None
_rule_engine = None

def get_retrieval_service():
    global _retrieval_service
    if _retrieval_service is None:
        _retrieval_service = RetrievalService()
    return _retrieval_service

def get_feature_extractor():
    global _feature_extractor
    if _feature_extractor is None:
        _feature_extractor = FeatureExtractionService()
    return _feature_extractor

def get_ranking_service():
    global _ranking_service
    if _ranking_service is None:
        _ranking_service = RankingService()
    return _ranking_service

def get_behavioral_service():
    global _behavioral_service
    if _behavioral_service is None:
        _behavioral_service = BehavioralService()
    return _behavioral_service

def get_fusion_service():
    global _fusion_service
    if _fusion_service is None:
        _fusion_service = FusionService()
    return _fusion_service

def get_rule_engine():
    global _rule_engine
    if _rule_engine is None:
        _rule_engine = RuleEngine()
    return _rule_engine

@tool
def retrieve_candidates_tool(job_description: str, top_k: int = 20) -> List[Dict[str, Any]]:
    """
    Retrieve top candidate IDs from the semantic FAISS index based on the job description, 
    and fetch their raw profile data from the database.
    """
    retrieval = get_retrieval_service()
    results = retrieval.search_candidates(job_description, top_k=top_k)
    
    if not results:
        return []
        
    candidate_ids = [res["candidate_id"] for res in results]
    scores_map = {res["candidate_id"]: res["score"] * 100 for res in results}
    
    async def fetch_candidates():
        async with AsyncSessionLocal() as db:
            stmt = select(Candidate).filter(Candidate.id.in_(candidate_ids))
            res = await db.execute(stmt)
            return res.scalars().all()
            
    try:
        db_candidates = asyncio.run(fetch_candidates())
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        db_candidates = loop.run_until_complete(fetch_candidates())
        loop.close()
        
    hydrated = []
    found_ids = set()
    for cand in db_candidates:
        c_id = str(cand.id)
        found_ids.add(c_id)
        hydrated.append({
            "candidate_id": c_id,
            "embedding_score": scores_map.get(c_id, 0.0),
            "profile": cand.profile_jsonb or {},
            "behavioral_metrics": {}
        })
        
    for res in results:
        if str(res["candidate_id"]) not in found_ids:
            hydrated.append({
                "candidate_id": str(res["candidate_id"]),
                "embedding_score": res["score"] * 100,
                "profile": {},
                "behavioral_metrics": {}
            })
    return hydrated

@tool
def analyze_features_tool(job_description: str, candidates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Extract deterministic features (skill match, experience scores) for a list of candidates 
    based on the job description.
    """
    extractor = get_feature_extractor()
    return extractor.extract_features(candidates, job_description)

@tool
def rank_candidates_tool(job_description: str, candidates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Apply Cross-Encoder semantic ranking to candidate profiles against the job description.
    """
    ranking = get_ranking_service()
    return ranking.rank_candidates(job_description, candidates)

@tool
def analyze_behavior_tool(candidates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Analyze behavioral metrics and apply rule engine penalties (e.g. keyword stuffing) 
    to candidates.
    """
    rule_engine = get_rule_engine()
    behavioral = get_behavioral_service()
    
    # 1. Apply rules
    filtered_candidates = []
    for cand in candidates:
        _, flags = rule_engine.apply_rules(cand, 0.0)
        cand["flags"] = cand.get("flags", []) + flags
        if "HONEYPOT_DETECTED" in flags:
            cand["dropped"] = True
            
    filtered = [c for c in candidates if not c.get("dropped", False)]
    
    # 2. Behavioral Scoring
    return behavioral.score_candidates(filtered)

@tool
def finalize_and_fuse_tool(candidates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Apply final semantic fusion, business rules, penalties, and tie breakers to produce the official final ranking.
    Pass the candidates list returned by analyze_behavior_tool exactly as-is.
    """
    fused_candidates = get_fusion_service().rank_candidates(candidates)
    return fused_candidates

from typing import Optional

@tool
def propose_action_tool(action_type: str, target_id: str, reason: str, payload: Dict[str, Any], job_id: Optional[str] = None) -> str:
    """
    Proposes an action to be taken (e.g., "EMAIL_CANDIDATE").
    The action is saved in a PENDING_APPROVAL state.
    A human must review and approve it before execution can occur.
    """
    import asyncio
    from app.database.session import AsyncSessionLocal
    from app.models.action import ActionProposal
    from app.models.enums import ActionType
    
    async def _save_action():
        async with AsyncSessionLocal() as session:
            try:
                action_enum = ActionType(action_type)
            except ValueError:
                return f"Invalid action_type: {action_type}. Allowed: {[e.value for e in ActionType]}"
            
            proposal = ActionProposal(
                job_id=job_id,
                action_type=action_enum,
                target_id=target_id,
                reason=reason,
                payload=payload
            )
            session.add(proposal)
            await session.commit()
            return f"Action {action_type} proposed for target {target_id}. Status is PENDING_APPROVAL. Execution is paused waiting for human approval."
    
    # Run async function in sync tool
    loop = asyncio.get_event_loop()
    if loop.is_running():
        # This occurs if called from an async context like FastAPI
        import nest_asyncio
        nest_asyncio.apply()
    
    # We must use asyncio.run to execute the coroutine if no event loop, 
    # but since this might be run in an async context by LangGraph's asyncio.to_thread,
    # we can use a helper or just run it.
    try:
        return asyncio.run(_save_action())
    except RuntimeError:
        # Event loop is running in thread
        import nest_asyncio
        nest_asyncio.apply()
        return asyncio.run(_save_action())


@tool
def get_job_context_tool(job_id: str) -> Dict[str, Any]:
    """
    Return real job context from the database: title, description, required skills, and candidate count.
    """
    import asyncio
    from app.ai.feature_extraction import COMMON_SKILLS

    async def _fetch():
        async with AsyncSessionLocal() as db:
            job_res = await db.execute(select(Job).filter(Job.id == job_id))
            job = job_res.scalars().first()
            if not job:
                return {"error": "Job not found", "job_id": job_id}
            count_res = await db.execute(select(func.count()).select_from(Candidate))
            candidate_count = count_res.scalar() or 0
            jd_lower = (job.description or "").lower()
            required_skills = sorted({s for s in COMMON_SKILLS if s in jd_lower})
            return {
                "job_id": str(job.id),
                "title": job.title,
                "description": job.description or "",
                "department": job.department,
                "location": job.location,
                "required_skills": required_skills,
                "candidate_count": candidate_count,
            }

    try:
        return asyncio.run(_fetch())
    except RuntimeError:
        import nest_asyncio
        nest_asyncio.apply()
        return asyncio.run(_fetch())


@tool
def rank_candidates_pipeline_tool(job_id: str, job_description: str, top_k: int = 20) -> List[Dict[str, Any]]:
    """
    Run the full deterministic ranking pipeline: feature extraction, cross-encoder,
    behavioral scoring, and fusion. Returns real ranked candidates with scores.
    """
    from app.ai.orchestrator import AIOrchestrator
    orchestrator = AIOrchestrator()
    result = orchestrator.process_job(job_id, job_description, top_k=top_k)
    return result.get("results", [])


@tool
def compare_candidates_tool(candidates: List[Dict[str, Any]], top_n: int = 3) -> Dict[str, Any]:
    """
    Compare top candidates using actual pipeline scores and return structured comparison.
    """
    return compare_candidates(candidates, top_n=top_n)


@tool
def explain_candidate_tool(candidate: Dict[str, Any], rank_position: int = 1) -> Dict[str, Any]:
    """
    Return structured evidence-based explanation for a candidate using real pipeline scores.
    """
    return explain_candidate(candidate, rank_position=rank_position)
