import pytest

from cel.connectors.telegram.model.telegram_lead import TelegramLead
from cel.gateway.model.message import Message
from cel.middlewares.in_mem_blacklist import InMemBlackListMiddleware

class MockMessage(Message):
    def __init__(self, lead):
        self.lead = lead

    def is_voice_message(self):
        """This method should be implemented by the subclass to check if the message is a voice message"""
        return False
    
    @classmethod
    def load_from_dict(cls, message_dict: dict):
        pass


@pytest.mark.asyncio
async def test_in_mem_black_list_middleware():
    # Crear una instancia de la clase
    middleware = InMemBlackListMiddleware()

    # Prueba el método __call__
    lead = TelegramLead("123")
    message = MockMessage(lead)  # Deberías definir este objeto
    assert await middleware(message, None, None) == True

    # Prueba el método add_to_black_list
    middleware.add_to_black_list(lead.get_session_id(), 'test reason')
    assert lead.get_session_id() in middleware.black_list
    assert middleware.black_list[lead.get_session_id()].reason == 'test reason'

    # Prueba el método remove_from_black_list
    middleware.remove_from_black_list('telegram:123')
    assert 'telegram:123' not in middleware.black_list
    

    
@pytest.mark.asyncio
async def test_in_mem_black_list_middleware_block():
    # Crear una instancia de la clase
    middleware = InMemBlackListMiddleware()

    # Prueba el método __call__
    lead = TelegramLead("123")
    message = MockMessage(lead)  # Deberías definir este objeto
    assert await middleware(message, None, None) == True

    # Prueba el método add_to_black_list
    middleware.add_to_black_list(lead.get_session_id(), 'test reason')
        
    # Prueba el método __call__ con un usuario en la lista negra
    assert await middleware(message, None, None) == False