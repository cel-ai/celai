from cel.stores.common.memory_cache import MemoryCache


def test_memory_cache():
    cache = MemoryCache('test', memory_maxsize=2)

    # Test set method
    cache.set('key1', 'value1')
    assert cache.get('key1') == 'value1'

    # Test get method with callback
    result = cache.get('key2', callback=lambda: 'value2')
    assert result == 'value2'
    assert cache.get('key2') == 'value2'

    # Test LRU property
    cache.set('key3', 'value3')
    assert cache.get('key1') is None
    assert cache.get('key2') == 'value2'
    assert cache.get('key3') == 'value3'

    # Test delete method
    cache.delete('key2')
    assert cache.get('key2') is None

    # Test clear method
    cache.clear()
    assert cache.get('key3') is None

    # Test all method
    cache.set('key1', 'value1')
    cache.set('key2', 'value2')
    assert set(cache.all()) == {('key1', 'value1'), ('key2', 'value2')}