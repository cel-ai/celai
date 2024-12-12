import json
from abc import ABC

class ConversationPeer(ABC):
    
    def __init__(self, name: str, metadata: dict = None, id: str = None, phone: str = None, avatarUrl: str = None, email: str = None):
        self.name = name
        self.metadata = metadata
        self.id = id
        self.phone = phone
        self.avatarUrl = avatarUrl
        self.email = email
        
    def to_dict(self):
        return {
            'name': self.name,
            'metadata': self.metadata,
            'id': self.id,
            'phone': self.phone,
            'avatarUrl': self.avatarUrl,
            'email': self.email
        }
        
    def to_json(self):
        return json.dumps(self.to_dict())
    
    def __str__(self):
        return f"ConversationPeer: {self.name}"
    
    @classmethod
    def from_dict(cls, peer_dict):
        return ConversationPeer(
            name=peer_dict.get("name"),
            metadata=peer_dict.get("metadata"),
            id=peer_dict.get("id"),
            phone=peer_dict.get("phone"),
            avatarUrl=peer_dict.get("avatarUrl"),
            email=peer_dict.get("email")
        )

class ConversationPeerEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ConversationPeer):
            return obj.to_dict()
        return super().default(obj)


# if __name__ == "__main__":
#     peer = ConversationPeer(name="John Doe")
    
#     obj = {
#         "id": 1,
#         "peer": peer
#     }

#     # json.dumps(obj)

#     json_str = json.dumps(obj, cls=ConversationPeerEncoder)
#     print(json_str)
    