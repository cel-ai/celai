
from abc import ABC
from dataclasses import dataclass


@dataclass
class Param(ABC):
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
    text: str = None
    image: str = None
    audio: str = None
    video: str = None
    disable_ai_response: bool = False
    blend: bool = False
    is_private: bool = False
