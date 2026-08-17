from fastapi import APIRouter, Depends, HTTPException
from app.core.auth import get_current_user, UserContext
import uuid
from typing import Dict, Any

router = APIRouter(prefix="/skills", tags=["skills"])


@router.get("/graph/{candidate_id}")
async def get_skill_graph(
    candidate_id: uuid.UUID,
    current_user: UserContext = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Returns a skill graph (nodes + links) for a given candidate.
    Currently returns a deterministic demo graph for presentation purposes.
    """
    nodes = [
        {"id": "Python", "group": 1},
        {"id": "FastAPI", "group": 2},
        {"id": "Machine Learning", "group": 3},
    ]
    links = [
        {"source": "Python", "target": "FastAPI", "value": 1},
        {"source": "Python", "target": "Machine Learning", "value": 2},
    ]
    return {"nodes": nodes, "links": links}
