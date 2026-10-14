"""Render name-masked books as anonymous part files for the Story readers.

Readers must not learn the title, so books get opaque ids (b01..) and the mapping
stays in data/story/ids.csv, which readers are never shown.
"""

import csv
import json
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SUBSET = """fathers_garnett fathers_hogarth gentlefolk_garnett gentlefolk_ralston journey_malleson
journey_1871 frankenstein_1818 frankenstein_1831 burnett_princess burnett_sara_crewe holmes_study
holmes_hound oz_wizard oz_land tarzan_apes tarzan_return wells_time wells_worlds wharton_frome
conrad_agent christie_styles zamyatin_we merriman_barlasch hammett_falcon""".split()
PART_WORDS = 12_000


def main() -> None:
    out = ROOT / "data" / "story"
    keys = SUBSET[:]
    random.Random(20261008).shuffle(keys)
    rows = []
    for n, key in enumerate(keys, 1):
        bid = f"b{n:02d}"
        chunks = [json.loads(x) for x in open(ROOT / "data" / "chunks" / "maskB" / f"{key}.jsonl")]
        parts: list[list[str]] = [[]]
        words = 0
        for c in chunks:
            if words >= PART_WORDS:
                parts.append([])
                words = 0
            parts[-1].append(c["text"])
            words += c["n_words"]
        d = out / "parts" / bid
        d.mkdir(parents=True, exist_ok=True)
        for i, p in enumerate(parts, 1):
            (d / f"part_{i:02d}_of_{len(parts):02d}.txt").write_text("\n\n".join(p))
        rows.append({"bid": bid, "key": key, "n_parts": len(parts)})
    with open(out / "ids.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["bid", "key", "n_parts"])
        w.writeheader()
        w.writerows(rows)
    (out / "out").mkdir(exist_ok=True)
    (out / "notes").mkdir(exist_ok=True)


if __name__ == "__main__":
    main()
