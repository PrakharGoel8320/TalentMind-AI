from fastapi import APIRouter, Depends, HTTPException
import uuid
from pydantic import BaseModel
from typing import List, Any, Dict, Optional
from app.ai.agent.graph import TalentMindAgent
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.session import get_db
from sqlalchemy import select
from app.models.job import Job
from app.core.auth import get_current_user, UserContext

router = APIRouter(prefix="/agent", tags=["agent"])

class AgentRequest(BaseModel):
    job_id: uuid.UUID
    request: str = "Find the strongest candidates for this role and explain why."

class AgentResponse(BaseModel):
    job_id: uuid.UUID
    status: str
    explanation: str
    candidates: List[Dict[str, Any]]
    errors: List[str]

@router.post("/run", response_model=AgentResponse)
async def run_agent(
    req: AgentRequest,
    db: AsyncSession = Depends(get_db),
    current_user: UserContext = Depends(get_current_user),
):
    # Fetch job to get description
    result = await db.execute(select(Job).filter(Job.id == req.job_id))
    job = result.scalars().first()
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
        
    job_description = job.description or ""
    
    agent = TalentMindAgent()
    
    # Run agent in thread since it contains synchronous ML and LangGraph calls
    import asyncio
    result = await asyncio.to_thread(agent.run, str(req.job_id), job_description, req.request)
    
    return AgentResponse(
        job_id=req.job_id,
        status=result.get("status", "error"),
        explanation=result.get("explanation", ""),
        candidates=result.get("candidates", []),
        errors=result.get("errors", [])
    )
