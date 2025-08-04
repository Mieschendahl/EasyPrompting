from typing import Optional
from easy_prompting._utils import If

class Option:
    seperator: str = ":"
    stop: str = "(done)"
    
    def __init__(self, name: str, condition: str, action: str = "Write nothing", effect: Optional[str] = None) -> None:
        self.name = name
        self.condition = condition
        self.action = action
        self.effect = effect
    
    def get_description(self) -> str:
        return (
            f"{self.condition}"
            f"\n1. Write \"{self.name}{Option.seperator}\""
            f"\n2. {self.action}"
            f"\n3. Write \"{Option.stop}\""
            +
            If(self.effect is not None, f"\n4. {self.effect}")
        )