import pytest
import asyncio
from app.db.session import SessionLocal
from app.ai.ranking.service import RankerService
from app.db.models import Job

@pytest.mark.asyncio
async def test_determinism_5_runs():
    job_id = "ea039e44-f6e1-45e5-b395-fe5170536b8b"
    async with SessionLocal() as db:
        service = RankerService()
        results = []
        for i in range(5):
            res = await service.rank_candidates_for_job(db, job_id)
            extracted = [(r["candidate"].id, r["match"].semantic_score, r["match"].skill_match_score, r["match"].experience_score, r["match"].behavioral_score, r["match"].fusion_score) for r in res]
            results.append(extracted)
        
        first = results[0]
        for idx, run in enumerate(results[1:], start=2):
            assert run == first, f"Run {idx} failed determinism check"
        print("DETERMINISM TEST PASSED: All 5 runs yielded identical candidate ordering and scores.")
