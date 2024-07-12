from dataclasses import dataclass
from typing import Callable


class RequestMode:
    STREAM = "stream"
    SINGLE = "single"


@dataclass
class FunctionResponse:
    text: str

    """ the execution function response will be sent as a stream of chunks or as a single response """
    request_mode: str = RequestMode.SINGLE

    """ If you want to disable direct response from Asiistant AI, use callback to handle the response.
    It is useful when you want to handle the response in a different way, like sending the response to a different service.
    Another use case is when oyu need to use specific platform features to send the response, like interactives messages, buttons, etc.
    """
    callback: Callable = None
    
    