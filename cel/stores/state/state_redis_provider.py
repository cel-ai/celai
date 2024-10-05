import json
from redis import Redis
from loguru import logger as log
from cel.stores.state.base_state_provider import BaseChatStateProvider

class RedisChatStateProvider(BaseChatStateProvider):

    def __init__(self, redis: str | Redis, key_prefix: str = "s"):
        super().__init__()
        log.debug("Create: RedisChatStateProvider")
        self.client = redis if isinstance(redis, Redis) else Redis.from_url(redis)
        self.prefix = key_prefix
        
    def get_key(self, sessionId):
        return f"{self.prefix}:{sessionId}"
        
    async def set_key_value(self, sessionId: str, key: str, value, ttl_in_seconds=None):
        hash_key = self.get_key(sessionId)
        self.client.hset(hash_key, key, json.dumps(value))
        if ttl_in_seconds:
            self.client.expire(hash_key, ttl_in_seconds)

    async def get_key_value(self, sessionId: str, key: str):
        hash_key = self.get_key(sessionId)
        value = self.client.hget(hash_key, key)
        if not value:
            return None
        return json.loads(value)

    async def clear_store(self, sessionId: str):
        hash_key = self.get_key(sessionId)
        self.client.delete(hash_key)

    async def clear_all_stores(self):
        hash_key = self.get_key("*")
        keys = self.client.keys(hash_key)
        if not keys:
            return
        for key in keys:
            self.client.delete(key)

    async def get_store(self, sessionId: str):
        hash_key = self.get_key(sessionId)
        store = self.client.hgetall(hash_key)
        if not store:
            return None
        s = {k.decode('utf-8'): json.loads(store[k]) for k in store}
        return s


    async def set_store(self, sessionId: str, store, ttl=None):
        hash_key = self.get_key(sessionId)
        for key in store:
            self.client.hset(hash_key, key, json.dumps(store[key]))
        if ttl:
            self.client.expire(hash_key, ttl)


