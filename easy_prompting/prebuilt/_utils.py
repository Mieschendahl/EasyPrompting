import re
from easy_prompting._utils import If, pad

def extract_code(code: str) -> str:
    match = re.search(r'```(?:[a-zA-Z]*\n)?(.*)```', code, re.DOTALL)
    if not match:
        return code  # No code block found
    return match.group(1).strip()