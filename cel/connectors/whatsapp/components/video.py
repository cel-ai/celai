#   {
#     "type": "video",
#     "video": {
#       "link": "the-provider-name/protocol://the-url"
#       # provider is an optional parameter
#       "provider": {
#         "name" : "provider-name"
#       }
#     }
#   }

from .component import Component
from .utils import del_none
import json


class Video(Component):
    def __init__(self, link: str, provider: str | None = None) -> None:
        self.link = link
        self.provider = provider

    def __str__(self):
        video = {
            "type": "video",
            "video": {
                "link": self.link,
                "provider": {"name": self.provider} if self.provider else None
            }
        }
        del_none(video)
        return json.dumps(video)

    def __repr__(self):
        return f"VideoComponent(link={self.link}, provider={self.provider})"

    def __eq__(self, other):
        return self.link == other.link and self.provider == other.provider
    
    
    
    
    
if __name__ == "__main__":
    video = Video("the-provider-name/protocol://the-url", "provider-name")
    print(video)
    # Expected output: '{"type": "video", "video": {"link": "the-provider-name/protocol://the-url", "provider": {"name": "provider-name"}}}
    video = Video("the-provider-name/protocol://the-url")
    print(video)    
    # Expected output: '{"type": "video", "video": {"link": "the-provider-name/protocol://the-url", "provider": null}}'