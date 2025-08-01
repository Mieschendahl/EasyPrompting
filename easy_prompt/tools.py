import re

def extract_code(code: str) -> str:
    match = re.search(r'```(?:[a-zA-Z]*\n)?(.*)```', code, re.DOTALL)

    if not match:
        return code  # No code block found

    return match.group(1).strip()

If = lambda a, b: b if a else ""
IfNot = lambda a, b: "" if a else b
IfElse = lambda a, b, c: b if a else c