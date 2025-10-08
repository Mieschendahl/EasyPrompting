from typing import Literal

roles = "user", "assistant", "developer"
Role = Literal["user", "assistant", "developer"]

class Message:
    def __init__(self, content: str, role: Role = "user") -> None:
        self._content = content
        self._role: Role = role
    
    def get_content(self) -> str:
        return self._content
    
    def get_role(self) -> Role:
        return self._role

    def __repr__(self) -> str:
        return f"Message(role={self._role!r}, content={self._content!r})"
    
    def to_dict(self) -> dict:
        return dict(content=self._content, role=self._role)

    @staticmethod
    def length(messages: list['Message']) -> int:
        return sum(len(message._content) for message in messages)