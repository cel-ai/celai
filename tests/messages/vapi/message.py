import pytest
from cel.connectors.telegram.model.telegram_message import TelegramMessage
from cel.connectors.vapi.model.vapi_lead import VAPILead
from cel.connectors.vapi.model.vapi_message import VAPIMessage
from cel.gateway.model.conversation_lead import ConversationLead
from cel.connectors.telegram.model.telegram_lead import TelegramLead
import dotenv

dotenv.load_dotenv()

request = {
    "model": "gpt-3.5-turbo",
    "messages": [
        {
            "role": "system",
            "content": "This is a blank template with minimal defaults, you can change the model, temperature, and messages."
        },
        {
            "role": "assistant",
            "content": "Hi. My name is John."
        },
        {
            "role": "user",
            "content": "Hi."
        }
    ],
    "temperature": 0.7,
    "stream": True,
    "max_tokens": 250,
    "call": {
        "id": "c7719e5c-ea98-40e1-b1dc-66131da31532",
        "orgId": "2ac97024-f9e9-425e-a846-ce5e2e3540f1",
        "createdAt": "2024-07-02T05:29:55.903Z",
        "updatedAt": "2024-07-02T05:29:55.903Z",
        "type": "webCall",  
        "status": "queued",
        "assistantId": "1d9d46ba-618e-4867-8797-5a8dc2f9f42x",
        "webCallUrl": "https://vapi.daily.co/E3pM5r6l7Q82gThElS7"
    },
    "metadata": {}
}



@pytest.mark.asyncio
async def test_parse_message():

   msg: VAPIMessage = await VAPIMessage.load_from_message(request)
   
   assert isinstance(msg.lead, VAPILead)
   assert isinstance(msg.lead, ConversationLead)
   
   assert msg.lead.get_session_id() == f"vapi:{request['call']['id']}"
   assert msg.lead.call_object == request['call']
   
   assert msg.text == "Hi."
   assert msg.date is not None
    
    