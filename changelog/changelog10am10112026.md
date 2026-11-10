# Changelog — 10:00 AM, 10 November 2026

## 📌 Ringkasan Sesi
- **Fokus:** Implementasi Penuh Fase 2 (v1.1.0-macos) — UX Drag & Drop GUI, Universal 2 Fat Binary, Stylized DMG Installer, dan Otomatisasi Rilis GitHub Actions.
- **Pengembang / AI Agent:** Antigravity (Google DeepMind)
- **Otoritas Proyek:** Yogi Ario
- **Hasil Pengujian Otomatis:** **100% PASS (49 Unit Tests, 0 GAGAL / 0 ERROR)**.

---

## 🚀 Rincian Perubahan Fase 2 (v1.1.0-macos)

### 1. Antarmuka Pengguna & UX Lanjutan (Native Drag & Drop)
- Menambahkan metode `parse_dropped_files` dan `handle_dropped_paths` pada `src/gui/app.py`.
- Menambahkan integrasi callback native macOS `::tk::mac::OpenDocument` saat berkas ditarik ke ikon MrClean di macOS Dock atau dibuka melalui menu Finder *"Open With"*.
- Memperbarui antarmuka daftar berkas dengan drop-zone visual saat tabel dalam keadaan kosong.
- Menambahkan unit test `tests/test_drag_and_drop.py` yang menguji parsing path berkas dengan spasi dan format kurung kurawal.

### 2. Packaging & Universal 2 Fat Binary (`build_mac.py`)
- Menambahkan argumen `--universal` untuk mengompilasi biner fat binary Universal 2 (`--target-arch universal2`) sehingga satu bundel `.app` berjalan native di Apple Silicon (`arm64`) dan Intel (`x86_64`).
- Mengintegrasikan utilitas `create-dmg` dengan visual layout Apple (Ikon MrClean di kiri ➜ Panah petunjuk ➜ Folder `/Applications` di kanan) dengan fallback otomatis ke `hdiutil`.

### 3. Otomatisasi Rilis & GitHub Actions Workflow
- Membuat alat CLI `tools/create_release.py` untuk pembuatan tag Git Semantic Versioning resmi (`v*`), validasi testing gate 100% PASS sebelum rilis, dan sinkronisasi rilis bersih ke branch `main`.
- Menambahkan unit test `tests/test_release_tool.py` untuk validasi format SemVer.
- Memperbarui `.github/workflows/build-mac.yml` dengan langkah otomatisasi pembuatan *GitHub Release* dan unggah aset biner `MrClean-macOS.dmg` saat tag rilis di-push.

### 4. Pembaruan Pelacak & Dokumentasi
- Memperbarui `Docs/Task_Status.md` dan `Docs/Roadmap.md` (Fase 2 status 100% Selesai).
- Menambahkan rekaman keputusan arsitektur ADR-007 dan ADR-008 pada `Docs/Decision_Log.md`.
- Memperbarui ringkasan roadmap pada `README.md`.
