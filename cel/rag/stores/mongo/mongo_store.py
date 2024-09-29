from abc import ABC
from dataclasses import dataclass
from loguru import logger as log
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database
from pymongo.operations import SearchIndexModel
from cel.rag.stores.vector_store import VectorRegister, VectorStore
from cel.rag.text2vec.utils import Embedding, Text2VectorProvider
from cel.rag.text2vec.cached_openai import CachedOpenAIEmbedding
from typing import Optional


@dataclass
class VectorRegisterResult(VectorRegister):
    """Vector register result with distance for MongoDB Atlas Search"""
    distance: float


class AtlasStore(VectorStore):
    """Vector store implementation using MongoDB Atlas Search"""

    def __init__(
        self,
        text2vec_provider: Text2VectorProvider = None,
        collection_name: str = "my_collection",
        db_name: str = "my_database",
        mongo_uri: str = "mongodb://localhost:27017",
        index_name: str = "default",
        index_definition: dict = None,
        num_dimensions: Optional[int] = None,
    ):
        log.debug(
            f"Instantiate AtlasStore with collection_name: {collection_name}, db_name: {db_name}"
        )
        self.text2vec = text2vec_provider or CachedOpenAIEmbedding()
        self.client = MongoClient(mongo_uri)
        self.db: Database = self.client[db_name]
        self.collection: Collection = self.db[collection_name]
        self.index_name = index_name
        self.num_dimensions = num_dimensions

        self._ensure_index(index_definition)

    def _ensure_index(self, index_definition: dict):
        """Ensure that the required search index exists in the collection"""
        log.debug(f"Checking if index '{self.index_name}' exists on collection '{self.collection.name}'")
        
        # Use collection.list_search_indexes() to list existing search indexes
        cursor = self.collection.list_search_indexes()
        indexes = list(cursor)
        index_names = [index['name'] for index in indexes]

        if self.index_name in index_names:
            log.debug(f"Index '{self.index_name}' already exists")
        else:
            log.debug(f"Creating index '{self.index_name}'")
            if not index_definition:
                # Use default index definition if none provided
                # Get the dimension of the embeddings
                if self.num_dimensions is None:
                    log.debug("num_dimensions not provided")
                    # Try to infer num_dimensions from the text2vec_provider if possible
                    self.num_dimensions = self._infer_num_dimensions()
                    log.debug(f"Inferred num_dimensions: {self.num_dimensions}")
                if self.num_dimensions is None:
                    raise ValueError(
                        "num_dimensions is required to create the search index. "
                        "Please provide num_dimensions when initializing AtlasStore."
                    )
                index_definition = {
                    "mappings": {
                        "dynamic": False,
                        "fields": {
                            "embedding": {
                                "type": "knnVector",
                                "dimensions": self.num_dimensions,
                                "similarity": "cosine"  # Choose 'cosine', 'euclidean', or 'dotProduct' as needed
                            }
                        }
                    }
                }
            # Create the search index
            result = self.collection.create_search_index(SearchIndexModel(index_definition))
            log.debug(f"Search index created: {result}")

    def _infer_num_dimensions(self) -> Optional[int]:
        """Attempt to infer the number of dimensions from the text2vec_provider"""
        sample_text = "sample text to infer embedding dimension"
        try:
            sample_embedding = self.text2vec.text2vec(sample_text)
            if isinstance(sample_embedding, list):
                return len(sample_embedding)
            else:
                return None
        except Exception as e:
            log.warning(f"Could not infer embedding dimensions: {e}")
            return None

    def get_vector(self, id: str) -> VectorRegister:
        """Retrieve a vector register by its ID"""
        document = self.collection.find_one({"_id": id})
        if not document:
            raise ValueError(f"Document with id '{id}' not found")

        vector = document.get("embedding")
        text = document.get("text")
        metadata = document.get("metadata")

        return VectorRegister(id=id, vector=vector, text=text, metadata=metadata)

    def get_similar(self, vector: Embedding, top_k: int) -> list[VectorRegisterResult]:
        """Retrieve the most similar vectors to the given vector"""
        pipeline = [
            {
                '$search': {
                    'knnBeta': {
                        'vector': vector,
                        'path': 'embedding',
                        'k': top_k
                    }
                }
            },
            {
                '$project': {
                    '_id': 1,
                    'text': 1,
                    'metadata': 1,
                    'embedding': 1,
                    'score': {'$meta': 'searchScore'}
                }
            },
            {
                '$limit': top_k
            }
        ]
        results = list(self.collection.aggregate(pipeline))
        return [
            VectorRegisterResult(
                id=result['_id'],
                vector=result.get('embedding'),
                text=result.get('text'),
                metadata=result.get('metadata'),
                distance=result.get('score')
            )
            for result in results
        ]

    def search(self, query: str, top_k: int = 1) -> list[VectorRegisterResult]:
        """Search for vectors similar to the query text"""
        vector = self.text2vec.text2vec(query)
        return self.get_similar(vector, top_k)

    def upsert(self, id: str, vector: Embedding, text: str, metadata: dict):
        """Insert or update a vector in the store"""
        document = {
            '_id': id,
            'embedding': vector,
            'text': text,
            'metadata': metadata
        }
        self.collection.replace_one({'_id': id}, document, upsert=True)

    def upsert_text(self, id: str, text: str, metadata: dict):
        """Insert or update text in the store, computing its vector representation"""
        vector = self.text2vec.text2vec(text)
        self.upsert(id, vector, text, metadata)

    def delete(self, id):
        """Delete a vector from the store by its ID"""
        self.collection.delete_one({'_id': id})
