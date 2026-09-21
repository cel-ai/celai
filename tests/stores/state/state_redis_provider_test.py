import asyncio
import random
import pytest
import fakeredis.aioredis
import pytest_asyncio
import redis
import redis.asyncio
from cel.gateway.model.conversation_lead import ConversationLead
from cel.stores.state.state_redis_provider import RedisChatStateProvider

@pytest_asyncio.fixture()
def lead() -> str:
    lead = ConversationLead()
    return lead.get_session_id()

@pytest_asyncio.fixture()
def redis_client():
    redis_client = fakeredis.FakeRedis()
    return redis_client

@pytest_asyncio.fixture()
def async_redis_client():
    return fakeredis.aioredis.FakeRedis()

@pytest.fixture(params=["sync", "async"])
def store(request, redis_client, async_redis_client):
    """The provider must keep working with a legacy synchronous client while
    driving a redis.asyncio client natively, so both are exercised here."""
    client = redis_client if request.param == "sync" else async_redis_client
    return RedisChatStateProvider(client, 's')

@pytest.mark.asyncio
async def test_set_key_value(store: RedisChatStateProvider, lead):
    await store.set_key_value(lead, 'key1', 'value1')
    v = await store.get_key_value(lead, 'key1')
    assert v == 'value1'
    
@pytest.mark.asyncio
async def test_get_store(store: RedisChatStateProvider, lead):
    await store.set_key_value(lead, 'key0', 'value0')
    await store.set_key_value(lead, 'key1', 'value1')
    s = await store.get_store(lead)
    assert s == {'key0': 'value0', 'key1': 'value1'}

@pytest.mark.asyncio
async def test_clear_store(store: RedisChatStateProvider, lead):
    await store.set_key_value(lead, 'key0', 'value0')
    await store.set_key_value(lead, 'key1', 'value1')
    s = await store.get_store(lead)
    assert s == {'key0': 'value0', 'key1': 'value1'}
    await store.clear_store(lead)
    s = await store.get_store(lead)
    assert s == None

@pytest.mark.asyncio
async def test_clear_all_stores(store: RedisChatStateProvider):
    sessionId1 = ConversationLead()
    sessionId2 = ConversationLead()
    await store.set_key_value(sessionId1, 'key0', 'value0')
    await store.set_key_value(sessionId1, 'key1', 'value1')
    await store.set_key_value(sessionId2, 'key0', 'value0')
    await store.set_key_value(sessionId2, 'key1', 'value1')
    
    s = await store.get_store(sessionId1)
    assert s == {'key0': 'value0', 'key1': 'value1'}
    
    s = await store.get_store(sessionId2)
    assert s == {'key0': 'value0', 'key1': 'value1'}
    
    await store.clear_all_stores()
    s = await store.get_store(sessionId1)
    assert s == None
    
    s = await store.get_store(sessionId2)
    assert s == None


@pytest.mark.asyncio
async def test_url_builds_an_async_client():
    """A blocking redis round trip stalls every conversation on the event loop,
    so a connection url must produce a redis.asyncio client."""
    store = RedisChatStateProvider("redis://localhost:6379/0")
    assert store.is_async is True
    assert isinstance(store.client, redis.asyncio.Redis)
