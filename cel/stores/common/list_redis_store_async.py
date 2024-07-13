import json
from redis import asyncio as aioredis
from cel.stores.common.key_value_store import ListStore

Redis = aioredis.Redis

class ListRedisStoreAsync(ListStore):

    def __init__(self, redis: str | Redis, key_prefix="h", ttl=60):
        self.redis_client = redis if isinstance(redis, Redis) else aioredis.from_url(redis)
        self.key_prefix = key_prefix
        self.key_prefix = key_prefix
        self.ttl = ttl

    async def list_append(self, key, entry, ttl=None):
        key = self.key_prefix + ":" + key
        value = json.dumps(entry)
        await self.redis_client.rpush(key, value)
        if ttl:
            await self.redis_client.expire(key, ttl)

    async def list_clear(self, key):
        key = self.key_prefix + ":" + key
        await self.redis_client.delete(key)

    async def list_get(self, key):
        key = self.key_prefix + ":" + key
        l = await self.redis_client.lrange(key, 0, -1)
        # decode
        return [json.loads(v) for v in l]

    async def list_get_last(self, key, count: int):
        key = self.key_prefix + ":" + key
        l = await self.redis_client.lrange(key, -count, -1)
        # decode
        return [json.loads(v) for v in l]    