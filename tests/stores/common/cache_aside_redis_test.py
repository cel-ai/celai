import time
import pytest
import unittest.mock as mock
import fakeredis
from cel.stores.common.cache_aside_redis import MemRedisCacheAside


@pytest.fixture
def redis_client():
    redis_client = fakeredis.FakeRedis()
    return redis_client
    
@pytest.fixture
def cache(redis_client) -> MemRedisCacheAside:
    cache = MemRedisCacheAside(redis_client, 'test', 10, 60, False)
    return cache


# TESTS 
# -------------------------------------------

def test_init(cache: MemRedisCacheAside):
    assert cache.key_prefix == 'test'
    assert cache.ttl == 60
    assert cache.wait_for_redis == False

def test_set_get(cache: MemRedisCacheAside):
    cache.set('key', 'value')
    assert cache.get('key') == 'value'

def test_delete(cache: MemRedisCacheAside):
    cache.set('key', 'value')
    time.sleep(0.5)
    cache.delete('key')
    assert cache.get('key') == 'value'
    cache.delete('key')
    cache.delete_redis('key')
    assert cache.get('key') is None


def test_clear(cache: MemRedisCacheAside):
    cache.set('key', 'value')
    cache.clear()
    # wait 100 ms
    time.sleep(0.1)
    assert cache.get('key') is not None
    cache.clear_redis()
    cache.clear()
    assert cache.get('key') is None

def test_set_wait_for_redis(cache: MemRedisCacheAside):
    cache.set_wait_for_redis(True)
    assert cache.wait_for_redis == True

def test_callback(cache: MemRedisCacheAside):
    callback = mock.Mock(return_value='value')
    assert cache.get('key', callback) == 'value'
    callback.assert_called_once()