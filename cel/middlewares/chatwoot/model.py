
from dataclasses import dataclass

ChatwootMessageTypes = ["incoming", "outgoing"]

@dataclass
class ChatwootConversationRef:
    id: int
    identifier: str
    updated_at: int
    
    
@dataclass
class InboxRef:
    id: int
    name: str
    
@dataclass
class ContactLead:
    identifier: str
    name: str = None
    email: str = None
    phone_number: str = None
    
