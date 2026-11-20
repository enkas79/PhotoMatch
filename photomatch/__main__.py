"""Entry point dell'applicazione PhotoMatch."""

import sys

from PyQt6.QtWidgets import QApplication

from photomatch.main_window import MainWindow


def apply_dark_theme(app: QApplication) -> None:
    """Applica stile Fusion + palette scura (tema dark di default)."""
    from PyQt6.QtGui import QColor, QPalette

    app.setStyle("Fusion")
    palette = QPalette()
    window = QColor(53, 53, 53)
    window_text = QColor(220, 220, 220)
    base = QColor(42, 42, 42)
    base_alt = QColor(35, 35, 35)
    highlight = QColor(42, 130, 218)

    palette.setColor(QPalette.ColorRole.Window, window)
    palette.setColor(QPalette.ColorRole.WindowText, window_text)
    palette.setColor(QPalette.ColorRole.Base, base)
    palette.setColor(QPalette.ColorRole.AlternateBase, base_alt)
    palette.setColor(QPalette.ColorRole.Text, window_text)
    palette.setColor(QPalette.ColorRole.Button, window)
    palette.setColor(QPalette.ColorRole.ButtonText, window_text)
    palette.setColor(QPalette.ColorRole.Highlight, highlight)
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor(255, 255, 255))
    palette.setColor(QPalette.ColorRole.ToolTipBase, base)
    palette.setColor(QPalette.ColorRole.ToolTipText, window_text)
    palette.setColor(QPalette.ColorRole.PlaceholderText, QColor(130, 130, 130))
    palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Text, QColor(110, 110, 110))
    palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.ButtonText, QColor(110, 110, 110))

    app.setPalette(palette)


def main() -> int:
    app = QApplication(sys.argv)
    app.setOrganizationName("enkas79")
    app.setApplicationName("PhotoMatch")
    apply_dark_theme(app)
    window = MainWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
