"""film2vec experiments: film-level vectors from the cached features, and the experiments of PLAN.md.

Throwaway experiment code, not library code. numpy / scipy / scikit-learn on the CPU; no models are loaded.

    analyse.py [--catalog catalog.csv] [--features DIR] [--proxies DIR] [--out results] [--include-extra]

Reads   <home>/experiments/film2vec/features/<id>/{look,time,sound,words}.npz (only where <stage>.json exists)
        <home>/experiments/film2vec/proxies/<name>.npz with arrays `ids` and `vectors` (optional)
Writes  results/results.json, results/RESULTS.md, results/neighbours.json

Every block is: ids + a matrix; rows L2-normalised, centred on the mean of the films present, L2-normalised
again; distance = cosine. Films whose id is not in the catalog are dropped unless --include-extra is given, and
are never counted in the leak statistics.
"""

from __future__ import annotations

import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "2")

import argparse  # noqa: E402
import csv  # noqa: E402
import json  # noqa: E402
import math  # noqa: E402
import zlib  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
from scipy import stats as sps  # noqa: E402
from sklearn.linear_model import RidgeCV  # noqa: E402

HERE = Path(__file__).resolve().parent
SEED = 0
N_SLICES = 8
SUBSAMPLE_NS = [3, 5, 10, 20, 40, 80, 160, 320]
SUBSAMPLE_SEEDS = 5
STILLS_N = 10
MIN_SPEECH_SHARE = 0.05
SAT_GATE = 0.08
MANTEL_PERMS = 200
XPRED_PERMS = 20
RIDGE_ALPHAS = np.logspace(-2, 4, 13)
MIN_FILMS = 5  # below this an experiment is reported as skipped
COLOUR_STATS = ["lum_mean", "lum_std", "lum_p10", "lum_p90", "sat_mean", "colourfulness"]
PRIMARY = ["look:mean", "look_grid", "colour", "time", "motion:mid:mean", "sound:mid:mean", "words", "fused", "fused:look+time"]
FAMILIES = {
    "look": ["look:mean", "look:mean+std", "look:profile8", "look:patchmean", "look_grid"],
    "time": ["time", "time_sl"],
    "motion": ["motion:mid:mean", "motion:mid:mean+std", "motion:last:mean"],
    "sound": ["sound:mid:mean", "sound:mid:mean+std", "sound:last_c:mean", "sound:last_c:mean+std",
              "sound:mid:mean+stats", "sound:stats"],
}  # fmt: skip
NEIGHBOUR_BLOCKS = {
    "look": "look:mean",
    "colour": "colour",
    "time": "time",
    "motion": "motion:mid:mean",
    "sound": "sound:mid:mean",
    "words": "words",
    "fused": "fused",
    "fused:look+time": "fused:look+time",  # an extra list: `fused` needs sound, so silents are only in this one
}


def cache_home() -> Path:
    env = os.environ.get("ART2VEC_HOME")
    return Path(env).expanduser() if env else Path.home() / "Library" / "Caches" / "art2vec"


# ------------------------------------------------------------------------------------------------ loading


def load_stage(d: Path, stage: str) -> dict | None:
    """A stage's arrays, only if its .json marker (written last by extract.py) is there."""
    if not (d / f"{stage}.json").exists() or not (d / f"{stage}.npz").exists():
        return None
    try:
        with np.load(d / f"{stage}.npz") as z:
            return {k: z[k] for k in z.files}
    except Exception as e:  # a half-written or damaged file must not stop the run
        print(f"  {d.name}: {stage}.npz unreadable ({e!r}); stage ignored")
        return None


def read_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text())
    except Exception:
        return {}


def slice_index(t: np.ndarray, lo: float, hi: float, n: int = N_SLICES) -> np.ndarray:
    if hi <= lo:
        return np.zeros(len(t), int)
    return np.clip(((t - lo) / (hi - lo) * n).astype(int), 0, n - 1)


def time_features(shot_len_s: np.ndarray, shot_start_s: np.ndarray, motion_1hz: np.ndarray) -> dict:
    """The hand-built time vector of one film, before z-scoring across films. 32 numbers, named."""
    length = np.maximum(shot_len_s.astype(np.float64), 1e-3)
    duration = float(shot_start_s[-1] + length[-1])
    ll = np.log(length)
    q25, q75 = np.percentile(ll, [25, 75])
    names = ["log_median_shot_s", "iqr_log_shot_s"]
    vals = [float(np.median(ll)), float(q75 - q25)]
    names += [f"log_shot_s_decile{d}" for d in range(10, 100, 10)]
    vals += [float(v) for v in np.percentile(ll, np.arange(10, 100, 10))]
    names += ["frac_shots_over_30s", "frac_shots_under_2s"]
    vals += [float((length > 30).mean()), float((length < 2).mean())]
    n_sl = len(names)  # the shot-length terms end here
    counts = np.bincount(slice_index(shot_start_s, 0.0, duration), minlength=N_SLICES)
    names += [f"cut_rate_slice{i}_rel" for i in range(N_SLICES)] + ["log_shots_per_min"]
    vals += [float(c * N_SLICES / len(length)) for c in counts] + [math.log(len(length) / (duration / 60.0))]
    m = motion_1hz.astype(np.float64)
    ok = np.isfinite(m)
    m_mean = float(m[ok].mean()) if ok.any() else 0.0
    m_std = float(m[ok].std()) if ok.any() else 0.0
    sl = slice_index(np.arange(len(m)) + 0.5, 0.0, float(len(m)))
    prof = []
    for i in range(N_SLICES):
        sel = ok & (sl == i)
        prof.append(float(m[sel].mean() / m_mean) if sel.any() and m_mean > 0 else 1.0)
    names += ["motion_mean", "motion_std"] + [f"motion_slice{i}_rel" for i in range(N_SLICES)]
    vals += [m_mean, m_std] + prof
    return {"names": names, "values": np.array(vals), "n_shot_length_terms": n_sl, "duration_s": duration}


