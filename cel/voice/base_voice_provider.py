from abc import ABC, abstractmethod
from typing import Any

class BaseVoiceProvider(ABC):
    
    @abstractmethod
    def TTS(self, text: str, voice: str = None, settings: Any = None):
        raise NotImplementedError
    
    @abstractmethod
    def STT(self, audio: bytes | str) -> str:
        raise NotImplementedError