from functools import partial
from typing import Any, Callable, override
from easy_prompting._interaction import Interaction
from easy_prompting._message import Role
from easy_prompting._prompter import Prompter

class LoggedInteraction(Interaction):
    def __init__(self, logger: Callable[[str], Any], role: Role = "user") -> None:
        self._logger = logger
        self._role: Role = role

    @override
    def interact(self, prompter: Prompter) -> None:
        try:
            self._logger(f"Input(role={self._role!r}, continue={"↵"!r}, exit={"Ctrl+C"!r}): ")
            content = input()
            self._logger("\n")
            if content != "":
                prompter.add_message(content, self._role)
        except (KeyboardInterrupt, EOFError):
            self._logger(" User aborted\n")
            exit(0)

class PrintInteraction(LoggedInteraction):
    @override
    def __init__(self, role: Role = "user") -> None:
        super().__init__(partial(print, end="", flush=True), role)