def load_film(fid: str, d: Path) -> dict:
    """Everything analyse.py needs from one film, reduced on the way in so 129 films stay well under 1 GB."""
    meta = read_json(d / "meta.json")
    rec: dict = {"id": fid, "meta": meta, "flags": []}
    diag: dict = {"id": fid, "title": meta.get("title"), "stages": []}
    flags = rec["flags"]
    if meta.get("errors"):
        flags.append(f"meta.json errors: {sorted(meta['errors'])}")

    def check(name: str, a: np.ndarray, nan_ok: bool = False) -> None:
        a = np.asarray(a, np.float64)
        if a.size == 0:
            flags.append(f"{name}: empty")
        elif not nan_ok and not np.isfinite(a).all():
            flags.append(f"{name}: {int((~np.isfinite(a)).sum())} non-finite values")
        elif a.size > 1 and np.nanstd(a) == 0:
            flags.append(f"{name}: constant ({float(np.nanmean(a)):.4g})")

    tz = load_stage(d, "time")
    if tz is not None and len(tz["shot_len_s"]) > 0:
        diag["stages"].append("time")
        check("time.shot_len_s", tz["shot_len_s"])
        check("time.motion_1hz", tz["motion_1hz"], nan_ok=True)
        tf = time_features(tz["shot_len_s"], tz["shot_start_s"], tz["motion_1hz"])
        rec["time"] = tf
        n_shots, med = len(tz["shot_len_s"]), float(np.median(tz["shot_len_s"]))
        nan_share = float((~np.isfinite(tz["motion_1hz"])).mean())
        diag.update(n_shots=n_shots, median_shot_s=round(med, 3), duration_s=round(tf["duration_s"], 1),
                    mean_shot_s=round(float(tz["shot_len_s"].mean()), 3),
                    max_shot_s=round(float(tz["shot_len_s"].max()), 1),
                    motion_nan_share=round(nan_share, 4))  # fmt: skip
        if tf["duration_s"] > 1200 and n_shots < 60:
            flags.append(f"only {n_shots} shots in {tf['duration_s'] / 60:.0f} min")
        if med < 1.0 or med > 30.0:
            flags.append(f"median shot length {med:.2f} s")
        if nan_share > 0.2:
            flags.append(f"motion_1hz is NaN for {nan_share:.0%} of seconds")
        probe_d = (meta.get("probe") or {}).get("duration_s")
        if probe_d and abs(probe_d - tf["duration_s"]) > 0.02 * probe_d + 2:
            flags.append(f"decoded duration {tf['duration_s']:.0f} s vs container {probe_d:.0f} s")

    lz = load_stage(d, "look")
    if lz is not None and len(lz["shot_cls"]) > 0 and len(lz["grid_cls"]) > 0:
        diag["stages"].append("look")
        info = read_json(d / "look.json")
        if info.get("warning"):
            flags.append(f"look.json warning: {info['warning']}")
        for k in ("shot_cls", "shot_patch_mean", "grid_cls", "grid_lum_mean"):  # saturation is 0 in a grey file
            check(f"look.{k}", lz[k])
        t = lz["shot_time_s"].astype(np.float64)
        win = info.get("sampling_window_s") or [float(t.min()), float(t.max())]
        grid = {s: lz[f"grid_{s}"].astype(np.float64) for s in COLOUR_STATS}
        rec["look"] = {
            "cls": lz["shot_cls"],  # float16 [n_shot_frames, 768]; kept for subsampling
            "slice": slice_index(t, float(win[0]), float(win[1])),
            "patch_mean": lz["shot_patch_mean"].astype(np.float32).mean(0),
            "grid_mean": lz["grid_cls"].astype(np.float32).mean(0),
            "colour_scalars": np.array([f(grid[s]) for s in COLOUR_STATS for f in (np.mean, np.std)]),
            "lum_hist": lz["grid_lum_hist"].astype(np.float64).mean(0),
            "hue_hist": lz["grid_hue_hist_chroma"].astype(np.float64).mean(0),
            "sat_mean": float(grid["sat_mean"].mean()),
        }
        diag.update(n_shot_frames=int(len(t)), n_grid_frames=int(len(lz["grid_cls"])),
                    sat_mean=round(rec["look"]["sat_mean"], 4), lum_mean=round(float(grid["lum_mean"].mean()), 4),
                    active_aspect=round(float((info.get("crop") or {}).get("active_aspect") or 0), 3))  # fmt: skip
        if "n_shots" in diag and len(t) < 0.5 * min(diag["n_shots"], 1500):
            flags.append(f"{len(t)} shot frames for {diag['n_shots']} shots")

    mz = load_stage(d, "motion")
    if mz is not None and len(mz["emb_mid"]) > 0:
        diag["stages"].append("motion")
        rec["motion"] = {"mid": mz["emb_mid"], "last": mz["emb_last"]}

    sz = load_stage(d, "sound")
    if sz is not None and len(sz["emb_mid"]) > 0:
        diag["stages"].append("sound")
        for k in ("emb_mid", "emb_last", "rms_db", "spectral_centroid_hz"):
            check(f"sound.{k}", sz[k])
        rms = np.clip(sz["rms_db"].astype(np.float64), -80.0, 0.0)
        cen = np.log(np.maximum(sz["spectral_centroid_hz"].astype(np.float64), 20.0))
        rec["sound"] = {
            "mid": sz["emb_mid"],
            "last": sz["emb_last"],
            "stats": np.array(
                [
                    rms.mean(),
                    rms.std(),
                    *np.percentile(rms, [10, 90]),
                    cen.mean(),
                    cen.std(),
                    *np.percentile(cen, [10, 90]),
                ]
            ),  # fmt: skip
        }
        silent_windows = float((sz["rms_db"] < -60).mean())
        diag.update(n_sound_windows=int(len(rms)), rms_db_mean=round(float(rms.mean()), 1),
                    silent_window_share=round(silent_windows, 3))  # fmt: skip
        if silent_windows > 0.2:
            flags.append(f"{silent_windows:.0%} of sound windows below -60 dB")

    wz = load_stage(d, "words")
    if wz is not None:
        diag["stages"].append("words")
        share, capped = float(wz["speech_share"]), float(wz["speech_share_capped"])
        info = read_json(d / "words.json")
        diag.update(speech_share=round(share, 4), speech_share_capped=round(capped, 4),
                    n_word_chunks=int(len(wz["chunk_emb"])), language=info.get("language"),
                    n_words=info.get("n_words"))  # fmt: skip
        if len(wz["chunk_emb"]) > 0:
            check("words.chunk_emb", wz["chunk_emb"])
            if capped >= MIN_SPEECH_SHARE:
                rec["words"] = wz["chunk_emb"].astype(np.float32).mean(0)
        if capped < MIN_SPEECH_SHARE:
            flags.append(f"speech share {capped:.3f} (capped) under {MIN_SPEECH_SHARE}; left out of words")
        if info.get("n_chunks_truncated_at_512_tokens"):
            flags.append(f"{info['n_chunks_truncated_at_512_tokens']} word chunks truncated at 512 tokens")

    silent = bool(meta.get("silent"))
    for s in ("look", "time") + (() if silent else ("sound", "words")):
        if s not in diag["stages"]:
            flags.append(f"stage {s} missing")
    probe = meta.get("probe") or {}
    if probe.get("height") and probe.get("duration_s") and probe.get("file_bytes"):
        diag.update(height=int(probe["height"]), kbps=round(probe["file_bytes"] * 8 / probe["duration_s"] / 1000, 1))
    diag["flags"] = flags
    rec["diag"] = diag
    return rec


def load_catalog(path: Path) -> dict[str, dict]:
    with open(path, newline="", encoding="utf-8") as fh:
        return {r["id"].strip(): r for r in csv.DictReader(fh)}


# ------------------------------------------------------------------------------------------------- blocks


def l2(x: np.ndarray) -> np.ndarray:
    return x / np.maximum(np.linalg.norm(x, axis=1, keepdims=True), 1e-12)


def finalise(x: np.ndarray) -> np.ndarray:
    """L2 rows, centre on the mean of the films present, L2 again."""
    x = l2(np.asarray(x, np.float64))
    return l2(x - x.mean(0, keepdims=True))


