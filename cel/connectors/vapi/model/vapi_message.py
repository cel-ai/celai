import time
from loguru import logger as log
from cel.connectors.vapi.model.vapi_lead import VAPILead
from cel.gateway.model.base_connector import BaseConnector
from cel.connectors.telegram.model.telegram_attachment import TelegramAttachment
from cel.connectors.telegram.model.telegram_lead import TelegramLead
from cel.gateway.model.conversation_lead import ConversationLead
from cel.gateway.model.message import Message


class VAPIMessage(Message):
    
    def __init__(self, 
                 lead: ConversationLead, 
                 text: str = None, 
                 metadata: dict = None, 
                 date: int = None
                ):
        super().__init__(lead, text=text, date=date, metadata=metadata)
    
    
    def is_voice_message(self):
        #  check if the message has a voice attachment
        return False
    
    @classmethod
    async def load_from_message(cls, request, connector: BaseConnector = None):
        
        try: 
            messages = request.get("messages")
            if not messages:
                raise ValueError("No messages found in the message_dict")
            
            # take the last message
            user_message = messages[-1]
            
            if not user_message:
                raise ValueError("No message found in the message_dict")
            
            if user_message.get("role") != "user":
                raise ValueError("The message is not from a user")
            
            # get text from message or caption if it is a media message
            text = user_message.get("content")
            date = time.time()
            metadata = {'raw': user_message}
            lead = VAPILead.from_vapi_message(request, connector=connector)
            return VAPIMessage(lead=lead, text=text, date=date, metadata=metadata)
        except Exception as e:
            log.error(f"Error loading VAPI message from message_dict: {e}")
            return None        

    def __str__(self):
        return f"TelegramMessage: {self.text}"
        
    def __repr__(self):
        return f"TelegramMessage: {self.text}"
    
    