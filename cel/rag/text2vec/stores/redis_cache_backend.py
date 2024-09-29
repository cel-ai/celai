import redis
from .cache_backend import CacheBackend

class RedisCacheBackend(CacheBackend):
    def __init__(self, host: str, port: int, db: int):
        self.client = redis.StrictRedis(host=host, port=port, db=db)

    def memoize(self, typed: bool, expire: int, tag: str):
        def decorator(func):
            def wrapper(*args, **kwargs):
                key = f"{tag}:{args}:{kwargs}" if typed else f"{tag}:{args}"
                cached_result = self.client.get(key)
                if cached_result:
                    return eval(cached_result)
                result = func(*args, **kwargs)
                if result is not None:
                    self.client.setex(key, expire, str(result))
                return result
            return wrapper
        return decorator