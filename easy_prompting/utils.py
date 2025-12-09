import shutil
import hashlib
from pathlib import Path
from typing import Optional
        
def create_dir(dst_path: Path, src_path: Optional[Path] = None, overwrite: bool = False) -> None:
    if overwrite:
        shutil.rmtree(dst_path, ignore_errors=True)
    if src_path is None:
        dst_path.mkdir(parents=True, exist_ok=True)
    else:
        shutil.copytree(src_path, dst_path, dirs_exist_ok=True, symlinks=True)

def load_text(file_path: Path) -> Optional[str]:
    if file_path.is_file():
        return file_path.read_text()
    return None

def save_text(file_path: Path, text: Optional[str]) -> None:
    if text is None:
        if file_path.is_file():
            file_path.unlink()
    else:
        create_dir(file_path.parent)
        file_path.write_text(text)

def hash_str(text: str, length: int = 16) -> str:
    return hashlib.blake2b(text.encode(), digest_size=length).hexdigest()

def pad_text(text: str, padding: str = "  ", pad_first: bool = True) -> str:
    if pad_first:
        return "\n".join(f"{padding}{line}" for line in text.split("\n"))
    return f"\n{padding}".join(text.split("\n"))

def scope_text(text: str) -> str:
    return " {\n" + pad_text(text) + "\n}"

def enumerate_text(*texts: Optional[str], add_scope: bool = False) -> str:
    i = 1
    text_ls = []
    for text in texts:
        if text is not None:
            text_ls.append(f"{i}. {pad_text(text, pad_first=False)}")
        i += 1
    text_out = "\n".join(text_ls)
    if add_scope:
        return scope_text(text_out)
    return text_out

def list_text(*texts: Optional[str], add_scope: bool = False) -> str:
    text_out = "\n".join(f"- {pad_text(text, pad_first=False)}" for text in texts if text is not None)
    if add_scope:
        return scope_text(text_out)
    return text_out

def wrap_text(text: str) -> str:
    return f"[[{text}]]"

def multi_str(text: str, base: str = "| ") -> str:
    lines = text.split("\n")[1:-1]
    return "\n".join(line.split(base)[1] for line in lines)