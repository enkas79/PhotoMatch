"""version.txt deve restare allineato a photomatch.__version__: la build CI lo usa per il tag vX.Y.Z."""

from pathlib import Path

from photomatch import __version__


def test_version_txt_matches_package_version():
    root = Path(__file__).resolve().parent.parent
    assert (root / "version.txt").read_text(encoding="utf-8").strip() == __version__
