from abc import ABC, abstractmethod
from typing import List, Optional

from easy_prompting._message import Message

class LMError(Exception):
    pass

class LM(ABC):
    @abstractmethod
    def get_completion(self, messages: List[Message], stop: Optional[str] = None) -> str:
        pass