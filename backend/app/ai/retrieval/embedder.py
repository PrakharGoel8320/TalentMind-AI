import logging
import numpy as np
from typing import List
from sentence_transformers import SentenceTransformer
from app.ai.retrieval.config import settings
import torch

logger = logging.getLogger(__name__)

class Embedder:
    _instance = None
    
    def __init__(self):
        if Embedder._instance is not None:
            raise Exception("Embedder is a singleton. Use Embedder.get_instance()")
            
        logger.info(f"Loading SentenceTransformer model: {settings.MODEL_NAME}")
        self.model = SentenceTransformer(settings.MODEL_NAME)
        
        logger.info("Applying PyTorch INT8 dynamic quantization to Embedder model...")
        self.model[0].auto_model = torch.quantization.quantize_dynamic(
            self.model[0].auto_model,
            {torch.nn.Linear},
            dtype=torch.qint8
        )
        Embedder._instance = self

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls()
        return cls._instance
        
    def encode(self, texts: List[str]) -> np.ndarray:
        if not texts:
            return np.empty((0, settings.EMBEDDING_DIM), dtype=np.float32)
            
        logger.debug(f"Encoding batch of {len(texts)} texts...")
        
        embeddings = self.model.encode(
            texts,
            batch_size=settings.BATCH_SIZE,
            show_progress_bar=False,
            convert_to_numpy=True
        )
        
        embeddings = embeddings.astype(np.float32)
        
        norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
        norms[norms == 0] = 1e-10
        embeddings_normalized = embeddings / norms
        
        return embeddings_normalized
