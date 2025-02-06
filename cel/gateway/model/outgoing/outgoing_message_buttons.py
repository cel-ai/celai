from cel.gateway.model.attachment import FileAttachment
from cel.gateway.model.conversation_lead import ConversationLead
from cel.gateway.model.outgoing.outgoing_message import OutgoingMessage, OutgoingMessageType


class OutgoingButtonsMessage(OutgoingMessage):
    """This class represents a specific outgoing message object with select options"""
    
    def __init__(self, 
                 lead: ConversationLead, 
                 content: str = None,
                 options: list[str] = None,
                 **kwargs
                ):
        super().__init__(OutgoingMessageType.BUTTONS, 
                         lead, **kwargs)
        
        self.content = content
        self.options = options

        assert isinstance(self.content, str), "body must be a string"
        assert isinstance(self.options, list), "options must be a list"
        for option in self.options:
            assert isinstance(option, str), "each option must be a string"
            
    def __str__(self):
        """Returns the content of the message plus the options"""
        return f"{self.content}\n\n" + "\n".join([f"{i + 1}. {option}" for i, option in enumerate(self.options)])
            
    @staticmethod
    def from_dict(data: dict) -> 'OutgoingButtonsMessage':
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
        
        return OutgoingButtonsMessage(
            content=data["content"],
            options=data["options"],
            lead=data["lead"],
            metadata=data.get("metadata"),
            attachments=[FileAttachment.from_dict(attachment) for attachment in data.get("attachments", [])],
            is_partial=data.get("is_partial", True)
        )
        
        
    @staticmethod
    def description() -> str:
        return """When the message asks the user to make a choice between a limited number of options (up to 3).
Ideal for yes/no kind of questions. Use the following structure:
{
    "type": "buttons",
    "options": [],
    "content": "A body text",
}

The options must be a list of strings. Options should be short and clear in title case. Maximum of 3 options and a maximum text of 20 characters.
The prompt is keeped in the content field, and the options are the possible choices.
"""