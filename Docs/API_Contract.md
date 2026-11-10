# API Contract & System Specification — MrClean Mac

> **JENIS APLIKASI:** Desktop Standalone (100% Offline, Zero-Telemetry)  
> **TARGET SISTEM OPERASI:** macOS 11+ (Big Sur, Monterey, Ventura, Sonoma, Sequoia) — Apple Silicon (arm64) & Intel (x86_64)  
> **BAHASA & GUI:** Python 3.13+ & CustomTkinter  

---

## 1. Lingkup Operasional
Aplikasi ini beroperasi secara penuh di lingkungan lokal pengguna tanpa ketergantungan pada koneksi internet atau server pihak ketiga. Seluruh modul I/O berkas memproses data langsung dalam memori atau penyimpanan lokal dengan integritas berkas cadangan (*safety copy*).

---

## 2. Kontrak Modul Inti (Core Specifications)

### 2.1 Metadata Inspectors (`src/inspectors/`)
- Menerima: Path berkas (`str` / `Path`).
- Mengembalikan: Objek kamus metadata terstruktur berisi:
  - `file_type`: Jenis MIME / kategori berkas.
  - `metadata`: Pasangan kunci-nilai tag metadata yang diekstrak.
  - `risk_score`: Nilai numerik 0–100%.
  - `risk_level`: Label `AMAN`, `SEDANG`, atau `KRITIS`.
  - `ai_forensics`: Informasi prompt AI generative / manifes C2PA (jika ditemukan).

### 2.2 Metadata Cleaners (`src/cleaners/`)
- Menerima: Path berkas sumber dan path berkas keluaran.
- Opsi: Preset (Default Lossless, Social Media, Academic, Developer).
- Mengembalikan: Boolean keberhasilan pembersihan dan log ringkasan tag yang dihapus.
- Garansi: Kualitas visual gambar (piksel) dan konten dokumen tidak terkompresi atau rusak (lossless).

### 2.3 AI Watermark Cleaner (`src/watermarks/`)
- Menerima: Teks atau berkas dokumen/teks.
- Menghapus: Zero-width spaces (`\u200B`), zero-width joiners (`\u200D`), zero-width non-joiners (`\u200C`), variation selectors (`\uFE0F`), dan token tersembunyi lainnya.
- Mengembalikan: Teks bersih dan jumlah karakter tersembunyi yang dimusnahkan.

### 2.4 Metadata Spoofing & Editor (`src/editors/`)
- Menerima: Target modifikasi (field tertentu untuk preservasi atau model kamera sintetis Canon/Nikon/Sony).
- Menghasilkan: Berkas dengan metadata yang disesuaikan atau disamarkan tanpa merusak struktur file asli.

### 2.5 Exporters (`src/utils/`)
- **PDF Report:** Dihasilkan via ReportLab beresolusi tinggi dengan kop logo resmi (`assets/logo.png`), tabel risiko, dan timestamp analisis.
- **Markdown Report:** Dihasilkan dalam format tabel markdown standar GitHub Flavored Markdown (.md).
