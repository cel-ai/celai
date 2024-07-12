#   {
#     "type": "document",
#     "document": {
#       "id": "your-media-id",
#       # filename is an optional parameter
#       "filename": "your-document-filename"
#     }
#   }
from abc import ABC
import json
from .component import Component
from .utils import del_none

class Document(Component):
    def __init__(self, id: str, filename: str | None = None) -> None:
        self.id = id
        self.filename = filename

    def __str__(self):
        document = {
            "type": "document",
            "document": {
                "id": self.id,
                "filename": self.filename
            }
        }
        del_none(document)
        return json.dumps(document)

    def __repr__(self):
        return f"DocumentComponent(id={self.id}, filename={self.filename})"

    def __eq__(self, other):
        return self.id == other.id and self.filename == other.filename
    
    
if __name__ == "__main__":
    document = Document("your-media-id", "your-document-filename")
    print(document)
    # Expected output: '{"type": "document", "document": {"id": "your-media-id", "filename": "your-document-filename"}}'
    document = Document("your-media-id")
    print(document)    
    # Expected output: '{"type": "document", "document": {"id": "your-media-id", "filename": null}}'