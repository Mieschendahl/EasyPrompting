from typing import Optional
from easy_prompting._utils import pad, wrap

class Message:
    key_prefix = "[["
    key_suffix = "]]"
    left_bracket = " {\n"
    right_bracket = "\n}"
    padding = "  "
    bullet_point = "- "

    @staticmethod
    def create_key(name: str) -> str:
        return wrap(name, Message.key_prefix, Message.key_suffix)

    @staticmethod
    def create_scope(text: str) -> str:
        return f"{Message.left_bracket}{pad(text, Message.padding)}{Message.right_bracket}"
    
    @staticmethod
    def create_list(*list: Optional[str], scope: bool = False) -> str:
        output = "\n".join(f"{Message.bullet_point}{element}" for element in list if element is not None)
        if scope:
            output = Message.create_scope(output)
        return output

    @staticmethod
    def describe_key(name: str) -> str:
        return f"Write \"{Message.create_key(name)}\""

    @staticmethod
    def describe_sequence(*sequence: Optional[str], scope: bool = False) -> str:
        output = []
        for i, element in enumerate(sequence):
            if element is None:
                continue
            if i % 2:
                output.append(element)
            else:
                output.append(Message.describe_key(element))
        return Message.create_list(*output, scope=scope)

    @staticmethod
    def extract_sequence(sequence_str: str, dividers: list[str]) -> list[str]:
        sequence = []
        for divider in dividers:
            if Message.create_key(divider) not in sequence_str:
                raise Exception(f"\"{Message.create_key(divider)}\" not found in \"{sequence_str}\"")
            head, sequence_str = sequence_str.split(Message.create_key(divider), 1)
            sequence.append(head)
        sequence = sequence[1:] + [sequence_str]
        return [element.strip() for element in sequence]

    @staticmethod
    def extract_repeating_sequence(sequence_str: str, dividers: list[str]) -> list[list[str]]:
        sequence = Message.extract_sequence(sequence_str, dividers)
        if Message.create_key(dividers[0]) not in sequence[-1]:
            return [sequence]
        head, _ = sequence[-1].split(Message.create_key(dividers[0]), 1)
        sequences = Message.extract_repeating_sequence(sequence[-1], dividers)
        return [sequence[:-1] + [head]] + sequences

    def __init__(self, content: str, role: str = "user") -> None:
        assert role in ["developer", "user", "assistant"], "Invalid role was given"
        self.content = content
        self.role = role
    
    def __str__(self) -> str:
        return f"{self.role.upper()}:\n{pad(self.content, " | ")}"
    
    def __repr__(self) -> str:
        return f"Message(role={self.role!r}, content={self.content!r})"
    
    def to_dict(self) -> dict:
        return dict(content=self.content, role=self.role)

    @staticmethod
    def length(messages: list['Message']) -> int:
        return sum(len(message.content) for message in messages)