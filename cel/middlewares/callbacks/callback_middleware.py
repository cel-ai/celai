from abc import ABC
import re
import time
from typing import Any, Dict, Optional
from fastapi import BackgroundTasks, HTTPException, Request
from pydantic import BaseModel
# from redis import asyncio as aioredis
import json
from dataclasses import asdict, dataclass
from cel.assistants.base_assistant import BaseAssistant
from cel.gateway.message_gateway import MessageGateway
from cel.gateway.model.base_connector import BaseConnector
from cel.gateway.model.conversation_lead import ConversationLead
from cel.gateway.model.message import Message
from loguru import logger as log
from .utils import decode_jwt, generate_encryption_key, generate_link, generate_secret_key

# Redis = aioredis.Redis

class CallbackdMiddleware(ABC):

    def __init__(self, 
                 chat_url: str = None,
                 endpoint: str = "callback",
                 http_verb: str = "GET",
                 secret_key: str = None,
                 encryption_key: str = None,
                ):
        
        self.endpoint = endpoint
        self.chat_url = chat_url
        self.external_url = None
        # secret_key = generate_secret_key()
        # encryption_key = generate_encryption_key()
        self.secret_key = secret_key or generate_secret_key()
        self.encryption_key = encryption_key or generate_encryption_key()

        if http_verb.upper() not in ["GET", "POST"]:
            raise ValueError("HTTP Verb must be GET or POST")
        
        self.http_verb = http_verb




    async def _handle_callback(self, 
                                token: str,  
                                request: Request):
        
        if not token:
            raise HTTPException(status_code=401, detail="Token not found")
        
        try:
        #  Decode token
            json_lead = decode_jwt(token, self.secret_key, self.encryption_key)
            lead = ConversationLead.deserialize(json_lead)
            log.debug(f"Decoded lead: {lead}")
            
            await self.gateway.assistant.call_event('callback', lead, None, lead.connector, data=request.query_params)
            
            return {
                "status": "ok",
                "token": token,
                "params": request.query_params
            }
        
        except Exception as e:
            log.error(f"Error decoding token: {e}")
            raise HTTPException(status_code=401, detail="Error decoding token")

    

    # Setup the middleware with the FastAPI application
    # This method is called when the middleware is added to the FastAPI application
    def setup(self, app):
        """ Setup the middleware with the FastAPI application. Here you can define
        the routes for the invitation system.
        """
        log.debug("Setting up Callback Middleware")
        

        if self.http_verb.upper() == "GET":
            app.get("/" + self.endpoint + "/{token}")(self._handle_callback)
            
        if self.http_verb.upper() == "POST":
            # app.post(f"/{self.endpoint}")(handle_callback)
            log.warning("POST method not implemented yet")

    def on_startup(self, gateway: MessageGateway):
        """ This method is called when the Message Gateway starts."""
        log.debug("Callback Middleware started")
        self.gateway = gateway
        self.external_url = self.gateway.webhook_url

    def generate_callback_url(self, lead: ConversationLead, ttl=180):
        assert isinstance(lead, ConversationLead), "Lead must be a ConversationLead object"
        assert self.external_url, "External URL must be set"
    
        link = generate_link(
            base_url=self.external_url + "/" + self.endpoint,
            secret_key=self.secret_key,
            encryption_key=self.encryption_key,
            data=lead.serialize(),
            ttl=ttl
        )
        log.debug(f"Generated link: {link}")
        return link
            
        
    # MAIN METHOD - Handle the message
    async def __call__(self, message: Message, connector: BaseConnector, assistant: BaseAssistant):
        return True
        # try:
        #     assert isinstance(message, Message), "Message must be a Message object"
        #     assert isinstance(connector, BaseConnector), "Connector must be a BaseConnector object"
        #     assert isinstance(assistant, BaseAssistant), "Assistant must be a BaseAssistant object"
        #     return True
        # except Exception as e:
        #     log.error(f"Error in CallbackdMiddleware: {e}")
        #     return False
    



        entry = await self.get_auth_entry(id)
        if entry:
            entry.client_cmd_enabled = True
            await self.client.hset(self.key_prefix, id, json.dumps(asdict(entry)))
            return entry
        return None