from typing import Optional
from easy_prompting._utils import pad_text, scope_text

def list_text(*texts: Optional[str], add_scope: bool = False) -> str:
    text_out = "\n".join(f"- {pad_text(text, pad_first=False)}" for text in texts if text is not None)
    if add_scope:
        return scope_text(text_out)
    return text_out

def extract_code(code: str, language: str = "") -> str:
    lines = code.split("\n")
    start = None
    for i, line in enumerate(lines):
        if line.startswith("```" + language):
            start = i + 1
            break
    if start is not None:
        for i, line in enumerate(lines[start:]):
            if line.startswith("```"):
                return "\n".join(lines[start:start+i]).strip()
    return "\n".join(line for line in lines if not line.startswith("```")).strip()

def delimit_code(text: str, keyword: str = "") -> str:
    return f"```{keyword}\n{text}\n```"