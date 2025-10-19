from pathlib import Path
from typing import Any, Optional

from easy_prompting._instruction import ListI, ItemI
from easy_prompting._debugger import Debugger
from easy_prompting._utils import load_text, save_text, hash_str, wrap_text
from easy_prompting._message import Role, Message
from easy_prompting._lm import LM
from easy_prompting._logger import Logger

class Prompter:
    def __init__(self, lm: LM):
        self.set_lm(lm)
        self.set_messages([])
        self.set_logger()
        self.set_debugger()
        self.set_cache()
        self.set_tag()

    def set_lm(self, lm: LM) -> None:
        self._lm = lm
    
    def get_lm(self) -> LM:
        return self._lm

    def set_tag(self, tag: Optional[str] = None) -> None:
        self._tag = tag
    
    def get_tag(self) -> Optional[str]:
        return self._tag
    
    def set_messages(self, messages: list[Message]) -> None:
        self._messages = messages
    
    def get_messages(self) -> list[Message]:
        return self._messages
    
    def set_cache(self, cache_path: Optional[str | Path] = None) -> None:
        self._cache_path = None if cache_path is None else Path(cache_path)
        
    def get_cache(self) -> Optional[Path]:
        return self._cache_path

    def set_logger(self, logger: Optional[Logger] = None) -> None:
        self._logger = logger

    def get_logger(self) -> Optional[Logger]:
        return self._logger
    
    def set_debugger(self, debugger: Optional[Debugger] = None) -> None:
        self._debugger = debugger

    def get_debugger(self) -> Optional[Debugger]:
        return self._debugger
    
    def get_copy(self) -> "Prompter":
        prompter = Prompter(self.get_lm())
        prompter.set_messages(self.get_messages().copy())
        prompter.set_logger(self.get_logger())
        prompter.set_debugger(self.get_debugger())
        prompter.set_cache(self.get_cache())
        prompter.set_tag()
        return prompter

    def add_message(self, content: str, role: Role = "user") -> None:
        message = Message(content, role)
        self._messages.append(message)
        if self._logger is not None:
            self._logger.log(message, len(self._messages)-1, self._tag)

    def add_completion(self, stop: Optional[str] = None) -> None:
        if self._debugger is not None:
            self._debugger.debug(self)
        if self._cache_path is None:
            completion = self._lm.get_completion(self._messages, stop)
        else:
            file_path = self._cache_path / hash_str("\n\n".join(repr(message) for message in self._messages))
            completion = load_text(file_path)
            if completion is None:
                completion = self._lm.get_completion(self._messages, stop)
                save_text(file_path, completion)
        if stop is not None:
            completion += stop
        self.add_message(completion, "assistant")
    
    def get_data(self, ilist: ListI, role: Role = "user") -> Any:
        items = ilist._items + [ItemI(ListI.stop)]
        ilist = ListI(ilist._context, *items)
        self.add_message(ilist.describe(), role)
        self.add_completion(wrap_text(ListI.stop))
        completion = self._messages[-1].get_content()
        return ilist.extract(completion)[:-1]