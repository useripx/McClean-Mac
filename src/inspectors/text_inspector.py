"""
MetaClean — Text, Markdown & Code Watermark Inspector
Mendeteksi karakter tak kasat mata (Zero-Width Chars, Variation Selectors, Steganography)
yang kerap digunakan model AI (ChatGPT, Claude) untuk melacak asal teks maupun kode pemrograman.
"""
import os
from typing import Dict, Any
from src.inspectors.base import BaseInspector
from src.utils.scanner import ALL_TEXT_AND_CODE_EXTENSIONS, get_file_category

INVISIBLE_CODEPOINTS = {
    0x200B: "Zero-Width Space (U+200B)",
    0x200C: "Zero-Width Non-Joiner (U+200C)",
    0x200D: "Zero-Width Joiner (U+200D)",
    0x200E: "Left-to-Right Mark (U+200E)",
    0x200F: "Right-to-Left Mark (U+200F)",
    0x202A: "Left-to-Right Embedding (U+202A)",
    0x202B: "Right-to-Left Embedding (U+202B)",
    0x202C: "Pop Directional Formatting (U+202C)",
    0x202D: "Left-to-Right Override (U+202D)",
    0x202E: "Right-to-Left Override (U+202E)",
    0x2060: "Word Joiner (U+2060)",
    0x2061: "Function Application (U+2061)",
    0x2062: "Invisible Times (U+2062)",
    0x2063: "Invisible Separator (U+2063)",
    0x2064: "Invisible Plus (U+2064)",
    0xFEFF: "Zero-Width No-Break Space / BOM (U+FEFF)",
    0x180E: "Mongolian Vowel Separator (U+180E)",
}

def is_invisible_char(cp: int) -> bool:
    """Mengecek apakah suatu kode poin termasuk karakter tak terlihat / variasi watermark."""
    if cp in INVISIBLE_CODEPOINTS:
        return True
    # Variation Selectors (U+FE00 - U+FE0F, termasuk U+FE0F Variation Selector-16)
    if 0xFE00 <= cp <= 0xFE0F:
        return True
    # Variation Selectors Supplement (U+E0100 - U+E01EF)
    if 0xE0100 <= cp <= 0xE01EF:
        return True
    # Unicode Tags Block (U+E0000 - U+E007F)
    if 0xE0000 <= cp <= 0xE007F:
        return True
    return False

def get_char_name(cp: int) -> str:
    if cp in INVISIBLE_CODEPOINTS:
        return INVISIBLE_CODEPOINTS[cp]
    if 0xFE00 <= cp <= 0xFE0F:
        return f"Variation Selector-{cp - 0xFE00 + 1} (U+{cp:04X})"
    if 0xE0000 <= cp <= 0xE007F:
        return f"Tag Character (U+{cp:05X})"
    return f"Invisible Character (U+{cp:04X})"

class TextInspector(BaseInspector):
    SUPPORTED_EXTS = ALL_TEXT_AND_CODE_EXTENSIONS

    def can_inspect(self, file_path: str) -> bool:
        return os.path.splitext(file_path)[1].lower() in self.SUPPORTED_EXTS

    def inspect_text(self, text_content: str, source_name: str = "Teks Langsung") -> Dict[str, Any]:
        """Menganalisis string teks atau kode pemrograman langsung."""
        char_counts = {}
        total_invisibles = 0

        for char in text_content:
            cp = ord(char)
            if is_invisible_char(cp):
                name = get_char_name(cp)
                char_counts[name] = char_counts.get(name, 0) + 1
                total_invisibles += 1

        has_wm = total_invisibles > 0
        categories = {
            "Statistik Teks": {
                "Total Karakter": len(text_content),
                "Total Karakter Terlihat": len(text_content) - total_invisibles,
                "Total Karakter Tak Kasat Mata": total_invisibles
            }
        }

        if has_wm:
            categories["Rincian Watermark Tersembunyi"] = {
                k: f"{v} karakter ditemukan" for k, v in char_counts.items()
            }

        return {
            "file_name": source_name,
            "category": "text",
            "has_metadata": has_wm,
            "metadata_count": total_invisibles,
            "categories": categories,
            "has_ai_watermark": has_wm,
            "watermarks_detected": [f"{v}x {k}" for k, v in char_counts.items()] if has_wm else []
        }

    def inspect(self, file_path: str) -> Dict[str, Any]:
        category = get_file_category(file_path)
        result = {
            "file_path": file_path,
            "file_name": os.path.basename(file_path),
            "file_size": os.path.getsize(file_path) if os.path.exists(file_path) else 0,
            "category": category,
            "has_metadata": False,
            "metadata_count": 0,
            "categories": {},
            "has_ai_watermark": False,
            "watermarks_detected": []
        }

        try:
            # Baca dengan penanganan encoding bertingkat (UTF-8, UTF-8 dengan BOM, fallback Latin-1)
            content = None
            for enc in ["utf-8", "utf-8-sig", "latin-1", "cp1252"]:
                try:
                    with open(file_path, "r", encoding=enc) as f:
                        content = f.read()
                    break
                except UnicodeDecodeError:
                    continue

            if content is None:
                with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                    content = f.read()

            text_analysis = self.inspect_text(content, os.path.basename(file_path))
            result.update(text_analysis)
            result["category"] = category
            result["file_path"] = file_path
            result["file_size"] = os.path.getsize(file_path)

        except Exception as e:
            result["categories"]["Error"] = {"Pesan": f"Gagal membaca teks/kode: {str(e)}"}

        return result
