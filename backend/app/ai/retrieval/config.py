from pydantic_settings import BaseSettings
from pathlib import Path
import os

class RetrievalConfig(BaseSettings):
    MODEL_NAME: str = 'all-MiniLM-L6-v2'
    EMBEDDING_DIM: int = 384
    BATCH_SIZE: int = 256
    
    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent.parent
    INDEX_DIR: Path = BASE_DIR / 'app' / 'ai' / 'retrieval' / 'data'
    FAISS_INDEX_PATH: Path = INDEX_DIR / 'candidates.index'
    ID_MAPPING_PATH: Path = INDEX_DIR / 'id_mapping.json'
    FAISS_INDEX_TYPE: str = 'HNSWFlat'

    class Config:
        env_prefix = "RETRIEVAL_"

settings = RetrievalConfig()
os.makedirs(settings.INDEX_DIR, exist_ok=True)
