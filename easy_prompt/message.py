class Message:
    def __init__(self, message, role="user"):
        assert role in ["developer", "user", "assistant"], "Invalid role was given"
        self.content = message
        self.role = role
    
    def __str__(self):
        content = "".join(" # " + line for line in self.content.split("\n"))
        return f"{self.role}:{content}"
    
    def to_dict(self):
        return dict(content=self.content, role=self.role)

    @staticmethod
    def length(messages):
        return sum(len(message.content) for message in messages)