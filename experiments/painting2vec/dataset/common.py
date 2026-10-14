"""Shared helpers for the painting2vec pilot dataset scripts.

Run every script from the repository root, one at a time:
    uv run --no-project --with requests --with pillow --with pandas python experiments/painting2vec/dataset/<script>.py
"""
from __future__ import annotations

import io
import json
import shutil
import time
from pathlib import Path

import requests
from PIL import Image

UA = "art2vec-research/0.1 (https://github.com/sameraslan/recmyrecord)"
ROOT = Path(__file__).resolve().parents[3]
DATA = ROOT / "data" / "painting2vec"
CACHE = DATA / "cache"
HERE = Path(__file__).resolve().parent
SPARQL = "https://query.wikidata.org/sparql"
WD_API = "https://www.wikidata.org/w/api.php"
COMMONS_API = "https://commons.wikimedia.org/w/api.php"
LONG_SIDE = 1024
JPEG_QUALITY = 90
MIN_FREE_BYTES = int(1.5 * 1024**3)
# Decompression-bomb guard: refuse anything above 60 megapixels (we only fetch thumbnails).
Image.MAX_IMAGE_PIXELS = 60_000_000

S = requests.Session()
S.headers["User-Agent"] = UA


def free_bytes() -> int:
    return shutil.disk_usage(ROOT).free


def check_disk() -> None:
    if free_bytes() < MIN_FREE_BYTES:
        raise SystemExit(f"STOP: free disk {free_bytes()/1e9:.2f} GB is under the 1.5 GB floor")


def get(url, params=None, tries=8, timeout=70, pause=0.0, headers=None, stream=False, net_wait=3600):
    """GET with exponential backoff. Returns a Response, or None after giving up.

    Connection/DNS/timeout errors are an outage on our side, not an answer from the server, so they
    do not use up `tries`: the call keeps waiting (back-off capped at 2 min) for up to `net_wait`
    seconds in total before giving up. 429/5xx responses back off and count against `tries`.
    """
    delay, net_delay, waited, n = 2.0, 5.0, 0.0, 0
    while n < tries:
        try:
            r = S.get(url, params=params, timeout=timeout, headers=headers, stream=stream)
            if not stream:
                r.content  # pull the body inside the try so a dropped transfer is retried too
        except requests.RequestException as e:
            if waited >= net_wait:
                print(f"  giving up after {waited:.0f}s offline: {url[:90]}", flush=True)
                return None
            print(f"  net error {type(e).__name__} on {url[:90]}; sleep {net_delay:.0f}s", flush=True)
            time.sleep(net_delay)
            waited += net_delay
            net_delay = min(net_delay * 2, 120)
            continue
        net_delay = 5.0
        if r.status_code == 200:
            if pause:
                time.sleep(pause)
            return r
        if r.status_code in (429, 500, 502, 503, 504):
            n += 1
            ra = r.headers.get("Retry-After")
            wait = float(ra) if ra and ra.isdigit() else delay
            print(f"  HTTP {r.status_code} on {url[:90]}; sleep {wait:.0f}s", flush=True)
            time.sleep(min(wait, 180))
            delay = min(delay * 2, 120)
            continue
        return r  # 403/404 etc: caller decides
    return None


def sparql(query: str, tries=4):
    r = get(SPARQL, params={"query": query, "format": "json"}, tries=tries, timeout=75, pause=1.0)
    if r is None or r.status_code != 200:
        raise RuntimeError(f"SPARQL failed: {r.status_code if r is not None else 'no response'}")
    return r.json()["results"]["bindings"]


def qid(uri: str) -> str:
    return uri.rsplit("/", 1)[-1]


def load_json(path: Path, default=None):
    if path.exists():
        return json.loads(path.read_text())
    return default


def save_json(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(obj, ensure_ascii=False))
    tmp.replace(path)


def decode_and_save(raw: bytes, dest: Path, long_side: int = LONG_SIDE):
    """Treat `raw` as untrusted: decode with Pillow only, verify, downscale, re-encode as JPEG.

    Returns (width, height) of the stored file, or None if the bytes do not decode.
    One image at a time; everything is closed before returning.
    """
    try:
        with Image.open(io.BytesIO(raw)) as probe:
            probe.verify()
        with Image.open(io.BytesIO(raw)) as im:
            im.draft("RGB", (long_side * 2, long_side * 2))
            im = im.convert("RGB")
            if max(im.size) > long_side:
                im.thumbnail((long_side, long_side), Image.LANCZOS)
            dest.parent.mkdir(parents=True, exist_ok=True)
            tmp = dest.with_suffix(".part")
            im.save(tmp, "JPEG", quality=JPEG_QUALITY, optimize=True)
            size = im.size
        tmp.replace(dest)
        return size
    except Exception as e:  # noqa: BLE001 - any decode failure means discard
        print(f"  decode failed for {dest.name}: {type(e).__name__}: {e}", flush=True)
        return None


def lab_thumb(path: Path):
    """64x64 CIELAB thumbnail (D65) as a float array, aspect ratio ignored."""
    import numpy as np

    with Image.open(path) as im:
        im = im.convert("RGB").resize((64, 64), Image.BOX)
        a = np.asarray(im, dtype=np.float64) / 255.0
    a = np.where(a > 0.04045, ((a + 0.055) / 1.055) ** 2.4, a / 12.92)
    m = np.array([[0.4124564, 0.3575761, 0.1804375],
                  [0.2126729, 0.7151522, 0.0721750],
                  [0.0193339, 0.1191920, 0.9503041]])
    xyz = a @ m.T / np.array([0.95047, 1.0, 1.08883])
    f = np.where(xyz > 0.008856, np.cbrt(xyz), 7.787 * xyz + 16 / 116)
    return np.stack([116 * f[..., 1] - 16, 500 * (f[..., 0] - f[..., 1]), 200 * (f[..., 1] - f[..., 2])], -1)


def lab_diff(a: Path, b: Path) -> float:
    """Mean absolute difference of the two 64x64 LAB thumbnails (L 0..100 units)."""
    import numpy as np

    return float(np.abs(lab_thumb(a) - lab_thumb(b)).mean())


def link_or_copy(src: Path, dest: Path) -> None:
    """Hard-link (no extra disk) with a copy as fallback."""
    import os

    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists():
        return
    try:
        os.link(src, dest)
    except OSError:
        shutil.copyfile(src, dest)
