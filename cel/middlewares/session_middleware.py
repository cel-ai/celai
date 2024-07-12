from abc import ABC
import time
from redis import asyncio as aioredis
import json
from dataclasses import asdict, dataclass
from cel.assistants.base_assistant import BaseAssistant
from cel.gateway.model.base_connector import BaseConnector
from cel.gateway.model.message import Message
from loguru import logger as log

Redis = aioredis.Redis
DEFUALT_MASTER_KEY = "123456"

@dataclass
class AuthEntry(ABC):
    id: str = None
    client_cmd_enabled: bool = False
    last_request: int = 0
    metadata: dict = None

class SessionMiddlewareEvents:
    new_conversation = "new_conversation"
    login = "login"
    logout = "logout"

class SessionMiddleware(ABC):
    """Middleware to secure client commands, session handling and user lyfe cycle related events
    Based on a Redis database.
    
    Triggered events:
        - new_conversation: Event called when a new conversation is started.
        - login: Event called when a user logs in.
        - logout: Event called when a user logs out.
        
    Message extended metadata:
        - time_since_last_request: Time since last request in seconds.
        
    """
    events: SessionMiddlewareEvents = SessionMiddlewareEvents()
    
    def __init__(self, redis: str | Redis = None, key_prefix: str = "authmw", master_key: str = None):
        self.client = redis if isinstance(redis, Redis) else aioredis.from_url(redis or 'redis://localhost:6379/0')
        self.key_prefix = key_prefix
        log.critical("No master key provided. Using default key") if not master_key else None
        self.master_key = master_key or DEFUALT_MASTER_KEY
        
    async def __call__(self, message: Message, connector: BaseConnector, assistant: BaseAssistant):
        assert isinstance(message, Message), "Message must be a Message object"
        assert isinstance(connector, BaseConnector), "Connector must be a BaseConnector object"
        
        entry = await self.get_entry(message.lead.get_session_id())
        
        # add last request time in message
        if entry:
            time_since_last_request = time.time() - (entry.last_request or 0)
            message.metadata = message.metadata or {}
            message.metadata['time_since_last_request'] = time_since_last_request
            await self.set_entry(message.lead.get_session_id(), client_cmd_enabled=entry.client_cmd_enabled, metadata=message.metadata)
        else:
            await self.set_entry(message.lead.get_session_id(), 
                                 client_cmd_enabled=False, 
                                 metadata={})
            await assistant.call_event(self.events.new_conversation, message.lead, message, connector)
            
        if not await self.__handle_login_command(message, connector, entry, assistant):
            return False
        
        if not await self.__secure_client_commands(message, connector, entry):
            return False
        
        return True
        
    
    async def __handle_login_command(self, 
                                     message: Message, 
                                     connector: BaseConnector, 
                                     entry: AuthEntry,
                                     assistant: BaseAssistant):
        text = message.text or ''
        if text.startswith("/logout"):
            await self.clear_auth(message.lead.get_session_id())
            await connector.send_text_message(message.lead, "You have been logged out!")
            await assistant.call_event(self.events.logout,  message.lead, message, connector)
            return False
        
        if text.startswith("/login"):
            parts = text.split(" ")
            if len(parts) == 2:
                if parts[1] == self.master_key:
                    await self.set_entry(message.lead.get_session_id(), client_cmd_enabled=True)
                    await assistant.call_event(self.events.login,  message.lead, message, connector)
                    await connector.send_text_message(message.lead, "You have been logged in.")
                    await connector.send_text_message(message.lead, "Welcome AI bender!")
                    return False
                else:
                    log.critical(f"Invalid master key provided for login")
                    return False
            else:
                log.critical(f"Invalid login command format")
                return False
        return True
        
    async def __secure_client_commands(self, message: Message, connector: BaseConnector, entry: AuthEntry):
        text = message.text or ''
        if text.startswith("/") and not text.startswith("/login") and not text.startswith("/logout"):
            if not entry or not entry.client_cmd_enabled:
                log.critical(f"Client command {text} from {message.lead.get_session_id()} is not allowed")
                return False

            
        if text.startswith("/reset all"):
            # clear entry for this session
            await connector.send_text_message(message.lead, "Resetting session data")
            await self.clear_auth(message.lead.get_session_id())
            
            
            
        return True
    
    async def set_entry(self, id: str, client_cmd_enabled: bool = False, metadata: dict = None):
        entry = AuthEntry(id=id, 
                          client_cmd_enabled=client_cmd_enabled, 
                          metadata=metadata,
                          last_request=time.time()
                        )
        await self.client.hset(self.key_prefix, id, json.dumps(asdict(entry)))
        return entry
        
    async def clear_auth(self, id: str):
        await self.client.hdel(self.key_prefix, id)
        
    async def get_entry(self, id: str):
        entry = await self.client.hget(self.key_prefix, id)
        if entry:
            entry = json.loads(entry)
            return AuthEntry(id=entry.get('id'), 
                            client_cmd_enabled=entry.get('client_cmd_enabled'), 
                            last_request=entry.get('last_request'),
                            metadata=entry.get('metadata'))

        return None