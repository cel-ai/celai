from abc import ABC, abstractmethod


class Component(ABC):
    @abstractmethod
    def __str__(self):
        pass