from cel.gateway.model.attachment import FileAttachment
from cel.gateway.model.conversation_lead import ConversationLead
from cel.gateway.model.outgoing.outgoing_message import OutgoingMessage, OutgoingMessageType


class OutgoingSelectMessage(OutgoingMessage):
    """This class represents a specific outgoing message object with select options"""
    
    def __init__(self, 
                 lead: ConversationLead, 
                 metadata: dict = None, 
                 attachments: list[FileAttachment] = None,
                 is_partial: bool = True,
                 content: str = None,
                 options: list[str] = None
                ):
        super().__init__(OutgoingMessageType.SELECT, lead, metadata, attachments, is_partial)
        self.content = content
        self.options = options

        assert isinstance(self.content, str), "body must be a string"
        assert isinstance(self.options, list), "options must be a list"
        for option in self.options:
            assert isinstance(option, str), "each option must be a string"
            
            
    @staticmethod
    def from_dict(data: dict) -> 'OutgoingSelectMessage':
        """Creates an OutgoingSelectMessage instance from a dictionary"""
        assert isinstance(data, dict),\
            "data must be a dictionary"
        assert "content" in data,\
            "data must have a 'content' key"
        assert "options" in data,\
            "data must have a 'options' key"
        assert isinstance(data["options"], list),\
            "options must be a list"
        assert "lead" in data,\
            "data must have a 'lead' key"
        assert isinstance(data["lead"], ConversationLead),\
            "lead must be an instance of ConversationLead"
        
        return OutgoingSelectMessage(
            content=data["content"],
            options=data["options"],
            lead=data["lead"],
            metadata=data.get("metadata"),
            attachments=[FileAttachment.from_dict(attachment) for attachment in data.get("attachments", [])],
            is_partial=data.get("is_partial", True)
        )
        
        
    @staticmethod
    def description() -> str:
        return """When the message asks the user to make a choice, use the following structure:
{
    "type": "select",
    "options": [],
    "content": "A boody text",
}

The options must be a list of strings. Options should be short and clear in title case. 
The prompt is keeped in the content field, and the options are the possible choices.
"""