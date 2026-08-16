import copy

from app.ai.fusion.service import FusionService
from app.ai.feature_extraction import FeatureExtractionService


def test_fusion_ranking_is_deterministic_for_identical_input():
    service = FusionService()

    candidates = [
        {
            "candidate_id": "c1",
            "cross_encoder_score": 82.5,
            "embedding_score": 76.0,
            "skill_match_score": 90.0,
            "experience_score": 80.0,
            "behavioral_score": 60.0,
        },
        {
            "candidate_id": "c2",
            "cross_encoder_score": 80.0,
            "embedding_score": 78.0,
            "skill_match_score": 88.0,
            "experience_score": 85.0,
            "behavioral_score": 62.0,
        },
        {
            "candidate_id": "c3",
            "cross_encoder_score": 50.0,
            "embedding_score": 45.0,
            "skill_match_score": 55.0,
            "experience_score": 40.0,
            "behavioral_score": 50.0,
        },
    ]

    run1 = service.rank_candidates(copy.deepcopy(candidates))
    run2 = service.rank_candidates(copy.deepcopy(candidates))
    run3 = service.rank_candidates(copy.deepcopy(candidates))

    assert run1 == run2 == run3

    order1 = [cand["candidate_id"] for cand in run1]
    order2 = [cand["candidate_id"] for cand in run2]
    order3 = [cand["candidate_id"] for cand in run3]

    assert order1 == order2 == order3


def test_fusion_maps_semantic_score_to_cross_encoder():
    """RankingService stores cross-encoder output as semantic_score; fusion must use it."""
    service = FusionService()
    candidates = [
        {
            "candidate_id": "c1",
            "semantic_score": 90.0,
            "embedding_score": 70.0,
            "skill_match_score": 80.0,
            "experience_score": 75.0,
            "behavioral_score": 60.0,
        },
        {
            "candidate_id": "c2",
            "cross_encoder_score": 50.0,
            "embedding_score": 95.0,
            "skill_match_score": 80.0,
            "experience_score": 75.0,
            "behavioral_score": 60.0,
        },
    ]
    ranked = service.rank_candidates(copy.deepcopy(candidates))
    assert ranked[0]["candidate_id"] == "c1"
    assert ranked[0]["cross_encoder_score"] == 90.0


def test_different_candidate_profiles_produce_different_skill_scores():
    extractor = FeatureExtractionService()
    job = "Senior Python FastAPI developer with Kubernetes experience"

    candidate_a = [{"candidate_id": "a", "profile": {"skills": ["Python", "FastAPI", "Kubernetes"]}}]
    candidate_b = [{"candidate_id": "b", "profile": {"skills": ["Java", "Spring"]}}]

    result_a = extractor.extract_features(copy.deepcopy(candidate_a), job)
    result_b = extractor.extract_features(copy.deepcopy(candidate_b), job)

    assert result_a[0]["skill_match_score"] != result_b[0]["skill_match_score"]
    assert len(result_a[0]["matched_skills"]) > len(result_b[0]["matched_skills"])

