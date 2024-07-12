

from abc import ABC, abstractmethod
from dataclasses import dataclass
import datetime

from .attachment import FileAttachment
from .conversation_lead import ConversationLead



class Message(ABC):
    """This class represents a generic message object that can be sent or received by the system.
    this class should be subclassed by the specific message platform such as telegram, slack, whatsapp, etc.
    """
    def __init__(self, 
                 lead: ConversationLead, 
                 text: str = None, 
                 date: int = None, 
                 metadata: dict = None, 
                 attachments: list[FileAttachment] = None,
                 isSTT: bool = False,
                 id: str = None
                ):
        self.lead = lead
        self.text = text
        self.metadata = metadata
        self.date = date or datetime.datetime.now().timestamp()
        self.attachments: list[FileAttachment] = attachments
        self.isSTT = isSTT or False
        self.id = id
        
    @abstractmethod
    def is_voice_message(self):
        """This method should be implemented by the subclass to check if the message is a voice message"""
        raise NotImplementedError
    
    @classmethod
    def load_from_dict(cls, message_dict: dict):
        """This method should be implemented by the subclass to load the message from the message object"""
        raise NotImplementedError