"""
MetaClean — Cleaner Dispatcher
"""
from typing import Dict, Any, Optional
from src.cleaners.image_cleaner import ImageCleaner
from src.cleaners.pdf_cleaner import PdfCleaner
from src.cleaners.docx_cleaner import DocxCleaner
from src.cleaners.media_cleaner import MediaCleaner
from src.cleaners.text_cleaner import TextCleaner

ALL_CLEANERS = [
    ImageCleaner(),
    PdfCleaner(),
    DocxCleaner(),
    MediaCleaner(),
    TextCleaner()
]

def clean_file(input_path: str, output_path: Optional[str] = None, inplace: bool = False) -> Dict[str, Any]:
    """Mendeteksi jenis file dan menjalankan cleaner yang sesuai (mendukung in-place)."""
    for cleaner in ALL_CLEANERS:
        if cleaner.can_clean(input_path):
            return cleaner.clean(input_path, output_path, inplace=inplace)

    return {
        "success": False,
        "input_path": input_path,
        "error": "Format berkas tidak didukung untuk pembersihan otomatis."
    }
