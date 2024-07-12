import time
from cel.connectors.cli.model.cli_lead import CliLead
from cel.gateway.model.base_connector import BaseConnector
from cel.connectors.telegram.model.telegram_attachment import TelegramAttachment
from cel.connectors.telegram.model.telegram_lead import TelegramLead
from cel.gateway.model.conversation_lead import ConversationLead
from cel.gateway.model.message import Message


class CliMessage(Message):
    
    def __init__(self, 
                 lead: ConversationLead, 
                 text: str = None, 
                 metadata: dict = None, 
                 date: int = None,
                 attachments: list[TelegramAttachment] = None
                ):
        super().__init__(lead, 
                         text=text, 
                         date=date, 
                         metadata=metadata, 
                         attachments=attachments)
    
    
    def is_voice_message(self):
        return False
    
    @classmethod
    async def load_from_message(cls, 
                                message: str,
                                connector: BaseConnector = None):
 
        # get text from message or caption if it is a media message
        text = message
        date = int(time.time())
        lead = CliLead.from_message(connector=connector)
        return CliMessage(lead=lead, 
                          text=text, 
                          date=date)
        

    def __str__(self):
        return f"CliMessage: {self.text}"
        
    def __repr__(self):
        return f"CliMessage: {self.text}"
    
    