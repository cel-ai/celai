from abc import ABC
import os
import time
from typing import cast
from diskcache import Cache

from cel.cache import get_cache
from .utils import Embedding, Embeddings, Text2VectorProvider

try:
    import ollama
except ImportError:
    raise ValueError(
        "The Ollama library is required for this example. Please install it by running: pip install ollama"
    )
    
cache = get_cache()
CACHE_TAG = 'ollama'
CACHE_EXPIRE = None
DEFAULT_MAX_RETRIES = 5

class CachedOllamaEmbedding(Text2VectorProvider):
    """A wrapper around the Ollama library that caches the results of the embeddings calls.
    Uses diskcache to cache the results of text2vec calls.
    Usefull for reducing the number of API calls
    For example, if you are using ChromaDB every time you boot up your application, 
    Chroma needs to be re-embedded. This can be time consuming and costly.
    This class will cache the results of the text2vec calls, so that the next time you boot up your application,
    the embeddings will be retrieved from the cache.

    
    Parameters:
    model: str
        Ollama embedding models, check the Ollama documentation for the available models.
        https://ollama.com/library
        default: "mxbai-embed-large"
    """
    
    def __init__(self, model: str = "mxbai-embed-large"):
        self.model = model


    def text2vec(self, text: str) -> Embedding:
        return ollama_cached_text2vec(text, self.model)
    
    def texts2vec(self, texts: list[str]) -> list[Embedding]:
        return [self.text2vec(text) for text in texts]
    
    
    
    
@cache.memoize(typed=True, expire=CACHE_EXPIRE, tag=CACHE_TAG)
def ollama_cached_text2vec(text: str, model: str) -> list[float]:
    response = ollama.embeddings(model=model, prompt=text)
    embedding = response["embedding"]
    return embedding
    
