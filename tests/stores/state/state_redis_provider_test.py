import fakeredis
import pytest
from cel.gateway.model.conversation_lead import ConversationLead
from cel.stores.state.state_redis_provider import RedisChatStateProvider

@pytest.fixture
def lead() -> str:
    lead = ConversationLead()
    return lead.get_session_id()

@pytest.fixture
def redis_client():
    redis_client = fakeredis.FakeRedis()
    return redis_client

@pytest.fixture
def store(redis_client):
    return RedisChatStateProvider(redis_client, 's')

def test_set_key_value(store: RedisChatStateProvider, lead):
    store.set_key_value(lead, 'key1', 'value1')
    v = store.get_key_value(lead, 'key1')
    assert v == 'value1'
    
def test_get_store(store: RedisChatStateProvider, lead):
    store.set_key_value(lead, 'key0', 'value0')
    store.set_key_value(lead, 'key1', 'value1')
    s = store.get_store(lead)
    assert s == {'key0': 'value0', 'key1': 'value1'}

def test_clear_store(store: RedisChatStateProvider, lead):
    store.set_key_value(lead, 'key0', 'value0')
    store.set_key_value(lead, 'key1', 'value1')
    s = store.get_store(lead)
    assert s == {'key0': 'value0', 'key1': 'value1'}
    store.clear_store(lead)
    s = store.get_store(lead)
    assert s == None

def test_clear_all_stores(store: RedisChatStateProvider):
    sessionId1 = ConversationLead()
    sessionId2 = ConversationLead()
    store.set_key_value(sessionId1, 'key0', 'value0')
    store.set_key_value(sessionId1, 'key1', 'value1')
    store.set_key_value(sessionId2, 'key0', 'value0')
    store.set_key_value(sessionId2, 'key1', 'value1')
    
    s = store.get_store(sessionId1)
    assert s == {'key0': 'value0', 'key1': 'value1'}
    
    s = store.get_store(sessionId2)
    assert s == {'key0': 'value0', 'key1': 'value1'}
    
    store.clear_all_stores()
    s = store.get_store(sessionId1)
    assert s == None
    
    s = store.get_store(sessionId2)
    assert s == None
