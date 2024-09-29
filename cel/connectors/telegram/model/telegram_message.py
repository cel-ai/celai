from cel.gateway.model.base_connector import BaseConnector
from cel.connectors.telegram.model.telegram_attachment import TelegramAttachment
from cel.connectors.telegram.model.telegram_lead import TelegramLead
from cel.gateway.model.conversation_lead import ConversationLead
from cel.gateway.model.message import Message


class TelegramMessage(Message):
    
    def __init__(self, 
                 lead: ConversationLead, 
                 text: str = None, 
                 metadata: dict = None, 
                 date: int = None,
                 attachments: list[TelegramAttachment] = None
                ):
        super().__init__(lead, text=text, date=date, metadata=metadata, attachments=attachments)
    
    
    def is_voice_message(self):
        #  check if the message has a voice attachment
        if self.attachments:
            for attach in self.attachments:
                if attach.type == "voice":
                    return True
        return False
    
    @classmethod
    async def load_from_message(cls, message_dict, token: str, connector: BaseConnector = None):
        msg = message_dict.get("message")
        # get text from message or caption if it is a media message
        text = msg.get("text") or msg.get("caption")
        
        # if text begins with /start, it is a command
        if text and text.startswith("/start"):
            # decode the arguments
            args = text.split(" ")[1:]
            # decode string from base64
            import base64
            text = base64.b64decode(args[0]).decode("utf-8")
        
        date = msg.get("date")
        metadata = {'raw': msg}
        lead = TelegramLead.from_telegram_message(msg, connector=connector)
        attach = await TelegramAttachment.load_from_message(message_dict, token)
        return TelegramMessage(lead=lead, text=text, date=date, metadata=metadata, attachments=[attach] if attach else None)
        

    def __str__(self):
        return f"TelegramMessage: {self.text}"
        
    def __repr__(self):
        return f"TelegramMessage: {self.text}"
    
    