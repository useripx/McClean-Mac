"""
Editor Metadata Audio & Video untuk Mrclean
Mendukung penyuntingan selektif tag media (Title, Artist, Album, Date/Year, Genre)
secara lossless tanpa re-encoding aliran audio/video.
"""

import os
import shutil
from typing import Dict, Any
import mutagen
from mutagen.easyid3 import EasyID3
from src.editors.base import BaseMetadataEditor

class MediaEditor(BaseMetadataEditor):
    """Editor metadata selektif untuk media audio dan video (MP3, MP4, M4A, FLAC, OGG)."""

    FIELDS = ["Title", "Artist", "Album", "Date", "Genre"]

    def _get_output_path(self, file_path: str, inplace: bool) -> str:
        if inplace:
            return file_path
        base, ext = os.path.splitext(file_path)
        return f"{base}_edited{ext}"

    def get_editable_fields(self, file_path: str) -> Dict[str, str]:
        results = {f: "" for f in self.FIELDS}
        try:
            audio = mutagen.File(file_path, easy=True)
            if audio is not None and audio.tags:
                tags = audio.tags
                for f in self.FIELDS:
                    k = f.lower()
                    if k in tags and tags[k]:
                        results[f] = str(tags[k][0])
        except Exception as e:
            # Fallback jika EasyID3 belum diinisialisasi pada MP3
            try:
                audio = EasyID3(file_path)
                for f in self.FIELDS:
                    k = f.lower()
                    if k in audio and audio[k]:
                        results[f] = str(audio[k][0])
            except Exception:
                pass
        return results

    def save_fields(self, file_path: str, updated_fields: Dict[str, str], inplace: bool = True) -> Dict[str, Any]:
        output_path = self._get_output_path(file_path, inplace)
        try:
            if not inplace and output_path != file_path:
                shutil.copy2(file_path, output_path)

            target = output_path
            try:
                audio = mutagen.File(target, easy=True)
            except Exception:
                audio = None

            if audio is None or audio.tags is None:
                # Coba inisialisasi EasyID3 jika berkas adalah MP3
                if target.lower().endswith(".mp3"):
                    try:
                        audio = EasyID3(target)
                    except Exception:
                        try:
                            audio = mutagen.File(target)
                            audio.add_tags()
                            audio.save()
                            audio = EasyID3(target)
                        except Exception:
                            pass

            if audio is not None:
                for f in self.FIELDS:
                    if f in updated_fields:
                        val = updated_fields[f]
                        k = f.lower()
                        if val:
                            audio[k] = [val]
                        elif k in audio:
                            del audio[k]
                audio.save()
            else:
                return {
                    "success": False,
                    "output_path": None,
                    "error": "Format media tidak mendukung penulisan tag ID3 langsung."
                }

            return {
                "success": True,
                "output_path": output_path,
                "error": None
            }
        except Exception as e:
            return {
                "success": False,
                "output_path": None,
                "error": str(e)
            }

