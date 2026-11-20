"""Test della logica core: senza Qt, con fixture temporanee."""

from pathlib import Path

from photomatch.core.logic import (
    MatchResult,
    PhotoInfo,
    compare,
    make_report,
    scan_photos,
)


def _photo(path: str, size: int, exif: str | None = None) -> PhotoInfo:
    return PhotoInfo(path=Path(path), name=Path(path).name, size=size, exif_date=exif)


def test_exact_match():
    nas = [_photo("/nas/foto1.jpg", 1000, "2024:01:01 10:00:00")]
    pc = [_photo("/pcloud/foto1.jpg", 1000, "2024:01:01 10:00:00")]
    levels = [r.match_level for r in compare(nas, pc)]
    assert levels == ["exact"]


def test_name_size_without_exif():
    nas = [_photo("/nas/foto1.jpg", 1000)]
    pc = [_photo("/pcloud/foto1.jpg", 1000)]
    levels = [r.match_level for r in compare(nas, pc)]
    assert levels == ["name_size"]


def test_same_name_different_size_is_candidate():
    nas = [_photo("/nas/foto1.jpg", 1000)]
    pc = [_photo("/pcloud/foto1.jpg", 2000)]
    results = compare(nas, pc)
    assert results[0].match_level == "candidate"
    assert results[0].pcloud_photo is not None


def test_unique():
    nas = [_photo("/nas/solo_nas.jpg", 1000)]
    results = compare(nas, [])
    assert results[0].match_level == "unique"
    assert results[0].pcloud_photo is None


def test_case_insensitive_name():
    nas = [_photo("/nas/FOTO1.jpg", 1000, "2024:01:01 10:00:00")]
    pc = [_photo("/pcloud/foto1.JPG", 1000, "2024:01:01 10:00:00")]
    assert compare(nas, pc)[0].match_level == "exact"


def test_size_tolerance():
    nas = [_photo("/nas/foto1.jpg", 1000, "2024:01:01 10:00:00")]
    pc = [_photo("/pcloud/foto1.jpg", 1010, "2024:01:01 10:00:00")]
    assert compare(nas, pc, size_tolerance=20)[0].match_level == "exact"
    assert compare(nas, pc, size_tolerance=0)[0].match_level == "candidate"


def test_exif_same_name_size_but_different_date():
    nas = [_photo("/nas/foto1.jpg", 1000, "2024:01:01 10:00:00")]
    pc = [_photo("/pcloud/foto1.jpg", 1000, "2023:06:15 08:30:00")]
    results = compare(nas, pc)
    assert results[0].match_level == "name_size"
    assert results[0].pcloud_photo is pc[0]


def test_scan_photos(tmp_path: Path):
    image = tmp_path / "a.jpg"
    image.write_bytes(b"\xff\xd8" + b"x" * 100)
    (tmp_path / "note.txt").write_text("ignora")
    sub = tmp_path / "sub"
    sub.mkdir()
    (sub / "b.png").write_bytes(b"y" * 50)
    photos = scan_photos(
        tmp_path, recursive=True,
        progress=lambda c, n: None, exif_enabled=False,
    )
    names = {photo.name for photo in photos}
    assert names == {"a.jpg", "b.png"}
    assert all(photo.exif_date is None for photo in photos)


def test_make_report_rows():
    nas_photo = _photo("/nas/foto1.jpg", 1000, "2024:01:01 10:00:00")
    pc_photo = _photo("/pcloud/foto1.jpg", 1000, "2024:01:01 10:00:00")
    rows = make_report([MatchResult(nas_photo, pc_photo, "exact")])
    assert rows[0]["file"] == "foto1.jpg"
    assert rows[0]["level"] == "exact"
    assert rows[0]["exif_nas"] == "2024:01:01 10:00:00"
    assert rows[0]["pcloud_path"] == "/pcloud/foto1.jpg"


def test_updater_version_tuple():
    from photomatch.core.updater import _version_tuple

    assert _version_tuple("0.2.0") > _version_tuple("0.1.0")
    assert _version_tuple("1.0") > _version_tuple("0.9.9")


def test_scan_photos_multi_dedupes_overlapping_roots(tmp_path):
    from photomatch.core.logic import scan_photos_multi

    nas = tmp_path / "nas"
    (nas / "sub").mkdir(parents=True)
    (nas / "a.jpg").write_bytes(b"x" * 100)
    (nas / "sub" / "b.jpg").write_bytes(b"y" * 200)

    photos = scan_photos_multi([nas, nas / "sub"], exif_enabled=False)
    paths = {str(p.path) for p in photos}
    assert len(photos) == 2  # b.jpg scansionata da entrambe le root, conta una volta
    assert paths == {str(nas / "a.jpg"), str(nas / "sub" / "b.jpg")}


def test_scan_photos_multi_skips_missing_root(tmp_path):
    from photomatch.core.logic import scan_photos_multi

    root = tmp_path / "root"
    root.mkdir()
    (root / "a.jpg").write_bytes(b"x" * 50)

    photos = scan_photos_multi([tmp_path / "non_esiste", root], exif_enabled=False)
    assert [p.name for p in photos] == ["a.jpg"]
