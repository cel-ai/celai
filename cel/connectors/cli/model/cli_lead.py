import os
from cel.gateway.model.conversation_lead import ConversationLead
from cel.gateway.model.conversation_peer import ConversationPeer


class CliLead(ConversationLead):

    def __init__(self, **kwargs):
        super().__init__(connector_name="cli", **kwargs)
        # get current process id from os
        self.process_id = os.getpid()


    def get_session_id(self):
        return f"{self.connector_name}:{self.process_id}"  

    def to_dict(self):
        data = super().to_dict()
        data['process_id'] = self.process_id
        return data

    @classmethod
    def from_dict(cls, lead_dict):
        return CliLead()
        

    def __str__(self):
        return f"CliLead: {self.process_id}"
    
    
    @classmethod
    def from_message(cls, **kwargs):
        conversation_peer = ConversationPeer(
            name='terminal',
            id=os.getpid(),
            phone=None,
            avatarUrl=None,
            email=None
        )
        return CliLead(conversation_from=conversation_peer, **kwargs)