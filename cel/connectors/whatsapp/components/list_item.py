from abc import ABC
from .component import Component
import json
from .utils import del_none

class ListItem(Component):
    def __init__(self, title: str, id: str = None, description: str = None) -> None:
        self.title = title
        self.id = id or title
        self.description = description
        
    def __str__(self):
        item = {
            "id": self.id, 
            "title": self.title, 
            "description": self.description
        }
        del_none(item)
        return json.dumps(item)
        
    
    def __repr__(self):
        return f"ListItem(id={self.id}, title={self.title})"
        
    
    def __eq__(self, other):
        return self.id == other.id and self.title == other.title


if __name__ == "__main__":
    item = ListItem("id", "title")
    print(item)
