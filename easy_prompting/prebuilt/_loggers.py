from pathlib import Path
from typing import Optional, Self, override

from easy_prompting._prompter import Logger
from easy_prompting._utils import create_dir

class LogList(Logger):
    def __init__(self, loggers: list[Logger]):
        self._loggers = loggers

    @override
    def log(self, text: str) -> None:
        for logger in self._loggers:
            logger.log(text)

    @override
    def close(self) -> None:
        for logger in self._loggers:
            logger.close()

class LogPrint(Logger):
    def __init__(self):
        self.set_max_lines()

    def set_max_lines(self, max_lines: Optional[int] = None) -> Self:
        self.max_lines = max_lines
        return self

    def get_max_lines(self) -> Optional[int]:
        return self.max_lines

    @override
    def log(self, text: str) -> None:
        lines = text.split("\n")
        num_hidden_lines = 0
        if self.max_lines is not None and len(lines) > self.max_lines:
            num_hidden_lines = len(lines) - self.max_lines
            lines = lines[:self.max_lines]
            lines.append(f"{num_hidden_lines} LINE(S) WERE HIDDEN")
    
        print("\n".join(lines), end="", flush=True)

    @override
    def close(self) -> None:
        pass

class LogFile(Logger):
    def __init__(self, file_path: str | Path):
        self._file_path = Path(file_path)
        create_dir(self._file_path.parent)
        self._file = self._file_path.open("a", buffering=1, encoding="utf-8")
    
    @override
    def log(self, text: str) -> None:
        print(text, end="", file=self._file, flush=True)

    @override
    def close(self) -> None:
        self._file.close()