def zscore(x: np.ndarray) -> np.ndarray:
    x = np.asarray(x, np.float64)
    sd = x.std(0)
    return (x - x.mean(0)) / np.where(sd > 0, sd, 1.0) * (sd > 0)


def cos_dist(xn: np.ndarray) -> np.ndarray:
    d = 1.0 - xn @ xn.T
    np.fill_diagonal(d, 0.0)
    return d


def film_rng(seed: int, n: int, fid: str, salt: int) -> np.random.Generator:
    return np.random.default_rng([seed, n, zlib.crc32(fid.encode()), salt])


def pooled_subsample(films: list[dict], key: tuple[str, str], n: int, seed: int) -> np.ndarray:
    """Mean of n rows drawn without replacement from each film's per-shot or per-window vectors."""
    rows = []
    for f in films:
        a = f[key[0]][key[1]]
        take = film_rng(seed, n, f["id"], salt=len(key[0])).choice(len(a), size=min(n, len(a)), replace=False)
        rows.append(a[np.sort(take)].astype(np.float32).mean(0))
    return np.stack(rows)


def mean_std(a: np.ndarray) -> np.ndarray:
    a = a.astype(np.float32)
    return np.concatenate([a.mean(0), a.std(0)])


def build_blocks(films: list[dict]) -> dict[str, dict]:
    """name -> {ids, raw}. `raw` is the matrix before the common normalisation."""
    blocks: dict[str, dict] = {}

    def add(name: str, ids: list[str], raw: np.ndarray, what: str) -> None:
        if ids:
            blocks[name] = {"ids": ids, "raw": np.asarray(raw, np.float64), "what": what}

    fl = [f for f in films if "look" in f]
    if fl:
        ids = [f["id"] for f in fl]
        add("look:mean", ids, np.stack([f["look"]["cls"].astype(np.float32).mean(0) for f in fl]),
            "mean of per-shot DINOv2 CLS vectors")  # fmt: skip
        add("look:mean+std", ids, np.stack([mean_std(f["look"]["cls"]) for f in fl]),
            "per-shot CLS: mean and per-dimension std, concatenated")  # fmt: skip
        prof = []
        for f in fl:
            cls, sl = f["look"]["cls"].astype(np.float32), f["look"]["slice"]
            whole = cls.mean(0)
            prof.append(np.concatenate([cls[sl == i].mean(0) if (sl == i).any() else whole for i in range(N_SLICES)]))
        add("look:profile8", ids, np.stack(prof),
            "per-shot CLS: mean within each of 8 equal slices of the sampled running time, concatenated")  # fmt: skip
        add("look:patchmean", ids, np.stack([f["look"]["patch_mean"] for f in fl]),
            "mean over shots of the mean patch token")  # fmt: skip
        add("look_grid", ids, np.stack([f["look"]["grid_mean"] for f in fl]),
            "mean of DINOv2 CLS over the every-20-s frame set")  # fmt: skip
        gate = np.array([f["look"]["sat_mean"] >= SAT_GATE for f in fl])
        scal = zscore(np.stack([f["look"]["colour_scalars"] for f in fl]))
        lum = zscore(np.stack([f["look"]["lum_hist"] for f in fl]))
        hue = np.stack([f["look"]["hue_hist"] for f in fl])
        hue_z = np.zeros_like(hue)
        if gate.sum() >= 2:  # standardised among the films that have colour; the others sit at zero
            hue_z[gate] = zscore(hue[gate])
        add("colour", ids, np.hstack([scal, lum, hue_z]),
            "every-20-s frames: mean and std over frames of 6 light/colour statistics (12), mean 8-bin luminance "
            "histogram (8), mean 12-bin chroma-weighted hue histogram gated off when mean saturation < 0.08 (12); "
            "z-scored across films")  # fmt: skip

    ft = [f for f in films if "time" in f]
    if ft:
        ids = [f["id"] for f in ft]
        z = zscore(np.stack([f["time"]["values"] for f in ft]))
        add("time", ids, z, "hand-built shot-length, cutting-rate and motion-energy terms, z-scored across films")
        add("time_sl", ids, z[:, : ft[0]["time"]["n_shot_length_terms"]], "the shot-length terms of `time` only")

    fm = [f for f in films if "motion" in f]
    if fm:
        ids = [f["id"] for f in fm]
        add("motion:mid:mean", ids, np.stack([f["motion"]["mid"].astype(np.float32).mean(0) for f in fm]),
            "mean over clips of the V-JEPA 2 ViT-L embedding at about 65% depth, 16 frames from the middle of up to 200 shots")  # fmt: skip
        add("motion:mid:mean+std", ids, np.stack([mean_std(f["motion"]["mid"]) for f in fm]),
            "mean and per-dimension std over clips of the same embedding")
        add("motion:last:mean", ids, np.stack([f["motion"]["last"].astype(np.float32).mean(0) for f in fm]),
            "mean over clips of the V-JEPA 2 final-layer embedding")

    fs = [f for f in films if "sound" in f]
    if fs:
        ids = [f["id"] for f in fs]
        mid_mean = np.stack([f["sound"]["mid"].astype(np.float32).mean(0) for f in fs])
        add("sound:mid:mean", ids, mid_mean, "mean over windows of the EAT middle-layer (block 6 of 12) embedding")
        add("sound:mid:mean+std", ids, np.stack([mean_std(f["sound"]["mid"]) for f in fs]),
            "EAT middle layer: mean and per-dimension std over windows")  # fmt: skip
        corpus = np.stack([f["sound"]["last"].astype(np.float32).mean(0) for f in fs]).mean(0)
        centred = [l2(f["sound"]["last"].astype(np.float64) - corpus) for f in fs]
        add("sound:last_c:mean", ids, np.stack([c.mean(0) for c in centred]),
            "EAT last layer; each window minus the corpus mean (mean of film means), L2-normalised, then "
            "averaged")  # fmt: skip
        add("sound:last_c:mean+std", ids, np.stack([np.concatenate([c.mean(0), c.std(0)]) for c in centred]),
            "as sound:last_c:mean, with the per-dimension std over windows appended")  # fmt: skip
        st = zscore(np.stack([f["sound"]["stats"] for f in fs]))
        add("sound:stats", ids, st,
            "loudness (RMS dB, clipped at -80) and log spectral centroid over windows: mean, std, p10, p90 of each; "
            "z-scored across films")  # fmt: skip
        parts = [finalise(mid_mean), finalise(st)]
        add("sound:mid:mean+stats", ids, np.hstack([equal_variance(p) for p in parts]),
            "sound:mid:mean and sound:stats concatenated, each scaled to the same total variance")  # fmt: skip

    fw = [f for f in films if "words" in f]
    if fw:
        add("words", [f["id"] for f in fw], np.stack([f["words"] for f in fw]),
            f"mean of multilingual-e5-small transcript chunk embeddings; films with capped speech share under "
            f"{MIN_SPEECH_SHARE} left out")  # fmt: skip
    return blocks


def equal_variance(xn: np.ndarray) -> np.ndarray:
    tv = float(xn.var(0).sum())
    return xn / math.sqrt(tv) if tv > 0 else xn


