"""Shared loading, block building and distances for the describer-blocks experiment. numpy/pandas only."""
import glob
import json

import numpy as np
import pandas as pd

HERE = "experiments/painting2vec/exp_describer_blocks"
FEAT = "data/painting2vec/features"
FELT = "calm tense tender eerie festive desolate joyful melancholy awed uneasy intimate playful solemn alarming sensual lonely hopeful oppressive dreamlike energetic still warm cold mysterious".split()
THINGS = "sky clouds sun_or_moon water trees mountains_or_hills rocks field_or_grass flowers fruit_or_food snow_or_ice fire_or_smoke buildings window_or_door furniture bridge road_or_path boat_or_ship cart_or_carriage horse dog cattle_or_sheep bird fish other_animal man woman child old_person nude crowd dead_or_wounded_body soldier_or_armour weapon book_or_paper musical_instrument vessel_or_tableware curtain_or_drapery hat_or_headdress jewellery_or_crown flag_or_banner halo wings cross skull_or_skeleton written_text".split()
SCALES_V1 = "abstraction contour finish detail depth palette_breadth saturation colour_temperature darkness contrast crowding symmetry closeness".split()
SCALES_V2 = "edge_hardness outline stroke_direction flat_colour modelling ornament idealisation distortion".split()
CUES = "linear_perspective atmospheric_perspective overlap size_diminution cast_shadows foreshortening stacked_space".split()
HUES = "red orange yellow green blue purple pink brown gold black white grey".split()
COUNTS = ["0", "1", "2", "3-5", "6+"]
SETTINGS = ["interior", "landscape", "townscape", "seascape", "garden", "sky_or_heaven", "plain_background", "mixed", "none"]
# which scale goes in which block
MANNER_V1 = ["abstraction", "contour", "finish", "detail", "depth"]
MANNER = MANNER_V1 + SCALES_V2
COLOUR_SCALES = ["palette_breadth", "saturation", "colour_temperature", "darkness", "contrast"]
COMP_SCALES = ["crowding", "symmetry", "closeness"]


def flat(r):
    """One describer record -> flat dict of numbers and strings."""
    d = {f"f_{k}": r["felt"][k] for k in FELT}
    d.update({f"t_{k}": r["subject"]["things"][k] for k in THINGS})
    d.update(people=r["subject"]["people"], animals=r["subject"]["animals"], setting=r["subject"]["setting"],
             action=r["subject"]["main_action"])
    d.update({f"m_{k}": v for k, v in r["manner"].items()})
    if "space" in r:
        d.update({f"d_{k}": r["space"]["depth_cues"][k] for k in CUES})
        c = r["colour"]
        d.update({f"h_{k}": c["hues"][k] for k in HUES})
        d.update(main_hue=c["main_hue"], accent_hue=c["accent_hue"], value_key=c["value_key"])
    g = r["recognition"]
    d.update(rec=g["recognised"], rec_title=g["title"], rec_painter=g["painter"], conf=g["confidence"],
             school=g["guess_school"], century=g["guess_century"])
    return d


def load_records():
    """Returns (items, v2, v1): items is one row per analysed image with every field.

    item ids: a pilot qid; a non-pilot version partner's qid; '<qid>__b' for a second photograph.
    For the original 60 the v1 fields are the earlier study's `orig` marks and only the added fields come from v2.
    """
    key = pd.read_csv(f"{HERE}/key.csv").set_index("code")
    rows = []
    for f in sorted(glob.glob(f"{HERE}/raw/batch_*.json")):
        for r in json.load(open(f))["records"]:
            rows.append({"code": r["code"], **flat(r)})
    v2 = pd.DataFrame(rows).set_index("code").join(key)
    v2["item"] = np.where(v2.kind == "photo_b", v2.qid + "__b", v2.qid)
    v2 = v2.set_index("item")
    k1 = pd.read_csv("experiments/painting2vec/describer/key.csv")
    k1 = k1[k1.condition == "orig"].set_index("code")
    rows = []
    for f in sorted(glob.glob("experiments/painting2vec/describer/raw/batch_*.json")):
        for r in json.load(open(f))["records"]:
            if r["code"] in k1.index:
                rows.append({"item": k1.qid[r["code"]], **flat(r)})
    v1 = pd.DataFrame(rows).set_index("item")
    items = v2.copy()
    items.loc[v1.index, v1.columns] = v1
    num = [c for c in items.columns if c[:2] in ("f_", "t_", "m_", "d_", "h_")]
    items[num] = items[num].astype(float)
    return items, v2, v1


