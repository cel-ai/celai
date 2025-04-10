from dataclasses import dataclass
from loguru import logger as log
import chromadb
from typing import List, Dict, Any, Optional, Union
import numpy as np
import os
from chromadb.config import Settings
from cel.rag_standard.text2vec import OpenAIEmbedding
from cel.rag_standard.stores.vector_store import VectorStore


class ChromaStore(VectorStore):
    """ChromaDB implementation of the VectorStore interface for RAG Standard"""
    
    def __init__(
        self,
        persist_directory: str = "./chroma_db",
        collection_name: str = "default_collection",
        openai_api_key: Optional[str] = None,
        openai_model: str = "text-embedding-3-small"
    ):
        """
        Initialize ChromaDB store with OpenAI embeddings
        
        Args:
            persist_directory: Directory to persist the database
            collection_name: Name of the collection to use
            openai_api_key: OpenAI API key (if None, will try to get from environment)
            openai_model: OpenAI embedding model to use
        """
        self.persist_directory = persist_directory
        self.collection_name = collection_name
        
        # Initialize OpenAI embedding
        self.embedding = OpenAIEmbedding(
            api_key=openai_api_key,
            model=openai_model
        )
        
        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(
            path=persist_directory,
            settings=Settings(
                anonymized_telemetry=False
            )
        )
        
        # Get or create collection
        self.collection = self._get_or_create_collection()
        
        log.info(f"Initialized ChromaStore with collection '{collection_name}'")
    
    def _get_or_create_collection(self) -> chromadb.Collection:
        """Get existing collection or create a new one"""
        try:
            return self.client.get_collection(
                name=self.collection_name,
                embedding_function=self.embedding.get_embedding_function()
            )
        except ValueError:
            log.info(f"Collection '{self.collection_name}' not found, creating new one")
            return self.client.create_collection(
                name=self.collection_name,
                embedding_function=self.embedding.get_embedding_function()
            )
    
    def add_documents(
        self,
        documents: List[str],
        ids: Optional[List[str]] = None,
        metadatas: Optional[List[Dict[str, Any]]] = None
    ) -> List[str]:
        """
        Add documents to the collection
        
        Args:
            documents: List of text documents to add
            ids: Optional list of IDs for the documents
            metadatas: Optional list of metadata dictionaries for the documents
            
        Returns:
            List of document IDs
        """
        if not documents:
            return []
            
        # Generate IDs if not provided
        if ids is None:
            ids = [f"doc_{i}" for i in range(len(documents))]
            
        # Add documents to collection
        self.collection.add(
            documents=documents,
            ids=ids,
            metadatas=metadatas
        )
        
        log.info(f"Added {len(documents)} documents to collection")
        return ids
    
    def search(
        self,
        query: str,
        n_results: int = 5,
        where: Optional[Dict[str, Any]] = None,
        where_document: Optional[Dict[str, Any]] = None
    ) -> Dict[str, List[Any]]:
        """
        Search for documents similar to the query
        
        Args:
            query: Search query
            n_results: Number of results to return
            where: Filter on metadata
            where_document: Filter on document content
            
        Returns:
            Dictionary with search results
        """
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results,
            where=where,
            where_document=where_document
        )
        
        return {
            "ids": results["ids"][0],
            "documents": results["documents"][0],
            "metadatas": results["metadatas"][0],
            "distances": results["distances"][0] if "distances" in results else None
        }
    
    def get_document(self, document_id: str) -> Dict[str, Any]:
        """
        Get a document by ID
        
        Args:
            document_id: ID of the document to retrieve
            
        Returns:
            Document data
        """
        result = self.collection.get(
            ids=[document_id]
        )
        
        if not result["ids"]:
            raise ValueError(f"Document with ID '{document_id}' not found")
            
        return {
            "id": result["ids"][0],
            "document": result["documents"][0],
            "metadata": result["metadatas"][0] if result["metadatas"] else None
        }
    
    def update_document(
        self,
        document_id: str,
        document: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Update a document
        
        Args:
            document_id: ID of the document to update
            document: New document text
            metadata: New metadata
        """
        self.collection.update(
            ids=[document_id],
            documents=[document] if document is not None else None,
            metadatas=[metadata] if metadata is not None else None
        )
        
        log.info(f"Updated document with ID '{document_id}'")
    
    def delete_document(self, document_id: str) -> None:
        """
        Delete a document
        
        Args:
            document_id: ID of the document to delete
        """
        self.collection.delete(
            ids=[document_id]
        )
        
        log.info(f"Deleted document with ID '{document_id}'")
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the collection
        
        Returns:
            Dictionary with collection statistics
        """
        count = self.collection.count()
        
        return {
            "collection_name": self.collection_name,
            "document_count": count
        }
    
    def reset_collection(self) -> None:
        """Delete and recreate the collection"""
        try:
            self.client.delete_collection(self.collection_name)
            log.info(f"Deleted collection '{self.collection_name}'")
        except ValueError:
            log.info(f"Collection '{self.collection_name}' does not exist")
            
        self.collection = self._get_or_create_collection()
        log.info(f"Recreated collection '{self.collection_name}'")
        
