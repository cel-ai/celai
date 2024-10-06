
from abc import ABC
from dataclasses import dataclass


@dataclass
class Param(ABC):
    """ Tool/Function parameter definition, mind that the enum and required 
    fields may not be present in models other than the OpenAI. """
    name: str
    type: str
    description: str
    required: bool = True
    enum: list[str] = None

@dataclass
class FunctionDefinition(ABC):
    name: str
    description: str
    parameters: list[Param]

@dataclass
class EventResponse(ABC):
    # text: str = None
    # image: str = None
    # audio: str = None
    # video: str = None
    disable_ai_response: bool = False
    # blend: bool = False
    # is_private: bool = False
    # append_to_history: bool = True
