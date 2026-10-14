"""Fetch about 30 public-domain paintings from the Art Institute of Chicago for testing.

    uv run python -m features.fetch_sample            # -> data/painting2vec/sample/

Includes awkward cases on purpose: the widest and tallest paintings among the candidates and some
near-monochrome ones (grisaille / nocturne searches). Images are IIIF at 843 px wide, CC0.
"""

from __future__ import annotations

import json
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

from .store import DATA_DIR, free_disk_gb

API = "https://api.artic.edu/api/v1/artworks/search"
UA = {"User-Agent": "art2vec-painting2vec-feature-test/0.1", "AIC-User-Agent": "art2vec painting2vec feature test"}
FIELDS = "id,title,artist_title,date_end,image_id,thumbnail,is_public_domain,artwork_type_title"


def _get(url: str) -> bytes:
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60) as r:
        return r.read()


def search(q: str | None, page: int, limit: int = 100) -> list[dict]:
    body = {"query": {"bool": {"must": [{"term": {"is_public_domain": True}}, {"term": {"artwork_type_id": 1}},
                                        {"exists": {"field": "image_id"}}]}}}
    params = {"params": json.dumps(body), "fields": FIELDS, "limit": limit, "page": page}
    if q:
        params["q"] = q
    data = json.loads(_get(API + "?" + urllib.parse.urlencode(params)))
    return [d for d in data["data"] if d.get("image_id") and d.get("thumbnail") and d.get("is_public_domain")]


def main() -> None:
    out = DATA_DIR / "sample"
    out.mkdir(parents=True, exist_ok=True)
    cands = search(None, 1) + search(None, 2)
    aspect = lambda d: d["thumbnail"]["width"] / d["thumbnail"]["height"]  # noqa: E731
    by_aspect = sorted(cands, key=aspect)
    picks: dict[int, tuple[dict, str]] = {}
    for d in by_aspect[:3]:
        picks[d["id"]] = (d, "tall")
    for d in by_aspect[-3:]:
        picks[d["id"]] = (d, "wide")
    for q in ("grisaille", "nocturne grey"):
        for d in search(q, 1, 10)[:2]:
            picks.setdefault(d["id"], (d, "mono?"))
    for d in cands:
        if len(picks) >= 30:
            break
        picks.setdefault(d["id"], (d, ""))
    manifest = []
    for d, tag in picks.values():
        dest = out / f"aic{d['id']}.jpg"
        if not dest.exists():
            if free_disk_gb() < 2.0:
                sys.exit("under 2 GB free; stopping")
            url = f"https://www.artic.edu/iiif/2/{d['image_id']}/full/843,/0/default.jpg"
            try:
                dest.write_bytes(_get(url))
            except Exception as e:  # noqa: BLE001
                print("skip", d["id"], e)
                continue
            time.sleep(1.0)
        manifest.append({"id": dest.stem, "title": d["title"], "artist": d.get("artist_title"), "year": d.get("date_end"),
                         "tag": tag, "aspect": round(aspect(d), 3), "source": f"https://www.artic.edu/artworks/{d['id']}",
                         "licence": "CC0 (AIC public domain)"})
        print(dest.name, tag, d["title"][:60])
    (out / "manifest.json").write_text(json.dumps(manifest, indent=1) + "\n")
    print(len(manifest), "images in", out)


if __name__ == "__main__":
    main()
