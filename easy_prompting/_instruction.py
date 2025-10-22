from abc import ABC, abstractmethod
from typing import Any, Optional

class ExtractionError(Exception):
    pass

class Instruction(ABC):
    @abstractmethod
    def describe(self) -> str:
        pass

    @abstractmethod
    def extract(self, data: str) -> Any:
        pass
    
    def get_stop(self) -> Optional[str]:
        return None