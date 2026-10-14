"""Draw the 300-painting sample, the version-pair extras and the 30 second photographs. Seeded.

Run from the repo root:
  uv run --no-project --with pillow --with numpy --with pandas python experiments/painting2vec/exp_describer_blocks/01_sample.py
"""
import json

import numpy as np
import pandas as pd
from PIL import Image

SEED = 20261009
HERE = "experiments/painting2vec/exp_describer_blocks"
PILOT = "data/painting2vec/pilot"
N = 300

CLUSTER_PAINTERS = ["Vincent van Gogh", "Rembrandt", "Francisco Goya", "Édouard Manet", "Peter Paul Rubens",
                    "Titian", "Gustave Courbet", "Diego Velázquez", "Pieter Brueghel the Elder", "Albrecht Dürer",
                    "Paul Gauguin", "Itō Jakuchū"]
PER_PAINTER = 8
GENRE_SETS = {
    "portrait": {"portrait", "self-portrait", "group portrait", "family portrait", "double portrait", "tronie",
                 "equestrian portrait", "court painting"},
    "landscape": {"landscape painting", "marine art", "cityscape", "veduta", "shan shui", "seascape"},
    "still_life": {"still life", "floral painting", "vanitas", "bird-and-flower painting", "kachō-ga"},
    "religious": {"religious art", "Buddhist painting", "Christian art", "sacred art"},
    "interior": {"genre art", "interior view"},
    "crowd": {"history painting", "battle painting"},
    "animal": {"animal art"},
}
PER_GENRE = 14
BROAD = {**{g: "portrait" for g in GENRE_SETS["portrait"]}, **{g: "landscape" for g in GENRE_SETS["landscape"]},
         **{g: "stilllife" for g in GENRE_SETS["still_life"] | GENRE_SETS["animal"]},
         "religious art": "narrative", "mythological painting": "narrative", "history painting": "narrative",
         "allegory": "narrative", "battle painting": "narrative", "Buddhist painting": "narrative",
         "genre art": "genre", "figure painting": "genre", "interior view": "genre", "nude": "nude"}


def chroma(path):
    a = np.asarray(Image.open(path).convert("RGB").resize((64, 64)), dtype=np.int16)
    return float((a.max(-1) - a.min(-1)).mean())


def gset(s):
    return set(s.split("|")) if isinstance(s, str) else set()


