from easy_prompting._utils import pad

class Message:
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