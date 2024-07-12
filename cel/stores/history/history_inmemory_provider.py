import json
from loguru import logger as log
from cel.stores.history.base_history_provider import BaseHistoryProvider


class InMemoryHistoryProvider(BaseHistoryProvider):

    def __init__(self, key_prefix: str = "h"):
        self.store = {}
        self.key_prefix = key_prefix
        log.warning(f"Create: InMemoryHistoryProvider - Avoid using this in production.")

    def get_key(self, sessionId: str):
        return f"{self.key_prefix}:{sessionId}"

    async def append_to_history(self, sessionId: str, entry, metadata=None, ttl=None):
        key = self.get_key(sessionId)
        value = json.dumps(entry)
        if key not in self.store:
            self.store[key] = []
        self.store[key].append(value)

    async def get_history(self, sessionId: str):
        key = self.get_key(sessionId)
        values = self.store.get(key, [])
        res = [json.loads(v) for v in values]
        # remove None elements
        res = [r for r in res if r]

        return res

    async def clear_history(self, sessionId: str, keep_last_messages=None):
        key = self.get_key(sessionId)
        if keep_last_messages:
            self.store[key] = self.store[key][:keep_last_messages]
        else:
            self.store.pop(key, None)

    async def get_history_slice(self, sessionId: str, start, end):
        key = self.get_key(sessionId)
        history = self.store.get(key, [])[start:end]
        return [json.loads(h) for h in history]

    async def get_last_messages(self, sessionId: str, count):
        key = self.get_key(sessionId)
        history = self.store.get(key, [])[-count:]
        return [json.loads(h) for h in history]

    async def close_conversation(self, sessionId: str):
        raise NotImplementedError("Method not implemented.")