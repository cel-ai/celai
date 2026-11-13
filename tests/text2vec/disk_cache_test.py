from types import SimpleNamespace
from unittest.mock import patch

import pytest
from diskcache_community import Cache, Disk

import cel.rag.text2vec.cached_openai as cached_openai
from cel.rag.text2vec.cache.disk_cache import DiskCache
from cel.rag.text2vec.cached_openai import CachedOpenAIEmbedding

VECTOR = [0.25, -0.5, 0.125]
planted_calls = []


def planted():
    planted_calls.append("ran")
    return [9.0, 9.0, 9.0]


class Planted:
    def __reduce__(self):
        return (planted, ())


@pytest.fixture
def api_requests():
    requests = []

    class FakeOpenAI:
        api_key = None

        def __init__(self, max_retries=2):
            self.embeddings = SimpleNamespace(create=self.create)

        def create(self, input, model):
            requests.append(input)
            return SimpleNamespace(data=[SimpleNamespace(embedding=list(VECTOR))])

    with patch.object(cached_openai, "OpenAI", FakeOpenAI):
        yield requests


def test_tampered_cache_entry_is_fetched_again(tmp_path, api_requests):
    planted_calls.clear()
    embedding = CachedOpenAIEmbedding(api_key="test", cache_backend=DiskCache(cache_dir=str(tmp_path)))

    assert embedding.text2vec("parrots") == VECTOR
    assert embedding.text2vec("parrots") == VECTOR
    assert len(api_requests) == 1

    with Cache(str(tmp_path), disk=Disk) as other_writer:
        (key,) = list(other_writer)
        other_writer.set(key, Planted())

    assert embedding.text2vec("parrots") == VECTOR
    assert planted_calls == []
    assert len(api_requests) == 2
