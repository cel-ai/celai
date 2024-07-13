from cel.connectors.whatsapp.phone_utils import filter_phone_number
from cel.gateway.model.conversation_lead import ConversationLead
from cel.gateway.model.conversation_peer import ConversationPeer


class WhatsappLead(ConversationLead):

    def __init__(self, phone: str, connector_name: str = None, **kwargs):
        super().__init__(connector_name=connector_name or 'whatsapp', **kwargs)
        self.phone: str = filter_phone_number(str(phone))

    def get_session_id(self):
        return f"{self.connector_name}:{self.phone}"  

    def to_dict(self):
        data = super().to_dict()
        data['phone'] = self.phone
        return data

    @classmethod
    def from_dict(cls, lead_dict):
        return WhatsappLead(
            phone=lead_dict.get("phone"),
            metadata=lead_dict.get("metadata")
        )

    def __str__(self):
        return f"WhatsappLead: {self.phone}"
    
    @classmethod
    def from_whatsapp_message(cls, data: dict, **kwargs):
        assert isinstance(data, dict), "data must be a dictionary"
        
        phone = data.get("entry")[0].get("changes")[0].get("value").get("contacts")[0].get("wa_id")
        
        metadata = {
            'phone_number_id': data.get("entry")[0].get("changes")[0].get("value").get("metadata").get("phone_number_id"),
            'display_phone_number': data.get("entry")[0].get("changes")[0].get("value").get("metadata").get("display_phone_number"),
            'message_id': data.get("entry")[0].get("id"),
            'date': data.get("entry")[0].get("changes")[0].get("value").get("timestamp"),
            'raw': data,
            'wamid': data.get("entry")[0].get("changes")[0].get("value").get("messages")[0].get("id")
        }
        conversation_peer = ConversationPeer(
            name=data.get("entry")[0].get("changes")[0].get("value").get("contacts")[0].get("profile").get("name"),
            id=data.get("entry")[0].get("changes")[0].get("value").get("contacts")[0].get("wa_id"),
            phone=phone,
            avatarUrl=None,
            email=None
        )
        return WhatsappLead(phone=phone, metadata=metadata, conversation_from=conversation_peer, **kwargs)