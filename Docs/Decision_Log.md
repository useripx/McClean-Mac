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
