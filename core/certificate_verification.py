import os
import json
import uuid
from datetime import datetime


class CertificateGenerator:

    def __init__(self, output_dir: str = "certificates"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    # =========================================
    # BUILD CERTIFICATE
    # =========================================
    def generate_certificate(
        self,
        original_file_path: str,
        hash_data: dict,
        fingerprint_data: dict,
        metadata: dict,
        issuer: str
    ) -> dict:

        if not os.path.isfile(original_file_path):
            raise FileNotFoundError("File asli tidak ditemukan.")

        certificate_id = str(uuid.uuid4())

        file_info = {
            "filename": os.path.basename(original_file_path),
            "extension": os.path.splitext(original_file_path)[1].lower(),
            "size_bytes": os.path.getsize(original_file_path),
            "absolute_path": os.path.abspath(original_file_path)
        }

        certificate_data = {
            "certificate_id": certificate_id,
            "issued_at_utc": datetime.utcnow().isoformat() + "Z",
            "issuer": issuer,
            "file_info": file_info,
            "hash": hash_data,
            "fingerprint": fingerprint_data,
            "metadata": metadata
        }

        return certificate_data

    # =========================================
    # SAVE CERTIFICATE
    # =========================================
    def save_certificate(self, certificate_data: dict) -> str:
        certificate_id = certificate_data["certificate_id"]
        filename = f"{certificate_id}.certificate.json"
        filepath = os.path.join(self.output_dir, filename)

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(certificate_data, f, indent=4)

        return filepath


# =========================================
# CLI TEST
# =========================================
if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        print("Usage: python certificate_generator.py <path_to_file>")
        exit(1)

    file_path = sys.argv[1]

    # Dummy data (biasanya dari cad_handler)
    dummy_hash = {"sha256": "example_hash"}
    dummy_fingerprint = {"fingerprint": "example_fp"}
    dummy_metadata = {"note": "example metadata"}

    generator = CertificateGenerator()

    cert = generator.generate_certificate(
        original_file_path=file_path,
        hash_data=dummy_hash,
        fingerprint_data=dummy_fingerprint,
        metadata=dummy_metadata,
        issuer="DesignProof-ID"
    )

    path = generator.save_certificate(cert)

    print("Sertifikat dibuat:", path)