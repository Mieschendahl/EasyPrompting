from typing import Optional
from easy_prompting._message import Message

class Option:
    stop = "stop"
    introduction = "Choose exactly one of the following options and terminate it correctly"

    @staticmethod
    def describe_options(*options: "Option", scope: bool = False):
        return Message.create_list(*map(str, options), scope=scope)

    def __init__(self, name: str, condition: str, action: Optional[str] = None, effect: Optional[str] = None) -> None:
        self.name = name
        self.condition = condition
        self.action = action
        self.effect = effect

    def __str__(self) -> str:
        return (
            self.condition
            +
            Message.describe_sequence(
                self.name,
                self.action,
                Option.stop,
                self.effect,
                scope=True
            )
        )

    def __repr__(self) -> str:
        return f"Option(name={self.name!r}, condition={self.condition!r}, action={self.action!r}, effect={self.effect!r})"