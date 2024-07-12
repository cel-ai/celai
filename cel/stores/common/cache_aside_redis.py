
import json
import threading
import time
import cachetools
import redis as redis_module
from .key_value_store import KeyValueStore

Redis = redis_module.client.Redis
 
class MemRedisCacheAside(KeyValueStore):
    """Implements a cache-aside pattern with memory and Redis cache.

    This class uses both an in-memory cache (using cachetools) and a Redis cache for storing data.
    The in-memory cache is used for fast access, while the Redis cache provides persistence and can be shared across multiple instances.

    Attributes:
        redis_client: A StrictRedis client connected to the Redis server.
        cache: An in-memory LRU cache.
        key_prefix: A prefix added to all keys stored in the Redis cache.
        ttl: The time-to-live (in seconds) for keys in the Redis cache.
        wait_for_redis: A flag indicating whether to wait for Redis operations to complete.
    """

    def __init__(self, redis: str | Redis , key_prefix, memory_maxsize=1000, ttl=60, wait_for_redis=False):
        """Initializes the cache with the given parameters."""
        self.redis_client = redis if isinstance(redis, Redis) else redis_module.StrictRedis.from_url(redis)
        self.cache = cachetools.LRUCache(maxsize=memory_maxsize)
        self.key_prefix = key_prefix
        self.ttl = ttl
        self.wait_for_redis = wait_for_redis

    def set_wait_for_redis(self, wait_for_redis):
        """Sets the wait_for_redis flag. When True, the cache will wait for Redis write operations to complete."""
        self.wait_for_redis = wait_for_redis

    def get(self, key, callback=None):
        """Retrieves the value associated with the given key from the cache.

        If the key is not in the in-memory cache, it tries to retrieve it from the Redis cache.
        If the key is not in the Redis cache either, it calls the provided callback function to compute the value.

        callback: A function that computes the value for the given key if it is not in the cache (optional).
        """        
        data = self.cache.get(key)
        if data is not None:
            return data

        data = self.redis_client.get(self.key_prefix + key)
        if data is not None:
            data = json.loads(data)
            self.cache[key] = data
            return data
        
        if callback:
            data = callback()
            if data is not None:
                self.set(key, data)
                return data

        return None

    def set(self, key, value):
        """Sets the value for the given key in both the in-memory and Redis caches.

        If wait_for_redis is False, the Redis operation is performed in a separate thread. 
        Useful for write-heavy workloads.
        """        
        # Update the in-memory cache
        self.cache[key] = value

        if not self.wait_for_redis:
            # update redis in a separate thread in background
            threading.Thread(target=self.redis_client.setex, args=(self.key_prefix + key, self.ttl, json.dumps(value))).start()
        else:
            #avoid  redis.exceptions.DataError: Invalid input of type: 'dict'. Convert to a bytes, string, int or float first.
            self.redis_client.setex(self.key_prefix + key, self.ttl, json.dumps(value))

    def get_all(self):
        """Returns all items in the in-memory cache."""
        return self.cache.items()

    def delete(self, key):
        """Deletes the key from the in-memory cache."""
        self.cache.pop(key, None)
    
    def delete_redis(self, key):
        """Deletes the key from the Redis cache."""
        self.redis_client.delete(self.key_prefix + key)

    def clear(self):
        """Clears the in-memory cache."""
        self.cache.clear()

    def clear_redis(self):
        """Clears the Redis cache."""
        # delete all keys with the prefix
        keys = self.redis_client.keys(self.key_prefix + '*')
        if keys:
            self.redis_client.delete(*keys)
        


# if __name__ == '__main__':

    # import os
    # from dotenv import dotenv_values
    # config = {
    #     **dotenv_values("example/.env"),    # load development variables
    #     **os.environ,               # override loaded values with environment variables
    # }


    # # Example usage
    # cache = MemRedisCacheAside(
    #     redis_url=config['REDIS_URL'],
    #     key_prefix='cache:',
    #     memory_maxsize=1000,
    #     ttl=60,
    #     wait_for_redis=True
    # )

    # # Set a chat lead into cache
    # lead = gen_event('signature1')
    # id = lead['lead']['signature']
    # cache.set(id, lead)

    # # Get the chat lead from cache
    # l = cache.get(id)
    # # print type of l
    # print(type(l))
    # # print the chat lead id
    # print("Recovered Id:" + l['lead']['signature'])


    # print("Testing performance for wait_for_redis=True")
    # print("---------------------------------------------------")
    # start = time.time()
    # # set 20 keys
    # for i in range(20):
    #     lead = gen_event(f'signature{i}')
    #     id = lead['lead']['signature']
    #     cache.set(id, lead)

    # end = time.time()
    # print(f"Time spent setting 20 keys: {end - start}")

    # print("\n\n\n")


    # print("Testing performance for wait_for_redis=False")
    # print("---------------------------------------------------")
    # cache.set_wait_for_redis(False)
    # start = time.time()
    # # set 20 keys
    # for i in range(20):
    #     lead = gen_event(f'signature{i}')
    #     id = lead['lead']['signature']
    #     cache.set(id, lead)

    # end = time.time()
    # print(f"Time spent setting 20 keys: {end - start}")