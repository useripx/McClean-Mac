# 🗺️ Roadmap & Milestones — MrClean Mac (MCleanPro)

> **DOKUMEN PANDUAN PETA JALAN PRODUK (PRODUCT ROADMAP)**  
> **PROYEK:** MrClean Mac — Offline Metadata Inspector, Cleaner, Presets & AI Watermarks Remover  
> **OTORITAS / LEAD:** Yogi Ario  
> **STATUS:** AKTIF (TERAKHIR DIPERBARUI: 10 NOVEMBER 2026)  
> **FILOSOFI:** *100% Offline, Zero-Telemetry, Paritas Fitur Lengkap, Native Apple Human Interface Guidelines.*  

---

## 🧭 Peta Jalan Visual (Architecture & Release Timeline)

```mermaid
flowchart TD
    subgraph FASE1 ["Fase 1 (v1.0.0) — Pondasi Paritas & Native macOS [SELESAI]"]
        F1_1["Core Engine 11 Fitur Paritas"]
        F1_2["Test Suite 100% PASS (44 Tests)"]
        F1_3["GUI CustomTkinter macOS + SF Pro + ⌘ Cmd"]
        F1_4["Finder Quick Action & Notifikasi osascript"]
        F1_5["Aset Apple icon.icns (16-1024px)"]
        F1_6["Packaging build_mac.py (.app & .dmg)"]
        F1_7["Cloud CI/CD GitHub Actions macos-latest"]
        F1_8["Branch main Bersih via sync_to_main.py"]
    end

    subgraph FASE2 ["Fase 2 (v1.1.0) — UX Lanjutan & Universal Binary [SIAP DIKERJAKAN]"]
        F2_1["Rilis Publik GitHub Releases v1.0.0 (.dmg)"]
        F2_2["Universal 2 Fat Binary (arm64 + x86_64)"]
        F2_3["Stylized DMG Drag-to-Applications Installer"]
        F2_4["Dukungan Drag & Drop Berkas ke GUI"]
        F2_5["Demo GIF & Tangkapan Layar Resmi di README"]
    end

    subgraph FASE3 ["Fase 3 (v1.2.0) — Forensik Tingkat Lanjut [Q1 2027]"]
        F3_1["Dukungan Format Kamera RAW (ARW, CR3, NEF, RAF)"]
        F3_2["Ekstraksi Jejak GPS Video Drone (DJI, GoPro)"]
        F3_3["Viewer Peta GPS Interaktif 100% Offline"]
        F3_4["Deteksi Watermark Audio Lanjutan (Spectrogram)"]
    end

    subgraph FASE4 ["Fase 4 (v2.0.0) — Ekosistem Apple & CLI [Q2 2027]"]
        F4_1["Menu Bar / Status Item App (macOS Top Bar)"]
        F4_2["Integrasi Apple Shortcuts (Aplikasi Pintasan)"]
        F4_3["Distribusi via Homebrew Tap (brew install mrclean)"]
        F4_4["Persiapan Notarisasi Resmi Apple Developer"]
    end

    FASE1 --> FASE2
    FASE2 --> FASE3
    FASE3 --> FASE4
```

---

## 📍 Rincian Fase & Milestone Proyek

### 🟢 FASE 1: Pondasi Paritas Penuh & Adaptasi Native macOS (v1.0.0-macos)
**Target: 10 November 2026 | Status: SELESAI 100% (COMPLETED)**

- [x] **Tata Kelola 8 Pilar Universal:**
  - Penerapan Master Framework macOS, Approval Gate, Clean `main`, Zero Leakage `.gitignore`, dan Documentation-First.
