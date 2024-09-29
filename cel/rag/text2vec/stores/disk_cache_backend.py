from diskcache import Cache
from .cache_backend import CacheBackend

class DiskCacheBackend(CacheBackend):
    def __init__(self, cache_dir: str):
        self.cache = Cache(cache_dir)

    def memoize(self, typed: bool, expire: int, tag: str):
        return self.cache.memoize(typed=typed, expire=expire, tag=tag)