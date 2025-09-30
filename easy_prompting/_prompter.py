from pathlib import Path
from typing import Any, Optional, Self

from easy_prompting._instruction import IList, IItem
from easy_prompting._utils import load_text, If, save_text, hash_str, pad_text, wrap_text
from easy_prompting._message import Role, Message
from easy_prompting._llm import LLM
from easy_prompting._logger import Logger

class Prompter:
    def __init__(self, llm: LLM) -> None:
        self.set_llm(llm)\
            .set_tag()\
            .set_messages([])\
            .set_cache_path()\
            .set_logger()\
            .set_interaction(False)

    def set_llm(self, llm: LLM) -> Self:
        self._llm = llm
        return self
    
    def get_llm(self) -> LLM:
        return self._llm

    def set_tag(self, tag: Optional[str] = None) -> Self:
        self._tag = tag
        return self
    
    def get_tag(self) -> Optional[str]:
        return self._tag
    
    def set_messages(self, messages: list[Message]) -> Self:
        self._messages = messages
        return self
    
    def get_messages(self) -> list[Message]:
        return self._messages
    
    def set_cache_path(self, cache_path: Optional[str | Path] = None) -> Self:
        self._cache_path = None if cache_path is None else Path(cache_path)
        return self
        
    def get_cache_path(self) -> Optional[Path]:
        return self._cache_path

    def set_logger(self, logger: Optional[Logger] = None) -> Self:
        self._logger = logger
        return self
    
    def get_logger(self) -> Optional[Logger]:
        return self._logger

    def set_interaction(self, mode: bool, role: Role = "user") -> Self:
        self._interaction_mode: bool = mode
        self._interaction_role: Role = role
        return self
    
    def get_interaction(self) -> tuple[bool, Role]:
        return self._interaction_mode, self._interaction_role
    
    def get_copy(self) -> "Prompter":
        return Prompter(self.get_llm())\
            .set_tag()\
            .set_messages(self.get_messages().copy())\
            .set_cache_path(self.get_cache_path())\
            .set_logger(self.get_logger())\
            .set_interaction(*self.get_interaction())

    def add_message(self, content: str, role: Role = "user") -> Self:
        message = Message(content, role)
        self._messages.append(message)
        if self._logger is not None:
            self._logger.log(
                "Message("
                +
                f"tag={self._tag!r}, role={message._role!r}, id={len(self._messages)-1}):\n{pad_text(message._content, "| ")}"
            )
        return self

    def interact(self) -> Self:
        if self._interaction_mode:
            content = input(f"Injection(x: exit): ")
            print()
            if content == "x":
                exit(0)
            if content != "":
                self.add_message(content, self._interaction_role)
        return self
                
    def add_completion(self, stop: Optional[str] = None) -> Self:
        self.interact()
        if self._cache_path is None:
            completion = self._llm.get_completion(self._messages, stop)
        else:
            file_path = self._cache_path / hash_str("\n\n".join(repr(message) for message in self._messages))
            completion = load_text(file_path)
            if completion is None:
                completion = self._llm.get_completion(self._messages, stop)
                save_text(file_path, completion)
        if stop is not None:
            completion += stop
        self.add_message(completion, role="assistant")
        return self
    
    def get_data(self, ilist: IList, role: Role = "user") -> Any:
        items = ilist._items + [IItem(IList.stop)]
        ilist = IList(ilist._context, *items)
        self.add_message(ilist.describe(), role=role)
        self.add_completion(wrap_text(IList.stop))
        completion = self._messages[-1]._content
        return ilist.extract(completion)[:-1]