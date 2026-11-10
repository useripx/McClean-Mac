# 🍺 Distribusi Homebrew Cask — MrClean Mac

Panduan resmi instalasi MrClean Mac menggunakan manajer paket **Homebrew**.

---

## 🚀 Cara Instalasi untuk Pengguna Mac

Pengguna macOS dapat memasang MrClean Mac dengan satu baris perintah terminal:

```bash
# 1. Tambahkan tap resmi MrClean
brew tap useripx/mrclean

# 2. Pasang aplikasi biner Cask
brew install --cask mrclean
```

Setelah terpasang:
- **Aplikasi GUI**: Berada di folder `/Applications/MrClean.app` dan dapat dicari via Spotlight (`⌘ Space`).
- **Terminal CLI**: Otomatis tersedia di seluruh terminal Mac Anda dengan perintah:
  ```bash
  mrclean --help
  mrclean inspect foto.jpg
  mrclean clean dokumen.docx --preset academic
  ```

---

## 🔄 Pembaruan Versi (Upgrade)

Untuk memperbarui MrClean ke versi rilis terbaru:
```bash
brew upgrade --cask mrclean
```

---

## 🗑️ Pencopotan (Uninstall)

Untuk menghapus aplikasi dan seluruh preferensinya secara bersih:
```bash
brew uninstall --zap --cask mrclean
```
