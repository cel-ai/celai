import asyncio
import random
import pytest
import fakeredis.aioredis
import pytest_asyncio
import redis
from cel.gateway.model.conversation_lead import ConversationLead
from cel.stores.common.list_redis_store_async import ListRedisStoreAsync
from cel.stores.history.history_redis_provider_async import RedisHistoryProviderAsync



@pytest.fixture
def lead():
    lead = ConversationLead()
    return lead.get_session_id()

@pytest_asyncio.fixture()
async def aioredis(request) -> redis.asyncio.Redis:
     return fakeredis.aioredis.FakeRedis() 

@pytest.fixture
def store(aioredis) -> ListRedisStoreAsync:
    store = ListRedisStoreAsync(aioredis, key_prefix='h', ttl=2)
    return store

@pytest.fixture
def history_provider(store) -> RedisHistoryProviderAsync:
    history = RedisHistoryProviderAsync(store)
    return history

@pytest.mark.asyncio
async def test_get_key(history_provider: RedisHistoryProviderAsync, lead):
    await history_provider.append_to_history(lead, {'message': 'test'})
    l = await history_provider.get_history(lead)
    assert l == [{'message': 'test'}] 

@pytest.mark.asyncio
async def test_append_to_history(history_provider: RedisHistoryProviderAsync, lead):
    await history_provider.append_to_history(lead, {'message': 'test0'})
    await history_provider.append_to_history(lead, {'message': 'test1'})
    await history_provider.append_to_history(lead, {'message': 'test2'})
    l = await history_provider.get_history(lead)
    assert l == [{'message': 'test0'}, {'message': 'test1'}, {'message': 'test2'}]


@pytest.mark.asyncio
async def test_clear_history(history_provider: RedisHistoryProviderAsync, lead):
    await history_provider.append_to_history(lead, {'message': 'test0'})
    await history_provider.clear_history(lead)
    l = await history_provider.get_history(lead)
    assert l == []

@pytest.mark.asyncio
async def test_get_last_messages(history_provider: RedisHistoryProviderAsync, lead):
    await history_provider.append_to_history(lead, {'message': 'test0'})
    await history_provider.append_to_history(lead, {'message': 'test1'})
    await history_provider.append_to_history(lead, {'message': 'test2'})
    l = await history_provider.get_last_messages(lead, 2)
    assert l == [{'message': 'test1'}, {'message': 'test2'}]

@pytest.mark.asyncio
async def test_ttl(history_provider: RedisHistoryProviderAsync, lead):
    await history_provider.append_to_history(lead, {'message': 'test0'}, ttl=1)
    await asyncio.sleep(2)
    l = await history_provider.get_history(lead)
    assert l == []
        


