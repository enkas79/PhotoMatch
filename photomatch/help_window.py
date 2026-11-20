"""Finestra della guida in-app: mostra docs/GUIDA.md in un QTextBrowser."""

from __future__ import annotations

from PyQt6.QtWidgets import QDialog, QTextBrowser, QVBoxLayout

from photomatch.markdown_lite import guide_path, render_markdown


class GuideWindow(QDialog):
    """Mostra la guida completa dell'applicazione."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("PhotoMatch - Guida")
        self.resize(860, 680)
        browser = QTextBrowser(self)
        browser.setOpenExternalLinks(True)
        path = guide_path()
        if path.is_file():
            browser.setHtml(render_markdown(path.read_text(encoding="utf-8")))
        else:
            browser.setPlainText(f"Guida non trovata: {path}")
        layout = QVBoxLayout(self)
        layout.addWidget(browser)
