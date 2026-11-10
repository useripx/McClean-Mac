# Decision Log (ADR) — MrClean Mac

> **LOG KEPUTUSAN ARSITEKTUR & DESAIN TEKNIS**  
> **OTORITAS:** Yogi Ario  

---

## 🏛️ Daftar Rekaman Keputusan (Architecture Decision Records)

### ADR-001: Standarisasi Kerangka Kerja Universal macOS (8 Pilar)
- **Tanggal:** 10 November 2026
- **Status:** DITERIMA / AKTIF
- **Konteks:** Proyek MrClean Mac memerlukan tata kelola ketat untuk menjaga kebersihan branch `main`, perlindungan aset, dan verifikasi otomatis tanpa regresi.
- **Keputusan:** Mengadopsi 8 Pilar Standar Kerja Universal yang tercantum dalam `aturan/universal-rule.md`.
- **Konsekuensi:** Setiap perubahan kode wajib melalui *Approval Gate*, seluruh pengujian wajib 100% PASS, dan branch `main` dilarang memuat catatan internal pengembang (`Docs/`, `changelog/`).

### ADR-002: Standar Badges dan Presentasi Repositori Publik
- **Tanggal:** 10 November 2026
- **Status:** DITERIMA / AKTIF
- **Konteks:** Repositori GitHub `useripx/McClean-Mac` memerlukan representasi publik yang informatif, menarik, dan transparan.
- **Keputusan:** Memasang badges Shields.io untuk ukuran repositori (*repo-size*), forks, stars, issues, lisensi MIT, platform macOS, versi Python 3.13+, serta badge keamanan offline & zero-telemetry, disertai logo resmi di bagian atas `README.md`.
- **Konsekuensi:** Tampilan repositori profesional dan memenuhi standar publikasi open-source modern.

### ADR-003: Arsitektur Backend Agnostic & Porting Khusus macOS
- **Tanggal:** 10 November 2026
- **Status:** DITERIMA / AKTIF
- **Konteks:** Backend inspeksi dan pembersihan metadata bersifat murni Python (Pillow, PyPDF, mutagen, python-docx), sedangkan GUI menggunakan CustomTkinter dengan penyesuaian event Apple Command (`⌘`), font SF Pro, dan deteksi mode gelap via `darkdetect`.
- **Keputusan:** Mempertahankan logika backend 100% identik dengan versi Windows (paritas 11 fitur) dengan adaptasi spesifik macOS pada layer GUI, path developer regex (`/Users/user`), dan integrasi Finder Quick Action.
- **Konsekuensi:** Konsistensi hasil inspeksi dan pembersihan antar-platform terjamin 100%.

### ADR-004: Integrasi Sistem Native macOS (Finder Quick Actions & Notifikasi)
- **Tanggal:** 10 November 2026
- **Status:** DITERIMA / AKTIF
- **Konteks:** Di macOS tidak terdapat Windows Registry HKCU. Pengguna Mac memerlukan cara cepat membersihkan file langsung dari Finder.
- **Keputusan:** Membangun `MacShellIntegration` di `src/utils/mac_shell_integration.py` yang memasang bundel Quick Action Automator `.workflow` di `~/Library/Services/` dan mengirim notifikasi banner desktop native via `osascript`.
- **Konsekuensi:** Pengguna Mac dapat membersihkan berkas langsung dari menu klik kanan Finder tanpa hak Administrator.

### ADR-005: Pembangkitan Multi-Resolusi Ikon Apple ICNS
- **Tanggal:** 10 November 2026
- **Status:** DITERIMA / AKTIF
- **Konteks:** macOS mewajibkan format ikon `.icns` untuk tampilan Dock dan bundel `.app` Retina.
- **Keputusan:** Memperbarui `src/utils/icon_converter.py` untuk mengonversi `asset/logo.png` (1024x1024) langsung menjadi format biner Apple `assets/icon.icns` yang mencakup layer multi-resolusi 16x16 hingga 1024x1024 @2x Retina.
- **Konsekuensi:** Ikon aplikasi tampil tajam dan bebas pecah pada seluruh resolusi monitor Apple.

### ADR-006: Otomatisasi Cloud Packaging via GitHub Actions (`macos-latest`)
- **Tanggal:** 10 November 2026
- **Status:** DITERIMA / AKTIF
- **Konteks:** Pengembang memerlukan cara membuat bundel `.app` dan `.dmg` secara gratis dan otomatis tanpa harus memiliki perangkat keras Mac fisik lokal.
- **Keputusan:** Menyiapkan alur kerja CI/CD `.github/workflows/build-mac.yml` yang berjalan di runner native Apple Silicon M-series (`macos-latest`) pada setiap push ke branch `develop`/`main` atau tag rilis.
- **Konsekuensi:** Installer `MrClean-macOS.dmg` dihasilkan secara otomatis di cloud GitHub.

### ADR-007: Penanganan Drag & Drop Native dan macOS OpenDocument Callback
- **Tanggal:** 10 November 2026
- **Status:** DITERIMA / AKTIF
- **Konteks:** Pengguna desktop macOS menginginkan kemudahan menarik (*drag-and-drop*) berkas langsung ke jendela GUI atau ikon di Dock tanpa membuka file picker.
- **Keputusan:** Mengimplementasikan parser drop path pintar `parse_dropped_files` dan binding event `::tk::mac::OpenDocument` pada `src/gui/app.py` tanpa mewajibkan dependensi C-extension pihak ketiga.
- **Konsekuensi:** UX lebih mulus, stabil, dan ramah pengguna Apple.

### ADR-008: Release Automation SemVer & Tagged Release Pipeline
- **Tanggal:** 10 November 2026
- **Status:** DITERIMA / AKTIF
- **Konteks:** Pengembang membutuhkan kemudahan memublikasikan versi rilis dengan tag Git resmi tanpa risiko melanggar kebersihan branch `main`.
- **Keputusan:** Membangun `tools/create_release.py` yang memvalidasi SemVer, memastikan testing gate 100% PASS, menyinkronkan rilis bersih ke `main`, dan memicu workflow rilis GitHub Actions.
- **Konsekuensi:** Distribusi versi rilis terstandarisasi, aman, dan dapat diulang (*reproducible*).
