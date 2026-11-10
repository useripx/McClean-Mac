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


---

## 🚀 Rincian Tambahan Fase 3 (v1.2.0-macos)

### 1. Ekstensi Format Kamera Profesional (RAW Image Formats)
- Membangun `src/inspectors/raw_inspector.py` yang mendukung ekstraksi metadata format RAW: Sony (`.arw`), Canon (`.cr2`, `.cr3`), Nikon (`.nef`), Fujifilm (`.raf`), Adobe (`.dng`), Olympus (`.orf`), dan Panasonic (`.rw2`).
- Mengekstrak nomor seri bodi kamera, nomor seri lensa, dan koordinat GPS geofence.
- Membangun `src/cleaners/raw_cleaner.py` yang menetralkan tag sensitif RAW tanpa merusak data mentah sensor.
- Unit test `tests/test_raw_inspector.py` terverifikasi lulus.

### 2. Forensik Telemetri Video Drone & Action Camera (DJI / GoPro)
- Membangun `src/inspectors/drone_inspector.py` yang mendeteksi atom QuickTime `moov.udta` & subtitle stream GPS video drone DJI / GoPro.
- Membangun `src/cleaners/drone_cleaner.py` yang menetralkan atom telemetri menjadi atom `free` padding tanpa re-encoding video.
- Unit test `tests/test_drone_inspector.py` terverifikasi lulus.

### 3. Visualisasi Peta GPS Vektor 100% Offline
- Membangun `src/gui/dialogs/map_dialog.py` (`OfflineMapDialog`) yang menampilkan visualisasi pin peta vektor dan radar kompas koordinat (DD & DMS) lokal tanpa internet.
- Menambahkan tombol interaktif *"🗺️ Buka Peta GPS Offline"* pada baris Lokasi GPS di antarmuka GUI detail viewer (`src/gui/app.py`).
- Unit test `tests/test_offline_map.py` terverifikasi lulus.

### 4. Deteksi Steganografi Audio Spektrogram
- Membangun `src/watermarks/audio_stego.py` (`AudioStegoInspector`) yang menganalisis anomali frekuensi ultrasonik dan chunk tersembunyi pada berkas audio WAV, FLAC, dan MP3.
- Unit test `tests/test_audio_stego.py` terverifikasi lulus.

### 5. Hasil Verifikasi Pengujian Akhir
- Seluruh 57 unit tests di folder `tests/` berhasil lulus: **`HASIL: 100% PASS (57 PASS, 0 GAGAL / 0 ERROR)`**.

### 6. Publikasi Rilis Resmi v1.2.0 & Persiapan Fase 4
- Publikasi Git Tag resmi `v1.2.0` via `tools/create_release.py`.
- Otomatisasi sinkronisasi filtered release ke branch `main` (100% bersih dari folder internal).
- Push tag `v1.2.0` dan branch `main` ke remote GitHub `https://github.com/useripx/McClean-Mac.git` memicu workflow rilis DMG di GitHub Actions.
- Menyiapkan `Docs/Implementation_plan_Fase_4.md` dan ADR-012 untuk implementasi Fase 4.

---

## 🚀 Rincian Lengkap Fase 4 (v2.0.0-macos)

### 1. Headless CLI Engine (`src/cli.py`)
- Membangun antarmuka baris perintah murni tanpa GUI yang mendukung perintah `inspect`, `clean`, `spoof`, dan `--version`.
- Mendukung format output JSON terstruktur (`--json`) untuk integrasi skrip dan automasi.
- Mengintegrasikan deteksi sub-perintah CLI pada `src/main.py`.
- Unit test `tests/test_cli.py` (7 tests lulus).

### 2. Integrasi Apple Shortcuts & Skrip Shell (`integrations/shortcuts/`)
- Membangun skrip shell automasi `integrations/shortcuts/clean_file.sh` dengan notifikasi banner desktop macOS.
- Menyusun dokumentasi panduan konfigurasi Shortcuts untuk menu Finder Share Sheet, Folder Actions, dan Siri di `integrations/shortcuts/README.md`.

### 3. macOS Menu Bar / Status Item App (`src/gui/menubar_app.py`)
- Menghadirkan ikon status item di bar atas layar macOS (`pystray`) dengan ukuran 22x22 standar macOS Menu Bar.
- Menu kilat: Quick Clean berkas, preset cepat (Developer, Media Sosial, Akademik), peluncuran GUI utama, dan Keluar.
- Unit test `tests/test_menubar_app.py` terverifikasi lulus.

### 4. Formula Distribusi Homebrew Cask (`packaging/homebrew/mrclean.rb`)
- Membangun formula Cask Ruby resmi yang menghubungkan instalasi biner DMG dari GitHub Releases dan membuat symlink binary `mrclean` di terminal.
- Menyusun panduan instalasi `brew install --cask mrclean` di `packaging/homebrew/README.md`.
- Unit test `tests/test_homebrew_cask.py` terverifikasi lulus.

### 5. Otomatisasi Notarisasi & Code Signing Apple Developer (`tools/notarize_mac.py`)
- Membangun skrip helper generator perintah `codesign --options runtime`, `xcrun notarytool submit`, dan `xcrun stapler staple`.
- Unit test `tests/test_notarization_script.py` terverifikasi lulus.

### 6. Hasil Pengujian Akhir (Testing Gate Pilar 6)
- Seluruh 71 unit tests di folder `tests/` berhasil lulus: **`HASIL: 100% PASS (71 PASS, 0 GAGAL / 0 ERROR)`**.
