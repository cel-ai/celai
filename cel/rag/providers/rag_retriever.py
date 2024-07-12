from cel.model.common import ContextMessage
from cel.rag.stores.vector_store import VectorRegister


from abc import abstractmethod


class RAGRetriever:
    @abstractmethod
    def search(self,
                query: str,
                top_k: int = 1,
                history: list[ContextMessage] = None,
                state: dict = {}) -> list[VectorRegister]:
        raise NotImplementedError()