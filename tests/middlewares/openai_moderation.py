import asyncio
import pytest
import shortuuid
from cel.assistants.base_assistant import BaseAssistant
from cel.assistants.common import EventResponse
from cel.connectors.telegram.model.telegram_lead import TelegramLead
from cel.gateway.model.base_connector import BaseConnector
from cel.gateway.model.conversation_lead import ConversationLead
from cel.gateway.model.message import Message
from cel.middlewares.moderation.openai_mod_endpoint import OpenAIEndpointModerationMiddleware
from openai.types.moderation import Moderation

import dotenv
dotenv.load_dotenv()


class MockMessage(Message):
    def __init__(self, lead, text):
        self.lead = lead
        self.text = text
        self.metadata = {}

    def is_voice_message(self):
        """This method should be implemented by the subclass to check if the message is a voice message"""
        return False
    
    @classmethod
    def load_from_dict(cls, message_dict: dict):
        pass

class Assistant():
    def __init__(self):
        self.count = 0
    
    async def call_event(self, 
                        event_name: str, 
                        lead: ConversationLead, 
                        message: Message = None, 
                        connector: BaseConnector = None, 
                        data: dict= None) -> EventResponse:
        assert isinstance(data, dict)
        assert isinstance(data["results"], Moderation)
        assert data['flagged'] == True
        assert data["results"].flagged == True
        self.count = data['count']


@pytest.mark.asyncio
async def test_flagged_message():
      
    assistant = Assistant()
    
    # Create an instance of the class
    middleware = OpenAIEndpointModerationMiddleware(
        custom_evaluation_function=None,
        on_mod_fail_continue=True
    )
    
    # Test the __call__ method
    chat_id = shortuuid.uuid()
    lead = TelegramLead(chat_id)
    message = MockMessage(lead, "fuck off")  
    assert await middleware(message, None, assistant) == True
    assert assistant.count == 1
    
    message = MockMessage(lead, "let's kill that mother fucker")  
    assert await middleware(message, None, assistant) == True
    assert assistant.count == 2
    

@pytest.mark.asyncio
async def test_expiration_flags():
      
    assistant = Assistant()
    
    # Create an instance of the class
    middleware = OpenAIEndpointModerationMiddleware(
        custom_evaluation_function=None,
        on_mod_fail_continue=True,
        expire_after=2,
        enable_expiration=True,
        prunning_interval=1
    )
    
    # Test the __call__ method
    chat_id = shortuuid.uuid()
    lead = TelegramLead(chat_id)
    message = MockMessage(lead, "fuck off")  
    assert await middleware(message, None, assistant) == True
    assert assistant.count == 1
    
    flags = middleware.get_user_flags(lead.get_session_id())
    assert flags.count == 1
    
    # wait for 3 seconds
    await asyncio.sleep(3)
    
    flags = middleware.get_user_flags(lead.get_session_id())
    assert flags is None



@pytest.mark.asyncio
async def test_reset_flags():
      
    assistant = Assistant()
    
    # Create an instance of the class
    middleware = OpenAIEndpointModerationMiddleware(
        custom_evaluation_function=None,
        on_mod_fail_continue=True
    )
    
    # Test the __call__ method
    chat_id = shortuuid.uuid()
    lead = TelegramLead(chat_id)
    message = MockMessage(lead, "fuck off")  
    assert await middleware(message, None, assistant) == True
    assert assistant.count == 1
    
    flags = middleware.get_user_flags(lead.get_session_id())
    assert flags.count == 1
    
    middleware.reset_user_flags(lead.get_session_id())
    
    flags = middleware.get_user_flags(lead.get_session_id())
    assert flags is None
