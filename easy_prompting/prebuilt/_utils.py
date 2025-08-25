import re

def delimit_code(text: str, keyword: str = "", left: str = "```", right: str = "```") -> str:
    return f"{left}{keyword}\n{text}\n{right}"

def extract_code(code: str) -> str:
    match = re.search(r'```(?:[a-zA-Z]*\n)?(.*)```', code, re.DOTALL)
    if not match:
        return code  # No code block found
    return match.group(1).strip()