"""
MetaClean — Audio & Video Inspector
Mengekstrak tag ID3, Metadata Kontainer, Bitrate, Durasi, dan Perangkat Lunak Encoder media audio/video.
"""
import os
from typing import Dict, Any
import mutagen
from src.inspectors.base import BaseInspector

class MediaInspector(BaseInspector):
    SUPPORTED_EXTS = {".mp3", ".mp4", ".m4a", ".wav", ".flac", ".ogg", ".mkv", ".avi", ".wma"}

    def can_inspect(self, file_path: str) -> bool:
        return os.path.splitext(file_path)[1].lower() in self.SUPPORTED_EXTS

    def inspect(self, file_path: str) -> Dict[str, Any]:
        result = {
            "file_path": file_path,
            "file_name": os.path.basename(file_path),
            "file_size": os.path.getsize(file_path) if os.path.exists(file_path) else 0,
            "category": "media",
            "has_metadata": False,
            "metadata_count": 0,
            "categories": {},
            "has_ai_watermark": False,
            "watermarks_detected": []
        }

        try:
            audio = mutagen.File(file_path)
            if audio is None:
                result["categories"]["Informasi"] = {"Pesan": "Format media tidak mendukung pembacaan tag mutagen."}
                return result

            # 1. Info Teknis Stream
            stream_info = {}
            if hasattr(audio, "info") and audio.info:
                if hasattr(audio.info, "length"):
                    mins, secs = divmod(int(audio.info.length), 60)
                    stream_info["Durasi"] = f"{mins:02d}:{secs:02d} ({audio.info.length:.1f} detik)"
                if hasattr(audio.info, "bitrate") and audio.info.bitrate:
                    stream_info["Bitrate"] = f"{audio.info.bitrate // 1000} kbps"
                if hasattr(audio.info, "sample_rate") and audio.info.sample_rate:
                    stream_info["Sample Rate"] = f"{audio.info.sample_rate} Hz"
                if hasattr(audio.info, "channels") and audio.info.channels:
                    stream_info["Kanal Suara"] = f"{audio.info.channels} channel"

            if stream_info:
                result["categories"]["Informasi Stream Media"] = stream_info

            # 2. Tag Metadata (ID3 / MP4 Tags / Vorbis Comments)
            tag_data = {}
            if audio.tags:
                for k, v in audio.tags.items():
                    key_str = str(k)
                    val_str = str(v)
                    tag_data[key_str] = val_str

                    # Deteksi jejak AI audio generator (seperti Suno, Udio, dll.)
                    lower_val = val_str.lower()
                    if any(term in lower_val for term in ["suno", "udio", "ai-generated", "elevenlabs"]):
                        result["has_ai_watermark"] = True
                        result["watermarks_detected"].append(f"AI Audio tag pada {key_str}: {val_str}")

            if tag_data:
                result["categories"]["Tag Metadata Audio/Video"] = tag_data

            result["metadata_count"] = len(tag_data)
            result["has_metadata"] = len(tag_data) > 0

        except Exception as e:
            result["categories"]["Error"] = {"Pesan": f"Gagal membaca metadata media: {str(e)}"}

        return result

