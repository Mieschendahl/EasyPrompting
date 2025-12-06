from abc import ABC, abstractmethod
from typing import Any, Self, Optional

from easy_prompting.message import Message

class Logger(ABC):
    def __init__(self):
        self.set_verbose()
    
    def set_verbose(self, verbose: bool = True) -> None:
        self._verbose = verbose
    
    def get_verbose(self) -> bool:
        return self._verbose
    
    def __enter__(self) -> Self:
        return self
    
    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        self.close()
    
    def log(self, message: Message, idx: Optional[int] = None, tag: Optional[str] = None) -> None:
        if self._verbose:
            self._log(message, idx, tag)

    @abstractmethod
    def _log(self, message: Message, idx: Optional[int] = None, tag: Optional[str] = None) -> None:
        pass

    @abstractmethod
    def close(self) -> None:
        pass