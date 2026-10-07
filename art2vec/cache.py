"""Where derived data lives on disk. See ARCHITECTURE.md section 6."""

from __future__ import annotations

import os
from pathlib import Path

from platformdirs import user_cache_dir

ENV_HOME = "ART2VEC_HOME"
CACHEDIR_TAG = "Signature: 8a477f597d28d172789f06886806bc55\n# art2vec cache; safe to delete.\n"


def home() -> Path:
    """The cache root: `$ART2VEC_HOME`, else the platform's user cache dir.

    Creates it and a CACHEDIR.TAG so backup tools skip it. Model weights stay
    in their own hub caches; only artefacts and vectors go here.
    """
    root = Path(os.environ.get(ENV_HOME) or user_cache_dir("art2vec"))
    root.mkdir(parents=True, exist_ok=True)
    tag = root / "CACHEDIR.TAG"
    if not tag.exists():
        tag.write_text(CACHEDIR_TAG)
    return root


def artefacts(medium: str) -> Path:
    path = home() / "artefacts" / medium
    path.mkdir(parents=True, exist_ok=True)
    return path


def vectors(medium: str, block: str, model: str, version: str) -> Path:
    path = home() / "vectors" / medium / f"{block}@{model}@{version}"
    path.mkdir(parents=True, exist_ok=True)
    return path
