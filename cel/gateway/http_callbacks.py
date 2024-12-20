from abc import ABC
import inspect
import re
import time
from typing import Any, Dict, Optional
from fastapi import BackgroundTasks, HTTPException, Request
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
import json
from dataclasses import asdict, dataclass
from cel.assistants.base_assistant import BaseAssistant
from cel.gateway.model.base_connector import BaseConnector
from cel.gateway.model.conversation_lead import ConversationLead
from cel.gateway.model.message import Message
from loguru import logger as log

from cel.gateway.model.message_gateway_context import MessageGatewayContext
from .utils import decode_jwt, generate_encryption_key, generate_link, generate_secret_key

@dataclass  
class CallbackEntry(ABC):
    handler: callable
    redirect_url: str = None,
    single_use: bool = True

    

class HttpCallbackProvider(ABC):

    def __init__(self, 
                 endpoint: str = "callback",
                 http_verb: str = "GET",
                 secret_key: str = None,
                 encryption_key: str = None,
                ):
        
        self.endpoint = endpoint
        self.external_url = None
        self.secret_key = secret_key or generate_secret_key()
        self.encryption_key = encryption_key or generate_encryption_key()

        if http_verb.upper() not in ["GET", "POST"]:
            raise ValueError("HTTP Verb must be GET or POST")
        
        self.http_verb = http_verb
        
        self.handlers = {}



    async def _handle_callback(self, 
                                token: str,  
                                request: Request):
        
        if not token:
            raise HTTPException(status_code=401, detail="Token not found")
        
        try:
        #  Decode token
            json_data = decode_jwt(token, self.secret_key, self.encryption_key)
            json_lead = json_data.get("lead")
            lead = ConversationLead.deserialize(json_lead)
            log.debug(f"Decoded lead: {lead}")
            
            # await self.gateway.assistant.call_event('callback', lead, None, lead.connector, data=request.query_params)
            handler_id = json_data.get("handler_id")
            entry = self.handlers.get(handler_id)
            
            if not entry or not isinstance(entry, CallbackEntry):
                raise HTTPException(status_code=401, detail="Handler not found")
            
            handler = entry.handler
            params_dict = {}
            try: 
                # Convert QueryParams to dict
                params_dict.update(dict(request.query_params))
                # get request body if it's a POST request
                if self.http_verb.upper() == "POST":
                    body = await request.body()
                    try:
                        body_dict = json.loads(body)
                        params_dict.update(body_dict)
                    except Exception as e:
                        log.error(f"Error parsing body: {e}")
                        raise HTTPException(status_code=401, detail="Error parsing body")
                    
                # handler is coroutine function?
                res = None
                if inspect.iscoroutinefunction(handler):
                    res = await handler(lead, params_dict)
                else:
                    res = handler(lead, params_dict)
                    
                if res: 
                    log.debug(f"Handler response: {res}")
                    return res
                    
            except Exception as e:
                log.error(f"Error calling handler with lead: {lead}: {e}")
                raise HTTPException(status_code=401, detail="Error calling handler")

            if entry.single_use:
                self.handlers.pop(handler_id)
            
            if entry.redirect_url:
                log.debug(f"Redirecting to lead: {lead} to {entry.redirect_url}")
                return RedirectResponse(url=entry.redirect_url)
            
            
            return {
                "status": "ok"
            }
        
        except Exception as e:
            log.error(f"Error processing callback: {e}")
            raise HTTPException(status_code=401, detail="Error processing callback")

    

    def setup(self, ctx: MessageGatewayContext):
        log.debug("Setting up Http Callback Manager")
        self.external_url = ctx.webhook_url
        app = ctx.app

        if self.http_verb.upper() == "GET":
            app.get("/" + self.endpoint + "/{token}")(self._handle_callback)
            
        if self.http_verb.upper() == "POST":
            app.post("/" + self.endpoint + "/{token}")(self._handle_callback)



    def create_callback(self, lead: ConversationLead, handler: callable, ttl: int = 180, redirect_url: str = None, single_use: bool = True):
        """ Create a callback link for a lead """
        
        assert isinstance(lead, ConversationLead), "Lead must be a ConversationLead object"
        assert self.external_url, "External URL must be set"
        
        callback_id = id(handler)
        data = {
            "lead": ConversationLead.serialize(lead),
            "handler_id": callback_id
        }
    
        link = generate_link(
            base_url=self.external_url + "/" + self.endpoint,
            secret_key=self.secret_key,
            encryption_key=self.encryption_key,
            data=data,
            ttl=ttl
        )
        
        self.handlers[callback_id] = CallbackEntry(
            redirect_url=redirect_url,
            handler=handler,
            single_use=single_use
        )
        
        log.debug(f"Generated link: {link}")
        return link
