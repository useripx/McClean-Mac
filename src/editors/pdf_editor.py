"""
Editor Metadata PDF untuk Mrclean
Mendukung penyuntingan selektif metadata dokumen PDF (Author, Title, Subject, Keywords, Creator)
secara preservative tanpa merusak struktur dokumen atau halaman.
"""

import os
from typing import Dict, Any
from pypdf import PdfReader, PdfWriter
from src.editors.base import BaseMetadataEditor

class PdfEditor(BaseMetadataEditor):
    """Editor metadata selektif untuk dokumen PDF."""

    FIELDS = ["Author", "Title", "Subject", "Keywords", "Creator"]

    def _get_output_path(self, file_path: str, inplace: bool) -> str:
        if inplace:
            return file_path
        base, ext = os.path.splitext(file_path)
        return f"{base}_edited{ext}"

    def get_editable_fields(self, file_path: str) -> Dict[str, str]:
        results = {f: "" for f in self.FIELDS}
        try:
            reader = PdfReader(file_path)
            meta = reader.metadata
            if meta:
                results["Author"] = str(meta.author or "")
                results["Title"] = str(meta.title or "")
                results["Subject"] = str(meta.subject or "")
                results["Keywords"] = str(meta.get("/Keywords", "") or "")
                results["Creator"] = str(meta.creator or "")
        except Exception as e:
            print(f"[WARN] PdfEditor.get_editable_fields: {e}")
        return results

    def save_fields(self, file_path: str, updated_fields: Dict[str, str], inplace: bool = True) -> Dict[str, Any]:
        output_path = self._get_output_path(file_path, inplace)
        temp_path = f"{output_path}.tmp_pdf"
        try:
            reader = PdfReader(file_path)
            writer = PdfWriter()

            for page in reader.pages:
                writer.add_page(page)

            # Salin metadata asli yang ada
            new_meta = {}
            if reader.metadata:
                for k, v in reader.metadata.items():
                    if v is not None:
                        new_meta[str(k)] = str(v)

            # Perbarui hanya field yang diminta pengguna
            field_map = {
                "Author": "/Author",
                "Title": "/Title",
                "Subject": "/Subject",
                "Keywords": "/Keywords",
                "Creator": "/Creator"
            }

            for field_name, pdf_key in field_map.items():
                if field_name in updated_fields:
                    val = updated_fields[field_name]
                    if val:
                        new_meta[pdf_key] = val
                    elif pdf_key in new_meta:
                        del new_meta[pdf_key]

            writer.add_metadata(new_meta)

            with open(temp_path, "wb") as f:
                writer.write(f)

            if os.path.exists(output_path):
                os.remove(output_path)
            os.rename(temp_path, output_path)

            return {
                "success": True,
                "output_path": output_path,
                "error": None
            }
        except Exception as e:
            if os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                except Exception:
                    pass
            return {
                "success": False,
                "output_path": None,
                "error": str(e)
            }

