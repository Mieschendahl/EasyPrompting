import shutil
import hashlib

def create_dir(dir_path, src_path=None, remove=True):
    if remove:
        shutil.rmtree(dir_path, ignore_errors=True)
    if src_path is None:
        dir_path.mkdir(parents=True, exist_ok=True)
    else:
        shutil.copytree(src_path, dir_path, dirs_exist_ok=True) 

def load_text(file_path):
    if file_path.is_file():
        return file_path.read_text()
    return None

def save_text(file_path, text):
    file_path = file_path
    if text is None:
        if file_path.is_file():
            file_path.unlink()
    else:
        create_dir(file_path.parent, remove=False)
        file_path.write_text(text)

def hash_str(text, length=16):
    return hashlib.blake2b(text.encode(), digest_size=length).hexdigest()