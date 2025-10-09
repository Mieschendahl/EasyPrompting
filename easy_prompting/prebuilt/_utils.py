from functools import partial
from typing import Any, Callable, Optional

from easy_prompting._message import Role
from easy_prompting._prompter import Prompter
from easy_prompting._utils import scope_text

def list_text(*texts: Optional[str], add_scope: bool = False) -> str:
    text_out = "\n".join(f"- {text}" for text in texts if text is not None)
    if add_scope:
        return scope_text(text_out)
    return text_out

def extract_code(code: str) -> str:
    lines = code.split("\n")
    new_lines = []
    start = None
    for i, line in enumerate(lines):
        if line.startswith("```"):
            if start is not None:
                return "\n".join(lines[start+1:i]).strip()
            start = i
        else:
            new_lines.append(lines)
    return "\n".join(new_lines).strip()

def delimit_code(text: str, keyword: str = "") -> str:
    return f"```{keyword}\n{text}\n```"

def create_interceptor(printer: Optional[Callable[[str], Any]] = None, role: Role = "user") -> Callable[[Prompter], Any]:
    if printer is None:
        printer = partial(print, end="", flush=True)
    def interceptor(prompter: Prompter) -> None:
        try:
            printer(f"Input(role={role!r}, continue={"↵"!r}, exit={"Ctrl+C"!r}): ")
            content = input()
            printer("\n")
            if content != "":
                prompter.add_message(content, role)
        except (KeyboardInterrupt, EOFError):
            printer(" User aborted\n")
            exit(0)
    return interceptor