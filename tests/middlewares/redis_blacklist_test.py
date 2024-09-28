import pytest
import shortuuid
from cel.connectors.telegram.model.telegram_lead import TelegramLead
from cel.gateway.model.message import Message
from cel.middlewares.redis_blacklist import RedisBlackListMiddleware
import fakeredis

class MockMessage(Message):
    def __init__(self, lead):
        self.lead = lead

    def is_voice_message(self):
        """This method should be implemented by the subclass to check if the message is a voice message"""
        return False
    
    @classmethod
    def load_from_dict(cls, message_dict: dict):
        pass



@pytest.fixture
def redis_client():
    redis_client = fakeredis.FakeRedis()
    return redis_client

@pytest.mark.asyncio
async def test_in_mem_black_list_middleware(redis_client):
    # Create an instance of the class
    middleware = RedisBlackListMiddleware(redis=redis_client)

    # Test the __call__ method
    chat_id = shortuuid.uuid()
    lead = TelegramLead(chat_id)
    message = MockMessage(lead)  # Deberías definir este objeto
    assert await middleware(message, None, None) == True

    # Test the add_to_black_list method
    middleware.add_to_black_list(lead.get_session_id(), 'test reason')
    entry = middleware.get_entry(lead.get_session_id())
    assert entry is not None
    assert entry['reason'] == 'test reason'

    # Test the remove_from_black_list method
    middleware.remove_from_black_list(lead.get_session_id())
    entry = middleware.get_entry(lead.get_session_id())
    assert entry is None
    
    

    
@pytest.mark.asyncio
async def test_in_mem_black_list_middleware_block(redis_client):
    # Create an instance of the class
    middleware = RedisBlackListMiddleware(redis=redis_client)

    # Test the __call__ method
    chat_id = shortuuid.uuid()
    lead = TelegramLead(chat_id)
    message = MockMessage(lead)  # Deberías definir este objeto
    assert await middleware(message, None, None) == True

    # Test the add_to_black_list method
    middleware.add_to_black_list(lead.get_session_id(), 'test reason')
        
    # Test the __call__ method with a user in the blacklist
    assert await middleware(message, None, None) == False