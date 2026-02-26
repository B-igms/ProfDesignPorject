import os
import json
import platform
from datetime import datetime


class MetadataExtractor:

    def __init__(self, file_path):
        self.file_path = file_path
        self.file_extension = os.path.splitext(file_path)[1].lower()

    # ==============================
    # UNIVERSAL FILESYSTEM METADATA
    # ==============================
    def extract_filesystem_metadata(self):
        stats = os.stat(self.file_path)

        return {
            "filename": os.path.basename(self.file_path),
            "extension": self.file_extension,
            "size_bytes": stats.st_size,
            "created_time": self._format_time(stats.st_ctime),
            "modified_time": self._format_time(stats.st_mtime),
            "accessed_time": self._format_time(stats.st_atime),
            "os_platform": platform.system()
        }

    # ==============================
    # DXF (TEXT BASED)
    # ==============================
    def extract_dxf_metadata(self):
        metadata = {}
        try:
            with open(self.file_path, "r", errors="ignore") as f:
                content = f.read(5000)  # read first part only

            if "$ACADVER" in content:
                metadata["acad_version"] = self._extract_value(content, "$ACADVER")

            if "$LASTSAVEDBY" in content:
                metadata["last_saved_by"] = self._extract_value(content, "$LASTSAVEDBY")

        except Exception as e:
            metadata["dxf_error"] = str(e)

        return metadata

    # ==============================
    # IFC (TEXT BASED BIM)
    # ==============================
    def extract_ifc_metadata(self):
        metadata = {}
        try:
            with open(self.file_path, "r", errors="ignore") as f:
                header = f.read(2000)

            if "FILE_DESCRIPTION" in header:
                metadata["file_description"] = "Detected"

            if "FILE_NAME" in header:
                metadata["file_name_section"] = "Detected"

            if "FILE_SCHEMA" in header:
                metadata["file_schema"] = "Detected"

        except Exception as e:
            metadata["ifc_error"] = str(e)

        return metadata

    # ==============================
    # STEP / IGES
    # ==============================
    def extract_step_metadata(self):
        metadata = {}
        try:
            with open(self.file_path, "r", errors="ignore") as f:
                header = f.read(1000)

            if "FILE_NAME" in header:
                metadata["file_name_section"] = "Detected"

            if "FILE_SCHEMA" in header:
                metadata["file_schema"] = "Detected"

        except Exception as e:
            metadata["step_error"] = str(e)

        return metadata

    # ==============================
    # MAIN CONTROLLER
    # ==============================
    def extract_all_metadata(self):
        data = {
            "filesystem": self.extract_filesystem_metadata(),
            "cad_specific": {}
        }

        if self.file_extension == ".dxf":
            data["cad_specific"] = self.extract_dxf_metadata()

        elif self.file_extension == ".ifc":
            data["cad_specific"] = self.extract_ifc_metadata()

        elif self.file_extension in [".step", ".stp", ".iges", ".igs"]:
            data["cad_specific"] = self.extract_step_metadata()

        else:
            data["cad_specific"] = {
                "note": "No specific parser available for this format."
            }

        return data

    # ==============================
    # HELPER FUNCTIONS
    # ==============================
    def _format_time(self, timestamp):
        return datetime.utcfromtimestamp(timestamp).isoformat() + "Z"

    def _extract_value(self, content, key):
        try:
            start = content.find(key)
            return content[start:start+200]
        except:
            return "Not found"


# ==============================
# CLI TEST
# ==============================
if __name__ == "__main__":
    import sys

    file_path = sys.argv[1]
    extractor = MetadataExtractor(file_path)
    metadata = extractor.extract_all_metadata()

    print(json.dumps(metadata, indent=4))