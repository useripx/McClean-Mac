"""
MetaClean — PDF Document Inspector
Mengekstrak informasi Penulis, Software Pembuat, Tanggal Pembuatan/Modifikasi, dan XMP metadata pada PDF.
"""
import os
from typing import Dict, Any
from pypdf import PdfReader
from src.inspectors.base import BaseInspector

class PdfInspector(BaseInspector):
    def can_inspect(self, file_path: str) -> bool:
        return os.path.splitext(file_path)[1].lower() == ".pdf"

    def inspect(self, file_path: str) -> Dict[str, Any]:
        result = {
            "file_path": file_path,
            "file_name": os.path.basename(file_path),
            "file_size": os.path.getsize(file_path) if os.path.exists(file_path) else 0,
            "category": "pdf",
            "has_metadata": False,
            "metadata_count": 0,
            "categories": {},
            "has_ai_watermark": False,
            "watermarks_detected": []
        }

        try:
            reader = PdfReader(file_path)
            doc_info = {
                "Jumlah Halaman": len(reader.pages),
                "Terenkripsi": "Ya" if reader.is_encrypted else "Tidak"
            }
            result["categories"]["Informasi Dokumen"] = doc_info

            meta_dict = {}
            if reader.metadata:
                for k, v in reader.metadata.items():
                    clean_key = k.lstrip("/")
                    str_val = str(v)
                    meta_dict[clean_key] = str_val
                    
                    # Deteksi jejak AI generator
                    lower_val = str_val.lower()
                    if any(term in lower_val for term in ["chatgpt", "openai", "claude", "anthropic", "midjourney", "c2pa"]):
                        result["has_ai_watermark"] = True
                        result["watermarks_detected"].append(f"AI Provenance tag pada {clean_key}: {str_val}")

            # Cek XMP Metadata bila ada
            try:
                if hasattr(reader, "xmp_metadata") and reader.xmp_metadata:
                    meta_dict["XMP Metadata"] = "Tersedia (Data XML terstruktur)"
            except Exception:
                pass

            if meta_dict:
                result["categories"]["Metadata Penulis & Aplikasi"] = meta_dict

            result["metadata_count"] = len(meta_dict)
            result["has_metadata"] = len(meta_dict) > 0

        except Exception as e:
            result["categories"]["Error"] = {"Pesan": f"Gagal membaca berkas PDF: {str(e)}"}

        return result