- [x] **Backend Agnostic (Paritas 11 Fitur Lengkap):**
  - Inspeksi mendalam EXIF, GPS, Serial Perangkat, Author, dan Riwayat Software pada Gambar, PDF, DOCX, Media, dan Teks.
  - Pembersihan Lossless (tanpa kompresi piksel/kerusakan format).
  - Penghapusan AI Steganography & Zero-Width Spaces (`\u200B`, `\u200C`, `\u200D`, `\uFE0F`).
  - Privacy Risk Scorer (0–100% dengan status Kritis, Sedang, Aman).
  - Quick Presets: Media Sosial, Akademik, dan Developer (penyamaran path `/Users/user`).
  - AI Forensics (Prompt Stable Diffusion, Midjourney, DALL-E) dan pembersih manifes Adobe C2PA.
  - Metadata Spoofing (penyuntikan profil sintetis Canon/Nikon/Sony).
  - Preservative Selective Editor.
  - Ekspor Laporan PDF (ReportLab dengan logo resmi) dan Markdown (.md).
  - Multi-Item Selection & Batch Mode.
- [x] **Suite Pengujian Otomatis (100% PASS Gate):**
  - 44 unit tests lulus tanpa gagal (0 error / 0 fail).
- [x] **Adaptasi Antarmuka macOS:**
  - Font Apple `.AppleSystemUIFont` / `SF Pro Text`.
  - Pintasan keyboard Apple `⌘ Command` (`<Command-c>`, `<Command-v>`, `<Command-a>`, `<Command-q>`).
  - Tampilan HiDPI Retina 2x anti-buram.
  - Sinkronisasi mode Dark/Light real-time via `darkdetect`.
- [x] **Integrasi Native macOS:**
  - Quick Action Finder di `~/Library/Services/` (menu klik kanan di Finder).
  - Notifikasi desktop banner via `osascript`.
- [x] **Standarisasi Aset Apple:**
  - Ikon resmi Apple multi-resolusi `assets/icon.icns` (16x16 hingga 1024x1024 Retina).
- [x] **Packaging & CI/CD Cloud:**
  - Skrip mandiri `build_mac.py` (PyInstaller `--windowed` bundel `.app` dan `.dmg`).
  - Alur kerja GitHub Actions `.github/workflows/build-mac.yml` di runner Apple Silicon `macos-latest`.
  - Sinkronisasi rilis bersih ke branch `main` via `tools/sync_to_main.py`.

---

### 🟢 FASE 2: UX Lanjutan, Universal Binary & Rilis Publik (v1.1.0-macos)
**Target: 10 November 2026 | Status: SELESAI 100% (COMPLETED)**

- [x] **Dukungan Drag & Drop Langsung ke GUI (`src/gui/app.py`):**
  - Parser drop data pintar `parse_dropped_files` dan handler drop `handle_dropped_paths`.
  - Event native macOS `::tk::mac::OpenDocument` untuk penarikan berkas langsung ke ikon Dock atau Finder OpenWith.
  - Tampilan visual drop-zone ramah pengguna saat daftar berkas kosong.
- [x] **Universal 2 Fat Binary Support:**
  - Opsi flag `--universal` (`--target-arch universal2`) pada `build_mac.py` untuk mengemas biner Apple Silicon (`arm64`) dan Intel (`x86_64`) sekaligus.
- [x] **Stylized DMG Installer Layout:**
  - Integrasi utilitas `create-dmg` dengan visual layout Apple (Ikon MrClean di kiri ➜ Panah petunjuk ➜ Folder `/Applications` di kanan) dengan fallback otomatis `hdiutil`.
- [x] **Alat Otomatisasi Rilis (`tools/create_release.py`):**
  - Validasi SemVer resmi, testing gate 100% PASS otomatis, pembuatan Git tag, dan sinkronisasi ke branch `main`.
- [x] **Pembaruan Workflow GitHub Actions (`.github/workflows/build-mac.yml`):**
  - Mengotomatiskan publikasi *GitHub Release* dengan biner `dist/MrClean-macOS.dmg` terlampir saat tag rilis di-push.
- [x] **Unit Testing Suite Tambahan:**
  - 49 unit tests lulus tanpa gagal (**100% PASS, 0 GAGAL / 0 ERROR**).

---

### 🟢 FASE 3: Ekstensi Format & Forensik Tingkat Lanjut (v1.2.0-macos)
**Target: 10 November 2026 | Status: SELESAI 100% (COMPLETED)**

