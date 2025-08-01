class Option:
    seperator = ":"
    stop = "(done)"
    
    def __init__(self, name, condition, action, effect):
        self.name = name
        self.condition = condition
        self.action = action
        self.effect = effect
    
    def get_description(self):
        return (
            f"{self.condition}"
            f"1. Write \"{self.name}{Option.seperator}\""
            f"2. {self.action}"
            f"3. Write \"{Option.stop}\""
            f"4. {self.effect}"
        )
