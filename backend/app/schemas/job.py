from pydantic import BaseModel, UUID4
from typing import Optional, List, Dict, Any
from app.models.enums import JobStatus

class JobBase(BaseModel):
    title: str
    department: Optional[str] = None
    location: Optional[str] = None
    description: str
    skills: Optional[List[str]] = None

class JobCreate(JobBase):
    pass

class JobResponse(JobBase):
    id: UUID4
    status: JobStatus

    class Config:
        from_attributes = True

class JobSimulateRequest(BaseModel):
    job_id: UUID4
    candidate_id: UUID4
    new_description: str
    old_description: str
