from dataclasses import dataclass
import json
import asyncio
import time
from typing import Any
import cachetools
from .key_value_store import KeyValueStore
from redis import asyncio as aioredis

Redis = aioredis.Redis


@dataclass
class CacheData:
    data: Any
    ttl: int
    created_at: int

class AsyncMemRedisCacheAside(KeyValueStore):
    """Implements a cache-aside pattern with memory and Redis cache.

    This class uses both an in-memory cache (based on async_lru) and a Redis cache for storing data.
    The in-memory cache is used for fast access, while the Redis cache provides persistence and can be shared across multiple instances.

    Attributes:
        redis_client: A Redis client connected to the Redis server.
        cache: An in-memory LRU cache.
        key_prefix: A prefix added to all keys stored in the Redis cache.
        ttl: The time-to-live (in seconds) for keys in the Redis cache.
    """

    def __init__(self, redis: str | Redis, key_prefix, memory_maxsize=1000, ttl=60, wait_for_redis=True):
        """Initializes the cache with the given parameters."""
        self.redis_client = redis if isinstance(redis, Redis) else aioredis.from_url(redis)
        self.cache = cachetools.LRUCache(maxsize=memory_maxsize)
        self.maxsize = memory_maxsize
        self.key_prefix = key_prefix
        self.ttl = ttl
        self.wait_for_redis = wait_for_redis
        self.cache_memory_hits = 0
        self.cache_redis_hits = 0
        self.cache_misses = 0
        
    
        
    def get_key(self, key):
        return self.key_prefix + ":" + key
    
    def __warp_cache_data(self, data) -> CacheData:
        return CacheData(data, self.ttl, int(time.time()))
    
    
    def __get_from_cache(self, key):
        data = self.cache.get(key)
        if data is not None:
            if (time.time() - data.created_at) > data.ttl:
                self.cache.pop(key, None)
                data = None
            else:
                return data.data
        return None
    
    def __set_to_cache(self, key, value):
        self.cache[key] = self.__warp_cache_data(value)
    

    async def get(self, key, callback=None):
        """Retrieves the value associated with the given key from the cache.

        If the key is not in the in-memory cache, it tries to retrieve it from the Redis cache.
        If the key is not in the Redis cache either, it calls the provided callback function to compute the value.

        callback: A function that computes the value for the given key if it is not in the cache (optional).
        """
        k = self.get_key(key)
        
        data = self.__get_from_cache(k)
        if data is not None:
            self.cache_memory_hits += 1
            return data
        
        data = await self.redis_client.get(k)
        if data is not None:
            self.cache_redis_hits += 1
            data = json.loads(data)
            self.__set_to_cache(k, data)
            return data
        
        self.cache_misses += 1
        
        if callback:
            data = await callback()
            if data is not None:
                await self.set(k, data)
                return data

        
        return None

    async def set(self, key, value):
        """Sets the value for the given key in both the in-memory and Redis caches."""        
        k = self.get_key(key)
        
        # Update the in-memory cache
        self.__set_to_cache(k, value)

        # Update the Redis cache
        if self.wait_for_redis:
            await self.redis_client.setex(k, self.ttl, json.dumps(value))
        else:
            asyncio.create_task(self.redis_client.setex(k, self.ttl, json.dumps(value)))

    async def get_all(self):
        keys = await self.redis_client.keys(self.key_prefix + ":" + '*')
        data = {}
        for k in keys:
            data[k] = await self.redis_client.get(k)
        return data

    async def delete(self, key):
        """Deletes the key from the in-memory cache."""
        k = self.get_key(key)
        self.cache.pop(k, None)
        
    
    async def delete_deep(self, key):
        """Deletes the key from the Redis cache."""
        k = self.get_key(key)
        await self.delete(key)
        await self.redis_client.delete(k)

    async def clear(self):
        """Clears the in-memory cache."""
        self.cache.clear()
        self.cache_memory_hits = 0
        self.cache_redis_hits = 0
        self.cache_misses = 0

    async def clear_deep(self):
        """Clears the Redis cache."""
        # delete all keys with the prefix
        await self.clear()
        keys = await self.redis_client.keys(self.key_prefix + ":" + '*')
        if keys:
            await self.redis_client.delete(*keys)

