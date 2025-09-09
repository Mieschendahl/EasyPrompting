import io
from pathlib import Path
from typing import Any, Optional, TextIO

from easy_prompting._instruction import IList, IItem
from easy_prompting._utils import load_text, If, save_text, hash_str, pad_text, wrap_text
from easy_prompting._llm import LLM
from easy_prompting._message import Message

class PromptingError(Exception):
    pass

class Prompter:
    def __init__(self, llm: LLM) -> None:
        self.set_llm(llm)\
            .set_tag()\
            .set_messages()\
            .set_cache_path()\
            .set_loggers()\
            .set_interaction()

    def set_llm(self, llm: LLM) -> "Prompter":
        self.llm = llm
        return self
    
    def get_llm(self) -> LLM:
        return self.llm

    def set_tag(self, id: Optional[str] = None) -> "Prompter":
        self.id = id
        return self
    
    def get_tag(self) -> Optional[str]:
        return self.id
    
    def set_messages(self, messages: Optional[list[Message]] = None) -> "Prompter":
        self.messages = [] if messages is None else messages
        return self
    
    def get_messages(self) -> list[Message]:
        return self.messages
    
    def set_cache_path(self, cache_path: Optional[str | Path] = None) -> "Prompter":
        self.cache_path = None if cache_path is None else Path(cache_path)
        return self
        
    def get_cache_path(self) -> Optional[Path]:
        return self.cache_path

    def set_loggers(self, *logger: Optional[TextIO | io.TextIOBase]) -> "Prompter":
        self.loggers = logger
        return self
    
    def get_loggers(self) -> tuple[Optional[TextIO | io.TextIOBase], ...]:
        return self.loggers

    def set_interaction(self, interaction_role: Optional[str] = None) -> "Prompter":
        self.interaction_role = interaction_role
        return self
    
    def get_interaction(self) -> Optional[str]:
        return self.interaction_role
    
    def get_copy(self) -> "Prompter":
        return Prompter(self.get_llm())\
            .set_tag()\
            .set_messages(self.get_messages().copy())\
            .set_cache_path(self.get_cache_path())\
            .set_loggers(*self.get_loggers())\
            .set_interaction(self.get_interaction())
    
    def add_log(self, text) -> "Prompter":
        for logger in self.loggers:
            print(text, end="\n\n", file=logger, flush=True)
        return self

    def add_message(self, content: str, role: str = "user") -> "Prompter":
        message = Message(content, role)
        self.messages.append(message)

        self.add_log(
            f"{message.role.upper()} "
            +
            If(self.id is not None, f"({self.id}) ")
            +
            f"({len(self.messages)-1}):\n{pad_text(message.content, "| ")}"
        )

        return self

    def interact(self) -> "Prompter":
        if self.interaction_role is not None:
            content = input(f"{self.interaction_role.upper()} (↵: next, x: exit): ")
            print()
            if content == "x":
                exit(0)
            if content != "":
                self.add_message(content, self.interaction_role)
        return self
                
    def add_completion(self, stop: Optional[str] = None) -> "Prompter":
        self.interact()

        if self.cache_path is None:
            completion = self.llm.get_completion(self.messages, stop)
        else:
            file_path = self.cache_path / hash_str("\n\n".join(repr(message) for message in self.messages))
            completion = load_text(file_path)
            if completion is None:
                completion = self.llm.get_completion(self.messages, stop)
                save_text(file_path, completion)

        if stop is not None:
            completion += stop
        self.add_message(completion, role="assistant")

        # self.interact()
        return self
    
    def get_data(self, ilist: IList, role: str = "user") -> Any:
        items = ilist.items + [IItem(IList.stop)]
        ilist = IList(ilist.context, *items)
        self.add_message(ilist.describe(), role=role)
        self.add_completion(wrap_text(IList.stop))
        completion = self.messages[-1].content
        return ilist.extract(completion)[:-1]