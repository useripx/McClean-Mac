"""
MetaClean — Metadata Report Exporter
Mengekspor hasil analisis metadata ke format JSON atau TXT terstruktur.
"""
import json
import os
from typing import List, Dict, Any

def export_to_json(data: List[Dict[str, Any]], output_path: str) -> bool:
    """Mengekspor daftar metadata ke berkas JSON."""
    try:
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except Exception:
        return False

def export_to_text(data: List[Dict[str, Any]], output_path: str) -> bool:
    """Mengekspor laporan metadata ke berkas teks laporan (.txt) yang mudah dibaca."""
    try:
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        lines = []
        lines.append("=" * 70)
        lines.append("METACLEAN — LAPORAN ANALISIS METADATA & AI WATERMARK")
        lines.append("=" * 70)
        lines.append(f"Total Berkas Diperiksa: {len(data)}\n")

        for idx, item in enumerate(data, 1):
            lines.append(f"[{idx}] {item.get('file_name', 'Tanpa Nama')}")
            lines.append(f"     Lokasi      : {item.get('file_path')}")
            lines.append(f"     Kategori    : {item.get('category')}")
            lines.append(f"     Ukuran      : {item.get('file_size', 0)} bytes")
            lines.append(f"     Ada Metadata: {'YA' if item.get('has_metadata') else 'TIDAK'}")
            lines.append(f"     Ada Watermark AI: {'YA' if item.get('has_ai_watermark') else 'TIDAK'}")

            wm_list = item.get("watermarks_detected", [])
            if wm_list:
                lines.append("     Watermark Terdeteksi:")
                for wm in wm_list:
                    lines.append(f"       - {wm}")

            categories = item.get("categories", {})
            for cat_name, cat_vals in categories.items():
                lines.append(f"     --- {cat_name} ---")
                if isinstance(cat_vals, dict):
                    for k, v in cat_vals.items():
                        lines.append(f"       * {k}: {v}")
                else:
                    lines.append(f"       * {cat_vals}")
            lines.append("-" * 70)

        with open(output_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        return True
    except Exception:
        return False

