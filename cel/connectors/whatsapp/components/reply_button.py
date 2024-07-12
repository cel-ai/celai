from abc import ABC
from .component import Component
import json
from .utils import del_none

class ReplyButton(Component):
    def __init__(self, title: str, id: str = None) -> None:
        self.title = title
        self.id = id or title
        
    def __str__(self):
        button = {
            "type": "reply",
            "reply": {"id": self.id, "title": self.title }
        }
        del_none(button)
        return json.dumps(button)
        
    
    def __repr__(self):
        return f"ReplyButton(id={self.id}, title={self.title})"
        
    
    def __eq__(self, other):
        return self.id == other.id and self.title == other.title


if __name__ == "__main__":
    button = ReplyButton("id", "title")
    print(button)
    # Expected output: '{"type": "reply", "reply": {"id": "id", "title": "title"}}'