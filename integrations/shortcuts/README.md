# ⚡ Integrasi Apple Shortcuts (Aplikasi Pintasan macOS) — MrClean Mac

> **Panduan Resmi Automasi macOS untuk MrClean Mac (v2.0.0-macos)**  
> Memungkinkan pembersihan metadata langsung melalui **Finder Share Sheet (Quick Action)**, **Folder Actions**, dan **Perintah Suara Siri**.

---

## 🧭 Ikhtisar Kemampuan

Dengan Apple Shortcuts, pengguna dapat:
1. **Membersihkan Foto/Dokumen Sekali Klik**: Melalui menu klik kanan di Finder ➜ *Quick Actions* ➜ *Bersihkan dengan MrClean*.
2. **Automasi Folder Masuk**: Setiap kali berkas baru ditaruh di folder unduhan tertentu, MrClean langsung membersihkan metadata secara otomatis.
3. **Integrasi Perintah Suara Siri**: *"Hey Siri, bersihkan foto terakhir."*

---

## 🛠️ Resep Pintasan 1: Pembersihan Cepat dari Menu Finder (Share Sheet)

Langkah menyusun pintasan di aplikasi **Shortcuts (Pintasan)** macOS:

1. Buka aplikasi **Shortcuts** di Mac (`/System/Applications/Shortcuts.app`).
2. Klik tombol **`+`** (Buat Pintasan Baru).
3. Beri nama: **"Bersihkan Metadata (MrClean)"**.
4. Di panel kanan (Shortcut Details), centang:
   - ✅ **Use as Quick Action**
   - ✅ **Finder**
   - Pilih jenis masukan: **Files** & **Images**.
5. Tambahkan aksi: **Run Shell Script**:
   - Shell: `/bin/bash`
   - Pass Input: **as arguments**
   - Isi skrip:
     ```bash
     /Applications/MrClean.app/Contents/MacOS/MrClean clean "$@" --inplace
     osascript -e 'display notification "Metadata berhasil dibersihkan!" with title "MrClean Mac" sound name "Glass"'
     ```
6. Simpan pintasan. Kini pintasan langsung muncul saat Anda mengklik kanan berkas di Finder!

---

## 📂 Resep Pintasan 2: Pembersihan Berkas Otomatis via Folder Action

1. Di aplikasi Shortcuts, pilih tab **Automations** atau gunakan aplikasi **Automator**.
2. Pilih pemicu: **Folder Action** pada folder `~/Downloads/AutoClean/`.
3. Pasang aksi eksekusi shell yang memanggil `clean_file.sh`:
   ```bash
   bash /path/to/McClean-Mac/integrations/shortcuts/clean_file.sh social "$@"
   ```
4. Setiap berkas yang dipindahkan ke folder tersebut akan langsung dibersihkan dengan preset media sosial.

---

## 🎙️ Resep Pintasan 3: Perintah Suara Siri

1. Buat pintasan baru dengan nama panggilan: **"Bersihkan Foto Terakhir"**.
2. Tambahkan aksi: **Get Latest Photos** (Ambil 1 foto terbaru).
3. Sambungkan ke aksi **Run Shell Script**:
   ```bash
   /Applications/MrClean.app/Contents/MacOS/MrClean clean "$1" --preset social --inplace
   ```
4. Ucapkan kepada Siri: *"Hey Siri, bersihkan foto terakhir"*.

---

## 🔒 Privasi & Keamanan 100% Offline
Seluruh eksekusi skrip Apple Shortcuts berjalan secara lokal di Mac Anda tanpa mengirimkan data, byte gambar, atau identitas perangkat ke jaringan eksternal (*Zero-Telemetry*).
