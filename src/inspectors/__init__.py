"""
MetaClean — Inspector Dispatcher
Menentukan dan menjalankan inspektor yang tepat untuk setiap berkas.
"""
from typing import Dict, Any, List
from src.inspectors.image_inspector import ImageInspector
from src.inspectors.pdf_inspector import PdfInspector
from src.inspectors.docx_inspector import DocxInspector
from src.inspectors.media_inspector import MediaInspector
from src.inspectors.text_inspector import TextInspector
from src.inspectors.risk_scorer import calculate_privacy_risk
from src.inspectors.ai_forensics import AIForensicsInspector

ALL_INSPECTORS = [
    ImageInspector(),
    PdfInspector(),
    DocxInspector(),
    MediaInspector(),
    TextInspector()
]

def inspect_file(file_path: str) -> Dict[str, Any]:
    """Mendeteksi jenis file dan menjalankan inspektor yang sesuai serta menghitung skor risiko privasi."""
    result = None
    for inspector in ALL_INSPECTORS:
        if inspector.can_inspect(file_path):
            result = inspector.inspect(file_path)
            break

    if result is None:
        # Fallback untuk file yang belum didukung spesifik
        result = {
            "file_path": file_path,
            "file_name": file_path.split("/")[-1].split("\\")[-1],
            "category": "unknown",
            "has_metadata": False,
            "metadata_count": 0,
            "categories": {
                "Info": {"Status": "Format berkas belum didukung untuk inspeksi mendalam."}
            },
            "has_ai_watermark": False,
            "watermarks_detected": []
        }

    # Analisis forensik AI tambahan (Prompt & C2PA)
    try:
        ai_info = AIForensicsInspector.inspect_ai_metadata(file_path)
        result["ai_forensics"] = ai_info
        if ai_info.get("is_ai_generated"):
            result["has_ai_watermark"] = True
            gen = ai_info.get("generator") or "AI Generatif"
            prompt_preview = ai_info.get("prompt")
            msg = f"Jejak AI ({gen})" if not prompt_preview else f"Jejak AI ({gen}): {prompt_preview[:40]}..."
            if msg not in result["watermarks_detected"]:
                result["watermarks_detected"].append(msg)
    except Exception:
        pass

    # Hitung skor ancaman privasi secara otomatis
    result["risk_assessment"] = calculate_privacy_risk(result)
    return result

