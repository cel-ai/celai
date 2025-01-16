from abc import abstractmethod
from loguru import logger as log
from cel.assistants.base_assistant import BaseAssistant
from cel.gateway.model.base_connector import BaseConnector
from cel.gateway.model.message import Message
from cel.gateway.model.message_gateway_context import MessageGatewayContext
from cel.gateway.model.outgoing.outgoing_message import OutgoingMessage


class BaseMiddleware:

    @abstractmethod
    async def incoming_message(self,  
                               message: Message, 
                               connector: BaseConnector, 
                               assistant: BaseAssistant):
        
        raise NotImplementedError
    
    
    
    @abstractmethod
    async def outgoing_message(self, 
                               message: OutgoingMessage, 
                               connector: BaseConnector, 
                               assistant: BaseAssistant, 
                               is_partial: bool = False, 
                               is_summary: bool = False,
                               mode = None):
        
        raise NotImplementedError
    
    
    
    @abstractmethod
    async def startup(self, ctx: MessageGatewayContext):
        pass