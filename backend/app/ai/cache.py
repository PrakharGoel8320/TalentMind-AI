import logging
from typing import Any, Optional

try:
    from cachetools import LRUCache
except ImportError:
    LRUCache = None

logger = logging.getLogger(__name__)


class CacheManager:
    """Singleton class"""
    _instance = None

    def __init__(self, max_memory_items: int = 512):
        if CacheManager._instance is not None:
            raise Exception("Singleton")
        if LRUCache is not None:
            self.memory_cache = LRUCache(maxsize=max_memory_items)
        else:
            self.memory_cache = {}
        self.redis_client = None
        CacheManager._instance = self

    @classmethod
    def get_instance(cls, max_memory_items: int = 512) -> "CacheManager":
        if cls._instance is None:
            cls(max_memory_items=max_memory_items)
        return cls._instance

    def get(self, key: str) -> Any:
        val = self.memory_cache.get(key)
        if val is not None:
            return val
        if self.redis_client:
            try:
                return self.redis_client.get(key)
            except Exception as e:
                logger.warning("Redis cache GET error: %s", e)
        return None

    def set(self, key: str, value: Any, ttl: int = 3600) -> None:
        self.memory_cache[key] = value
        if self.redis_client:
            try:
                self.redis_client.setex(key, ttl, value)
            except Exception as e:
                logger.warning("Redis cache SET error: %s", e)

    def get_many(self, keys: list) -> dict:
        results = {}
        missing_keys = []
        for k in keys:
            v = self.memory_cache.get(k)
            if v is not None:
                results[k] = v
            else:
                missing_keys.append(k)

        if missing_keys and self.redis_client:
            try:
                redis_results = self.redis_client.mget(missing_keys)
                for k, v in zip(missing_keys, redis_results):
                    if v is not None:
                        results[k] = v
            except Exception as e:
                logger.warning("Redis cache MGET error: %s", e)
        return results

    def set_many(self, mapping: dict, ttl: int = 3600) -> None:
        for k, v in mapping.items():
            self.memory_cache[k] = v
        if self.redis_client:
            try:
                pipeline = self.redis_client.pipeline()
                for k, v in mapping.items():
                    pipeline.setex(k, ttl, v)
                pipeline.execute()
            except Exception as e:
                logger.warning("Redis cache SET_MANY error: %s", e)