- [x] **Dukungan Format Kamera Profesional (RAW Formats):**
  - Ekstraksi dan pembersihan metadata foto mentah: Sony (`.ARW`), Canon (`.CR2`/`.CR3`), Nikon (`.NEF`), Fujifilm (`.RAF`), Adobe (`.DNG`), Olympus (`.ORF`), dan Panasonic (`.RW2`).
  - Netralisasi nomor seri bodi kamera, nomor seri lensa, dan tag GPS IFD.
- [x] **Ekstraksi & Pembersihan Telemetri Video Drone (DJI / GoPro):**
  - Deteksi dan pembersihan atom QuickTime `moov.udta` & subtitle stream GPS video drone tanpa re-encoding video.
- [x] **Viewer Peta GPS Interaktif 100% Offline (`OfflineMapDialog`):**
  - Jendela visualisasi pin peta vektor dan radar kompas koordinat (DD & DMS) lokal tanpa internet.
  - Tombol *"🗺️ Buka Peta GPS Offline"* pada antarmuka GUI detail viewer.
- [x] **Deteksi Steganografi Audio Spektrogram (`AudioStegoInspector`):**
  - Analisis anomali frekuensi ultrasonik dan chunk tersembunyi pada berkas audio WAV, FLAC, dan MP3.
- [x] **Pengujian Unit Otomatis Tambahan:**
  - 57 unit tests lulus tanpa gagal (**100% PASS, 0 GAGAL / 0 ERROR**).

---

### 🟢 FASE 4: Ekosistem Mendalam macOS & Distribusi Luas (v2.0.0-macos)
**Target: 10 November 2026 | Status: SELESAI 100% (COMPLETED)**

- [x] **Headless CLI Interface (`src/cli.py`):**
  - Perintah `inspect` (--json), `clean` (--preset, --inplace, -o), `spoof` (--profile), dan `--version` dengan exit code standar UNIX (`0` atau `1`).
- [x] **Integrasi Apple Shortcuts (Pintasan macOS):**
  - Panduan dan skrip shell automasi `integrations/shortcuts/` untuk Finder Share Sheet, Folder Actions, dan Siri.
- [x] **Menu Bar / Status Item App (`src/gui/menubar_app.py`):**
  - Status item di bar atas layar macOS via `pystray` (Quick Clean, Presets, Launch GUI) dengan notifikasi banner desktop.
- [x] **Distribusi via Homebrew Tap & Cask:**
  - Formula resmi Cask `packaging/homebrew/mrclean.rb` dengan symlink terminal `mrclean` dan panduan instalasi satu baris:
    ```bash
    brew tap useripx/mrclean
    brew install --cask mrclean
    ```
- [x] **Alat Otomatisasi Notarisasi Resmi Apple Developer (`tools/notarize_mac.py`):**
  - Generator perintah `codesign --options runtime`, `xcrun notarytool submit`, dan `xcrun stapler staple`.
- [x] **Unit Testing Suite Menyeluruh:**
  - 71 unit tests lulus tanpa gagal (**100% PASS, 0 GAGAL / 0 ERROR**).

---

## 📊 Matriks Status Milestone

| Milestone | Versi Target | Fitur Utama | Status Saat Ini |
| :--- | :---: | :--- | :---: |
| **Milestone 1** | `v1.0.0` | Paritas 11 Fitur, 44 Tests PASS, GUI Mac, Quick Action, `.icns`, CI/CD | 🟢 **SELESAI (100%)** |
| **Milestone 2** | `v1.1.0` | Drag & Drop GUI, Universal 2 Fat Binary, Stylized DMG, Release Tool | 🟢 **SELESAI (100%)** |
| **Milestone 3** | `v1.2.0` | Format RAW, Telemetri Drone GPS, Offline Map Viewer, Audio Stego | 🟢 **SELESAI (100%)** |
| **Milestone 4** | `v2.0.0` | Menu Bar Quick Clean, Headless CLI, Apple Shortcuts, Homebrew Cask, Notarisasi | 🟢 **SELESAI (100%)** |
