#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
from PyQt5.QtWidgets import QApplication
from gui.main_window import MainWindow

def main():
    """Point d'entrée principal de l'application."""
    app = QApplication(sys.argv)
    app.setDesktopFileName('csf_gaspard.desktop')
    # Charger la feuille de style
    # style_path = os.path.join(os.path.dirname(__file__), 'resources', 'style.qss')
    # try:
    #     with open(style_path, "r") as f:
    #         app.setStyleSheet(f.read())
    # except FileNotFoundError:
    #     print(f"Avertissement : Feuille de style non trouvée à {style_path}", file=sys.stderr)
    # except Exception as e:
    #     print(f"Erreur lors du chargement de la feuille de style: {e}", file=sys.stderr)

    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main() 
