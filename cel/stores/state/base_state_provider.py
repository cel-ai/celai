from abc import ABC, abstractmethod


class BaseChatStateProvider(ABC):
    """Contract for chat state providers.

    Every accessor is a coroutine: providers are called from the gateway event
    loop, so implementations must not block it.
    """

    @abstractmethod
    def get_key(self, sessionId: str) -> str:
        raise NotImplementedError

    @abstractmethod
    async def set_key_value(self, sessionId: str, key, value, ttl_in_seconds=None):
        raise NotImplementedError

    @abstractmethod
    async def get_key_value(self, sessionId: str, key):
        raise NotImplementedError

    @abstractmethod
    async def clear_store(self, sessionId: str):
        raise NotImplementedError

    @abstractmethod
    async def clear_all_stores(self):
        raise NotImplementedError

    @abstractmethod
    async def get_store(self, sessionId: str) -> dict | None:
        raise NotImplementedError

    @abstractmethod
    async def set_store(self, sessionId: str, store, ttl=None):
        raise NotImplementedError
