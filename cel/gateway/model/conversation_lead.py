from abc import ABC
import json

import shortuuid
from cel.gateway.model.base_connector import BaseConnector
from cel.gateway.model.conversation_peer import ConversationPeer


class ConversationLead(ABC):

    def __init__(self, 
                 connector_name: str = None, 
                 metadata : dict = None, 
                 conversation_from: ConversationPeer = None,
                 connector: BaseConnector = None):
        self.connector_name = connector_name or "unknown"
        self.metadata = metadata
        self.conversation_from = conversation_from
        self.tmp_id = shortuuid.uuid()
        self.connector = connector

    def get_session_id(self):
        """ This method should be overriden in the child class """
        return self.tmp_id

    def to_dict(self):
        return {
            'connector_name': self.connector_name,
            'metadata': self.metadata,
            'conversation_from': self.conversation_from.to_dict() if self.conversation_from else None
        }

    def to_json(self):
        return json.dumps(self.to_dict())
    
    @classmethod
    def from_dict(cls, lead_dict):
        return ConversationLead(
            connector_name=lead_dict.get("connector_name"),
            metadata=lead_dict.get("metadata"),
            conversation_from=ConversationPeer.from_dict(lead_dict.get("conversation_from"))
        )
        
    def __str__(self):
        return f"ConversationLead: {self.connector_name}"
    
