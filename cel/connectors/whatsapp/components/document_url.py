#   {
#     "type": "document",
#     "document": {
#       "link": "the-provider-name/protocol://the-url",
#       # provider and filename are optional parameters
#       "provider": {
#         "name" : "provider-name"
#       },
#       "filename": "your-document-filename"
#     }
#   }
from .component import Component
from .utils import del_none
import json



class DocumentURL(Component):
    def __init__(self, link: str, provider: str | None = None, filename: str | None = None) -> None:
        self.link = link
        self.provider = provider
        self.filename = filename

    def __str__(self):
        document = {
            "type": "document",
            "document": {
                "link": self.link,
                "provider": {"name": self.provider} if self.provider else None,
                "filename": self.filename
            }
        }
        del_none(document)
        return json.dumps(document)

    def __repr__(self):
        return f"DocumentURLComponent(link={self.link}, provider={self.provider}, filename={self.filename})"

    def __eq__(self, other):
        return self.link == other.link and self.provider == other.provider and self.filename == other.filename