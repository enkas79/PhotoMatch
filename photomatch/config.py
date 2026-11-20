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

    # Cartelle di confronto (liste; migrazione automatica dai vecchi valori singoli)
    def _folder_list(self, key: str, legacy_key: str) -> list[str]:
        value = self.settings.value(key, [])
        if isinstance(value, str):
            value = [value] if value else []
        folders = [str(item) for item in value]
        if not folders:
            legacy = str(self.settings.value(legacy_key, ""))
            if legacy:
                folders = [legacy]
        return folders

    @property
    def nas_folders(self) -> list[str]:
        return self._folder_list("paths/nas_list", "paths/nas")

    @nas_folders.setter
    def nas_folders(self, value: list[str]) -> None:
        self.settings.setValue("paths/nas_list", [str(item) for item in value])

    @property
    def pcloud_folders(self) -> list[str]:
        return self._folder_list("paths/pcloud_list", "paths/pcloud")

    @pcloud_folders.setter
    def pcloud_folders(self, value: list[str]) -> None:
        self.settings.setValue("paths/pcloud_list", [str(item) for item in value])

    @property
    def last_nas_dir(self) -> str:
        return str(self.settings.value("paths/last_nas_dir", str(Path.home())))

    @last_nas_dir.setter
    def last_nas_dir(self, value: str) -> None:
        self.settings.setValue("paths/last_nas_dir", value)

    @property
    def last_pcloud_dir(self) -> str:
        return str(self.settings.value("paths/last_pcloud_dir", str(Path.home())))

    @last_pcloud_dir.setter
    def last_pcloud_dir(self, value: str) -> None:
        self.settings.setValue("paths/last_pcloud_dir", value)

    @property
    def help_seen(self) -> bool:
        value = self.settings.value("prefs/help_seen", False)
        return bool(value) if not isinstance(value, str) else value.lower() in ("true", "1")

    @help_seen.setter
    def help_seen(self, value: bool) -> None:
        self.settings.setValue("prefs/help_seen", value)

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
