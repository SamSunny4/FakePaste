"""
FakePaste — Realistic Human Typing Simulator
Entry point for the application.
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QFont, QFontDatabase, QIcon
from PyQt6.QtCore import Qt

from ui.main_window import MainWindow
from ui.styles import DARK_STYLESHEET


def main():
    # High DPI support
    os.environ['QT_ENABLE_HIGHDPI_SCALING'] = '1'

    app = QApplication(sys.argv)
    app.setApplicationName("FakePaste")
    app.setOrganizationName("FakePaste")
    app.setApplicationVersion("1.0.0")

    # Set style
    app.setStyle("Fusion")

    # Apply dark stylesheet
    app.setStyleSheet(DARK_STYLESHEET)

    # Load preferred fonts
    preferred_fonts = ["Segoe UI", "Inter", "Roboto", "SF Pro Display"]
    available_families = QFontDatabase.families()
    font_set = False
    for font_name in preferred_fonts:
        if font_name in available_families:
            app.setFont(QFont(font_name, 10))
            font_set = True
            break
    if not font_set:
        app.setFont(QFont("Segoe UI", 10))

    # Create and show main window
    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
