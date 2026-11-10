"""
MetaClean — DOCX Document Inspector
Mengekstrak informasi Penulis Asli, Editor Terakhir, Revisi, dan Tanggal Dokumen Word (.docx).
"""
import os
from typing import Dict, Any
from docx import Document
from src.inspectors.base import BaseInspector

class DocxInspector(BaseInspector):
    def can_inspect(self, file_path: str) -> bool:
        return os.path.splitext(file_path)[1].lower() == ".docx"

    def inspect(self, file_path: str) -> Dict[str, Any]:
        result = {
            "file_path": file_path,
            "file_name": os.path.basename(file_path),
            "file_size": os.path.getsize(file_path) if os.path.exists(file_path) else 0,
            "category": "docx",
            "has_metadata": False,
            "metadata_count": 0,
            "categories": {},
            "has_ai_watermark": False,
            "watermarks_detected": []
        }

        try:
            doc = Document(file_path)
            core_props = doc.core_properties
            prop_data = {}

            fields = [
                ("Penulis (Author)", core_props.author),
                ("Editor Terakhir", core_props.last_modified_by),
                ("Judul", core_props.title),
                ("Subjek", core_props.subject),
                ("Kata Kunci", core_props.keywords),
                ("Kategori", core_props.category),
                ("Komentar", core_props.comments),
                ("Nomor Revisi", str(core_props.revision) if core_props.revision else None),
                ("Tanggal Dibuat", str(core_props.created) if core_props.created else None),
                ("Tanggal Terakhir Diubah", str(core_props.modified) if core_props.modified else None),
                ("Terakhir Dicetak", str(core_props.last_printed) if core_props.last_printed else None),
            ]

            for label, val in fields:
                if val:
                    prop_data[label] = str(val)

            if prop_data:
                result["categories"]["Properti Dokumen Word"] = prop_data

            result["metadata_count"] = len(prop_data)
            result["has_metadata"] = len(prop_data) > 0

        except Exception as e:
            result["categories"]["Error"] = {"Pesan": f"Gagal membaca dokumen DOCX: {str(e)}"}

        return result

