"""Media are the top-level `<form>2vec` folders. The core never imports one except by name."""

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MEDIA_PACKAGES = sorted(
    p.name for p in ROOT.iterdir() if p.is_dir() and p.name.endswith("2vec") and p.name != "art2vec"
)


def test_core_does_not_import_media() -> None:
    pattern = re.compile(r"^\s*(from|import)\s+(" + "|".join(MEDIA_PACKAGES) + r")\b", re.M)
    offenders = [p for p in (ROOT / "art2vec").glob("*.py") if pattern.search(p.read_text())]
    assert offenders == [], f"core modules import a medium: {offenders}"


def test_media_folders_carry_a_framework() -> None:
    missing = [m for m in MEDIA_PACKAGES if not (ROOT / m / "FRAMEWORK.md").exists()]
    assert missing == []
