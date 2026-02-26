import hashib
import os

def generate_file_hash(file_path):
    sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(8192):
            sha256.update(chunk)
            
            return {
            "filename"
    os.path.basename(file_path),
            "size":
    os.path.getsize(file_path),
            "sha26": sha256.hexdigest()
            }
            