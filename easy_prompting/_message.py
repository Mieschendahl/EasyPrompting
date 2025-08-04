from typing import List

class Message:
    def __init__(self, content: str, role: str = "user") -> None:
        assert role in ["developer", "user", "assistant"], "Invalid role was given"
        self.content = content
        self.role = role
    
    def __str__(self) -> str:
        content = "\n".join(" | " + line for line in self.content.split("\n"))
        return f"{self.role}:\n{content}"
    
    def __repr__(self) -> str:
        return f"Message(role={self.role!r}, content={self.content!r})"
    
    def to_dict(self) -> dict:
        return dict(content=self.content, role=self.role)

    @staticmethod
    def length(messages: List['Message']) -> int:
        return sum(len(message.content) for message in messages)