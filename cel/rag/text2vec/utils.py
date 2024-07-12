from abc import ABC, abstractmethod
from typing import Sequence, Union
import numpy as np


Embedding = Union[Sequence[float], Sequence[int]]
Embeddings = Sequence[Embedding]



class Text2VectorProvider(ABC):

    @abstractmethod    
    def text2vec(self, text: str) -> Embedding:
        pass

    @abstractmethod
    def texts2vec(self, texts: list[str]) -> Embeddings:
        pass