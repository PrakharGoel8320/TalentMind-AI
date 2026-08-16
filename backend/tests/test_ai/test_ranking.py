import pytest
from unittest.mock import patch, MagicMock
from typing import List

from app.ai.ranking.config import config
from app.ai.ranking.ranker import SemanticRanker
from app.ai.ranking.service import RankingService

# Mock data
MOCK_JD = "Looking for a Senior Python Developer with FastAPI and ML experience."
MOCK_CANDIDATES = [
    {
        "candidate_id": "c1",
        "profile": {"current_title": "Senior Backend Engineer"},
        "skills": [{"name": "Python"}, {"name": "FastAPI"}, {"name": "Machine Learning"}],
        "career_history": [{"description": "Built AI backend services."}]
    },
    {
        "candidate_id": "c2",
        "profile": {"current_title": "Frontend Developer"},
        "skills": [{"name": "React"}, {"name": "JavaScript"}, {"name": "CSS"}],
        "career_history": [{"description": "Built web interfaces."}]
    }
]

@pytest.fixture
def mock_cross_encoder():
    with patch('app.ai.ranking.ranker.CrossEncoder') as mock_ce:
        # Create a mock instance
        instance = MagicMock()
        # predict() should return a list/numpy array of float logits
        def mock_predict(pairs, **kwargs):
            results = []
            for q, d in pairs:
                if "Backend" in d or "doc1" in d:
                    results.append(8.0)
                else:
                    results.append(-5.0)
            return results
        instance.predict.side_effect = mock_predict
        mock_ce.return_value = instance
        yield instance

@pytest.fixture(autouse=True)
def reset_singleton():
    """Reset the SemanticRanker singleton before each test."""
    SemanticRanker._instance = None
    yield
    SemanticRanker._instance = None

def test_semantic_ranker_normalization(mock_cross_encoder):
    ranker = SemanticRanker.get_instance()
    
    # -10 -> 0, +10 -> 100, 0 -> 50
    assert ranker._normalize_score(-10.0) == 0.0
    assert ranker._normalize_score(10.0) == 100.0
    assert ranker._normalize_score(0.0) == 50.0
    
    # Check clamping (config is -10 to 10 by default)
    assert ranker._normalize_score(-15.0) == 0.0
    assert ranker._normalize_score(15.0) == 100.0

def test_semantic_ranker_predict(mock_cross_encoder):
    ranker = SemanticRanker.get_instance()
    
    query = "test query"
    docs = ["doc1", "doc2"]
    
    scores = ranker.predict_batch(query, docs)
    
    # 8.0 normalized (-10 to +10 range is size 20) -> (8 - -10) / 20 = 18/20 = 0.9 = 90.0
    # -5.0 normalized -> (-5 - -10) / 20 = 5/20 = 0.25 = 25.0
    assert len(scores) == 2
    assert scores[0] == 90.0
    assert scores[1] == 25.0
    
    # Verify model predict was called with correct pairs
    mock_cross_encoder.predict.assert_called_once()
    args, kwargs = mock_cross_encoder.predict.call_args
    assert args[0] == [("test query", "doc1"), ("test query", "doc2")]

def test_ranking_service(mock_cross_encoder):
    service = RankingService()
    
    # Rank candidates
    ranked = service.rank_candidates(MOCK_JD, MOCK_CANDIDATES)
    
    assert len(ranked) == 2
    
    # c1 should be first because its score is higher (90.0 vs 25.0)
    assert ranked[0]['candidate_id'] == 'c1'
    assert ranked[0]['semantic_score'] == 90.0
    
    assert ranked[1]['candidate_id'] == 'c2'
    assert ranked[1]['semantic_score'] == 25.0
