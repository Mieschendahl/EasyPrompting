from dataclasses import dataclass
import io
from pathlib import Path
from easy_prompting._option import Option
from easy_prompting._utils import load_text, If, pad, save_text, hash_str
from easy_prompting._llm import LLM
from easy_prompting._message import Message
from typing import Optional, TextIO

class ChoiceError(Exception):
    pass

class SummaryError(Exception):
    pass

class Prompter:
    def __init__(self, llm: LLM) -> None:
        self.set_llm(llm)\
            .set_tag()\
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

    def set_tag(self, id: Optional[str] = None) -> 'Prompter':
        self.id = id
        return self
    
    def get_tag(self) -> Optional[str]:
        return self.id
    
    def set_messages(self, messages: Optional[list[Message]] = None) -> 'Prompter':
        self.messages = [] if messages is None else messages
        return self
    
    def get_messages(self) -> list[Message]:
        return self.messages
    
    def set_cache_path(self, cache_path: Optional[str | Path] = None) -> 'Prompter':
        self.cache_path = None if cache_path is None else Path(cache_path)
        return self
        
    def get_cache_path(self) -> Optional[Path]:
        return self.cache_path

    def set_logger(self, logger: Optional[TextIO | io.TextIOBase] = None) -> 'Prompter':
        self.logger = logger
        return self
    
    def get_logger(self) -> Optional[TextIO | io.TextIOBase]:
        return self.logger

    def set_interaction(self, interaction_role: Optional[str] = None) -> 'Prompter':
        self.interaction_role = interaction_role
        return self
    
    def get_interaction(self) -> Optional[str]:
        return self.interaction_role
    
    def set_summary(self, start_size: Optional[int] = None, include_size: Optional[int] = None) -> 'Prompter':
        self.start_size = start_size
        self.include_size = include_size
        
        if self.start_size is not None:
            assert self.include_size is not None and self.include_size > 0 and self.include_size <= self.start_size, "Invalid values chosen for include_size"
        return self
    
    def get_summary(self) -> tuple[Optional[int], Optional[int]]:
        return self.start_size, self.include_size
    
    def get_copy(self) -> 'Prompter':
        return Prompter(self.get_llm())\
            .set_tag()\
            .set_messages(self.get_messages().copy())\
            .set_cache_path(self.get_cache_path())\
            .set_logger(self.get_logger())\
            .set_interaction(self.get_interaction())\
            .set_summary(*self.get_summary())

    def add_message(self, content: str, role: str = "user") -> 'Prompter':
        message = Message(content, role)
        self.messages.append(message)
        if self.logger is not None:
            text = (
                f"{message.role.upper()} "
                +
                If(self.id is not None, f"({self.id}) ")
                +
                f"({len(self.messages)-1}):\n{pad(message.content, " | ")}"
            )
            print(text, end="\n\n", file=self.logger, flush=True)
        if self.start_size is not None and Message.length(self.messages) >= self.start_size:
            self.summarize()
            if Message.length(self.messages) >= self.start_size:
                raise SummaryError("Prompter was unable to summarize the past conversation to a sufficient level.")
        return self

    def interact(self) -> 'Prompter':
        if self.interaction_role is not None:
            content = input(f"{self.interaction_role.upper()} (↵: next, x: exit): ")
            print()
            if content == "x":
                exit(0)
            if content != "":
                self.add_message(content, self.interaction_role)
        return self
                
    def add_completion(self, stop: Optional[str] = None) -> 'Prompter':
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
        
        self.interact()
        return self
    
    def get_completion(self, stop: Optional[str] = None) -> str:
        self.add_completion(stop)
        completion = self.messages[-1].content
        if stop is not None:
            completion = completion.split(stop, 1)[0]
        return completion
    
    def get_choice(self, *options: Option, role: str = "user") -> tuple[str, str]:
        self.add_message(
                f"{Option.introduction} "
                +
                Option.create_scope(
                    Option.describe_options(*options)
                ),
                role=role
            )
        completion = self.get_completion(Option.create_key(Option.stop))
        for option in options:
            split = completion.split(Option.create_key(option.name), 1)
            if len(split) == 2:
                return option.name, split[1].strip()
        raise ChoiceError(f"The LLM did not adhere to the selection format: \"{completion}\"")

    def summarize(self) -> 'Prompter':        
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
            )\
            .add_message(
                f"Here is the conversation:\n{conversation}",
                role="developer"
            )\
            .get_completion()

        summary_message = Message(
            f"Here is a summary of the conversation until this point:\n```summary\n{summary}\n```",
            role="developer"
        )
        self.set_messages([summary_message] + excluded)
        return self