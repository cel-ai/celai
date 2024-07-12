from abc import ABC
import os
import time
from typing import cast
from diskcache import Cache
from cel.cache import get_cache
from .utils import Embedding, Embeddings, Text2VectorProvider

try:
    from openai import OpenAI
except ImportError:
    raise ValueError(
        "The openai python package is not installed. Please install it with `pip install openai`"
    )
    
cache = get_cache()
CACHE_TAG = 'oaie'
CACHE_EXPIRE = None
DEFAULT_MAX_RETRIES = 5

class CachedOpenAIEmbedding(Text2VectorProvider):
    """A wrapper around the OpenAI API that caches the results of text2vec calls.
    Uses diskcache to cache the results of text2vec calls.
    Usefull for reducing the number of API calls to OpenAI Embedding API.
    For example, if you are using ChromaDB every time you boot up your application, 
    Chroma needs to be re-embedded. This can be time consuming and costly.
    This class will cache the results of the text2vec calls, so that the next time you boot up your application,
    the embeddings will be retrieved from the cache.

    
    Parameters:
    api_key: str
        The OpenAI API key. If not provided, it will look for the OPENAI_API_KEY environment variable.
    model: str
        The OpenAI model to use. Default is "text-embedding-3-small"
    max_retries: int
        The maximum number of retries to make when the API call fails. Default is 5.
    kwargs: dict
    """
    
    def __init__(self, api_key: str = None, model: str = "text-embedding-3-small", max_retries: int = DEFAULT_MAX_RETRIES):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model

        if self.api_key is not None:
            OpenAI.api_key = api_key
        # If the api key is still not set, raise an error
        elif OpenAI.api_key is None:
            raise ValueError(
                "Please provide an OpenAI API key. You can get one at https://platform.openai.com/account/api-keys"
            )
            
        
        self.max_retries = max_retries

    def text2vec(self, text: str) -> Embedding:
        return openai_cached_text2vec(text, self.model, self.max_retries)
    
    def texts2vec(self, texts: list[str]) -> list[Embedding]:
        return [self.text2vec(text) for text in texts]
    
    
    
    
@cache.memoize(typed=True, expire=CACHE_EXPIRE, tag=CACHE_TAG)
def openai_cached_text2vec(text: str, model: str, max_retries: int = 3) -> list[float]:
    
    client = OpenAI(max_retries=max_retries)

    # replace newlines, which can negatively affect performance.
    text = text.replace("\n", " ")

    response = client.embeddings.create(input=[text], model=model)
    embeddings = response.data[0].embedding
    return embeddings
    
