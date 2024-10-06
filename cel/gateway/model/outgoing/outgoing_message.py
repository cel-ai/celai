from abc import ABC
import datetime
from cel.gateway.model.attachment import FileAttachment
from cel.gateway.model.conversation_lead import ConversationLead

class OutgoingMessageType:
    TEXT = "text"
    IMAGE = "image"
    AUDIO = "audio"
    VOICE = "voice"
    VIDEO = "video"
    DOCUMENT = "document"
    LOCATION = "location"
    CONTACT = "contact"
    
    SELECT = "select"
    LINK = "link"


class OutgoingMessage(ABC):
    """This class represents a generic outgoing message object"""
    
    def __init__(self, 
                #  outgoing message type:
                 type: str,
                 lead: ConversationLead, 
                 metadata: dict = None, 
                 attachments: list[FileAttachment] = None,
                 is_partial: bool = True
                ):
        self.date = datetime.datetime.now().timestamp()
        self.attachments: list[FileAttachment] = attachments
        self.lead = lead
        self.metadata = metadata
        self.is_partial = is_partial
        self.type = type
        
        assert isinstance(self.lead, ConversationLead),\
            "lead must be an instance of ConversationLead"
        assert self.metadata is None or isinstance(self.metadata, dict),\
            "metadata must be a dictionary"
        assert self.attachments is None or isinstance(self.attachments, list),\
            "attachments must be a list"
        assert self.type in [OutgoingMessageType.TEXT, 
                        OutgoingMessageType.IMAGE, 
                        OutgoingMessageType.AUDIO, 
                        OutgoingMessageType.VIDEO, 
                        OutgoingMessageType.DOCUMENT, 
                        OutgoingMessageType.LOCATION, 
                        OutgoingMessageType.CONTACT, 
                        OutgoingMessageType.SELECT, 
                        OutgoingMessageType.LINK],\
            "type must be a valid OutgoingMessageType"
        
        