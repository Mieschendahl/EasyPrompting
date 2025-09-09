import re
import shutil
import hashlib
from pathlib import Path
from typing import Optional

def create_dir(dir_path: Path, src_path: Optional[Path] = None, remove: bool = True) -> None:
    if remove:
        shutil.rmtree(dir_path, ignore_errors=True)
    if src_path is None:
        dir_path.mkdir(parents=True, exist_ok=True)
    else:
        shutil.copytree(src_path, dir_path, dirs_exist_ok=True) 

def load_text(file_path: Path) -> Optional[str]:
    if file_path.is_file():
        return file_path.read_text()
    return None

def save_text(file_path: Path, text: Optional[str]) -> None:
    if text is None:
        if file_path.is_file():
            file_path.unlink()
    else:
        create_dir(file_path.parent, remove=False)
        file_path.write_text(text)

def hash_str(text: str, length: int = 16) -> str:
    return hashlib.blake2b(text.encode(), digest_size=length).hexdigest()

def If[T](condition: bool, then_text: T, else_text: T = "") -> T:
    if condition:
        return then_text
    return else_text

def pad_text(text: str, padding: str = "  ") -> str:
    return "\n".join(f"{padding}{line}" for line in text.split("\n"))

def wrap_text(text: str) -> str:
    return f"[[{text}]]"

def scope_text(text: str) -> str:
    return " {\n" + pad_text(text) + "\n}"

def list_text(*texts: Optional[str], add_scope: bool = False) -> str:
    text_out = "\n".join(f"- {text}" for text in texts if text is not None)
    if add_scope:
        return scope_text(text_out)
    return text_out

def enumerate_text(*texts: Optional[str], add_scope: bool = False) -> str:
    i = 1
    text_ls = []
    for text in texts:
        if text is not None:
            text_ls.append(f"{i}. {text}")
        i += 1
    text_out = "\n".join(text_ls)
    if add_scope:
        return scope_text(text_out)
    return text_out

def extract_code(code: str) -> str:
    match = re.search(r'```(?:[a-zA-Z]*\n)?(.*)```', code, re.DOTALL)
    if not match:
        return code.strip()  # No code block found
    return match.group(1).strip()