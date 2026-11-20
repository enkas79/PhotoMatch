"""Worker QThread per la scansione: mai logica bloccante nel thread UI."""

from __future__ import annotations

from pathlib import Path

from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot

from photomatch.core.logic import compare, make_report, scan_photos


class ScanWorker(QObject):
    """Scansiona cestino NAS e pCloud in un thread separato e confronta."""

    progress = pyqtSignal(int, int, str)  # scansione (0 NAS, 1 pCloud), file letti, nome file
    finished_ok = pyqtSignal(list)  # righe report
    failed = pyqtSignal(str)

    def __init__(self, nas_folder: Path, pcloud_folder: Path,
                 exif_enabled: bool = True, size_tolerance: int = 0) -> None:
        super().__init__()
        self.nas_folder = nas_folder
        self.pcloud_folder = pcloud_folder
        self.exif_enabled = exif_enabled
        self.size_tolerance = size_tolerance
        self._cancelled = False

    def cancel(self) -> None:
        self._cancelled = True

    @pyqtSlot()
    def run(self) -> None:
        try:
            nas_photos = scan_photos(
                self.nas_folder, recursive=True,
                progress=lambda count, name: self.progress.emit(0, count, name),
                exif_enabled=self.exif_enabled,
            )
            if self._cancelled:
                return
            pcloud_photos = scan_photos(
                self.pcloud_folder, recursive=True,
                progress=lambda count, name: self.progress.emit(1, count, name),
                exif_enabled=self.exif_enabled,
            )
            if self._cancelled:
                return
            results = compare(nas_photos, pcloud_photos, self.size_tolerance)
            self.finished_ok.emit(make_report(results))
        except Exception as exc:  # noqa: BLE001 - il thread non deve mai crashare
            self.failed.emit(str(exc))
