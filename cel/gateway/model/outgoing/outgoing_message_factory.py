from cel.gateway.model.conversation_lead import ConversationLead
from cel.gateway.model.outgoing.outgoing_message import OutgoingMessage, OutgoingMessageType
from cel.gateway.model.outgoing.outgoing_message_link import OutgoingLinkMessage
from cel.gateway.model.outgoing.outgoing_message_select import OutgoingSelectMessage
from cel.gateway.model.outgoing.outgoing_message_text import OutgoingTextMessage
from loguru import logger as log

def outgoing_message_from_dict(data: dict) -> OutgoingMessage:
    
    try:
        """Creates an OutgoingMessage instance from a dictionary"""
        assert isinstance(data, dict),\
            "data must be a dictionary"
        assert "type" in data,\
            "data must have a 'type' key"
        
        if data["type"] == OutgoingMessageType.TEXT:
            return OutgoingTextMessage.from_dict(data)
        
        if data["type"] == OutgoingMessageType.SELECT:
            return OutgoingSelectMessage.from_dict(data)
        
        if data["type"] == OutgoingMessageType.LINK:
            return OutgoingLinkMessage.from_dict(data)
        
        # TODO: add other message types here
        raise ValueError(f"Not implemented message type: {data['type']}")
        
    except AssertionError as e:
        log.error(f"Invalid outgoing message creating params: {e}")
        raise e
    except Exception as e:
        log.error(f"Error creating outgoing message: {e}")
        raise e
        
        

    