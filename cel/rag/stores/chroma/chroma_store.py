
from abc import ABC
from dataclasses import dataclass
from loguru import logger as log
import chromadb
from cel.rag.stores.vector_store import VectorRegister, VectorStore
from cel.rag.text2vec.utils import Embedding, Text2VectorProvider



@dataclass
class VectorRegisterResult(VectorRegister):
    """Vector register for ChromaDB"""
    distance: float
    

class ChromaStore(VectorStore):
    
    def __init__(self, text2vec_provider: Text2VectorProvider, collection_name: str = "my_collection"):
        log.debug(f"Instantiate ChromaStore with collection_name: {collection_name}")
        self.text2vec = text2vec_provider
        self.client = chromadb.Client()
        self.collection_name = collection_name
        
        # create collection if not exists
        collections = self.client.list_collections()
        for collection in collections:
            if collection.name == collection_name:
                self.collection = collection
                log.debug(f"Collection {collection_name} already exists")
                break
        else:
            log.debug(f"Creating collection {collection_name}")
            self.collection = self.client.create_collection(
                            name=collection_name,
                        )

    def get_vector(self, id: str) -> VectorRegister:
        """Get a vector chromadb by id"""
        v = self.collection.get(id, include=['documents', 'metadatas', 'embeddings'])
        # create a VectorRegister object
        return VectorRegister(id=id,
                                vector=v['embeddings'][0],
                                text=v['documents'][0],
                                metadata=v['metadatas'][0])
        

    def get_similar(self, vector: Embedding, top_k) -> list[VectorRegisterResult]:
        """Get the most similar vectors to the given vector"""
        res = self.collection.query(
            query_embeddings=[vector],
            n_results=top_k,
            include=['documents', 'metadatas', 'distances', 'embeddings']
        )
        
        return [VectorRegisterResult(id=id, 
                               vector=embedding, 
                               distance=distance,
                               text=text,
                               metadata=metadata) for id, embedding, distance, text, metadata in zip(res['ids'][0],
                                                                                        res['embeddings'][0],
                                                                                        res['distances'][0],
                                                                                        res['documents'][0], 
                                                                                        res['metadatas'][0])]   
                

    def search(self, query: str, top_k: int = 1) -> list[VectorRegisterResult]:
        """Search for vectors by a query"""
        
        vector = self.text2vec.text2vec(query)
        res = self.collection.query(
            query_embeddings=[vector],
            n_results=top_k,
            include=['documents', 'metadatas', 'distances', 'embeddings']
        )

        # convert QueryResult to VectorRegister
        # res sample: {'data': None, 'distances': [[0.7714858651161194, 1.6371256113052368]], 'documents': [['This is a document about parrots', 'This is a document about pineapple']], 'ids': [['4', '0']], 'metadatas': [[{'metadata': 'metadata'}, {'metadata': 'metadata'}]]}
        return [VectorRegisterResult(id=id, 
                               vector=embedding, 
                               distance=distance,
                               text=text,
                               metadata=metadata) for id, embedding, distance, text, metadata in zip(res['ids'][0],
                                                                                        res['embeddings'][0],
                                                                                        res['distances'][0],
                                                                                        res['documents'][0], 
                                                                                        res['metadatas'][0])]   
        

        
        

    def upsert(self, id: str, vector: Embedding, text: str, metadata: dict):
        """Upsert a vector to the store"""
        self.collection.add(
            documents=text,
            ids=[id],
            metadatas=metadata
        )
        
    def upsert_text(self, id: str, text: str, metadata: dict):
        """Upsert a vector to the store"""
        vector =  self.text2vec.text2vec(text)
        self.collection.add(
            ids=[id],
            documents=text,
            metadatas=metadata,
            embeddings=vector
        )

    def delete(self, id):
        """Delete a vector from the store"""
        self.collection.delete(id)