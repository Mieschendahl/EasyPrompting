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

def If(condition: bool, then_text: str, else_text: str = "") -> str:
    if condition:
        return then_text
    return else_text