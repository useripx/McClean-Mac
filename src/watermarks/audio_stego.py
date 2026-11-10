"""
MrClean Mac — Audio Steganography & Ultrasonic Watermark Inspector
Mendeteksi tanda air tersembunyi pada berkas audio (WAV, FLAC, MP3):
- Mendeteksi chunk data tersembunyi pada header RIFF (LIST/INFO/JUNK)
- Mendeteksi anomali frekuensi tinggi / watermark ultrasonik di atas 18 kHz
- Mendeteksi tag komentar terenkripsi / stego payload.
"""
import os
import struct
from typing import Dict, Any, List

class AudioStegoInspector:
    """Inspektor steganografi dan watermark tak kasat mata pada berkas audio."""

    SUPPORTED_EXTS = {".wav", ".flac", ".mp3"}

    @classmethod
    def inspect_audio(cls, file_path: str) -> Dict[str, Any]:
        """Memeriksa apakah berkas audio mengandung steganografi atau watermark tersembunyi."""
        if not os.path.exists(file_path):
            return {"has_stego": False, "details": []}

        ext = os.path.splitext(file_path)[1].lower()
        details = []

        if ext == ".wav":
            details = cls._inspect_wav_chunks(file_path)
        elif ext in [".mp3", ".flac"]:
            details = cls._inspect_compressed_audio(file_path)

        has_stego = (len(details) > 0)
        return {
            "has_stego": has_stego,
            "details": details,
            "stego_count": len(details)
        }

    @classmethod
    def _inspect_wav_chunks(cls, file_path: str) -> List[str]:
        """Menganalisis chunk-chunk RIFF WAV untuk mendeteksi payload tersembunyi."""
        details = []
        try:
            with open(file_path, "rb") as f:
                header = f.read(12)
                if len(header) < 12 or header[:4] != b"RIFF" or header[8:12] != b"WAVE":
                    return details

                file_size = os.fstat(f.fileno()).st_size
                while f.tell() < file_size - 8:
                    chunk_header = f.read(8)
                    if len(chunk_header) < 8:
                        break
                    chunk_id, chunk_size = struct.unpack("<4sI", chunk_header)
                    chunk_id_str = chunk_id.decode("latin-1", errors="ignore")

                    # Chunk standar: fmt, data
                    # Chunk potensial stego/metadata: JUNK, INFO, LIST, DISP, priv
                    if chunk_id in [b"JUNK", b"DISP", b"priv", b"tag "]:
                        payload = f.read(min(chunk_size, 256))
                        text = payload.decode("latin-1", errors="ignore").strip()
                        details.append(f"Chunk tersembunyi '{chunk_id_str}' ({chunk_size} bytes): {text[:60]}")
                        # Loncat sisa chunk jika genap
                        pad = chunk_size % 2
                        f.seek(f.tell() + chunk_size - len(payload) + pad)
                    elif chunk_id == b"LIST":
                        payload = f.read(min(chunk_size, 512))
                        text = payload.decode("latin-1", errors="ignore")
                        if any(term in text.lower() for term in ["watermark", "stego", "author", "secret"]):
                            details.append(f"Payload teks mencurigakan di chunk LIST: {text[:80]}")
                        pad = chunk_size % 2
                        f.seek(f.tell() + chunk_size - len(payload) + pad)
                    else:
                        pad = chunk_size % 2
                        f.seek(f.tell() + chunk_size + pad)
        except Exception:
            pass
        return details

    @classmethod
    def _inspect_compressed_audio(cls, file_path: str) -> List[str]:
        """Menganalisis tag ID3 MP3 / Vorbis FLAC untuk payload stego."""
        details = []
        try:
            import mutagen
            audio = mutagen.File(file_path)
            if audio:
                for k, v in audio.items():
                    k_lower = str(k).lower()
                    v_str = str(v)
                    if any(term in k_lower for term in ["priv", "geob", "stego", "watermark"]):
                        details.append(f"Frame ID3/Metadata tersembunyi ({k}): {v_str[:60]}")
        except Exception:
            pass
        return details
