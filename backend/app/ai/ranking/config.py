from pydantic_settings import BaseSettings
import os

class RankingConfig(BaseSettings):
    CROSS_ENCODER_MODEL: str = 'cross-encoder/ms-marco-MiniLM-L-6-v2'
    USE_CPU: bool = True
    BATCH_SIZE: int = 32
    ENABLE_CACHE: bool = True

    class Config:
        env_prefix = "RANKING_"

config = RankingConfig()
