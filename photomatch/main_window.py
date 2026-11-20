"""Finestra principale: solo UI e wiring dei segnali."""

from __future__ import annotations

import csv
from pathlib import Path

from PyQt6.QtCore import Qt, QThread
from PyQt6.QtGui import QAction, QCloseEvent
from PyQt6.QtWidgets import (
    QFileDialog, QHBoxLayout, QHeaderView, QLabel, QListWidget, QMainWindow,
    QMenu, QMessageBox, QProgressBar, QPushButton, QStatusBar, QTableWidget,
    QTableWidgetItem, QVBoxLayout, QWidget, QCheckBox, QSpinBox, QGroupBox,
)

from photomatch import __version__
from photomatch.config import Config
from photomatch.core.updater import check_github_release
from photomatch.worker import ScanWorker


class MainWindow(QMainWindow):
    """Finestra: selettori cartelle, avvio scansione, tabella risultati."""

    def __init__(self) -> None:
        super().__init__()
        self.config = Config()
        self.results: list[dict[str, object]] = []
        self._thread: QThread | None = None
        self._worker: ScanWorker | None = None
        self._rescue_thread: QThread | None = None
        self._rescue_worker = None

        self.setWindowTitle("PhotoMatch - Cestino NAS vs pCloud")
        self.resize(1000, 640)

        central = QWidget()
        layout = QVBoxLayout(central)
        layout.addWidget(self._build_folders_group())
        layout.addWidget(self._build_options_group())
        layout.addWidget(self._build_results_table())
        self.setCentralWidget(central)
        self._build_menu()
        self._build_statusbar()
        self._restore_geometry()
        self._first_run_hint()

    # --- UI -----------------------------------------------------------------
    def _build_folders_group(self) -> QGroupBox:
        box = QGroupBox("Cartelle (aggiungi quante vuoi per lato)")
        columns = QHBoxLayout()

        self.nas_list = QListWidget()
        self.nas_list.setToolTip("Cartelle del cestino NAS da confrontare (scansione ricorsiva)")
        for folder in self.config.nas_folders:
            self.nas_list.addItem(folder)
        columns.addLayout(self._folder_column(
            "Cestino NAS:", self.nas_list, self._add_nas, self._remove_nas, self._clear_nas,
        ))

        self.pcloud_list = QListWidget()
        self.pcloud_list.setToolTip("Cartelle pCloud da confrontare (scansione ricorsiva)")
        for folder in self.config.pcloud_folders:
            self.pcloud_list.addItem(folder)
        columns.addLayout(self._folder_column(
            "pCloud:", self.pcloud_list, self._add_pcloud, self._remove_pcloud, self._clear_pcloud,
        ))

        action_row = QHBoxLayout()
        self.scan_button = QPushButton("Confronta")
        self.scan_button.clicked.connect(self._start_scan)
        self.export_button = QPushButton("Esporta CSV")
        self.export_button.setEnabled(False)
        self.export_button.clicked.connect(self._export_csv)
        self.rescue_button = QPushButton("Recupera foto da CSV...")
        self.rescue_button.clicked.connect(self._start_rescue)
        self.rescue_candidates_check = QCheckBox("includi le 'candidate'")
        self.rescue_candidates_check.setToolTip(
            "Copia anche le foto con stesso nome ma dimensione diversa, "
            "in una sottocartella _da_verificare"
        )
        action_row.addWidget(self.scan_button)
        action_row.addWidget(self.export_button)
        action_row.addWidget(self.rescue_button)
        action_row.addWidget(self.rescue_candidates_check)
        action_row.addStretch(1)
        outer = QVBoxLayout()
        outer.addLayout(columns)
        outer.addLayout(action_row)
        box.setLayout(outer)
        return box

    def _folder_column(self, title: str, list_widget: QListWidget,
                       on_add, on_remove, on_clear) -> QVBoxLayout:
        col = QVBoxLayout()
        col.addWidget(QLabel(title))
        col.addWidget(list_widget, stretch=1)
        buttons = QHBoxLayout()
        btn_add = QPushButton("Aggiungi...")
        btn_add.clicked.connect(on_add)
        btn_remove = QPushButton("Rimuovi selezionata")
        btn_remove.clicked.connect(on_remove)
        btn_clear = QPushButton("Svuota")
        btn_clear.clicked.connect(on_clear)
        buttons.addWidget(btn_add)
        buttons.addWidget(btn_remove)
        buttons.addWidget(btn_clear)
        col.addLayout(buttons)
        return col

    def _build_options_group(self) -> QGroupBox:
        box = QGroupBox("Opzioni confronto")
        row = QHBoxLayout()
        self.exif_check = QCheckBox("Confronta data EXIF (piu' lento, piu' preciso)")
        self.exif_check.setChecked(self.config.exif_enabled)
        self.exif_check.toggled.connect(
            lambda checked: setattr(self.config, "exif_enabled", checked)
        )
        row.addWidget(self.exif_check)
        row.addWidget(QLabel("Tolleranza dimensione (byte):"))
        self.tolerance_spin = QSpinBox()
        self.tolerance_spin.setRange(0, 100 * 1024 * 1024)
        self.tolerance_spin.setValue(self.config.size_tolerance)
        self.tolerance_spin.valueChanged.connect(
            lambda value: setattr(self.config, "size_tolerance", value)
        )
        row.addWidget(self.tolerance_spin)
        row.addStretch(1)
        box.setLayout(row)
        return box

    def _build_results_table(self) -> QTableWidget:
        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels(
            ["File", "Esito", "EXIF NAS", "EXIF pCloud", "Percorso NAS", "Percorso pCloud"]
        )
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        header.setStretchLastSection(True)
        return self.table

    def _build_menu(self) -> None:
        menu_bar = self.menuBar()
        file_menu: QMenu = menu_bar.addMenu("File")
        exit_action = QAction("Esci", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        help_menu: QMenu = menu_bar.addMenu("Aiuto")
        guide_action = QAction("Guida (F1)", self)
        guide_action.setShortcut("F1")
        guide_action.triggered.connect(self._show_guide)
        help_menu.addAction(guide_action)
        help_menu.addSeparator()
        update_action = QAction("Controlla aggiornamenti", self)
        update_action.triggered.connect(self._check_updates)
        help_menu.addAction(update_action)
        about_action = QAction("Info", self)
        about_action.triggered.connect(self._about)
        help_menu.addAction(about_action)

    def _build_statusbar(self) -> None:
        self.progress = QProgressBar()
        self.progress.setRange(0, 0)  # indeterminato durante la scansione
        self.progress.hide()
        self.progress_label = QLabel("")
        status: QStatusBar = self.statusBar()
        status.addWidget(self.progress_label, stretch=1)
        status.addPermanentWidget(self.progress)

    # --- Azioni ---------------------------------------------------------------
    def _folders_of(self, list_widget: QListWidget) -> list[str]:
        return [list_widget.item(i).text() for i in range(list_widget.count())]

    def _add_unique(self, list_widget: QListWidget, folder: str) -> None:
        if folder not in self._folders_of(list_widget):
            list_widget.addItem(folder)

    def _add_nas(self) -> None:
        folder = QFileDialog.getExistingDirectory(
            self, "Aggiungi cartella cestino NAS", self.config.last_nas_dir
        )
        if folder:
            self.config.last_nas_dir = str(Path(folder).parent)
            self._add_unique(self.nas_list, folder)
            self.config.nas_folders = self._folders_of(self.nas_list)

    def _add_pcloud(self) -> None:
        folder = QFileDialog.getExistingDirectory(
            self, "Aggiungi cartella foto pCloud", self.config.last_pcloud_dir
        )
        if folder:
            self.config.last_pcloud_dir = str(Path(folder).parent)
            self._add_unique(self.pcloud_list, folder)
            self.config.pcloud_folders = self._folders_of(self.pcloud_list)

    def _remove_selected(self, list_widget: QListWidget) -> None:
        for item in list_widget.selectedItems():
            list_widget.takeItem(list_widget.row(item))

    def _remove_nas(self) -> None:
        self._remove_selected(self.nas_list)
        self.config.nas_folders = self._folders_of(self.nas_list)

    def _remove_pcloud(self) -> None:
        self._remove_selected(self.pcloud_list)
        self.config.pcloud_folders = self._folders_of(self.pcloud_list)

    def _clear_nas(self) -> None:
        self.nas_list.clear()
        self.config.nas_folders = []

    def _clear_pcloud(self) -> None:
        self.pcloud_list.clear()
        self.config.pcloud_folders = []

    def _start_scan(self) -> None:
        nas_folders = [Path(p) for p in self._folders_of(self.nas_list)]
        pcloud_folders = [Path(p) for p in self._folders_of(self.pcloud_list)]
        nas_valid = [p for p in nas_folders if p.is_dir()]
        pcloud_valid = [p for p in pcloud_folders if p.is_dir()]
        if not nas_valid:
            QMessageBox.warning(self, "PhotoMatch", "Aggiungi almeno una cartella cestino NAS valida.")
            return
        if not pcloud_valid:
            QMessageBox.warning(self, "PhotoMatch", "Aggiungi almeno una cartella pCloud valida.")
            return
        missing = [str(p) for p in nas_folders + pcloud_folders if not p.is_dir()]
        if missing:
            QMessageBox.warning(
                self, "PhotoMatch",
                "Alcune cartelle non sono raggiungibili e saranno saltate:\n" + "\n".join(missing),
            )

        self.scan_button.setEnabled(False)
        self.export_button.setEnabled(False)
        self.progress.show()
        self.progress_label.setText("Scansione in corso...")

        self._thread = QThread()
        self._worker = ScanWorker(
            nas_valid, pcloud_valid,
            exif_enabled=self.config.exif_enabled,
            size_tolerance=self.config.size_tolerance,
        )
        self._worker.moveToThread(self._thread)
        self._thread.started.connect(self._worker.run)
        self._worker.progress.connect(self._on_progress)
        self._worker.finished_ok.connect(self._on_finished)
        self._worker.failed.connect(self._on_failed)
        self._thread.start()

    def _on_progress(self, phase: int, count: int, name: str) -> None:
        source = "NAS" if phase == 0 else "pCloud"
        self.progress_label.setText(f"Scansione {source}: {count} foto (ultimo: {name})")

    def _on_finished(self, rows: list[dict[str, object]]) -> None:
        self._teardown_thread()
        self.results = rows
        counts = self._count_by_level(rows)
        self.table.setRowCount(len(rows))
        for row_index, row in enumerate(rows):
            values = [
                str(row["file"]),
                str(row["level_label"]),
                str(row["exif_nas"]),
                str(row["exif_pcloud"]),
                str(row["nas_path"]),
                str(row["pcloud_path"]),
            ]
            for column, value in enumerate(values):
                item = QTableWidgetItem(value)
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.table.setItem(row_index, column, item)
        self.progress.hide()
        self.progress_label.setText(
            f"{len(rows)} foto nel cestino | "
            f"identiche: {counts['exact']} | nome+dim: {counts['name_size']} | "
            f"candidati: {counts['candidate']} | uniche: {counts['unique']}"
        )
        self.scan_button.setEnabled(True)
        self.export_button.setEnabled(bool(rows))

    def _on_failed(self, message: str) -> None:
        self._teardown_thread()
        self.progress.hide()
        self.progress_label.setText("Errore durante la scansione.")
        self.scan_button.setEnabled(True)
        QMessageBox.critical(self, "PhotoMatch", f"Scansione fallita:\n{message}")

    def _teardown_thread(self) -> None:
        if self._thread:
            self._thread.quit()
            self._thread.wait(5000)
        self._thread = None
        self._worker = None

    def _count_by_level(self, rows: list[dict[str, object]]) -> dict[str, int]:
        counts = {"exact": 0, "name_size": 0, "candidate": 0, "unique": 0}
        for row in rows:
            level = str(row["level"])
            if level in counts:
                counts[level] += 1
        return counts

    def _export_csv(self) -> None:
        default_dir = self.config.last_report_dir
        path, _ = QFileDialog.getSaveFileName(
            self, "Esporta report", str(Path(default_dir) / "photomatch_report.csv"),
            "CSV (*.csv)",
        )
        if not path:
            return
        self.config.last_report_dir = str(Path(path).parent)
        with open(path, "w", newline="", encoding="utf-8-sig") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(self.results[0].keys()))
            writer.writeheader()
            writer.writerows(self.results)
        self.progress_label.setText(f"Report esportato: {path}")

    def _start_rescue(self) -> None:
        csv_path, _ = QFileDialog.getOpenFileName(
            self, "Scegli il report CSV", self.config.last_report_dir, "CSV (*.csv)"
        )
        if not csv_path:
            return
        dest_folder = QFileDialog.getExistingDirectory(
            self, "Cartella di destinazione dei salvataggi (es. D:\\Foto_Salvate)"
        )
        if not dest_folder:
            return
        self.config.last_report_dir = str(Path(csv_path).parent)

        self.scan_button.setEnabled(False)
        self.export_button.setEnabled(False)
        self.rescue_button.setEnabled(False)
        self.progress.show()
        self.progress_label.setText("Lettura report e copia in corso...")

        from photomatch.rescue_worker import RescueWorker

        self._rescue_thread = QThread()
        self._rescue_worker = RescueWorker(
            Path(csv_path), Path(dest_folder),
            include_candidates=self.rescue_candidates_check.isChecked(),
        )
        self._rescue_worker.moveToThread(self._rescue_thread)
        self._rescue_thread.started.connect(self._rescue_worker.run)
        self._rescue_worker.progress.connect(self._on_rescue_progress)
        self._rescue_worker.finished_ok.connect(self._on_rescue_finished)
        self._rescue_worker.failed.connect(self._on_rescue_failed)
        self._rescue_thread.start()

    def _on_rescue_progress(self, done: int, total: int, name: str) -> None:
        if total:
            self.progress.setRange(0, total)
            self.progress.setValue(done)
        self.progress_label.setText(f"Recupero: {done}/{total} file (ultimo: {name})")

    def _on_rescue_finished(self, stats) -> None:
        if self._rescue_thread:
            self._rescue_thread.quit()
            self._rescue_thread.wait(5000)
        self._rescue_thread = None
        self._rescue_worker = None
        self.progress.hide()
        self.progress.setRange(0, 0)
        self.progress_label.setText(f"Recupero completato. {stats.summary()}")
        self.scan_button.setEnabled(True)
        self.export_button.setEnabled(bool(self.results))
        self.rescue_button.setEnabled(True)
        detail = stats.summary()
        if stats.errors:
            detail += "\n\nPrimi errori:\n" + "\n".join(stats.errors[:10])
        QMessageBox.information(self, "PhotoMatch - Recupero", detail)

    def _on_rescue_failed(self, message: str) -> None:
        if self._rescue_thread:
            self._rescue_thread.quit()
            self._rescue_thread.wait(5000)
        self._rescue_thread = None
        self._rescue_worker = None
        self.progress.hide()
        self.progress_label.setText("Recupero fallito.")
        self.scan_button.setEnabled(True)
        self.export_button.setEnabled(bool(self.results))
        self.rescue_button.setEnabled(True)
        QMessageBox.critical(self, "PhotoMatch", f"Recupero fallito:\n{message}")

    def _check_updates(self) -> None:
        try:
            info = check_github_release("enkas79/PhotoMatch", __version__)
        except Exception as exc:  # noqa: BLE001
            QMessageBox.warning(self, "PhotoMatch", f"Verifica aggiornamenti fallita:\n{exc}")
            return
        if info["update"]:
            QMessageBox.information(
                self, "PhotoMatch",
                f"Nuova versione {info['latest']} disponibile.\n{info['url']}",
            )
        else:
            QMessageBox.information(self, "PhotoMatch", "PhotoMatch e' aggiornato.")

    def _show_guide(self) -> None:
        from photomatch.help_window import GuideWindow

        GuideWindow(self).exec()

    def _first_run_hint(self) -> None:
        if self.config.help_seen:
            return
        box = QMessageBox(self)
        box.setWindowTitle("PhotoMatch")
        box.setIcon(QMessageBox.Icon.Information)
        box.setText(
            "Benvenuto in PhotoMatch!\n\n"
            "Aggiungi una o piu' cartelle per lato, poi premi \"Confronta\".\n"
            "La guida completa e' in Aiuto > Guida (tasto F1)."
        )
        dont_show = QCheckBox("Non mostrare piu' questo messaggio")
        box.setCheckBox(dont_show)
        box.exec()
        if dont_show.isChecked():
            self.config.help_seen = True

    def _about(self) -> None:
        QMessageBox.about(
            self, "PhotoMatch",
            f"PhotoMatch {__version__}\n\n"
            "Confronta le foto del cestino del NAS con quelle presenti su pCloud "
            "in base a nome file, dimensione e data EXIF.\n\nEnrico Martini (c) 2026",
        )

    # --- Geometria --------------------------------------------------------------
    def _restore_geometry(self) -> None:
        geometry = self.config.window_geometry()
        if geometry:
            self.restoreGeometry(geometry)

    def closeEvent(self, event: QCloseEvent) -> None:
        self.config.set_window_geometry(self.saveGeometry())
        if self._worker:
            self._worker.cancel()
        self._teardown_thread()
        if self._rescue_worker and self._rescue_thread:
            self._rescue_thread.quit()
            self._rescue_thread.wait(5000)
        super().closeEvent(event)
