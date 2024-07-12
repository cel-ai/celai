import os
import pytest
import requests
from cel.connectors.telegram.model.telegram_attachment import TelegramAttachment
from cel.connectors.telegram.model.telegram_message import TelegramMessage
from cel.gateway.model.conversation_lead import ConversationLead
from cel.connectors.telegram.model.telegram_lead import TelegramLead
import dotenv

dotenv.load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

sample_message = {
    "update_id": 794947863,
    "message": {
        "message_id": 647,
        "from": {
            "id": 1320141,
            "is_bot": False,
            "first_name": "John",
            "username": "foobar",
            "language_code": "en"
        },
        "chat": {
            "id": 1320141,
            "first_name": "John",
            "username": "foobar",
            "type": "private"
        },
        "date": 1717182488,
        "voice": {
            "duration": 2,
            "mime_type": "audio/ogg",
            "file_id": "AwACAgEAAxkBAAICh2ZaIBgQeMjTu4_DOlmioRlXy6PGAAKeBQACWnjQRhHL8mHBhl-FNQQ",
            "file_unique_id": "AgADngUAAlp40EY",
            "file_size": 8537
        }
    }
}

# @pytest.fixture
# def fix():
#     pass

@pytest.mark.asyncio
async def test_parse_attachment():
   
    attach = await TelegramAttachment.load_from_message(sample_message, TELEGRAM_TOKEN)

    assert attach.title == "audio"
    # assert attach.file_url == "https://es.wikipedia.org/static/images/icons/wikipedia.png"
    # http download file using attach.file_url

    response = requests.get(attach.file_url)

    # Asegúrate de que la solicitud fue exitosa
    assert response.status_code == 200
    assert attach.type == "voice"
    



@pytest.mark.asyncio
async def test_parse_message_with_image():

   msg = await TelegramMessage.load_from_message(sample_message, TELEGRAM_TOKEN)
   
   assert isinstance(msg.lead, TelegramLead)
   assert isinstance(msg.lead, ConversationLead)
   
   assert msg.lead.chat_id == '1320141'
   assert msg.lead.metadata['message_id'] == '647'
   assert msg.lead.metadata['date'] == 1717182488
   assert msg.lead.metadata['raw'] == sample_message['message']
   
#    assert msg.text == "This is an image 😍"
   assert msg.date == 1717182488
   assert msg.metadata == {'raw': sample_message['message']}
   assert msg.is_voice_message() == True
    
