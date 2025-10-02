from pathlib import Path
from typing import Any, Callable, Optional, Self, override

from easy_prompting._prompter import Logger
from easy_prompting._utils import create_dir

class LogPrint(Logger):
    def __init__(self):
        super().__init__()

    @override
    def _log(self, text: str) -> None:
        print(text, end="\n\n", flush=True)

    @override
    def close(self) -> None:
        pass

class LogFunc(Logger):
    def __init__(self, func: Callable[[str], Any]):
        super().__init__()
        self.set_func(func)
    
    def set_func(self, func: Callable[[str], Any]) -> Self:
        self._func = func
        return self
    
    def get_func(self) -> Callable[[str], Any]:
        return self._func
    
    @override
    def _log(self, text: str) -> None:
        self._func(text)

    @override
    def close(self) -> None:
        pass

class LogFile(Logger):
    def __init__(self, file_path: str | Path):
        super().__init__()
        self.set_file_path(file_path)
    
    def set_file_path(self, file_path: str | Path) -> Self:
        self._file_path = Path(file_path)
        create_dir(self._file_path.parent)
        self._file = self._file_path.open("w", encoding="utf-8")
        return self
    
    def get_file_path(self) -> Path:
        return self._file_path

    @override
    def _log(self, text: str) -> None:
        print(text, end="\n\n", file=self._file, flush=True)

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
    def _log(self, text: str) -> None:
        for logger in self._loggers:
            logger.log(text)

    @override
    def close(self) -> None:
        for logger in self._loggers:
            logger.close()

class LogReadable(Logger):
    def __init__(self, logger: Logger):
        super().__init__()
        self.set_logger(logger)\
            .set_vertical_crop()\
            .set_horizontal_crop()
    
    def set_logger(self, logger: Logger) -> Self:
        self._logger = logger
        return self

    def get_logger(self) -> Logger:
        return self._logger

    def set_vertical_crop(self, limit: Optional[int] = None) -> Self:
        self._vertical_limit = limit
        return self

    def get_vertical_crop(self) -> Optional[int]:
        return self._vertical_limit
    
    def set_horizontal_crop(self, limit: Optional[int] = None) -> Self:
        self._horizontal_limit = limit
        return self

    def get_horizontal_crop(self) -> Optional[int]:
        return self._horizontal_limit

    @override
    def _log(self, text: str) -> None:
        lines = text.split("\n")
        if self._vertical_limit is not None:
            cropped_lines = []
            for line in lines:
                if len(line) <= self._vertical_limit:
                    cropped_lines.append(line)
                    continue
                # num_cropped_chars = len(line[self._vertical_limit:])
                cropped_lines.append(line[:self._vertical_limit] + f"...")
            lines = cropped_lines
        if self._horizontal_limit is not None and len(lines) > self._horizontal_limit:
            # num_cropped_lines = len(lines) - self._horizontal_limit
            lines = lines[:self._horizontal_limit]
            lines.append(f"...")
        self._logger.log("\n".join(lines))

    @override
    def close(self) -> None:
        self._logger.close()