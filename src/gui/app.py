"""
MetaClean — Modern Desktop GUI
Antarmuka pengguna grafis berbasis CustomTkinter dengan dukungan Dark/Light mode,
pemindaian berkas tunggal & batch satu folder, inspeksi detail, pembersihan instan,
dan dukungan pembersihan di tempat (In-Place Cleaning) untuk menimpa berkas asli secara aman.
"""
import os
import sys
import threading
from tkinter import filedialog, messagebox
import customtkinter as ctk
from PIL import Image

from src.utils.scanner import scan_files
from src.inspectors import inspect_file
from src.cleaners import clean_file
from src.watermarks import AIWatermarkCleaner
from src.utils.md_exporter import MarkdownExporter
from src.utils.pdf_exporter import PDFExporter
from src.gui.dialogs.export_dialog import ExportFormatDialog
from src.gui.dialogs.edit_dialog import MetadataEditDialog
from src.editors import get_editor_for_file, is_editable_file
from src.cleaners.preset_cleaner import PresetCleaner
from src.cleaners.c2pa_cleaner import C2PACleaner
from src.editors.spoofing import MetadataSpoofer
from src.utils.shell_integration import WindowsShellIntegration
from src.utils.mac_shell_integration import MacShellIntegration

try:
    import darkdetect
except ImportError:
    darkdetect = None

IS_MAC = (sys.platform == "darwin")
APP_FONT_FAMILY = ".AppleSystemUIFont" if IS_MAC else "Segoe UI"

# Pengaturan Default Tema
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

def get_asset_path(filename: str) -> str:
    """Mendapatkan path absolut aset, baik saat running via script maupun PyInstaller .exe."""
    if hasattr(sys, '_MEIPASS'):
        p = os.path.join(sys._MEIPASS, "assets", filename)
        if os.path.exists(p):
            return p
        p_root = os.path.join(sys._MEIPASS, filename)
        if os.path.exists(p_root):
            return p_root

    # Mode pengembangan lokal
    local_p = os.path.abspath(os.path.join("assets", filename))
    if os.path.exists(local_p):
        return local_p

    # Fallback ke direktori proyek
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    return os.path.join(base_dir, "assets", filename)

class MetaCleanApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("MrClean Mac — Offline Metadata & AI Watermarks Tool")
        self.geometry("1160x740")
        self.minsize(960, 640)

        # Pintasan Keluar macOS (⌘ Command+Q)
        if IS_MAC:
            self.bind("<Command-q>", lambda e: self.quit())
            self.bind("<Command-w>", lambda e: self.quit())

        # Ikon Aplikasi Window & Taskbar
        icon_path = get_asset_path("icon.ico")
        if os.path.exists(icon_path):
            try:
                self.iconbitmap(icon_path)
            except Exception:
                pass

        # Data State
        self.scanned_items = []  # List of inspection result dicts
        self.selected_item = None
        self.selected_file_paths = set()  # Set of paths of checked files
        self.item_check_vars = {}  # Map file_path -> ctk.BooleanVar
        self.is_processing = False

        self._build_ui()

    def _build_ui(self):
        # 1. Header Frame
        self.header_frame = ctk.CTkFrame(self, corner_radius=10, height=75)
        self.header_frame.pack(fill="x", padx=15, pady=(15, 10))

        # Logo Gambar (assets/logo.png dari Material/logo.jpg)
        logo_path = get_asset_path("logo.png")
        if os.path.exists(logo_path):
            try:
                pil_logo = Image.open(logo_path)
                self.logo_ctk_image = ctk.CTkImage(light_image=pil_logo, dark_image=pil_logo, size=(40, 40))
                self.logo_label = ctk.CTkLabel(self.header_frame, text="", image=self.logo_ctk_image)
                self.logo_label.pack(side="left", padx=(18, 10), pady=10)
            except Exception:
                pass

        # Title & Subtitle
        self.title_label = ctk.CTkLabel(
            self.header_frame,
            text="MrClean Mac",
            font=ctk.CTkFont(family=APP_FONT_FAMILY, size=22, weight="bold")
        )
        self.title_label.pack(side="left", padx=(0, 10), pady=12)

        self.subtitle_label = ctk.CTkLabel(
            self.header_frame,
            text="Pemeriksa & Pembersih Metadata Offline + AI Watermarks Remover (Edisi macOS) | Dikembangkan untuk Yogi Ario",
            font=ctk.CTkFont(family=APP_FONT_FAMILY, size=12),
            text_color="gray"
        )
        self.subtitle_label.pack(side="left", padx=5, pady=12)

        # Appearance Mode Toggle
        self.theme_switch = ctk.CTkSwitch(
            self.header_frame,
            text="Mode Gelap",
            command=self._toggle_theme
        )
        self.theme_switch.select()
        self.theme_switch.pack(side="right", padx=15, pady=12)

        # Windows Explorer Context Menu Toggle Button
        self.btn_shell = ctk.CTkButton(
            self.header_frame,
            text="⚙️ Menu Klik Kanan",
            width=135,
            height=28,
            fg_color="#334155",
            hover_color="#1e293b",
            font=ctk.CTkFont(size=11),
            command=self._toggle_shell_integration
        )
        self.btn_shell.pack(side="right", padx=10, pady=12)
        self._update_shell_button_text()

        # 2. Control & Action Bar (Pilih Berkas / Folder)
        self.control_frame = ctk.CTkFrame(self, corner_radius=8)
        self.control_frame.pack(fill="x", padx=15, pady=5)

        self.btn_add_files = ctk.CTkButton(
            self.control_frame,
            text="📄 Tambah Berkas...",
            width=140,
            command=self._on_choose_files
        )
        self.btn_add_files.pack(side="left", padx=(15, 5), pady=10)

        self.btn_add_folder = ctk.CTkButton(
            self.control_frame,
            text="📁 Pindai 1 Folder...",
            width=150,
            fg_color="#2b7a78",
            hover_color="#205e5c",
            command=self._on_choose_folder
        )
        self.btn_add_folder.pack(side="left", padx=5, pady=10)

        self.chk_recursive = ctk.CTkCheckBox(
            self.control_frame,
            text="Pindai Subfolder"
        )
        self.chk_recursive.select()
        self.chk_recursive.pack(side="left", padx=10, pady=10)

        self.chk_inplace = ctk.CTkCheckBox(
            self.control_frame,
            text="Timpa Berkas Asli Langsung (In-Place)",
            text_color="#80cbc4",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        self.chk_inplace.select()
        self.chk_inplace.pack(side="left", padx=15, pady=10)

        self.btn_clear = ctk.CTkButton(
            self.control_frame,
            text="🗑️ Kosongkan Daftar",
            width=130,
            fg_color="#802b2b",
            hover_color="#5a1e1e",
            command=self._clear_list
        )
        self.btn_clear.pack(side="right", padx=15, pady=10)

        # 3. Main Workspace (Panels: File List on Left, Detail Viewer on Right)
        self.main_paned = ctk.CTkFrame(self, corner_radius=8)
        self.main_paned.pack(fill="both", expand=True, padx=15, pady=5)

        # 3A. Left Panel: File List
        self.left_panel = ctk.CTkFrame(self.main_paned, width=460)
        self.left_panel.pack(side="left", fill="both", expand=False, padx=(5, 5), pady=5)

        self.left_header_frame = ctk.CTkFrame(self.left_panel, fg_color="transparent")
        self.left_header_frame.pack(fill="x", padx=15, pady=(10, 2))

        self.left_header = ctk.CTkLabel(
            self.left_header_frame,
            text="Daftar Berkas Terpindai",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.left_header.pack(side="left")

        # Selection Bar (Master Checkbox "Pilih Semua" & Indikator Jumlah)
        self.selection_bar = ctk.CTkFrame(self.left_panel, fg_color="transparent")
        self.selection_bar.pack(fill="x", padx=15, pady=(2, 6))

        self.var_select_all = ctk.BooleanVar(value=False)
        self.chk_select_all = ctk.CTkCheckBox(
            self.selection_bar,
            text="Pilih Semua",
            font=ctk.CTkFont(size=11),
            width=20,
            checkbox_width=16,
            checkbox_height=16,
            variable=self.var_select_all,
            command=self._toggle_select_all
        )
        self.chk_select_all.pack(side="left")

        self.lbl_selected_count = ctk.CTkLabel(
            self.selection_bar,
            text="(0 terpilih)",
            font=ctk.CTkFont(size=11),
            text_color="gray"
        )
        self.lbl_selected_count.pack(side="left", padx=8)

        self.file_scroll = ctk.CTkScrollableFrame(self.left_panel, width=440)
        self.file_scroll.pack(fill="both", expand=True, padx=10, pady=(5, 10))

        # 3B. Right Panel: Metadata & Watermark Details
        self.right_panel = ctk.CTkFrame(self.main_paned)
        self.right_panel.pack(side="right", fill="both", expand=True, padx=(5, 5), pady=5)

        self.right_header = ctk.CTkLabel(
            self.right_panel,
            text="Detail Hasil Inspeksi Metadata",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.right_header.pack(anchor="w", padx=15, pady=(10, 5))

        self.detail_scroll = ctk.CTkScrollableFrame(self.right_panel)
        self.detail_scroll.pack(fill="both", expand=True, padx=10, pady=(5, 10))

        self._show_empty_detail_message()

        # 4. Bottom Action Bar (Cleaning & Export Actions)
        self.bottom_bar = ctk.CTkFrame(self, corner_radius=8, height=60)
        self.bottom_bar.pack(fill="x", padx=15, pady=(5, 10))

        self.btn_clean_selected = ctk.CTkButton(
            self.bottom_bar,
            text="🛡️ Bersihkan Berkas Terpilih",
            font=ctk.CTkFont(weight="bold"),
            command=self._clean_selected_file
        )
        self.btn_clean_selected.pack(side="left", padx=(15, 8), pady=12)

        self.btn_edit_meta = ctk.CTkButton(
            self.bottom_bar,
            text="✏️ Edit Metadata",
            fg_color="#0284c7",
            hover_color="#0369a1",
            font=ctk.CTkFont(weight="bold"),
            command=self._edit_metadata
        )
        self.btn_edit_meta.pack(side="left", padx=8, pady=12)

        self.btn_clean_all = ctk.CTkButton(
            self.bottom_bar,
            text="⚡ Bersihkan Semua di Folder (Batch)",
            fg_color="#1d7874",
            hover_color="#155d5a",
            font=ctk.CTkFont(weight="bold"),
            command=self._clean_all_files
        )
        self.btn_clean_all.pack(side="left", padx=8, pady=12)

        self.btn_clean_ai = ctk.CTkButton(
            self.bottom_bar,
            text="🤖 Hapus Watermark AI Saja",
            fg_color="#673ab7",
            hover_color="#512da8",
            font=ctk.CTkFont(weight="bold"),
            command=self._clean_ai_watermarks
        )
        self.btn_clean_ai.pack(side="left", padx=8, pady=12)

        self.btn_spoof = ctk.CTkButton(
            self.bottom_bar,
            text="🎭 Samarkan (Spoof)",
            fg_color="#00897b",
            hover_color="#00695c",
            font=ctk.CTkFont(weight="bold"),
            command=self._spoof_metadata_action
        )
        self.btn_spoof.pack(side="left", padx=8, pady=12)

        self.preset_var = ctk.StringVar(value="⚡ Profil Cepat...")
        self.opt_preset = ctk.CTkOptionMenu(
            self.bottom_bar,
            values=["⚡ Profil Cepat...", "📱 Media Sosial", "🎓 Akademik", "💻 Developer/OSS"],
            variable=self.preset_var,
            width=140,
            command=self._apply_preset_action
        )
        self.opt_preset.pack(side="left", padx=8, pady=12)

        self.btn_export = ctk.CTkButton(
            self.bottom_bar,
            text="💾 Ekspor Laporan...",
            fg_color="#37474f",
            hover_color="#263238",
            command=self._export_report
        )
        self.btn_export.pack(side="right", padx=15, pady=12)

        # 5. Status Bar
        self.status_bar = ctk.CTkLabel(
            self,
            text="Siap. Silakan tambahkan berkas atau pilih folder untuk memulai inspeksi.",
            font=ctk.CTkFont(size=11),
            text_color="gray",
            anchor="w"
        )
        self.status_bar.pack(fill="x", padx=20, pady=(0, 8))

    def _toggle_theme(self):
        if self.theme_switch.get():
            ctk.set_appearance_mode("Dark")
            self.theme_switch.configure(text="Mode Gelap")
        else:
            ctk.set_appearance_mode("Light")
            self.theme_switch.configure(text="Mode Terang")

    def _show_empty_detail_message(self):
        for widget in self.detail_scroll.winfo_children():
            widget.destroy()

        msg = ctk.CTkLabel(
            self.detail_scroll,
            text="Pilih salah satu berkas di daftar sebelah kiri\nuntuk melihat rincian metadata dan watermark secara mendalam.",
            font=ctk.CTkFont(size=13),
            text_color="gray",
            justify="center"
        )
        msg.pack(expand=True, pady=120)

    def _on_choose_files(self):
        filetypes = [
            ("Semua Berkas yang Didukung", "*.jpg;*.jpeg;*.png;*.webp;*.pdf;*.docx;*.mp3;*.mp4;*.md;*.txt;*.html;*.js;*.py;*.php;*.java;*.cpp;*.json;*.xml;*.yaml"),
            ("Berkas Markdown (*.md)", "*.md;*.markdown"),
            ("Berkas Kode Pemrograman (*.html, *.js, *.py, dll.)", "*.html;*.htm;*.css;*.js;*.jsx;*.ts;*.tsx;*.py;*.php;*.java;*.c;*.cpp;*.cs;*.go;*.rs;*.json;*.xml;*.yaml;*.sql;*.sh"),
            ("Gambar (JPG, PNG, WEBP)", "*.jpg;*.jpeg;*.png;*.webp;*.tiff;*.bmp"),
            ("Dokumen (PDF, Word)", "*.pdf;*.docx"),
            ("Media (Audio & Video)", "*.mp3;*.mp4;*.wav;*.mkv;*.m4a"),
            ("Seluruh Berkas (*.*)", "*.*")
        ]
        paths = filedialog.askopenfilenames(title="Pilih Berkas untuk Diperiksa", filetypes=filetypes)
        if paths:
            self._process_paths(list(paths))

    def _on_choose_folder(self):
        folder = filedialog.askdirectory(title="Pilih Folder untuk Batch Scan")
        if folder:
            self._process_paths([folder])

    def _process_paths(self, paths):
        if self.is_processing:
            messagebox.showwarning("Peringatan", "Proses pemindaian sedang berjalan, mohon tunggu.")
            return

        self.is_processing = True
        self.status_bar.configure(text="⏳ Sedang memindai berkas & memeriksa metadata...")

        def worker():
            recursive = bool(self.chk_recursive.get())
            discovered = scan_files(paths, recursive=recursive)

            new_results = []
            for item in discovered:
                info = inspect_file(item["path"])
                new_results.append(info)

            # Update UI on main thread
            self.after(0, lambda: self._on_scan_completed(new_results))

        threading.Thread(target=worker, daemon=True).start()

    def _on_scan_completed(self, new_results):
        self.is_processing = False
        self.scanned_items.extend(new_results)
        self._refresh_file_list()

        total = len(self.scanned_items)
        has_meta = sum(1 for x in self.scanned_items if x.get("has_metadata"))
        has_wm = sum(1 for x in self.scanned_items if x.get("has_ai_watermark"))

        self.status_bar.configure(
            text=f"Selesai memindai. Total: {total} berkas | {has_meta} berkas memiliki metadata | {has_wm} berkas terindikasi watermark AI"
        )

    def _refresh_file_list(self):
        for widget in self.file_scroll.winfo_children():
            widget.destroy()

        self.item_check_vars.clear()

        # Bersihkan path yang sudah tidak ada di scanned_items
        valid_paths = {it.get("file_path") for it in self.scanned_items if it.get("file_path")}
        self.selected_file_paths = {p for p in self.selected_file_paths if p in valid_paths}

        if not self.scanned_items:
            empty_lbl = ctk.CTkLabel(
                self.file_scroll,
                text="Belum ada berkas yang dimuat.",
                text_color="gray"
            )
            empty_lbl.pack(pady=40)
            self._show_empty_detail_message()
            self._update_selection_counter()
            return

        for idx, item in enumerate(self.scanned_items):
            file_path = item.get("file_path")
            is_checked = file_path in self.selected_file_paths
            var = ctk.BooleanVar(value=is_checked)
            self.item_check_vars[file_path] = var

            item_frame = ctk.CTkFrame(self.file_scroll, corner_radius=6)
            item_frame.pack(fill="x", padx=5, pady=4)

            # Checkbox pemilihan berkas individual
            chk = ctk.CTkCheckBox(
                item_frame,
                text="",
                width=20,
                checkbox_width=18,
                checkbox_height=18,
                variable=var,
                command=lambda p=file_path: self._on_item_check_toggle(p)
            )
            chk.pack(side="left", padx=(8, 2), pady=6)

            # Left indicators
            category = item.get("category", "file").upper()
            cat_badge = ctk.CTkLabel(
                item_frame,
                text=f"[{category}]",
                font=ctk.CTkFont(size=10, weight="bold"),
                text_color="#64b5f6"
            )
            cat_badge.pack(side="left", padx=(2, 4), pady=6)

            name = item.get("file_name", "Unknown")
            if len(name) > 24:
                display_name = name[:21] + "..."
            else:
                display_name = name

            btn_select = ctk.CTkButton(
                item_frame,
                text=display_name,
                fg_color="transparent",
                hover_color="#333333",
                anchor="w",
                font=ctk.CTkFont(size=12),
                command=lambda it=item: self._on_item_click(it)
            )
            btn_select.pack(side="left", fill="x", expand=True, padx=4)

            # Badges
            if item.get("has_ai_watermark"):
                wm_badge = ctk.CTkLabel(
                    item_frame,
                    text="🤖 AI-WM",
                    font=ctk.CTkFont(size=10, weight="bold"),
                    text_color="#e040fb"
                )
                wm_badge.pack(side="right", padx=6)

            if item.get("has_metadata"):
                meta_badge = ctk.CTkLabel(
                    item_frame,
                    text="⚠️ Metadata",
                    font=ctk.CTkFont(size=10),
                    text_color="#ffb74d"
                )
                meta_badge.pack(side="right", padx=4)
            else:
                clean_badge = ctk.CTkLabel(
                    item_frame,
                    text="✅ Bersih",
                    font=ctk.CTkFont(size=10),
                    text_color="#81c784"
                )
                clean_badge.pack(side="right", padx=4)

            # Privacy Risk Badge
            risk = item.get("risk_assessment") or {}
            risk_score = risk.get("score", 0)
            risk_level = risk.get("level", "AMAN")
            risk_color = risk.get("color", "#43a047")
            r_icon = "🔴" if risk_level == "KRITIS" else ("🟡" if risk_level == "SEDANG" else "🟢")

            risk_badge = ctk.CTkLabel(
                item_frame,
                text=f"{r_icon} {risk_score}%",
                font=ctk.CTkFont(size=10, weight="bold"),
                text_color=risk_color
            )
            risk_badge.pack(side="right", padx=(4, 6))

        self._update_selection_counter()

    def _on_item_click(self, item):
        self._display_detail(item)

    def _on_item_check_toggle(self, file_path):
        var = self.item_check_vars.get(file_path)
        if var:
            if var.get():
                self.selected_file_paths.add(file_path)
            else:
                self.selected_file_paths.discard(file_path)
        self._update_selection_counter()

    def _toggle_select_all(self):
        select_all = bool(self.var_select_all.get())
        if select_all:
            for it in self.scanned_items:
                p = it.get("file_path")
                if p:
                    self.selected_file_paths.add(p)
            for var in self.item_check_vars.values():
                var.set(True)
        else:
            self.selected_file_paths.clear()
            for var in self.item_check_vars.values():
                var.set(False)

        self._update_selection_counter()

    def _update_selection_counter(self):
        count = len(self.selected_file_paths)
        total = len(self.scanned_items)
        if hasattr(self, 'lbl_selected_count'):
            self.lbl_selected_count.configure(text=f"({count} dari {total} terpilih)")

        if hasattr(self, 'var_select_all'):
            if total > 0 and count == total:
                self.var_select_all.set(True)
            else:
                self.var_select_all.set(False)

        if hasattr(self, 'btn_clean_selected'):
            if count > 1:
                self.btn_clean_selected.configure(text=f"🛡️ Bersihkan Berkas Terpilih ({count})")
            else:
                self.btn_clean_selected.configure(text="🛡️ Bersihkan Berkas Terpilih")

        if hasattr(self, 'btn_clean_ai'):
            if count > 1:
                self.btn_clean_ai.configure(text=f"🤖 Hapus Watermark AI Saja ({count})")
            else:
                self.btn_clean_ai.configure(text="🤖 Hapus Watermark AI Saja")

    def _display_detail(self, item):
        self.selected_item = item

        for widget in self.detail_scroll.winfo_children():
            widget.destroy()

        # Header Info Card
        card = ctk.CTkFrame(self.detail_scroll, corner_radius=8)
        card.pack(fill="x", padx=5, pady=5)

        ctk.CTkLabel(
            card,
            text=f"📁 {item.get('file_name')}",
            font=ctk.CTkFont(size=15, weight="bold")
        ).pack(anchor="w", padx=12, pady=(10, 2))

        ctk.CTkLabel(
            card,
            text=f"Lokasi: {item.get('file_path')}",
            font=ctk.CTkFont(size=11),
            text_color="gray"
        ).pack(anchor="w", padx=12, pady=2)

        size_kb = item.get("file_size", 0) / 1024
        ctk.CTkLabel(
            card,
            text=f"Ukuran: {size_kb:.1f} KB | Kategori: {item.get('category').upper()}",
            font=ctk.CTkFont(size=11),
            text_color="gray"
        ).pack(anchor="w", padx=12, pady=(2, 10))

        # Privacy Risk Assessment Card
        risk = item.get("risk_assessment") or {}
        risk_score = risk.get("score", 0)
        risk_level = risk.get("level", "AMAN")
        risk_color = risk.get("color", "#43a047")
        risk_reasons = risk.get("reasons", [])
        risk_rec = risk.get("recommendation", "")

        risk_card = ctk.CTkFrame(self.detail_scroll, corner_radius=8, fg_color="#18181b")
        risk_card.pack(fill="x", padx=5, pady=5)

        risk_top = ctk.CTkFrame(risk_card, fg_color="transparent")
        risk_top.pack(fill="x", padx=12, pady=(8, 2))

        ctk.CTkLabel(
            risk_top,
            text=f"🛡️ Skor Risiko Privasi: {risk_score}%",
            font=ctk.CTkFont(size=13, weight="bold")
        ).pack(side="left")

        ctk.CTkLabel(
            risk_top,
            text=f"[{risk_level}]",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=risk_color
        ).pack(side="left", padx=8)

        risk_bar = ctk.CTkProgressBar(risk_card, height=7, corner_radius=4)
        risk_bar.pack(fill="x", padx=12, pady=4)
        risk_bar.set(risk_score / 100.0)
        risk_bar.configure(progress_color=risk_color)

        if risk_reasons:
            for r in risk_reasons:
                ctk.CTkLabel(
                    risk_card,
                    text=f"• {r}",
                    font=ctk.CTkFont(size=10),
                    text_color="#cfd8dc"
                ).pack(anchor="w", padx=16, pady=1)

        ctk.CTkLabel(
            risk_card,
            text=f"💡 Rekomendasi: {risk_rec}",
            font=ctk.CTkFont(size=10, slant="italic"),
            text_color="#90a4ae"
        ).pack(anchor="w", padx=12, pady=(4, 8))

        # AI Watermark Alert Box if present
        if item.get("has_ai_watermark"):
            wm_box = ctk.CTkFrame(self.detail_scroll, corner_radius=8, fg_color="#3e1b4a")
            wm_box.pack(fill="x", padx=5, pady=5)

            ctk.CTkLabel(
                wm_box,
                text="⚠️ Tanda Air AI / Steganografi Terdeteksi!",
                font=ctk.CTkFont(size=13, weight="bold"),
                text_color="#ff80ab"
            ).pack(anchor="w", padx=12, pady=(8, 2))

            for wm in item.get("watermarks_detected", []):
                ctk.CTkLabel(
                    wm_box,
                    text=f"• {wm}",
                    font=ctk.CTkFont(size=11),
                    text_color="#f8bbd0"
                ).pack(anchor="w", padx=20, pady=1)

        # AI Forensics & Prompt Details Card
        ai_f = item.get("ai_forensics") or {}
        if ai_f.get("is_ai_generated") or ai_f.get("prompt"):
            ai_card = ctk.CTkFrame(self.detail_scroll, corner_radius=8, fg_color="#261230")
            ai_card.pack(fill="x", padx=5, pady=5)

            ctk.CTkLabel(
                ai_card,
                text="🎨 Deteksi AI Generatif & Prompt Asli",
                font=ctk.CTkFont(size=13, weight="bold"),
                text_color="#f48fb1"
            ).pack(anchor="w", padx=12, pady=(8, 2))

            if ai_f.get("generator"):
                ctk.CTkLabel(
                    ai_card,
                    text=f"Model: {ai_f.get('generator')}",
                    font=ctk.CTkFont(size=11, weight="bold"),
                    text_color="#ce93d8"
                ).pack(anchor="w", padx=14, pady=1)

            if ai_f.get("prompt"):
                ctk.CTkLabel(
                    ai_card,
                    text=f'Prompt: "{ai_f.get("prompt")}"',
                    font=ctk.CTkFont(size=10, slant="italic"),
                    text_color="#fce4ec",
                    wraplength=430,
                    justify="left"
                ).pack(anchor="w", padx=14, pady=3)

            btn_clean_c2pa = ctk.CTkButton(
                ai_card,
                text="🤖 Hapus Jejak AI & Manifes C2PA",
                height=26,
                fg_color="#8e24aa",
                hover_color="#6a1b9a",
                font=ctk.CTkFont(size=11, weight="bold"),
                command=lambda p=item.get("file_path"): self._clean_ai_and_c2pa_action(p)
            )
            btn_clean_c2pa.pack(anchor="w", padx=12, pady=(4, 8))

        # Categories & Tag Details
        categories = item.get("categories", {})
        if not categories or not item.get("has_metadata"):
            no_meta_lbl = ctk.CTkLabel(
                self.detail_scroll,
                text="✅ Tidak ditemukan metadata sensitif atau berkas sudah bersih murni.",
                font=ctk.CTkFont(size=12),
                text_color="#81c784"
            )
            no_meta_lbl.pack(pady=20)
            return

        for cat_name, cat_data in categories.items():
            cat_frame = ctk.CTkFrame(self.detail_scroll, corner_radius=8)
            cat_frame.pack(fill="x", padx=5, pady=5)

            ctk.CTkLabel(
                cat_frame,
                text=f"🔹 {cat_name}",
                font=ctk.CTkFont(size=13, weight="bold")
            ).pack(anchor="w", padx=12, pady=(8, 4))

            if isinstance(cat_data, dict):
                for k, v in cat_data.items():
                    row = ctk.CTkFrame(cat_frame, fg_color="transparent")
                    row.pack(fill="x", padx=15, pady=2)

                    ctk.CTkLabel(
                        row,
                        text=f"{k}:",
                        font=ctk.CTkFont(size=11, weight="bold"),
                        width=180,
                        anchor="w"
                    ).pack(side="left")

                    ctk.CTkLabel(
                        row,
                        text=str(v),
                        font=ctk.CTkFont(size=11),
                        anchor="w",
                        text_color="#b0bec5",
                        wraplength=400
                    ).pack(side="left", fill="x", expand=True)
            else:
                ctk.CTkLabel(
                    cat_frame,
                    text=str(cat_data),
                    font=ctk.CTkFont(size=11),
                    text_color="#b0bec5"
                ).pack(anchor="w", padx=15, pady=4)

    def _clear_list(self):
        self.scanned_items.clear()
        self.selected_item = None
        self.selected_file_paths.clear()
        self.item_check_vars.clear()
        self._refresh_file_list()
        self.status_bar.configure(text="Daftar berkas telah dikosongkan.")

    def _get_target_selection_paths(self):
        """Mendapatkan daftar path berkas yang akan diproses (dari centang checkbox atau item aktif)."""
        if self.selected_file_paths:
            return [p for p in self.selected_file_paths if os.path.exists(p)]
        elif self.selected_item and os.path.exists(self.selected_item.get("file_path", "")):
            return [self.selected_item.get("file_path")]
        return []

    def _clean_selected_file(self):
        target_paths = self._get_target_selection_paths()
        if not target_paths:
            messagebox.showinfo("Petunjuk", "Silakan centang atau pilih berkas di daftar terlebih dahulu.")
            return

        inplace = bool(self.chk_inplace.get())
        mode_str = "langsung di tempat (menimpa berkas asli)" if inplace else "sebagai salinan baru (<nama>_clean.<ext>)"

        if len(target_paths) == 1:
            path = target_paths[0]
            res = clean_file(path, inplace=inplace)

            if res.get("success"):
                target_path = path if inplace else res.get("output_path")
                new_info = inspect_file(target_path)

                if inplace:
                    # Perbarui data item di daftar secara in-place
                    for idx, it in enumerate(self.scanned_items):
                        if it.get("file_path") == path:
                            self.scanned_items[idx] = new_info
                            break
                else:
                    self.scanned_items.append(new_info)

                self._refresh_file_list()
                self._display_detail(new_info)

                msg_location = "di tempat (berkas asli telah bersih)" if inplace else f"sebagai berkas baru:\n{os.path.basename(target_path)}"
                messagebox.showinfo("Berhasil", f"Metadata & Watermark AI berhasil dibersihkan {msg_location}!")
            else:
                messagebox.showerror("Gagal", res.get("error", "Gagal membersihkan berkas."))
        else:
            # Multi-file batch cleaning untuk berkas yang dicentang
            confirm = messagebox.askyesno(
                "Konfirmasi Pembersihan Berkas Terpilih",
                f"Apakah Anda ingin membersihkan metadata dari {len(target_paths)} berkas yang dicentang?\n\nMode: Pembersihan {mode_str}."
            )
            if not confirm:
                return

            self.status_bar.configure(text=f"⚡ Sedang membersihkan {len(target_paths)} berkas terpilih...")

            def worker():
                success_count = 0
                new_items = []
                for path in target_paths:
                    res = clean_file(path, inplace=inplace)
                    if res.get("success"):
                        success_count += 1
                        target_p = path if inplace else res.get("output_path")
                        cleaned_info = inspect_file(target_p)
                        if inplace:
                            for idx, it in enumerate(self.scanned_items):
                                if it.get("file_path") == path:
                                    self.scanned_items[idx] = cleaned_info
                                    break
                        else:
                            new_items.append(cleaned_info)

                def on_finish():
                    if not inplace:
                        self.scanned_items.extend(new_items)
                    self._refresh_file_list()

                    # Refresh detail jika sedang ada yang dipilih
                    if self.selected_item:
                        sel_path = self.selected_item.get("file_path")
                        for it in self.scanned_items:
                            if it.get("file_path") == sel_path:
                                self._display_detail(it)
                                break

                    msg_location = "di tempat" if inplace else "sebagai salinan baru"
                    self.status_bar.configure(text=f"Pembersihan selesai: {success_count} dari {len(target_paths)} berkas berhasil dibersihkan.")
                    messagebox.showinfo(
                        "Selesai",
                        f"Pembersihan Selesai!\n{success_count} dari {len(target_paths)} berkas terpilih telah dibersihkan {msg_location}."
                    )

                self.after(0, on_finish)

            threading.Thread(target=worker, daemon=True).start()

    def _clean_all_files(self):
        if not self.scanned_items:
            messagebox.showinfo("Petunjuk", "Tidak ada berkas di daftar untuk dibersihkan.")
            return

        inplace = bool(self.chk_inplace.get())
        mode_str = "langsung di tempat (menimpa berkas asli)" if inplace else "sebagai salinan baru (<nama>_clean.<ext>)"
        confirm = messagebox.askyesno(
            "Konfirmasi Pembersihan Batch",
            f"Apakah Anda ingin membersihkan metadata dari {len(self.scanned_items)} berkas?\n\nMode: Pembersihan {mode_str}."
        )
        if not confirm:
            return

        self.status_bar.configure(text="⚡ Sedang membersihkan seluruh berkas...")

        def worker():
            success_count = 0
            new_items = []
            for idx, item in enumerate(self.scanned_items):
                p = item.get("file_path")
                res = clean_file(p, inplace=inplace)
                if res.get("success"):
                    success_count += 1
                    target_p = p if inplace else res.get("output_path")
                    cleaned_info = inspect_file(target_p)
                    if inplace:
                        self.scanned_items[idx] = cleaned_info
                    else:
                        new_items.append(cleaned_info)

            def on_finish():
                if not inplace:
                    self.scanned_items.extend(new_items)
                self._refresh_file_list()

                # Refresh detail jika sedang ada yang dipilih
                if self.selected_item:
                    sel_path = self.selected_item.get("file_path")
                    for it in self.scanned_items:
                        if it.get("file_path") == sel_path:
                            self._display_detail(it)
                            break

                self.status_bar.configure(text=f"Pembersihan batch selesai: {success_count} berkas berhasil dibersihkan.")
                messagebox.showinfo(
                    "Selesai",
                    f"Pembersihan Batch Berhasil!\n{success_count} berkas telah dibersihkan {mode_str}."
                )

            self.after(0, on_finish)

        threading.Thread(target=worker, daemon=True).start()

    def _clean_ai_watermarks(self):
        target_paths = self._get_target_selection_paths()
        if not target_paths:
            messagebox.showinfo("Petunjuk", "Silakan centang atau pilih berkas di daftar untuk dibersihkan watermarknya.")
            return

        inplace = bool(self.chk_inplace.get())
        mode_str = "langsung di tempat" if inplace else "sebagai salinan baru"

        if len(target_paths) == 1:
            path = target_paths[0]
            res = AIWatermarkCleaner.clean_file(path, inplace=inplace)

            if res.get("success"):
                target_path = path if inplace else res.get("output_path")
                wm_count = res.get("watermarks_removed", "Semua")
                new_info = inspect_file(target_path)

                if inplace:
                    for idx, it in enumerate(self.scanned_items):
                        if it.get("file_path") == path:
                            self.scanned_items[idx] = new_info
                            break
                else:
                    self.scanned_items.append(new_info)

                self._refresh_file_list()
                self._display_detail(new_info)

                msg_location = "di tempat" if inplace else f"sebagai:\n{os.path.basename(target_path)}"
                messagebox.showinfo(
                    "Berhasil",
                    f"Watermark AI ({wm_count} tanda air) berhasil dihapus {msg_location}!"
                )
            else:
                messagebox.showerror("Gagal", res.get("error", "Gagal menghapus watermark."))
        else:
            confirm = messagebox.askyesno(
                "Konfirmasi Hapus Watermark AI",
                f"Apakah Anda ingin menghapus tanda air AI dari {len(target_paths)} berkas yang dicentang?\n\nMode: Pembersihan {mode_str}."
            )
            if not confirm:
                return

            self.status_bar.configure(text=f"🤖 Sedang menghapus watermark AI dari {len(target_paths)} berkas terpilih...")

            def worker():
                success_count = 0
                new_items = []
                for path in target_paths:
                    res = AIWatermarkCleaner.clean_file(path, inplace=inplace)
                    if res.get("success"):
                        success_count += 1
                        target_p = path if inplace else res.get("output_path")
                        cleaned_info = inspect_file(target_p)
                        if inplace:
                            for idx, it in enumerate(self.scanned_items):
                                if it.get("file_path") == path:
                                    self.scanned_items[idx] = cleaned_info
                                    break
                        else:
                            new_items.append(cleaned_info)

                def on_finish():
                    if not inplace:
                        self.scanned_items.extend(new_items)
                    self._refresh_file_list()

                    if self.selected_item:
                        sel_path = self.selected_item.get("file_path")
                        for it in self.scanned_items:
                            if it.get("file_path") == sel_path:
                                self._display_detail(it)
                                break

                    self.status_bar.configure(text=f"Pembersihan watermark selesai: {success_count} dari {len(target_paths)} berkas berhasil diproses.")
                    messagebox.showinfo(
                        "Selesai",
                        f"Pembersihan Watermark AI Selesai!\n{success_count} dari {len(target_paths)} berkas berhasil dibersihkan {mode_str}."
                    )

                self.after(0, on_finish)

            threading.Thread(target=worker, daemon=True).start()

    def _edit_metadata(self):
        if not self.selected_item:
            messagebox.showinfo("Petunjuk", "Silakan pilih berkas di daftar yang ingin diedit metadatanya.")
            return

        file_path = self.selected_item.get("file_path")
        if not file_path or not os.path.exists(file_path):
            messagebox.showerror("Kesalahan", "Berkas tidak ditemukan.")
            return

        editor = get_editor_for_file(file_path)
        if not editor:
            messagebox.showinfo(
                "Tidak Didukung",
                "Format berkas ini belum mendukung penyuntingan metadata langsung.\n\nFormat yang didukung: Gambar (JPG/PNG/TIFF), Dokumen (PDF, Word DOCX), dan Media (MP3, MP4)."
            )
            return

        dlg = MetadataEditDialog(self, file_path, editor)
        self.wait_window(dlg)

        if dlg.result and dlg.result.get("success"):
            inplace = dlg.result.get("inplace", True)
            target_path = file_path if inplace else dlg.result.get("output_path")
            new_info = inspect_file(target_path)

            if inplace:
                for idx, it in enumerate(self.scanned_items):
                    if it.get("file_path") == file_path:
                        self.scanned_items[idx] = new_info
                        break
            else:
                self.scanned_items.append(new_info)

            self._refresh_file_list()
            self._display_detail(new_info)

            save_loc = "di tempat (berkas asli)" if inplace else f"sebagai salinan baru:\n{os.path.basename(target_path)}"
            messagebox.showinfo("Berhasil", f"Metadata berhasil diperbarui {save_loc}!")

    def _export_report(self):
        if not self.scanned_items:
            messagebox.showinfo("Petunjuk", "Belum ada data metadata untuk diekspor.")
            return

        dlg = ExportFormatDialog(self)
        self.wait_window(dlg)

        if not dlg.selected_format:
            return

        if dlg.selected_format == "pdf":
            save_path = filedialog.asksaveasfilename(
                title="Simpan Dokumen Laporan PDF",
                defaultextension=".pdf",
                filetypes=[("Dokumen PDF (*.pdf)", "*.pdf")]
            )
            if not save_path:
                return

            ok = PDFExporter.export(self.scanned_items, save_path)
            if ok:
                messagebox.showinfo("Berhasil", f"Laporan formal PDF berhasil disimpan ke:\n{save_path}")
            else:
                messagebox.showerror("Gagal", "Gagal menyimpan berkas laporan PDF.")

        elif dlg.selected_format == "md":
            save_path = filedialog.asksaveasfilename(
                title="Simpan Laporan Markdown",
                defaultextension=".md",
                filetypes=[("Berkas Markdown (*.md)", "*.md")]
            )
            if not save_path:
                return

            ok = MarkdownExporter.export(self.scanned_items, save_path)
            if ok:
                messagebox.showinfo("Berhasil", f"Laporan Markdown berhasil disimpan ke:\n{save_path}")
            else:
                messagebox.showerror("Gagal", "Gagal menyimpan berkas laporan Markdown.")

    def _update_shell_button_text(self):
        if not hasattr(self, 'btn_shell'):
            return
        if IS_MAC:
            if MacShellIntegration.is_installed():
                self.btn_shell.configure(text="✓ Quick Action Finder Aktif", fg_color="#15803d", hover_color="#166534")
            else:
                self.btn_shell.configure(text="⚙️ Integrasi Finder", fg_color="#334155", hover_color="#1e293b")
        else:
            if WindowsShellIntegration.is_installed():
                self.btn_shell.configure(text="✓ Menu Explorer Aktif", fg_color="#15803d", hover_color="#166534")
            else:
                self.btn_shell.configure(text="⚙️ Menu Klik Kanan", fg_color="#334155", hover_color="#1e293b")

    def _toggle_shell_integration(self):
        if IS_MAC:
            if MacShellIntegration.is_installed():
                confirm = messagebox.askyesno(
                    "Konfirmasi Pencopotan",
                    "Quick Action Finder MrClean saat ini aktif di macOS.\n\nApakah Anda ingin mencopotnya dari menu klik kanan Finder?"
                )
                if confirm:
                    ok, msg = MacShellIntegration.uninstall()
                    if ok:
                        messagebox.showinfo("Berhasil", msg)
                    else:
                        messagebox.showerror("Gagal", msg)
                    self._update_shell_button_text()
            else:
                confirm = messagebox.askyesno(
                    "Integrasi Finder macOS",
                    "Tambahkan Quick Action 'Bersihkan Metadata dengan MrClean' ke menu klik kanan Finder macOS?\n\n(Akan dipasang ke ~/Library/Services/)"
                )
                if confirm:
                    ok, msg = MacShellIntegration.install()
                    if ok:
                        messagebox.showinfo("Berhasil", msg)
                    else:
                        messagebox.showerror("Gagal", msg)
                    self._update_shell_button_text()
        else:
            if WindowsShellIntegration.is_installed():
                confirm = messagebox.askyesno(
                    "Konfirmasi Pencopotan",
                    "Menu klik kanan MrClean saat ini sedang aktif di Windows Explorer.\n\nApakah Anda ingin mencopotnya dari menu klik kanan?"
                )
                if confirm:
                    ok, msg = WindowsShellIntegration.uninstall()
                    if ok:
                        messagebox.showinfo("Berhasil", msg)
                    else:
                        messagebox.showerror("Gagal", msg)
                    self._update_shell_button_text()
            else:
                confirm = messagebox.askyesno(
                    "Integrasi Windows Explorer",
                    "Tambahkan pintasan 'Bersihkan Metadata dengan MrClean' ke menu klik kanan Windows Explorer?\n\n(Beroperasi 100% aman di akun pengguna saat ini / HKCU tanpa butuh hak Administrator)."
                )
                if confirm:
                    ok, msg = WindowsShellIntegration.install()
                    if ok:
                        messagebox.showinfo("Berhasil", msg)
                    else:
                        messagebox.showerror("Gagal", msg)
                    self._update_shell_button_text()

    def _apply_preset_action(self, choice):
        if choice == "⚡ Profil Cepat...":
            return

        target_paths = list(self.selected_file_paths)
        if not target_paths and self.selected_item:
            sel_p = self.selected_item.get("file_path")
            if sel_p:
                target_paths = [sel_p]

        if not target_paths:
            messagebox.showinfo("Petunjuk", "Silakan centang atau pilih berkas di daftar sebelum menerapkan profil cepat.")
            self.preset_var.set("⚡ Profil Cepat...")
            return

        preset_map = {
            "📱 Media Sosial": "social_media",
            "🎓 Akademik": "academic",
            "💻 Developer/OSS": "developer"
        }
        preset_key = preset_map.get(choice, "social_media")
        inplace = bool(self.chk_inplace.get())
        mode_str = "di tempat (In-Place)" if inplace else "sebagai salinan baru"

        confirm = messagebox.askyesno(
            "Terapkan Profil Pembersihan",
            f"Terapkan profil '{choice}' pada {len(target_paths)} berkas terpilih?\n\nMode: Pembersihan {mode_str}."
        )
        if not confirm:
            self.preset_var.set("⚡ Profil Cepat...")
            return

        self.status_bar.configure(text=f"Sedang menerapkan profil {choice} pada {len(target_paths)} berkas...")

        def worker():
            success_count = 0
            new_items = []
            for path in target_paths:
                res = PresetCleaner.clean_with_preset(path, preset_key=preset_key, inplace=inplace)
                if res.get("success"):
                    success_count += 1
                    target_p = path if inplace else res.get("output_path", path)
                    cleaned_info = inspect_file(target_p)
                    if inplace:
                        for idx, it in enumerate(self.scanned_items):
                            if it.get("file_path") == path:
                                self.scanned_items[idx] = cleaned_info
                                break
                    else:
                        new_items.append(cleaned_info)

            def on_finish():
                if not inplace:
                    self.scanned_items.extend(new_items)
                self._refresh_file_list()
                if self.selected_item:
                    sel_p = self.selected_item.get("file_path")
                    for it in self.scanned_items:
                        if it.get("file_path") == sel_p:
                            self._display_detail(it)
                            break
                self.preset_var.set("⚡ Profil Cepat...")
                self.status_bar.configure(text=f"Profil {choice} selesai diterapkan pada {success_count} dari {len(target_paths)} berkas.")
                messagebox.showinfo(
                    "Selesai",
                    f"Profil {choice} berhasil diterapkan pada {success_count} dari {len(target_paths)} berkas {mode_str}!"
                )

            self.after(0, on_finish)

        threading.Thread(target=worker, daemon=True).start()

    def _spoof_metadata_action(self):
        target_paths = list(self.selected_file_paths)
        if not target_paths and self.selected_item:
            sel_p = self.selected_item.get("file_path")
            if sel_p:
                target_paths = [sel_p]

        if not target_paths:
            messagebox.showinfo("Petunjuk", "Silakan centang atau pilih berkas di daftar untuk disamarkan metadatanya.")
            return

        inplace = bool(self.chk_inplace.get())
        mode_str = "di tempat (In-Place)" if inplace else "sebagai salinan baru"

        confirm = messagebox.askyesno(
            "Konfirmasi Samarkan Metadata (Spoofing)",
            f"Apakah Anda ingin menyamarkan metadata {len(target_paths)} berkas dengan metadata kamera sintetis yang wajar (Canon/Nikon/Sony acak)?\n\nMode: Pemrosesan {mode_str}."
        )
        if not confirm:
            return

        self.status_bar.configure(text=f"Sedang menyamarkan metadata {len(target_paths)} berkas...")

        def worker():
            success_count = 0
            new_items = []
            for path in target_paths:
                res = MetadataSpoofer.spoof(path, profile_name="random", inplace=inplace)
                if res.get("success"):
                    success_count += 1
                    target_p = path if inplace else res.get("output_path", path)
                    spoofed_info = inspect_file(target_p)
                    if inplace:
                        for idx, it in enumerate(self.scanned_items):
                            if it.get("file_path") == path:
                                self.scanned_items[idx] = spoofed_info
                                break
                    else:
                        new_items.append(spoofed_info)

            def on_finish():
                if not inplace:
                    self.scanned_items.extend(new_items)
                self._refresh_file_list()
                if self.selected_item:
                    sel_p = self.selected_item.get("file_path")
                    for it in self.scanned_items:
                        if it.get("file_path") == sel_p:
                            self._display_detail(it)
                            break
                self.status_bar.configure(text=f"Penyuntikan metadata sintetis selesai pada {success_count} dari {len(target_paths)} berkas.")
                messagebox.showinfo(
                    "Berhasil",
                    f"Metadata sintetis berhasil disuntikkan ke {success_count} dari {len(target_paths)} berkas {mode_str}!"
                )

            self.after(0, on_finish)

        threading.Thread(target=worker, daemon=True).start()

    def _clean_ai_and_c2pa_action(self, file_path):
        if not file_path or not os.path.exists(file_path):
            messagebox.showerror("Error", "Berkas tidak ditemukan.")
            return

        inplace = bool(self.chk_inplace.get())
        res = C2PACleaner.clean_ai_and_c2pa(file_path, inplace=inplace)
        if res.get("success"):
            target_p = file_path if inplace else res.get("output_path")
            new_info = inspect_file(target_p)
            if inplace:
                for idx, it in enumerate(self.scanned_items):
                    if it.get("file_path") == file_path:
                        self.scanned_items[idx] = new_info
                        break
            else:
                self.scanned_items.append(new_info)
            self._refresh_file_list()
            self._display_detail(new_info)
            messagebox.showinfo("Berhasil", "Jejak AI generatif dan manifes C2PA berhasil dibersihkan!")
        else:
            messagebox.showerror("Gagal", res.get("error", "Gagal membersihkan jejak AI."))

def main():
    app = MetaCleanApp()
    # Jika dipanggil via CLI atau Finder Quick Action dengan argumen berkas/folder
    if len(sys.argv) > 1:
        initial_paths = [p for p in sys.argv[1:] if os.path.exists(p)]
        if initial_paths:
            app.after(300, lambda: app._process_paths(initial_paths))
    app.mainloop()

if __name__ == "__main__":
    main()
