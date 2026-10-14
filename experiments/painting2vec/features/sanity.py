"""Sanity checks on the sample.

    uv run python -m features.sanity make                 # altered copies + framed test images
    uv run python -m features.sanity autocrop             # how well the auto-crop does
    uv run python -m features.sanity table --orig <features dir> --alt <features dir>

`make` writes, for five sample paintings, two altered copies each into data/painting2vec/sample_alt/:
  <id>__warm.jpg  warm cast (sRGB R x1.08, B x0.86) and a 3% crop off every side, JPEG q92
  <id>__bc.jpg    contrast x1.2 about mid-grey, brightness +0.06, JPEG q60
`table` asks, per feature: is the altered copy closer to its original than every other painting is?
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

from .colour import palette_emd
from .preprocess import autocrop_box, list_images, load_image
from .store import DATA_DIR

ALT_KINDS = ("warm", "bc")


def _pick_five(paths: list[Path]) -> list[Path]:
    man = {m["id"]: m for m in json.loads((paths[0].parent / "manifest.json").read_text())}
    plain = [p for p in paths if not man[p.stem]["tag"]]
    return plain[:: max(1, len(plain) // 5)][:5]


def make(sample: Path) -> None:
    paths = list_images(sample)
    alt = sample.parent / "sample_alt"
    alt.mkdir(exist_ok=True)
    for p in _pick_five(paths):
        img = load_image(p)
        a = np.asarray(img, np.float32) / 255
        warm = np.clip(a * np.array([1.08, 1.0, 0.86], np.float32), 0, 1)
        h, w, _ = warm.shape
        dy, dx = round(0.03 * h), round(0.03 * w)
        Image.fromarray((warm[dy : h - dy, dx : w - dx] * 255).round().astype(np.uint8)).save(alt / f"{p.stem}__warm.jpg", quality=92)
        bc = np.clip((a - 0.5) * 1.2 + 0.5 + 0.06, 0, 1)
        Image.fromarray((bc * 255).round().astype(np.uint8)).save(alt / f"{p.stem}__bc.jpg", quality=60)
        print("altered", p.stem)

    # framed test images with known inner boxes
    fr = sample.parent / "sample_frames"
    fr.mkdir(exist_ok=True)
    truth = {}
    rs = np.random.RandomState(3)
    for p in paths[::4][:8]:
        img = load_image(p)
        w, h = img.size
        m = round(0.07 * min(w, h))
        for kind in ("white", "black", "wall", "gilt"):
            if kind in ("white", "black"):
                canvas = Image.new("RGB", (w + 2 * m, h + 2 * m), (250, 250, 248) if kind == "white" else (6, 6, 6))
                box = (m, m, m + w, m + h)
            elif kind == "wall":  # plain wall with slight noise and a lighting gradient; no frame
                wall = np.full((h + 4 * m, w + 4 * m, 3), (176, 170, 160), np.float32)
                wall += np.linspace(-10, 10, wall.shape[1])[None, :, None] + rs.randn(*wall.shape) * 2.5
                canvas = Image.fromarray(np.clip(wall, 0, 255).astype(np.uint8))
                box = (2 * m, 2 * m, 2 * m + w, 2 * m + h)
            else:  # wall, then a textured gold frame with a dark inner lip
                wall = np.full((h + 4 * m, w + 4 * m, 3), (188, 184, 176), np.float32) + rs.randn(h + 4 * m, w + 4 * m, 3) * 2.5
                canvas = Image.fromarray(np.clip(wall, 0, 255).astype(np.uint8))
                d = ImageDraw.Draw(canvas)
                for i in range(m):  # ridged moulding
                    shade = 150 + 60 * np.sin(i / m * 3 * np.pi) + rs.randint(-6, 6)
                    c = (int(np.clip(shade + 25, 0, 255)), int(np.clip(shade - 5, 0, 255)), int(np.clip(shade - 80, 0, 255)))
                    d.rectangle((m + i, m + i, 3 * m + w - 1 - i, 3 * m + h - 1 - i), outline=c)
                d.rectangle((2 * m - 3, 2 * m - 3, 2 * m + w + 2, 2 * m + h + 2), outline=(40, 30, 18), width=3)
                box = (2 * m, 2 * m, 2 * m + w, 2 * m + h)
            canvas.paste(img, box[:2])
            name = f"{p.stem}__{kind}"
            canvas.save(fr / f"{name}.jpg", quality=90)
            truth[name] = box
    (fr / "truth.json").write_text(json.dumps(truth, indent=1))
    print(len(truth), "framed test images in", fr)


def autocrop_report(sample: Path) -> None:
    fr = sample.parent / "sample_frames"
    truth = json.loads((fr / "truth.json").read_text())
    print("Synthetic borders and frames (known inner box). ok = every side within 1.5% of the short side.")
    print("| case | mode | ok | mean abs side error (% of short side) |\n|---|---|---|---|")
    for kind in ("white", "black", "wall", "gilt"):
        for mode in ("border", "frame"):
            errs, ok = [], 0
            names = [n for n in truth if n.endswith("__" + kind)]
            for n in names:
                img = load_image(fr / f"{n}.jpg")
                box = autocrop_box(img, mode)
                t = truth[n]
                short = min(t[2] - t[0], t[3] - t[1])
                e = [abs(a - b) / short * 100 for a, b in zip(box, t, strict=True)]
                errs.append(np.mean(e))
                ok += max(e) < 1.5
            print(f"| {kind} | {mode} | {ok}/{len(names)} | {np.mean(errs):.2f} |")
    print("\nUnframed images (nothing should be cut): share of the area removed.")
    print("| set | mode | images cropped at all | mean area removed (%) | worst (%) | worst id |\n|---|---|---|---|---|---|")
    sets = {"sample": list_images(sample)}
    for extra in ("pilot/images", "repro", "versions"):
        d = sample.parent / extra
        if d.is_dir():
            ps = [p for p in sorted(d.rglob("*")) if p.suffix.lower() in (".jpg", ".jpeg", ".png")][:150]
            if ps:
                sets[extra + " (first 150; may truly have borders)"] = ps
    for label, ps in sets.items():
        for mode in ("border", "frame"):
            lost = []
            for p in ps:
                try:
                    img = load_image(p)
                except Exception:  # noqa: BLE001
                    continue
                b = autocrop_box(img, mode)
                lost.append((100 * (1 - (b[2] - b[0]) * (b[3] - b[1]) / (img.width * img.height)), p.stem))
            v = np.array([x[0] for x in lost])
            worst = max(lost)
            print(f"| {label} | {mode} | {(v > 0).sum()}/{len(v)} | {v.mean():.2f} | {worst[0]:.1f} | {worst[1]} |")


def _dist(a: np.ndarray, B: np.ndarray, metric: str) -> np.ndarray:
    if metric == "emd":
        return np.array([palette_emd(a, b) for b in B])
    if metric == "cos":
        return 1 - (B @ a) / (np.linalg.norm(B, axis=1) * np.linalg.norm(a) + 1e-12)
    return np.linalg.norm(B - a, axis=1)


def table(orig: Path, alt: Path, only: str | None) -> None:
    """Per feature and alteration: copies ranked nearest (of 5), and d(original, copy) divided by
    d(original, nearest other painting): mean and worst over the five. Under 1 passes; smaller is better."""
    names = sorted(p.stem for p in orig.glob("*.npz") if (alt / p.name).exists())
    print("| feature | part | dim | metric | warm+crop: nearest | ratio mean | worst | bright/contrast+q60: nearest | ratio mean | worst |")
    print("|---|---|---|---|---|---|---|---|---|---|")
    for name in names:
        if only and only not in name:
            continue
        ids = (orig / f"{name}.ids.txt").read_text().split()
        aids = (alt / f"{name}.ids.txt").read_text().split()
        zo, za = np.load(orig / f"{name}.npz"), np.load(alt / f"{name}.npz")
        learned = not (name.startswith("colour") or name == "composition")
        parts = list(json.loads((orig / f"{name}.json").read_text())["parts"])
        rows: list[tuple[str, np.ndarray, np.ndarray, str]] = []
        for k in parts:
            metric = "cos" if learned else ("emd" if k == "palette_kmeans" else "L2")
            rows.append((k, zo[k].astype(np.float64), za[k].astype(np.float64), metric))
        if not learned:
            # every Euclidean part, each divided by its mean pairwise distance on the sample
            keep = [r for r in rows if r[3] == "L2" and np.ptp(r[1], axis=0).max() > 1e-6]
            scale = []
            for _, O, _, _ in keep:
                d = np.linalg.norm(O[:, None] - O[None], axis=2)
                scale.append(max(d[np.triu_indices(len(O), 1)].mean(), 1e-9))
            rows.append(("ALL (parts equalised)", np.concatenate([r[1] / s for r, s in zip(keep, scale, strict=True)], axis=1),
                         np.concatenate([r[2] / s for r, s in zip(keep, scale, strict=True)], axis=1), "L2"))
        for k, O, A, metric in rows:
            if np.ptp(O, axis=0).max() < 1e-6:
                print(f"| {name} | {k} | {O.shape[1]} | {metric} | constant by construction | | | | | |")
                continue
            cells = []
            for kind in ALT_KINDS:
                ratios, first = [], 0
                for j, aid in enumerate(aids):
                    base, kd = aid.split("__")
                    if kd != kind or base not in ids:
                        continue
                    i = ids.index(base)
                    others = np.delete(_dist(O[i], O, metric), i)
                    d_alt = _dist(O[i], A[j : j + 1], metric)[0]
                    ratios.append(d_alt / max(others.min(), 1e-12))
                    first += d_alt < others.min()
                cells += [f"{first}/{len(ratios)}", f"{np.mean(ratios):.2f}", f"{np.max(ratios):.2f}"]
            print(f"| {name} | {k} | {O.shape[1]} | {metric} | " + " | ".join(cells) + " |")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cmd", choices=("make", "autocrop", "table"))
    ap.add_argument("--sample", default=str(DATA_DIR / "sample"))
    ap.add_argument("--orig")
    ap.add_argument("--alt")
    ap.add_argument("--only", default=None, help="substring filter on store names")
    a = ap.parse_args()
    if a.cmd == "make":
        make(Path(a.sample))
    elif a.cmd == "autocrop":
        autocrop_report(Path(a.sample))
    else:
        table(Path(a.orig), Path(a.alt), a.only)


if __name__ == "__main__":
    main()
