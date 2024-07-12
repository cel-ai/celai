from abc import ABC
from dataclasses import dataclass, field
import time
from cel.assistants.base_assistant import BaseAssistant
from cel.gateway.model.base_connector import BaseConnector
from cel.gateway.model.message import Message
from loguru import logger as log

@dataclass
class BlackListEntry(ABC):
    reason: str = None
    date: int = field(default_factory=lambda: int(time.time()))


class InMemBlackListMiddleware:
    """Middleware to block users based on a blacklist. The blacklist is stored in memory."""
    
    def __init__(self, black_list: dict[str, BlackListEntry] = None):
        self.black_list = black_list or {}
        
    async def __call__(self, message: Message, connector: BaseConnector, assistant: BaseAssistant):
        assert isinstance(message, Message), "Message must be a Message object"

        id =  message.lead.get_session_id()
        source = message.lead.connector_name
        entry = self.black_list.get(id)
        if entry:
            log.critical(f"User {id} from {source} is blacklisted. Reason: {entry.reason}")
            return False
        else:
            return True
    
    def add_to_black_list(self, id: str, reason: str = None):
        self.black_list[id] = BlackListEntry(reason=reason, date=int(time.time()))
        
    def remove_from_black_list(self, id: str):
        self.black_list.pop(id, None)
        
    def get_entry(self, id: str):
        return self.black_list.get(id)
        
        
    