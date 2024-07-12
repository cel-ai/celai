from cel.gateway.model.attachment import FileAttachment
from cel.gateway.model.conversation_lead import ConversationLead
from cel.gateway.model.outgoing.outgoing_message import OutgoingMessage, OutgoingMessageType


class OutgoingTextMessage(OutgoingMessage):
    """This class represents a text outgoing text message object"""
    
    def __init__(self, 
                 content: str,
                 lead: ConversationLead, 
                 metadata: dict = None, 
                 attachments: list[FileAttachment] = None,
                 is_partial: bool = True
                ):
        super().__init__(OutgoingMessageType.TEXT, lead, metadata, attachments, is_partial)
        self.content = content

        assert isinstance(self.content, str), "text must be a string"


    @staticmethod
    def from_dict(data: dict) -> 'OutgoingTextMessage':
        """Creates an OutgoingTextMessage instance from a dictionary"""
        assert isinstance(data, dict),\
            "data must be a dictionary"
        assert "content" in data,\
            "data must have a 'content' key"
        assert "lead" in data,\
            "data must have a 'lead' key"
        assert isinstance(data["lead"], ConversationLead),\
            "lead must be an instance of ConversationLead"
        
        return OutgoingTextMessage(
            content=data["content"],
            lead=data["lead"],
            metadata=data.get("metadata"),
            attachments=[FileAttachment.from_dict(attachment) for attachment in data.get("attachments", [])],
            is_partial=data.get("is_partial", True)
        )
        
    @staticmethod
    def description() -> str:
        return """For a simple text message, use the following structure:
{
    "type": "text",
    "content": "message content",
}"""