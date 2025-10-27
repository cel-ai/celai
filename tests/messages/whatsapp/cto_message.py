import os
import time
import pytest
from cel.gateway.model.base_connector import BaseConnector
from cel.connectors.whatsapp.model.whatsapp_lead import WhatsappLead
from cel.connectors.whatsapp.model.whatsapp_message import WhatsappMessage
from cel.gateway.model.conversation_lead import ConversationLead
from cel.connectors.whatsapp.whatsapp_connector import WhatsappConnector
import dotenv

dotenv.load_dotenv()


sample_message = {
  "object": "whatsapp_business_account",
  "entry": [
    {
      "id": "11232312744885479",
      "changes": [
        {
          "value": {
            "messaging_product": "whatsapp",
            "metadata": {
              "display_phone_number": "15553453430",
              "phone_number_id": "16563546234234282"
            },
            "contacts": [
              {
                "profile": { "name": "Ruben Sarasa" },
                "wa_id": "52161231257946"
              }
            ],
            "messages": [
              {
                "from": "52161231257946",
                "id": "wamid.SDFAASDASDSADS==",
                "timestamp": "1746830741",
                "type": "contacts",
                "contacts": [
                  {
                    "name": {
                      "first_name": "Jonathan",
                      "last_name": "Doe",
                      "formatted_name": "Jonathan Doe"
                    },
                    "phones": [
                      {
                        "phone": "+1 123 205 1111",
                        "wa_id": "5216621111",
                        "type": "CELL"
                      }
                    ]
                  }
                ]
              }
            ]
          },
          "field": "messages"
        }
      ]
    }
  ]
}


@pytest.fixture
def connector():
    # Create Whatsapp Connector
    return WhatsappConnector(phone_number_id="123456", token="123:ASD", verify_token="1234") 

@pytest.mark.asyncio
async def test_parse_text_message(connector):
   
    token = os.getenv('WHATSAPP_TOKEN')
    phone_number = os.getenv('WHATSAPP_PHONE_NUMBER_ID')

    
    start = time.time()
    msg: WhatsappMessage = await WhatsappMessage.load_from_message(sample_message, 
                                                                    connector=connector,
                                                                    token=token,
                                                                    phone_number_id=phone_number)
                                                                    
    end = time.time()
    enlapced = end - start
    print(f"Elapsed time: {enlapced}")
    
    assert isinstance(msg.lead, WhatsappLead)
    assert isinstance(msg.lead, ConversationLead)
    assert isinstance(msg.lead, WhatsappLead)
    
    assert msg.lead.phone == '5261231257946'
    
    assert len(msg.attachments) > 0
    assert msg.attachments[0].type == 'contact'
    assert msg.attachments[0].name == 'Jonathan Doe'
    assert len(msg.attachments[0].metadata.get("phones", [])) == 1
    assert msg.attachments[0].metadata.get("phones")[0].get('phone') == '+1 123 205 1111'
    
    # breakpoint()
   
    