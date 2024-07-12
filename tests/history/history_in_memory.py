# import random
import asyncio
import time
import pytest
# import fakeredis.aioredis
from cel.gateway.model.conversation_lead import ConversationLead
from cel.stores.history.history_inmemory_provider import InMemoryHistoryProvider
# from prompter.stores.history.history_redis_provider import RedisHistoryProvider



@pytest.fixture
def lead():
    lead = ConversationLead()
    return lead.get_session_id()

    
@pytest.fixture
def history() -> InMemoryHistoryProvider:
    h = InMemoryHistoryProvider(key_prefix='test')
    return h

@pytest.mark.asyncio
async def test_get_key(history: InMemoryHistoryProvider, lead):
    await history.append_to_history(lead, {'message': 'test'})
    l = await history.get_history(lead)
    assert l == [{'message': 'test'}]

@pytest.mark.asyncio
async def test_append_to_history(history: InMemoryHistoryProvider, lead):
    await history.append_to_history(lead, {'message': 'test0'})
    await history.append_to_history(lead, {'message': 'test1'})
    await history.append_to_history(lead, {'message': 'test2'})
    l = await history.get_history(lead)
    assert l == [{'message': 'test0'}, {'message': 'test1'}, {'message': 'test2'}]

@pytest.mark.asyncio
async def test_clear_history(history: InMemoryHistoryProvider, lead):
    await history.append_to_history(lead, {'message': 'test0'})
    await history.clear_history(lead)
    l =  await history.get_history(lead)
    assert l == []

@pytest.mark.asyncio
async def test_get_last_messages(history: InMemoryHistoryProvider, lead):
    await history.append_to_history(lead, {'message': 'test0'})
    await history.append_to_history(lead, {'message': 'test1'})
    await history.append_to_history(lead, {'message': 'test2'})
    l =  await history.get_last_messages(lead, 2)
    assert l == [{'message': 'test1'}, {'message': 'test2'}]

# TODO:
# @pytest.mark.asyncio
# async def test_ttl(history: InMemoryHistoryProvider, lead):
#     await history.append_to_history(lead, {'message': 'test0'}, ttl=1)
#     asyncio.sleep(2)
#     l =  await history.get_history(lead)
#     assert l == []


