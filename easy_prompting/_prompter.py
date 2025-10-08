from pathlib import Path
from typing import Any, Callable, Optional, Self

from easy_prompting._instruction import IList, IItem
from easy_prompting._utils import load_text, save_text, hash_str, wrap_text
from easy_prompting._message import Role, Message
from easy_prompting._llm import LLM
from easy_prompting._logger import Logger

class Prompter:
    def __init__(self, llm: LLM) -> None:
        self.set_llm(llm)\
            .set_tag()\
            .set_messages([])\
            .set_cache_path()\
            .set_logger()

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
    
    def get_copy(self) -> "Prompter":
        return Prompter(self.get_llm())\
            .set_tag()\
            .set_messages(self.get_messages().copy())\
            .set_cache_path(self.get_cache_path())\
            .set_logger(self.get_logger())

    def add_message(self, content: str, role: Role = "user") -> Self:
        message = Message(content, role)
        self._messages.append(message)
        if self._logger is not None:
            self._logger.log(message, len(self._messages)-1, self._tag)
        return self

    def add_completion(self, stop: Optional[str] = None, interceptor: Optional[Callable[[Self], Any]] = None) -> Self:
        if interceptor is not None:
            interceptor(self)
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
        self.add_message(completion, "assistant")
        return self
    
    def get_data(self, ilist: IList, role: Role = "user", interceptor: Optional[Callable[[Self], Any]] = None) -> Any:
        items = ilist._items + [IItem(IList.stop)]
        ilist = IList(ilist._context, *items)
        self.add_message(ilist.describe(), role)
        self.add_completion(wrap_text(IList.stop), interceptor)
        completion = self._messages[-1].get_content()
        return ilist.extract(completion)[:-1]