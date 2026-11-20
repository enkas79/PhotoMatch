"""Wrapper QSettings: dimensione finestra, ultimi percorsi, preferenze."""

from __future__ import annotations

from pathlib import Path

from PyQt6.QtCore import QSettings


class Config:
    """Accesso centralizzato alle impostazioni persistenti dell'app."""

    def __init__(self) -> None:
        self.settings = QSettings("enkas79", "PhotoMatch")

    # Finestra
    def window_geometry(self) -> bytes | None:
        value = self.settings.value("window/geometry")
        return bytes(value) if isinstance(value, bytes) else None

    def set_window_geometry(self, geometry: bytes) -> None:
        self.settings.setValue("window/geometry", geometry)

    # Percorsi
    @property
    def nas_folder(self) -> str:
        return str(self.settings.value("paths/nas", ""))

    @nas_folder.setter
    def nas_folder(self, value: str) -> None:
        self.settings.setValue("paths/nas", value)

    @property
    def pcloud_folder(self) -> str:
        return str(self.settings.value("paths/pcloud", ""))

    @pcloud_folder.setter
    def pcloud_folder(self, value: str) -> None:
        self.settings.setValue("paths/pcloud", value)

    # Preferenze
    @property
    def exif_enabled(self) -> bool:
        value = self.settings.value("prefs/exif", True)
        return bool(value) if not isinstance(value, str) else value.lower() in ("true", "1")

    @exif_enabled.setter
    def exif_enabled(self, value: bool) -> None:
        self.settings.setValue("prefs/exif", value)

    @property
    def size_tolerance(self) -> int:
        return int(self.settings.value("prefs/size_tolerance", 0))

    @size_tolerance.setter
    def size_tolerance(self, value: int) -> None:
        self.settings.setValue("prefs/size_tolerance", value)

    @property
    def last_report_dir(self) -> str:
        return str(self.settings.value("paths/report_dir", str(Path.home())))

    @last_report_dir.setter
    def last_report_dir(self, value: str) -> None:
        self.settings.setValue("paths/report_dir", value)
