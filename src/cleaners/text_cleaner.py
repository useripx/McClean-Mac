"""
MetaClean — Markdown & Coding Files Cleaner
Membersihkan karakter watermark tersembunyi (Zero-Width Chars, Variation Selectors U+FE0F, Steganografi AI)
dari berkas Markdown (.md), HTML, CSS, JavaScript, Python, PHP, dan seluruh berkas bahasa pemrograman.
Mendukung pembersihan di tempat (in-place) maupun penyimpanan sebagai berkas salinan baru.
"""
import os
import re
from typing import Dict, Any, Optional
from src.cleaners.base import BaseCleaner
from src.utils.scanner import ALL_TEXT_AND_CODE_EXTENSIONS
from src.watermarks.ai_cleaner import RE_INVISIBLE_CHARS, is_invisible_char, get_char_name

class TextCleaner(BaseCleaner):
    SUPPORTED_EXTS = ALL_TEXT_AND_CODE_EXTENSIONS

    def can_clean(self, file_path: str) -> bool:
        return os.path.splitext(file_path)[1].lower() in self.SUPPORTED_EXTS

    def clean(self, input_path: str, output_path: Optional[str] = None, inplace: bool = False) -> Dict[str, Any]:
        if not os.path.exists(input_path):
            return {"success": False, "error": f"Berkas tidak ditemukan: {input_path}"}

        if inplace or output_path == input_path:
            is_inplace = True
            output_path = input_path
            temp_output = f"{input_path}.tmp_clean"
        else:
            is_inplace = False
            if output_path is None:
                dirname, filename = os.path.split(input_path)
                name, ext = os.path.splitext(filename)
                output_path = os.path.join(dirname, f"{name}_clean{ext}")
            temp_output = output_path

        orig_size = os.path.getsize(input_path)

        try:
            # 1. Baca isi berkas dengan decoding bertingkat
            content = None
            for enc in ["utf-8", "utf-8-sig", "latin-1", "cp1252"]:
                try:
                    with open(input_path, "r", encoding=enc) as f:
                        content = f.read()
                    break
                except UnicodeDecodeError:
                    continue

            if content is None:
                with open(input_path, "r", encoding="utf-8", errors="replace") as f:
                    content = f.read()

            # 2. Hitung statistik karakter watermark sebelum dibersihkan
            removed_breakdown = {}
            total_removed = 0
            for char in content:
                cp = ord(char)
                if is_invisible_char(cp):
                    name = get_char_name(cp)
                    removed_breakdown[name] = removed_breakdown.get(name, 0) + 1
                    total_removed += 1

            # 3. Bersihkan seluruh invisible characters menggunakan regex
            cleaned_content = RE_INVISIBLE_CHARS.sub("", content)

            # 4. Tulis berkas hasil pembersihan (newline="" mempertahankan format asli)
            with open(temp_output, "w", encoding="utf-8", newline="") as f_out:
                f_out.write(cleaned_content)

            # Jika in-place, gantikan berkas asli secara atomik
            if is_inplace:
                os.replace(temp_output, input_path)

            cleaned_size = os.path.getsize(output_path)
            return {
                "success": True,
                "input_path": input_path,
                "output_path": output_path,
                "inplace": is_inplace,
                "original_size_bytes": orig_size,
                "cleaned_size_bytes": cleaned_size,
                "watermarks_removed": total_removed,
                "breakdown": removed_breakdown,
                "message": f"Berhasil membersihkan {total_removed} karakter watermark tersembunyi/steganografi."
            }

        except Exception as e:
            if is_inplace and os.path.exists(temp_output):
                try:
                    os.remove(temp_output)
                except Exception:
                    pass
            return {
                "success": False,
                "input_path": input_path,
                "error": f"Gagal membersihkan berkas teks/coding: {str(e)}"
            }
