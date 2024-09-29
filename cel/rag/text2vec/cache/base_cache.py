from abc import ABC, abstractmethod

class BaseCache(ABC):
    @abstractmethod
    def memoize(self, typed: bool, expire: int, tag: str):
        pass