"""
Engine Pembuat Laporan Markdown (.md) untuk Mrclean
Menghasilkan laporan analisis metadata terstruktur dengan tabel GitHub Flavored Markdown.
"""

import os
from datetime import datetime
from typing import List, Dict, Any

class MarkdownExporter:
    """Menyusun dan mengekspor data hasil pemindaian metadata ke format Markdown (.md)."""

    @staticmethod
    def export(scanned_items: List[Dict[str, Any]], output_path: str) -> bool:
        """
        Mengekspor daftar hasil inspeksi ke berkas Markdown.
        """
        try:
            total_files = len(scanned_items)
            meta_count = sum(1 for item in scanned_items if item.get("has_metadata"))
            wm_count = sum(1 for item in scanned_items if item.get("has_ai_watermark"))
            clean_count = sum(1 for item in scanned_items if not item.get("has_metadata") and not item.get("has_ai_watermark"))
            now_str = datetime.now().strftime("%d %B %Y, %H:%M:%S")

            lines = []
            lines.append("# 🛡️ Laporan Inspeksi Metadata & Tanda Air AI — Mrclean")
            lines.append("")
            lines.append(f"> **Tanggal Laporan:** {now_str}  ")
            lines.append(f"> **Aplikasi:** Mrclean (Offline Metadata & AI Watermarks Remover)  ")
            lines.append(f"> **Total Berkas Terperiksa:** {total_files} berkas  ")
            lines.append("")
            lines.append("---")
            lines.append("")
            lines.append("## 📊 1. Ringkasan Statistik Global")
            lines.append("")
            lines.append("| Indikator | Jumlah Berkas | Persentase |")
            lines.append("| :--- | :---: | :---: |")
            
            p_clean = (clean_count / total_files * 100) if total_files else 0
            p_meta = (meta_count / total_files * 100) if total_files else 0
            p_wm = (wm_count / total_files * 100) if total_files else 0

            lines.append(f"| 🟢 **Berkas Bersih (Bebas Metadata & WM)** | {clean_count} | {p_clean:.1f}% |")
            lines.append(f"| ⚠️ **Terdeteksi Menyimpan Metadata Identitas** | {meta_count} | {p_meta:.1f}% |")
            lines.append(f"| 🤖 **Terdeteksi Tanda Air / Steganografi AI** | {wm_count} | {p_wm:.1f}% |")
            lines.append(f"| 📁 **Total Seluruh Berkas** | {total_files} | 100.0% |")
            lines.append("")
            lines.append("---")
            lines.append("")
            lines.append("## 📋 2. Tabel Ikhtisar Berkas")
            lines.append("")
            lines.append("| No | Nama Berkas | Kategori | Ukuran | Risiko Privasi | Status Metadata | Status Watermark AI |")
            lines.append("| :-: | :--- | :---: | :-: | :---: | :---: | :---: |")

            for idx, it in enumerate(scanned_items, start=1):
                name = it.get("file_name", "Unknown")
                cat = it.get("category", "-").upper()
                sz_kb = it.get("file_size", 0) / 1024
                sz_str = f"{sz_kb:.1f} KB" if sz_kb < 1024 else f"{(sz_kb / 1024):.2f} MB"
                
                meta_badge = "⚠️ Metadata" if it.get("has_metadata") else "✅ Bersih"
                wm_badge = "🤖 AI-WM" if it.get("has_ai_watermark") else "✅ Bersih"

                risk = it.get("risk_assessment")
                if not risk:
                    from src.inspectors.risk_scorer import calculate_privacy_risk
                    risk = calculate_privacy_risk(it)
                r_score = risk.get("score", 0)
                r_lvl = risk.get("level", "AMAN")
                r_icon = "🔴" if r_lvl == "KRITIS" else ("🟡" if r_lvl == "SEDANG" else "🟢")
                r_badge = f"{r_icon} {r_score}% {r_lvl}"
                
                lines.append(f"| {idx} | `{name}` | {cat} | {sz_str} | {r_badge} | {meta_badge} | {wm_badge} |")

            lines.append("")
            lines.append("---")
            lines.append("")
            lines.append("## 🔍 3. Rincian Detail Metadata per Berkas")
            lines.append("")

            for idx, it in enumerate(scanned_items, start=1):
                name = it.get("file_name", "Unknown")
                path = it.get("file_path", "-")
                cat = it.get("category", "-").upper()
                sz_kb = it.get("file_size", 0) / 1024

                risk = it.get("risk_assessment")
                if not risk:
                    from src.inspectors.risk_scorer import calculate_privacy_risk
                    risk = calculate_privacy_risk(it)
                r_score = risk.get("score", 0)
                r_lvl = risk.get("level", "AMAN")
                r_icon = "🔴" if r_lvl == "KRITIS" else ("🟡" if r_lvl == "SEDANG" else "🟢")
                r_badge = f"{r_icon} {r_score}% {r_lvl}"
                
                lines.append(f"### 📄 {idx}. {name}")
                lines.append(f"- **Lokasi Berkas:** `{path}`")
                lines.append(f"- **Kategori:** `{cat}` | **Ukuran:** `{sz_kb:.1f} KB` | **Risiko Privasi:** {r_badge}")
                lines.append(f"- **Evaluasi Keamanan:** {risk.get('recommendation', '')}")
                lines.append("")

                if it.get("has_ai_watermark"):
                    lines.append("> [!WARNING]")
                    lines.append("> **Tanda Air / Steganografi AI Terdeteksi pada berkas ini!**")
                    wm_det = it.get("ai_watermark_details", {})
                    if isinstance(wm_det, dict):
                        for k, v in wm_det.items():
                            lines.append(f"> - **{k}:** {v}")
                    else:
                        lines.append(f"> - {wm_det}")
                    lines.append("")

                metadata = it.get("metadata", {})
                if metadata:
                    for section_name, section_data in metadata.items():
                        lines.append(f"#### 🏷️ {section_name}")
                        if isinstance(section_data, dict):
                            lines.append("| Properti / Tag | Nilai |")
                            lines.append("| :--- | :--- |")
                            for k, v in section_data.items():
                                val_clean = str(v).replace("\n", " ").replace("|", "\\|")
                                lines.append(f"| **{k}** | `{val_clean}` |")
                            lines.append("")
                        else:
                            lines.append(f"- `{section_data}`")
                            lines.append("")
                else:
                    lines.append("*(Tidak ada metadata sensitif yang terdeteksi)*")
                    lines.append("")

            os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
            with open(output_path, "w", encoding="utf-8", newline="") as f:
                f.write("\n".join(lines))

            return True
        except Exception as e:
            print(f"[ERROR] MarkdownExporter.export: {e}")
            return False

