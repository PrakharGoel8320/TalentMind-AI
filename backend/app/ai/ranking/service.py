import logging
from typing import List, Dict, Any

from app.ai.ranking.ranker import SemanticRanker
from app.ai.retrieval.preprocessor import CandidatePreprocessor, JDPreprocessor

logger = logging.getLogger(__name__)


class RankingService:
    def __init__(self):
        self.ranker = SemanticRanker.get_instance()

    def rank_candidates(self, job_description: str, candidates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        query = JDPreprocessor.flatten_jd(job_description)
        candidate_texts = [CandidatePreprocessor.flatten_candidate(cand) for cand in candidates]

        try:
            scores = self.ranker.predict_batch(query, candidate_texts)
        except Exception as e:
            logger.error("Ranking failed: %s. Falling back to 0.0 scores.", e)
            scores = [0.0] * len(candidates)

        ranked_candidates = []
        for cand, score in zip(candidates, scores):
            cand_copy = cand.copy()
            cand_copy["semantic_score"] = float(score)
            ranked_candidates.append(cand_copy)

        ranked_candidates.sort(key=lambda x: x["semantic_score"], reverse=True)
        return ranked_candidates
