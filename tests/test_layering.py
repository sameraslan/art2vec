"""Media are the `<form>2vec` folders inside the package. The core never imports one."""

import re
from pathlib import Path

PACKAGE = Path(__file__).resolve().parents[1] / "src" / "art2vec"
MEDIA = sorted(p.name for p in PACKAGE.iterdir() if p.is_dir() and p.name.endswith("2vec"))


def test_there_is_at_least_one_medium() -> None:
    assert "album2vec" in MEDIA


def test_core_does_not_import_media() -> None:
    names = "|".join(MEDIA)
    pattern = re.compile(
        rf"^\s*(from|import)\s+art2vec\.({names})\b|^\s*from\s+art2vec\s+import\s+({names})\b", re.M
    )
    offenders = [p.name for p in PACKAGE.glob("*.py") if pattern.search(p.read_text())]
    assert offenders == [], f"core modules import a medium: {offenders}"


def test_media_do_not_import_each_other() -> None:
    for medium in MEDIA:
        others = "|".join(m for m in MEDIA if m != medium) or "$^"
        pattern = re.compile(rf"art2vec\.({others})\b")
        offenders = [
            p.name for p in (PACKAGE / medium).glob("*.py") if pattern.search(p.read_text())
        ]
        assert offenders == [], f"{medium} imports another medium: {offenders}"


def test_media_folders_carry_a_framework() -> None:
    assert [m for m in MEDIA if not (PACKAGE / m / "FRAMEWORK.md").exists()] == []
