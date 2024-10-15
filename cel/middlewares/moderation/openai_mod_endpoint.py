from abc import ABC
import asyncio
import threading
import time
from typing import Callable
from openai import OpenAI
from openai.types.moderation import Moderation
from cel.assistants.base_assistant import BaseAssistant
from cel.gateway.model.base_connector import BaseConnector
from cel.gateway.model.message import Message
from loguru import logger as log
from dataclasses import dataclass

from cel.middlewares.moderation.moderation_events import ModMiddlewareEvents

@dataclass
class RedFlagEntry(ABC):
    count: int = 0
    updated_at: int = 0
    

class OpenAIEndpointModerationMiddleware():
    """ OpenAIEndpointModerationMiddleware is a middleware that uses OpenAI API to moderate messages.
    It uses the OpenAI API to moderate messages and flags them if they are inappropriate.
    The middleware bubbles up the flagged messages to further processing using the `on_message_flagged` event.
    
    Events:
     - on_message_flagged: Event that is triggered when a message is flagged by the OpenAI API.
     
    Args:
        - custom_evaluation_function: A custom function that accepts a message and returns a Moderation object.
        - on_mod_fail_continue: A boolean that determines if the middleware should continue processing if the moderation fails.
        - expire_after: An integer that determines the time in seconds after which the user flags should be reset.
        
        For more info follow https://platform.openai.com/docs/guides/moderation
    """
    
    def __init__(self,
                 custom_evaluation_function: Callable[[str], Moderation] = None,
                 enable_expiration: bool = False,
                 expire_after: int = 86400,
                 prunning_interval: int = 60,
                 on_mod_fail_continue: bool = True):
        
        self.custom_evaluation_function = custom_evaluation_function
        self.on_mod_fail_continue = on_mod_fail_continue
        self.client = OpenAI()
        self.user_flags = {}
        self.expire_after = expire_after
        self.prunning_interval = prunning_interval
        
        
        if enable_expiration:
            # Asegúrate de que el bucle de eventos esté corriendo
            self.loop = asyncio.get_event_loop()
            if not self.loop.is_running():
                threading.Thread(target=self._start_event_loop, daemon=True).start()
            
            # Inicia la coroutine en segundo plano
            self.loop.call_soon_threadsafe(asyncio.create_task, self.reset_user_flags_loop()) 
                           
        
    def _start_event_loop(self):
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()
        
        
    async def reset_user_flags_loop(self):
        while True:            
            await asyncio.sleep(self.prunning_interval)
            log.debug(f"OpenAIEndpointModerationMiddleware: Prunning user flags each {self.prunning_interval} seconds")
            current_time = time.time()
            expired_sessions = [
                session_id for session_id, flags in self.user_flags.items()
                if current_time - flags.updated_at > self.expire_after
            ]

            for session_id in expired_sessions:
                self.reset_user_flags(session_id)
        

    async def __call__(self, message: Message, connector: BaseConnector, assistant: BaseAssistant):
        
        try:
            text = message.text
            log.debug(f"OpenAIEndpointModerationMiddleware: {text}")
            
            moderation = self.client.moderations.create(input=text)
            result = moderation.results[0]
            assert isinstance(result, Moderation)
            
            log.debug(f"OpenAIEndpointModerationMiddleware: {text} -> {result.flagged}")
            
            custom_flagged = False
            if self.custom_evaluation_function:
                custom_flagged = self.custom_evaluation_function(result)
            
            if result.flagged or custom_flagged:
                session_id = message.lead.get_session_id()
                count = await self.__count_flagged(session_id)
                # append to message metadata moderation result, init metadata if not exists
                report = {
                    'flagged': result.flagged,
                    'count': count,
                    custom_flagged: custom_flagged,
                    'results': result
                }
                message.metadata = message.metadata or {}
                message.metadata['moderation'] = report
                
                # (self, event_name: str, lead: ConversationLead, message: Message = None, connector: BaseConnector = None, data: dict= None) -> EventResponse:
                await assistant.call_event(
                    ModMiddlewareEvents.on_message_flagged, 
                    lead=message.lead, 
                    connector=connector,
                    data=report)
                
            return True
            
        except Exception as e:
            log.error(f"OpenAIEndpointModerationMiddleware: {e}")
            if self.on_mod_fail_continue:
                return True
            else:
                return False
            
            
    async def __count_flagged(self, session_id: str):
        if session_id in self.user_flags:
            self.user_flags[session_id].count += 1
        else:
            self.user_flags[session_id] = RedFlagEntry(count=1, updated_at=time.time())
            # self.user_flags[session_id].count = 1
            # self.user_flags[session_id].updated_at = time.time()
            
        return self.user_flags[session_id].count
    
    
    def reset_user_flags(self, session_id: str):
        if session_id in self.user_flags:
            del self.user_flags[session_id]
        return True
    
    
    def get_user_flags(self, session_id: str):
        if session_id in self.user_flags:
            return self.user_flags[session_id]
        return None