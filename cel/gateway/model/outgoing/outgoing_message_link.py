from cel.gateway.model.attachment import FileAttachment
from cel.gateway.model.conversation_lead import ConversationLead
from cel.gateway.model.outgoing.outgoing_message import OutgoingMessage, OutgoingMessageType


class OutgoingLinkMessage(OutgoingMessage):
    """This class represents a specific outgoing message object with a link"""
    
    def __init__(self, 
                 lead: ConversationLead, 
                 metadata: dict = None, 
                 attachments: list[FileAttachment] = None,
                 is_partial: bool = True,
                 content: str = None,
                 links: list = None
                ):
        super().__init__(OutgoingMessageType.LINK, lead, metadata, attachments, is_partial)
        self.content = content
        self.links = links

        assert isinstance(self.content, str), "body must be a string"
        assert isinstance(self.links, list), "link must be a list"


    @staticmethod
    def from_dict(data: dict) -> 'OutgoingLinkMessage':
        """Creates an OutgoingLinkMessage instance from a dictionary"""
        assert isinstance(data, dict),\
            "data must be a dictionary"
        assert "content" in data,\
            "data must have a 'content' key"
        assert "links" in data,\
            "data must have a 'links' key"
        assert "lead" in data,\
            "data must have a 'lead' key"
        assert isinstance(data["lead"], ConversationLead),\
            "lead must be an instance of ConversationLead"
            
        for link in data["links"]:
            # link mus have a text and a url
            assert "text" in link, f"link: {link} must have a 'text' key"
            assert "url" in link, f"link: {link} must have a 'url' key"
        
        return OutgoingLinkMessage(
            content=data["content"],
            links=data["links"],
            lead=data["lead"],
            metadata=data.get("metadata"),
            attachments=[FileAttachment.from_dict(attachment) for attachment in data.get("attachments", [])],
            is_partial=data.get("is_partial", True)
        )
        
    @staticmethod
    def description() -> str:
        return """If the contains a link, you will generate a message of type link with the information from the text.
{
    "type": "link",
    "content": "A boody text",
    "links": [
        {"text": "link text", "url": "https://link.url"}
    ]
}"""