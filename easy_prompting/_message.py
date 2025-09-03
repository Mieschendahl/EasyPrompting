from typing import Optional, Union
from easy_prompting._utils import pad_text

class Message:
    def __init__(self, content: str, role: str = "user") -> None:
        assert role in ["developer", "user", "assistant"], "Invalid role was given"
        self.content = content
        self.role = role
    
    def __str__(self) -> str:
        return f"{self.role.upper()}:\n{pad_text(self.content)}"
    
    def __repr__(self) -> str:
        return f"Message(role={self.role!r}, content={self.content!r})"
    
    def to_dict(self) -> dict:
        return dict(content=self.content, role=self.role)

    @staticmethod
    def length(messages: list['Message']) -> int:
        return sum(len(message.content) for message in messages)

class Instruction:
    key_prefix = "[["
    key_suffix = "]]"
    left_bracket = " {\n"
    right_bracket = "\n}"
    bullet_point = "- "
    padding = "  "
    stop = "stop"
    choice_message = "Choose exactly one of the following options and terminate it correctly"

    @staticmethod
    def uniquify(key: str) -> str:
        return f"{Instruction.key_prefix}{key}{Instruction.key_suffix}"

    def __init__(self, message: Optional[str] = None, mode: str = "list"):
        assert mode in ["text", "list", "choice", "loop"]
        self.message = message
        self.mode = mode
        self.items: list[tuple[str, Optional[Union[str, "Instruction"]]]] = []
        self.stop_added = False
    
    def add_item(self, key: str, value: Optional[Union[str, "Instruction"]] = None) -> "Instruction":
        self.items.append((key, value))
        return self

    def add_stop(self) -> "Instruction":
        assert self.mode == "list", "Can only add stop to list mode instruction"
        assert not self.stop_added, "Stop can not be added twice"
        self.stop_added = True
        self.add_item(Instruction.stop)
        return self

    def __str__(self) -> str:
        instructions: list[str] = []
        for key, value in self.items:
            instructions.append(f"{Instruction.bullet_point}Write \"{Instruction.uniquify(key)}\"")
            if value is not None:
                instructions.append(str(value))

        instructions_str = '\n'.join(instructions)
        if self.message is not None:
            return f"{self.message}{Instruction.left_bracket}{pad_text(instructions_str, Instruction.padding)}{Instruction.right_bracket}"
        return instructions_str

    def extract_list(self, completion: str) -> list:
        extraction = []
        for key, _ in self.items:
            if key not in completion:
                raise Exception(f"LLM did not adhere to extraction format: \"{Instruction.uniquify(key)}\" missing in \"{completion}\"")
            head, completion = completion.split(key, 1)
            extraction.append(head)
        extraction.append(completion)

        extraction = extraction[1:]
        for i, (_, value) in enumerate(self.items):
            if isinstance(value, Instruction):
                extraction[i] = value.extract(extraction[i])

        if self.stop_added:
            extraction = extraction[:-1]
        return extraction

    def extract_choice(self, completion: str) -> str | list:
        for key, value in self.items:
            if key in completion:
                _, completion = completion.split(key, 1)
                if isinstance(value, Instruction):
                    return value.extract(completion)
                return completion
        raise Exception(f"LLM did not adhere to extraction format: No key option found in \"{completion}\"")

    def extract_loop(self, completion: str) -> list | str:
        assert len(self.items) > 0, "Need at least one item for looped extraction"

        if self.items[0][0] not in completion:
            return []

        extractions = []
        while True:
            extraction = []
            for key, _ in self.items:
                if key not in completion:
                    raise Exception(f"LLM did not adhere to extraction format: \"{Instruction.uniquify(key)}\" missing in \"{completion}\"")
                head, completion = completion.split(key, 1)
                extraction.append(head)

            if self.items[0][0] in completion:
                head, _ = completion.split(self.items[0][0], 1)
                extraction.append(head)
            else:
                extraction.append(completion)

            extraction = extraction[1:]
            for i, (_, value) in enumerate(self.items):
                if isinstance(value, Instruction):
                    extraction[i] = value.extract(extraction[i])

            extractions.append(extraction)
            if self.items[0][0] not in completion:
                return extractions

    def extract(self, completion: str) -> list | str:
        match self.mode:
            case "text":
                return completion
            case "list":
                return self.extract_list(completion)
            case "choice":
                return self.extract_choice(completion)
            case "option":
                return self.extract_loop(completion)
        assert False, "impossible"