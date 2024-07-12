import json
from abc import ABC
from .component import Component
from .utils import del_none


#    {
#         "type": "image",
#         "image": {
#           "link": "http(s)://the-url",
#           # provider is an optional parameter
#           "provider": {
#             "name" : "provider-name"
#           },
#         }
#     }


class Image(Component):
    def __init__(self, link: str, provider: str | None = None) -> None:
        self.link = link
        self.provider = provider

    def __str__(self):
        image = {
            "type": "image",
            "image": {
                "link": self.link,
                "provider": {"name": self.provider} if self.provider else None
            }
        }
        del_none(image)
        return json.dumps(image)



    def __repr__(self):
        return f"ImageComponent(link={self.link}, provider={self.provider})"


    def __eq__(self, other):
        return self.link == other.link and self.provider == other.provider
    
    
if __name__ == '__main__':
    image = Image("http(s)://the-url", "provider-name")
    print(image)
    image = Image("http(s)://the-url")
    print(image)    
    # Expected output: '{"type": "image", "image": {"link": "http(s)://the-url", "provider": {"name": "provider-name"}}}