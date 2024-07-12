#  define roles type
from abc import ABC
from dataclasses import dataclass

from cel.assistants.common import FunctionDefinition



class Role:
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"
    FUNCTION = "function"
    
@dataclass
class ContextMessage(ABC):
    role: Role
    content: str
    name: str = None
    function_call: dict = None
    
    
@dataclass
class PromptCompiled:
    prompt: str
    settings: dict
    functions: list[FunctionDefinition]
    context: dict
    
@dataclass
class PromptContext:
    history: list[ContextMessage]
    state: dict
    message: str | None
    date: str


