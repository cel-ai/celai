from typing import List, Optional
from dataclasses import dataclass, field
from cel.model.common import ContextMessage
from cel.rag.providers.rag_retriever import RAGRetriever
from cel.rag.stores.vector_store import VectorRegister
from langchain_openai import ChatOpenAI
from langchain_core.messages import (
    SystemMessage
)

DEFAULT_PROMPT = (
    "You are an AI assistant specialized in transforming conversation inputs into well-structured and context-aware queries for retrieval-augmented generation (RAG). "
    "Your goal is to analyze the conversation history and refine the user's query to maximize its relevance and effectiveness for vectorization and retrieval, without changing the original intent. "
    "Focus on capturing the key context, entities, and intent from the conversation to generate concise, precise, and highly actionable queries. "
    "Avoid introducing unnecessary complexity or irrelevant details. When refining, ensure the enhanced query naturally aligns with the context and flow of the conversation."
)

@dataclass
class QueryRefiner:
    model_name: str = "gpt-3.5-turbo"
    n_history_messages: int = 3
    custom_prompt: str = DEFAULT_PROMPT
    temperature: float = 0.0
    max_tokens: int = 50
    llm: Optional[ChatOpenAI] = field(init=False, default=None)

    def __post_init__(self):
        self.llm = ChatOpenAI(
            model=self.model_name,
            temperature=self.temperature,
            max_tokens=self.max_tokens
        )

    def enhance_query(self, query: str, history: List[ContextMessage]) -> str:

        enhanced_query = query

        if history:
            history_context = "\n".join(
                [f"User: {msg.content}" for msg in history[-self.n_history_messages:]])
            prompt = f"{self.custom_prompt}\n\nHistory:\n{history_context}\n\nUser Query: {query}\n\nEnhanced Query:"

            response = self.llm.invoke([SystemMessage(content=prompt)])

            if response and isinstance(response, SystemMessage):
                enhanced_query = response.content

        return enhanced_query


class EnhancedRetriever(RAGRetriever):
    def __init__(self, base_retriever: RAGRetriever, query_builder: QueryRefiner = None):
        self.base_retriever = base_retriever
        self.query_builder = query_builder or QueryRefiner()

    def search(self,
               query: str,
               top_k: int = 1,
               history: List[ContextMessage] = None,
               state: dict = {}) -> List[VectorRegister]:
        # Use the QueryBuilder to enhance the query
        enhanced_query = self.query_builder.enhance_query(query, history)
        # Call the base retriever with the enhanced query
        return self.base_retriever.search(enhanced_query, top_k)
