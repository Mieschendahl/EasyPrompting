from typing import Literal

Role = Literal["user", "assistant", "developer"]

class Message:
    def __init__(self, content: str, role: Role = "user") -> None:
        self._content = content
        self._role = role

    def __repr__(self) -> str:
        return f"Message(role={self._role!r}, content={self._content!r})"
    
    def to_dict(self) -> dict:
        return dict(content=self._content, role=self._role)

    @staticmethod
    def length(messages: list['Message']) -> int:
        return sum(len(message._content) for message in messages)