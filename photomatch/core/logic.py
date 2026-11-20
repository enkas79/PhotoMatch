"""Logica di confronto foto: nessun import Qt qui, testabile con pytest puro."""

from __future__ import annotations

import hashlib
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Iterable, Optional

PHOTO_EXTENSIONS = {
    ".jpg", ".jpeg", ".png", ".heic", ".heif", ".tif", ".tiff",
    ".bmp", ".gif", ".webp", ".cr2", ".nef", ".arw", ".dng", ".avif",
}

ProgressCallback = Callable[[int, str], None]


@dataclass(frozen=True)
class PhotoInfo:
    """Metadati minimi di una foto usati per il confronto."""

    path: Path
    name: str
    size: int
    exif_date: Optional[str] = field(default=None)  # "YYYY:MM:DD HH:MM:SS" o None

    @property
    def size_key(self) -> tuple[str, int]:
        return (self.name.lower(), self.size)

    @property
    def match_key(self) -> tuple[str, int, Optional[str]]:
        return (self.name.lower(), self.size, self.exif_date)


@dataclass
class MatchResult:
    """Un file delle cartelle A confrontato con l'eventuale controparte in B."""

    nas_photo: PhotoInfo
    pcloud_photo: Optional[PhotoInfo]
    match_level: str  # "exact" | name_size | "candidate" | "unique"

    @property
    def match_level_label(self) -> str:
        return {
            "exact": "Identica (nome + dimensione + data EXIF)",
            "name_size": "Nome e dimensione uguali, data EXIF diversa/assente",
            "candidate": "Stesso nome, dimensione diversa",
            "unique": "Non presente nelle cartelle B",
        }.get(self.match_level, self.match_level)


def extract_exif_date(path: Path) -> Optional[str]:
    """Estrae la data di scatto EXIF (DateTimeOriginal, fallback DateTime).

    Restituisce None se Pillow non e' disponibile o il file non ha EXIF.
    """
    try:
        from PIL import Image
        from PIL.ExifTags import BaseExif  # type: ignore[attr-defined]
    except ImportError:
        return None
    try:
        with Image.open(path) as img:
            exif = img.getexif()
            for tag in ("DateTimeOriginal", "DateTime"):
                value = exif.get(getattr(BaseExif, tag, None) or _fallback_tag_id(tag))
                if value:
                    return str(value)
    except Exception:
        return None
    return None


def _fallback_tag_id(name: str) -> int:
    # ID EXIF standard: 36867 DateTimeOriginal, 306 DateTime
    return 36867 if name == "DateTimeOriginal" else 306


def scan_photos(root: Path, recursive: bool = True,
                progress: Optional[ProgressCallback] = None,
                exif_enabled: bool = True) -> list[PhotoInfo]:
    """Scandisce una cartella e restituisce i metadati delle foto trovate.

    Non alza mai: gli errori di lettura singolo file vengono ignorati.
    """
    photos: list[PhotoInfo] = []
    if not root.is_dir():
        return photos
    iterator: Iterable[Path] = (
        root.rglob("*") if recursive else root.glob("*")
    )
    count = 0
    for item in iterator:
        if not item.is_file() or item.suffix.lower() not in PHOTO_EXTENSIONS:
            continue
        count += 1
        exif_date = extract_exif_date(item) if exif_enabled else None
        photos.append(
            PhotoInfo(
                path=item,
                name=item.name,
                size=item.stat().st_size,
                exif_date=exif_date,
            )
        )
        if progress and count % 25 == 0:
            progress(count, item.name)
    return photos


MultiProgressCallback = Callable[[int, int, int, str], None]  # indice root, totale root, file letti, nome


def scan_photos_multi(roots: Iterable[Path], recursive: bool = True,
                      progress: Optional[MultiProgressCallback] = None,
                      exif_enabled: bool = True) -> list[PhotoInfo]:
    """Scandisce piu' cartelle e deduplica per percorso reale (root sovrapposte).

    Le root non esistenti vengono saltate.
    """
    roots = list(roots)
    photos: list[PhotoInfo] = []
    seen: set[str] = set()
    total = len(roots)
    for index, root in enumerate(roots):
        sub_progress = None
        if progress:
            sub_progress = lambda count, name, i=index, t=total: progress(i, t, count, name)
        for photo in scan_photos(root, recursive=recursive, progress=sub_progress,
                                 exif_enabled=exif_enabled):
            key = os.path.realpath(photo.path)
            if key in seen:
                continue
            seen.add(key)
            photos.append(photo)
    return photos


