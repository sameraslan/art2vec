"""Spot-check helper: labelled contact sheets, built one tile at a time, written to a scratch directory.

    python 07_contact_sheets.py pilot <out_dir>      48 pilot images, a fixed sample (half rank stratum, half non-European)
    python 07_contact_sheets.py repro <out_dir>      reproduction pairs side by side, spread over the lab_diff range
    python 07_contact_sheets.py versions <out_dir>   every version pair side by side
"""
import csv
import hashlib
import sys
from pathlib import Path

from PIL import Image, ImageDraw

from common import DATA

TILE = 300


def h(s):
    return hashlib.md5(s.encode()).hexdigest()


def sheet(items, out: Path, cols=4, rows=3):
    """items: [(path, caption)]"""
    out.parent.mkdir(parents=True, exist_ok=True)
    canvas = Image.new("RGB", (cols * TILE, rows * (TILE + 16)), "white")
    d = ImageDraw.Draw(canvas)
    for i, (path, cap) in enumerate(items[:cols * rows]):
        x, y = (i % cols) * TILE, (i // cols) * (TILE + 16)
        with Image.open(path) as im:
            im = im.convert("RGB")
            im.thumbnail((TILE - 4, TILE - 4))
            canvas.paste(im, (x + (TILE - im.width) // 2, y + 16 + (TILE - im.height) // 2))
        d.text((x + 3, y + 2), cap[:48], fill="black")
    canvas.save(out, "JPEG", quality=80)
    print(out)


def main(kind, out_dir):
    out_dir = Path(out_dir)
    if kind == "pilot":
        meta = list(csv.DictReader(open(DATA / "pilot" / "meta.csv", encoding="utf-8")))
        a = sorted((r for r in meta if r["stratum"] == "sitelink_rank"), key=lambda r: h(r["qid"]))[:24]
        b = sorted((r for r in meta if r["stratum"] != "sitelink_rank"), key=lambda r: h(r["qid"]))[:24]
        items = [(DATA / "pilot" / "images" / f"{r['qid']}.jpg", f"{r['qid']} {r['title']}") for r in a + b]
        for i in range(0, len(items), 12):
            sheet(items[i:i + 12], out_dir / f"pilot_{i // 12}.jpg")
    elif kind == "repro":
        rows = [r for r in csv.DictReader(open(DATA / "repro" / "repro_pairs.csv", encoding="utf-8")) if r["pair_kind"] == "primary"]
        rows.sort(key=lambda r: float(r["lab_diff"]))
        n = int(sys.argv[3]) if len(sys.argv) > 3 else 36
        pick = [rows[round(i * (len(rows) - 1) / (n - 1))] for i in range(n)]
        items = []
        for r in pick:
            items.append((DATA / "repro" / r["file_a"], f"{r['qid']} commons"))
            items.append((DATA / "repro" / r["file_b"], f"{r['source_b']} d={r['lab_diff']}"))
        for i in range(0, len(items), 12):
            sheet(items[i:i + 12], out_dir / f"repro_{i // 12}.jpg")
    elif kind == "versions":
        rows = list(csv.DictReader(open(DATA / "versions" / "version_pairs.csv", encoding="utf-8")))
        items = []
        for r in rows:
            items.append((DATA / "versions" / "images" / f"{r['qid_a']}.jpg", f"{r['qid_a']} {r['relation'][:14]}"))
            items.append((DATA / "versions" / "images" / f"{r['qid_b']}.jpg", f"{r['qid_b']} {r['note'][:30]}"))
        for i in range(0, len(items), 24):
            sheet(items[i:i + 24], out_dir / f"versions_{i // 24:02d}.jpg", cols=6, rows=4)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
