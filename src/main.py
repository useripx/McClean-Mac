"""
MetaClean — Main Application Entry Point
"""
import sys
import os

# Menambahkan root project ke sys.path agar impor modul berjalan lancar
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.gui.app import main

if __name__ == "__main__":
    main()