def build_index(photos: Iterable[PhotoInfo]) -> dict[tuple[str, int], list[PhotoInfo]]:
    """Indice per (nome, dimensione); piu' foto possono condividere la chiave."""
    index: dict[tuple[str, int], list[PhotoInfo]] = {}
    for photo in photos:
        index.setdefault(photo.size_key, []).append(photo)
    return index


def _by_name(photos: Iterable[PhotoInfo]) -> dict[str, list[PhotoInfo]]:
    index: dict[str, list[PhotoInfo]] = {}
    for photo in photos:
        index.setdefault(photo.name.lower(), []).append(photo)
    return index


def compare(nas_photos: list[PhotoInfo], pcloud_photos: list[PhotoInfo],
            size_tolerance: int = 0) -> list[MatchResult]:
    """Confronta i file delle cartelle A con quelli delle cartelle B.

    Livelli:
      - exact: nome + dimensione (+/- tolleranza) + data EXIF identica
      - name_size: nome + dimensione uguali, EXIF divergente o assente
      - candidate: stesso nome, dimensione diversa
      - unique: nessuna controparte
    """
    by_name = _by_name(pcloud_photos)
    results: list[MatchResult] = []

    for nas_photo in nas_photos:
        same_name = by_name.get(nas_photo.name.lower(), [])
        if not same_name:
            results.append(MatchResult(nas_photo, None, "unique"))
            continue

        candidates = [
            candidate
            for candidate in same_name
            if abs(candidate.size - nas_photo.size) <= size_tolerance
        ]
        if not candidates:
            results.append(MatchResult(nas_photo, same_name[0], "candidate"))
            continue

        exact = [
            candidate
            for candidate in candidates
            if candidate.exif_date is not None
            and candidate.exif_date == nas_photo.exif_date
        ]
        if exact:
            results.append(MatchResult(nas_photo, exact[0], "exact"))
        else:
            best = _best_exif_candidate(candidates, nas_photo)
            results.append(MatchResult(nas_photo, best, "name_size"))
    return results


def _best_exif_candidate(candidates: list[PhotoInfo],
                         reference: PhotoInfo) -> PhotoInfo:
    """Sceglie il candidato con EXIF piu' vicino (o il primo senza EXIF)."""
    with_exif = [candidate for candidate in candidates if candidate.exif_date]
    if not with_exif:
        return candidates[0]
    if reference.exif_date is None:
        return with_exif[0]
    return min(with_exif, key=lambda c: abs(_timestamp(c.exif_date) - _timestamp(reference.exif_date)))


def _timestamp(exif_date: str) -> int:
    """Converte 'YYYY:MM:DD HH:MM:SS' in secondi; robusto a formati strani."""
    import time

    for pattern in ("%Y:%m:%d %H:%M:%S", "%Y-%m-%d %H:%M:%S"):
        try:
            return int(time.mktime(time.strptime(exif_date, pattern)))
        except ValueError:
            continue
    return 0


def file_sha256(path: Path, chunk_size: int = 1024 * 1024) -> str:
    """Hash del contenuto, utile come verifica finale su singola corrispondenza."""
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        while chunk := handle.read(chunk_size):
            digest.update(chunk)
    return digest.hexdigest()


def make_report(results: list[MatchResult]) -> list[dict[str, object]]:
    """Trasforma i risultati in righe piatta per CSV/QTableView."""
    return [
        {
            "file": result.nas_photo.name,
            "size_bytes": result.nas_photo.size,
            "exif_nas": result.nas_photo.exif_date or "",
            "exif_pcloud": (result.pcloud_photo.exif_date or "") if result.pcloud_photo else "",
            "level": result.match_level,
            "level_label": result.match_level_label,
            "nas_path": str(result.nas_photo.path),
            "pcloud_path": str(result.pcloud_photo.path) if result.pcloud_photo else "",
        }
        for result in results
    ]
