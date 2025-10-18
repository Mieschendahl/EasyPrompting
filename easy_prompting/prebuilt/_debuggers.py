from functools import partial
from typing import Any, Callable, Optional, override
from easy_prompting._debugger import Debugger
from easy_prompting._message import Role
from easy_prompting._prompter import Prompter
from easy_prompting._utils import pad_text

class PrintDebugger(Debugger):
    def __init__(self, printer: Optional[Callable[[str], Any]] = None, role: Role = "user"):
        self._printer = partial(print, end="", flush=True) if printer is None else printer
        self._role: Role = role

    @override
    def debug(self, prompter: Prompter) -> None:
        try:
            self._printer(f"Input(role={self._role!r}, continue={"↵"!r}, exit={"Ctrl+c"!r}):\n{pad_text("")}")
            content = input()
            self._printer("\n")
            if content != "":
                prompter.add_message(content, self._role)
        except (KeyboardInterrupt, EOFError):
            self._printer(" User aborted\n")
            exit(0)