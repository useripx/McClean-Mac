"""
Editor Metadata Dokumen Word (.docx) untuk Mrclean
Mendukung penyuntingan selektif properti dokumen (Author, Title, Subject, Keywords, Category, Comments)
secara preservative tanpa merusak struktur dan konten dokumen.
"""

import os
from typing import Dict, Any
from docx import Document
from src.editors.base import BaseMetadataEditor

class DocxEditor(BaseMetadataEditor):
    """Editor metadata selektif untuk dokumen Word (.docx)."""

    FIELDS = ["Author", "Title", "Subject", "Keywords", "Category", "Comments"]

    def _get_output_path(self, file_path: str, inplace: bool) -> str:
        if inplace:
            return file_path
        base, ext = os.path.splitext(file_path)
        return f"{base}_edited{ext}"

    def get_editable_fields(self, file_path: str) -> Dict[str, str]:
        results = {f: "" for f in self.FIELDS}
        try:
            doc = Document(file_path)
            cp = doc.core_properties
            results["Author"] = str(cp.author or "")
            results["Title"] = str(cp.title or "")
            results["Subject"] = str(cp.subject or "")
            results["Keywords"] = str(cp.keywords or "")
            results["Category"] = str(cp.category or "")
            results["Comments"] = str(cp.comments or "")
        except Exception as e:
            print(f"[WARN] DocxEditor.get_editable_fields: {e}")
        return results

    def save_fields(self, file_path: str, updated_fields: Dict[str, str], inplace: bool = True) -> Dict[str, Any]:
        output_path = self._get_output_path(file_path, inplace)
        temp_path = f"{output_path}.tmp_docx"
        try:
            doc = Document(file_path)
            cp = doc.core_properties

            if "Author" in updated_fields:
                cp.author = updated_fields["Author"]
            if "Title" in updated_fields:
                cp.title = updated_fields["Title"]
            if "Subject" in updated_fields:
                cp.subject = updated_fields["Subject"]
            if "Keywords" in updated_fields:
                cp.keywords = updated_fields["Keywords"]
            if "Category" in updated_fields:
                cp.category = updated_fields["Category"]
            if "Comments" in updated_fields:
                cp.comments = updated_fields["Comments"]

            doc.save(temp_path)

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

