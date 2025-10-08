from pathlib import Path
from typing import Any, Callable, Optional, Self, override

from easy_prompting._message import Message
from easy_prompting._logger import Logger
from easy_prompting._utils import create_dir, pad_text

def message_to_str(message: Message, idx: Optional[int] = None, tag: Optional[str] = None, padding: str = "  ") -> str:
    return (
        f"Message(tag={tag!r}, role={message.get_role()!r}, idx={idx}):"
        f"\n{pad_text(message.get_content(), padding)}"
    )

class LogPrint(Logger):
    def __init__(self):
        super().__init__()
        self.set_padding()
    
    def set_padding(self, padding: str = "  ") -> Self:
        self._padding = padding
        return self
    
    def get_padding(self) -> str:
        return self._padding

    @override
    def _log(self, message: Message, idx: Optional[int] = None, tag: Optional[str] = None) -> None:
        print(message_to_str(message, idx, tag, self._padding), end="\n\n", flush=True)

    @override
    def close(self) -> None:
        pass

class LogFunc(Logger):
    def __init__(self, func: Callable[[str], Any]):
        super().__init__()
        self.set_func(func)\
            .set_padding()
    
    def set_padding(self, padding: str = "  ") -> Self:
        self._padding = padding
        return self
    
    def get_padding(self) -> str:
        return self._padding
    
    def set_func(self, func: Callable[[str], Any]) -> Self:
        self._func = func
        return self
    
    def get_func(self) -> Callable[[str], Any]:
        return self._func
    
    @override
    def _log(self, message: Message, idx: Optional[int] = None, tag: Optional[str] = None) -> None:
        self._func(message_to_str(message, idx, tag, self._padding))

    @override
    def close(self) -> None:
        pass

class LogFile(Logger):
    def __init__(self, file_path: str | Path):
        super().__init__()
        self.set_file_path(file_path)\
            .set_padding()
    
    def set_padding(self, padding: str = "  ") -> Self:
        self._padding = padding
        return self
    
    def get_padding(self) -> str:
        return self._padding
    
    def set_file_path(self, file_path: str | Path) -> Self:
        self._file_path = Path(file_path)
        create_dir(self._file_path.parent)
        self._file = self._file_path.open("w", encoding="utf-8")
        return self
    
    def get_file_path(self) -> Path:
        return self._file_path

    @override
    def _log(self, message: Message, idx: Optional[int] = None, tag: Optional[str] = None) -> None:
        print(message_to_str(message, idx, tag, self._padding), end="\n\n", file=self._file, flush=True)

    @override
    def close(self) -> None:
        self._file.close()

class LogList(Logger):
    def __init__(self, *loggers: Logger):
        super().__init__()
        self.set_loggers(*loggers)
    
    def set_loggers(self, *loggers: Logger) -> Self:
        self._loggers = list(loggers)
        return self
    
    def get_loggers(self) -> list[Logger]:
        return self._loggers

    @override
    def _log(self, message: Message, idx: Optional[int] = None, tag: Optional[str] = None) -> None:
        for logger in self._loggers:
            logger.log(message, idx, tag)

    @override
    def close(self) -> None:
        for logger in self._loggers:
            logger.close()

class LogReadable(Logger):
    def __init__(self, logger: Logger):
        super().__init__()
        self._limits = {}
        self.set_logger(logger)
    
    def set_logger(self, logger: Logger) -> Self:
        self._logger = logger
        return self

    def get_logger(self) -> Logger:
        return self._logger

    def add_crop(self, limit: int, offset: int = 0) -> Self:
        self._limits[offset] = min(self._limits[offset], limit) if offset in self._limits else limit 
        return self

    @override
    def _log(self, message: Message, idx: Optional[int] = None, tag: Optional[str] = None) -> None:
        # crop message content
        if 0 in self._limits:
            limit = self._limits[0]
            lines = message.get_content().split("\n")
            if len(lines) > limit:
                lines, cropped = lines[:limit], lines[limit:]
                lines.append(f"... ({len(cropped)} line(s) cropped)")
            message = Message("\n".join(lines), message.get_role())
        # update crop settings
        limits = {}
        for offset, limit in self._limits.items():
            if offset > 0:
                limits[offset-1] = limit
        self._limits = limits
        # pass cropped message to logger
        self._logger.log(message, idx, tag)

    @override
    def close(self) -> None:
        self._logger.close()