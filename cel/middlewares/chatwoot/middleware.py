from typing import Any, Dict
from urllib.parse import urljoin
from fastapi import HTTPException
import shortuuid
from cel.assistants.base_assistant import BaseAssistant
from cel.gateway.message_gateway import StreamMode
from cel.gateway.model.base_connector import BaseConnector
from cel.gateway.model.message import Message
from cel.gateway.model.message_gateway_context import MessageGatewayContext
from cel.gateway.model.middleware import BaseMiddleware
from cel.gateway.model.outgoing.outgoing_message import OutgoingMessage
from cel.middlewares.chatwoot.conversation_manager import ConversationManager
from cel.middlewares.chatwoot.model import ContactLead
from loguru import logger as log


class ChatwootMiddleware(BaseMiddleware):

    def __init__(self, base_url: str, access_key: str, account_id: str, inbox_name: str, auto_create_inbox: bool = True):
        self.conversation_manager = None
        self.base_url = base_url    
        self.access_key = access_key
        self.account_id = account_id
        self.inbox_name = inbox_name
        self.auto_create_inbox = auto_create_inbox
        # random generate a code for the webhook using short uuid
        self.security_token = shortuuid.uuid()
        
    def create_contact_from_incoming_message(self, message: Message) -> ContactLead:
        return ContactLead(
            identifier=message.lead.get_session_id(),
            name=message.lead.conversation_from.name,
            phone_number=message.lead.conversation_from.phone
        )

            
    async def startup(self, ctx: MessageGatewayContext):
        
        endpoint_url = await self.setup_routes(ctx.app)
        
        webhook_url = urljoin(ctx.webhook_url, endpoint_url)
        
        self.conversation_manager = ConversationManager(
            base_url=self.base_url,
            access_key=self.access_key,
            webhook_url=webhook_url,
            account_id=self.account_id,
            inbox_name=self.inbox_name
        )
    
        await self.conversation_manager.init(auto_create_inbox=self.auto_create_inbox)
        
        
    async def setup_routes(self, app):
        log.debug("Setting up Chatwoot middleware routes")
        prefix = "/middleware/chatwoot"
        
        
        # Add echo route
        @app.get(prefix + "/echo")
        async def echo():
            return {"status": "ok"}
        
        @app.post(prefix + "/messages/{security_token}", 
                 summary="Incoming message",
                 description="This endpoint receives incoming messages from Chatwoot")
        async def incoming_message(security_token: str, payload: Dict[Any, Any]):
            # check code is == self.code
            if security_token != self.security_token:
                raise HTTPException(status_code=401, detail="Unauthorized")
            
            # message_type = payload.get("message_type")
            log.debug(f"Incoming message: {payload}")
            # Messages that may be sent by a Chatwoot Support Agent directly
            # to the user. We can ignore these messages.
            # if message_type == "outgoing":
                # return {"status": "ok"}
            
            return {"status": "ok"}
            

        message_endpoint_url = f"{prefix}/messages/{self.security_token}"
        return message_endpoint_url
    
    
    async def incoming_message(self,  message: Message, connector: BaseConnector, assistant: BaseAssistant):
        
        try:
            assert self.conversation_manager is not None, "ChatwootMiddleware is not initialized"
            
            cto = self.create_contact_from_incoming_message(message)
            await self.conversation_manager.send_incoming_text_message(cto, message.text)
            
            return True
        except Exception as e:
            log.error(f"Middleware Chatwoot: Error processing incoming message: {e}")
            return True
    
    
    
    async def outgoing_message(self, 
                               message: OutgoingMessage, 
                               connector: BaseConnector, 
                               assistant: BaseAssistant,
                               is_partial: bool = False, 
                               is_summary: bool = False,
                               mode: StreamMode = None):
        
        try:
            assert self.conversation_manager is not None, "ChatwootMiddleware is not initialized"
                    
            if (mode == StreamMode.FULL and not is_summary) or (mode != StreamMode.FULL and is_summary):
                cto = self.create_contact_from_incoming_message(message)
                await self.conversation_manager.send_outgoing_text_message(cto, str(message))
            
            return True
        except Exception as e:
            log.error(f"Middleware Chatwoot: Error processing outgoing message: {e}")
            return True