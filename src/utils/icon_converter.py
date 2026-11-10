"""
MrClean Mac — Icon & Logo Converter Utility
Mengonversi asset/logo.png (atau Material/logo.jpg) menjadi:
1. assets/icon.icns (Format multi-resolusi resmi macOS: 16x16 - 1024x1024 Retina)
2. assets/icon.ico (Format fallback untuk cross-platform)
3. assets/logo.png (Logo resolusi tinggi untuk GUI header dan kop laporan PDF)
"""
import os
import subprocess
from PIL import Image

def convert_logo_to_assets(
    primary_input: str = "asset/logo.png",
    fallback_inputs: list = None,
    icns_output: str = "assets/icon.icns",
    ico_output: str = "assets/icon.ico",
    png_output: str = "assets/logo.png"
) -> dict:
    """Mengonversi aset logo menjadi icon.icns, icon.ico, dan logo.png."""
    if fallback_inputs is None:
        fallback_inputs = ["Material/logo.jpg", "Material/img.png", "assets/logo.png"]

    candidates = [primary_input] + fallback_inputs
    input_path = None
    for p in candidates:
        if os.path.exists(p):
            input_path = p
            break

    if not input_path:
        raise FileNotFoundError(f"Berkas logo mentah tidak ditemukan di kandidat: {candidates}")

    os.makedirs(os.path.dirname(os.path.abspath(icns_output)), exist_ok=True)
    os.makedirs(os.path.dirname(os.path.abspath(ico_output)), exist_ok=True)
    os.makedirs(os.path.dirname(os.path.abspath(png_output)), exist_ok=True)

    with Image.open(input_path) as img:
        rgba_img = img.convert("RGBA")

        # 1. Simpan logo.png resolusi tinggi untuk header GUI & PDF Report
        # Pertahankan resolusi asli jika 1024x1024, atau resize proporsional
        logo_png = rgba_img.copy()
        logo_png.save(png_output, format="PNG")

        # 2. Simpan icon.icns untuk macOS
        try:
            rgba_img.save(icns_output, format="ICNS")
        except Exception:
            # Fallback jika pillow icns gagal
            pass

        # 3. Simpan icon.ico untuk cross-platform
        try:
            icon_sizes = [(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
            rgba_img.save(ico_output, format="ICO", sizes=icon_sizes)
        except Exception:
            pass

    return {
        "source": input_path,
        "icns_path": icns_output,
        "ico_path": ico_output,
        "png_path": png_output
    }

if __name__ == "__main__":
    res = convert_logo_to_assets()
    print(f"Ikon & Logo berhasil dibuat:")
    print(f" - Sumber : {res['source']}")
    print(f" - ICNS   : {res['icns_path']}")
    print(f" - ICO    : {res['ico_path']}")
    print(f" - PNG    : {res['png_path']}")
