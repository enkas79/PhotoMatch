"""Worker QThread per il recupero foto da report CSV."""

from __future__ import annotations

from pathlib import Path

from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot

from photomatch.core.rescue import (
    ReportRow, execute_rescue, parse_report, plan_rescue, RescueStats,
)


class RescueWorker(QObject):
    """Recupera i file unici (e opzionalmente le candidate) dalle cartelle A."""

    progress = pyqtSignal(int, int, str)  # copiati, totali, nome file
    finished_ok = pyqtSignal(object)  # RescueStats
    failed = pyqtSignal(str)

    def __init__(self, csv_path: Path, dest_folder: Path,
                 include_candidates: bool = False) -> None:
        super().__init__()
        self.csv_path = csv_path
        self.dest_folder = dest_folder
        self.include_candidates = include_candidates

    @pyqtSlot()
    def run(self) -> None:
        try:
            rows: list[ReportRow] = parse_report(self.csv_path)
            plan = plan_rescue(rows, include_candidates=self.include_candidates)
            if not plan:
                self.finished_ok.emit(RescueStats())
                return
            stats = execute_rescue(
                plan, self.dest_folder,
                progress=lambda done, total, name: self.progress.emit(done, total, name),
            )
            self.finished_ok.emit(stats)
        except Exception as exc:  # noqa: BLE001
            self.failed.emit(str(exc))
