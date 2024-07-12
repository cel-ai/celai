import os
import time
import pytest
from cel.gateway.model.base_connector import BaseConnector
from cel.connectors.whatsapp.model.media_utils import download_media
from cel.connectors.whatsapp.model.whatsapp_attachment import WhatsappAttachment
from cel.connectors.whatsapp.model.whatsapp_lead import WhatsappLead
from cel.connectors.whatsapp.model.whatsapp_message import WhatsappMessage
from cel.gateway.model.conversation_lead import ConversationLead
import dotenv

dotenv.load_dotenv()


sample_data = {
    "object": "whatsapp_business_account",
    "entry": [
        {
            "id": "103048736088448",
            "changes": [
                {
                    "value": {
                        "messaging_product": "whatsapp",
                        "metadata": {
                            "display_phone_number": "15550463673",
                            "phone_number_id": "105602452496989"
                        },
                        "contacts": [
                            {
                                "profile": {
                                    "name": "John Doe"
                                },
                                "wa_id": "134911669XXXXX"
                            }
                        ],
                        "messages": [
                            {
                                "from": "134911669XXXXX",
                                "id": "wamid.HBgNNTQ5MTE2NjkzNzg0OBUCABIYFDNBRkEzN0ZFMDXXXX==",
                                "timestamp": "1717858794",
                                "type": "image",
                                "image": {
                                    "caption": "Take a look",
                                    "mime_type": "image/jpeg",
                                    "sha256": "dEctuifbo+EGLhzh3H5KAuaS1b9fnn10LMpZBqiSmjA=",
                                    "id": "971782074594239"
                                }
                            }
                        ]
                    },
                    "field": "messages"
                }
            ]
        }
    ]
}

# @pytest.fixture
# def fix():
#     pass

@pytest.mark.asyncio
async def test_parse_text_message():
   
    token = os.getenv('WHATSAPP_TOKEN')
    phone_number = os.getenv('WHATSAPP_PHONE_NUMBER_ID')
   
    base_conn = BaseConnector()
    
    start = time.time()
    msg: WhatsappMessage = await WhatsappMessage.load_from_message(sample_data, 
                                                                   connector=base_conn, 
                                                                   token=token, 
                                                                   phone_number_id=phone_number)
    end = time.time()
    enlapced = end - start
    print(f"Elapsed time: {enlapced}")   
    
    assert isinstance(msg.lead, WhatsappLead)
    assert isinstance(msg.lead, ConversationLead)
    assert isinstance(msg.lead, WhatsappLead)
    
    assert msg.lead.phone == '134911669XXXXX'
    
    assert msg.text == None
    assert msg.date == 1717858794
    assert msg.metadata == {}
    
    attach = msg.attachments[0]
    assert attach is not None
    assert isinstance(attach, WhatsappAttachment)
    assert attach.file_url is not None and isinstance(attach.file_url, str)
    
    assert attach.mimeType is not None
    
    # try download image
    path = download_media(attach.file_url, attach.mimeType, token)
    
    print(f"Downloaded media to: {path}")
   
   
    