def main():
    rng = np.random.RandomState(SEED)
    m = pd.read_csv(f"{PILOT}/meta.csv")
    excluded = set(json.load(open("experiments/painting2vec/exp_separation/results/setup.json"))["excluded"])
    ar = m.px_width / m.px_height
    m["ok"] = (~m.qid.isin(excluded)) & (ar >= 1 / 3) & (ar <= 3) & (m[["px_width", "px_height"]].min(axis=1) >= 300)
    m["painter"] = m.creator_name.fillna("").str.split("|").str[0]
    m["gs"] = m.genres.map(gset)
    m["broad"] = m.gs.map(lambda g: sorted({BROAD[t] for t in g if t in BROAD}))
    by = m.set_index("qid")
    chosen, why = [], {}

    def add(q, reason):
        if q in why:
            why[q] += "|" + reason
            return False
        if not by.ok[q] or chroma(f"{PILOT}/images/{q}.jpg") < 8.0:
            return False
        chosen.append(q)
        why[q] = reason
        return True

    # A. the original 60
    old = pd.read_csv("experiments/painting2vec/describer/sample.csv")
    for q in old.qid:
        chosen.append(q); why[q] = "orig60"

    # B. version pairs with a pilot member; composition judged the same; one pair per painting, balanced by hand
    vm = pd.read_csv("data/painting2vec/versions/meta.csv").set_index("qid")
    vp = pd.read_csv("data/painting2vec/versions/version_pairs.csv")
    P = set(m.qid)
    vp = vp[(vp.composition_match == "yes") & (vp.qid_a.isin(P) | vp.qid_b.isin(P))].copy()
    ca, cb = vp.qid_a.map(vm.creator_qid), vp.qid_b.map(vm.creator_qid)
    vp["hand"] = np.where(ca.isna() | cb.isna(), "other_anon", np.where(ca == cb, "same", "other"))
    vp.loc[(vp.hand == "other_anon") & ~vp.note.str.startswith("different_creator"), "hand"] = "unknown"
    vp = vp[vp.hand != "unknown"].sample(frac=1, random_state=rng)
    vp["both"] = vp.qid_a.isin(P) & vp.qid_b.isin(P)
    vp = vp.sort_values("both", ascending=False, kind="stable")
    used, pairs = set(), []
    for want, hands in [(13, ["same"]), (13, ["other", "other_anon"])]:
        k = 0
        for _, r in vp[vp.hand.isin(hands)].iterrows():
            if k == want:
                break
            if r.qid_a in used or r.qid_b in used:
                continue
            members = [r.qid_a, r.qid_b]
            if any(q in P and (not by.ok[q]) for q in members):
                continue
            if any(chroma(f"data/painting2vec/versions/images/{q}.jpg") < 8.0 for q in members):
                continue
            used.update(members); pairs.append(r); k += 1
    pairs = pd.DataFrame(pairs)[["qid_a", "qid_b", "relation", "hand", "both", "lab_diff", "note"]]
    extras = []
    for _, r in pairs.iterrows():
        for q in (r.qid_a, r.qid_b):
            if q in P:
                add(q, "version")
            else:
                extras.append(q)
    pairs.to_csv(f"{HERE}/version_pairs_used.csv", index=False)

    # C. second photographs: unflagged primary pairs, largest colour difference, not in the original 60
    rp = pd.read_csv("data/painting2vec/repro/repro_pairs.csv")
    rp = rp[(rp.pair_kind == "primary") & rp.flag.isna() & ~rp.qid.isin(old.qid)].sort_values("lab_diff", ascending=False)
    photo = []
    for _, r in rp.iterrows():
        if len(photo) == 30:
            break
        if not by.ok[r.qid] or chroma(f"data/painting2vec/repro/{r.file_b}") < 8.0:
            continue
        if r.qid in why or add(r.qid, "photo"):
            if "photo" not in why[r.qid]:
                why[r.qid] += "|photo"
            photo.append(r)
    photo = pd.DataFrame(photo)[["qid", "file_a", "file_b", "source_b", "lab_diff", "title"]]
    photo.to_csv(f"{HERE}/photo_pairs_used.csv", index=False)

    # D. painter clusters: PER_PAINTER works each, round-robin over broad genres
    for p in CLUSTER_PAINTERS:
        pool = m[(m.painter == p) & m.ok].sample(frac=1, random_state=rng)
        have = [q for q in chosen if by.painter[q] == p]
        for q in have:
            why[q] += "|painter"
        pool = pool[~pool.qid.isin(have)]
        pool["b0"] = pool.broad.map(lambda b: b[0] if b else "none")
        pool["turn"] = pool.groupby("b0").cumcount()
        n = len(have)
        for q in pool.sort_values("turn", kind="stable").qid:
            if n >= PER_PAINTER:
                break
            n += add(q, "painter")

    # E. genres across periods and traditions: PER_GENRE each, one per painter, non-European first, then spread over years
    for g, names in GENRE_SETS.items():
        pool = m[m.gs.map(lambda s: bool(s & names)) & m.ok & ~m.qid.isin(chosen)].sample(frac=1, random_state=rng)
        pool = pool[(pool.painter == "") | (pool.groupby("painter").cumcount() < 1)]
        ne = pool[pool.tradition != "european_american"].head(PER_GENRE // 3)
        eu = pool[pool.tradition == "european_american"].copy()
        eu["era"] = pd.cut(eu.inception_year.fillna(1700), [0, 1500, 1600, 1700, 1800, 1870, 2100], labels=False)
        eu["turn"] = eu.groupby("era").cumcount()
        n = 0
        for q in list(ne.qid) + list(eu.sort_values("turn", kind="stable").qid):
            if n >= PER_GENRE:
                break
            n += add(q, f"genre:{g}")

    # F. fill: non-European, least-represented tradition first, up to 72 in all, then anything, at most 3 more per painter
    rest = m[m.ok & ~m.qid.isin(chosen)].sample(frac=1, random_state=rng)
    ne = rest[rest.tradition != "european_american"].copy()
    have = pd.Series([by.tradition[c] for c in chosen]).value_counts()
    ne["turn"] = ne.groupby("tradition").cumcount() + ne.tradition.map(have).fillna(0)  # least-represented first
    for q in ne.sort_values("turn", kind="stable").qid:
        if sum(by.tradition[c] != "european_american" for c in chosen) >= 72 or len(chosen) >= N - 3:
            break
        add(q, "fill_non_european")
    for q in rest.qid:
        if len(chosen) >= N:
            break
        if by.painter[q] and sum(by.painter[c] == by.painter[q] for c in chosen) >= 3:
            continue
        add(q, "fill")

    s = by.loc[chosen].reset_index()
    s["why"] = [why[q] for q in chosen]
    s["broad"] = s.broad.map("|".join)
    assert len(s) == N and s.qid.is_unique
    cols = ["qid", "why", "stratum", "tradition", "title", "creator_qid", "creator_name", "painter", "inception_year",
            "sitelinks", "genres", "broad", "movements", "px_width", "px_height"]
    s[cols].to_csv(f"{HERE}/sample.csv", index=False)
    ex = vm.loc[extras].reset_index()[["qid", "title", "creator_qid", "creator_name", "inception_year", "genres"]]
    ex.to_csv(f"{HERE}/version_extras.csv", index=False)
    print("sample", len(s), "| version pairs", len(pairs), pairs.hand.value_counts().to_dict(), "| extras", len(ex),
          "| photo pairs", len(photo), "lab_diff", photo.lab_diff.min(), photo.lab_diff.max())
    print(s.why.str.split("|").explode().value_counts().to_string())
    print(s.tradition.value_counts().to_string())
    print(s.painter.value_counts().head(20).to_string())
    print(s.broad.str.split("|").explode().value_counts().to_string())
    print(pd.cut(s.inception_year, [0, 1400, 1500, 1600, 1700, 1800, 1870, 2100]).value_counts().sort_index().to_string())


if __name__ == "__main__":
    main()
