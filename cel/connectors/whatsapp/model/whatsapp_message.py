from cel.gateway.model.base_connector import BaseConnector
from cel.connectors.whatsapp.model.whatsapp_attachment import WhatsappAttachment
from cel.connectors.whatsapp.model.whatsapp_lead import WhatsappLead
from cel.gateway.model.conversation_lead import ConversationLead
from cel.gateway.model.message import Message


class WhatsappMessage(Message):
    
    def __init__(self, 
                 lead: ConversationLead, 
                 text: str = None, 
                 metadata: dict = None, 
                 date: int = None,
                 attachments: list[WhatsappAttachment] = None,
                 id: str = None
                ):
        super().__init__(lead, 
                         text=text, 
                         date=date, 
                         metadata=metadata, 
                         attachments=attachments, 
                         id=id)
    
    
    def is_voice_message(self):
        # TODO: Implement voice message check
        return False

    
    
# {
#     "object": "whatsapp_business_account",
#     "entry": [
#         {
#             "id": "103048736088448",
#             "changes": [
#                 {
#                     "value": {
#                         "messaging_product": "whatsapp",
#                         "metadata": {
#                             "display_phone_number": "15550463673",
#                             "phone_number_id": "105602452496989"
#                         },
#                         "contacts": [
#                             {
#                                 "profile": {
#                                     "name": "Alejandro"
#                                 },
#                                 "wa_id": "5491166937848"
#                             }
#                         ],
#                         "messages": [
#                             {
#                                 "from": "5491166937848",
#                                 "id": "wamid.HBgNNTQ5MTE2NjkzNzg0OBUCABIYFDNBQTdBQzAzMDMxOTVBQkQ3QzU5AA==",
#                                 "timestamp": "1717847190",
#                                 "text": {
#                                     "body": "hola"
#                                 },
#                                 "type": "text"
#                             }
#                         ]
#                     },
#                     "field": "messages"
#                 }
#             ]
#         }
#     ]
# }    
    
    
    
    
    @classmethod
    async def load_from_message(cls, 
                                data: dict, 
                                connector: BaseConnector, 
                                token: str,
                                phone_number_id: str = None):
        
        assert token is not None, "token must be provided for attachment download"
        
        assert isinstance(data, dict), "data must be a dictionary"
        assert isinstance(connector, BaseConnector), "connector must be an instance of BaseConnector"
        assert "entry" in data, "data must have an entry key"
        
        entry = data.get("entry")
        assert isinstance(entry, list), "entry must be a list"
        assert len(entry) > 0, "entry must have at least one element"
        
        entry0 = entry[0]
        assert isinstance(entry0, dict), "first entry must be a dictionary"
        assert "changes" in entry0, "first entry must have a changes key"
        
        changes = entry0.get("changes")
        assert isinstance(changes, list), "changes must be a list"
        assert len(changes) > 0, "changes must have at least one element"
        
        change0 = changes[0]
        assert isinstance(change0, dict), "first change must be a dictionary"
        
        change0 = change0.get("value")
        msg0 = change0.get("messages")[0]

        # get text from message or caption if it is a media message
        text = msg0.get("text", {}).get("body") 
        date = int(msg0.get("timestamp"))
        id = msg0.get("id")
        metadata = {}
        lead = WhatsappLead.from_whatsapp_message(data, connector=connector)
        attach = await WhatsappAttachment.load_from_message(data, token, phone_number_id)
        return WhatsappMessage(lead=lead,
                               id=id,
                               text=text,
                               date=date,
                               metadata=metadata,
                               attachments=[attach] if attach else None
                            )
        

    def __str__(self):
        return f"TelegramMessage: {self.text}"
        
    def __repr__(self):
        return f"TelegramMessage: {self.text}"
    
    