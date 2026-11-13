from diskcache_community import Cache, SafeDisk
from .base_cache import BaseCache

class DiskCache(BaseCache):
    def __init__(self, cache_dir: str):
        self.cache = Cache(cache_dir, disk=SafeDisk.with_options(on_error="miss"))

    def memoize(self, typed: bool, expire: int, tag: str):
        return self.cache.memoize(typed=typed, expire=expire, tag=tag)