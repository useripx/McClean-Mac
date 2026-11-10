# Changelog — 09:00 AM, 10 November 2026

## 📌 Ringkasan Sesi
- **Fokus:** Porting Mandiri & Implementasi Lengkap MrClean Versi macOS (Apple Silicon & Intel) — Batch 1 hingga Batch 6.
- **Pengembang / AI Agent:** Antigravity (Google DeepMind)
- **Otoritas Proyek:** Yogi Ario
- **Status Akhir Pengujian:** **100% PASS (44 Unit Tests, 0 GAGAL / 0 ERROR)**.

---

## 🚀 Rincian Perubahan Lengkap

### 1. Fondasi Tata Kelola & Standar Repositori
- Membaca dan mematuhi seluruh panduan `aturan/universal-rule.md`, `aturan/AGENTS.md`, dan `aturan/GEMINI.md`.
- Membangun `.gitignore` komprehensif penyaring artefak macOS (`.DS_Store`, `._*`), direktori build (`build/`, `dist/`), cache Python, dan virtual environment.
- Membangun `README.md` berstandar publik dengan badges Shields.io lengkap (Repo Size, Forks, Stars, Issues, MIT License, macOS Platform, Python 3.13+, Offline Security) serta logo terpusat.
- Menyiapkan `LICENSE` resmi MIT atas nama Yogi Ario dan `.env.example`.
- Menginisialisasi Git, menghubungkan remote `https://github.com/useripx/McClean-Mac.git`, dan membuat branch kerja `develop`.

### 2. Batch 1: Inisialisasi Backend Core Engine & Automated Tests (100% PASS Gate)
- Mengonfigurasi `requirements.txt` (`customtkinter`, `Pillow`, `pypdf`, `mutagen`, `python-docx`, `piexif`, `reportlab`, `darkdetect`, `pyinstaller`).
- Membangun modul inspektor di `src/inspectors/` (`image_inspector.py`, `pdf_inspector.py`, `docx_inspector.py`, `media_inspector.py`, `text_inspector.py`, `risk_scorer.py`, `ai_forensics.py`).
- Membangun modul pembersih di `src/cleaners/` (`image_cleaner.py`, `pdf_cleaner.py`, `docx_cleaner.py`, `media_cleaner.py`, `text_cleaner.py`, `preset_cleaner.py`, `c2pa_cleaner.py`).
- Membangun modul penyunting selektif dan spoofing di `src/editors/` (`image_editor.py`, `pdf_editor.py`, `docx_editor.py`, `media_editor.py`, `spoofing.py`).
- Membangun pembersih tanda air AI di `src/watermarks/` (`ai_cleaner.py`).
- Membangun utilitas ekspor di `src/utils/` (`scanner.py`, `exporter.py`, `md_exporter.py`, `pdf_exporter.py`).
- Menjalankan 44 unit tests di `tests/` dengan hasil verifikasi **100% PASS (0 GAGAL / 0 ERROR)**.

### 3. Batch 2: Adaptasi Antarmuka GUI (CustomTkinter macOS)
- Menyesuaikan tipografi font sistem ke `.AppleSystemUIFont` / `SF Pro Text` pada macOS.
- Menambahkan *event binding* pintasan keyboard Apple `⌘ Command` (`<Command-c>`, `<Command-v>`, `<Command-a>`, `<Command-q>`) pada dialog form dan jendela utama.
- Menjamin dukungan Retina HiDPI 2x untuk logo dan antarmuka.
- Menambahkan sinkronisasi tema Light/Dark mode sistem operasi melalui `darkdetect`.

### 4. Batch 3: Integrasi Sistem Operasi macOS Native
- Membangun modul `src/utils/mac_shell_integration.py` untuk memasang Finder Quick Action (`~/Library/Services/Bersihkan Metadata dengan MrClean.workflow`).
- Menambahkan notifikasi desktop native macOS via `osascript` saat proses batch cleaning selesai.
- Menyesuaikan penyamaran path developer Unix/Mac (`/Users/username/...` disamarkan menjadi `/Users/user`).

### 5. Batch 4: Standarisasi Aset Apple (`assets/icon.icns`)
- Memperbarui `src/utils/icon_converter.py` untuk mengonversi `asset/logo.png` (1024x1024) menjadi biner Apple `.icns` multi-resolusi (16x16 hingga 1024x1024 Retina).
- Menghasilkan berkas `assets/icon.icns` berukuran ~2 MB.

### 6. Batch 5 & 6: Packaging Standalone & CI/CD Cloud Runner
- Membuat skrip build mandiri `build_mac.py` (`PyInstaller --windowed --onedir` dan pengemasan disk image `hdiutil create .dmg`).
- Menguji eksekusi `build_mac.py` secara lokal dengan status sukses (`[SUCCESS] PROSES BUILD SELESAI DENGAN SUKSES!`).
- Menyusun alur kerja GitHub Actions `.github/workflows/build-mac.yml` yang berjalan otomatis pada runner `macos-latest` (Apple Silicon M-series) untuk validasi unit test dan build artifact `.dmg`.

### 7. Pembaruan Pelacak Dokumentasi
- Memperbarui `Docs/Task_Status.md` (status seluruh batch 100% selesai).
- Menambahkan rekaman keputusan ADR-001 hingga ADR-006 pada `Docs/Decision_Log.md`.
