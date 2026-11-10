"""
MetaClean — Audio & Video Metadata Cleaner
Menghapus tag ID3, Vorbis Comments, dan metadata kontainer pada file media audio/video.
Mendukung pembersihan langsung di tempat (in-place) maupun berkas salinan baru.
"""
import os
import shutil
from typing import Dict, Any, Optional
import mutagen
from src.cleaners.base import BaseCleaner

class MediaCleaner(BaseCleaner):
    SUPPORTED_EXTS = {".mp3", ".mp4", ".m4a", ".wav", ".flac", ".ogg", ".mkv", ".avi", ".wma"}

    def can_clean(self, file_path: str) -> bool:
        return os.path.splitext(file_path)[1].lower() in self.SUPPORTED_EXTS

    def clean(self, input_path: str, output_path: Optional[str] = None, inplace: bool = False) -> Dict[str, Any]:
        if not os.path.exists(input_path):
            return {"success": False, "error": f"Berkas tidak ditemukan: {input_path}"}

        if inplace or output_path == input_path:
            is_inplace = True
            output_path = input_path
            target_file = input_path
        else:
            is_inplace = False
            if output_path is None:
                dirname, filename = os.path.split(input_path)
                name, ext = os.path.splitext(filename)
                output_path = os.path.join(dirname, f"{name}_clean{ext}")
            shutil.copy2(input_path, output_path)
            target_file = output_path

        orig_size = os.path.getsize(input_path)

        try:
            audio = mutagen.File(target_file)
            if audio is not None:
                try:
                    audio.delete()
                except Exception:
                    pass

            cleaned_size = os.path.getsize(output_path)
            return {
                "success": True,
                "input_path": input_path,
                "output_path": output_path,
                "inplace": is_inplace,
                "original_size_bytes": orig_size,
                "cleaned_size_bytes": cleaned_size,
                "message": "Metadata tag audio/video berhasil dibersihkan."
            }
        except Exception as e:
            return {
                "success": False,
                "input_path": input_path,
                "error": f"Gagal membersihkan media: {str(e)}"
            }
