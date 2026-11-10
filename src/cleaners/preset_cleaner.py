"""
MetaClean — Quick Clean Presets
Menyediakan profil pembersihan otomatis sekali klik berdasarkan skenario penggunaan:
1. Media Sosial (Hapus GPS & Identitas Perangkat, amankan orientasi & profil sRGB).
2. Akademik (Hapus Author, Institusi, Komentar, dan Steganografi AI pada dokumen).
3. Developer / Open Source (Hapus Path Lokal, Header Author, dan Karakter Zero-Width pada kode).
"""
import os
import re
from typing import Dict, Any, List
from src.cleaners import clean_file
from src.watermarks.ai_cleaner import AIWatermarkCleaner
from src.cleaners.image_cleaner import ImageCleaner
from src.cleaners.docx_cleaner import DocxCleaner
from src.cleaners.pdf_cleaner import PdfCleaner
from src.cleaners.text_cleaner import TextCleaner

class PresetCleaner:
    """Pengelola profil pembersihan cepat (Quick Presets)."""

    PRESETS = {
        "social_media": {
            "name": "📱 Media Sosial",
            "desc": "Menghapus GPS, Serial Number & Identitas Kamera, mengamankan profil warna & orientasi."
        },
        "academic": {
            "name": "🎓 Dokumen Akademik",
            "desc": "Menghapus Author, Institusi, Riwayat Revisi, serta Watermark Steganografi AI."
        },
        "developer": {
            "name": "💻 Developer / OSS",
            "desc": "Menghapus Path Folder Lokal, Header Author, dan Karakter Zero-Width pada berkas kode."
        }
    }

    @classmethod
    def clean_with_preset(cls, file_path: str, preset_key: str, inplace: bool = False) -> Dict[str, Any]:
        """
        Menjalankan pembersihan berkas sesuai profil preset yang dipilih.
        """
        if not os.path.exists(file_path):
            return {"success": False, "error": f"Berkas tidak ditemukan: {file_path}"}

        ext = os.path.splitext(file_path)[1].lower()

        if preset_key == "social_media":
            # Preset Media Sosial: Pembersihan metadata gambar/media
            if ext in ImageCleaner.SUPPORTED_EXTS:
                res = ImageCleaner().clean(file_path, inplace=inplace)
                # Pastikan tanda air C2PA juga dibersihkan
                AIWatermarkCleaner.clean_file(file_path if inplace else res.get("output_path", file_path), inplace=True)
                return res
            else:
                return clean_file(file_path, inplace=inplace)

        elif preset_key == "academic":
            # Preset Akademik: Bersihkan metadata dokumen + Steganografi AI
            clean_res = clean_file(file_path, inplace=inplace)
            target = file_path if inplace else clean_res.get("output_path", file_path)
            if os.path.exists(target):
                AIWatermarkCleaner.clean_file(target, inplace=True)
            return clean_res

        elif preset_key == "developer":
            # Preset Developer: Bersihkan watermark AI dan bersihkan path lokal jika teks/kode
            target_work = file_path if inplace else cls._get_output_path(file_path)
            if not inplace:
                import shutil
                shutil.copy2(file_path, target_work)

            # 1. Bersihkan tanda air AI
            AIWatermarkCleaner.clean_file(target_work, inplace=True)

            # 2. Bersihkan path lokal seperti C:\Users\xxx
            if ext in TextCleaner.SUPPORTED_EXTS:
                try:
                    with open(target_work, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read()
                    
                    # Samarkan path Windows, Linux, dan macOS menggunakan lambda agar bebas escape error
                    sanitized = re.sub(r"[A-Za-z]:\\[Uu]sers\\[^\\]+", lambda m: "C:\\Users\\User", content)
                    sanitized = re.sub(r"/home/[^/\s]+", lambda m: "/home/user", sanitized)
                    sanitized = re.sub(r"/Users/[^/\s]+", lambda m: "/Users/user", sanitized)
                    
                    with open(target_work, "w", encoding="utf-8") as f:
                        f.write(sanitized)
                except Exception:
                    pass

            return {"success": True, "output_path": target_work}

        else:
            # Fallback standar
            return clean_file(file_path, inplace=inplace)

    @staticmethod
    def _get_output_path(file_path: str) -> str:
        d, f = os.path.split(file_path)
        name, ext = os.path.splitext(f)
        return os.path.join(d, f"{name}_clean{ext}")
