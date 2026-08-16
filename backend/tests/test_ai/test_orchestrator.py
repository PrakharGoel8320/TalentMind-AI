import pytest
from app.ai.orchestrator import AIOrchestrator
from app.ai.context import PipelineContext

@pytest.fixture
def orchestrator():
    return AIOrchestrator()

def test_pipeline_context():
    ctx = PipelineContext("jd_123", "Looking for a Python developer")
    assert ctx.job_description_id == "jd_123"
    assert ctx.job_description_text == "Looking for a Python developer"
    
    ctx.record_phase("test_phase", 15.5)
    assert ctx.phase_timings["test_phase"] == 15.5

def test_full_orchestration_mocked(mocker, orchestrator):
    # We will mock the individual services to just pass data through to test the orchestrator flow
    
    mocker.patch.object(orchestrator.retrieval, 'search_candidates', return_value=[
        {"candidate_id": "1", "score": 0.8},
        {"candidate_id": "2", "score": 0.6}
    ])
    
    # Mock DB fetch to return some dummy Candidate scalars
    class DummyCand:
        def __init__(self, id_str):
            self.id = id_str
            self.profile_jsonb = {"skills": ["Python"]}
            
    # Mock AsyncSessionLocal and its async context manager
    mock_db = mocker.AsyncMock()
    mock_db.__aenter__.return_value = mock_db
    
    mock_res = mocker.MagicMock()
    mock_res.scalars.return_value.all.return_value = [DummyCand("1"), DummyCand("2")]
    mock_db.execute.return_value = mock_res
    
    mocker.patch('app.ai.orchestrator.AsyncSessionLocal', return_value=mock_db)
    
    # Feature extractor will add skills automatically
    
    # Mock Ranking
    mocker.patch.object(orchestrator.ranking, 'rank_candidates', side_effect=lambda jd, cands: [
        {**c, "cross_encoder_score": 90.0} for c in cands
    ])
    
    # Mock behavioral
    mocker.patch.object(orchestrator.behavioral, 'score_candidates', side_effect=lambda cands: [
        {**c, "behavior_score": 85.0} for c in cands
    ])
    
    # Mock fusion - return one candidate
    mocker.patch.object(orchestrator.fusion, 'rank_candidates', side_effect=lambda cands: [
        {**cands[0], "final_score": 88.0, "fusion_confidence": 90.0}
    ])
    
    # Run
    result = orchestrator.process_job("jd_test", "Python dev needed", top_k=1)
    
    assert result["status"] == "success"
    assert "retrieval" in result["phase_timings"]
