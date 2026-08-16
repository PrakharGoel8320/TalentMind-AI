import pytest
from app.ai.feature_extraction import FeatureExtractionService

@pytest.fixture
def service():
    return FeatureExtractionService()

def test_determinism_same_input(service):
    """Test 1: Same input produces same feature scores."""
    candidates = [
        {
            "candidate_id": "c1",
            "profile": {
                "skills": ["Python", "FastAPI", "React"],
                "experience": [{"title": "Dev"}, {"title": "Senior Dev"}]
            }
        }
    ]
    jd_text = "Looking for a Python and FastAPI backend developer."
    
    # Run twice on independent copies
    import copy
    run1 = service.extract_features(copy.deepcopy(candidates), jd_text)
    run2 = service.extract_features(copy.deepcopy(candidates), jd_text)
    
    assert run1[0]["skill_match_score"] == run2[0]["skill_match_score"]
    assert run1[0]["experience_score"] == run2[0]["experience_score"]

def test_different_candidate_data(service):
    """Test 2: Different candidate data can produce different scores."""
    candidates = [
        {
            "candidate_id": "c1", # Strong match
            "profile": {
                "skills": ["Python", "FastAPI"],
                "experience": [{"title": "Dev"}, {"title": "Senior Dev"}, {"title": "Lead"}]
            }
        },
        {
            "candidate_id": "c2", # Weak match
            "profile": {
                "skills": ["Java"],
                "experience": [{"title": "Intern"}]
            }
        }
    ]
    jd_text = "Need Python and FastAPI expert."
    
    results = service.extract_features(candidates, jd_text)
    
    # c1 should have a higher skill score than c2
    assert results[0]["skill_match_score"] > results[1]["skill_match_score"]
    # c1 should have a higher experience score than c2
    assert results[0]["experience_score"] > results[1]["experience_score"]

def test_missing_data(service):
    """Test 3: Missing fields do not create random scores, but fallback deterministically."""
    candidates = [{"candidate_id": "c_missing", "profile": {}}]
    jd_text = "Requires Python."
    
    import copy
    run1 = service.extract_features(copy.deepcopy(candidates), jd_text)
    run2 = service.extract_features(copy.deepcopy(candidates), jd_text)
    
    assert run1[0]["skill_match_score"] == 0.0 # 0/1 matched
    assert run1[0]["experience_score"] == 0.0
    
    assert run1[0]["skill_match_score"] == run2[0]["skill_match_score"]
    assert run1[0]["experience_score"] == run2[0]["experience_score"]
    
def test_no_jd_skills(service):
    """Fallback if JD has no recognizable skills."""
    candidates = [
        {
            "candidate_id": "c1",
            "profile": {"skills": ["Python"]}
        }
    ]
    jd_text = "We are looking for someone." # No COMMON_SKILLS
    results = service.extract_features(candidates, jd_text)
    
    assert results[0]["skill_match_score"] == 50.0
