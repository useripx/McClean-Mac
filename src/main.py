"""
MetaClean — Main Application Entry Point
"""
import sys
import os

# Menambahkan root project ke sys.path agar impor modul berjalan lancar
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.gui.app import main as run_gui_app

def main():
    args = sys.argv[1:]
    if args and args[0] in ("inspect", "clean", "spoof", "-v", "--version", "--help", "-h"):
        from src.cli import main as run_cli
        sys.exit(run_cli(args))
    elif args and args[0] in ("--menubar", "-m"):
        from src.gui.menubar_app import run_menubar_app
        run_menubar_app()
    else:
        run_gui_app()

if __name__ == "__main__":
    main()

