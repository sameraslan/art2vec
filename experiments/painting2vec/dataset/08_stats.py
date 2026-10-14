"""Step 8: the numbers quoted in README.md, recomputed from what is on disk. Prints Markdown."""
import os
from collections import Counter

import numpy as np
import pandas as pd

from common import DATA, HERE, lab_thumb


def du(path):
    seen, total, n = set(), 0, 0
    for root, _, files in os.walk(path):
        for f in files:
            st = os.stat(os.path.join(root, f))
            n += 1
            if st.st_ino not in seen:  # hard links counted once
                seen.add(st.st_ino)
                total += st.st_size
    return total, n


def table(counter, head, top=None):
    rows = counter.most_common(top) if top else sorted(counter.items(), key=lambda kv: str(kv[0]))
    print(f"| {head} | n |\n|---|---|")
    for k, v in rows:
        print(f"| {k} | {v} |")
    print()


def main():
    m = pd.read_csv(DATA / "pilot" / "meta.csv", dtype=str).fillna("")
    print("## pilot:", len(m), "paintings\n")
    table(Counter(m["stratum"]), "stratum")
    sl = m["sitelinks"].astype(int)
    for s, g in m.groupby("stratum"):
        v = g["sitelinks"].astype(int)
        print(f"- {s}: sitelinks min {v.min()}, median {int(v.median())}, max {v.max()}; with zero sitelinks {(v == 0).sum()}")
    print()
    yr = pd.to_numeric(m["inception_year"], errors="coerce")
    cent = yr.apply(lambda y: "unknown" if pd.isna(y) else f"{int(y // 100 + 1):02d}th" if y > 0 else "BCE")
    table(Counter(cent), "century")
    table(Counter(m["tradition"]), "tradition")
    table(Counter(m["country_name"].replace("", "(none recorded)")), "country (origin, else creator citizenship)", top=30)
    table(Counter(m["collection_name"].str.split("|").str[0].replace("", "(none recorded)")), "holding collection (first listed)", top=30)
    print("distinct collections:", m["collection_name"].str.split("|").str[0].nunique(), "\n")
    painters = Counter(c for cs in m["creator_name"] for c in cs.split("|") if c)
    big = [(k, v) for k, v in painters.most_common() if v >= 8]
    print("painters with 8+ works:", len(big), "| distinct painters:", len(painters), "| no creator recorded:", (m["creator_qid"] == "").sum())
    print(", ".join(f"{k} {v}" for k, v in big), "\n")
    print("### metadata coverage (non-empty)\n")
    for c in ["title", "creator_qid", "creator_death_year", "inception_year", "movements", "genres", "depicts", "materials",
              "height_cm", "width_cm", "collection_qid", "country_qid", "inventory_number", "fame_score", "met_id", "aic_id",
              "nga_id", "rijksmuseum_id", "prado_id", "louvre_ark", "google_arts_id", "rkdimages_id", "joconde_id", "artuk_id",
              "getty_id", "philadelphia_id", "mfa_boston_id", "walters_id", "mia_id", "cleveland_id"]:
        print(f"- {c}: {(m[c] != '').sum()}")
    print()
    table(Counter(m["licence"]), "Commons licence")
    table(Counter(m["pd_basis"]), "PD basis")
    table(Counter(m["in_poc"].replace("", "not in canon candidates.csv")), "in_poc (canon agent's file)")
    w, h = m["px_width"].astype(int), m["px_height"].astype(int)
    long_side = np.maximum(w, h)
    print(f"stored long side: =1024 for {(long_side == 1024).sum()}, under 1024 for {(long_side < 1024).sum()} (min {long_side.min()})")
    ar = w / h
    print("stored short side under 200 px (long scrolls shrunk to a strip):", (np.minimum(w, h) < 200).sum(), "| under 100 px:", (np.minimum(w, h) < 100).sum())
    print(f"aspect ratio (w/h): min {ar.min():.2f}, max {ar.max():.2f}; wider than 3:1: {(ar > 3).sum()}; taller than 1:3: {(ar < 1/3).sum()}\n")
    grey = []
    for q in m["qid"]:
        t = lab_thumb(DATA / "pilot" / "images" / f"{q}.jpg")
        if float(np.hypot(t[..., 1], t[..., 2]).mean()) < 2.0:
            grey.append(q)
    print("near-greyscale stored images (mean LAB chroma < 2):", len(grey))
    g = m[m["qid"].isin(grey)]
    print(dict(Counter(g["tradition"])), "\n", " ".join(grey[:60]), "\n")
    kw = m[m["materials"].str.contains("chalk|charcoal|pencil|graphite|pastel|engraving|woodcut|etching", case=False)]
    print("materials naming a drawing/print medium:", len(kw))
    print("; ".join(f"{q} {t[:30]} [{x[:40]}]" for q, t, x in list(zip(kw["qid"], kw["title"], kw["materials"]))[:25]), "\n")
    det = m[m["commons_file"].str.contains(r"detail|cropped|\bcrop\b|frame", case=False)]
    print("Commons file names containing detail/crop/frame:", len(det), "|", "; ".join(det["qid"] + " " + det["commons_file"].str[:50]), "\n")

    r = pd.read_csv(DATA / "repro" / "repro_pairs.csv", dtype=str).fillna("")
    p = r[r["pair_kind"] == "primary"]
    print("## repro: paintings", r["qid"].nunique(), "| pair rows", len(r), "| primary pairs", len(p),
          "| paintings with 3 reproductions", (r.groupby("qid")["file_b"].nunique() >= 2).sum(), "\n")
    table(Counter(p["source_b"].str.rstrip("23")), "second source (primary pair)")
    table(Counter(p["flag"].replace("", "none")), "flag (primary pairs)")
    table(Counter(r["flag"].replace("", "none")), "flag (all pair rows)")
    d = p["lab_diff"].astype(float)
    print(f"lab_diff of primary pairs: min {d.min():.2f}, quartiles {d.quantile(.25):.2f} / {d.median():.2f} / {d.quantile(.75):.2f}, max {d.max():.2f}")
    mm = m.set_index("qid")
    print("repro paintings by stratum:", dict(Counter(mm.loc[p["qid"], "stratum"])), "\n")

    v = pd.read_csv(DATA / "versions" / "version_pairs.csv", dtype=str).fillna("")
    vm = pd.read_csv(DATA / "versions" / "meta.csv", dtype=str).fillna("")
    used = set(v["qid_a"]) | set(v["qid_b"])
    print("## versions: pairs", len(v), "| paintings in kept pairs", len(used), "| rows in versions/meta.csv", len(vm),
          "| of the kept-pair paintings also in pilot:", len(used & set(m["qid"])), "\n")
    table(Counter(v["relation"]), "relation")
    table(Counter(v["relation"] + " / " + v["composition_match"]), "relation / composition_match")
    print("versions paintings failing the strict pilot PD rule (pd_basis empty):", (vm[vm["qid"].isin(used)]["pd_basis"] == "").sum(), "\n")

    print("## disk\n")
    tot = 0
    for name in ("pilot", "repro", "versions", "cache"):
        b, n = du(DATA / name)
        print(f"- data/painting2vec/{name}: {b:,} bytes, {n} files")
    seen, total = set(), 0
    for name in ("pilot", "repro", "versions", "cache"):
        for root, _, files in os.walk(DATA / name):
            for f in files:
                st = os.stat(os.path.join(root, f))
                if st.st_ino not in seen:
                    seen.add(st.st_ino)
                    total += st.st_size
    print(f"- total, hard links counted once: {total:,} bytes ({total / 1e6:.0f} MB)")
    b, n = du(HERE)
    print(f"- experiments/painting2vec/dataset: {b:,} bytes, {n} files")


if __name__ == "__main__":
    main()
