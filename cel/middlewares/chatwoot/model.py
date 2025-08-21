
from dataclasses import dataclass

ChatwootMessageTypes = ["incoming", "outgoing"]

@dataclass
class ChatwootConversationRef:
    id: int
    identifier: str
    updated_at: int
    assigned: bool = False
    
    
@dataclass
class InboxRef:
    id: int
    name: str
    
@dataclass
class ContactLead:
    identifier: str
    celai_lead: str
    name: str = None
    email: str = None
    phone_number: str = None
    
    
