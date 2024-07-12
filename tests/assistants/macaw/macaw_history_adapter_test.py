import pytest
from cel.assistants.macaw.macaw_history_adapter import MacawHistoryAdapter
from cel.assistants.macaw.macaw_utils import map_function_to_tool_message
from cel.gateway.model.conversation_lead import ConversationLead
from cel.stores.history.history_inmemory_provider import InMemoryHistoryProvider
from langchain_core.messages import HumanMessage, AIMessage

@pytest.mark.asyncio
async def test_macaw_history_store_adapter():
    adapter = MacawHistoryAdapter(store=InMemoryHistoryProvider())
    
    lead = ConversationLead()
    await adapter.append_to_history(lead, HumanMessage("Hello"))
    await adapter.append_to_history(lead, AIMessage("Hi"))
    
    
    history = await adapter.get_history(lead)
    assert len(history) == 2
    assert isinstance(history[0], HumanMessage), "Expected HumanMessage"
    assert isinstance(history[1], AIMessage), "Expected AIMessage"