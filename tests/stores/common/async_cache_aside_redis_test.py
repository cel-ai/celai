import pytest
import asyncio
import pytest_asyncio
import redis
import fakeredis.aioredis
from cel.stores.common.async_cache_aside_redis import AsyncMemRedisCacheAside


@pytest_asyncio.fixture()
async def aioredis(request) -> redis.asyncio.Redis:
     return fakeredis.aioredis.FakeRedis() 

@pytest.fixture
def cache(aioredis) -> AsyncMemRedisCacheAside:
    cache = AsyncMemRedisCacheAside(aioredis, 'test', 10, 60)
    return cache

@pytest.fixture
def no_wait_cache(aioredis) -> AsyncMemRedisCacheAside:
    cache = AsyncMemRedisCacheAside(aioredis, 'test', 10, 60, True)
    return cache



# TESTS 
# -------------------------------------------

@pytest.mark.asyncio
async def test_set_get(cache: AsyncMemRedisCacheAside):
    await cache.set('key', 'value')
    data = await cache.get('key') 
    assert data == 'value'

@pytest.mark.asyncio
async def test_get_with_callback(cache: AsyncMemRedisCacheAside):
    async def callback():
        return 'value1'
    assert await cache.get('key', callback) == 'value1'

@pytest.mark.asyncio
async def test_delete(cache: AsyncMemRedisCacheAside):
    await cache.set('key', 'value')
    await cache.delete_deep('key')
    assert await cache.get('key') is None
    
@pytest.mark.asyncio
async def test_delete_callback(cache: AsyncMemRedisCacheAside):
    """
    Test that the callback is called when the key is not in the cache
    and not in the redis cache
    """
    
    await cache.set('key', 'value')
    await cache.delete_deep('key')
    
    async def callback():
        return 'value1'

    assert await cache.get('key', callback) == 'value1'
    
    assert cache.cache_misses == 1
    assert cache.cache_memory_hits == 0
    assert cache.cache_redis_hits == 0
        
@pytest.mark.asyncio
async def test_clear(cache: AsyncMemRedisCacheAside):
    await cache.set('key', 'value')
    # await cache.clear()
    await cache.clear_deep()
    assert await cache.get('key') is None

@pytest.mark.asyncio
async def test_wr_speed_no_wait(no_wait_cache: AsyncMemRedisCacheAside):
    
    start = asyncio.get_event_loop().time()
    for i in range(100):
        value = f'value:{i}'
        await no_wait_cache.set('key', value)
        assert await no_wait_cache.get('key') == value
        
    end = asyncio.get_event_loop().time()
    print(f'async cache speed: {end-start}')

@pytest.mark.asyncio
async def test_wr_speed_wait_for_redis(cache: AsyncMemRedisCacheAside):
    
    start = asyncio.get_event_loop().time()
    for i in range(100):
        value = f'value:{i}'
        await cache.set('key', value)
        assert await cache.get('key') == value
        
    end = asyncio.get_event_loop().time()
    print(f'async cache speed: {end-start}')

@pytest.mark.asyncio
async def test_delete_memory(cache: AsyncMemRedisCacheAside):
    """
    Test that the cache memory is deleted but the redis cache is still there
    """
    
    await cache.set('key', 'value')
    await cache.delete('key')
    
    async def callback():
        return 'value1'

    assert await cache.get('key', callback) == 'value'
    
    assert cache.cache_misses == 0
    assert cache.cache_memory_hits == 0
    assert cache.cache_redis_hits == 1