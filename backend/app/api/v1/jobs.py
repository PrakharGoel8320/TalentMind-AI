from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database.session import get_db
from app.core.auth import get_current_user, UserContext
from app.schemas.job import JobCreate, JobResponse
from app.schemas.match import MatchResponse
from app.models.job import Job
from app.models.match import Match
from app.ai.orchestrator import AIOrchestrator
import uuid
from app.utils.logger import get_logger

router = APIRouter(prefix="/jobs", tags=["jobs"])
logger = get_logger("app.api.v1.jobs")


@router.post("/", response_model=JobResponse)
async def create_job(
    job_in: JobCreate,
    db: AsyncSession = Depends(get_db),
    current_user: UserContext = Depends(get_current_user)
):
    job = Job(**job_in.model_dump())
    db.add(job)
    await db.commit()
    await db.refresh(job)
    return job

async def run_ranking_pipeline_task(job_id: uuid.UUID, job_description: str):
    from app.database.session import AsyncSessionLocal
    import asyncio
    from sqlalchemy import delete
    try:
        orchestrator = AIOrchestrator()
        logger.info("ranking_background_started", job_id=str(job_id))
        result = await asyncio.to_thread(orchestrator.process_job, str(job_id), job_description, 100)
        results_list = result.get("results", [])
        logger.info("ranking_background_orchestrator_done", job_id=str(job_id), total_candidates=len(results_list))
        async with AsyncSessionLocal() as db:
            await db.execute(delete(Match).where(Match.job_id == job_id))
            for rank, cand in enumerate(results_list):
                try:
                    c_str = cand["candidate_id"]
                    # Skip mock candidates from Kaggle dataset that don't exist in our DB
                    if isinstance(c_str, str) and c_str.startswith("CAND_"):
                        continue

                    if isinstance(c_str, str):
                        cand_id = uuid.UUID(c_str)
                    else:
                        cand_id = c_str
                        
                    match = Match(
                        job_id=job_id,
                        candidate_id=cand_id,
                        final_score=cand.get("final_score", cand.get("embedding_score", 0.0)),
                        score_components={
                            "cross_encoder_score": cand.get("cross_encoder_score", cand.get("semantic_score", 0.0)),
                            "embedding_score": cand.get("embedding_score", 0.0),
                            "skill_match_score": cand.get("skill_match_score", 0.0),
                            "experience_score": cand.get("experience_score", 0.0),
                            "behavior_score": cand.get("behavioral_score", 0.0),
                        },
                        flags=cand.get("flags", [])
                    )
                    db.add(match)
                except Exception as ex:
                    logger.warning(
                        "ranking_candidate_skipped",
                        job_id=str(job_id),
                        candidate_id=str(cand.get("candidate_id")),
                        error=str(ex),
                    )
            await db.commit()
            logger.info("ranking_background_saved", job_id=str(job_id))
    except Exception as e:
        logger.error("ranking_background_failed", job_id=str(job_id), error=str(e))

@router.post("/{job_id}/rank")
async def rank_candidates(
    job_id: uuid.UUID,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: UserContext = Depends(get_current_user)
):
    """
    Triggers the AI Orchestrator to rank candidates for this job and persist Match objects.
    Runs as a background task.
    """
    result = await db.execute(select(Job).filter(Job.id == job_id))
    job = result.scalars().first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    background_tasks.add_task(run_ranking_pipeline_task, job_id, job.description or "Senior Backend Engineer")
    
    return {
        "status": "processing", 
        "message": "Ranking job started in the background."
    }

@router.get("/{job_id}", response_model=JobResponse)
async def get_job(
    job_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: UserContext = Depends(get_current_user),
):
    result = await db.execute(select(Job).filter(Job.id == job_id))
    job = result.scalars().first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job

@router.put("/{job_id}", response_model=JobResponse)
async def update_job(
    job_id: uuid.UUID,
    job_in: dict,
    db: AsyncSession = Depends(get_db),
    current_user: UserContext = Depends(get_current_user),
):
    result = await db.execute(select(Job).filter(Job.id == job_id))
    job = result.scalars().first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    for key, value in job_in.items():
        if hasattr(job, key):
            setattr(job, key, value)
    await db.commit()
    await db.refresh(job)
    return job

@router.delete("/{job_id}")
async def delete_job(
    job_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: UserContext = Depends(get_current_user),
):
    result = await db.execute(select(Job).filter(Job.id == job_id))
    job = result.scalars().first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    await db.delete(job)
    await db.commit()
    return {"status": "deleted"}

@router.post("/extract-requirements")
async def extract_requirements(file: UploadFile = File(...)):
    try:
        content = await file.read()
        text = content.decode("utf-8", errors="ignore").lower()
        
        from app.ai.feature_extraction import COMMON_SKILLS
        extracted_skills = [skill for skill in COMMON_SKILLS if skill in text]
        
        return {"skills": extracted_skills if extracted_skills else ["Communication", "Problem Solving"]}
    except Exception as e:
        return {"skills": []}

@router.post("/{job_id}/match")
async def match_job(job_id: uuid.UUID):
    return {"status": "ok"}

@router.get("/{job_id}/matches", response_model=list[MatchResponse])
async def get_matches(
    job_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: UserContext = Depends(get_current_user)
):
    """
    Retrieves the persisted ranked candidates (matches) from the database for the given job.
    """
    result = await db.execute(select(Match).filter(Match.job_id == job_id).order_by(Match.final_score.desc()))
    return result.scalars().all()

@router.get("/", response_model=list[JobResponse])
async def list_jobs(db: AsyncSession = Depends(get_db), current_user: UserContext = Depends(get_current_user)):
    result = await db.execute(select(Job).limit(50))
    return result.scalars().all()


