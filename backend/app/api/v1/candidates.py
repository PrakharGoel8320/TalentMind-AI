from fastapi import APIRouter, Depends, UploadFile, File, Form, BackgroundTasks, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database.session import get_db
from app.core.auth import get_current_user, UserContext
from app.schemas.candidate import CandidateResponse
from app.models.candidate import Candidate
from app.models.resume import Resume
import fitz  # PyMuPDF
import uuid
from app.core.config import settings
from app.utils.logger import get_logger

router = APIRouter(prefix="/candidates", tags=["candidates"])
logger = get_logger("app.api.v1.candidates")

def process_resume_background(candidate_id: uuid.UUID, text: str):
    """
    Background task to process resume text, generate embeddings, and store in FAISS.
    """
    # This imports the AI Orchestrator or Retrieval Service to generate embeddings
    from app.ai.retrieval.service import RetrievalService
    
    retrieval_service = RetrievalService()
    try:
        # In a real implementation, we would insert to DB and then to FAISS
        # For hackathon: update FAISS index directly.
        retrieval_service.index_candidates([{
            "candidate_id": str(candidate_id),
            "resume_text": text,
            "skills": []
        }])
    except Exception as e:
        logger.error("resume_background_index_failed", candidate_id=str(candidate_id), error=str(e))

@router.post("/upload", response_model=CandidateResponse, status_code=202)
async def upload_resume(
    background_tasks: BackgroundTasks,
    name: str = Form(...),
    email: str = Form(...),
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: UserContext = Depends(get_current_user)
):
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
    
    # Extract text
    try:
        content = await file.read()
        max_size_bytes = settings.UPLOAD_MAX_PDF_MB * 1024 * 1024
        if len(content) > max_size_bytes:
            raise HTTPException(
                status_code=413,
                detail=f"PDF file too large. Max allowed size is {settings.UPLOAD_MAX_PDF_MB} MB.",
            )

        if not content.startswith(b"%PDF"):
            raise HTTPException(status_code=400, detail="Invalid PDF file")

        doc = fitz.open(stream=content, filetype="pdf")
        text = ""
        for page in doc:
            text += page.get_text()
    except HTTPException:
        raise
    except Exception as e:
        logger.error("resume_parse_failed", error=str(e), filename=file.filename)
        raise HTTPException(status_code=400, detail="Failed to parse PDF")
        
    # Create Candidate
    candidate = Candidate(name=name, email=email)
    db.add(candidate)
    await db.commit()
    await db.refresh(candidate)
    
    # Create Resume
    resume = Resume(
        candidate_id=candidate.id,
        file_path=file.filename, # Normally upload to S3, storing name for now
        parsed_data={"raw_text": text}
    )
    db.add(resume)
    candidate.latest_resume_id = resume.id
    await db.commit()
    await db.refresh(candidate)
    
    # Offload heavy embedding to BackgroundTask
    background_tasks.add_task(process_resume_background, candidate.id, text)
    
    return candidate

@router.post("/", response_model=CandidateResponse)
async def create_candidate(
    cand_data: dict,
    db: AsyncSession = Depends(get_db),
    current_user: UserContext = Depends(get_current_user),
):
    # Handle both new simplified schema and old detailed schema from tests
    name = cand_data.get("name", cand_data.get("first_name", "") + " " + cand_data.get("last_name", "")).strip()
    candidate = Candidate(name=name, email=cand_data.get("email", "unknown@example.com"))
    db.add(candidate)
    await db.commit()
    await db.refresh(candidate)
    return candidate

@router.post("/{candidate_id}/screen")
async def screen_candidate(
    candidate_id: uuid.UUID,
    data: dict,
    current_user: UserContext = Depends(get_current_user),
):
    return {"status": "ok"}

@router.get("/{candidate_id}", response_model=CandidateResponse)
async def get_candidate(
    candidate_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: UserContext = Depends(get_current_user),
):
    result = await db.execute(select(Candidate).filter(Candidate.id == candidate_id))
    candidate = result.scalars().first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    return candidate


@router.get("/", response_model=list[CandidateResponse])
async def list_candidates(
    db: AsyncSession = Depends(get_db),
    current_user: UserContext = Depends(get_current_user),
):
    result = await db.execute(select(Candidate).limit(50))
    return result.scalars().all()
