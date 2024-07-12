import threading
from diskcache import Cache
import functools
from cel.config import CACHE_DEFAULT_SETTINGS, CACHE_DIRECTORY



def singleton(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if wrapper.instance is None:
            with wrapper.lock:
                if wrapper.instance is None:
                    wrapper.instance = func(*args, **kwargs)
        return wrapper.instance

    wrapper.lock = threading.Lock()
    wrapper.instance = None
    return wrapper

@singleton
def get_cache(directory: str = CACHE_DIRECTORY, **settings):
    return Cache(directory, **{**CACHE_DEFAULT_SETTINGS, **settings})