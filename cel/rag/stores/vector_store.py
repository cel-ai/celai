# Vector store abstract class

from abc import ABC
from abc import abstractmethod
from dataclasses import dataclass
from typing import Union
import numpy as np
from cel.rag.text2vec.utils import Embedding


@dataclass
class VectorRegister(ABC):
    id: str
    vector: np.ndarray
    text: str
    metadata: dict

    def __str__(self):
        return f"{self.text}"


class VectorStore(ABC):
    """Base class for vector stores. A vector store is a class that stores and retrieves by similarity and id.
    For simplicity, the vector store will define the embedding model to be used.
    We strongly recommend implement your own vector store flavor to suit your needs, combining the vector store
    with a database or a cache system and a embedding model of your choice.
    """
    
    @abstractmethod
    def get_vector(self, id: str) -> VectorRegister:
        """Get the vector representation of an id"""
        pass
    
    @abstractmethod
    def get_similar(self, vector: Embedding, top_k: int) -> list[VectorRegister]:
        """Get the most similar vectors to the given vector"""
        pass
    
    @abstractmethod
    def search(self, query: str, top_k: int) -> list[VectorRegister]:
        """Search for vectors by a query"""
        pass

    @abstractmethod
    def upsert(self, id: str, vector: Embedding, text: str, metadata: dict):
        """Upsert a vector to the store"""
        pass
    
    @abstractmethod
    def upsert_text(self, id: str, text: str, metadata: dict):
        """Upsert a text to the store"""
        pass
    
    @abstractmethod
    def delete(self, id: str):
        """Delete a vector from the store"""
        pass