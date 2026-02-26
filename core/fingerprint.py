import os
import hashlib
from datetime import datetime


class FileFingerprint:
    def __init__(self, file_path: str):
        if not os.path.isfile(file_path):
            raise FileNotFoundError(f"File tidak ditemukan: {file_path}")

        self.file_path = file_path
        self.file_size = os.path.getsize(file_path)

    # =========================================
    # FULL FILE HASH (SHA-256)
    # =========================================
    def full_hash(self, buffer_size: int = 8192) -> str:
        sha256 = hashlib.sha256()

        with open(self.file_path, "rb") as f:
            while True:
                chunk = f.read(buffer_size)
                if not chunk:
                    break
                sha256.update(chunk)

        return sha256.hexdigest()

    # =========================================
    # HEAD + TAIL HASH
    # =========================================
    def head_tail_hash(self, chunk_size: int = 2048) -> str:
        if self.file_size == 0:
            return None

        with open(self.file_path, "rb") as f:
            head = f.read(chunk_size)

            if self.file_size > chunk_size:
                f.seek(max(self.file_size - chunk_size, 0))
                tail = f.read(chunk_size)
            else:
                tail = b""

        combined = head + tail
        return hashlib.sha256(combined).hexdigest()

    # =========================================
    # SEGMENTED HASH
    # =========================================
    def segmented_hash(self, segments: int = 5, chunk_size: int = 1024) -> str:
        if self.file_size == 0:
            return None

        sha256 = hashlib.sha256()
        step = max(self.file_size // segments, 1)

        with open(self.file_path, "rb") as f:
            for i in range(segments):
                position = i * step
                if position >= self.file_size:
                    break

                f.seek(position)
                chunk = f.read(chunk_size)
                sha256.update(chunk)

        return sha256.hexdigest()

    # =========================================
    # STRUCTURAL INFO
    # =========================================
    def structural_info(self) -> dict:
        return {
            "size_bytes": self.file_size,
            "size_kb": round(self.file_size / 1024, 2),
            "size_mb": round(self.file_size / (1024 * 1024), 2),
        }

    # =========================================
    # COMPLETE FINGERPRINT PACKAGE
    # =========================================
    def generate(self) -> dict:
        return {
            "generated_at_utc": datetime.utcnow().isoformat() + "Z",
            "full_sha256": self.full_hash(),
            "head_tail_sha256": self.head_tail_hash(),
            "segmented_sha256": self.segmented_hash(),
            "structural": self.structural_info()
        }


# =========================================
# CLI TEST
# =========================================
if __name__ == "__main__":
    import sys
    import json

    if len(sys.argv) != 2:
        print("Usage: python fingerprint.py <path_to_file>")
        sys.exit(1)

    file_path = sys.argv[1]

    fingerprint = FileFingerprint(file_path)
    result = fingerprint.generate()

    print(json.dumps(result, indent=4))