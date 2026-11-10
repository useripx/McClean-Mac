"""
MetaClean — Base Cleaner Class
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class BaseCleaner(ABC):
    """Interface dasar untuk seluruh modul pembersih metadata."""

    @abstractmethod
    def can_clean(self, file_path: str) -> bool:
        """Menentukan apakah cleaner ini dapat menangani format berkas."""
        pass

    @abstractmethod
    def clean(self, input_path: str, output_path: Optional[str] = None, inplace: bool = False) -> Dict[str, Any]:
        """
        Membersihkan metadata dari berkas input.
        Jika inplace=True, berkas asli langsung dibersihkan dan ditimpa di tempat.
        Jika inplace=False, disimpan ke output_path (default: <nama>_clean.<ext>).
        """
        pass