def add_fused(blocks: dict[str, dict], name: str, parts: list[str]) -> None:
    if not all(p in blocks for p in parts):
        return
    shared = [i for i in blocks[parts[0]]["ids"] if all(i in set(blocks[p]["ids"]) for p in parts[1:])]
    if not shared:
        return
    mats = []
    for p in parts:
        pos = {i: n for n, i in enumerate(blocks[p]["ids"])}
        mats.append(equal_variance(finalise(blocks[p]["raw"][[pos[i] for i in shared]])))
    blocks[name] = {"ids": shared, "raw": np.hstack(mats),
                    "what": " + ".join(parts) + ", each normalised on the shared films and scaled to equal total "
                    "variance, concatenated"}  # fmt: skip


def load_proxies(pdir: Path, keep: set[str]) -> dict[str, dict]:
    out: dict[str, dict] = {}
    if not pdir.is_dir():
        return out
    for path in sorted(pdir.glob("*.npz")):
        try:
            with np.load(path, allow_pickle=False) as z:
                ids, vec = [str(i) for i in z["ids"]], np.asarray(z["vectors"], np.float64)
        except Exception as e:
            print(f"  proxy {path.name}: unreadable ({e!r}); skipped")
            continue
        if vec.ndim != 2 or len(ids) != len(vec):
            print(f"  proxy {path.name}: ids and vectors do not match; skipped")
            continue
        sel = [n for n, i in enumerate(ids) if i in keep and np.isfinite(vec[n]).all()]
        sel = [n for k, n in enumerate(sel) if ids[n] not in {ids[m] for m in sel[:k]}]  # first of any duplicate id
        if sel:
            out[f"proxy:{path.stem}"] = {"ids": [ids[n] for n in sel], "raw": vec[sel],
                                         "what": f"proxy vectors from {path.name}"}  # fmt: skip
    return out


# ---------------------------------------------------------------------------------------------- measures


def topk(d: np.ndarray, k: int) -> np.ndarray:
    d = d.copy()
    np.fill_diagonal(d, np.inf)
    return np.argsort(d, axis=1, kind="stable")[:, :k]


def overlap(na: np.ndarray, nb: np.ndarray) -> float:
    return float(np.mean([len(set(a) & set(b)) / len(a) for a, b in zip(na, nb, strict=True)]))


def k_for(n: int, k: int) -> int:
    return max(1, min(k, n - 2))


def agreement(da: np.ndarray, db: np.ndarray, k: int, perms: int = 0, seed: int = SEED) -> dict | None:
    """Spearman of the two pairwise-distance vectors and mean top-k overlap, each with its chance level."""
    n = len(da)
    if n < MIN_FILMS:
        return None
    kk = k_for(n, k)
    iu = np.triu_indices(n, 1)
    ra, rb = sps.rankdata(da[iu]), sps.rankdata(db[iu])
    rho = float(np.corrcoef(ra, rb)[0, 1]) if ra.std() > 0 and rb.std() > 0 else float("nan")
    out = {"n": n, "k": kk, "spearman": rho, "overlap": overlap(topk(da, kk), topk(db, kk)),
           "overlap_chance": kk / (n - 1), "spearman_chance": 0.0}  # fmt: skip
    if perms:
        rng = np.random.default_rng([seed, n, perms])
        rbm = np.zeros((n, n))
        rbm[iu] = rb
        rbm += rbm.T
        null_rho, null_ov = [], []
        na = topk(da, kk)
        for _ in range(perms):
            p = rng.permutation(n)
            null_rho.append(np.corrcoef(ra, rbm[np.ix_(p, p)][iu])[0, 1])
            null_ov.append(overlap(na, topk(db[np.ix_(p, p)], kk)))
        out.update(spearman_null_mean=float(np.mean(null_rho)), spearman_null_p95=float(np.percentile(null_rho, 95)),
                   overlap_null_mean=float(np.mean(null_ov)), overlap_null_p95=float(np.percentile(null_ov, 95)),
                   null_permutations=perms)  # fmt: skip
    return out


class Space:
    """The finalised blocks, with distances on any subset of films."""

    def __init__(self, blocks: dict[str, dict]) -> None:
        self.blocks = blocks
        self.pos = {name: {i: n for n, i in enumerate(b["ids"])} for name, b in blocks.items()}
        self.norm = {name: finalise(b["raw"]) for name, b in blocks.items()}
        self.dist = {name: cos_dist(x) for name, x in self.norm.items()}

    def shared(self, a: str, b: str) -> list[str]:
        return [i for i in self.blocks[a]["ids"] if i in self.pos[b]]

    def sub(self, name: str, ids: list[str]) -> np.ndarray:
        idx = [self.pos[name][i] for i in ids]
        return self.dist[name][np.ix_(idx, idx)]

    def pair(self, a: str, b: str, k: int, perms: int = MANTEL_PERMS) -> dict | None:
        ids = self.shared(a, b)
        r = agreement(self.sub(a, ids), self.sub(b, ids), k, perms) if len(ids) >= MIN_FILMS else None
        return {"a": a, "b": b, **r} if r else None


def exp_pairs(space: Space, names: list[str], k: int) -> list[dict]:
    names = [n for n in names if n in space.blocks]
    rows = []
    for i, a in enumerate(names):
        for b in names[i + 1 :]:
            r = space.pair(a, b, k)
            if r:
                rows.append(r)
    return rows


def exp_subsampling(space: Space, films: list[dict], k: int) -> dict:
    out = {}
    for block, key in (("look:mean", ("look", "cls")), ("sound:mid:mean", ("sound", "mid"))):
        label = block
        if block not in space.blocks or len(space.blocks[block]["ids"]) < MIN_FILMS:
            continue
        by_id = {f["id"]: f for f in films}
        fl = [by_id[i] for i in space.blocks[block]["ids"]]
        sizes = np.array([len(f[key[0]][key[1]]) for f in fl])
        full = space.dist[block]
        rows = []
        for n in SUBSAMPLE_NS:
            subs = [pooled_subsample(fl, key, n, s) for s in range(SUBSAMPLE_SEEDS)]
            res = [agreement(cos_dist(finalise(x)), full, k) for x in subs]
            ov, rho = np.array([r["overlap"] for r in res]), np.array([r["spearman"] for r in res])
            rows.append({"n_requested": n, "mean_n_used": float(np.minimum(sizes, n).mean()),
                         "films_capped": int((sizes < n).sum()), "overlap_mean": float(ov.mean()),
                         "overlap_sd": float(ov.std(ddof=1)), "spearman_mean": float(rho.mean()),
                         "spearman_sd": float(rho.std(ddof=1)), "overlap_chance": res[0]["overlap_chance"],
                         "spearman_chance": 0.0, "k": res[0]["k"], "n_films": len(fl),
                         "seeds": SUBSAMPLE_SEEDS})  # fmt: skip
        out[label] = {"unit": "shot frames" if key[0] == "look" else "10-s windows", "rows": rows,
                      "available_per_film": {"min": int(sizes.min()), "median": float(np.median(sizes)),
                                             "max": int(sizes.max())}}  # fmt: skip
    return out


