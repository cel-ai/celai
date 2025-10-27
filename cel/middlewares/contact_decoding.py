import json
from loguru import logger as log
from cel.assistants.base_assistant import BaseAssistant
from cel.gateway.model.base_connector import BaseConnector
from cel.gateway.model.message import Message
from cel.gateway.model.attachment import ContactAttachment



class ContactDecodingMiddleware:
    
    
    def __init__(self, 
                 msg_prefix: str = "User shared a contact: ",
                 on_fail_message: str = 'User shared a contact but it could not be decoded.'):
        log.debug(f"ContactDecodingMiddleware initialized")
        self.msg_prefix = msg_prefix
        self.on_fail_message = on_fail_message

        
    async def __call__(self, message: Message, connector: BaseConnector, assistant: BaseAssistant):
        assert isinstance(message, Message), "Message must be a Message object"
        
        try:
            
            
            if not message.attachments or len(message.attachments) < 1:
                return True
            
            # Get first attachment
            attach = message.attachments[0]
            
            if attach.type != "contact":
                log.error(f"Attachment is not a voice message")
                return True
            
            log.debug(f"Message {message.lead.get_session_id()} -> Decoding contact attachment")
            
            assert isinstance(attach, ContactAttachment), "Attachment must be a ContactAttachment"
            
            # Decode contact attachment
            cto_metadata = attach.metadata
            cto_name = attach.name
            
            # Build contact text
            cto_data = json.dumps(cto_metadata)
            text = f"{self.msg_prefix} Name: {cto_name}. Data: {cto_data}"
            
            # if text is empty or None, set the on_fail_message
            message.text = text if text else self.on_fail_message
            
            return True
        except Exception as e:
            log.error(f"Failed to decode contact attachment: {e}")
            # return True, so fails on STT won't stop the message processing
            if self.on_fail_message:
                message.text = self.on_fail_message
            return True
        
    
