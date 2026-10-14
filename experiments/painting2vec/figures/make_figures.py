"""Copy a few of the experiments' contact sheets into this folder, small enough to commit.

The sheets themselves are written under data/painting2vec/ (gitignored) by each experiment's sheet
script. This only reads them, shrinks each to at most LONG px on the long side and saves a JPEG.
One image is open at a time.

Every sheet chosen here shows only pilot paintings (data/painting2vec/pilot/images), and the
invariance sheets also the second photographs in data/painting2vec/repro/. See figures/README.md
for the rights note.

  uv run --no-project --with pillow python experiments/painting2vec/figures/make_figures.py [DATA_DIR]

DATA_DIR defaults to data/painting2vec.
"""
import sys
from pathlib import Path

from PIL import Image

LONG = 1400
QUALITY = 80
OUT = Path(__file__).resolve().parent

# (source under DATA_DIR, file written here)
FIGURES = [
    ("exp_separation/sheet_03_Q151047.jpg", "separation_birth_of_venus.jpg"),
    ("exp_separation/sheet_20_Q587514.jpg", "separation_city_rises.jpg"),
    ("exp_separation/sheet_04_Q12418.jpg", "separation_mona_lisa.jpg"),
    ("exp_separation/sheet_13_Q2339059.jpg", "separation_turner.jpg"),
    ("exp_fusion/period_01_Q12418.jpg", "fusion_period_mona_lisa.jpg"),
    ("exp_fusion/period_02_Q45585.jpg", "fusion_period_starry_night.jpg"),
    ("exp_fusion/tint_sheet_01_Q45585.jpg", "fusion_tint_starry_night.jpg"),
    ("exp_describer_blocks/sheets/manner_2.jpg", "describer_manner.jpg"),
    ("exp_describer_blocks/sheets/subject_1.jpg", "describer_subject.jpg"),
    ("exp_invariance/worst_colour_clean.jpg", "invariance_worst_colour.jpg"),
    ("exp_invariance/autocrop_helped.jpg", "invariance_autocrop_helped.jpg"),
]


def main(data: Path) -> None:
    total = 0
    for src, dst in FIGURES:
        with Image.open(data / src) as im:
            im = im.convert("RGB")
            if max(im.size) > LONG:
                s = LONG / max(im.size)
                im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
            im.save(OUT / dst, "JPEG", quality=QUALITY, optimize=True, progressive=True)
            size = (OUT / dst).stat().st_size
            total += size
            print(f"{dst:40s} {im.width}x{im.height}  {size / 1024:.0f} KB")
    print(f"total {total / 1024 / 1024:.2f} MB")


if __name__ == "__main__":
    main(Path(sys.argv[1]) if len(sys.argv) > 1 else Path("data/painting2vec"))
