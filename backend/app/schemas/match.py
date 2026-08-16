from typing import Any, Dict, List, Optional
import uuid
from pydantic import BaseModel

class MatchResponse(BaseModel):
    id: uuid.UUID
    job_id: uuid.UUID
    candidate_id: uuid.UUID
    final_score: float
    score_components: Dict[str, float]
    flags: List[str]
    explanation: Optional[Dict[str, Any]] = None
    model_versions: Optional[Dict[str, str]] = None
