import json
import os
import logging

logger = logging.getLogger(__name__)

class FusionConfig:
    """Loads and provides access to the external JSON configuration for the Ranking Fusion Engine."""
    _instance = None
    _config = None
    
    def __init__(self):
        if FusionConfig._instance is not None:
            raise Exception("Singleton")
        self.load_config()
        FusionConfig._instance = self

    def load_config(self, filepath=None):
        if filepath is None:
            filepath = os.path.join(os.path.dirname(__file__), "config.json")
        try:
            with open(filepath, 'r') as f:
                self._config = json.load(f)
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
            self._config = {
                "weights": {
                    "semantic_score": 0.4,
                    "keyword_score": 0.3,
                    "behavioral_score": 0.3
                }
            }

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls()
        return cls._instance
        
    def get(self, key, default=None):
        return self._config.get(key, default)

config = FusionConfig.get_instance()
