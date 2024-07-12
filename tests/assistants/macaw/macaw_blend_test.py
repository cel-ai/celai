import pytest
from cel.assistants.macaw.macaw_assistant import MacawAssistant
from cel.assistants.macaw.macaw_history_adapter import MacawHistoryAdapter
from cel.assistants.macaw.macaw_inference_context import MacawNlpInferenceContext
from cel.assistants.macaw.macaw_nlp import blend_message
from cel.assistants.macaw.macaw_settings import MacawSettings
from cel.gateway.model.conversation_lead import ConversationLead
from cel.stores.history.history_inmemory_provider import InMemoryHistoryProvider
from cel.stores.state.state_inmemory_provider import InMemoryStateProvider
from langchain_core.messages import HumanMessage

@pytest.mark.asyncio
async def test_blend_message():
    
    ctx = MacawNlpInferenceContext(
        lead = ConversationLead(),
        prompt="Your are a helpful assistant that can get the current price of a cryptocurrency. Get the price of a cryptocurrency.",
        history_store=InMemoryHistoryProvider(),
        state_store=InMemoryStateProvider(),
        settings=MacawSettings()
    )
    
    history_adapter = MacawHistoryAdapter(ctx.history_store)
    
    await history_adapter.append_to_history(ctx.lead, HumanMessage("Hola! dime por favor cuento es 2+2?"))

    res = await blend_message(ctx, message="You have a 10% discount on all products.")
    
    assert res is not None
    assert "descuento" in res
    assert "10%" in res
                

@pytest.mark.asyncio
async def test_assistant_blend():

    lead = ConversationLead()
    history_store=InMemoryHistoryProvider()
    history_adapter = MacawHistoryAdapter(history_store)
    await history_adapter.append_to_history(lead, HumanMessage("Hola! dime por favor cuento es 2+2?"))

    ast = MacawAssistant(history_store=history_store)
    
    res = await ast.blend(lead, text="You have a 10% discount on all products.")
    
    assert res is not None
    assert "descuento" in res
    assert "10%" in res
                
