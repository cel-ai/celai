
from typing import Union
import cachetools
from .key_value_store import KeyValueStore, ListStore


class MemoryCache(KeyValueStore):
    """MemoryCache is a CacheStore implementation that stores cache data in memory using cachetools.LRUCache.
    
    Args:
        key_prefix (str): A key prefix for the cache store.
        memory_maxsize (int): The maximum number of items to store in the cache.
    """
    
    
    def __init__(self, key_prefix, memory_maxsize=1000):
        self.cache = cachetools.LRUCache(maxsize=memory_maxsize)
        self.key_prefix = key_prefix

    def get(self, key, callback=None):
        """Retrieves the value associated with the given key from the cache.
        
        If the key is not in the cache, it calls the provided callback function to compute the value.
        
        Args:
            key (str): The cache key.
            callback (callable): A function that computes the value for the given key if it is not in the cache (optional).
        
        Returns:
            The value associated with the key, or None if the key is not in the cache.
        """
        
        data = self.cache.get(key)
        if data is not None:
            return data
        
        if callback:
            data = callback()
            if data is not None:
                self.set(key, data)
                return data

        return None

    
    def set(self, key, value):
        """Sets the value for the given key in the cache.
        
        Args:
            key (str): The cache key.
            value (any): The value to store in the cache.
        """
        self.cache[key] = value
        
    def get_all(self):
        """Returns all items in the cache.
        
        Returns:
            A list of key-value pairs in the cache.
        """
        return self.cache.items()

    def delete(self, key):
        """Deletes the key from the cache.
        
        Args:
            key (str): The cache key.
        """
        self.cache.pop(key, None)
       
    def clear(self):
        """Clears the cache."""
        self.cache.clear()
    
    def all(self):
        """Returns all items in the cache.
        
        Returns:
            A list of key-value pairs in the cache.
        """
        return self.cache.items()
    
