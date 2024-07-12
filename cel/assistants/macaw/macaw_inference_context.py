from cel.assistants.common import FunctionDefinition
from cel.assistants.macaw.macaw_settings import MacawSettings
from cel.gateway.model.conversation_lead import ConversationLead
from cel.prompt.prompt_template import PromptTemplate
from cel.rag.providers.rag_retriever import RAGRetriever
from cel.stores.history.base_history_provider import BaseHistoryProvider
from cel.stores.state.base_state_provider import BaseChatStateProvider


from abc import ABC
from dataclasses import dataclass
from typing import Any


@dataclass
class MacawNlpInferenceContext(ABC):
    lead: ConversationLead
    settings: MacawSettings
    prompt: PromptTemplate = ''
    init_state: dict = None
    local_state: dict = None
    functions: list[FunctionDefinition] = None
    rag_retriever: RAGRetriever = None
    # default value {} is used to avoid mutable default arguments
    llm_kwargs: dict[str, Any] = None
    history_store: BaseHistoryProvider = None
    state_store: BaseChatStateProvider = None
    llm: Any = None