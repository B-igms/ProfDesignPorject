import os
import hashlib
import json
from datetime import datetime

from metadata_extractor import MetadataExtractor


class CADHandler:

    SUPPORTED_FORMATS = [
        ".dwg", ".dxf",
        ".rvt", ".ifc",
        ".step", ".stp",
        ".iges", ".igs",
        ".sldprt", ".sldasm",
        ".skp"
    ]

    def __init__(self, file_path):
        self.file_path = file_path
        self.extension = os.path.splitext(file_path)[1].lower()

        if not os.path.exists(file_path):
            raise FileNotFoundError("File tidak ditemukan.")

        if self.extension not in self.SUPPORTED_FORMATS:
            print("⚠ Format tidak dikenali sebagai CAD/BIM standar.")

    # =====================================
    # RAW HASH (FILE AS IS)
    # =====================================
    def generate_raw_hash(self):
        sha256 = hashlib.sha256()

        with open(self.file_path, "rb") as f:
            while chunk := f.read(8192):
                sha256.update(chunk)

        return sha256.hexdigest()

    # =====================================
    # NORMALIZED HASH (BASIC VERSION)
    # =====================================
    def generate_normalized_hash(self):
        """
        Versi dasar:
        - Hilangkan whitespace berlebih untuk file text-based
        - Binary tetap raw
        """

        if self.extension in [".dxf", ".ifc", ".step", ".stp", ".iges", ".igs"]:
            try:
                with open(self.file_path, "r", errors="ignore") as f:
                    content = f.read()

                normalized = "".join(content.split())
                return hashlib.sha256(normalized.encode()).hexdigest()

            except:
                return self.generate_raw_hash()

        else:
            # Untuk binary proprietary
            return self.generate_raw_hash()

    # =====================================
    # BASIC FINGERPRINT
    # =====================================
    def generate_fingerprint(self):
        """
        Fingerprint ringan berbasis:
        - Ukuran file
        - 1KB awal
        - 1KB akhir
        """

        file_size = os.path.getsize(self.file_path)

        with open(self.file_path, "rb") as f:
            head = f.read(1024)
            f.seek(max(file_size - 1024, 0))
            tail = f.read(1024)

        combined = head + tail
        fingerprint_hash = hashlib.sha256(combined).hexdigest()

        return {
            "size_bytes": file_size,
            "fingerprint_hash": fingerprint_hash
        }

    # =====================================
    # FULL PROCESS
    # =====================================
    def process_file(self):
        extractor = MetadataExtractor(self.file_path)

        result = {
            "file_info": {
                "filename": os.path.basename(self.file_path),
                "extension": self.extension,
                "processed_at": datetime.utcnow().isoformat() + "Z"
            },
            "hash": {
                "raw_sha256": self.generate_raw_hash(),
                "normalized_sha256": self.generate_normalized_hash()
            },
            "fingerprint": self.generate_fingerprint(),
            "metadata": extractor.extract_all_metadata()
        }

        return result


# =====================================
# CLI TEST
# =====================================
if __name__ == "__main__":
    import sys

    file_path = sys.argv[1]

    handler = CADHandler(file_path)
    result = handler.process_file()

    print(json.dumps(result, indent=4))