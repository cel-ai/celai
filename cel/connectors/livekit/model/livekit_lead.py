from cel.gateway.model.conversation_lead import ConversationLead
from cel.gateway.model.conversation_peer import ConversationPeer


class LiveKitLead(ConversationLead):
    """ LiveKitLead class."""

    def __init__(self, call_object: dict, **kwargs):
        super().__init__(connector_name="livekit", **kwargs)
        self.call_object: dict = call_object

    def get_session_id(self):
        return f"{self.connector_name}:{self.call_object['session_id']}"
    
    @classmethod
    def from_message(cls, message: dict, **kwargs):
        conversation_peer = ConversationPeer(
            name='Unknown',
            id=message['session_id'],
            phone=None,
            avatarUrl=None,
            email=None,
        )
        return LiveKitLead(call_object=message, conversation_from=conversation_peer, **kwargs)
