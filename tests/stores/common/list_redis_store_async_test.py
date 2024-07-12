import pytest
import pytest_asyncio
import redis
import fakeredis.aioredis
from cel.stores.common.list_redis_store_async import ListRedisStoreAsync


@pytest_asyncio.fixture()
async def aioredis(request) -> redis.asyncio.Redis:
     return fakeredis.aioredis.FakeRedis() 

@pytest.fixture
def store(aioredis):
    return ListRedisStoreAsync(aioredis, key_prefix='h', ttl=10)


# TESTS 
# -------------------------------------------

@pytest.mark.asyncio
async def test_list_append(store):
    await store.list_append('key', 'value0')
    await store.list_append('key', 'value1')
    l = await store.list_get('key')
    assert l == ['value0', 'value1'] 
    # assert 1

@pytest.mark.asyncio
async def test_list_clear(store):
    await store.list_append('key', 'value0')
    await store.list_clear('key')
    l = await store.list_get('key')
    assert l == []

@pytest.mark.asyncio
async def test_list_get_last(store):
    await store.list_append('key', 'value0')
    await store.list_append('key', 'value1')
    await store.list_append('key', 'value2')
    l = await store.list_get_last('key', 2)
    assert l == ['value1', 'value2']
