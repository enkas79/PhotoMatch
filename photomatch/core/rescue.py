"""Recupero foto da report CSV: logica pura, nessun import Qt qui."""

from __future__ import annotations

import csv
import os
import shutil
from dataclasses import dataclass
from pathlib import Path, PureWindowsPath
from typing import Callable, Optional

ProgressCallback = Callable[[int, int, str], None]  # copiati, totali, nome file


@dataclass(frozen=True)
class ReportRow:
    """Una riga del report CSV esportato da PhotoMatch."""

    file: str
    level: str
    size_bytes: int
    nas_path: Path

    @property
    def is_unique(self) -> bool:
        return self.level == "unique"

    @property
    def is_candidate(self) -> bool:
        return self.level == "candidate"


def _to_path(raw: str) -> Path:
    """Converte 'C:\\\\a\\\\b.jpg' o '/nas/a/b.jpg' in Path confrontabile."""
    return Path(PureWindowsPath(os.path.normpath(raw))) if "\\" in raw else Path(raw)


def parse_report(csv_path: Path) -> list[ReportRow]:
    """Legge il CSV del report e restituisce le righe con percorsi NAS validi."""
    rows: list[ReportRow] = []
    with open(csv_path, newline="", encoding="utf-8-sig") as handle:
        for raw in csv.DictReader(handle):
            nas_raw = (raw.get("nas_path") or "").strip()
            size_raw = (raw.get("size_bytes") or "0").strip()
            if not nas_raw:
                continue
            rows.append(
                ReportRow(
                    file=raw.get("file") or "",
                    level=raw.get("level") or "",
                    size_bytes=int(size_raw) if size_raw.isdigit() else 0,
                    nas_path=_to_path(nas_raw),
                )
            )
    return rows


def common_root(paths: list[Path]) -> Optional[Path]:
    """Radice comune dei percorsi NAS del report (server per ricostruire l'albero)."""
    if not paths:
        return None
    parts = [list(p.parts) for p in paths]
    common: list[str] = []
    for first, *rest in zip(*parts):
        if all(segment == first for segment in rest):
            common.append(first)
        else:
            break
    if len(common) < 2:  # almeno una radice con un elemento
        return None
    return Path(*common)


def plan_rescue(rows: list[ReportRow], include_candidates: bool = False) -> list[tuple[Path, Path, int]]:
    """Copia da pianificare: coppie (origine, destinazione relativa, dimensione).

    L'albero di destinazione preserva la struttura del report sotto la radice NAS.
    I 'candidate' finiscono nella sottocartella riservata _da_verificare.
    """
    selected = [row for row in rows if row.is_unique or (include_candidates and row.is_candidate)]
    root = common_root([row.nas_path for row in selected])
    plan: list[tuple[Path, Path, int]] = []
    for row in selected:
        relative = relative_to_root(row.nas_path, root)
        if row.is_candidate:
            relative = Path("_da_verificare") / relative
        plan.append((row.nas_path, relative, row.size_bytes))
    return plan


def relative_to_root(path: Path, root: Optional[Path]) -> Path:
    """Percorso relativo alla radice comune; fallback sul solo nome file."""
    if root is not None:
        try:
            return path.relative_to(root)
        except ValueError:
            pass
    return Path(path.name)


@dataclass
class RescueStats:
    """Esito del recupero."""

    copied: int = 0
    skipped: int = 0  # gia' presenti con stessa dimensione
    missing: int = 0
    errors: list[str] = None  # type: ignore[assignment]

    def __post_init__(self) -> None:
        if self.errors is None:
            self.errors = []

    @property
    def total(self) -> int:
        return self.copied + self.skipped + self.missing + len(self.errors)

    def summary(self) -> str:
        return (
            f"Copiati: {self.copied} | Gia' presenti: {self.skipped} | "
            f"Non trovati sul NAS: {self.missing} | Errori: {len(self.errors)}"
        )


def execute_rescue(plan: list[tuple[Path, Path, int]], dest_root: Path,
                   progress: Optional[ProgressCallback] = None) -> RescueStats:
    """Esegue le copie pianificate. Non cancella mai nulla, non sovrascrive."""
    stats = RescueStats()
    total = len(plan)
    dest_root.mkdir(parents=True, exist_ok=True)
    for index, (source, relative, size) in enumerate(plan):
        target = dest_root / relative
        if progress and index % 10 == 0:
            progress(index, total, source.name)
        try:
            if target.exists() and target.stat().st_size == size:
                stats.skipped += 1
                continue
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)
            stats.copied += 1
        except FileNotFoundError:
            stats.missing += 1
        except OSError as exc:
            stats.errors.append(f"{source}: {exc}")
    if progress:
        progress(total, total, "")
    return stats
