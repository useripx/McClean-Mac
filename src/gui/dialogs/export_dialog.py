"""
Dialog Pilihan Format Ekspor Laporan untuk Mrclean
Menyediakan antarmuka modal dengan Radio Button untuk memilih format PDF atau Markdown (.md).
"""

import customtkinter as ctk
from typing import Optional

class ExportFormatDialog(ctk.CTkToplevel):
    """Jendela modal untuk memilih format ekspor laporan (PDF atau Markdown)."""

    def __init__(self, parent):
        super().__init__(parent)
        self.title("Ekspor Laporan Hasil Analisis")
        self.geometry("420x280")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        self.selected_format: Optional[str] = None
        self.var_format = ctk.StringVar(value="pdf")

        self._build_ui()
        self.center_window(parent)

    def center_window(self, parent):
        self.update_idletasks()
        try:
            px = parent.winfo_x()
            py = parent.winfo_y()
            pw = parent.winfo_width()
            ph = parent.winfo_height()
            w = 420
            h = 280
            x = px + (pw - w) // 2
            y = py + (ph - h) // 2
            self.geometry(f"{w}x{h}+{x}+{y}")
        except Exception:
            pass

    def _build_ui(self):
        # Header Box
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=(18, 10))

        ctk.CTkLabel(
            header,
            text="💾 Pilih Format Berkas Laporan",
            font=ctk.CTkFont(size=15, weight="bold")
        ).pack(anchor="w")

        ctk.CTkLabel(
            header,
            text="Tentukan format dokumen hasil analisis metadata yang ingin disimpan:",
            font=ctk.CTkFont(size=11),
            text_color="gray"
        ).pack(anchor="w", pady=(2, 0))

        # Radio Group Frame
        opt_frame = ctk.CTkFrame(self, corner_radius=8)
        opt_frame.pack(fill="x", padx=20, pady=10)

        # Radio 1: PDF
        r1 = ctk.CTkRadioButton(
            opt_frame,
            text="Dokumen PDF (.pdf)",
            variable=self.var_format,
            value="pdf",
            font=ctk.CTkFont(size=13, weight="bold")
        )
        r1.pack(anchor="w", padx=16, pady=(12, 2))

        ctk.CTkLabel(
            opt_frame,
            text="Laporan formal siap cetak berlogo resmi, tabel berwarna & kartu per berkas.",
            font=ctk.CTkFont(size=10),
            text_color="#94a3b8"
        ).pack(anchor="w", padx=40, pady=(0, 8))

        # Radio 2: Markdown
        r2 = ctk.CTkRadioButton(
            opt_frame,
            text="Berkas Markdown (.md)",
            variable=self.var_format,
            value="md",
            font=ctk.CTkFont(size=13, weight="bold")
        )
        r2.pack(anchor="w", padx=16, pady=(4, 2))

        ctk.CTkLabel(
            opt_frame,
            text="Tabel GitHub-flavored Markdown terstruktur, cocok untuk repositori & catatan.",
            font=ctk.CTkFont(size=10),
            text_color="#94a3b8"
        ).pack(anchor="w", padx=40, pady=(0, 12))

        # Action Buttons
        btn_box = ctk.CTkFrame(self, fg_color="transparent")
        btn_box.pack(fill="x", padx=20, pady=(10, 15))

        btn_cancel = ctk.CTkButton(
            btn_box,
            text="Batal",
            fg_color="#334155",
            hover_color="#475569",
            width=90,
            command=self._on_cancel
        )
        btn_cancel.pack(side="left")

        btn_submit = ctk.CTkButton(
            btn_box,
            text="Lanjutkan Ekspor →",
            fg_color="#0284c7",
            hover_color="#0369a1",
            width=140,
            command=self._on_submit
        )
        btn_submit.pack(side="right")

    def _on_cancel(self):
        self.selected_format = None
        self.destroy()

    def _on_submit(self):
        self.selected_format = self.var_format.get()
        self.destroy()

