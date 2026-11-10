"""
MrClean Mac — Offline GPS Map Viewer Modal Dialog
Menampilkan visualisasi lokasi koordinat GPS secara 100% Offline:
- Menghitung format Desimal (DD) dan Derajat Menit Detik (DMS)
- Merender radar kompas dan pin peta vektor interaktif via Tkinter Canvas
- Menjamin privasi absolut tanpa pernah mengirim panggilan jaringan ke luar.
"""
import math
import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk

class OfflineMapDialog(ctk.CTkToplevel):
    """Jendela modal visualisasi koordinat GPS 100% Offline."""

    def __init__(self, parent, latitude: float, longitude: float, altitude: str = None, file_name: str = ""):
        super().__init__(parent)
        self.latitude = latitude
        self.longitude = longitude
        self.altitude = altitude or "Tidak tertera"
        self.file_name = file_name

        self.title("🗺️ Penampil Lokasi GPS 100% Offline — MrClean Mac")
        self.geometry("540x500")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        self._build_ui()
        self.center_window(parent)

    def center_window(self, parent):
        self.update_idletasks()
        try:
            px = parent.winfo_x()
            py = parent.winfo_y()
            pw = parent.winfo_width()
            ph = parent.winfo_height()
            x = px + (pw - 540) // 2
            y = py + (ph - 500) // 2
            self.geometry(f"540x500+{x}+{y}")
        except Exception:
            pass

    def _to_dms(self, deg: float, is_lat: bool) -> str:
        """Mengonversi derajat desimal ke format DMS (Degrees Minutes Seconds)."""
        direction = ("U" if deg >= 0 else "S") if is_lat else ("T" if deg >= 0 else "B")
        abs_deg = abs(deg)
        d = int(abs_deg)
        m = int((abs_deg - d) * 60)
        s = (abs_deg - d - m / 60) * 3600
        return f"{d}° {m}' {s:.1f}\" {direction}"

    def _build_ui(self):
        # 1. Header Card
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=(15, 8))

        ctk.CTkLabel(
            header,
            text="📍 Koordinat Lokasi GPS Terdeteksi",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(anchor="w")

        subtext = f"Berkas: {self.file_name}" if self.file_name else "Visualisasi Vektor Offline"
        ctk.CTkLabel(
            header,
            text=subtext,
            font=ctk.CTkFont(size=12),
            text_color="#38bdf8"
        ).pack(anchor="w")

        # 2. Canvas Visual Peta / Radar Kompas Offline
        canvas_frame = ctk.CTkFrame(self, fg_color="#0f172a", corner_radius=10)
        canvas_frame.pack(fill="both", expand=True, padx=20, pady=5)

        self.canvas = tk.Canvas(canvas_frame, bg="#0f172a", highlightthickness=0, width=500, height=220)
        self.canvas.pack(fill="both", expand=True, padx=10, pady=10)
        self._draw_offline_map()

        # 3. Info Kartu Koordinat
        info_card = ctk.CTkFrame(self, corner_radius=8)
        info_card.pack(fill="x", padx=20, pady=8)

        # Baris Desimal
        dms_lat = self._to_dms(self.latitude, is_lat=True)
        dms_lon = self._to_dms(self.longitude, is_lat=False)

        ctk.CTkLabel(
            info_card,
            text=f"🌐 Koordinat Desimal : {self.latitude:.6f}, {self.longitude:.6f}",
            font=ctk.CTkFont(size=12, weight="bold")
        ).pack(anchor="w", padx=15, pady=(8, 2))

        ctk.CTkLabel(
            info_card,
            text=f"🧭 Derajat Menit Detik : {dms_lat}, {dms_lon}",
            font=ctk.CTkFont(size=11),
            text_color="gray"
        ).pack(anchor="w", padx=15, pady=2)

        ctk.CTkLabel(
            info_card,
            text=f"⛰️ Ketinggian (Altitude) : {self.altitude}",
            font=ctk.CTkFont(size=11),
            text_color="gray"
        ).pack(anchor="w", padx=15, pady=(2, 8))

        # 4. Action Buttons
        btn_box = ctk.CTkFrame(self, fg_color="transparent")
        btn_box.pack(fill="x", padx=20, pady=(8, 15))

        btn_copy = ctk.CTkButton(
            btn_box,
            text="📋 Salin Koordinat",
            width=140,
            command=self._copy_coords
        )
        btn_copy.pack(side="left")

        btn_close = ctk.CTkButton(
            btn_box,
            text="Tutup",
            fg_color="#334155",
            hover_color="#475569",
            width=90,
            command=self.destroy
        )
        btn_close.pack(side="right")

    def _draw_offline_map(self):
        """Menggambar proyeksi radar koordinat bumi lokal 100% offline."""
        self.canvas.delete("all")
        w, h = 500, 220
        cx, cy = w // 2, h // 2

        # Grid peta dunia vektor sederhana
        self.canvas.create_rectangle(20, 15, w - 20, h - 15, outline="#334155", width=1)
        # Garis khatulistiwa (Equator)
        self.canvas.create_line(20, cy, w - 20, cy, fill="#1e293b", dash=(3, 3))
        # Garis bujur utama (Prime Meridian)
        self.canvas.create_line(cx, 15, cx, h - 15, fill="#1e293b", dash=(3, 3))

        # Petunjuk Mata Angin
        self.canvas.create_text(cx, 26, text="U (Utara)", fill="#64748b", font=("Helvetica", 9, "bold"))
        self.canvas.create_text(cx, h - 26, text="S (Selatan)", fill="#64748b", font=("Helvetica", 9, "bold"))
        self.canvas.create_text(w - 45, cy, text="T (Timur)", fill="#64748b", font=("Helvetica", 9, "bold"))
        self.canvas.create_text(45, cy, text="B (Barat)", fill="#64748b", font=("Helvetica", 9, "bold"))

        # Hitung posisi pin dari Latitude (-90 s/d +90) dan Longitude (-180 s/d +180)
        # Proyeksi Equirectangular sederhana
        map_w = (w - 40)
        map_h = (h - 30)

        # Longitude: -180 (kiri) ke +180 (kanan)
        px = 20 + ((self.longitude + 180.0) / 360.0) * map_w
        # Latitude: +90 (atas) ke -90 (bawah)
        py = 15 + ((90.0 - self.latitude) / 180.0) * map_h

        # Pin Marker (Lingkaran Pulsing + Titik Merah)
        self.canvas.create_oval(px - 14, py - 14, px + 14, py + 14, outline="#ef4444", width=1)
        self.canvas.create_oval(px - 8, py - 8, px + 8, py + 8, fill="#ef4444", outline="#ffffff", width=1.5)

        # Label Koordinat Mengambang
        lbl_text = f"📍 {self.latitude:.4f}, {self.longitude:.4f}"
        self.canvas.create_text(px, py - 20, text=lbl_text, fill="#f8fafc", font=("Helvetica", 10, "bold"))

    def _copy_coords(self):
        text = f"{self.latitude:.6f}, {self.longitude:.6f}"
        self.clipboard_clear()
        self.clipboard_append(text)
        messagebox.showinfo("Berhasil", f"Koordinat disalin ke clipboard:\n{text}", parent=self)
