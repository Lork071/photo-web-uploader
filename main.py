#!/usr/bin/env python3
"""
FTP Photo Manager
Aplikace pro nahrávání a správu fotografií na FTP serveru
"""

import sys
from gui.main_window import MainApplication


def main():
    """Hlavní funkce"""
    try:
        app = MainApplication()
        app.mainloop()
    except KeyboardInterrupt:
        print("\nAplikace ukončena")
        sys.exit(0)
    except Exception as e:
        print(f"Chyba při spuštění aplikace: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
