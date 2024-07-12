import os
import pytest
from cel.connectors.telegram.model.telegram_attachment import TelegramAttachment
from cel.connectors.telegram.model.telegram_message import TelegramMessage
from cel.gateway.model.conversation_lead import ConversationLead
from cel.connectors.telegram.model.telegram_lead import TelegramLead
import dotenv

dotenv.load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

sample_message = {
    "update_id": 1692169,
    "message": {
        "message_id": 153,
        "from": {
            "id": 1320141991,
            "is_bot": False,
            "first_name": "John",
            "last_name": "Doe",
            "language_code": "en"
        },
        "chat": {
            "id": 1320141991,
            "first_name": "John",
            "last_name": "Doe",
            "type": "private"
        },
        "date": 1687752535,
        "photo": [
            {
                "file_id": "123",
                "file_unique_id": "AQADOqsxG9tG0ER4",
                "file_size": 1562,
                "width": 90,
                "height": 90
            },
            {
                "file_id": "123",
                "file_unique_id": "AQADOqsxG9tG0ERy",
                "file_size": 14487,
                "width": 320,
                "height": 320
            },
            {
                "file_id": "123",
                "file_unique_id": "AQADOqsxG9tG0ER9",
                "file_size": 21976,
                "width": 512,
                "height": 512
            }
        ],
        "caption": "This is an image 😍"
    }
}

# @pytest.fixture
# def fix():
#     pass

@pytest.mark.asyncio
async def test_parse_attachment():
   
   attach = await TelegramAttachment.load_from_message(sample_message, TELEGRAM_TOKEN)
   
   assert attach.title == "photo"
   assert attach.file_url == "https://es.wikipedia.org/static/images/icons/wikipedia.png"
   



@pytest.mark.asyncio
async def test_parse_message_with_image():

   msg = await TelegramMessage.load_from_message(sample_message, TELEGRAM_TOKEN)
   
   assert isinstance(msg.lead, TelegramLead)
   assert isinstance(msg.lead, ConversationLead)
   
   assert msg.lead.chat_id == '1320141991'
   assert msg.lead.metadata['message_id'] == '153'
   assert msg.lead.metadata['date'] == 1687752535
   assert msg.lead.metadata['raw'] == sample_message['message']
   
   assert msg.text == "This is an image 😍"
   assert msg.date == 1687752535
   assert msg.metadata == {'raw': sample_message['message']}