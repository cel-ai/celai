import pytest
from cel.assistants.albert.albert_assistant import AlbertAssistant
from cel.gateway.model.conversation_lead import ConversationLead

# load envs
from dotenv import load_dotenv
load_dotenv()



@pytest.fixture
def lead():
    lead = ConversationLead()
    return lead


@pytest.mark.asyncio
async def test_add_function_repsonse_to_history(lead: ConversationLead):
    assistant = AlbertAssistant()
    function_call = {
        "name": "get_crypto_price",
        "arguments": {"asset": "BTC"}
    }
    assistant.engine.add_function_response_message(lead, function_call, "The price of BTC is $1000 USD")
    h = assistant.engine.get_history(lead.get_session_id(), last_n=10)
    assert len(h) == 1
    assert h[0].get("content") == "The price of BTC is $1000 USD"

    
@pytest.mark.asyncio
async def test_add_function_call_to_history(lead: ConversationLead):
    assistant = AlbertAssistant()
    function_call = {
        "name": "get_crypto_price",
        "arguments": {"asset": "BTC"}
    }
    assistant.engine.add_function_call_message(lead, function_call)
    assistant.engine.add_function_response_message(lead, function_call, "The price of BTC is $1000 USD")
    h = assistant.engine.get_history(lead.get_session_id(), last_n=10)
    assert len(h) == 2
    assert h[0].get("role") == "assistant"
    assert h[0].get("function_call") == function_call
    
    assert h[1].get("name") == "get_crypto_price"
    assert h[1].get("content") == "The price of BTC is $1000 USD"
    
