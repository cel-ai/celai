from loguru import logger as log
from cel.gateway.model.conversation_lead import ConversationLead
from cel.gateway.model.outgoing.outgoing_message import OutgoingMessage
from cel.gateway.model.outgoing.outgoing_message_text import OutgoingTextMessage



class DefaultMessageEnhancer:
    """This dummy enhancer will map each input text from genAI to a simple text message."""
    
    def __init__(self):
        log.warning("Creating default message enhancer. This is a dummy enhancer. You should try smarter enhancers.")        
                
    async def __call__(self, lead: ConversationLead, 
                  text: str, 
                  is_partial: bool = True) -> OutgoingMessage:
        
        return OutgoingTextMessage(
            lead=lead,
            content=text
        )

