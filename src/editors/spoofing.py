"""
MetaClean — Metadata Spoofing & Anonymizer
Menyamarkan identitas berkas dengan mengganti metadata asli menggunakan metadata dummy/sintetis
yang realistis (Kamera Canon, Nikon, Sony acak) untuk mencegah deteksi pembersihan metadata.
"""
import os
import random
from datetime import datetime, timedelta
from typing import Dict, Any
import piexif
from PIL import Image

class MetadataSpoofer:
    """Mesin penyamar metadata sintetis (Metadata Anonymizer & Spoofing)."""

    PROFILES = {
        "canon": {
            "make": "Canon",
            "model": "Canon EOS 5D Mark IV",
            "software": "Canon Digital Photo Professional 4.15",
            "artist": "Photographer"
        },
        "nikon": {
            "make": "NIKON CORPORATION",
            "model": "NIKON D850",
            "software": "Nikon NX Studio 1.2.0",
            "artist": "Photographer"
        },
        "sony": {
            "make": "SONY",
            "model": "ILCE-7RM4",
            "software": "Sony Imaging Edge Desktop 3.2",
            "artist": "Photographer"
        }
    }

    @classmethod
    def spoof(cls, file_path: str, profile_name: str = "random", inplace: bool = False) -> Dict[str, Any]:
        """
        Menyuntikkan metadata sintetis yang wajar ke dalam berkas.
        """
        if not os.path.exists(file_path):
            return {"success": False, "error": f"Berkas tidak ditemukan: {file_path}"}

        ext = os.path.splitext(file_path)[1].lower()
        output_path = file_path if inplace else cls._get_output_path(file_path)

        # Pilih profil kamera
        if profile_name == "random" or profile_name not in cls.PROFILES:
            profile_key = random.choice(list(cls.PROFILES.keys()))
        else:
            profile_key = profile_name

        profile = cls.PROFILES[profile_key]

        # Generate tanggal acak dalam 30 hari terakhir
        random_days = random.randint(1, 28)
        synthetic_date = (datetime.now() - timedelta(days=random_days)).strftime("%Y:%m:%d %H:%M:%S")

        if ext in [".jpg", ".jpeg", ".tiff", ".tif"]:
            try:
                if not inplace:
                    import shutil
                    shutil.copy2(file_path, output_path)

                # Siapkan struktur EXIF sintetis murni
                zeroth_ifd = {
                    piexif.ImageIFD.Make: profile["make"].encode("utf-8"),
                    piexif.ImageIFD.Model: profile["model"].encode("utf-8"),
                    piexif.ImageIFD.Software: profile["software"].encode("utf-8"),
                    piexif.ImageIFD.Artist: profile["artist"].encode("utf-8"),
                    piexif.ImageIFD.DateTime: synthetic_date.encode("utf-8")
                }

                iso_val = random.choice([100, 200, 400])
                exif_ifd = {
                    piexif.ExifIFD.DateTimeOriginal: synthetic_date.encode("utf-8"),
                    piexif.ExifIFD.ISOSpeedRatings: iso_val,
                    piexif.ExifIFD.FNumber: (28, 10),      # f/2.8
                    piexif.ExifIFD.ExposureTime: (1, 250), # 1/250s
                    piexif.ExifIFD.FocalLength: (50, 1)    # 50mm
                }

                # GPS sengaja dikosongkan untuk perlindungan privasi
                exif_dict = {
                    "0th": zeroth_ifd,
                    "Exif": exif_ifd,
                    "GPS": {},
                    "1st": {},
                    "thumbnail": None
                }

                exif_bytes = piexif.dump(exif_dict)
                piexif.insert(exif_bytes, output_path)

                return {
                    "success": True,
                    "output_path": output_path,
                    "profile_applied": profile["model"],
                    "synthetic_date": synthetic_date
                }

            except Exception as e:
                return {"success": False, "error": f"Gagal menerapkan metadata spoofing: {str(e)}"}

        elif ext == ".pdf":
            try:
                from src.editors.pdf_editor import PdfEditor
                return PdfEditor().update_fields(file_path, {
                    "Title": "Document",
                    "Author": "User",
                    "Subject": "General Document",
                    "Producer": "PDF Generator"
                }, inplace=inplace)
            except Exception as e:
                return {"success": False, "error": str(e)}

        elif ext == ".docx":
            try:
                from src.editors.docx_editor import DocxEditor
                return DocxEditor().update_fields(file_path, {
                    "Title": "Document",
                    "Author": "User",
                    "Subject": "General Document"
                }, inplace=inplace)
            except Exception as e:
                return {"success": False, "error": str(e)}

        else:
            return {"success": False, "error": f"Format {ext} belum didukung untuk spoofing metadata."}

    @staticmethod
    def _get_output_path(file_path: str) -> str:
        d, f = os.path.split(file_path)
        name, ext = os.path.splitext(f)
        return os.path.join(d, f"{name}_spoofed{ext}")
