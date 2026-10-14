"""Part F: contact sheets for the looking session. One image per seed: the seed in the left column,
its 8 nearest neighbours under each block on a row. No titles or names are drawn; rows carry a
letter only. Neighbour ids are written to results/sheets_neighbours.json for decoding afterwards.
"""
import json

import numpy as np
from PIL import Image, ImageDraw

from lib import DATA, IMG, OUT, cosdist
from run_stage3 import B, C, ev, stats

SEEDS = [
    "Q2016193", "Q220859", "Q151047", "Q12418", "Q500985", "Q969377", "Q185372", "Q2881603",
    "Q117191193", "Q2629559", "Q1091086", "Q693746", "Q2339059", "Q1283024", "Q683274", "Q45585",
    "Q1044742", "Q3873324", "Q698487", "Q587514", "Q116490341", "Q109621099", "Q18683017", "Q78918837",
]
ROWS = {  # letter: (description, vectors)
    "A": ("subject: DINOv2-L cls", lambda: B("dinov2_l__pad", "cls")),
    "B": ("subject: SigLIP 2 embed", lambda: B("siglip2_b__pad", "embed")),
    "C": ("subject residual: DINOv2-L cls minus CSD style", lambda: C.resid(B("dinov2_l__pad", "cls"), [B("csd_l__pad", "style")])),
    "D": ("manner: DINOv2-L second-order statistics (early+mid)", lambda: stats("dinov2_l__pad")),
    "E": ("manner: DINOv2-L meanstd_mid", lambda: B("dinov2_l__pad", "meanstd_mid")),
    "F": ("manner: CSD style", lambda: B("csd_l__pad", "style")),
    "G": ("manner residual: CSD style minus DINOv2-L cls", lambda: C.resid(B("csd_l__pad", "style"), [B("dinov2_l__pad", "cls")])),
    "H": ("manner residual: meanstd_mid minus DINOv2-L cls", lambda: C.resid(B("dinov2_l__pad", "meanstd_mid"), [B("dinov2_l__pad", "cls")])),
}
T = 160
K = 8


def thumb(qid):
    im = Image.open(DATA / "pilot" / "images" / f"{qid}.jpg").convert("RGB")
    im.thumbnail((T - 4, T - 4), Image.LANCZOS)
    cell = Image.new("RGB", (T, T), (60, 60, 60))
    cell.paste(im, ((T - im.width) // 2, (T - im.height) // 2))
    return cell


if __name__ == "__main__":
    m = ev.m
    pos = {q: i for i, q in enumerate(m.qid)}
    sidx = np.array([pos[q] for q in SEEDS])
    neigh = {}
    for letter, (desc, f) in ROWS.items():
        Z = f()[0][ev.keep]
        D = cosdist(Z[sidx], Z)
        D[np.arange(len(sidx)), sidx] = np.inf
        neigh[letter] = np.argsort(D, axis=1)[:, :K]
    out = {"rows": {k: v[0] for k, v in ROWS.items()}, "seeds": {}}
    for si, q in enumerate(SEEDS):
        sheet = Image.new("RGB", (T * (K + 1) + 8, T * len(ROWS)), (20, 20, 20))
        d = ImageDraw.Draw(sheet)
        seed = thumb(q)
        out["seeds"][q] = {}
        for ri, letter in enumerate(ROWS):
            sheet.paste(seed, (0, ri * T))
            d.rectangle([0, ri * T, 16, ri * T + 14], fill=(255, 255, 255))
            d.text((4, ri * T + 1), letter, fill=(0, 0, 0))
            ids = [m.qid[j] for j in neigh[letter][si]]
            out["seeds"][q][letter] = ids
            for ci, nq in enumerate(ids):
                sheet.paste(thumb(nq), (T + 8 + ci * T, ri * T))
        sheet.save(IMG / f"sheet_{si+1:02d}_{q}.jpg", quality=85)
    json.dump(out, open(OUT / "sheets_neighbours.json", "w"), indent=1)
    cols = ["qid", "title", "creator_name", "inception_year", "tradition", "genres"]
    m[m.qid.isin(SEEDS)].set_index("qid").loc[SEEDS].reset_index()[cols].to_csv(OUT / "seeds.csv", index=False)
    print("wrote", len(SEEDS), "sheets to", IMG)
