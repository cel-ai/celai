from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

class VectorStore(ABC):
    """Abstract base class for vector stores in RAG Standard"""
    
    @abstractmethod
    def add_documents(
        self,
        documents: List[str],
        ids: Optional[List[str]] = None,
        metadatas: Optional[List[Dict[str, Any]]] = None
    ) -> List[str]:
        """Add documents to the store"""
        pass
    
    @abstractmethod
    def search(
        self,
        query: str,
        n_results: int = 5,
        where: Optional[Dict[str, Any]] = None,
        where_document: Optional[Dict[str, Any]] = None
    ) -> Dict[str, List[Any]]:
        """Search for documents similar to the query"""
        pass
    
    @abstractmethod
    def get_document(self, document_id: str) -> Dict[str, Any]:
        """Get a document by ID"""
        pass
    
    @abstractmethod
    def update_document(
        self,
        document_id: str,
        document: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Update a document"""
        pass
    
    @abstractmethod
    def delete_document(self, document_id: str) -> None:
        """Delete a document"""
        pass

class VectorRegister:
    """Registry for vector store implementations"""
    
    _stores: Dict[str, type] = {}
    
    @classmethod
    def register(cls, name: str, store_class: type) -> None:
        """Register a vector store implementation"""
        if not issubclass(store_class, VectorStore):
            raise ValueError(f"Store class must inherit from VectorStore")
        cls._stores[name] = store_class
    
    @classmethod
    def get_store(cls, name: str) -> type:
        """Get a registered vector store implementation"""
        if name not in cls._stores:
            raise ValueError(f"Vector store '{name}' not found")
        return cls._stores[name]
    
    @classmethod
    def list_stores(cls) -> List[str]:
        """List all registered vector store implementations"""
        return list(cls._stores.keys()) 