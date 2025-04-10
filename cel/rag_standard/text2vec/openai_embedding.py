import os
from typing import List, Optional
from loguru import logger as log
from chromadb.utils import embedding_functions


class OpenAIEmbedding:
    """OpenAI embedding implementation for text-to-vector conversion"""
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "text-embedding-3-small"
    ):
        """
        Initialize OpenAI embedding
        
        Args:
            api_key: OpenAI API key (if None, will try to get from environment)
            model: OpenAI embedding model to use
        """
        # Get OpenAI API key from environment if not provided
        if api_key is None:
            api_key = os.environ.get("OPENAI_API_KEY")
            if api_key is None:
                raise ValueError("OpenAI API key must be provided or set in OPENAI_API_KEY environment variable")
        
        self.api_key = api_key
        self.model = model
        
        # Initialize OpenAI embedding function
        self.embedding_function = embedding_functions.OpenAIEmbeddingFunction(
            api_key=self.api_key,
            model_name=self.model
        )
        
        log.info(f"Initialized OpenAI embedding with model '{model}'")
    
    def get_embedding_function(self):
        """
        Get the ChromaDB embedding function
        
        Returns:
            ChromaDB OpenAI embedding function
        """
        return self.embedding_function
    
    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """
        Embed a list of texts
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of embeddings
        """
        return self.embedding_function(texts)
    
    def embed_query(self, query: str) -> List[float]:
        """
        Embed a single query text
        
        Args:
            query: Query text to embed
            
        Returns:
            Embedding vector
        """
        return self.embedding_function([query])[0] 