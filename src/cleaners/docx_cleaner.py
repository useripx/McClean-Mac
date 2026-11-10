"""
MetaClean — DOCX Metadata Cleaner
Menghapus riwayat penulis, editor terakhir, komentar, dan tanggal pada dokumen Word (.docx).
Mendukung pembersihan langsung di tempat (in-place) maupun berkas salinan baru.
"""
import os
from typing import Dict, Any, Optional
from docx import Document
from src.cleaners.base import BaseCleaner

class DocxCleaner(BaseCleaner):
    def can_clean(self, file_path: str) -> bool:
        return os.path.splitext(file_path)[1].lower() == ".docx"

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
            doc = Document(input_path)

            if hasattr(doc, "core_properties") and hasattr(doc.core_properties, "_element"):
                elem = doc.core_properties._element
                for child in list(elem):
                    elem.remove(child)

            doc.save(temp_output)

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
                "message": "Metadata dokumen Word (.docx) berhasil dibersihkan."
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
                "error": f"Gagal membersihkan DOCX: {str(e)}"
            }
