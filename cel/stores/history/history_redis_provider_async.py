import json
from cel.stores.common.key_value_store import ListStore
from cel.stores.history.base_history_provider import BaseHistoryProvider



class RedisHistoryProviderAsync(BaseHistoryProvider):

    def __init__(self, store: ListStore, key_prefix: str = "h", ttl=None):
        """ Create a new RedisHistoryProviderAsync instance.
        :param store: Redis store
        :param key_prefix: Prefix for the keys
        :param ttl: Time to live in seconds for history. If None, it will never expire
        """
        
        print(f"Create: RedisHistoryProviderAsync")
        self.store = store
        self.key_prefix = key_prefix
        self.ttl = ttl

    def get_key(self, sessionId: str):
        return f"{self.key_prefix}:{sessionId}"

    async def append_to_history(self, sessionId: str, entry, metadata=None, ttl=None):
        key = self.get_key(sessionId)
        value = json.dumps(entry)
        await self.store.list_append(key, value, self.ttl or ttl)


    async def get_history(self, sessionId: str):
        key = self.get_key(sessionId)
        values = await self.store.list_get(key)
        res = [json.loads(v) for v in values]
        # remove None elements
        res = [r for r in res if r]
        return res
        

    async def clear_history(self, sessionId: str, keep_last_messages=None):
        key = self.get_key(sessionId)

        if keep_last_messages:
            # self.client.ltrim(key, 0, keep_last_messages)
            msgs = await self.store.list_get_last(key, keep_last_messages)
            await self.store.list_clear(key)
            for msg in msgs:
                await self.store.list_append(key, msg)
                
        else:
            await self.store.list_clear(key)


    async def get_last_messages(self, sessionId: str, count):
        key = self.get_key(sessionId)
        # history = self.client.lrange(key, -count, -1)
        history = await self.store.list_get_last(key, count)
        return [json.loads(h) for h in history]

    async def close_conversation(self, sessionId: str):
        raise NotImplementedError("Method not implemented.")
    

