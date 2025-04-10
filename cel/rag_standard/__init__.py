"""
RAG Standard - Retrieval Augmented Generation

This package provides a standardized implementation of the RAG functionality
compared to the original cel.rag package. It offers better type hints,
error handling, and a more consistent API.
"""

from cel.rag_standard.stores import VectorStore, VectorRegister, ChromaStore
from cel.rag_standard.text2vec import Embedding, normalize_embedding
from cel.rag_standard.migration import migrate_store, create_migration_guide

__version__ = "1.0.0"

__all__ = [
    'VectorStore',
    'VectorRegister',
    'ChromaStore',
    'Embedding',
    'normalize_embedding',
    'migrate_store',
    'create_migration_guide',
] 