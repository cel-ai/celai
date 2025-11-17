import asyncio
import json
from typing import Any, Dict
from urllib.parse import urljoin
from fastapi import HTTPException
import shortuuid
from cel.assistants.base_assistant import BaseAssistant
from cel.gateway.message_gateway import StreamMode
from cel.gateway.model.base_connector import BaseConnector
from cel.gateway.model.conversation_lead import ConversationLead
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
            phone_number=message.lead.conversation_from.phone,
            celai_lead=ConversationLead.serialize(message.lead)
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
            try:
                log.debug(f"Incoming message: {payload}")
                
                if payload.get("event") == "conversation_updated":
                    # A conversation was updated
                    # we need to check if conversation was assigned to an agent
                    # if the conversation was assigned to an agent, we need to mark the conversation
                    # so Celai does not respond to it
                    changes = payload.get("changed_attributes", [])
                    # if changes array contains an object with assignee_id property defined
                    assignee_id = next((item for item in payload.get("changed_attributes", []) if "assignee_id" in item),{}).get('assignee_id')
                    if assignee_id:
                        # This means the conversation was assigned to an agent
                        # we need to mark the conversation as assigned in Celai
                        # so Celai does not respond to it
                    
                        # Conversation was assigned to an agent
                        messages = payload.get("messages", [])
                        if messages:
                            # Get the last message
                            last_message = messages[-1]
                            conversation_id = last_message.get("conversation_id")
                            if conversation_id:
                                # Mark conversation as assigned
                                conversation = self.conversation_manager.get_conversation_by_id(conversation_id)
                                if conversation:
                                    previous_value = assignee_id.get("previous_value")
                                    current_value = assignee_id.get("current_value")
                                    if current_value:
                                        conversation.assigned = True
                                        log.debug(f"Conversation {conversation_id} assigned to agent, marking as assigned in Celai")
                                    elif previous_value and not current_value:
                                        conversation.assigned = False
                                        log.debug(f"Conversation {conversation_id} unassigned from agent, marking as unassigned in Celai")
                                    
                
                if payload.get("message_type") == "outgoing" and not payload.get("private"):
                    # This is an outgoing message from Chatwoot
                    # we must send it to the client
                    content = payload.get("content", "")
                    if content.startswith("[LOLA]: "):
                        # This is a message from Celai, we can ignore it
                        log.debug("Ignoring Celai message from Chatwoot")
                        return {"status": "ok"}
                    
                    celai_lead = payload.get("conversation", {}).get("custom_attributes", {}).get("celai_lead")
                    if not celai_lead:
                        log.error("No celai_lead found in the message payload", payload=payload)
                        return {"status": "ok"}
                    
                    # Deserialize the lead, context aware
                    lead = ConversationLead.deserialize(celai_lead)
                    content = payload.get("content", "")
                    
                    await lead.connector.send_text_message(lead=lead, text=content)
                    log.debug(f"Message from Chatwoot sent to lead: {lead.get_session_id()} with content: {content}")
                    
            except Exception as e:
                log.error(f"Chatwoot Middleware: Error processing incoming message: {e}")
            
            finally:
                return {"status": "ok"}
            

        message_endpoint_url = f"{prefix}/messages/{self.security_token}"
        return message_endpoint_url
    
    
    async def incoming_message(self,  message: Message, connector: BaseConnector, assistant: BaseAssistant):
        
        try:
            assert self.conversation_manager is not None, "ChatwootMiddleware is not initialized"
            
            cto = self.create_contact_from_incoming_message(message)
            # await self.conversation_manager.send_incoming_text_message(cto, message.text)
            asyncio.create_task(self.conversation_manager.send_incoming_text_message(cto, message.text))
            
            
            conv = await self.conversation_manager.get_conversation(cto.identifier)
            if conv and conv.assigned:
                log.warning(f"Conversation {conv.id} is assigned to an agent, skipping Celai response")
                return False
            
            
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
                asyncio.create_task(self.conversation_manager.send_outgoing_text_message(cto,  '[LOLA]: ' + str(message)))
            
            return True
        except Exception as e:
            log.error(f"Middleware Chatwoot: Error processing outgoing message: {e}")
            return True