def loo_ridge(a: np.ndarray, target: np.ndarray, n_comp: int) -> tuple[np.ndarray, list]:
    """Leave-one-film-out folds of A reduced to n_comp PCs (fitted on the training films only)."""
    n = len(a)
    folds = []
    for i in range(n):
        tr = np.delete(np.arange(n), i)
        mu = a[tr].mean(0)
        _, _, vt = np.linalg.svd(a[tr] - mu, full_matrices=False)
        ztr = (a[tr] - mu) @ vt[:n_comp].T
        sd = np.where(ztr.std(0) > 0, ztr.std(0), 1.0)
        folds.append((tr, ztr / sd, ((a[i] - mu) @ vt[:n_comp].T) / sd))
    return predict_folds(folds, target), folds


def predict_folds(folds: list, target: np.ndarray) -> np.ndarray:
    pred = np.zeros_like(target)
    for i, (tr, ztr, zte) in enumerate(folds):
        model = RidgeCV(alphas=RIDGE_ALPHAS, alpha_per_target=True).fit(ztr, target[tr])
        pred[i] = model.predict(zte[None])[0]
    return pred


def loo_r2(target: np.ndarray, pred: np.ndarray) -> np.ndarray:
    """R^2 against the leave-one-out mean of the training films, so predicting that mean scores exactly 0."""
    n = len(target)
    base = (target.sum(0, keepdims=True) - target) / (n - 1)
    return 1.0 - ((target - pred) ** 2).sum(0) / np.maximum(((target - base) ** 2).sum(0), 1e-12)


