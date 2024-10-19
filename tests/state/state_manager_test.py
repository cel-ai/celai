import asyncio
import pytest
from fakeredis import FakeRedis
import pytest_asyncio
import redis
from cel.assistants.state_manager import AsyncStateManager
from cel.gateway.model.conversation_lead import ConversationLead
from cel.stores.history.history_redis_provider_async import RedisHistoryProviderAsync
from cel.stores.state.state_inmemory_provider import InMemoryStateProvider
from cel.stores.state.state_redis_provider import RedisChatStateProvider



@pytest.fixture
def lead():
    lead = ConversationLead()
    return lead

@pytest.fixture
def redis_client(request) -> redis.Redis:
    # fake redis
    return FakeRedis()

@pytest.fixture
def state_store(redis_client) -> RedisChatStateProvider:
    store = RedisChatStateProvider(redis_client, key_prefix='h')
    return store


@pytest.mark.asyncio
async def test_state_manager(lead, state_store):
    state = AsyncStateManager(lead, state_store)

    async with state:
        state['amount'] = 1000
        # do something
        state['result'] = "done"
        
    async with state:
        assert state['amount'] == 1000
        assert state['result'] == "done"


@pytest.mark.asyncio
async def test_state_manager_inmemory(lead):
    state = AsyncStateManager(lead, InMemoryStateProvider())

    async with state:
        state['amount'] = 1000
        # do something
        state['result'] = "done"
        
    async with state:
        assert state['amount'] == 1000
        assert state['result'] == "done"
        
        
@pytest.mark.asyncio
async def test_state_manager_exception(lead):
    state = AsyncStateManager(lead, InMemoryStateProvider())

    try:
        async with state:
            state['amount'] = 1000
            # do something and raise an exception
            # then the state should be empty
            raise ValueError("Error")
        
    except ValueError as e:
        pass
        
    # Check if the state is empty
    state = await state.load_state()
    assert 'amount' not in state