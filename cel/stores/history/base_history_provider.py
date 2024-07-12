from abc import ABC, abstractmethod


class BaseHistoryProvider(ABC):
    @abstractmethod
    async def append_to_history(self, sessionId, entry, metadata=None, ttl=None):
        raise NotImplementedError

    @abstractmethod
    async def get_history(self, sessionId) -> list:
        raise NotImplementedError

    @abstractmethod
    async def clear_history(self, sessionId, keep_last_messages=None):
        raise NotImplementedError

    @abstractmethod
    async def get_last_messages(self, sessionId, count) -> list:
        raise NotImplementedError

    @abstractmethod
    async def close_conversation(self, sessionId):
        raise NotImplementedError

