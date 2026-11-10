# Task Status — MrClean Mac

> **STATUS PROYEK:** FASE 1 & FASE 2 SELESAI 100% (49 TESTS PASS)  
> **TERAKHIR DIPERBARUI:** 10 November 2026 (10:00 AM)  
> **LEAD DEVELOPER:** Yogi Ario  

---

## 📊 Matriks Progres Keseluruhan

| Fase / Milestone | Deskripsi | Status | Progres |
| :--- | :--- | :---: | :---: |
| **Fase 0** | Inisialisasi Repositori, Aturan, Badges, & Dokumentasi | 🟢 Selesai | 100% |
| **Fase 1 (v1.0.0)** | Core Engine Paritas, GUI macOS, Quick Action, ICNS & CI/CD | 🟢 Selesai (44 Tests PASS) | 100% |
| **Fase 2 (v1.1.0)** | Drag & Drop GUI, Universal 2 Fat Binary, Stylized DMG & Release Tool | 🟢 Selesai (49 Tests PASS) | 100% |
| **Fase 3 (v1.2.0)** | Format RAW Kamera, Telemetri Drone GPS, Offline Map Viewer | ⚪ Antre (Q1 2027) | 0% |
| **Fase 4 (v2.0.0)** | Menu Bar Tray App, Apple Shortcuts, Homebrew Cask, Notarisasi | ⚪ Antre (Q2 2027) | 0% |

---

## 📋 Rincian Checklist Fase 2 (v1.1.0-macos)

### UX Lanjutan & Drag-and-Drop
- [x] Implementasi `handle_dropped_paths` dan `parse_dropped_files` pada `src/gui/app.py`.
- [x] Dukungan event native macOS `::tk::mac::OpenDocument` untuk penarikan berkas ke ikon Dock.
- [x] Tampilan visual drop-zone pada tabel daftar berkas saat kosong.
- [x] Unit test `tests/test_drag_and_drop.py` terverifikasi lulus.

### Packaging & Universal 2 Fat Binary
- [x] Penambahan opsi `--universal` (`--target-arch universal2`) pada `build_mac.py`.
- [x] Integrasi `create-dmg` dengan visual layout Apple HIG (Ikon ➜ Panah ➜ /Applications) dan fallback otomatis `hdiutil`.
- [x] Workflow `.github/workflows/build-mac.yml` dengan trigger upload aset biner DMG otomatis ke GitHub Releases.

### Release Automation
- [x] Pembuatan alat CLI rilis `tools/create_release.py` dengan validasi SemVer dan testing gate.
- [x] Unit test `tests/test_release_tool.py` terverifikasi lulus.
- [x] Sinkronisasi rilis bersih ke branch `main` via `tools/sync_to_main.py`.
