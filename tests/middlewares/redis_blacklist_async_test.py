import fakeredis
import pytest
import pytest_asyncio
import redis
import shortuuid
from cel.connectors.telegram.model.telegram_lead import TelegramLead
from cel.gateway.model.message import Message
from cel.middlewares.redis_blacklist_async import RedisBlackListAsyncMiddleware

class MockMessage(Message):
    def __init__(self, lead):
        self.lead = lead

    def is_voice_message(self):
        """This method should be implemented by the subclass to check if the message is a voice message"""
        return False
    
    @classmethod
    def load_from_dict(cls, message_dict: dict):
        pass


@pytest_asyncio.fixture()
async def client() -> redis.asyncio.Redis:
     return fakeredis.aioredis.FakeRedis() 

@pytest.mark.asyncio
async def test_redis_black_list_async_middleware(client):
    # Create an instance of the class
    middleware = RedisBlackListAsyncMiddleware(redis=client)

    # Test the __call__ method
    chat_id = shortuuid.uuid()
    lead = TelegramLead(chat_id)
    message = MockMessage(lead)  # Deberías definir este objeto
    assert await middleware(message, None, None) == True

    # Test the add_to_black_list method
    await middleware.add_to_black_list(lead.get_session_id(), 'test reason')
    entry = await middleware.get_entry(lead.get_session_id())
    assert entry is not None
    assert entry['reason'] == 'test reason'

    # Test the remove_from_black_list method
    await middleware.remove_from_black_list(lead.get_session_id())
    entry = await middleware.get_entry(lead.get_session_id())
    assert entry is None
    
    

    
@pytest.mark.asyncio
async def test_redis_black_list_async_middleware_block(client):
    # Create an instance of the class
    middleware = RedisBlackListAsyncMiddleware(redis=client)

    # Test the __call__ method
    chat_id = shortuuid.uuid()
    lead = TelegramLead(chat_id)
    message = MockMessage(lead)  # Deberías definir este objeto
    assert await middleware(message, None, None) == True

    # Test the add_to_black_list method
    await middleware.add_to_black_list(lead.get_session_id(), 'test reason')
        
    # Test the __call__ method with a user in the blacklist
    assert await middleware(message, None, None) == False