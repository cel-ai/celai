from cel.gateway.model.conversation_lead import ConversationLead
from cel.gateway.model.conversation_peer import ConversationPeer


class TelegramLead(ConversationLead):

    def __init__(self, chat_id: str, **kwargs):
        super().__init__(connector_name="telegram", **kwargs)
        self.chat_id: str = str(chat_id)


    def get_session_id(self):
        return f"{self.connector_name}:{self.chat_id}"  

    def to_dict(self):
        data = super().to_dict()
        data['chat_id'] = self.chat_id
        return data

    @classmethod
    def from_dict(cls, lead_dict):
        return TelegramLead(
            chat_id=lead_dict.get("chat_id"),
            metadata=lead_dict.get("metadata")
        )

    def __str__(self):
        return f"TelegramLead: {self.chat_id}"
    
    
    @classmethod
    def from_telegram_message(cls, message: dict, **kwargs):
        chat_id = str(message['chat']['id'])
        metadata = {
            'message_id': str(message['message_id']),
            'date': message['date'],
            'raw': message
        }
        conversation_peer = ConversationPeer(
            name=message['from']['first_name'],
            id=str(message['from']['id']),
            phone=None,
            avatarUrl=None,
            email=None
        )
        return TelegramLead(chat_id=chat_id, metadata=metadata, conversation_from=conversation_peer, **kwargs)