from abc import ABC
import os
import time
from typing import cast
from diskcache import Cache
from cel.cache import get_cache
from .cache.base_cache import BaseCache
from .cache.disk_cache import DiskCache
from .utils import Embedding, Text2VectorProvider

try:
    from openai import OpenAI
except ImportError:
    raise ValueError(
        "The openai python package is not installed. Please install it with `pip install openai`"
    )

class CachedOpenAIEmbedding(Text2VectorProvider):
    """A wrapper around the OpenAI API that caches the results of text2vec calls.
    Uses diskcache to cache the results of text2vec calls.
    Useful for reducing the number of API calls to OpenAI Embedding API.
    For example, if you are using ChromaDB every time you boot up your application, 
    Chroma needs to be re-embedded. This can be time consuming and costly.
    This class will cache the results of the text2vec calls, so that the next time you boot up your application,
    the embeddings will be retrieved from the cache.

    Parameters:
    api_key: str
        The OpenAI API key. If not provided, it will look for the OPENAI_API_KEY environment variable.
    model: str
        The OpenAI model to use. Default is "text-embedding-3-small"
    cache_backend: CacheBackend
        The cache backend to use. Default is DiskCacheBackend.
    max_retries: int
        The maximum number of retries to make when the API call fails. Default is 5.
    cache_expire: int
        The cache expiration time in milliseconds. Default is 12 hours (43200000 ms).
    """
    
    def __init__(self, api_key: str = None, model: str = "text-embedding-3-small", cache_backend: BaseCache = None, max_retries: int = 5, CACHE_EXPIRE: int = 43200000):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model
        self.cache_backend = cache_backend or DiskCache(cache_dir='/tmp/diskcache')
        self.max_retries = max_retries
        self.cache_expire = CACHE_EXPIRE
        self.cache_tag = 'openai_embedding'

        if self.api_key is not None:
            OpenAI.api_key = api_key
        # If the api key is still not set, raise an error
        elif OpenAI.api_key is None:
            raise ValueError(
                "Please provide an OpenAI API key. You can get one at https://platform.openai.com/account/api-keys"
            )

    def text2vec(self, text: str) -> Embedding:
        return self._cached_text2vec(text, self.model, self.max_retries)
    
    def texts2vec(self, texts: list[str]) -> list[Embedding]:
        return [self.text2vec(text) for text in texts]

    @property
    def _cached_text2vec(self):
        return self.cache_backend.memoize(typed=True, expire=self.cache_expire, tag=self.cache_tag)(openai_cached_text2vec)

def openai_cached_text2vec(text: str, model: str, max_retries: int = 3) -> list[float]:
    client = OpenAI(max_retries=max_retries)

    # replace newlines, which can negatively affect performance.
    text = text.replace("\n", " ")

    response = client.embeddings.create(input=[text], model=model)
    embeddings = response.data[0].embedding
    return embeddings