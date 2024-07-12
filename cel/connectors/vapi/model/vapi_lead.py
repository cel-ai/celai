import time
from cel.gateway.model.conversation_lead import ConversationLead
from cel.gateway.model.conversation_peer import ConversationPeer


class VAPILead(ConversationLead):
    """ VAPILead class """

    def __init__(self, call_object: dict, **kwargs):
        """ VAPILead constructor 
        
        Args:
            call_object (dict): Call object
            Sample:
            {
                "id": "c7719e5c-ea98-40e1-b1dc-66131da31532",
                "orgId": "2ac97024-f9e9-425e-a846-ce5e2e3540f1",
                "createdAt": "2024-07-02T05:29:55.903Z",
                "updatedAt": "2024-07-02T05:29:55.903Z",
                "type": "webCall",  
                "status": "queued",
                "assistantId": "1d9d46ba-618e-4867-8797-5a8dc2f9f42x",
                "webCallUrl": "https://vapi.daily.co/E3pM5r6l7Q82gT4hElS7"
            }
        
        """
        super().__init__(connector_name="vapi", **kwargs)
        self.call_object: dict = call_object


    def get_session_id(self):
        return f"{self.connector_name}:{self.call_object['id']}"  

    def to_dict(self):
        data = super().to_dict()
        data['call_object'] = self.call_object
        return data

    @classmethod
    def from_dict(cls, lead_dict):
        return VAPILead(
            call_object=lead_dict.get("call_object")
        )

    def __str__(self):
        return f"VAPILead: {self.call_object['id']}"
    
    
    @classmethod
    def from_vapi_message(cls, message: dict, **kwargs):
        call_object = message['call']
        metadata = {
            'date': time.time(),
            'raw': message
        }
        conversation_peer = ConversationPeer(
            name='Unknown',
            id=call_object['id'],
            phone=None,
            avatarUrl=None,
            email=None
        )
        return VAPILead(call_object=call_object, metadata=metadata, conversation_from=conversation_peer, **kwargs)