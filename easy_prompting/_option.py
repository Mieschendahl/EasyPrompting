from typing import Optional
from easy_prompting._utils import If, pad

class Option:
    stop = "stop"
    key_prefix = "[["
    key_suffix = "]]"
    left_bracket = "{\n"
    right_bracket = "\n}"
    padding = "  "
    bullet_point = "- "
    introduction = "Choose exactly one of the following options and terminate it correctly"
    
    @staticmethod
    def create_key(name: str) -> str:
        return Option.key_prefix + name + Option.key_suffix
    
    @staticmethod
    def describe_key(name: str) -> str:
        return f"Write \"{Option.create_key(name)}\""
    
    @staticmethod
    def create_scope(text: str) -> str:
        return f"{Option.left_bracket}{pad(text, Option.padding)}{Option.right_bracket}"

    @staticmethod
    def describe_sequence(*sequence: str) -> str:
        output = []
        for i, element in enumerate(sequence):
            if i % 2:
                output.append(f"\n{Option.bullet_point}{element}")
            else:
                output.append(f"\n{Option.bullet_point}{Option.describe_key(element)}")
        return "".join(output)

    @staticmethod
    def extract_sequence(sequence_str: str, dividers: list[str]) -> list[str]:
        sequence = []
        for divider in dividers:
            head, sequence_str = sequence_str.split(Option.create_key(divider), 1)
            sequence.append(head)
        sequence = sequence[1:] + [sequence_str]
        return [element.strip() for element in sequence]

    @staticmethod
    def extract_repeating_sequence(sequence_str: str, dividers: list[str]) -> list[list[str]]:
        sequence = Option.extract_sequence(sequence_str, dividers)
        if Option.create_key(dividers[0]) not in sequence[-1]:
            return [sequence]
        head, _ = sequence[-1].split(Option.create_key(dividers[0]), 1)
        sequences = Option.extract_repeating_sequence(sequence[-1], dividers)
        return [sequence[:-1] + [head]] + sequences

    @staticmethod
    def describe_options(*options: "Option"):
        return "\n\n".join(option.get_description() for option in options)

    def __init__(self, name: str, condition: str, action: Optional[str] = None, effect: Optional[str] = None) -> None:
        self.name = name
        self.condition = condition
        self.action = action
        self.effect = effect

    def get_description(self) -> str:
        return (
            f"{self.condition} "
            +
            Option.create_scope(
                f"{Option.bullet_point}{Option.describe_key(self.name)}"
                +
                If(self.effect is not None, f"\n{Option.bullet_point}{self.action}")
                +
                f"\n{Option.bullet_point}{Option.describe_key(Option.stop)}"
                +
                If(self.effect is not None, f"\n{Option.bullet_point}{self.effect}")
            )
        )