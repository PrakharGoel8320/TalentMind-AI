from fastapi import APIRouter, Depends
from typing import Dict, Any
import structlog
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from app.database.session import get_db
from app.database.redis import get_redis
from app.database.neo4j_client import get_neo4j
from app.ai.retrieval.embedder import Embedder
from app.ai.ranking.ranker import SemanticRanker
import os

logger = structlog.get_logger(__name__)
router = APIRouter()

@router.get("/health", response_model=Dict[str, Any])
async def health_check(
    db: AsyncSession = Depends(get_db),
    redis = Depends(get_redis),
    neo4j = Depends(get_neo4j)
) -> Dict[str, Any]:
    """Check connections to all core backend services."""
    status_report = {"status": "healthy", "dependencies": {}}
    
    # 1. Postgres Check
    try:
        await db.execute(text("SELECT 1"))
        status_report["dependencies"]["postgres"] = "healthy"
    except Exception as e:
        logger.error("healthcheck_postgres_failed", error=str(e))
        status_report["status"] = "degraded"
        status_report["dependencies"]["postgres"] = "unhealthy"
        
    # 2. Redis Check
    try:
        import asyncio
        await asyncio.wait_for(redis.ping(), timeout=2.0)
        status_report["dependencies"]["redis"] = "healthy"
    except Exception as e:
        logger.error("healthcheck_redis_failed", error=str(e))
        status_report["status"] = "degraded"
        status_report["dependencies"]["redis"] = "unhealthy"

    # 3. Neo4j Check
    try:
        import asyncio
        await asyncio.wait_for(neo4j.verify_connectivity(), timeout=2.0)
        status_report["dependencies"]["neo4j"] = "healthy"
    except Exception as e:
        logger.error("healthcheck_neo4j_failed", error=str(e))
        status_report["status"] = "degraded"
        status_report["dependencies"]["neo4j"] = "unhealthy"
        
    return status_report

@router.get("/pipeline/status", response_model=Dict[str, Any])
async def pipeline_status():
    """
    Returns specific telemetry for the ML/FAISS pipeline status.
    """
    from app.ai.retrieval.embedder import Embedder
    from app.ai.ranking.ranker import SemanticRanker
    from app.ai.cache import CacheManager  
    
    embedder = Embedder.get_instance()
    ranker = SemanticRanker.get_instance()
    cache = CacheManager.get_instance()
    
    models = []
    if getattr(embedder, "model", None):
        models.append("sentence-transformers")
    if getattr(ranker, "model", None):
        models.append("cross-encoder")
        
    return {
        "status": "online",
        "models_loaded": models,
        "cache_items": len(cache.memory_cache)
    }


@router.get("/readiness", response_model=Dict[str, Any])
async def readiness_check(
    db: AsyncSession = Depends(get_db),
    redis=Depends(get_redis),
    neo4j=Depends(get_neo4j),
) -> Dict[str, Any]:
    """
    Readiness probe that distinguishes required vs optional dependencies.
    Required: app process, database, and core ML model initialization.
    Optional: redis, neo4j, and non-mock LLM provider availability.
    """
    report: Dict[str, Any] = {
        "status": "ready",
        "required": {
            "app": "ready",
            "database": "unknown",
            "ml_models": "unknown",
        },
        "optional": {
            "redis": "unknown",
            "neo4j": "unknown",
            "llm": "unknown",
        },
    }

    # Required: database
    try:
        await db.execute(text("SELECT 1"))
        report["required"]["database"] = "ready"
    except Exception as e:
        logger.error("readiness_database_failed", error=str(e))
        report["required"]["database"] = "not_ready"
        report["status"] = "not_ready"

    # Required: ML models can initialize
    try:
        embedder = Embedder.get_instance()
        ranker = SemanticRanker.get_instance()
        if getattr(embedder, "model", None) and getattr(ranker, "model", None):
            report["required"]["ml_models"] = "ready"
        else:
            report["required"]["ml_models"] = "not_ready"
            report["status"] = "not_ready"
    except Exception as e:
        logger.error("readiness_ml_failed", error=str(e))
        report["required"]["ml_models"] = "not_ready"
        report["status"] = "not_ready"

    # Optional: redis
    try:
        await redis.ping()
        report["optional"]["redis"] = "ready"
    except Exception as e:
        logger.warning("readiness_redis_unavailable", error=str(e))
        report["optional"]["redis"] = "unavailable"

    # Optional: neo4j
    try:
        await neo4j.verify_connectivity()
        report["optional"]["neo4j"] = "ready"
    except Exception as e:
        logger.warning("readiness_neo4j_unavailable", error=str(e))
        report["optional"]["neo4j"] = "unavailable"

    # Optional: LLM provider
    provider = (os.getenv("LLM_PROVIDER", "mock") or "mock").lower()
    if provider == "mock":
        report["optional"]["llm"] = "mock"
    elif provider == "openai" and os.getenv("OPENAI_API_KEY"):
        report["optional"]["llm"] = "configured"
    elif provider == "ollama":
        report["optional"]["llm"] = "configured"
    else:
        report["optional"]["llm"] = "not_configured"

    return report
