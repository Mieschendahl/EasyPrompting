import re
from typing import Optional
from easy_prompting._utils import If, pad_text

def delimit_code(text: str, keyword: str = "") -> str:
    return f"```{keyword}\n{text}\n```"

def extract_code(code: str) -> str:
    match = re.search(r'```(?:[a-zA-Z]*\n)?(.*)```', code, re.DOTALL)
    if not match:
        return code  # No code block found
    return match.group(1).strip()

def wrap_text(text: str) -> str:
    return f"[[{text}]]"

def scope_text(text: str, padding: str = "  ") -> str:
    return " {\n" + pad_text(text, padding) + "\n}"

def list_text(*texts: Optional[str], scope: bool = True) -> str:
    text_out = "\n".join(f"- {text}" for text in texts if text is not None)
    if scope:
        return scope_text(text_out)
    return text_out