import logging
from typing import List, Dict, Any

from app.ai.retrieval.preprocessor import CandidatePreprocessor, JDPreprocessor
from app.ai.retrieval.embedder import Embedder
from app.ai.retrieval.index_manager import FaissIndexManager

logger = logging.getLogger(__name__)


class RetrievalService:
    def __init__(self):
        self.embedder = Embedder.get_instance()
        self.index_manager = FaissIndexManager.get_instance()

    def index_candidates(self, candidates: List[Dict[str, Any]]) -> None:
        texts = []
        candidate_ids = []
        for cand in candidates:
            c_id = cand.get("candidate_id", "")
            text = CandidatePreprocessor.flatten_candidate(cand)
            candidate_ids.append(c_id)
            texts.append(text)

        logger.info("Generating embeddings for %d candidates...", len(texts))
        embeddings = self.embedder.encode(texts)
        self.index_manager.add_vectors(candidate_ids, embeddings)
        logger.info("Successfully indexed %d candidates.", len(texts))

    def search_candidates(self, job_description_text: str, top_k: int = 100) -> List[Dict[str, Any]]:
        if not job_description_text:
            logger.warning("Empty job description provided for search.")
            return []

        cleaned_jd = JDPreprocessor.flatten_jd(job_description_text)
        logger.info("Embedding Job Description for search (top_k=%d)...", top_k)
        jd_embedding = self.embedder.encode([cleaned_jd])
        scores, results = self.index_manager.search(jd_embedding, top_k=top_k)

        output = []
        for score, candidate_id in zip(scores, results):
            norm_score = max(0.0, min(1.0, float(score)))
            output.append({"candidate_id": candidate_id, "score": norm_score})

        logger.info("Retrieved %d candidates for JD.", len(output))
        return output
