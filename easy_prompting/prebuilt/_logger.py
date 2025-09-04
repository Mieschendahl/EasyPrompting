import io
from typing import Optional, TextIO

class FormatLogger(io.TextIOBase):
    def __init__(self, target: TextIO | io.TextIOBase):
        self.set_target(target)\
            .set_max_lines()

    def set_target(self, target: TextIO | io.TextIOBase) -> "FormatLogger":
        self.target = target
        return self

    def get_target(self) -> TextIO | io.TextIOBase:
        return self.target

    def set_max_lines(self, n: Optional[int] = None) -> "FormatLogger":
        self.max_lines = n
        return self

    def get_max_lines(self) -> Optional[int]:
        return self.max_lines

    def get_copy(self) -> "FormatLogger":
        return FormatLogger(self.get_target())\
            .set_max_lines(self.get_max_lines())

    def write(self, text: str) -> int:
        output = text.split("\n")
        hidden = 0
        if self.max_lines is not None and len(output) > self.max_lines:
            hidden = len(output) - self.max_lines
            output = output[:self.max_lines]
            output.append(f"{hidden} LINE(S) WERE HIDDEN")

        self.target.write("\n".join(output))
        return len(text)

    def flush(self) -> None:
        self.target.flush()