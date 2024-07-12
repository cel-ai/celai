""" VAPI Connector
    This connector is used to connect to the VAPI platform.
    It is a dummy connector that will be used to test the streaming capabilities of the platform.
    
    The VAPI platform is a platform that allows the creation of voice assistants.
    
    This connector will use DIRECT stream mode to send messages to the platform. Core events,
    and Middleware events are availables.
    
    Smart Message Enhancer is disabled for this connector. No need to implement it.
    
    Based on: 
    https://github.com/VapiAI/server-side-example-python-flask/blob/main/app/api/custom_llm.py
    
"""

from fastapi.responses import StreamingResponse
from loguru import logger as log
from typing import Any, Callable, Dict
from fastapi import APIRouter, BackgroundTasks, Request, Response
from loguru import logger as log
import shortuuid
import json
from cel.assistants.stream_content_chunk import StreamContentChunk
from cel.connectors.vapi.model.vapi_message import VAPIMessage
from cel.connectors.vapi.utils import create_chunk_response
from cel.gateway.model.base_connector import BaseConnector
from cel.gateway.message_gateway import StreamMode
from cel.gateway.model.message import Message
from cel.connectors.telegram.model.telegram_lead import TelegramLead
from cel.gateway.model.message_gateway_context import MessageGatewayContext
from cel.gateway.model.outgoing import OutgoingMessage





class VAPIConnector(BaseConnector):
    
    endpoint = '/chat/completions'
       
    def __init__(self):
        log.debug("Creating VAPI connector")
        self.prefix = '/vapi'
        self.router = APIRouter(prefix=self.prefix)
        self.paused = False
        # generate shortuuid for security token
        self.__create_routes(self.router)
    

    
    def on_message(self, listener: Callable[[Message, StreamMode], None]):
        self.__on_message = listener

    def __create_routes(self, router: APIRouter):
        
        @router.post(f"{VAPIConnector.endpoint}")
        async def chat_complition(request: Request, background_tasks: BackgroundTasks):
            data = await request.json()
            streaming = data.get('stream', False)
            if streaming:
                log.debug("Streaming response")
                return StreamingResponse(self.__process_stream(data), media_type='text/event-stream')
            
            else:
                #  TODO:
                raise NotImplementedError("Non-streaming response is not implemented yet")
        

            
    async def __process_stream(self, payload: dict):
        try:
            log.debug(f"Received VAPI text for Stream Processing: {payload}")
            
            msg = await VAPIMessage.load_from_message(payload, connector=self)
            
            if self.paused:
                log.debug("Connector VAPI is paused, ignoring message")
                return 
                        
            if self.gateway:
                id = "vapi-" + shortuuid.uuid()
                async for chunk in self.gateway.process_message(msg, mode=StreamMode.DIRECT, capture_repsonse=True):
                    assert isinstance(chunk, StreamContentChunk), "stream chunk must be a StreamContentChunk object"
                    yield f"data: {json.dumps(create_chunk_response(id=id, text=chunk.content))}\n\n"
                
                # end of stream 
                yield f"data: {json.dumps(create_chunk_response(id=id))}\n\n"
                
        except Exception as e:
            log.error(f"Error processing VAPI message: {e}")
                   
    
    async def send_text_message(self, lead: TelegramLead, text: str, metadata: dict = {}, is_partial: bool = True):
        log.warning("send_text_message must be implemented in VAPI connector")


    async def send_select_message(self, 
                                  lead: TelegramLead, 
                                  text: str, 
                                  options: list[str], 
                                  metadata: dict = {}, 
                                  is_partial: bool = True):
        log.warning("send_select_message must be implemented in VAPI connector")

    async def send_link_message(self, 
                                lead: TelegramLead, 
                                text: str, 
                                links: list, 
                                metadata: dict = {}, 
                                is_partial: bool = True):
        log.warning("send_link_message must be implemented in VAPI connector")

        
    async def send_typing_action(self, lead: TelegramLead):
        log.warning("send_typing_action must be implemented in VAPI connector")
        
        
        
    async def send_message(self, message: OutgoingMessage):
        log.warning("send_message must be implemented in VAPI connector")
        
        
        
    def name(self) -> str:
        return "vapi"
    
    def set_gateway(self, gateway):
        from cel.gateway.message_gateway import MessageGateway
        assert isinstance(gateway, MessageGateway), \
            "gateway must be an instance of MessageGateway"
        self.gateway = gateway    
        
    def get_router(self) -> APIRouter:
        return self.router
    
    def startup(self, context: MessageGatewayContext):
        # verify if the webhook_url is set and is HTTPS
        assert context.webhook_url, "webhook_url must be set in the context"
        assert context.webhook_url.startswith("https"),\
            f"webhook_url must be HTTPS, got: {context.webhook_url}.\
            Be sure that your url is public and has a valid SSL certificate."
        
        webhook_url = f"{context.webhook_url}{self.prefix}{VAPIConnector.endpoint}"
        log.debug(f"Starting VAPI connector with url: {webhook_url}")
        log.debug("Be sure to setup this url in the VAPI Assistant, \
            go to Assistant Settings -> Model and select Custom LLM.\
            Then set the url in the Custom LLM URL field")
        

    
    def shutdown(self, context: MessageGatewayContext):
        log.debug("Shutting down VAPI connector")
        
        
    def pause(self):
        log.debug("Pausing VAPI connector")
        self.paused = True
    
    def resume(self):
        log.debug("Resuming VAPI connector")
        self.paused = False
