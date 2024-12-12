import pytest
from cel.connectors.whatsapp.model.whatsapp_lead import WhatsappLead
from cel.connectors.whatsapp.whatsapp_connector import WhatsappConnector


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
                                    "name": "John Doe"
                                },
                                "wa_id": "13566693XXXX"
                            }
                        ],
                        "messages": [
                            {
                                "from": "13566693XXXX",
                                "id": "wamid.HBgNNTQ5MTE2NjkzNzg0OBUCABIYFDNxxx==",
                                "timestamp": "1717847190",
                                "text": {
                                    "body": "hola"
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



@pytest.fixture
def connector():
    # Create Whatsapp Connector
    return WhatsappConnector(phone_number_id="123456", token="123:ASD", verify_token="1234") 


@pytest.mark.asyncio
async def test_parse_lead():

    lead = WhatsappLead.from_whatsapp_message(sample_message)
    
    assert isinstance(lead, WhatsappLead)
    
    assert lead.phone == '13566693XXXX'
    assert lead.metadata.get('display_phone_number') == '15550463673'
    assert lead.metadata.get('phone_number_id') == '105602452496989'
    assert lead.conversation_from.name == 'John Doe'
    assert lead.conversation_from.phone == '13566693XXXX'
    assert lead.conversation_from.id == '13566693XXXX'
    
    
    
@pytest.mark.asyncio
async def test_parse_lead(connector):

    lead = WhatsappLead.from_whatsapp_message(sample_message, connector=connector)
    assert isinstance(lead, WhatsappLead)
