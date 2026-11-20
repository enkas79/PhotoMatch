"""Test della logica di recupero da report CSV: senza Qt."""

import csv
from pathlib import Path

from photomatch.core.rescue import (
    execute_rescue,
    parse_report,
    plan_rescue,
    RescueStats,
)


def _write_report(path: Path, rows: list[tuple[str, str, int, str]]) -> None:
    with open(path, "w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.writer(handle)
        writer.writerow(
            ["exif_nas", "exif_pcloud", "file", "level", "level_label", "nas_path", "pcloud_path", "size_bytes"]
        )
        for name, level, size, nas_path in rows:
            writer.writerow(["", "", name, level, "x", nas_path, "", size])


def test_parse_and_plan_unique_only(tmp_path: Path):
    report = tmp_path / "r.csv"
    _write_report(report, [
        ("a.jpg", "unique", 100, r"\\NAS\Photos\2004\a.jpg"),
        ("b.jpg", "name_size", 200, r"\\NAS\Photos\b.jpg"),
    ])
    rows = parse_report(report)
    assert len(rows) == 2
    plan = plan_rescue(rows, include_candidates=False)
    assert len(plan) == 1
    source, relative, size = plan[0]
    assert source.name == "a.jpg"
    assert size == 100


def test_plan_includes_candidates_when_requested(tmp_path: Path):
    report = tmp_path / "r.csv"
    _write_report(report, [
        ("a.jpg", "unique", 100, r"\\NAS\Photos\a.jpg"),
        ("c.jpg", "candidate", 300, r"\\NAS\Photos\2004\c.jpg"),
    ])
    plan = plan_rescue(parse_report(report), include_candidates=True)
    relatives = {str(relative) for _, relative, _ in plan}
    assert any(r.endswith("_da_verificare") or "_da_verificare" in r for r in relatives)
    assert any("2004" in r for r in relatives)


def test_execute_rescue_copies_and_skips(tmp_path: Path):
    (tmp_path / "orig").mkdir()
    (tmp_path / "orig" / "x.jpg").write_bytes(b"data1234")
    dest = tmp_path / "saved"
    plan = [(tmp_path / "orig" / "x.jpg", Path("sub") / "x.jpg", 8)]
    stats = execute_rescue(plan, dest)
    assert stats.copied == 1
    assert (dest / "sub" / "x.jpg").read_bytes() == b"data1234"
    # seconda esecuzione: gia' presente, skippato
    stats2 = execute_rescue(plan, dest)
    assert stats2.skipped == 1 and stats2.copied == 0


def test_execute_rescue_counts_missing(tmp_path: Path):
    dest = tmp_path / "saved"
    plan = [(tmp_path / "manca.jpg", Path("manca.jpg"), 10)]
    stats = execute_rescue(plan, dest)
    assert stats.missing == 1
    assert RescueStats().total == 0
    assert "Copiati: 0" in stats.summary()