def zfit(X, fit):
    mu, sd = X[fit].mean(0), X[fit].std(0)
    return (X - mu) / np.where(sd > 0, sd, 1.0)


def onehot(s, cats):
    return np.stack([(s == c).to_numpy(float) for c in cats], 1)


def thermo(s):
    i = s.map(COUNTS.index).to_numpy()
    return np.stack([(i >= k).astype(float) for k in range(1, 5)], 1)


def subject_binary(it):
    X = np.hstack([it[[f"t_{k}" for k in THINGS]].to_numpy(float), onehot(it.setting, SETTINGS),
                   thermo(it.people), thermo(it.animals)])
    names = THINGS + [f"setting={s}" for s in SETTINGS] + [f"people>={c}" for c in COUNTS[1:]] + [f"animals>={c}" for c in COUNTS[1:]]
    return X, names


def group(X, fit, total):
    """z-score, then scale the whole group to a fixed total variance."""
    Z = zfit(X, fit)
    live = (X[fit].std(0) > 0).sum()
    return Z * np.sqrt(total / max(live, 1))


def manner_matrix(it, fit, cols=MANNER, cues=True):
    parts = [zfit(it[[f"m_{k}" for k in cols]].to_numpy(float), fit)]
    if cues:
        parts.append(group(it[[f"d_{k}" for k in CUES]].to_numpy(float), fit, 2.0))
    return np.hstack(parts)


def colour_matrix(it, fit):
    vk = it.value_key.map({"high": 0, "mid": 1, "low": 2}).to_numpy(float)[:, None]
    sc = np.hstack([it[[f"m_{k}" for k in COLOUR_SCALES]].to_numpy(float), vk])
    return np.hstack([zfit(sc, fit), group(it[[f"h_{k}" for k in HUES]].to_numpy(float), fit, 4.0),
                      group(onehot(it.main_hue, HUES), fit, 2.0), group(onehot(it.accent_hue, HUES + ["none"]), fit, 1.0)])


def euclid(X):
    g = (X * X).sum(1)
    return np.sqrt(np.maximum(g[:, None] + g[None] - 2 * X @ X.T, 0))


def cosine(X):
    n = X / np.maximum(np.linalg.norm(X, axis=1, keepdims=True), 1e-12)
    return np.maximum(1 - n @ n.T, 0)


def jaccard(B):
    inter = B @ B.T
    union = B.sum(1)[:, None] + B.sum(1)[None] - inter
    return 1 - np.where(union > 0, inter / np.maximum(union, 1), 1.0)


def pca_fit(X, k):
    mu = X.mean(0)
    _, s, vt = np.linalg.svd(X - mu, full_matrices=False)
    return mu, vt[:k], s[:k] / np.sqrt(len(X) - 1)


def store_rows(name, part, ids_wanted):
    """Rows of a feature store for the wanted ids: pilot qids, version qids, or '<qid>__b' second photographs."""
    ph = pd.read_csv(f"{HERE}/photo_pairs_used.csv").set_index("qid").file_b.str.replace(".jpg", "", regex=False)
    out, pil = {}, None
    for s in ("pilot", "versions", "repro"):
        ids = open(f"{FEAT}/{s}/{name}.ids.txt").read().split()
        A = np.load(f"{FEAT}/{s}/{name}.npz")[part].astype(np.float32)
        pos = {q: i for i, q in enumerate(ids)}
        if s == "pilot":
            pil = (ids, A)
        for w in ids_wanted:
            if w in out:
                continue
            k = ph[w[:-3]] if w.endswith("__b") else w
            if (s == "repro") == w.endswith("__b") and k in pos:
                out[w] = A[pos[k]]
    return np.stack([out[w] for w in ids_wanted]), pil
