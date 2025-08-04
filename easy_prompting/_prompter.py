from pathlib import Path
from easy_prompting._utils import load_text, save_text, hash_str
from easy_prompting._llm import LLM
from easy_prompting._message import Message
from easy_prompting._option import Option
from typing import Optional, List, Dict, TextIO, Tuple

class ChoiceError(Exception):
    pass

class SummaryError(Exception):
    pass

class Prompter:
    def __init__(self, llm: LLM) -> None:
        self.set_llm(llm)\
            .set_messages()\
            .set_cache_path()\
            .set_logger()\
            .set_interaction()\
            .set_summary()

    def set_llm(self, llm: LLM) -> 'Prompter':
        self.llm = llm
        return self
    
    def get_llm(self) -> LLM:
        return self.llm
    
    def set_messages(self, messages: Optional[List[Message]] = None) -> 'Prompter':
        self.messages = [] if messages is None else messages
        return self
    
    def get_messages(self) -> List[Message]:
        return self.messages
    
    def set_cache_path(self, cache_path: Optional[str | Path] = None) -> 'Prompter':
        self.cache_path = None if cache_path is None else Path(cache_path)
        return self
        
    def get_cache_path(self) -> Optional[Path]:
        return self.cache_path

    def set_logger(self, logger: Optional[TextIO] = None) -> 'Prompter':
        self.logger = logger
        return self
    
    def get_logger(self) -> Optional[TextIO]:
        return self.logger

    def set_interaction(self, interaction: bool = False) -> 'Prompter':
        self.interaction = interaction
        return self
    
    def get_interaction(self) -> bool:
        return self.interaction
    
    def set_summary(self, start_size: Optional[int] = None, include_size: Optional[int] = None) -> 'Prompter':
        self.start_size = start_size
        self.include_size = include_size
        
        if self.start_size is not None:
            assert self.include_size is not None and self.include_size > 0 and self.include_size <= self.start_size, "Invalid values chosen for include_size"
        return self
    
    def get_summary(self) -> Dict[str, Optional[int]]:
        return dict(start_size=self.start_size, include_size=self.include_size)
    
    def get_copy(self) -> 'Prompter':
        return Prompter(self.get_llm())\
            .set_messages(self.get_messages())\
            .set_cache_path(self.get_cache_path())\
            .set_logger(self.get_logger())\
            .set_interaction(self.get_interaction())\
            .set_summary(**self.get_summary())

    def add_message(self, content: str, role: str = "user") -> 'Prompter':
        message = Message(content, role)
        self.messages.append(message)
        if self.logger is not None:
            print(message, end="\n\n", file=self.logger)
        if self.start_size is not None and Message.length(self.messages) >= self.start_size:
            self.summarize()
            if Message.length(self.messages) >= self.start_size:
                raise SummaryError("Prompter was unable to summarize the past conversation to a sufficient level.")
        return self
    
    def add_completion(self, stop: Optional[str] = None) -> 'Prompter':
        if self.interaction:
            message = input("user (↵: next, x: exit): ")
            print()
            if message == "x":
                exit(0)
            if message != "":
                self.add_message(message)
        
        if self.cache_path is None:
            completion = self.llm.get_completion(self.messages, stop)
        else:
            file_path = self.cache_path / hash_str("\n\n".join(f"{message.role}:\n{message.content}" for message in self.messages))
            completion = load_text(file_path)
            if completion is None:
                completion = self.llm.get_completion(self.messages, stop)
                save_text(file_path, completion)
        self.add_message(completion, role="assistant")
        return self
    
    def get_completion(self, stop: Optional[str] = None) -> str:
        self.add_completion(stop)
        return self.messages[-1].content
    
    def get_choice(self, options: List[Option]) -> Tuple[str, str]:
        description = "\n\n".join(option.get_description() for option in options)
        self.add_message(f"Choose one of the following options:\n\n{description}", role="developer")
        completion = self.get_completion(Option.stop)
        if Option.seperator not in completion:
            raise ChoiceError(f"The llm did not adhere to the selection format: \"{completion}\"")
        name, data = map(str.strip, completion.split(Option.seperator, 1))
        if name not in {option.name for option in options}:
            raise ChoiceError(f"The llm made an invalid choice: \"{name}\"")
        return name, data

    def summarize(self) -> None:        
        akk = 0
        included = []
        excluded = []
        for i, message in enumerate(self.messages):
            akk += len(message.content)
            included.append(message.content)
            if akk >= self.include_size:  # type:ignore
                for j in range(i + 1, len(self.messages)):
                    excluded.append(self.messages[j])
                break
        
        conversation = "\n\n".join(f"{message.role}:\n{message.content}" for message in self.messages)
        summary = self.get_copy()\
            .set_messages()\
            .set_summary()\
            .add_message(
                f"Please summarize the following conversation."
                f"\nOnly keep the most important information about the conversation in the summary."
                f"\nOnly answer with the summary and nothing else."
                f"\nHere is the conversation:\n```conversation\n{conversation}\n```",
                role="developer"
            )\
            .get_completion()

        summary_message = Message(
            f"Here is a summary of the conversation until this point:\n```summary\n{summary}\n```",
            role="developer"
        )
        self.set_messages([summary_message] + excluded)