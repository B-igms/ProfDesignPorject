import sys
import json
import os

from core.cad_handler import CADHandler
from core.fingerprint import FileFingerprint
from core.metadata_extractor import MetadataExtractor
from core.certificate_generator import CertificateGenerator


def main():
    if len(sys.argv) != 2:
        print("Usage: python main.py <path_to_file>")
        sys.exit(1)

    file_path = sys.argv[1]

    if not os.path.isfile(file_path):
        print("File tidak ditemukan.")
        sys.exit(1)

    try:
        # ==============================
        # CAD Handler (Hash)
        # ==============================
        cad = CADHandler(file_path)
        hash_data = {
            "raw_sha256": cad.generate_raw_hash(),
            "normalized_sha256": cad.generate_normalized_hash()
        }

        # ==============================
        # Fingerprint
        # ==============================
        fingerprint = FileFingerprint(file_path)
        fingerprint_data = fingerprint.generate()

        # ==============================
        # Metadata
        # ==============================
        metadata_extractor = MetadataExtractor(file_path)
        metadata = metadata_extractor.extract_all_metadata()

        # ==============================
        # Certificate
        # ==============================
        cert_generator = CertificateGenerator()

        certificate = cert_generator.generate_certificate(
            original_file_path=file_path,
            hash_data=hash_data,
            fingerprint_data=fingerprint_data,
            metadata=metadata,
            issuer="DesignProof-ID CLI"
        )

        cert_path = cert_generator.save_certificate(certificate)

        # ==============================
        # Output
        # ==============================
        print("\n=== VERIFICATION COMPLETE ===")
        print("Certificate ID :", certificate["certificate_id"])
        print("Certificate File:", cert_path)
        print("Raw SHA256     :", hash_data["raw_sha256"])

    except Exception as e:
        print("Terjadi kesalahan:", str(e))
        sys.exit(1)


if __name__ == "__main__":
    main()