def exp_cross_prediction(space: Space, films: list[dict], k: int) -> dict:
    src = "look:mean"
    if src not in space.blocks or len(space.blocks[src]["ids"]) < MIN_FILMS:
        return {"skipped": "too few films"}
    by_id = {f["id"]: f for f in films}
    look_ids = space.blocks[src]["ids"]
    fl = [by_id[i] for i in look_ids]
    stills = [finalise(pooled_subsample(fl, ("look", "cls"), STILLS_N, s)) for s in range(SUBSAMPLE_SEEDS)]
    pos = {i: n for n, i in enumerate(look_ids)}
    out: dict = {"source": f"look:mean from {STILLS_N} random shot frames per film", "seeds": SUBSAMPLE_SEEDS,
                 "targets": {}, "plain": []}  # fmt: skip
    targets = [b for b in ("time", "sound:mid:mean", "colour", "words") if b in space.blocks]
    plain_targets = targets + [b for b in space.blocks if b not in targets and not b.startswith("fused")]
    for b in plain_targets:
        ids = [i for i in look_ids if i in space.pos[b]]
        if len(ids) < MIN_FILMS:
            continue
        idx = [pos[i] for i in ids]
        res = [agreement(cos_dist(finalise(s[idx])), space.sub(b, ids), k, MANTEL_PERMS if n == 0 else 0)
               for n, s in enumerate(stills)]  # fmt: skip
        out["plain"].append({
            "a": f"look:{STILLS_N}stills", "b": b, "n": res[0]["n"], "k": res[0]["k"],
            "spearman_mean": float(np.mean([r["spearman"] for r in res])),
            "spearman_sd": float(np.std([r["spearman"] for r in res], ddof=1)),
            "overlap_mean": float(np.mean([r["overlap"] for r in res])),
            "overlap_sd": float(np.std([r["overlap"] for r in res], ddof=1)),
            "overlap_chance": res[0]["overlap_chance"], "spearman_chance": 0.0,
            "spearman_null_p95": res[0]["spearman_null_p95"], "overlap_null_p95": res[0]["overlap_null_p95"],
        })  # fmt: skip
    for b in targets:
        ids = [i for i in look_ids if i in space.pos[b]]
        n = len(ids)
        if n < 2 * MIN_FILMS:
            out["targets"][b] = {"skipped": f"{n} shared films"}
            continue
        idx = [pos[i] for i in ids]
        bn = finalise(space.blocks[b]["raw"][[space.pos[b][i] for i in ids]])
        u, s, _ = np.linalg.svd(bn - bn.mean(0), full_matrices=False)
        q = int(min(8, n - 2, (s > 1e-9 * s[0]).sum()))
        target = zscore(u[:, :q] * s[:q])
        var_kept = float((s[:q] ** 2).sum() / (s**2).sum())
        n_comp = int(max(1, min(16, n // 4)))
        d_full, d_t = cos_dist(bn), cos_dist(finalise(target))
        kk = k_for(n, k)
        n_full, n_t = topk(d_full, kk), topk(d_t, kk)
        r2s, ov_full, ov_t, per_pc = [], [], [], []
        null_r2, null_ov = [], []
        rng = np.random.default_rng([SEED, n, 4])
        for seed, st in enumerate(stills):
            pred, folds = loo_ridge(finalise(st[idx]), target, n_comp)
            r2 = loo_r2(target, pred)
            n_pred = topk(cos_dist(finalise(pred)), kk)
            per_pc.append(r2)
            r2s.append(float(r2.mean()))
            ov_full.append(overlap(n_pred, n_full))
            ov_t.append(overlap(n_pred, n_t))
            if seed == 0:  # chance: the same pipeline with the films of B shuffled against the films of A
                for _ in range(XPRED_PERMS):
                    p = rng.permutation(n)
                    pp = predict_folds(folds, target[p])
                    null_r2.append(float(loo_r2(target[p], pp).mean()))
                    null_ov.append(overlap(topk(cos_dist(finalise(pp)), kk), topk(d_full[np.ix_(p, p)], kk)))
        out["targets"][b] = {
            "n": n, "k": kk, "a_components": n_comp, "b_components": q, "b_variance_in_components": var_kept,
            "r2_mean": float(np.mean(r2s)), "r2_sd": float(np.std(r2s, ddof=1)),
            "r2_per_component": [float(v) for v in np.mean(per_pc, axis=0)],
            "r2_chance_mean": float(np.mean(null_r2)), "r2_chance_p95": float(np.percentile(null_r2, 95)),
            "overlap_pred_vs_true_mean": float(np.mean(ov_full)),
            "overlap_pred_vs_true_sd": float(np.std(ov_full, ddof=1)),
            "overlap_pred_vs_true_components_mean": float(np.mean(ov_t)),
            "overlap_true_components_vs_true": overlap(n_t, n_full),
            "overlap_chance": kk / (n - 1), "overlap_chance_shuffled_mean": float(np.mean(null_ov)),
            "overlap_chance_shuffled_p95": float(np.percentile(null_ov, 95)), "chance_permutations": XPRED_PERMS,
        }  # fmt: skip
    return out


# ------------------------------------------------------------------------------------------------- leaks


def colour_class(c: str) -> str:
    c = (c or "").strip().lower()
    return c if c in ("bw", "tinted") else "colour"


def split(s: str | None) -> frozenset[str]:
    return frozenset(x.strip() for x in (s or "").split(";") if x.strip())


def film_attributes(catalog: dict[str, dict], films: list[dict]) -> dict[str, dict]:
    """Per catalog id: the sets and labels the leak tests use. Copy attributes come from meta.json."""
    attr: dict[str, dict] = {}
    for fid, r in catalog.items():
        year = int(r["year"]) if (r.get("year") or "").strip().isdigit() else None
        attr[fid] = {
            "director": split(r.get("director")),
            "lead_actor": split(r.get("lead_actors")),
            "decade": frozenset([str(year // 10 * 10)]) if year else frozenset(),
            "country": split(r.get("country")),
            "silent_or_sound": frozenset([r.get("silent_or_sound", "").strip().lower()]),
            "colour_class": frozenset([colour_class(r.get("colour", ""))]),
            "kind": frozenset([r.get("kind", "").strip().lower()]),
            "height_bucket": frozenset(),
            "bitrate_tercile": frozenset(),
        }
    rates = {}
    for f in films:
        d = f["diag"]
        if f["id"] in attr and "height" in d:
            h = d["height"]
            attr[f["id"]]["height_bucket"] = frozenset(["<=480" if h <= 480 else "<=720" if h <= 720 else ">720"])
            rates[f["id"]] = d["kbps"]
    if len(rates) >= 3:
        lo, hi = np.percentile(list(rates.values()), [100 / 3, 200 / 3])
        for fid, v in rates.items():
            attr[fid]["bitrate_tercile"] = frozenset(["low" if v <= lo else "mid" if v <= hi else "high"])
    return attr


SHARE_ATTRS = ["director", "lead_actor", "decade", "country", "silent_or_sound", "colour_class", "kind"]
KNN_ATTRS = ["decade", "silent_or_sound", "colour_class", "height_bucket", "bitrate_tercile"]


def share_matrix(sets: list[frozenset]) -> np.ndarray:
    n = len(sets)
    m = np.zeros((n, n), bool)
    for i in range(n):
        for j in range(i + 1, n):
            m[i, j] = m[j, i] = bool(sets[i] & sets[j])
    return m


def knn_accuracy(d: np.ndarray, labels: list[str], k: int) -> dict:
    nb = topk(d, k)
    hits = 0
    for i, row in enumerate(nb):
        votes = [labels[j] for j in row]  # nearest first
        counts = {v: votes.count(v) for v in votes}
        best = max(counts.values())
        hits += next(v for v in votes if counts[v] == best) == labels[i]  # a tie goes to the nearest of the tied
    vals, cnt = np.unique(labels, return_counts=True)
    return {"accuracy": hits / len(labels), "majority_rate": float(cnt.max() / cnt.sum()), "n": len(labels),
            "n_classes": int(len(vals)), "k": k}  # fmt: skip


def leaks_for(d: np.ndarray, ids: list[str], attr: dict[str, dict], k: int) -> dict | None:
    n = len(ids)
    if n < MIN_FILMS:
        return None
    kk = k_for(n, k)
    nb = topk(d, kk)
    out: dict = {"n": n, "k": kk, "share": {}, "knn": {}}
    share = {a: share_matrix([attr[i][a] for i in ids]) for a in ("director", "lead_actor")}
    for a in SHARE_ATTRS:
        m = share.get(a)
        if m is None:
            m = share_matrix([attr[i][a] for i in ids])
        out["share"][a] = {"top_k": float(np.mean([m[i, nb[i]].mean() for i in range(n)])),
                           "chance": float(m.sum(1).mean() / (n - 1))}  # fmt: skip
    for a in KNN_ATTRS:
        have = [j for j, i in enumerate(ids) if attr[i][a]]
        if len(have) < MIN_FILMS:
            continue
        labels = [next(iter(attr[ids[j]][a])) for j in have]
        out["knn"][a] = knn_accuracy(d[np.ix_(have, have)], labels, k_for(len(have), k))
    occ = np.bincount(nb.ravel(), minlength=n)
    p = kk / (n - 1)
    out["hubness"] = {
        "k_occurrence_skew": float(sps.skew(occ)) if occ.std() > 0 else 0.0,
        "skew_chance": float((1 - 2 * p) / math.sqrt((n - 1) * p * (1 - p))) if 0 < p < 1 else 0.0,
        "share_in_no_list": float((occ == 0).mean()),
        "share_in_no_list_chance": float((1 - p) ** (n - 1)),
        "max_k_occurrence": int(occ.max()),
    }
    iu = np.triu_indices(n, 1)
    pct = (sps.rankdata(d[iu]) - 0.5) / len(iu[0])
    sel = (share["lead_actor"] & ~share["director"])[iu]
    m = int(sel.sum())
    out["actor_not_director"] = {
        "n_pairs": m, "mean_distance_percentile": float(pct[sel].mean()) if m else None, "chance": 0.5,
        "chance_sd_if_independent": float(1 / math.sqrt(12 * m)) if m else None,
    }  # fmt: skip
    return out


def exp_leaks(space: Space, extra: dict[str, tuple[list[str], np.ndarray]], attr: dict[str, dict], k: int) -> dict:
    out = {}
    for name in space.blocks:
        ids = [i for i in space.blocks[name]["ids"] if i in attr]
        r = leaks_for(space.sub(name, ids), ids, attr, k)
        if r:
            out[name] = r
    for name, (ids_all, d) in extra.items():
        keep = [j for j, i in enumerate(ids_all) if i in attr]
        r = leaks_for(d[np.ix_(keep, keep)], [ids_all[j] for j in keep], attr, k)
        if r:
            out[name] = r
    return out


def neighbour_lists(space: Space, titles: dict[str, tuple[str, str]], k: int) -> dict:
    out: dict = {"k": k, "blocks": {}, "block_names": {}}
    for label, name in NEIGHBOUR_BLOCKS.items():
        if name not in space.blocks or len(space.blocks[name]["ids"]) < 2:
            continue
        ids, d = space.blocks[name]["ids"], space.dist[name]
        kk = min(k, len(ids) - 1)
        nb = topk(d, kk)
        out["block_names"][label] = name
        out["blocks"][label] = {
            fid: {"title": titles[fid][0], "year": titles[fid][1], "neighbours": [
                {"id": ids[j], "title": titles[ids[j]][0], "year": titles[ids[j]][1],
                 "distance": round(float(d[i, j]), 4)}
                for j in nb[i]]}
            for i, fid in enumerate(ids)
        }  # fmt: skip
    return out


# ------------------------------------------------------------------------------------------------ report


def fmt(v: object) -> str:
    if v is None:
        return ""
    if isinstance(v, float):
        if math.isnan(v):
            return "nan"
        return f"{v:.0f}" if abs(v) >= 1000 else f"{v:.1f}" if abs(v) >= 100 else f"{v:.3f}"
    if isinstance(v, list | tuple):
        return "; ".join(fmt(x) for x in v)
    return str(v).replace("|", "/")


def table(headers: list[str], rows: list[list]) -> str:
    if not rows:
        return "(no rows)\n"
    lines = ["| " + " | ".join(headers) + " |", "|" + "|".join("---" for _ in headers) + "|"]
    lines += ["| " + " | ".join(fmt(c) for c in r) + " |" for r in rows]
    return "\n".join(lines) + "\n"


def pair_table(rows: list[dict]) -> str:
    return table(
        ["block A", "block B", "films", "k", "Spearman", "chance", "shuffled p95", "top-k overlap", "chance k/(n-1)",
         "shuffled p95"],
        [[r["a"], r["b"], r["n"], r["k"], r["spearman"], 0.0, r.get("spearman_null_p95"), r["overlap"],
          r["overlap_chance"], r.get("overlap_null_p95")] for r in rows],
    )  # fmt: skip


def write_report(res: dict, path: Path) -> None:
    k = res["k"]
    o: list[str] = ["# film2vec experiments: results\n"]
    o.append(f"Films with features: {res['n_films']} ({res['n_catalog_films']} in the catalog). k = {k}. "
             f"Seed {SEED}. Distance: cosine after L2, centring on the films present, L2. Tables only; "
             "every number sits next to its chance level.\n")  # fmt: skip
    o.append("## Blocks\n")
    o.append(table(["block", "films", "dimension", "what"],
                   [[n, b["n"], b["dim"], b["what"]] for n, b in res["blocks"].items()]))  # fmt: skip
    o.append("## Films\n")
    o.append(table(
        ["id", "title", "stages", "min", "shots", "median shot s", "shot frames", "grid frames", "sound windows",
         "speech share", "capped", "word chunks", "height", "kbps", "flags"],
        [[d["id"], d.get("title"), ",".join(d["stages"]), round(d["duration_s"] / 60, 1) if "duration_s" in d else None,
          d.get("n_shots"), d.get("median_shot_s"), d.get("n_shot_frames"), d.get("n_grid_frames"),
          d.get("n_sound_windows"), d.get("speech_share"), d.get("speech_share_capped"), d.get("n_word_chunks"),
          d.get("height"), d.get("kbps"), d["flags"]] for d in res["films"]],
    ))  # fmt: skip
    o.append("## 1. Block agreement\n")
    o.append("Spearman: correlation of the two pairwise-distance vectors over the shared films; chance 0, and the "
             f"95th percentile over {MANTEL_PERMS} shuffles of the films of block B. Overlap: mean share of the "
             "top-k lists in common.\n")  # fmt: skip
    o.append(pair_table(res["exp1_block_agreement"]))
    o.append("## 2. Pooling\n")
    for fam, rows in res["exp2_pooling"].items():
        o.append(f"### {fam}\n")
        o.append(pair_table(rows))
    o.append("## 3. Subsampling\n")
    for name, e in res["exp3_subsampling"].items():
        av = e["available_per_film"]
        o.append(f"### {name} from n {e['unit']} per film\n")
        o.append(f"Against the full version. Available per film: min {av['min']}, median {av['median']:.0f}, "
                 f"max {av['max']}. {SUBSAMPLE_SEEDS} seeds; sd over seeds.\n")  # fmt: skip
        o.append(table(
            ["n", "mean n used", "films capped", "top-k overlap", "sd", "chance", "Spearman", "sd", "chance"],
            [[r["n_requested"], r["mean_n_used"], r["films_capped"], r["overlap_mean"], r["overlap_sd"],
              r["overlap_chance"], r["spearman_mean"], r["spearman_sd"], 0.0] for r in e["rows"]],
        ))  # fmt: skip
    x = res["exp4_cross_prediction"]
    o.append("## 4. Cross-prediction\n")
    if "skipped" in x:
        o.append(f"Skipped: {x['skipped']}.\n")
    else:
        o.append(f"A = {x['source']}. A reduced to PCs fitted on the training films, ridge (alpha by efficient "
                 "leave-one-out inside each fold) to each standardised PC of B, leave-one-film-out. R^2 is against "
                 f"the training-fold mean, so 0 = no skill. Chance: the films of B shuffled, {XPRED_PERMS} times, "
                 f"first seed. Mean and sd over {x['seeds']} draws of the stills. For the overlap the shuffled "
                 "figure is the baseline to use: a leave-one-out prediction with no skill is the training mean, "
                 "which mirrors the held-out film's own value and so keeps some of its neighbours, lifting the "
                 "overlap above k/(n-1).\n")  # fmt: skip
        o.append(table(
            ["B", "films", "k", "A PCs", "B PCs", "B variance kept", "mean R^2", "sd", "shuffled mean", "shuffled p95",
             "overlap pred vs true B", "sd", "chance k/(n-1)", "shuffled mean", "shuffled p95",
             "overlap pred vs B PCs", "overlap B PCs vs true B"],
            [[b, t["n"], t["k"], t["a_components"], t["b_components"], t["b_variance_in_components"], t["r2_mean"],
              t["r2_sd"], t["r2_chance_mean"], t["r2_chance_p95"], t["overlap_pred_vs_true_mean"],
              t["overlap_pred_vs_true_sd"], t["overlap_chance"], t["overlap_chance_shuffled_mean"],
              t["overlap_chance_shuffled_p95"], t["overlap_pred_vs_true_components_mean"],
              t["overlap_true_components_vs_true"]] for b, t in x["targets"].items() if "skipped" not in t],
        ))  # fmt: skip
        skipped = [f"{b}: {t['skipped']}" for b, t in x["targets"].items() if "skipped" in t]
        if skipped:
            o.append("Skipped: " + "; ".join(skipped) + ".\n")
        o.append("R^2 per component of B (mean over draws):\n")
        done = {b: t for b, t in x["targets"].items() if "skipped" not in t}
        o.append(table(["B", "R^2 of PC1..PCq"], [[b, t["r2_per_component"]] for b, t in done.items()]))
        o.append(f"The measures of experiment 1 for look from {STILLS_N} stills against each block "
                 "(shuffled p95 from the first draw):\n")  # fmt: skip
        o.append(table(
            ["block B", "films", "k", "Spearman", "sd", "chance", "shuffled p95", "top-k overlap", "sd",
             "chance k/(n-1)", "shuffled p95"],
            [[r["b"], r["n"], r["k"], r["spearman_mean"], r["spearman_sd"], 0.0, r["spearman_null_p95"],
              r["overlap_mean"], r["overlap_sd"], r["overlap_chance"], r["overlap_null_p95"]] for r in x["plain"]],
        ))  # fmt: skip
    lk = res["exp5_leaks"]
    o.append("## 5. Leaks\n")
    o.append("Catalog films only. Each cell: value / chance.\n")
    o.append("### Share of top-k neighbours with the same attribute / share of all other films with it\n")
    o.append(table(["block", "films", "k"] + SHARE_ATTRS,
                   [[n, e["n"], e["k"]] + [f"{e['share'][a]['top_k']:.3f} / {e['share'][a]['chance']:.3f}"
                                           for a in SHARE_ATTRS] for n, e in lk.items()]))  # fmt: skip
    o.append("### Leave-one-out kNN accuracy / majority-class rate (films with the label)\n")
    o.append(table(["block"] + KNN_ATTRS,
                   [[n] + [f"{e['knn'][a]['accuracy']:.3f} / {e['knn'][a]['majority_rate']:.3f} (n={e['knn'][a]['n']})"
                           if a in e["knn"] else "" for a in KNN_ATTRS] for n, e in lk.items()]))  # fmt: skip
    o.append("### Hubness\n")
    o.append("Chance: neighbour lists drawn at random (binomial k-occurrence).\n")
    o.append(table(["block", "films", "k", "k-occurrence skew", "chance", "share in nobody's list", "chance",
                    "max k-occurrence"],
                   [[n, e["n"], e["k"], e["hubness"]["k_occurrence_skew"], e["hubness"]["skew_chance"],
                     e["hubness"]["share_in_no_list"], e["hubness"]["share_in_no_list_chance"],
                     e["hubness"]["max_k_occurrence"]] for n, e in lk.items()]))  # fmt: skip
    o.append("### Pairs sharing a lead actor but no director\n")
    o.append("Mean percentile of their distance among all pairs (0 = nearest). Chance 0.5; sd of that mean if the "
             "pairs were independent.\n")  # fmt: skip
    o.append(table(["block", "pairs", "mean percentile", "chance", "chance sd"],
                   [[n, e["actor_not_director"]["n_pairs"], e["actor_not_director"]["mean_distance_percentile"], 0.5,
                     e["actor_not_director"]["chance_sd_if_independent"]] for n, e in lk.items()]))  # fmt: skip
    o.append("## 6. Neighbour lists\n")
    o.append("`neighbours.json`: " + ", ".join(f"{b} ({n} films)" for b, n in res["exp6_neighbours"].items()) + ".\n")
    if res["notes"]:
        o.append("## Notes\n")
        o += [f"- {n}" for n in res["notes"]]
        o.append("")
    path.write_text("\n".join(o))


# -------------------------------------------------------------------------------------------------- main


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--catalog", default=str(HERE / "catalog.csv"))
    ap.add_argument("--features", default=str(cache_home() / "experiments" / "film2vec" / "features"))
    ap.add_argument("--proxies", default=str(cache_home() / "experiments" / "film2vec" / "proxies"))
    ap.add_argument("--out", default=str(HERE / "results"))
    ap.add_argument("--include-extra", action="store_true",
                    help="keep films whose id is not in the catalog (never in the leak statistics)")  # fmt: skip
    args = ap.parse_args()

    catalog = load_catalog(Path(args.catalog))
    fdir = Path(args.features)
    notes: list[str] = []
    films = []
    for d in sorted(p for p in fdir.iterdir() if p.is_dir()) if fdir.is_dir() else []:
        if d.name not in catalog and not args.include_extra:
            continue
        rec = load_film(d.name, d)
        if "look" in rec or "time" in rec:
            films.append(rec)
    n_cat = sum(f["id"] in catalog for f in films)
    k = 10 if len(films) >= 60 else 3
    print(f"{len(films)} films with features ({n_cat} in the catalog); k = {k}")
    if len(films) != n_cat:
        notes.append(f"{len(films) - n_cat} films not in the catalog are in the blocks and the neighbour lists "
                     "(--include-extra) and are left out of experiment 5.")  # fmt: skip

    blocks = build_blocks(films)
    add_fused(blocks, "fused", ["look:mean", "time", "sound:mid:mean"])
    add_fused(blocks, "fused:look+time", ["look:mean", "time"])
    keep = set(catalog) | {f["id"] for f in films}
    proxies = load_proxies(Path(args.proxies), keep if args.include_extra else set(catalog))
    blocks.update(proxies)
    if not proxies:
        notes.append("No proxy blocks: the proxies directory is missing or empty.")
    space = Space(blocks)

    titles = {i: (r.get("title") or i, r.get("year") or "") for i, r in catalog.items()}
    for f in films:
        titles.setdefault(f["id"], (f["meta"].get("title") or f["id"], str(f["meta"].get("year") or "")))

    res: dict = {
        "k": k, "seed": SEED, "n_films": len(films), "n_catalog_films": n_cat,
        "blocks": {n: {"n": len(b["ids"]), "dim": int(b["raw"].shape[1]), "what": b["what"]}
                   for n, b in blocks.items()},
        "films": [f["diag"] for f in films],
        "time_feature_names": films[0]["time"]["names"] if films and "time" in films[0] else [],
        "notes": notes,
    }  # fmt: skip
    enough = len(films) >= MIN_FILMS
    if not enough:
        notes.append(f"Fewer than {MIN_FILMS} films: experiments 1 to 5 have no rows.")

    primary = [b for b in PRIMARY if b in blocks] + sorted(proxies)
    res["exp1_block_agreement"] = exp_pairs(space, primary, k)
    res["exp2_pooling"] = {fam: exp_pairs(space, names, k) for fam, names in FAMILIES.items()}
    print("experiments 1, 2 done")
    res["exp3_subsampling"] = exp_subsampling(space, films, k)
    print("experiment 3 done")
    res["exp4_cross_prediction"] = exp_cross_prediction(space, films, k)
    print("experiment 4 done")

    attr = film_attributes(catalog, films)
    extra = {}
    if "look:mean" in blocks and enough:
        by_id = {f["id"]: f for f in films}
        ids = blocks["look:mean"]["ids"]
        st = pooled_subsample([by_id[i] for i in ids], ("look", "cls"), STILLS_N, 0)
        extra[f"look:{STILLS_N}stills (seed 0)"] = (ids, cos_dist(finalise(st)))
    res["exp5_leaks"] = exp_leaks(space, extra, attr, k)
    nb = neighbour_lists(space, titles, k)
    res["exp6_neighbours"] = {b: len(v) for b, v in nb["blocks"].items()}

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    (out / "neighbours.json").write_text(json.dumps(nb, indent=1, ensure_ascii=False))
    (out / "results.json").write_text(json.dumps(res, indent=1, ensure_ascii=False, default=float))
    write_report(res, out / "RESULTS.md")

    print("\nblocks: " + ", ".join(f"{n} [{b['n']}x{b['dim']}]" for n, b in res["blocks"].items()))
    for r in res["exp1_block_agreement"]:
        print(f"  {r['a']:>16} ~ {r['b']:<16} n={r['n']:<3} spearman {r['spearman']:+.3f} "
              f"(p95 {r['spearman_null_p95']:+.3f})  overlap@{r['k']} {r['overlap']:.3f} "
              f"(chance {r['overlap_chance']:.3f})")  # fmt: skip
    for name, e in res["exp3_subsampling"].items():
        print(f"  subsample {name}: " + ", ".join(f"n={r['n_requested']}: {r['overlap_mean']:.2f}" for r in e["rows"])
              + f" (chance {e['rows'][0]['overlap_chance']:.2f})")  # fmt: skip
    for b, t in res["exp4_cross_prediction"].get("targets", {}).items():
        if "skipped" not in t:
            print(f"  {STILLS_N} stills -> {b}: R2 {t['r2_mean']:+.3f} (shuffled {t['r2_chance_mean']:+.3f}), overlap "
                  f"{t['overlap_pred_vs_true_mean']:.3f} (chance {t['overlap_chance']:.3f})")  # fmt: skip
    flagged = [d for d in res["films"] if d["flags"]]
    print(f"{len(flagged)} films with flags" + "".join(f"\n  {d['id']} {d.get('title')}: {'; '.join(d['flags'])}"
                                                       for d in flagged))  # fmt: skip
    print(f"wrote {out / 'results.json'}, {out / 'RESULTS.md'}, {out / 'neighbours.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
