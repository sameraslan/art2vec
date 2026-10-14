"""Contact sheets: 12 fixed seeds, seed plus its 8 nearest among the 300, one pair of sheets per block. No names.

  uv run --no-project --with pillow --with numpy --with pandas python experiments/painting2vec/exp_describer_blocks/05_sheets.py
"""
import json
import os

import numpy as np
import pandas as pd
from PIL import Image, ImageDraw

HERE = "experiments/painting2vec/exp_describer_blocks"
OUT = "data/painting2vec/exp_describer_blocks/sheets"
T, PAD = 150, 6
BLOCKS = {"subject": "subject (IDF cosine)", "manner": "manner", "colour": "colour", "felt": "felt",
          "picture": "picture (DINOv2-L cls)", "pixelcomp": "pixel composition (grid8_an)"}


def thumb(q):
    im = Image.open(f"data/painting2vec/pilot/images/{q}.jpg").convert("RGB")
    im.thumbnail((T, T), Image.LANCZOS)
    c = Image.new("RGB", (T, T), (40, 40, 40))
    c.paste(im, ((T - im.width) // 2, (T - im.height) // 2))
    return c


def main():
    os.makedirs(OUT, exist_ok=True)
    rng = np.random.RandomState(20261009)
    S = pd.read_csv(f"{HERE}/sample.csv")
    picks = [S[S.why.str.contains(f"genre:{g}")] for g in ["portrait", "landscape", "still_life", "religious", "interior", "crowd", "animal"]]
    picks += [S[S.painter == p] for p in ["Vincent van Gogh", "Rembrandt", "Itō Jakuchū"]]
    picks += [S[S.tradition.isin(["persian_ottoman", "south_asian"])], S[S.tradition.isin(["chinese", "korean"])]]
    seeds = []
    for p in picks:
        p = p[~p.qid.isin(seeds)]
        seeds.append(p.qid.iloc[rng.randint(len(p))])
    S.set_index("qid").loc[seeds, ["why", "title", "creator_name", "inception_year", "genres"]].to_csv(f"{HERE}/seeds.csv")
    NN = json.load(open(f"{HERE}/neighbours.json"))
    row = {q: i for i, q in enumerate(S.qid)}
    for short, name in BLOCKS.items():
        for half in range(2):
            sheet = Image.new("RGB", (30 + 9 * (T + PAD) + 14, 6 * (T + PAD) + PAD), (255, 255, 255))
            dr = ImageDraw.Draw(sheet)
            for r, q in enumerate(seeds[half * 6:half * 6 + 6]):
                y = PAD + r * (T + PAD)
                dr.text((8, y + T // 2), str(half * 6 + r + 1), fill=(0, 0, 0))
                sheet.paste(thumb(q), (30, y))
                for c, n in enumerate(NN[name][row[q]][:8]):
                    sheet.paste(thumb(n), (30 + 14 + (c + 1) * (T + PAD), y))
            sheet.save(f"{OUT}/{short}_{half + 1}.jpg", quality=88)
    print(pd.read_csv(f"{HERE}/seeds.csv").to_string())


if __name__ == "__main__":
    main()
