"""Contact sheets of reproduction pairs, one image in memory at a time."""

from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image, ImageDraw

from common import DATA, ROOT

sys.path.insert(0, str(ROOT / "experiments" / "painting2vec"))

T = 230  # thumbnail box


def thumb(path: Path, boxes=None) -> Image.Image:
    with Image.open(path) as im:
        im = im.convert("RGB")
        w, h = im.size
        s = T / max(w, h)
        t = im.resize((max(1, round(w * s)), max(1, round(h * s))), Image.BILINEAR)
    if boxes:
        d = ImageDraw.Draw(t)
        for (l, tp, r, b), col in boxes:
            if (l, tp, r, b) != (0, 0, w, h):
                d.rectangle([l * s, tp * s, r * s - 1, b * s - 1], outline=col, width=2)
    return t


def pair_sheet(items, out: Path, cols: int = 3, with_boxes: bool = False) -> None:
    """items: list of (file_a stem, file_b stem, [label lines])."""
    if with_boxes:
        from features.preprocess import autocrop_box, to_srgb
    cw, ch = 2 * T + 14, T + 46
    rows = (len(items) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * cw, rows * ch), (40, 40, 40))
    d = ImageDraw.Draw(sheet)
    for i, (a, b, lines) in enumerate(items):
        x0, y0 = (i % cols) * cw, (i // cols) * ch
        for j, stem in enumerate((a, b)):
            p = DATA / "repro" / f"{stem}.jpg"
            boxes = None
            if with_boxes:
                with Image.open(p) as im:
                    im.load()
                    img = to_srgb(im)
                boxes = [(autocrop_box(img, "frame"), (255, 40, 40)), (autocrop_box(img, "border"), (255, 230, 0))]
                del img
            t = thumb(p, boxes)
            sheet.paste(t, (x0 + 4 + j * (T + 4) + (T - t.width) // 2, y0 + 42 + (T - t.height) // 2))
        for k, ln in enumerate(lines[:3]):
            d.text((x0 + 5, y0 + 2 + 13 * k), ln[:78], fill=(255, 255, 255))
    out.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(out, quality=85)
