# Text to vector utilities for RAG Standard

from typing import Union, List, Dict, Any, Optional
import numpy as np

# Type alias for embeddings
Embedding = Union[np.ndarray, List[float], List[int]]

def normalize_embedding(embedding: Embedding) -> np.ndarray:
    """Normalize an embedding to a numpy array"""
    if isinstance(embedding, np.ndarray):
        return embedding
    elif isinstance(embedding, list):
        return np.array(embedding)
    else:
        raise ValueError(f"Unsupported embedding type: {type(embedding)}") 