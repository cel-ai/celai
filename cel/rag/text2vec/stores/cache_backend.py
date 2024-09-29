from abc import ABC, abstractmethod

class CacheBackend(ABC):
    @abstractmethod
    def memoize(self, typed: bool, expire: int, tag: str):
        pass