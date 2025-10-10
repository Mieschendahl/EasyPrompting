from pathlib import Path
from typing import Any, Callable, Optional, override

from easy_prompting._message import Message, roles, Role
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
    
    def set_padding(self, padding: str = "  ") -> None:
        self._padding = padding
    
    def get_padding(self) -> str:
        return self._padding

    @override
    def _log(self, message: Message, idx: Optional[int] = None, tag: Optional[str] = None) -> None:
        print(message_to_str(message, idx, tag, self._padding), end="\n\n", flush=True)

    @override
    def close(self) -> None:
        pass

class LogFunc(LogPrint):
    def __init__(self, func: Callable[[str], Any]):
        super().__init__()
        self.set_func(func)
    
    def set_func(self, func: Callable[[str], Any]) -> None:
        self._func = func
    
    def get_func(self) -> Callable[[str], Any]:
        return self._func
    
    @override
    def _log(self, message: Message, idx: Optional[int] = None, tag: Optional[str] = None) -> None:
        self._func(message_to_str(message, idx, tag, self._padding))

class LogFile(LogPrint):
    def __init__(self, file_path: str | Path):
        super().__init__()
        self.set_file_path(file_path)
    
    def set_file_path(self, file_path: str | Path) -> None:
        self._file_path = Path(file_path)
        create_dir(self._file_path.parent)
        self._file = self._file_path.open("w", encoding="utf-8")
    
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
    
    def set_loggers(self, *loggers: Logger) -> None:
        self._loggers = list(loggers)
    
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
        self.set_crop()
        self._delayed_crops: dict[int, Optional[int]] = {}
    
    def set_logger(self, logger: Logger) -> None:
        self._logger = logger

    def get_logger(self) -> Logger:
        return self._logger

    def set_crop(self, limit: Optional[int] = None, role: Optional[Role] = None) -> None:
        if role is None:
            self._limits = {role: limit for role in roles}
        else:
            self._limits[role] = limit

    def get_crop(self) -> dict[str, Optional[int]]:
        return self._limits

    @override
    def _log(self, message: Message, idx: Optional[int] = None, tag: Optional[str] = None) -> None:
        limit = self._limits[message.get_role()]
        if limit is not None:
            lines = message.get_content().split("\n")
            if len(lines) > limit:
                lines, cropped = lines[:limit], lines[limit:]
                lines.append(f"...{len(cropped)} line(s) cropped")
            message = Message("\n".join(lines), message.get_role())
        self._logger.log(message, idx, tag)

    @override
    def close(self) -> None:
        self._logger.close()