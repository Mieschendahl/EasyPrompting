import re

def extract_code(code: str) -> str:
    match = re.search(r'```(?:[a-zA-Z]*\n)?(.*)```', code, re.DOTALL)
    if not match:
        return code  # No code block found
    return match.group(1).strip()

def If(condition: bool, then_text: str, else_text: str = "") -> str:
    if condition:
        return then_text
    return else_text