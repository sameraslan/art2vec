"""Commons imageinfo lookups (50 titles per call, cached) and one-at-a-time thumbnail downloads."""
from __future__ import annotations

import re
import time
from pathlib import Path

from common import CACHE, COMMONS_API, LONG_SIDE, check_disk, decode_and_save, get, load_json, save_json

ICACHE = CACHE / "commons_info.json"
STEPS = (500, 960, 1280, 1920)  # Wikimedia's standard thumbnail widths
OPEN = re.compile(r"^(public domain|cc0|cc-pd-mark|pd[- ]?art|pdm|no restrictions)", re.I)
META = "LicenseShortName|License|UsageTerms|Copyrighted|Credit|Artist|Permission|ImageDescription"


def _txt(v, n=240):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", str(v or ""))).strip()[:n]


def _parse(page):
    ii = (page.get("imageinfo") or [None])[0]
    if not ii:
        return None
    em = {k: _txt(v.get("value")) for k, v in (ii.get("extmetadata") or {}).items()}
    return {"title": page["title"][5:], "url": ii.get("url"), "thumburl": ii.get("thumburl"),
            "w": ii.get("width"), "h": ii.get("height"), "sha1": ii.get("sha1"), "user": ii.get("user"),
            "mime": ii.get("mime"), "descurl": ii.get("descriptionurl"),
            "licence": em.get("LicenseShortName", ""),
            "licence_detail": " | ".join(f"{k}={em[k]}" for k in ("License", "UsageTerms", "Copyrighted") if em.get(k)),
            "credit": em.get("Credit", ""), "artist": em.get("Artist", ""), "desc": em.get("ImageDescription", "")}


def _query(names, width=None):
    params = {"action": "query", "prop": "imageinfo", "iiprop": "url|size|sha1|user|mime|extmetadata",
              "iiextmetadatafilter": META, "titles": "|".join("File:" + n for n in names),
              "redirects": 1, "format": "json", "formatversion": 2}
    if width:
        params["iiurlwidth"] = width
    r = get(COMMONS_API, params=params, pause=0.3)
    js = r.json() if r is not None else {}
    q = js.get("query")
    if q is None:
        print("  commons: bad response", str(js)[:200], flush=True)
        time.sleep(6)
        return {}
    fwd = {}
    for m in q.get("normalized", []) + q.get("redirects", []):
        fwd[m["from"]] = m["to"]
    pages = {p["title"]: p for p in q.get("pages", [])}
    out = {}
    for n in names:
        t = "File:" + n
        for _ in range(3):
            t = fwd.get(t, t)
        out[n] = _parse(pages[t]) if t in pages else None
    return out


def step_for(w, h):
    need = LONG_SIDE * w / max(w, h)
    return next((s for s in STEPS if s >= need), STEPS[-1])


def info(names):
    """{file name as given: record or None}. Records carry a thumbnail URL whose long side is >= 1024 px
    (or the original's URL when the original is no wider than the chosen step)."""
    cache = load_json(ICACHE, {})
    todo = [n for n in dict.fromkeys(names) if n not in cache]
    for i in range(0, len(todo), 50):
        got = _query(todo[i:i + 50])
        by_step = {}
        for n, rec in got.items():
            if rec and rec["w"] and rec["h"]:
                by_step.setdefault(step_for(rec["w"], rec["h"]), []).append(n)
        for step, ns in by_step.items():
            th = _query(ns, step)
            for n in ns:
                if th.get(n) and th[n].get("thumburl"):
                    got[n]["thumburl"] = th[n]["thumburl"]
        cache.update(got)
        save_json(ICACHE, cache)
        print(f"  commons info: {i + len(got)}/{len(todo)}", flush=True)
    return {n: cache.get(n) for n in names}


def is_open(rec) -> bool:
    return bool(rec and OPEN.match(rec["licence"] or ""))


def fetch_image(url: str, dest: Path, pause=0.5, headers=None, net_wait=3600):
    """Download one image into memory, decode-check with Pillow, store as <=1024 px JPEG. Resumable."""
    if dest.exists():
        return "exists"
    check_disk()
    r = get(url, timeout=90, pause=pause, headers=headers, net_wait=net_wait)
    if r is None or r.status_code != 200:
        return f"http_{r.status_code if r is not None else 'fail'}"
    if len(r.content) > 40_000_000:
        return "too_big"
    return "ok" if decode_and_save(r.content, dest) else "undecodable"
