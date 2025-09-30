from abc import ABC, abstractmethod
from typing import Any, Self

class Logger(ABC):
    @abstractmethod
    def log(self, text: str) -> None:
        pass

    @abstractmethod
    def close(self) -> None:
        pass
    
    def __enter__(self) -> Self:
        return self
    
    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        self.close()