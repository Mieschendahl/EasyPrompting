from abc import ABC, abstractmethod
from typing import List, Optional, Any

class LLMError(Exception):
    pass

class LLM(ABC):
    @abstractmethod
    def get_completion(self, messages: List[Any], stop: Optional[str] = None) -> str:
        pass