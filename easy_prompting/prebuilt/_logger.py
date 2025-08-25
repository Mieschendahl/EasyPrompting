import io
from typing import Optional, TextIO, Tuple

class PrettyLogger(io.TextIOBase):
    """
    A wrapper around a text stream (e.g. sys.stdout) that supports:

    - Line wrapping: long lines are broken into multiple lines,
      continuation lines are prefixed with wrap_char.
    - Line limiting: only a maximum number of lines are written;
      excess lines are summarized.
    """

    def __init__(self, target: TextIO | io.TextIOBase, raw_target: Optional[TextIO | io.TextIOBase] = None):
        self.set_target(target, raw_target)\
            .set_wrap()\
            .set_max_lines()

    def set_target(self, target: TextIO | io.TextIOBase, raw_target: Optional[TextIO | io.TextIOBase] = None) -> "PrettyLogger":
        self.target = target
        self.raw_target = raw_target
        return self

    def get_target(self) -> tuple[TextIO | io.TextIOBase, Optional[TextIO | io.TextIOBase]]:
        return (self.target, self.raw_target)

    def set_wrap(self, width: Optional[int] = None, wrap_char: Optional[str] = None) -> "PrettyLogger":
        self.width = width
        self.wrap_char = wrap_char
        return self

    def get_wrap(self) -> Tuple[Optional[int], Optional[str]]:
        return (self.width, self.wrap_char)

    def set_max_lines(self, n: Optional[int] = None) -> "PrettyLogger":
        self.max_lines = n
        self.line_count = 0
        return self

    def get_max_lines(self) -> Optional[int]:
        return self.max_lines

    def get_copy(self) -> "PrettyLogger":
        return PrettyLogger(*self.get_target())\
            .set_wrap(*self.get_wrap())\
            .set_max_lines(self.get_max_lines())

    def write(self, text: str) -> int:
        """
        Write string with wrapping and line limiting.
        Returns number of characters processed.
        """
        if self.raw_target is not None:
            self.raw_target.write(text)

        raw_lines = text.split("\n")

        # Step 2: wrap each line
        output: list[str] = []
        for line in raw_lines:
            if self.width is None or len(line) <= self.width:
                output.append(line)
            else:
                # break into chunks
                output.append(line[:self.width])
                line = line[self.width:]
                while line:
                    output.append((self.wrap_char or "") + line[:self.width])
                    line = line[self.width:]

        # Step 3: crop if too many lines
        hidden = 0
        if self.max_lines is not None and len(output) > self.max_lines:
            hidden = len(output) - self.max_lines
            output = output[:self.max_lines]
            output.append(f"{hidden} LINE(S) ARE HIDDEN")

        # Step 4: write everything
        self.target.write("\n".join(output))

        # Track how many lines went out
        self.line_count += len(output)
        return len(text)

    def flush(self) -> None:
        """Flush target."""
        if self.raw_target is not None:
            self.raw_target.flush()
        self.target.flush()