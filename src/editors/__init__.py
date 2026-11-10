"""
Dispatcher Metadata Editor untuk Mrclean
Mengidentifikasi tipe berkas dan menyediakan editor metadata selektif yang sesuai.
"""

import os
from typing import Optional
from src.editors.base import BaseMetadataEditor
from src.editors.image_editor import ImageEditor
from src.editors.pdf_editor import PdfEditor
from src.editors.docx_editor import DocxEditor
from src.editors.media_editor import MediaEditor

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".tiff", ".tif", ".webp"}
PDF_EXTENSIONS = {".pdf"}
DOCX_EXTENSIONS = {".docx"}
MEDIA_EXTENSIONS = {".mp3", ".mp4", ".m4a", ".flac", ".ogg", ".wav"}

def get_editor_for_file(file_path: str) -> Optional[BaseMetadataEditor]:
    """Mengembalikan instance editor yang sesuai untuk berkas tertentu."""
    if not file_path or not os.path.exists(file_path):
        return None

    ext = os.path.splitext(file_path)[1].lower()
    if ext in IMAGE_EXTENSIONS:
        return ImageEditor()
    elif ext in PDF_EXTENSIONS:
        return PdfEditor()
    elif ext in DOCX_EXTENSIONS:
        return DocxEditor()
    elif ext in MEDIA_EXTENSIONS:
        return MediaEditor()
    return None

def is_editable_file(file_path: str) -> bool:
    """Mengecek apakah format berkas mendukung penyuntingan metadata selektif."""
    if not file_path:
        return False
    ext = os.path.splitext(file_path)[1].lower()
    return ext in (IMAGE_EXTENSIONS | PDF_EXTENSIONS | DOCX_EXTENSIONS | MEDIA_EXTENSIONS)

