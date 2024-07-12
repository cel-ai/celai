from abc import ABC, abstractmethod


class KeyValueStore(ABC):
    
    @abstractmethod
    def get(self, key, callback=None):
        raise NotImplementedError()

    @abstractmethod
    def set(self, key, value, ttl=None):
        raise NotImplementedError()

    @abstractmethod
    def delete(self, key):
        raise NotImplementedError()
    
    @abstractmethod
    def clear(self):
        raise NotImplementedError()
    
    @abstractmethod
    def get_all(self):
        raise NotImplementedError()



class ListStore(ABC):
    
    @abstractmethod
    def list_append(self, key, value, ttl=None):
        raise NotImplementedError()
    
    @abstractmethod
    def list_clear(self, key):
        raise NotImplementedError()
    
    @abstractmethod
    def list_get(self, key):
        raise NotImplementedError()
    
    @abstractmethod
    def list_get_last(self, key, count: int):
        raise NotImplementedError()
    
