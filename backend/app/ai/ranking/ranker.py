import logging
import hashlib
import time
from typing import List, Dict, Any, Tuple
from functools import lru_cache
try:
    from sentence_transformers.cross_encoder import CrossEncoder
except ImportError:
    CrossEncoder = None
import torch
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
        if CrossEncoder is not None:
            logger.info(f"Loading CrossEncoder: {config.CROSS_ENCODER_MODEL}")
            self.model = CrossEncoder(config.CROSS_ENCODER_MODEL)
        else:
            self.model = None
        SemanticRanker._instance = self

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls()
        return cls._instance
        
    def _generate_cache_key(self, query: str, document: str) -> str:
        s = f"{query}:{document}"
        return hashlib.sha256(s.encode()).hexdigest()
        
    def rank(self, query: str, documents: List[str]) -> List[float]:
        if not documents:
            return []
        if self.model is None:
            return [0.0 for _ in documents]
        pairs = [[query, doc] for doc in documents]
        scores = self.model.predict(pairs, batch_size=config.BATCH_SIZE, show_progress_bar=False)
        if isinstance(scores, float) or isinstance(scores, int):
            return [float(scores)]
        return scores.tolist()
