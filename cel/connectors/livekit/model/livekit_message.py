from cel.gateway.model.message import Message
from cel.gateway.model.conversation_lead import ConversationLead
from cel.gateway.model.base_connector import BaseConnector
from cel.connectors.livekit.model.livekit_lead import LiveKitLead
from loguru import logger as log

class LiveKitMessage(Message):
    """
    LiveKitMessage class to represent a message in the LiveKit connector.
    """

    def __init__(self, lead: ConversationLead, text: str = None):
        """
        Initialize the LiveKitMessage instance.

        Args:
            lead (ConversationLead): The lead associated with the message.
            text (str): The text of the message.
        """
        super().__init__(lead, text=text)

    def is_voice_message(self):
        return False
    
    @classmethod
    async def load_from_message(cls, request, connector: BaseConnector = None):
        """
        Load a LiveKitMessage from a message dictionary.

        Args:
            message_dict (dict): The message dictionary.
            token (str): The token for authentication.
            connector: The connector instance.

        Returns:
            LiveKitMessage: The loaded LiveKitMessage instance.
        """
        log.debug(f"[LiveKit] Raw request in load_from_message: {request}")
        user_message = request.get("user_text")
        
        if not user_message:
            raise ValueError("No message found in the message_dict")

        lead = LiveKitLead.from_message(request, connector=connector)
        return LiveKitMessage(lead=lead, text=user_message)
    
    def __str__(self):
        return f"LiveKitMessage: {self.text}"
    
    def __repr__(self):
        return f"LiveKitMessage: {self.text}"
