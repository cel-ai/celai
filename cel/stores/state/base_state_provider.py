from abc import ABC, abstractmethod


class BaseChatStateProvider(ABC):
    @abstractmethod
    def get_key(self, sessionId: str):
        pass

    @abstractmethod
    def set_key_value(self, sessionId: str, key, value, ttl_in_seconds=None):
        pass

    @abstractmethod
    def get_key_value(self, sessionId: str, key):
        pass

    @abstractmethod
    def clear_store(self, sessionId: str):
        pass

    @abstractmethod
    def clear_all_stores(self, key_pattern: str = None):
        pass

    @abstractmethod
    def get_store(self, sessionId: str):
        pass

    @abstractmethod
    def set_store(self, sessionId: str, store, ttl=None):
        pass
