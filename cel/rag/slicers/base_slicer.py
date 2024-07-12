from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path



#  A Slice has a text, metadata: dict, and a id: str, source: str
@dataclass
class Slice(ABC):
    """
    A class used to represent a Slice.

    Attributes
    ----------
    id : str
        unique identifier for the slice
    text : str
        text content of the slice
    metadata : dict
        additional information about the slice
    source : str
        source from which the slice was derived
    """
    id: str
    text: str
    metadata: dict
    source: str    
    
    

class Slicer(ABC):
        
    @abstractmethod
    def slice(self) -> list[Slice]:
        pass
    
    
