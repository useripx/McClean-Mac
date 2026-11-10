"""
MetaClean — File & Folder Scanner Utility
Mendukung pemindaian berkas tunggal (per file) maupun seluruh isi direktori (batch folder scan),
mencakup berkas dokumen, gambar, audio/video, markdown, dan seluruh format kode pemrograman (HTML, JS, Python, dll.).
"""
import os
from typing import List, Dict, Any

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".tiff", ".tif", ".bmp", ".gif"}
PDF_EXTENSIONS = {".pdf"}
DOCX_EXTENSIONS = {".docx"}
MEDIA_EXTENSIONS = {".mp3", ".mp4", ".m4a", ".wav", ".flac", ".ogg", ".mkv", ".avi", ".wma"}

MARKDOWN_EXTENSIONS = {".md", ".markdown"}
TEXT_EXTENSIONS = {".txt", ".log", ".csv"}

CODING_EXTENSIONS = {
    # Web Front-End
    ".html", ".htm", ".css", ".scss", ".sass", ".less",
    ".js", ".jsx", ".ts", ".tsx", ".vue", ".svelte",
    # Back-End & General Languages
    ".py", ".pyw", ".php", ".phtml",
    ".java", ".c", ".cpp", ".cc", ".cxx", ".h", ".hpp", ".cs",
    ".go", ".rs", ".rb", ".swift", ".kt", ".kts", ".dart",
    # Data, Config & Database
    ".json", ".xml", ".yaml", ".yml", ".toml", ".ini", ".sql",
    # Shell Scripts
    ".sh", ".bash", ".bat", ".cmd", ".ps1"
}

ALL_TEXT_AND_CODE_EXTENSIONS = MARKDOWN_EXTENSIONS | TEXT_EXTENSIONS | CODING_EXTENSIONS

ALL_SUPPORTED_EXTENSIONS = (
    IMAGE_EXTENSIONS
    | PDF_EXTENSIONS
    | DOCX_EXTENSIONS
    | MEDIA_EXTENSIONS
    | ALL_TEXT_AND_CODE_EXTENSIONS
)

def get_file_category(file_path: str) -> str:
    """Mengembalikan kategori berkas berdasarkan ekstensinya."""
    ext = os.path.splitext(file_path)[1].lower()
    if ext in IMAGE_EXTENSIONS:
        return "image"
    elif ext in PDF_EXTENSIONS:
        return "pdf"
    elif ext in DOCX_EXTENSIONS:
        return "docx"
    elif ext in MEDIA_EXTENSIONS:
        return "media"
    elif ext in MARKDOWN_EXTENSIONS:
        return "markdown"
    elif ext in CODING_EXTENSIONS:
        return "coding"
    elif ext in TEXT_EXTENSIONS:
        return "text"
    return "unknown"

def scan_files(paths: List[str], recursive: bool = True) -> List[Dict[str, Any]]:
    """
    Menerima daftar path yang bisa berupa berkas individual atau folder.
    Mengembalikan daftar objek info berkas yang terdeteksi.
    """
    discovered_files = []
    seen_paths = set()

    for path in paths:
        if not os.path.exists(path):
            continue

        if os.path.isfile(path):
            abs_path = os.path.abspath(path)
            if abs_path not in seen_paths:
                seen_paths.add(abs_path)
                category = get_file_category(abs_path)
                discovered_files.append({
                    "path": abs_path,
                    "name": os.path.basename(abs_path),
                    "category": category,
                    "size_bytes": os.path.getsize(abs_path),
                    "extension": os.path.splitext(abs_path)[1].lower()
                })
        elif os.path.isdir(path):
            for root, _, files in os.walk(path):
                for file in files:
                    file_path = os.path.abspath(os.path.join(root, file))
                    if file_path in seen_paths:
                        continue

                    ext = os.path.splitext(file)[1].lower()
                    if ext in ALL_SUPPORTED_EXTENSIONS:
                        seen_paths.add(file_path)
                        discovered_files.append({
                            "path": file_path,
                            "name": file,
                            "category": get_file_category(file_path),
                            "size_bytes": os.path.getsize(file_path),
                            "extension": ext
                        })
                if not recursive:
                    break

    return discovered_files
