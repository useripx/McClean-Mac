"""
Editor Metadata Gambar untuk Mrclean
Mendukung penyuntingan selektif tag EXIF gambar (Artist, Judul, Hak Cipta, Software, Tanggal)
secara preservative tanpa merusak tag EXIF lain (kamera, lensa, resolusi, dll).
"""

import os
import shutil
from typing import Dict, Any
from PIL import Image
import piexif
from src.editors.base import BaseMetadataEditor

class ImageEditor(BaseMetadataEditor):
    """Editor metadata selektif untuk berkas gambar (JPEG, PNG, TIFF)."""

    FIELDS = [
        "Artist",           # Pembuat / Penulis
        "ImageDescription",  # Judul / Deskripsi
        "Copyright",        # Hak Cipta
        "Software",         # Perangkat Lunak
        "DateTimeOriginal"  # Tanggal & Waktu Asli (format: YYYY:MM:DD HH:MM:SS)
    ]

    def _get_output_path(self, file_path: str, inplace: bool) -> str:
        if inplace:
            return file_path
        base, ext = os.path.splitext(file_path)
        return f"{base}_edited{ext}"

    def get_editable_fields(self, file_path: str) -> Dict[str, str]:
        results = {f: "" for f in self.FIELDS}
        try:
            exif_dict = piexif.load(file_path)
            zeroth = exif_dict.get("0th", {})
            exif = exif_dict.get("Exif", {})

            def decode_val(v):
                if isinstance(v, bytes):
                    try:
                        return v.decode("utf-8", errors="replace").strip("\x00")
                    except Exception:
                        return str(v)
                return str(v) if v is not None else ""

            if piexif.ImageIFD.Artist in zeroth:
                results["Artist"] = decode_val(zeroth[piexif.ImageIFD.Artist])
            if piexif.ImageIFD.ImageDescription in zeroth:
                results["ImageDescription"] = decode_val(zeroth[piexif.ImageIFD.ImageDescription])
            if piexif.ImageIFD.Copyright in zeroth:
                results["Copyright"] = decode_val(zeroth[piexif.ImageIFD.Copyright])
            if piexif.ImageIFD.Software in zeroth:
                results["Software"] = decode_val(zeroth[piexif.ImageIFD.Software])
            if piexif.ExifIFD.DateTimeOriginal in exif:
                results["DateTimeOriginal"] = decode_val(exif[piexif.ExifIFD.DateTimeOriginal])

        except Exception as e:
            # Fallback jika gambar belum memiliki EXIF sama sekali
            pass

        return results

    def save_fields(self, file_path: str, updated_fields: Dict[str, str], inplace: bool = True) -> Dict[str, Any]:
        output_path = self._get_output_path(file_path, inplace)
        try:
            try:
                exif_dict = piexif.load(file_path)
            except Exception:
                exif_dict = {"0th": {}, "Exif": {}, "GPS": {}, "1st": {}, "thumbnail": None}

            if "0th" not in exif_dict:
                exif_dict["0th"] = {}
            if "Exif" not in exif_dict:
                exif_dict["Exif"] = {}

            # Perbarui hanya field yang ditentukan pengguna, biarkan yang lain tetap utuh
            if "Artist" in updated_fields:
                val = updated_fields["Artist"]
                if val:
                    exif_dict["0th"][piexif.ImageIFD.Artist] = val.encode("utf-8")
                elif piexif.ImageIFD.Artist in exif_dict["0th"]:
                    del exif_dict["0th"][piexif.ImageIFD.Artist]

            if "ImageDescription" in updated_fields:
                val = updated_fields["ImageDescription"]
                if val:
                    exif_dict["0th"][piexif.ImageIFD.ImageDescription] = val.encode("utf-8")
                elif piexif.ImageIFD.ImageDescription in exif_dict["0th"]:
                    del exif_dict["0th"][piexif.ImageIFD.ImageDescription]

            if "Copyright" in updated_fields:
                val = updated_fields["Copyright"]
                if val:
                    exif_dict["0th"][piexif.ImageIFD.Copyright] = val.encode("utf-8")
                elif piexif.ImageIFD.Copyright in exif_dict["0th"]:
                    del exif_dict["0th"][piexif.ImageIFD.Copyright]

            if "Software" in updated_fields:
                val = updated_fields["Software"]
                if val:
                    exif_dict["0th"][piexif.ImageIFD.Software] = val.encode("utf-8")
                elif piexif.ImageIFD.Software in exif_dict["0th"]:
                    del exif_dict["0th"][piexif.ImageIFD.Software]

            if "DateTimeOriginal" in updated_fields:
                val = updated_fields["DateTimeOriginal"]
                if val:
                    exif_dict["Exif"][piexif.ExifIFD.DateTimeOriginal] = val.encode("utf-8")
                elif piexif.ExifIFD.DateTimeOriginal in exif_dict["Exif"]:
                    del exif_dict["Exif"][piexif.ExifIFD.DateTimeOriginal]

            exif_bytes = piexif.dump(exif_dict)

            # Jika bukan inplace, salin berkas terlebih dahulu
            if not inplace and output_path != file_path:
                shutil.copy2(file_path, output_path)

            ext = os.path.splitext(output_path)[1].lower()
            if ext in [".jpg", ".jpeg", ".tiff", ".tif"]:
                piexif.insert(exif_bytes, output_path)
            else:
                # Untuk PNG atau format lain
                with Image.open(file_path) as img:
                    img.save(output_path, exif=exif_bytes)

            return {
                "success": True,
                "output_path": output_path,
                "error": None
            }
        except Exception as e:
            return {
                "success": False,
                "output_path": None,
                "error": str(e)
            }

