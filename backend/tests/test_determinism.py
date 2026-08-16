import pytest
import uuid
from typing import List, Dict, Any
from unittest.mock import patch, MagicMock

from app.ai.orchestrator import AIOrchestrator

@pytest.fixture
def deterministic_candidates() -> List[Dict[str, Any]]:
    return [
        {
            "candidate_id": "c1",
            "embedding_score": 85.0,
            "profile": {
                "current_title": "Senior Python Engineer",
                "skills": ["Python", "FastAPI", "SQL", "AWS"],
                "experience": [
                    {"title": "Senior Engineer", "years": 4, "description": "Backend API development."}
                ]
            },
            "behavioral_metrics": {}
        },
        {
            "candidate_id": "c2",
            "embedding_score": 70.0,
            "profile": {
                "current_title": "Frontend Developer",
                "skills": ["React", "JavaScript", "CSS"],
                "experience": [
                    {"title": "Developer", "years": 2, "description": "UI development."}
                ]
            },
            "behavioral_metrics": {}
        },
        {
            "candidate_id": "c3",
            "embedding_score": 90.0,
            "profile": {
                "current_title": "Backend Lead",
                "skills": ["Python", "Django", "SQL", "Docker", "Kubernetes"],
                "experience": [
                    {"title": "Lead Engineer", "years": 6, "description": "Led backend architecture."}
                ]
            },
            "behavioral_metrics": {}
        }
    ]

@patch.object(AIOrchestrator, '_run_retrieval')
def test_pipeline_determinism(mock_run_retrieval, deterministic_candidates):
    """
    Test that running the pipeline multiple times produces exactly identical outputs.
    This ensures no random generators, unseeded state, or race conditions affect ranking.
    """
    mock_run_retrieval.return_value = deterministic_candidates
    
    orchestrator = AIOrchestrator()
    job_desc = "Looking for a backend engineer with strong Python, FastAPI, and SQL experience."
    job_id = str(uuid.uuid4())
    
    # Run 1
    result1 = orchestrator.process_job(job_id, job_desc)
    
    # Run 2
    result2 = orchestrator.process_job(job_id, job_desc)
    
    # Run 3
    result3 = orchestrator.process_job(job_id, job_desc)
    
    assert result1["status"] == "success"
    
    cands1 = result1["results"]
    cands2 = result2["results"]
    cands3 = result3["results"]
    
    assert len(cands1) == 3
    assert len(cands2) == 3
    assert len(cands3) == 3
    
    order1 = [c["candidate_id"] for c in cands1]
    order2 = [c["candidate_id"] for c in cands2]
    order3 = [c["candidate_id"] for c in cands3]
    
    assert order1 == order2 == order3
    
    for i in range(len(cands1)):
        c1 = cands1[i]
        c2 = cands2[i]
        c3 = cands3[i]
        
        assert c1["final_score"] == c2["final_score"] == c3["final_score"]
        assert c1["semantic_score"] == c2["semantic_score"] == c3["semantic_score"]
        assert c1["skill_match_score"] == c2["skill_match_score"] == c3["skill_match_score"]
        assert c1["experience_score"] == c2["experience_score"] == c3["experience_score"]
        
        assert c1.get("flags") == c2.get("flags") == c3.get("flags")
        assert c1.get("matched_skills") == c2.get("matched_skills") == c3.get("matched_skills")
        assert c1.get("missing_skills") == c2.get("missing_skills") == c3.get("missing_skills")
