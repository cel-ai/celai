import random
import time
import pytest
import fakeredis.aioredis
from cel.gateway.model.conversation_lead import ConversationLead
from cel.stores.history.history_inmemory_provider import InMemoryHistoryProvider
from cel.stores.history.history_redis_provider import RedisHistoryProvider



@pytest.fixture
def lead():
    lead = ConversationLead()
    return lead.get_session_id()

# @pytest.fixture
# def redis_client():
#     redis_client = fakeredis.FakeRedis()
#     return redis_client
    
@pytest.fixture
def history() -> InMemoryHistoryProvider:
    h = InMemoryHistoryProvider(key_prefix='test')
    return h


def test_get_key(history: RedisHistoryProvider, lead):
    history.append_to_history(lead, {'message': 'test'})
    l = history.get_history(lead)
    assert l == [{'message': 'test'}]


def test_append_to_history(history: RedisHistoryProvider, lead):
    history.append_to_history(lead, {'message': 'test0'})
    history.append_to_history(lead, {'message': 'test1'})
    history.append_to_history(lead, {'message': 'test2'})
    l = history.get_history(lead)
    assert l == [{'message': 'test0'}, {'message': 'test1'}, {'message': 'test2'}]


def test_clear_history(history: RedisHistoryProvider, lead):
    history.append_to_history(lead, {'message': 'test0'})
    history.clear_history(lead)
    l =  history.get_history(lead)
    assert l == []


def test_get_last_messages(history: RedisHistoryProvider, lead):
    history.append_to_history(lead, {'message': 'test0'})
    history.append_to_history(lead, {'message': 'test1'})
    history.append_to_history(lead, {'message': 'test2'})
    l =  history.get_last_messages(lead, 2)
    assert l == [{'message': 'test1'}, {'message': 'test2'}]


# def test_ttl(history: RedisHistoryProvider, lead):
#     history.append_to_history(lead, {'message': 'test0'}, ttl=1)
#     time.sleep(2)
#     l =  history.get_history(lead)
#     assert l == []


