"""Draw the 60-painting sample (20 famous, 20 mid, 20 obscure), seeded.

Run from the repo root:
  uv run --no-project --with pillow --with numpy --with pandas python experiments/painting2vec/describer/01_sample.py
"""
import numpy as np
import pandas as pd
from PIL import Image

SEED = 20261008
META = "data/painting2vec/pilot/meta.csv"
IMG = "data/painting2vec/pilot/images/{}.jpg"
OUT = "experiments/painting2vec/describer/sample.csv"


def chroma(qid):
    """Mean (max-min) over RGB on a 64 px thumbnail, 0-255. Near 0 means a greyscale file."""
    a = np.asarray(Image.open(IMG.format(qid)).convert("RGB").resize((64, 64)), dtype=np.int16)
    return float((a.max(-1) - a.min(-1)).mean())


def usable(df):
    df = df[df.title.notna() & df.inception_year.notna()].copy()
    ar = df.px_width / df.px_height
    df = df[(ar >= 0.5) & (ar <= 2.0) & (df[["px_width", "px_height"]].min(axis=1) >= 450)]
    return df


def drop_grey(df):
    df = df.copy()
    df["chroma"] = [chroma(q) for q in df.qid]
    return df[df.chroma >= 8.0]


def main():
    rng = np.random.RandomState(SEED)
    m = usable(pd.read_csv(META))
    m["first_creator"] = m.creator_name.fillna("").str.split("|").str[0]
    rank = m[m.stratum == "sitelink_rank"]

    # famous: top sitelinks, at most two per painter
    fam = drop_grey(rank.sort_values(["sitelinks", "fame_score"], ascending=False).head(60))
    fam = fam[fam.groupby("first_creator").cumcount() < 2].head(20)

    # mid: rank stratum, sitelinks 12-20 (median to about the 85th centile), one per painter
    mid = rank[(rank.sitelinks >= 12) & (rank.sitelinks <= 20) & ~rank.qid.isin(fam.qid)]
    mid = drop_grey(mid.sample(80, random_state=rng))
    mid = mid[mid.groupby("first_creator").cumcount() < 1].head(20)

    # obscure: 2 per non-European stratum with sitelinks <= 2, plus 8 from the floor of the rank stratum
    obs = []
    for s in sorted(x for x in m.stratum.unique() if x.startswith("non_european")):
        pool = m[(m.stratum == s) & (m.sitelinks <= 2)]
        obs.append(drop_grey(pool.sample(min(12, len(pool)), random_state=rng)).head(2))
    floor = rank[(rank.sitelinks == rank.sitelinks.min()) & ~rank.qid.isin(mid.qid)]
    fl = drop_grey(floor.sample(30, random_state=rng))
    obs.append(fl[fl.groupby("first_creator").cumcount() < 1].head(8))
    obs = pd.concat(obs)

    fam["fame"], mid["fame"], obs["fame"] = "famous", "mid", "obscure"
    s = pd.concat([fam, mid, obs])
    assert len(s) == 60 and s.qid.is_unique, len(s)
    cols = ["qid", "fame", "stratum", "tradition", "title", "creator_name", "inception_year", "sitelinks",
            "fame_score", "genres", "movements", "depicts", "px_width", "px_height", "chroma"]
    s[cols].to_csv(OUT, index=False)
    print(s[["qid", "fame", "stratum", "title", "creator_name", "inception_year", "sitelinks", "chroma"]].to_string())


if __name__ == "__main__":
    main()
