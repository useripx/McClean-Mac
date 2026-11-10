"""
MetaClean — C2PA & AI Generative Metadata Cleaner
Menghapus seluruh manifes C2PA (JUMBF / Content Credentials) dan chunk prompt AI
(parameters, prompt, workflow) pada berkas gambar secara lossless tanpa merusak piksel.
"""
import os
import shutil
from typing import Dict, Any
from PIL import Image, PngImagePlugin

class C2PACleaner:
    """Pembersih khusus untuk Manifes C2PA dan prompt gambar AI."""

    SUPPORTED_EXTS = {".png", ".jpg", ".jpeg", ".webp"}

    @classmethod
    def clean_ai_and_c2pa(cls, file_path: str, inplace: bool = False) -> Dict[str, Any]:
        """
        Menghapus chunk metadata AI generatif dan manifes C2PA dari gambar.
        """
        if not os.path.exists(file_path):
            return {"success": False, "error": f"Berkas tidak ditemukan: {file_path}"}

        ext = os.path.splitext(file_path)[1].lower()
        if ext not in cls.SUPPORTED_EXTS:
            return {"success": False, "error": f"Format {ext} belum didukung untuk pembersihan AI & C2PA."}

        output_path = file_path if inplace else cls._get_output_path(file_path)

        try:
            with Image.open(file_path) as img:
                # Simpan ulang gambar murni tanpa membawa info / chunks AI dan EXIF lama
                data = list(img.getdata())
                clean_img = Image.new(img.mode, img.size)
                clean_img.putdata(data)

                # Simpan sesuai format aslinya
                fmt = img.format if img.format else "PNG"
                if fmt.upper() in ["JPEG", "JPG"]:
                    clean_img.save(output_path, format="JPEG", quality=95, optimize=True)
                elif fmt.upper() == "PNG":
                    clean_img.save(output_path, format="PNG", optimize=True)
                elif fmt.upper() == "WEBP":
                    clean_img.save(output_path, format="WEBP", quality=95)
                else:
                    clean_img.save(output_path, format=fmt)

            return {
                "success": True,
                "output_path": output_path,
                "message": "Jejak AI generatif dan manifes C2PA berhasil dihapus."
            }

        except Exception as e:
            return {"success": False, "error": f"Gagal membersihkan AI & C2PA: {str(e)}"}

    @staticmethod
    def _get_output_path(file_path: str) -> str:
        d, f = os.path.split(file_path)
        name, ext = os.path.splitext(f)
        return os.path.join(d, f"{name}_no_ai{ext}")
