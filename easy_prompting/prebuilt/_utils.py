import re
from typing import Optional

from easy_prompting._utils import scope_text

def list_text(*texts: Optional[str], add_scope: bool = False) -> str:
    text_out = "\n".join(f"- {text}" for text in texts if text is not None)
    if add_scope:
        return scope_text(text_out)
    return text_out

def extract_code(code: str) -> str:
    match = re.search(r'```(?:[a-zA-Z]*\n)?(.*)```', code, re.DOTALL)
    if not match:
        return code.strip()  # No code block found
    return match.group(1).strip()

def delimit_code(text: str, keyword: str = "") -> str:
    return f"```{keyword}\n{text}\n```"