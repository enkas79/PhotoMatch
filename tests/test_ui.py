"""Smoke test UI: richiede PyQt6 (usa la piattaforma offscreen); saltato se assente."""

import os

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

try:
    from PyQt6.QtWidgets import QApplication
except ImportError as exc:  # PyQt6 o librerie di sistema mancanti
    pytest.skip(f"PyQt6 non disponibile: {exc}", allow_module_level=True)

from photomatch.config import Config  # noqa: E402
from photomatch.main_window import MainWindow  # noqa: E402
from photomatch.worker import ScanWorker  # noqa: E402


@pytest.fixture(scope="module")
def qapp():
    Config().help_seen = True  # evita il dialogo di benvenuto bloccante
    app = QApplication.instance() or QApplication([])
    yield app


def test_scan_with_multiple_folders(qapp, tmp_path):
    nas1 = tmp_path / "nas1"
    nas2 = tmp_path / "nas2"
    pcloud = tmp_path / "pcloud"
    for folder in (nas1, nas2, pcloud):
        folder.mkdir()
    (nas1 / "a.jpg").write_bytes(b"x" * 100)
    (nas2 / "b.jpg").write_bytes(b"y" * 200)
    (nas1 / "sub").mkdir()
    (nas1 / "sub" / "b.jpg").write_bytes(b"y" * 200)  # duplicato via root sovrapposte
    (pcloud / "a.jpg").write_bytes(b"x" * 100)

    window = MainWindow()
    window.nas_list.addItem(str(nas1))
    window.nas_list.addItem(str(nas2))
    window.pcloud_list.addItem(str(pcloud))

    results: list[list] = []
    worker = ScanWorker([nas1, nas2, nas1 / "sub"], [pcloud], exif_enabled=False)
    worker.finished_ok.connect(results.append)
    worker.run()  # sincrono, stesso thread

    assert len(results) == 1
    rows = results[0]
    names = sorted(row["file"] for row in rows)
    assert names == ["a.jpg", "b.jpg"]  # b.jpg una sola volta nonostante le root sovrapposte
    levels = {row["file"]: row["level"] for row in rows}
    assert levels["a.jpg"] == "name_size"  # stesso nome+dimensione, EXIF disattivato
    assert levels["b.jpg"] == "unique"
    window.close()
