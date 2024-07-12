import fakeredis
import pytest
import shortuuid
from cel.assistants.albert.albert_assistant import AlbertAssistant
from cel.gateway.model.conversation_lead import ConversationLead
from cel.stores.history.history_redis_provider import RedisHistoryProvider
from cel.stores.state.state_redis_provider import RedisChatStateProvider

# load envs
from dotenv import load_dotenv
load_dotenv()


@pytest.fixture
def lead() -> ConversationLead:
    lead = ConversationLead()
    return lead

@pytest.fixture
def redis_client():
    redis_client = fakeredis.FakeRedis()
    return redis_client

@pytest.fixture
def state_store(redis_client):
    return RedisChatStateProvider(redis_client, 's')

@pytest.fixture
def history_store(redis_client):
    return RedisHistoryProvider(redis_client, 'h')

@pytest.fixture
def assistant(history_store, state_store):
    return AlbertAssistant(
        history_store=history_store,
        state_store=state_store
    )


@pytest.mark.asyncio
async def test_add_function_repsonse_to_history(lead: ConversationLead, assistant: AlbertAssistant):
    function_call = {
        "name": "get_crypto_price",
        "arguments": {"asset": "BTC"}
    }
    assistant.engine.add_function_response_message(lead, function_call, "The price of BTC is $1000 USD")
    h = assistant.engine.get_history(lead.get_session_id(), last_n=10)
    assert len(h) == 1
    assert h[0].get("content") == "The price of BTC is $1000 USD"

    
@pytest.mark.asyncio
async def test_add_function_call_to_history(lead: ConversationLead, assistant: AlbertAssistant):
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
    
