"""
MetaClean — AI Generative & C2PA Forensics Inspector
Mengekstrak prompt dan parameter pembuatan gambar AI (Midjourney, Stable Diffusion, DALL-E)
serta mendeteksi segmen manifes asal-usul konten C2PA (Content Credentials).
"""
import os
import json
import re
from typing import Dict, Any, Optional
from PIL import Image

class AIForensicsInspector:
    """Inspektor forensik khusus untuk metadata alat AI generatif dan C2PA."""

    @classmethod
    def inspect_ai_metadata(cls, file_path: str) -> Dict[str, Any]:
        """
        Menganalisis berkas gambar untuk mendeteksi jejak AI generatif, prompt asli, dan C2PA.
        """
        result = {
            "is_ai_generated": False,
            "generator": None,
            "prompt": None,
            "parameters": {},
            "has_c2pa": False,
            "c2pa_details": None
        }

        if not os.path.exists(file_path):
            return result

        ext = os.path.splitext(file_path)[1].lower()

        # 1. Cek Manifes C2PA pada bytes berkas
        try:
            with open(file_path, "rb") as f:
                header = f.read(1024 * 512)
                if b"c2pa" in header or b"jumbf" in header or b"contentCredentials" in header:
                    result["is_ai_generated"] = True
                    result["has_c2pa"] = True
                    result["generator"] = "C2PA Content Credentials (Adobe/Firefly)"
                    result["c2pa_details"] = "Segmen manifes provenance C2PA/JUMBF terdeteksi di dalam struktur berkas."
        except Exception:
            pass

        # 2. Cek metadata gambar (PNG chunk / EXIF)
        if ext in [".png", ".jpg", ".jpeg", ".webp"]:
            try:
                with Image.open(file_path) as img:
                    info = getattr(img, "info", {})

                    # A. Stable Diffusion / WebUI PNG chunks
                    if "parameters" in info:
                        result["is_ai_generated"] = True
                        result["generator"] = "Stable Diffusion"
                        raw_params = str(info["parameters"])
                        # Pisahkan prompt dari parameter teknis (Negative prompt, Steps, Seed)
                        lines = raw_params.split("\n")
                        result["prompt"] = lines[0].strip() if lines else raw_params
                        result["parameters"]["Raw Parameters"] = raw_params

                    # B. Midjourney metadata
                    elif "prompt" in info:
                        result["is_ai_generated"] = True
                        result["generator"] = "Midjourney"
                        result["prompt"] = str(info["prompt"]).strip()

                    elif "Description" in info and "prompt" in str(info.get("Description", "")).lower():
                        result["is_ai_generated"] = True
                        result["generator"] = "AI Generatif"
                        result["prompt"] = str(info["Description"]).strip()

                    # C. ComfyUI / Workflow chunks
                    elif "workflow" in info or "prompt" in info:
                        result["is_ai_generated"] = True
                        result["generator"] = "ComfyUI / Nodes Workflow"
                        result["parameters"]["Workflow"] = "Graf node generasi ComfyUI terdeteksi"

                    # D. Periksa EXIF UserComment pada JPEG
                    exif = img.getexif()
                    if exif:
                        for tag_id, val in exif.items():
                            val_str = str(val)
                            if any(k in val_str.lower() for k in ["prompt:", "steps:", "seed:", "dall-e", "midjourney"]):
                                result["is_ai_generated"] = True
                                if not result["generator"]:
                                    result["generator"] = "DALL-E / Generative Model"
                                result["prompt"] = val_str[:300]
                                break

            except Exception:
                pass

        return result
