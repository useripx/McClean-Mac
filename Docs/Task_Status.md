# Task Status — MrClean Mac

> **STATUS PROYEK:** FASE 1, FASE 2, & FASE 3 SELESAI 100% (57 TESTS PASS)  
> **TERAKHIR DIPERBARUI:** 10 November 2026 (10:15 AM)  
> **LEAD DEVELOPER:** Yogi Ario  

---

## 📊 Matriks Progres Keseluruhan

| Fase / Milestone | Deskripsi | Status | Progres |
| :--- | :--- | :---: | :---: |
| **Fase 0** | Inisialisasi Repositori, Aturan, Badges, & Dokumentasi | 🟢 Selesai | 100% |
| **Fase 1 (v1.0.0)** | Core Engine Paritas, GUI macOS, Quick Action, ICNS & CI/CD | 🟢 Selesai (44 Tests PASS) | 100% |
| **Fase 2 (v1.1.0)** | Drag & Drop GUI, Universal 2 Fat Binary, Stylized DMG & Release Tool | 🟢 Selesai (49 Tests PASS) | 100% |
| **Fase 3 (v1.2.0)** | Format RAW Kamera, Telemetri Drone GPS, Offline Map Viewer, Audio Stego | 🟢 Selesai (57 Tests PASS & Rilis Tag v1.2.0 Dipublikasikan) | 100% |
| **Fase 4 (v2.0.0)** | Menu Bar Tray App, Apple Shortcuts, Homebrew Cask, Notarisasi | 🟡 Siap Diimplementasikan (Plan Approved) | 0% |

---

## 📋 Rincian Checklist Fase 3 (v1.2.0-macos)

### Format Kamera Mentah / RAW
- [x] Parser RAW berbasis TIFF/IFD & ISOBMFF (`src/inspectors/raw_inspector.py`) untuk Sony ARW, Canon CR2/CR3, Nikon NEF, Fuji RAF, Adobe DNG, Olympus ORF, Panasonic RW2.
- [x] Pembersih tag RAW sensitif (`src/cleaners/raw_cleaner.py`).
- [x] Unit test `tests/test_raw_inspector.py` terverifikasi lulus.

### Telemetri Video Drone & Action Camera
- [x] Detektor atom QuickTime `moov.udta` & telemetri GPS drone DJI / GoPro (`src/inspectors/drone_inspector.py`).
- [x] Pembersih telemetri video drone (`src/cleaners/drone_cleaner.py`) tanpa re-encoding video.
- [x] Unit test `tests/test_drone_inspector.py` terverifikasi lulus.

### Visualisasi Peta GPS Offline
- [x] Dialog modal penampil peta vektor radar GPS 100% Offline (`src/gui/dialogs/map_dialog.py`).
- [x] Tombol *"🗺️ Buka Peta GPS Offline"* diintegrasikan pada antarmuka GUI detail viewer (`src/gui/app.py`).
- [x] Unit test `tests/test_offline_map.py` terverifikasi lulus.

### Steganografi Audio Spektrogram
- [x] Inspektor tanda air frekuensi ultrasonik dan chunk tersembunyi RIFF/ID3 (`src/watermarks/audio_stego.py`).
- [x] Unit test `tests/test_audio_stego.py` terverifikasi lulus.
