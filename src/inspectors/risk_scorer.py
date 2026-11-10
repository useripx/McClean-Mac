"""
MetaClean — Privacy Risk Scorer
Menghitung skor ancaman privasi (0–100%) dan klasifikasi tingkat bahaya (Kritis, Sedang, Aman)
berdasarkan sensitivitas metadata yang ditemukan (GPS, Serial Number, Author, Path Lokal, AI Watermark).
"""
import re
from typing import Dict, Any, List

def calculate_privacy_risk(inspection_result: Dict[str, Any]) -> Dict[str, Any]:
    """
    Menghitung skor risiko privasi (0-100%) dan memberikan evaluasi tingkat bahaya.
    
    Tingkat Bahaya:
    - KRITIS (≥ 70%): Warna #e53935 (Merah) — Bocor lokasi GPS, Serial Number, atau Identitas.
    - SEDANG (30 - 69%): Warna #fb8c00 (Oranye) — Bocor tipe device, software editor, atau AI watermark.
    - AMAN (< 30%): Warna #43a047 (Hijau) — Bersih atau hanya metadata teknis standar.
    """
    if not inspection_result:
        return {
            "score": 0,
            "level": "AMAN",
            "color": "#43a047",
            "reasons": ["Tidak ada metadata terdeteksi."],
            "recommendation": "Berkas bersih dan aman untuk dibagikan."
        }

    categories = inspection_result.get("categories", {})
    has_ai_watermark = inspection_result.get("has_ai_watermark", False)
    total_tags = inspection_result.get("metadata_count", 0)

    # Jika sama sekali tidak ada metadata dan tidak ada watermark AI
    if not inspection_result.get("has_metadata") and not has_ai_watermark:
        return {
            "score": 0,
            "level": "AMAN",
            "color": "#43a047",
            "reasons": ["Berkas bersih tanpa metadata sensitif."],
            "recommendation": "Berkas aman untuk dibagikan ke publik."
        }

    points = 0
    reasons: List[str] = []

    # Flatten all key-values for deep inspection
    flat_data: Dict[str, str] = {}
    for cat_name, cat_dict in categories.items():
        if isinstance(cat_dict, dict):
            for k, v in cat_dict.items():
                flat_data[f"{cat_name}.{k}"] = str(v)

    # 1. Deteksi GPS (Bobot Kritis: +40 poin)
    has_gps = False
    if "Lokasi GPS" in categories and categories["Lokasi GPS"]:
        has_gps = True
    else:
        for k in flat_data:
            k_lower = k.lower()
            if any(term in k_lower for term in ["gps", "latitude", "longitude", "koordinat"]):
                has_gps = True
                break

    if has_gps:
        points += 40
        reasons.append("Koordinat lokasi GPS presisi terdeteksi.")

    # 2. Deteksi Serial Number Perangkat (Bobot Kritis: +30 poin)
    has_serial = False
    for k in flat_data:
        k_lower = k.lower()
        if any(term in k_lower for term in ["serialnumber", "serial_number", "bodyserial", "lensserial"]):
            has_serial = True
            break
    if has_serial:
        points += 30
        reasons.append("Nomor seri perangkat (Serial Number) terdeteksi.")

    # 3. Deteksi Nama Lengkap Author / Pembuat Dokumen (Bobot Tinggi: +25 poin)
    has_author = False
    for k, v in flat_data.items():
        k_lower = k.lower()
        if any(term in k_lower for term in ["author", "creator", "artist", "xp_author", "owner", "last_modified_by"]):
            # Pastikan nilainya bukan string kosong atau nilai default
            if v and v.strip() and v.lower() not in ["none", "unknown", ""]:
                has_author = True
                break
    if has_author:
        points += 25
        reasons.append("Nama pembuat/author dokumen atau gambar terdeteksi.")

    # 4. Deteksi Path Direktori Lokal / Username Sistem (Bobot Tinggi: +25 poin)
    has_local_path = False
    path_pattern = re.compile(r"([A-Za-z]:\\[Uu]sers\\[^\\]+|/home/[^/]+|/Users/[^/]+)", re.IGNORECASE)
    for v in flat_data.values():
        if path_pattern.search(v):
            has_local_path = True
            break
    if has_local_path:
        points += 25
        reasons.append("Jalur direktori komputer lokal (Username sistem) terdeteksi.")

    # 5. Deteksi Tanda Air AI / Steganografi Tersembunyi (Bobot Sedang: +20 poin)
    if has_ai_watermark:
        points += 20
        reasons.append("Tanda air AI / jejak steganografi tak kasat mata terdeteksi.")

    # 6. Deteksi Merek & Model Kamera / Perangkat (Bobot Sedang: +15 poin)
    has_device = False
    for k in flat_data:
        k_lower = k.lower()
        if any(term in k_lower for term in ["make", "model", "cameramodel", "device_model"]):
            has_device = True
            break
    if has_device:
        points += 15
        reasons.append("Merek dan model perangkat kamera/smartphone terdeteksi.")

    # 7. Deteksi Software Editor (Bobot Sedang: +15 poin)
    has_software = False
    for k, v in flat_data.items():
        k_lower = k.lower()
        if any(term in k_lower for term in ["software", "producer", "application", "creatortool"]):
            if v and v.strip() and v.lower() not in ["none", ""]:
                has_software = True
                break
    if has_software:
        points += 15
        reasons.append("Informasi software/aplikasi pengeditan terdeteksi.")

    # 8. Deteksi Riwayat Tanggal & Waktu (Bobot Rendah: +10 poin)
    has_dates = False
    for k in flat_data:
        k_lower = k.lower()
        if any(term in k_lower for term in ["datetime", "creationdate", "moddate", "modifydate"]):
            has_dates = True
            break
    if has_dates:
        points += 10
        reasons.append("Riwayat tanggal dan waktu pembuatan/pengeditan terdeteksi.")

    # 9. Fallback jika metadata ada tapi belum tergolong kriteria di atas
    if points == 0 and total_tags > 0:
        points = 10
        reasons.append("Metadata teknis standar berkas terdeteksi.")

    # Kalkulasi skor final (0 - 100)
    score = min(100, max(0, points))

    # Klasifikasi tingkat bahaya
    if score >= 70:
        level = "KRITIS"
        color = "#e53935"  # Merah
        recommendation = "Sangat disarankan untuk dibersihkan sebelum dibagikan ke publik!"
    elif score >= 30:
        level = "SEDANG"
        color = "#fb8c00"  # Oranye
        recommendation = "Disarankan dibersihkan jika ingin menyamarkan perangkat atau software."
    else:
        level = "AMAN"
        color = "#43a047"  # Hijau
        recommendation = "Berkas memiliki risiko rendah, relatif aman dari kebocoran data."

    return {
        "score": score,
        "level": level,
        "color": color,
        "reasons": reasons if reasons else ["Hanya metadata teknis standar."],
        "recommendation": recommendation
    }
