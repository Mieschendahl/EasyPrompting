from abc import ABC, abstractmethod
from typing import TYPE_CHECKING
if TYPE_CHECKING: from easy_prompting._prompter import Prompter

class Interaction(ABC):
    @abstractmethod
    def interact(self, prompter: "Prompter"):
        pass