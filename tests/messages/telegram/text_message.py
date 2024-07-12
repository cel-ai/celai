import pytest
from cel.connectors.telegram.model.telegram_message import TelegramMessage
from cel.gateway.model.conversation_lead import ConversationLead
from cel.connectors.telegram.model.telegram_lead import TelegramLead
import dotenv

dotenv.load_dotenv()

sample_message = {
    "update_id": 169216955,
    "message": {
       "message_id":123,
       "from":{
          "id":1320141991,
          "is_bot": False,
          "first_name":"John Doe",
          "username":"john_doe",
          "language_code":"en"
       },
       "chat":{
          "id":1320141991,
          "first_name":"John Doe",
          "username":"john_doe",
          "type":"private"
       },
       "date":1716850049,
       "text":"Hello!"
    }
}


# @pytest.fixture
# def fix():
#     pass

@pytest.mark.asyncio
async def test_parse_message():

    msg: TelegramMessage = await TelegramMessage.load_from_message(sample_message)
    
    assert isinstance(msg.lead, TelegramLead)
    assert isinstance(msg.lead, ConversationLead)
    
    assert msg.lead.chat_id == '1320141991'
    assert msg.lead.metadata['message_id'] == '123'
    assert msg.lead.metadata['date'] == 1716850049
    assert msg.lead.metadata['raw'] == sample_message['message']
    
    assert msg.text == "Hello!"
    assert msg.date == 1716850049
    assert msg.metadata == {'raw': sample_message['message']}
    
    