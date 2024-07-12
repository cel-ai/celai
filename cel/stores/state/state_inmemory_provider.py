from cel.stores.state.base_state_provider import BaseChatStateProvider
from loguru import logger as log

class InMemoryStateProvider(BaseChatStateProvider):

    def __init__(self, key_prefix: str = "s"):
        super().__init__()
        log.warning(f"Create InMemoryStateProvider - Avoid using this in production.")
        self.store = {}
        self.prefix = key_prefix

    def get_key(self, sessionId):
        return f"{self.prefix}:{sessionId}"

    async def set_key_value(self, sessionId: str, key: str, value, ttl_in_seconds=None):
        hash_key = self.get_key(sessionId)
        if hash_key not in self.store:
            self.store[hash_key] = {}
        self.store[hash_key][key] = value

    async def get_key_value(self, sessionId: str, key: str):
        hash_key = self.get_key(sessionId)
        if hash_key in self.store and key in self.store[hash_key]:
            return self.store[hash_key][key]
        return None

    async def clear_store(self, sessionId: str):
        hash_key = self.get_key(sessionId)
        if hash_key in self.store:
            del self.store[hash_key]

    async def clear_all_stores(self):
        self.store = {}

    async def get_store(self, sessionId: str):
        hash_key = self.get_key(sessionId)
        if hash_key in self.store:
            return self.store[hash_key]
        return None

    async def set_store(self, sessionId: str, store, ttl=None):
        hash_key = self.get_key(sessionId)
        self.store[hash_key] = store