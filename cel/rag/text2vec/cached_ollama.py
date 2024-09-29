from .cache.base_cache import BaseCache
from .cache.disk_cache import DiskCache
from .utils import Embedding, Text2VectorProvider

try:
    import ollama
except ImportError:
    raise ValueError(
        "The Ollama library is required for this example. Please install it by running: pip install ollama"
    )



class CachedOllamaEmbedding(Text2VectorProvider):
    """A wrapper around the Ollama library that caches the results of the embeddings calls.
    Uses diskcache to cache the results of text2vec calls.
    Useful for reducing the number of API calls
    For example, if you are using ChromaDB every time you boot up your application, 
    Chroma needs to be re-embedded. This can be time consuming and costly.
    This class will cache the results of the text2vec calls, so that the next time you boot up your application,
    the embeddings will be retrieved from the cache.

    Parameters:
    model: str
        Ollama embedding models, check the Ollama documentation for the available models.
        https://ollama.com/library
        default: "mxbai-embed-large"
    cache_backend: CacheBackend
        The cache backend to use. Default is DiskCacheBackend.
    """
    
    def __init__(self, model: str = "mxbai-embed-large", cache_backend: BaseCache = None, CACHE_EXPIRE=86400):
        self.model = model
        self.cache_backend = cache_backend or DiskCache(cache_dir='/tmp/diskcache')
        self.cache_expire = CACHE_EXPIRE
        self.cache_tag= 'ollama'

    def text2vec(self, text: str) -> Embedding:
        return self._cached_text2vec(text, self.model)
    
    def texts2vec(self, texts: list[str]) -> list[Embedding]:
        return [self.text2vec(text) for text in texts]

    @property
    def _cached_text2vec(self):
        return self.cache_backend.memoize(typed=True, expire=self.cache_expire, tag=self.cache_tag)(ollama_cached_text2vec)

def ollama_cached_text2vec(text: str, model: str) -> list[float]:
    response = ollama.embeddings(model=model, prompt=text)
    embedding = response["embedding"]
    return embedding