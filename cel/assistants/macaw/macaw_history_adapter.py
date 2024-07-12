from cel.gateway.model.conversation_lead import ConversationLead
from langchain.load.dump import dumpd
from langchain.load.load import load
from langchain_core.messages import BaseMessage
from cel.stores.history.base_history_provider import BaseHistoryProvider


class MacawHistoryAdapter:
    def __init__(self, store: BaseHistoryProvider):
        self.store = store

    async def append_to_history(self, lead: ConversationLead, entry: BaseMessage, metadata=None, ttl=None):
        assert isinstance(lead, ConversationLead), f"Expected ConversationLead, got {type (lead)}"
        aux = dumpd(entry)
        await self.store.append_to_history(lead.get_session_id(), aux, metadata, ttl)

    async def get_history(self, lead: ConversationLead) -> list[BaseMessage]:
        assert isinstance(lead, ConversationLead), f"Expected ConversationLead, got {type (lead)}"
        history = await self.store.get_history(lead.get_session_id())
        return [load(h) for h in history]


    async def clear_history(self, lead: ConversationLead, keep_last_messages=None):
        assert isinstance(lead, ConversationLead), f"Expected ConversationLead, got {type (lead)}"
        await self.store.clear_history(lead.get_session_id(), keep_last_messages)

    async def get_last_messages(self, lead: ConversationLead, count) -> list[BaseMessage]:
        assert isinstance(lead, ConversationLead), f"Expected ConversationLead, got {type (lead)}"
        msgs = await self.store.get_last_messages(lead.get_session_id(), count)
        return [load(m) for m in msgs]

    async def close_conversation(self, lead: ConversationLead):
        raise NotImplementedError