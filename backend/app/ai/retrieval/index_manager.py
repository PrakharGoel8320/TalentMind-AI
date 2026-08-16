# pyrefly: ignore [missing-import]
import faiss
import json
import logging
# pyrefly: ignore [missing-import]
import numpy as np
from typing import List, Tuple
from app.ai.retrieval.config import settings
import os

logger = logging.getLogger(__name__)

class FaissIndexManager:
    def __init__(self):
        self.index_path = settings.FAISS_INDEX_PATH
        self.mapping_path = settings.ID_MAPPING_PATH
        self.dimension = settings.EMBEDDING_DIM
        self.index = None
        self.id_mapping = []  # Maps FAISS index (int) to candidate_id (str)
        self.load_index()

    def _init_index(self):
        if settings.FAISS_INDEX_TYPE == "HNSWFlat":
            logger.info("Initializing faiss.IndexHNSWFlat")
            self.index = faiss.IndexHNSWFlat(self.dimension, 32, faiss.METRIC_INNER_PRODUCT)
        else:
            logger.info("Initializing faiss.IndexFlatIP")
            self.index = faiss.IndexFlatIP(self.dimension)
            
        self.id_mapping = []

    def load_index(self):
        """Loads index and mapping from disk if they exist, otherwise initializes new."""
        if os.path.exists(self.index_path) and os.path.exists(self.mapping_path):
            try:
                logger.info(f"Loading FAISS index from {self.index_path}")
                self.index = faiss.read_index(str(self.index_path))
                with open(self.mapping_path, 'r', encoding='utf-8') as f:
                    self.id_mapping = json.load(f)
                logger.info(f"Successfully loaded index with {self.index.ntotal} vectors.")
            except Exception as e:
                logger.error(f"Failed to load index, initializing new one: {e}")
                self._init_index()
        else:
            logger.info("No existing index found. Initializing new FAISS index.")
            self._init_index()

    def save_index(self):
        """Saves index and mapping to disk."""
        try:
            logger.info(f"Saving FAISS index to {self.index_path}")
            faiss.write_index(self.index, str(self.index_path))
            with open(self.mapping_path, 'w', encoding='utf-8') as f:
                json.dump(self.id_mapping, f)
        except Exception as e:
            logger.error(f"Failed to save FAISS index: {e}")
            raise

    def add_vectors(self, embeddings: np.ndarray, candidate_ids: List[str]):
        """
        Incrementally adds new vectors to the FAISS index.
        """
        if embeddings.shape[0] != len(candidate_ids):
            raise ValueError("Number of embeddings must match number of candidate_ids")
        if embeddings.shape[1] != self.dimension:
            raise ValueError(f"Embeddings dimension {embeddings.shape[1]} does not match index dimension {self.dimension}")

        logger.info(f"Adding {len(candidate_ids)} vectors to FAISS index.")
        self.index.add(embeddings)
        self.id_mapping.extend(candidate_ids)
        self.save_index()

    def search(self, query_embedding: np.ndarray, top_k: int = 100) -> Tuple[List[str], List[float]]:
        """
        Searches the index for the top_k most similar vectors.
        Returns:
            Tuple containing list of candidate_ids and list of scores.
        """
        if self.index is None or self.index.ntotal == 0:
            logger.warning("FAISS index is empty. Cannot search.")
            return [], []

        # Ensure query is 2D
        if len(query_embedding.shape) == 1:
            query_embedding = np.expand_dims(query_embedding, axis=0)

        # Ensure type
        query_embedding = query_embedding.astype(np.float32)

        k = min(top_k, self.index.ntotal)
        scores, indices = self.index.search(query_embedding, k)
        
        # Flatten results (assuming single query)
        scores = scores[0].tolist()
        indices = indices[0].tolist()

        result_ids = [self.id_mapping[idx] for idx in indices if idx < len(self.id_mapping)]
        return result_ids, scores
