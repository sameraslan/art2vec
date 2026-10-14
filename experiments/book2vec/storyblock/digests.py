"""The reader's digests (from text, and from the title alone) as plain strings."""

from __future__ import annotations

import json

import pandas as pd
from eval.blocks import ROOT

STORY = ROOT / "data" / "story"
FIELDS = ("story", "characters", "world", "subjects")
FELT_WORDS = [
    "bleak",
    "melancholy",
    "tense",
    "eerie",
    "dreamlike",
    "warm",
    "funny",
    "serene",
    "claustrophobic",
    "wistful",
    "menacing",
    "exhilarating",
    "tender",
    "bitter",
    "playful",
    "solemn",
    "anxious",
    "hopeful",
    "cold",
    "lush",
    "grotesque",
    "disorienting",
    "cosy",
    "desolate",
]


def ids() -> pd.DataFrame:
    """bid, key, n_parts in reader order."""
    return pd.read_csv(STORY / "ids.csv")


def load(source: str, bid: str) -> dict:
    """source is "out" (read from the masked text) or "title_only" (written from memory)."""
    return json.loads((STORY / source / f"{bid}.json").read_text())


def field_text(d: dict, field: str) -> str:
    """One digest field as a string; "" when the reader left it empty."""
    v = d.get(field)
    if not v:
        return ""
    if field == "characters":
        return "\n".join(f"{c['role']}: {c['arc']}" for c in v)
    if field == "subjects":
        return "; ".join(v)
    return str(v)
