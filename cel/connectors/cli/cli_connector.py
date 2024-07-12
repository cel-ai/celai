import threading
import time
from loguru import logger as log
from fastapi import APIRouter
from loguru import logger as log
import json
from cel.comms.utils import async_run
from cel.connectors.cli.model.cli_lead import CliLead
from cel.connectors.cli.model.cli_message import CliMessage
from cel.gateway.model.base_connector import BaseConnector
from cel.gateway.message_gateway import StreamMode
from cel.gateway.model.message_gateway_context import MessageGatewayContext
from cel.gateway.model.outgoing import OutgoingMessage,\
                                            OutgoingMessageType,\
                                            OutgoingLinkMessage,\
                                            OutgoingSelectMessage,\
                                            OutgoingTextMessage



class CliConnector(BaseConnector):
       
    def __init__(self, stream_mode: StreamMode = StreamMode.SENTENCE):
        log.debug("Creating CLI connector")
        self.router = APIRouter(prefix="/cli")
        self.paused = False
        self.stream_mode = stream_mode

    def cli_listener(self):
        time.sleep(2)
        print("CLI Connector started")
        print("Type 'exit' to stop the connector")
        while True:
            command = input("User: ")
            
            if command == "exit":
                print("Exiting CLI Connector")
                exit()
            
            async_run(self.__process_message(command))
            
            
            

    async def __process_message(self, payload: str):
        try:
            log.debug("Received Cli Message")
            log.debug(payload)
            msg = await CliMessage.load_from_message(payload, connector=self)
            
            if self.paused:
                log.warning("Connector is paused, ignoring message")
                return 
            if self.gateway:
                async for m in self.gateway.process_message(msg, mode=self.stream_mode):
                    pass
            else:
                log.critical("Gateway not set in CLI Connector")
                raise Exception("Gateway not set in CLI Connector")
                
        except Exception as e:
            # TODO: TEST!
            log.error(f"Error processing CLI message: {e}")
                   
    
    async def send_text_message(self, lead: CliLead, text: str, metadata: dict = {}, is_partial: bool = True):
        """ Send a text message to the lead. The simplest way to send a message to the lead.
        
        Args:
            - lead[CliLead]: The lead to send the message
            - text[str]: The text to send
            - metadata[dict]: Metadata to send with the message
            - is_partial[bool]: If the message is partial or not
        """        
        # log.debug(f"Sending message to chat_id: {lead.chat_id}, text: {text}, is_partial: {is_partial}")
        # await self.bot.send_message(chat_id=lead.chat_id, text=text)
        print(f"Bot: {text}")     


    async def send_select_message(self, 
                                  lead: CliLead, 
                                  text: str, 
                                  options: list[str], 
                                  metadata: dict = {}, 
                                  is_partial: bool = True):
        print(f"Bot: {text}")


    async def send_link_message(self, 
                                lead: CliLead, 
                                text: str, 
                                links: list, 
                                metadata: dict = {}, 
                                is_partial: bool = True):
        print(f"Bot: {text}")
        
        
    async def send_typing_action(self, lead: CliLead):
        log.warning(f"Sending typing action to CLI is not implemented yet")
        
        
        
        
    async def send_message(self, message: OutgoingMessage):
        assert isinstance(message, OutgoingMessage),\
            "message must be an instance of OutgoingMessage"
        assert isinstance(message.lead, CliLead),\
            "lead must be an instance of CliLead"
        lead = message.lead
        
        if message.type == OutgoingMessageType.TEXT:
            assert isinstance(message, OutgoingTextMessage),\
            "message must be an instance of OutgoingMessage"
            await self.send_text_message(lead, 
                                         message.content, 
                                         metadata=message.metadata, 
                                         is_partial=message.is_partial)
            
        if message.type == OutgoingMessageType.SELECT:
            assert isinstance(message, OutgoingSelectMessage),\
            "message must be an instance of OutgoingSelectMessage"
            
            await self.send_select_message(lead, 
                                           message.content, 
                                           options=message.options, 
                                           metadata=message.metadata, 
                                           is_partial=message.is_partial)

        if message.type == OutgoingMessageType.LINK:
            assert isinstance(message, OutgoingLinkMessage),\
            "message must be an instance of OutgoingLinkMessage"
            
            await self.send_link_message(lead, 
                                           message.content, 
                                           url=message.links, 
                                           metadata=message.metadata, 
                                           is_partial=message.is_partial)
        
        
        
    def name(self) -> str:
        return "telegram"
        
    def get_router(self) -> APIRouter:
        return self.router
    
    def set_gateway(self, gateway):
        from cel.gateway.message_gateway import MessageGateway
        assert isinstance(gateway, MessageGateway), \
            "gateway must be an instance of MessageGateway"
        self.gateway = gateway
    
    def startup(self, context: MessageGatewayContext):
        log.debug("Starting CLI Connector")
        self.command_thread = threading.Thread(target=self.cli_listener, daemon=True)
        self.command_thread.daemon = True
        self.command_thread.start()
    
    def shutdown(self, context: MessageGatewayContext):
        log.debug("Shutting down telegram connector")
        # async_run(self.bot.delete_webhook(), then=lambda r: log.debug(f'Webhook deleted: {r}'))
        
    def pause(self):
        log.debug("Pausing telegram connector")
        self.paused = True
    
    def resume(self):
        log.debug("Resuming telegram connector")
        self.paused = False
