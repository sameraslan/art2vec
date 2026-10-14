"""film2vec experiments: eight small frames per catalog film, for the contact sheets.

Throwaway experiment code. The film is not downloaded: ffmpeg is given the Internet Archive URL with -ss before
-i, so it seeks by HTTP range request and reads only the index and the stretch around each frame.

    thumbs.py [--catalog catalog.csv] [--only id1,id2,...] [--limit N] [--timeout 120] [--force]

Writes  <home>/experiments/film2vec/thumbs/<id>/00.jpg .. 07.jpg   (height 180, JPEG -q:v 5) and times.json
        <home>/experiments/film2vec/thumbs.log                      one line per failure
Frames of public-domain films; they stay in the cache and never go in the repository.
Serial and resumable: a frame that exists is not fetched again; a frame that fails is logged and skipped.
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import json
import os
import shutil
import subprocess
import time
import urllib.parse
from pathlib import Path

HERE = Path(__file__).resolve().parent
FFMPEG = shutil.which("ffmpeg") or "/usr/local/bin/ffmpeg"
FFPROBE = shutil.which("ffprobe") or "/usr/local/bin/ffprobe"
N_FRAMES = 8
FIRST, LAST = 0.10, 0.90
HEIGHT = 180
JPEG_Q = 5
MIN_BYTES = 600  # smaller than this is not a picture


def cache_home() -> Path:
    env = os.environ.get("ART2VEC_HOME")
    return Path(env).expanduser() if env else Path.home() / "Library" / "Caches" / "art2vec"


def thumbs_dir() -> Path:
    return cache_home() / "experiments" / "film2vec" / "thumbs"


def log(*fields: object) -> None:
    line = "\t".join([dt.datetime.now().isoformat(timespec="seconds"), *[str(f) for f in fields]])
    print(line, flush=True)
    path = thumbs_dir().parent / "thumbs.log"
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a") as fh:
        fh.write(line + "\n")


def ia_url(row: dict) -> str:
    ident, name = row["ia_identifier"].strip(), row["ia_file"].strip()
    return f"https://archive.org/download/{urllib.parse.quote(ident)}/{urllib.parse.quote(name)}"


def remote_duration(url: str, timeout: float) -> float | None:
    try:
        r = subprocess.run(
            [FFPROBE, "-v", "error", "-rw_timeout", str(int(timeout * 1e6)), "-show_entries", "format=duration",
             "-of", "default=nw=1:nk=1", url],
            capture_output=True, text=True, timeout=timeout,
        )  # fmt: skip
        return float(r.stdout.strip())
    except (subprocess.TimeoutExpired, ValueError):
        return None


def grab(url: str, t: float, dest: Path, timeout: float) -> str:
    """One frame at t seconds. Returns '' on success, else a short reason."""
    tmp = dest.with_name(dest.stem + ".part.jpg")
    cmd = [FFMPEG, "-v", "error", "-nostdin", "-y", "-rw_timeout", str(int(timeout * 1e6)),
           "-ss", f"{t:.2f}", "-i", url, "-map", "0:v:0", "-an", "-sn", "-frames:v", "1",
           "-vf", f"scale=-2:{HEIGHT}", "-q:v", str(JPEG_Q), "-f", "image2", str(tmp)]  # fmt: skip
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        tmp.unlink(missing_ok=True)
        return f"timed out after {timeout:.0f} s"
    if r.returncode != 0 or not tmp.exists() or tmp.stat().st_size < MIN_BYTES:
        tmp.unlink(missing_ok=True)
        last = r.stderr.strip().splitlines()[-1] if r.stderr.strip() else "no frame written"
        return f"exit {r.returncode}: {last}"[:300]
    os.replace(tmp, dest)
    return ""


def film_thumbs(row: dict, timeout: float, force: bool) -> tuple[int, int]:
    """Returns (frames present afterwards, frames fetched now)."""
    fid = row["id"].strip()
    out = thumbs_dir() / fid
    paths = [out / f"{i:02d}.jpg" for i in range(N_FRAMES)]
    if not force and all(p.exists() and p.stat().st_size >= MIN_BYTES for p in paths):
        return N_FRAMES, 0
    if not row.get("ia_identifier", "").strip() or not row.get("ia_file", "").strip():
        log(fid, "FAIL", "row lacks ia_identifier or ia_file")
        return 0, 0
    url = ia_url(row)
    try:
        duration = float(row.get("ia_file_seconds") or 0)
    except ValueError:
        duration = 0.0
    source = "catalog ia_file_seconds"
    if duration <= 0:
        duration, source = remote_duration(url, timeout) or 0.0, "ffprobe on the URL"
    if duration <= 0:
        log(fid, "FAIL", "no running time in the catalog and ffprobe could not read one")
        return 0, 0
    out.mkdir(parents=True, exist_ok=True)
    times = [duration * (FIRST + (LAST - FIRST) * i / (N_FRAMES - 1)) for i in range(N_FRAMES)]
    fetched = 0
    for i, (t, p) in enumerate(zip(times, paths, strict=True)):
        if not force and p.exists() and p.stat().st_size >= MIN_BYTES:
            continue
        err = grab(url, t, p, timeout)
        if err:
            log(fid, "FAIL", f"frame {i:02d} at {t:.1f}s", err)
        else:
            fetched += 1
    (out / "times.json").write_text(json.dumps({"id": fid, "title": row.get("title"), "url": url,
                                                "duration_s": duration, "duration_source": source,
                                                "times_s": [round(t, 2) for t in times]}, indent=1))  # fmt: skip
    return sum(p.exists() for p in paths), fetched


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--catalog", default=str(HERE / "catalog.csv"))
    ap.add_argument("--only", help="comma list of ids")
    ap.add_argument("--limit", type=int, help="first N films")
    ap.add_argument("--timeout", type=float, default=120.0, help="seconds per frame")
    ap.add_argument("--force", action="store_true", help="fetch frames again even if they exist")
    args = ap.parse_args()

    with open(args.catalog, newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    if args.only:
        only = [x.strip() for x in args.only.split(",") if x.strip()]
        by_id = {r["id"].strip(): r for r in rows}
        for missing in [i for i in only if i not in by_id]:
            log(missing, "FAIL", "id not in the catalog")
        rows = [by_id[i] for i in only if i in by_id]
    if args.limit:
        rows = rows[: args.limit]
    complete = 0
    for n, row in enumerate(rows, 1):
        t0 = time.time()
        try:
            have, fetched = film_thumbs(row, args.timeout, args.force)
        except Exception as e:  # one bad film must not stop the run
            log(row.get("id", "?"), "FAIL", repr(e)[:300])
            continue
        complete += have == N_FRAMES
        print(f"[{n}/{len(rows)}] {row['id']} {row.get('title', '')}: {have}/{N_FRAMES} frames "
              f"({fetched} fetched, {time.time() - t0:.0f} s)", flush=True)  # fmt: skip
    print(f"{complete}/{len(rows)} films with all {N_FRAMES} frames in {thumbs_dir()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
