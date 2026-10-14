"""Single entry point.

    cd experiments/painting2vec
    uv run python -m features.run --images <dir> --out <dir> --blocks colour,composition,dinov2_b

See README.md in this directory for every option and for what each output file contains.
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

from . import colour, composition
from .preprocess import AUTOCROP, VIEWS, list_images, load_image, model_views, stats_array
from .store import Store, free_disk_gb, swap_used_mb, wait_for_memory

MODEL_NAMES = ("dinov2_b", "dinov2_l", "siglip2_b", "clip_l", "csd_l")
BLOCKS = ("colour", "composition", *MODEL_NAMES)


def _log_error(out: Path, block: str, path: Path, e: Exception) -> None:
    with open(out / "errors.txt", "a") as f:
        f.write(f"{block}\t{path.name}\t{type(e).__name__}: {e}\n")
    print(f"  ! {path.name}: {type(e).__name__}: {e}", flush=True)


def run_direct(args, paths: list[Path], do_colour: bool, do_comp: bool) -> None:
    out = Path(args.out)
    norms = args.colour_norms.split(",") if do_colour else []
    stores = {f"colour__{n}": Store(out, f"colour__{n}") for n in norms}
    if do_comp:
        stores["composition"] = Store(out, "composition")
    for s in stores.values():
        s.meta.update(autocrop=args.autocrop, stats_budget=args.stats_budget)
    t0, n = time.time(), 0
    for p in paths:
        todo = [k for k, s in stores.items() if p.stem not in s.done]
        if not todo:
            continue
        try:
            rgb = stats_array(load_image(p, args.autocrop), args.stats_budget)
            for k in todo:
                if k == "composition":
                    stores[k].add(p.stem, composition.composition_features(rgb))
                else:
                    stores[k].add(p.stem, colour.colour_features(rgb, k.split("__")[1]))
        except Exception as e:  # noqa: BLE001 - one bad file must not stop a 2,500-image run
            _log_error(out, "direct", p, e)
        n += 1
    for k, s in stores.items():
        if n:
            s.meta["seconds_per_image_all_direct_blocks"] = round((time.time() - t0) / n, 4)
        s.flush()
        print(f"{k}: {len(s.ids)} images -> {s.npz}", flush=True)


def run_model(args, paths: list[Path], name: str) -> None:
    from . import embed  # imports torch; also points the HF caches at data/painting2vec/models

    spec = embed.MODELS[name]
    views = args.views.split(",") if args.views else [spec.default_view]
    for v in views:
        if v not in spec.views:
            raise SystemExit(f"{name} does not support view {v!r} (has {spec.views})")
    out = Path(args.out)
    stores = {v: Store(out, f"{name}__{v}", dtype="float16") for v in views}
    if all(p.stem in s.done for p in paths for s in stores.values()) and not args.force_load:
        print(f"{name}: nothing to do", flush=True)
        if args.cleanup_weights:
            embed.remove_weights(spec)
        return
    pct = wait_for_memory(args.min_free_mem_pct)
    swap0 = swap_used_mb()
    print(f"{name}: free memory {pct}%, free disk {free_disk_gb():.2f} GB, device {embed.pick_device(args.device)}", flush=True)
    t_load = time.time()
    em = embed.Embedder(name, args.device, fp16=args.fp16, csd_allow_listed_globals=args.csd_allow_listed_globals)
    t_load = time.time() - t_load
    size = args.size or spec.size
    mean, std = spec.mean_std
    secs = {v: [] for v in views}
    try:
        for i, p in enumerate(paths):
            todo = [v for v in views if p.stem not in stores[v].done]
            if not todo:
                continue
            try:
                img = load_image(p, args.autocrop)
                for v in todo:
                    t = time.time()
                    px, mask = model_views(img, size, v, mean, std, spec.patch)
                    parts = em.embed(px, mask)  # one painting per pass: 1 view, or up to 5 tiles
                    stores[v].add(p.stem, parts)
                    secs[v].append(time.time() - t)
            except Exception as e:  # noqa: BLE001
                _log_error(out, name, p, e)
            if (i + 1) % 100 == 0:
                print(f"  {name}: {i + 1}/{len(paths)}  {em.memory_mb()}", flush=True)
            if i == 2 or (i + 1) % 20 == 0:
                sw = swap_used_mb()
                if swap0 is not None and sw is not None and sw - swap0 > args.max_swap_growth_mb:
                    raise SystemExit(f"{name}: system swap grew by {sw - swap0:.0f} MB during the run; stopping (a rerun resumes)")
    finally:
        mem = em.memory_mb()
        sw = swap_used_mb()
        if swap0 is not None and sw is not None:
            mem["system_swap_change_mb"] = round(sw - swap0, 1)  # whole machine, not just this process
        for v, s in stores.items():
            s.meta.update(model=name, repo=spec.repo, licence=spec.licence, view=v, input_size=size,
                          autocrop=args.autocrop, device=em.device, fp16=args.fp16, load_seconds=round(t_load, 1), **mem)
            if len(secs[v]) > 1:
                s.meta["seconds_per_image"] = round(sum(secs[v][1:]) / len(secs[v][1:]), 4)  # first call warms up
            s.flush()
            print(f"{name}__{v}: {len(s.ids)} images -> {s.npz}  {s.meta.get('seconds_per_image')} s/img  {mem}", flush=True)
        em.close()
        if args.cleanup_weights:
            embed.remove_weights(spec)
            print(f"{name}: weights removed; free disk {free_disk_gb():.2f} GB", flush=True)


def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser(prog="features.run", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--images", required=True, help="directory of images; the file stem is the id")
    ap.add_argument("--out", required=True, help="output directory (put it under data/painting2vec/features/)")
    ap.add_argument("--blocks", required=True, help="comma list from: " + ", ".join(BLOCKS))
    ap.add_argument("--autocrop", default="none", choices=AUTOCROP, help="trim flat borders / frames first (default none)")
    ap.add_argument("--views", default=None, help=f"comma list from {VIEWS}; how a painting becomes ViT input. Default: each model's own default")
    ap.add_argument("--size", type=int, default=None, help="ViT input side in pixels (default 224; DINOv2 also takes 448 etc.)")
    ap.add_argument("--colour-norms", default=",".join(colour.NORMS), help="colour normalisations to write (default: all)")
    ap.add_argument("--stats-budget", type=int, default=256 * 256, help="pixel budget of the statistics image")
    ap.add_argument("--device", default="auto", choices=("auto", "mps", "cpu"))
    ap.add_argument("--fp16", action="store_true", help="half precision on MPS (halves model memory)")
    ap.add_argument("--cleanup-weights", action="store_true", help="delete each model's weights when it finishes")
    ap.add_argument("--min-free-mem-pct", type=int, default=25, help="wait until this much system memory is free before loading a model")
    ap.add_argument("--max-swap-growth-mb", type=float, default=1024, help="stop a model run if swap grows by more than this")
    ap.add_argument("--csd-allow-listed-globals", action="store_true",
                    help="csd_l only: allow the four named non-tensor types its pickle needs (still weights_only=True); see README")
    ap.add_argument("--limit", type=int, default=None, help="only the first N images (sorted by name)")
    ap.add_argument("--force-load", action="store_true", help=argparse.SUPPRESS)
    args = ap.parse_args(argv)

    blocks = [b for b in args.blocks.split(",") if b]
    bad = [b for b in blocks if b not in BLOCKS]
    if bad:
        raise SystemExit(f"unknown blocks {bad}; choose from {BLOCKS}")
    paths = list_images(args.images)[: args.limit]
    if not paths:
        raise SystemExit(f"no images in {args.images}")
    stems = [p.stem for p in paths]
    if len(set(stems)) != len(stems):
        raise SystemExit("two images share a file stem; ids would collide")
    Path(args.out).mkdir(parents=True, exist_ok=True)
    print(f"{len(paths)} images; blocks {blocks}", flush=True)
    if "colour" in blocks or "composition" in blocks:
        run_direct(args, paths, "colour" in blocks, "composition" in blocks)
    for name in MODEL_NAMES:  # strictly one model at a time
        if name in blocks:
            run_model(args, paths, name)


if __name__ == "__main__":
    main(sys.argv[1:])
