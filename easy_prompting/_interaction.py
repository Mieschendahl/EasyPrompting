from abc import ABC, abstractmethod

class Interaction(ABC):
    @abstractmethod
    def interact(self, prompter) -> None:
        pass