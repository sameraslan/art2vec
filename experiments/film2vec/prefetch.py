"""Download catalog videos ahead of extract.py, a few at a time.

The Internet Archive serves about 1 MB/s per connection, so downloading is the
slow half of a run. This fetches into a staging folder and moves each finished
file to where extract.py looks for it; extract.py then finds the video already
there. Network only: no models, no decoding.
"""

from __future__ import annotations

import argparse
import csv
import shutil
import subprocess
import time
import urllib.parse
from concurrent.futures import ThreadPoolExecutor

from extract import cache_home, feat_dir, log_line, video_dir

STAGES = ("cuts", "look", "time", "sound", "words", "motion")


def staged_bytes() -> int:
    root = cache_home() / "artefacts" / "film"
    return sum(p.stat().st_size for p in root.rglob("*") if p.is_file()) if root.exists() else 0


def wanted(row: dict, stages: list[str]) -> bool:
    silent = row["silent_or_sound"] == "silent"
    need = [s for s in stages if not (silent and s in ("sound", "words"))]
    return not all((feat_dir(row["id"]) / f"{s}.json").exists() for s in need)


def fetch(row: dict, max_gb: float) -> None:
    dest = video_dir(row["id"]) / row["ia_file"].split("/")[-1]
    stage = cache_home() / "artefacts" / "film" / "_prefetch"
    stage.mkdir(parents=True, exist_ok=True)
    tmp = stage / f"{row['id']}.tmp"
    while staged_bytes() / 1e9 > max_gb or shutil.disk_usage(stage).free / 1e9 < 12:
        time.sleep(60)
    if dest.exists() or dest.with_name(dest.name + ".part").exists():
        return
    url = f"https://archive.org/download/{row['ia_identifier']}/{urllib.parse.quote(row['ia_file'])}"
    t0 = time.time()
    r = subprocess.run(
        ["curl", "-L", "--fail", "-sS", "-C", "-", "--retry", "5", "--retry-delay", "15",
         "--connect-timeout", "30", "-o", str(tmp), url],
        capture_output=True, text=True,
    )  # fmt: skip
    if r.returncode != 0:
        log_line(row["id"], "prefetch", "FAIL", r.stderr.strip()[-200:])
        return
    if dest.exists() or dest.with_name(dest.name + ".part").exists():
        tmp.unlink()  # extract.py got there first
        return
    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp.replace(dest)
    log_line(row["id"], "prefetch", "ok", f"{time.time() - t0:.0f}s", f"{dest.stat().st_size / 1e6:.0f}MB")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--catalog", default="catalog.csv")
    ap.add_argument("--only", default="")
    ap.add_argument("--stages", default="cuts,look,time,sound,words")
    ap.add_argument("--jobs", type=int, default=3)
    ap.add_argument("--max-gb", type=float, default=12.0, help="pause while this much video is waiting")
    args = ap.parse_args()
    only = {s for s in args.only.split(",") if s}
    rows = [r for r in csv.DictReader(open(args.catalog)) if not only or r["id"] in only]
    rows = [r for r in rows if wanted(r, args.stages.split(","))]
    with ThreadPoolExecutor(args.jobs) as pool:
        list(pool.map(lambda r: fetch(r, args.max_gb), rows))


if __name__ == "__main__":
    main()
