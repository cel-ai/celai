import os
import time
import pytest
from cel.gateway.model.base_connector import BaseConnector
from cel.connectors.whatsapp.model.whatsapp_lead import WhatsappLead
from cel.connectors.whatsapp.model.whatsapp_message import WhatsappMessage
from cel.gateway.model.conversation_lead import ConversationLead
import dotenv

dotenv.load_dotenv()


sample_message = {
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
                                    "name": "Alejandro"
                                },
                                "wa_id": "549116693XXXX"
                            }
                        ],
                        "messages": [
                            {
                                "from": "549116693XXXX",
                                "id": "wamid.HBgNNTQ5MTE2NjkzNzg0OBUCABIYFDNxxx==",
                                "timestamp": "1717847190",
                                "text": {
                                    "body": "Hello!"
                                },
                                "type": "text"
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
    msg: WhatsappMessage = await WhatsappMessage.load_from_message(sample_message, 
                                                                    connector=base_conn,
                                                                    token=token,
                                                                    phone_number_id=phone_number)
                                                                    
    end = time.time()
    enlapced = end - start
    print(f"Elapsed time: {enlapced}")
    
    assert isinstance(msg.lead, WhatsappLead)
    assert isinstance(msg.lead, ConversationLead)
    assert isinstance(msg.lead, WhatsappLead)
    
    assert msg.lead.phone == '549116693XXXX'
    
    assert msg.text == "Hello!"
    assert msg.date == 1717847190
    assert msg.metadata == {}
    
   
    