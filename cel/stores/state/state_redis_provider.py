import asyncio
import json
from redis import Redis
from redis.asyncio import Redis as AsyncRedis
from loguru import logger as log
from cel.stores.state.base_state_provider import BaseChatStateProvider

class RedisChatStateProvider(BaseChatStateProvider):

    def __init__(self, redis: str | Redis | AsyncRedis, key_prefix: str = "s"):
        super().__init__()
        log.debug("Create: RedisChatStateProvider")
        self.client = AsyncRedis.from_url(redis) if isinstance(redis, str) else redis
        self.is_async = isinstance(self.client, AsyncRedis)
        if not self.is_async:
            log.warning(
                "RedisChatStateProvider received a synchronous Redis client. "
                "Its commands are offloaded to a worker thread to keep the event "
                "loop free. Pass a redis.asyncio.Redis client or a connection url."
            )
        self.prefix = key_prefix

    async def _run(self, command, *args, **kwargs):
        """Await async redis commands and offload synchronous ones to a thread.

        Every caller of this provider runs on the gateway event loop, so a
        blocking redis round trip stalls every other conversation in flight.
        """
        if self.is_async:
            return await command(*args, **kwargs)
        return await asyncio.to_thread(command, *args, **kwargs)

    def get_key(self, sessionId):
        return f"{self.prefix}:{sessionId}"
        
    async def set_key_value(self, sessionId: str, key: str, value, ttl_in_seconds=None):
        hash_key = self.get_key(sessionId)
        await self._run(self.client.hset, hash_key, key, json.dumps(value))
        if ttl_in_seconds:
            await self._run(self.client.expire, hash_key, ttl_in_seconds)

    async def get_key_value(self, sessionId: str, key: str):
        hash_key = self.get_key(sessionId)
        value = await self._run(self.client.hget, hash_key, key)
        if not value:
            return None
        return json.loads(value)

    async def clear_store(self, sessionId: str):
        hash_key = self.get_key(sessionId)
        await self._run(self.client.delete, hash_key)

    async def clear_all_stores(self):
        hash_key = self.get_key("*")
        keys = await self._run(self.client.keys, hash_key)
        if not keys:
            return
        for key in keys:
            await self._run(self.client.delete, key)

    async def get_store(self, sessionId: str):
        hash_key = self.get_key(sessionId)
        store = await self._run(self.client.hgetall, hash_key)
        if not store:
            return None
        s = {k.decode('utf-8'): json.loads(store[k]) for k in store}
        return s


    async def set_store(self, sessionId: str, store, ttl=None):
        hash_key = self.get_key(sessionId)
        for key in store:
            await self._run(self.client.hset, hash_key, key, json.dumps(store[key]))
        if ttl:
            await self._run(self.client.expire, hash_key, ttl)
