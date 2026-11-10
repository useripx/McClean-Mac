"""
MetaClean — Base Inspector Class
"""
from abc import ABC, abstractmethod
from typing import Dict, Any

class BaseInspector(ABC):
    """Interface dasar untuk seluruh modul ekstraksi metadata."""

    @abstractmethod
    def can_inspect(self, file_path: str) -> bool:
        """Menentukan apakah inspektor ini dapat menangani tipe file yang diberikan."""
        pass

    @abstractmethod
    def inspect(self, file_path: str) -> Dict[str, Any]:
        """
        Mengekstrak metadata dari berkas target.
        Mengembalikan kamus data terstruktur.
        """
        pass

