from typing import Any, Dict, List, Optional
import uuid
from pydantic import BaseModel

class CandidateBase(BaseModel):
    name: str
    email: str

class CandidateCreate(CandidateBase):
    pass

class CandidateResponse(CandidateBase):
    id: uuid.UUID
    profile_jsonb: Optional[Dict[str, Any]] = None

