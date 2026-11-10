"""
Engine Pembuat Laporan PDF (.pdf) untuk Mrclean
Menghasilkan dokumen laporan profesional siap cetak dengan logo resmi,
tabel ringkasan berpewarna modern, dan rincian metadata per berkas.
"""

import os
import sys
from datetime import datetime
from typing import List, Dict, Any

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage, KeepTogether
)

class PDFExporter:
    """Menyusun dan mengekspor data hasil pemindaian metadata ke berkas PDF formal."""

    @staticmethod
    def _find_logo_path() -> str:
        candidates = []
        if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
            candidates.append(os.path.join(sys._MEIPASS, "assets", "logo.png"))
        candidates.append(os.path.abspath("assets/logo.png"))
        candidates.append(os.path.abspath("Material/logo.jpg"))

        for p in candidates:
            if os.path.exists(p):
                return p
        return ""

    @classmethod
    def export(cls, scanned_items: List[Dict[str, Any]], output_path: str) -> bool:
        """Mengekspor daftar item hasil pemindaian ke dokumen PDF."""
        try:
            os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
            doc = SimpleDocTemplate(
                output_path,
                pagesize=A4,
                leftMargin=36,
                rightMargin=36,
                topMargin=36,
                bottomMargin=36
            )

            styles = getSampleStyleSheet()
            
            # Custom Styles
            title_style = ParagraphStyle(
                'DocTitle',
                parent=styles['Heading1'],
                fontSize=18,
                leading=22,
                textColor=colors.HexColor("#1e293b"),
                spaceAfter=4
            )
            subtitle_style = ParagraphStyle(
                'DocSubTitle',
                parent=styles['Normal'],
                fontSize=9,
                leading=12,
                textColor=colors.HexColor("#64748b")
            )
            section_heading = ParagraphStyle(
                'SectionHead',
                parent=styles['Heading2'],
                fontSize=12,
                leading=16,
                textColor=colors.HexColor("#0f172a"),
                spaceBefore=12,
                spaceAfter=6
            )
            table_cell = ParagraphStyle(
                'TableCell',
                parent=styles['Normal'],
                fontSize=8,
                leading=10,
                textColor=colors.HexColor("#334155")
            )
            table_head = ParagraphStyle(
                'TableHead',
                parent=styles['Normal'],
                fontSize=8,
                leading=10,
                fontName="Helvetica-Bold",
                textColor=colors.white
            )
            code_cell = ParagraphStyle(
                'CodeCell',
                parent=styles['Normal'],
                fontSize=7.5,
                leading=9,
                fontName="Courier",
                textColor=colors.HexColor("#0f172a")
            )

            elements = []

            # 1. Header (Logo & Title)
            logo_path = cls._find_logo_path()
            header_table_data = []
            
            now_str = datetime.now().strftime("%d %B %Y, %H:%M:%S")
            info_text = (
                f"<b>Mrclean</b> — Offline Metadata & AI Watermarks Remover<br/>"
                f"Waktu Laporan: {now_str} | Total Berkas: {len(scanned_items)}"
            )

            if logo_path:
                try:
                    logo_img = RLImage(logo_path, width=42, height=42)
                    header_table_data = [[
                        logo_img,
                        [
                            Paragraph("Laporan Analisis Metadata & Tanda Air AI", title_style),
                            Paragraph(info_text, subtitle_style)
                        ]
                    ]]
                except Exception:
                    header_table_data = [[
                        Paragraph("Laporan Analisis Metadata & Tanda Air AI", title_style),
                        Paragraph(info_text, subtitle_style)
                    ]]
            else:
                header_table_data = [[
                    Paragraph("Laporan Analisis Metadata & Tanda Air AI", title_style),
                    Paragraph(info_text, subtitle_style)
                ]]

            header_table = Table(header_table_data, colWidths=[50, 470] if logo_path else [520])
            header_table.setStyle(TableStyle([
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ]))
            elements.append(header_table)
            elements.append(Spacer(1, 10))

            # 2. Ringkasan Statistik
            total_files = len(scanned_items)
            meta_count = sum(1 for item in scanned_items if item.get("has_metadata"))
            wm_count = sum(1 for item in scanned_items if item.get("has_ai_watermark"))
            clean_count = sum(1 for item in scanned_items if not item.get("has_metadata") and not item.get("has_ai_watermark"))

            stat_data = [
                [
                    Paragraph("<b>Kategori Status</b>", table_head),
                    Paragraph("<b>Jumlah Berkas</b>", table_head),
                    Paragraph("<b>Persentase</b>", table_head)
                ],
                [
                    Paragraph("🟢 Berkas Bersih (Bebas Metadata & WM)", table_cell),
                    Paragraph(str(clean_count), table_cell),
                    Paragraph(f"{(clean_count / total_files * 100):.1f}%" if total_files else "0%", table_cell)
                ],
                [
                    Paragraph("⚠️ Terdeteksi Menyimpan Metadata", table_cell),
                    Paragraph(str(meta_count), table_cell),
                    Paragraph(f"{(meta_count / total_files * 100):.1f}%" if total_files else "0%", table_cell)
                ],
                [
                    Paragraph("🤖 Terdeteksi Tanda Air / Steganografi AI", table_cell),
                    Paragraph(str(wm_count), table_cell),
                    Paragraph(f"{(wm_count / total_files * 100):.1f}%" if total_files else "0%", table_cell)
                ],
                [
                    Paragraph("<b>Total Seluruh Berkas</b>", table_cell),
                    Paragraph(f"<b>{total_files}</b>", table_cell),
                    Paragraph("<b>100.0%</b>", table_cell)
                ]
            ]
            stat_table = Table(stat_data, colWidths=[260, 130, 130])
            stat_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1e293b")),
                ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
                ('ROWBACKGROUNDS', (0, 1), (-1, -2), [colors.white, colors.HexColor("#f8fafc")]),
                ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor("#e2e8f0")),
                ('TOPPADDING', (0, 0), (-1, -1), 4),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ]))
            elements.append(Paragraph("1. Ringkasan Statistik Global", section_heading))
            elements.append(stat_table)
            elements.append(Spacer(1, 10))

            # 3. Tabel Ikhtisar Berkas
            elements.append(Paragraph("2. Ikhtisar Berkas Terperiksa", section_heading))
            overview_data = [[
                Paragraph("<b>No</b>", table_head),
                Paragraph("<b>Nama Berkas</b>", table_head),
                Paragraph("<b>Kategori</b>", table_head),
                Paragraph("<b>Ukuran</b>", table_head),
                Paragraph("<b>Risiko Privasi</b>", table_head),
                Paragraph("<b>Status Metadata</b>", table_head),
                Paragraph("<b>Status AI-WM</b>", table_head)
            ]]

            for idx, it in enumerate(scanned_items, start=1):
                name = it.get("file_name", "Unknown")
                cat = it.get("category", "-").upper()
                sz_kb = it.get("file_size", 0) / 1024
                sz_str = f"{sz_kb:.1f} KB" if sz_kb < 1024 else f"{(sz_kb / 1024):.2f} MB"
                
                meta_str = "⚠️ Metadata" if it.get("has_metadata") else "✅ Bersih"
                wm_str = "🤖 AI-WM" if it.get("has_ai_watermark") else "✅ Bersih"

                risk = it.get("risk_assessment")
                if not risk:
                    from src.inspectors.risk_scorer import calculate_privacy_risk
                    risk = calculate_privacy_risk(it)
                r_score = risk.get("score", 0)
                r_lvl = risk.get("level", "AMAN")
                r_color = "#b91c1c" if r_lvl == "KRITIS" else ("#d97706" if r_lvl == "SEDANG" else "#15803d")
                risk_p = Paragraph(f"<font color='{r_color}'><b>{r_score}% {r_lvl}</b></font>", table_cell)

                overview_data.append([
                    Paragraph(str(idx), table_cell),
                    Paragraph(name, table_cell),
                    Paragraph(cat, table_cell),
                    Paragraph(sz_str, table_cell),
                    risk_p,
                    Paragraph(meta_str, table_cell),
                    Paragraph(wm_str, table_cell)
                ])

            ov_table = Table(overview_data, colWidths=[20, 160, 60, 55, 75, 75, 75])
            ov_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#0f172a")),
                ('ALIGN', (0, 0), (0, -1), 'CENTER'),
                ('ALIGN', (2, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
                ('TOPPADDING', (0, 0), (-1, -1), 3),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
            ]))
            elements.append(ov_table)
            elements.append(Spacer(1, 12))

            # 4. Rincian Detail per Berkas
            elements.append(Paragraph("3. Rincian Detail Metadata per Berkas", section_heading))
            for idx, it in enumerate(scanned_items, start=1):
                file_blocks = []
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
                r_color = "#b91c1c" if r_lvl == "KRITIS" else ("#d97706" if r_lvl == "SEDANG" else "#15803d")

                title_p = Paragraph(f"<b>{idx}. {name}</b> ({cat} | {sz_kb:.1f} KB | <font color='{r_color}'><b>{r_score}% {r_lvl}</b></font>)", ParagraphStyle(
                    'ItemTitle', parent=styles['Heading3'], fontSize=10, textColor=colors.HexColor("#1e40af"), spaceBefore=6, spaceAfter=2
                ))
                path_p = Paragraph(f"Lokasi: {path}", ParagraphStyle(
                    'ItemPath', parent=styles['Normal'], fontSize=7.5, textColor=colors.HexColor("#64748b"), spaceAfter=4
                ))
                file_blocks.append(title_p)
                file_blocks.append(path_p)

                if it.get("has_ai_watermark"):
                    wm_info = it.get("ai_watermark_details", {})
                    wm_text = f"<b>⚠️ Tanda Air AI Terdeteksi:</b> {wm_info}"
                    wm_p = Paragraph(wm_text, ParagraphStyle(
                        'WMAlert', parent=styles['Normal'], fontSize=8, textColor=colors.HexColor("#b91c1c"), spaceAfter=4
                    ))
                    file_blocks.append(wm_p)

                metadata = it.get("metadata", {})
                if metadata:
                    for section_name, section_data in metadata.items():
                        sec_head = Paragraph(f"<b>Tag {section_name}</b>", ParagraphStyle(
                            'SecHead', parent=styles['Normal'], fontSize=8.5, fontName="Helvetica-Bold", textColor=colors.HexColor("#334155"), spaceBefore=2, spaceAfter=2
                        ))
                        file_blocks.append(sec_head)

                        if isinstance(section_data, dict):
                            rows = [[
                                Paragraph("<b>Property / Tag</b>", table_head),
                                Paragraph("<b>Value</b>", table_head)
                            ]]
                            for k, v in section_data.items():
                                val_str = str(v).replace("\n", " ")
                                if len(val_str) > 120:
                                    val_str = val_str[:117] + "..."
                                rows.append([
                                    Paragraph(str(k), table_cell),
                                    Paragraph(val_str, code_cell)
                                ])
                            t = Table(rows, colWidths=[160, 360])
                            t.setStyle(TableStyle([
                                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#475569")),
                                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
                                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
                                ('TOPPADDING', (0, 0), (-1, -1), 2),
                                ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
                            ]))
                            file_blocks.append(t)
                            file_blocks.append(Spacer(1, 4))
                else:
                    file_blocks.append(Paragraph("<i>(Tidak ada metadata sensitif yang terdeteksi)</i>", table_cell))
                    file_blocks.append(Spacer(1, 4))

                elements.append(KeepTogether(file_blocks))

            doc.build(elements)
            return True
        except Exception as e:
            print(f"[ERROR] PDFExporter.export: {e}")
            return False

