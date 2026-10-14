"""Paths and small helpers shared by the prep steps."""

from __future__ import annotations

import csv
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
RAW = DATA / "raw"
CLEAN = DATA / "clean"
TOK = DATA / "tok"
MASK_A = DATA / "maskA"
MASK_B = DATA / "maskB"
CHUNKS = DATA / "chunks"
DEFAULT_TESTBED = ROOT / "testbed.csv"

TESTBED_COLUMNS = [
    "key",
    "title",
    "author",
    "year",
    "translator",
    "orig_language",
    "source",
    "source_id",
    "url",
    "group_tags",
    "notes",
]

VOLUME_BREAK = "\n\n<<<BOOK2VEC-VOLUME-BREAK>>>\n\n"  # joins multi-file Gutenberg works
WORD_RE = re.compile(r"[^\W\d_]+(?:['’\-][^\W\d_]+)*|\d+")


def read_testbed(path: Path) -> list[dict[str, str]]:
    """Read the testbed CSV; every value is a stripped string, missing columns are empty."""
    with path.open(newline="", encoding="utf-8-sig") as fh:
        rows = [
            {k: (row.get(k) or "").strip() for k in TESTBED_COLUMNS} for row in csv.DictReader(fh)
        ]
    rows = [r for r in rows if r["key"] and not r["key"].startswith("#")]
    keys = [r["key"] for r in rows]
    dupes = sorted({k for k in keys if keys.count(k) > 1})
    if dupes:
        raise SystemExit(f"duplicate keys in {path}: {dupes}")
    return rows


def select(rows: list[dict[str, str]], only: list[str] | None) -> list[dict[str, str]]:
    """Keep the rows whose key was asked for (all rows when nothing was asked)."""
    if not only:
        return rows
    wanted = set(only)
    missing = wanted - {r["key"] for r in rows}
    if missing:
        raise SystemExit(f"keys not in testbed: {sorted(missing)}")
    return [r for r in rows if r["key"] in wanted]


def n_words(text: str) -> int:
    """Count words the same way everywhere: letter runs (with inner ' or -) and digit runs."""
    return len(WORD_RE.findall(text))


def read_paragraphs(path: Path) -> list[str]:
    """Paragraphs of a prep text file: blocks separated by blank lines."""
    text = path.read_text(encoding="utf-8")
    return [p for p in (b.strip("\n") for b in re.split(r"\n\s*\n", text)) if p.strip()]


def write_paragraphs(path: Path, paras: list[str]) -> None:
    """Write paragraphs separated by one blank line, atomically."""
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text("\n\n".join(paras) + "\n", encoding="utf-8")
    tmp.replace(path)


def raw_path(key: str) -> Path | None:
    """The downloaded file for a book, whichever source it came from."""
    for suffix in (".se.zip", ".pg.txt"):
        p = RAW / f"{key}{suffix}"
        if p.exists() and p.stat().st_size > 0:
            return p
    return None


def is_stale(out: Path, *inputs: Path) -> bool:
    """True when out is missing or older than any input (the resumability test)."""
    if not out.exists() or out.stat().st_size == 0:
        return True
    t = out.stat().st_mtime
    return any(i.exists() and i.stat().st_mtime > t for i in inputs)
