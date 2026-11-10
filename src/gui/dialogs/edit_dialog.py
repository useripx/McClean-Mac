"""
Dialog Edit Metadata Interaktif untuk Mrclean
Menyediakan form modal yang terisi otomatis dengan nilai metadata saat ini,
memungkinkan pengguna mengubah field tertentu saja (misal Author) tanpa mengubah tag lain.
"""

import os
from tkinter import messagebox
import customtkinter as ctk
from typing import Optional, Dict, Any
from src.editors.base import BaseMetadataEditor

class MetadataEditDialog(ctk.CTkToplevel):
    """Jendela modal penyuntingan metadata selektif untuk berkas terpilih."""

    def __init__(self, parent, file_path: str, editor: BaseMetadataEditor):
        super().__init__(parent)
        self.file_path = file_path
        self.editor = editor
        self.result: Optional[Dict[str, Any]] = None

        self.title(f"Edit Metadata — {os.path.basename(file_path)}")
        self.geometry("520x460")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        # Ambil nilai asli saat ini
        self.original_fields = self.editor.get_editable_fields(file_path)
        self.entry_widgets: Dict[str, ctk.CTkEntry] = {}
        self.var_inplace = ctk.BooleanVar(value=True)

        self._build_ui()
        self.center_window(parent)

    def center_window(self, parent):
        self.update_idletasks()
        try:
            px = parent.winfo_x()
            py = parent.winfo_y()
            pw = parent.winfo_width()
            ph = parent.winfo_height()
            w = 520
            h = 460
            x = px + (pw - w) // 2
            y = py + (ph - h) // 2
            self.geometry(f"{w}x{h}+{x}+{y}")
        except Exception:
            pass

    def _build_ui(self):
        # 1. Header Info Card
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=(15, 5))

        ctk.CTkLabel(
            header,
            text=f"✏️ Edit Metadata Berkas",
            font=ctk.CTkFont(size=15, weight="bold")
        ).pack(anchor="w")

        file_name = os.path.basename(self.file_path)
        ctk.CTkLabel(
            header,
            text=f"Berkas: {file_name}",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#38bdf8"
        ).pack(anchor="w", pady=(2, 0))

        ctk.CTkLabel(
            header,
            text="Ubah hanya nilai yang diinginkan (misal Author saja). Nilai lain tetap dipertahankan.",
            font=ctk.CTkFont(size=10),
            text_color="gray"
        ).pack(anchor="w")

        # 2. Form Scrollable Frame
        form_frame = ctk.CTkScrollableFrame(self, height=240, corner_radius=8)
        form_frame.pack(fill="both", expand=True, padx=20, pady=8)

        # Label terjemahan yang ramah pengguna
        label_aliases = {
            "Artist": "Author / Pembuat (Artist):",
            "Author": "Penulis Dokumen (Author):",
            "ImageDescription": "Judul / Deskripsi Gambar:",
            "Title": "Judul (Title):",
            "Subject": "Subjek Dokumen (Subject):",
            "Keywords": "Kata Kunci (Keywords):",
            "Creator": "Aplikasi Pembuat (Creator):",
            "Category": "Kategori (Category):",
            "Comments": "Komentar (Comments):",
            "Copyright": "Hak Cipta (Copyright):",
            "Software": "Perangkat Lunak (Software):",
            "DateTimeOriginal": "Tanggal Asli (YYYY:MM:DD HH:MM:SS):",
            "Album": "Nama Album:",
            "Date": "Tahun / Tanggal Rilis:",
            "Genre": "Genre Musik / Video:"
        }

        for field_name, original_val in self.original_fields.items():
            row = ctk.CTkFrame(form_frame, fg_color="transparent")
            row.pack(fill="x", padx=10, pady=5)

            disp_label = label_aliases.get(field_name, f"{field_name}:")
            ctk.CTkLabel(
                row,
                text=disp_label,
                font=ctk.CTkFont(size=11, weight="bold"),
                anchor="w",
                width=190
            ).pack(side="left")

            entry = ctk.CTkEntry(row, font=ctk.CTkFont(size=11))
            entry.pack(side="left", fill="x", expand=True)
            if original_val:
                entry.insert(0, original_val)

            # Dukungan Pintasan Keyboard macOS (⌘ Command) & Windows (Ctrl)
            entry.bind("<Command-c>", lambda e, w=entry: w.event_generate("<<Copy>>"))
            entry.bind("<Command-v>", lambda e, w=entry: w.event_generate("<<Paste>>"))
            entry.bind("<Command-a>", lambda e, w=entry: w.event_generate("<<SelectAll>>"))

            self.entry_widgets[field_name] = entry

        # 3. Mode In-Place Checkbox
        opt_box = ctk.CTkFrame(self, fg_color="transparent")
        opt_box.pack(fill="x", padx=20, pady=4)

        chk = ctk.CTkCheckBox(
            opt_box,
            text="Simpan Langsung di Tempat (Timpa Berkas Asli)",
            variable=self.var_inplace,
            font=ctk.CTkFont(size=11)
        )
        chk.pack(anchor="w")

        # 4. Action Buttons
        btn_box = ctk.CTkFrame(self, fg_color="transparent")
        btn_box.pack(fill="x", padx=20, pady=(10, 15))

        btn_cancel = ctk.CTkButton(
            btn_box,
            text="Batal",
            fg_color="#334155",
            hover_color="#475569",
            width=80,
            command=self._on_cancel
        )
        btn_cancel.pack(side="left")

        btn_reset = ctk.CTkButton(
            btn_box,
            text="Reset ke Semula",
            fg_color="#475569",
            hover_color="#64748b",
            width=120,
            command=self._on_reset
        )
        btn_reset.pack(side="left", padx=8)

        btn_save = ctk.CTkButton(
            btn_box,
            text="Simpan Perubahan 💾",
            fg_color="#10b981",
            hover_color="#059669",
            width=150,
            command=self._on_save
        )
        btn_save.pack(side="right")

    def _on_reset(self):
        for field_name, original_val in self.original_fields.items():
            if field_name in self.entry_widgets:
                ent = self.entry_widgets[field_name]
                ent.delete(0, "end")
                if original_val:
                    ent.insert(0, original_val)

    def _on_cancel(self):
        self.result = None
        self.destroy()

    def _on_save(self):
        updated = {}
        for field_name, entry in self.entry_widgets.items():
            updated[field_name] = entry.get().strip()

        inplace = bool(self.var_inplace.get())
        res = self.editor.save_fields(self.file_path, updated, inplace=inplace)

        if res.get("success"):
            self.result = {
                "success": True,
                "inplace": inplace,
                "output_path": res.get("output_path"),
                "updated_fields": updated
            }
            self.destroy()
        else:
            err = res.get("error", "Terjadi kesalahan saat menyimpan perubahan.")
            messagebox.showerror("Gagal Menyimpan", f"Gagal memperbarui metadata:\n{err}", parent=self)

