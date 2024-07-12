from dataclasses import dataclass
from typing import Any


@dataclass
class StreamContentChunk:
    content: str
    is_partial: bool = True


    def __add__(self, other: Any) -> "StreamContentChunk":
        assert isinstance(other, StreamContentChunk),\
            "StreamContentChunk can only be added to another StreamContentChunk"

        return self.__class__(
            content=self.content + other.content,
            is_partial=other.is_partial
        )

    def __str__(self):
        return self.content