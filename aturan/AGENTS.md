# AGENTS.md — Pedoman AI Agent untuk Proyek MrClean Mac

> **PERINGATAN WAJIB:**  
> Seluruh AI Agent (Antigravity, Gemini, Claude, Cursor, dll.) **WAJIB** membaca dan mematuhi seluruh aturan kerja yang tercantum di [`Docs/universal-rule.md`](universal-rule.md) sebelum melakukan tindakan apa pun pada repositori ini.

---

## 🏛️ Ringkasan Aturan Penting (macOS Edition)

1. **Approval Gate (Pilar 1):** Dilarang keras membuat atau mengedit kode aplikasi sebelum rencana implementasi tertulis ([`Docs/Implementation_plan.md`](Implementation_plan_mac.md)) disetujui secara eksplisit oleh **Yogi Ario**.
2. **Branching & Clean Main (Pilar 2):** Branch `main` terkunci murni untuk biner/runtime produksi. Semua pekerjaan dilakukan di branch `develop` atau `feature/*`. Folder catatan pengembang (`Docs/`, `changelog/`) dilarang masuk ke `main`.
3. **Asset Protection (Pilar 4):** Folder [`Material/`](../../Material/) bersifat **READ-ONLY**. Format ikon resmi untuk macOS wajib menggunakan `assets/icon.icns`.
4. **Dokumentasi (Pilar 5):** Wajib memperbarui `Docs/Task_Status.md` dan `Docs/Decision_Log.md`, serta membuat catatan bertimestamp di `changelog/changelog<jam><ampm><ddmmyyyy>.md` secara flat.
5. **Testing Gate (Pilar 6):** Fitur hanya boleh dinyatakan selesai jika seluruh pengujian di `tests/` menghasilkan **100% PASS (0 GAGAL / 0 ERROR)** di lingkungan macOS / runner GitHub Actions.
6. **Adaptasi Native macOS (Pilar 7):** Wajib mendukung font Apple (`SF Pro Text`), pintasan `⌘ Command`, Retina Display HiDPI (2x), dan Finder Quick Action.
7. **Chat Backup (Pilar 8):** Di setiap akhir respon, tanyakan secara proaktif kepada Mas Yogi Ario apakah ingin mencadangkan riwayat percakapan ke `Docs/chat/riwayat<ddmmyyyy>.md`.
