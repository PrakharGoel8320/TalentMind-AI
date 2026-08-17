import logging
import hashlib
import time
from typing import List, Dict, Any, Tuple
from functools import lru_cache
from app.ai.ranking.config import config

logger = logging.getLogger(__name__)

class SemanticRanker:
    """
    Singleton class to load and manage the CrossEncoder model for candidate re-ranking.
    """
    _instance = None
    
    def __init__(self):
        if SemanticRanker._instance is not None:
            raise Exception("Singleton")
        self.model = None
        SemanticRanker._instance = self

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls()
        return cls._instance
        
    def _ensure_model(self):
        if self.model is None:
            try:
                from sentence_transformers.cross_encoder import CrossEncoder
                logger.info(f"Lazy loading CrossEncoder: {config.CROSS_ENCODER_MODEL}")
                self.model = CrossEncoder(config.CROSS_ENCODER_MODEL)
            except Exception as e:
                logger.error(f"Failed to load CrossEncoder: {e}")
                self.model = None

    def _generate_cache_key(self, query: str, document: str) -> str:
        s = f"{query}:{document}"
        return hashlib.sha256(s.encode()).hexdigest()
        
    def rank(self, query: str, documents: List[str]) -> List[float]:
        if not documents:
            return []
        self._ensure_model()
        if self.model is None:
            return [0.0 for _ in documents]
        pairs = [[query, doc] for doc in documents]
        try:
            scores = self.model.predict(pairs, batch_size=config.BATCH_SIZE, show_progress_bar=False)
            if isinstance(scores, (float, int)):
                return [float(scores)]
            return scores.tolist()
        except Exception as e:
            logger.error(f"CrossEncoder prediction failed: {e}")
            return [0.0 for _ in documents]

    def predict_batch(self, query: str, documents: List[str]) -> List[float]:
        return self.rank(query, documents)
