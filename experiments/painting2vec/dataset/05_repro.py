"""Step 5: reproduction pairs. A second, independent photograph of paintings already in the pilot set.

Second sources, in order of preference:
  met / aic / cleveland / nga / rijksmuseum  the holding museum's own open-access image, via its API,
      only where the museum's record flags the image public domain / CC0 / open access;
  commons2, commons3  another file in the painting's Commons category (P373) that is PD/CC0, has a
      different uploader AND a different source/credit line from the P18 file, and the same aspect
      ratio to within 5 % (which rejects details and framed shots).
Every candidate is compared with the pilot image by mean absolute difference of 64x64 CIELAB
thumbnails. Candidates under NEAR_IDENTICAL are the same file re-encoded and are deleted; Commons
candidates over COMMONS_MAX are rejected as probably not the same picture (engraving, detail, B/W).
Everything is cached in cache/repro_candidates.json, so reruns only fetch what is missing.
"""
import csv
import math
import re
import sys
from collections import Counter

import pandas as pd

from common import CACHE, COMMONS_API, DATA, HERE, UA, check_disk, get, lab_diff, lab_thumb, link_or_copy, load_json, save_json
from commons import fetch_image, info, is_open
from wd import fetch_paintings

REPRO = DATA / "repro"
PILOT = DATA / "pilot"
STATE = CACHE / "repro_candidates.json"
NEAR_IDENTICAL = 1.0   # LAB units; below this the two files are one photograph re-encoded
COMMONS_MAX = 22.0     # above this a Commons-category candidate is not trusted to be the same picture
COMMONS_LOOKUPS = 160  # how many pilot paintings (most-linked first) to search for a second Commons file
RIJKS_QID = "Q190804"


def met(i):
    r = get(f"https://collectionapi.metmuseum.org/public/collection/v1/objects/{i}", pause=0.4, tries=3)
    if r is None or r.status_code != 200:
        return None
    d = r.json()
    # web-large is only ~600 px, so take the original; it is decoded in JPEG draft mode (reduced-size
    # decode) and never held at full size.
    return (d["primaryImage"], "isPublicDomain=true") if d.get("isPublicDomain") and d.get("primaryImage") else None


def aic(i):
    r = get(f"https://api.artic.edu/api/v1/artworks/{i}", params={"fields": "id,image_id,is_public_domain"}, pause=0.4, tries=3)
    if r is None or r.status_code != 200:
        return None
    d = r.json().get("data") or {}
    if d.get("is_public_domain") and d.get("image_id"):
        return f"https://www.artic.edu/iiif/2/{d['image_id']}/full/!1024,1024/0/default.jpg", "is_public_domain=true"
    return None


def cleveland(i):
    r = get(f"https://openaccess-api.clevelandart.org/api/artworks/{i}", pause=0.4, tries=3)
    if r is None or r.status_code != 200:
        return None
    d = r.json().get("data") or {}
    web = (d.get("images") or {}).get("web") or {}
    return (web["url"], "share_license_status=CC0") if d.get("share_license_status") == "CC0" and web.get("url") else None


_nga = None


def nga(i):
    """NGA publishes its image table as one 89 MB CSV; stream it once and keep only the rows we need."""
    global _nga
    if _nga is None:
        path = CACHE / "nga_images.json"
        _nga = load_json(path)
        if _nga is None:
            want = set(NGA_WANT)
            _nga = {}
            r = get("https://raw.githubusercontent.com/NationalGalleryOfArt/opendata/main/data/published_images.csv",
                    stream=True, timeout=120)
            lines = (ln.decode("utf-8", "replace") for ln in r.iter_lines())
            for row in csv.DictReader(lines):
                k = row.get("depictstmsobjectid")
                if k in want and row.get("viewtype") == "primary" and row.get("openaccess") == "1" and k not in _nga:
                    _nga[k] = row["iiifurl"]
            save_json(path, _nga)
    u = _nga.get(str(i))
    return (u + "/full/!1024,1024/0/default.jpg", "openaccess=1") if u else None


def rijks(ref):
    """ref is an object number (SK-A-...). Walk the museum's Linked Art records to the IIIF image."""
    hdr = {"Accept": "application/ld+json"}
    r = get("https://data.rijksmuseum.nl/search/collection", params={"objectNumber": ref}, pause=0.4, tries=3)
    items = r.json().get("orderedItems") if r is not None and r.status_code == 200 else None
    if not items:
        return None
    r = get(items[0]["id"], headers=hdr, pause=0.4, tries=3)          # the object
    shows = r.json().get("shows") if r is not None and r.status_code == 200 else None
    if not shows:
        return None
    r = get(shows[0]["id"], headers=hdr, pause=0.4, tries=3)          # its visual item: rights live here
    if r is None or r.status_code != 200:
        return None
    vis = r.json()
    rights = " ".join(x.get("id", "") for s in vis.get("subject_to", []) for x in s.get("classified_as", []))
    dig = vis.get("digitally_shown_by")
    if "creativecommons.org/publicdomain" not in rights or not dig:
        return None
    r = get(dig[0]["id"], headers=hdr, pause=0.4, tries=3)            # the digital object: IIIF access point
    if r is None or r.status_code != 200:
        return None
    ap = (r.json().get("access_point") or [{}])[0].get("id", "")
    m = re.match(r"(https://iiif\.micr\.io/[^/]+)/", ap)
    return (m.group(1) + "/full/!1024,1024/0/default.jpg", "rights=" + rights.strip()) if m else None


NGA_WANT = []
MUSEUMS = [("met", "met_id", met), ("aic", "aic_id", aic), ("cleveland", "cleveland_id", cleveland), ("nga", "nga_id", nga)]


def chroma(path):
    """Mean CIELAB chroma of the 64x64 thumbnail; near zero for a black-and-white reproduction."""
    import numpy as np

    t = lab_thumb(path)
    return round(float(np.hypot(t[..., 1], t[..., 2]).mean()), 2)


def norm(s):
    return re.sub(r"[^a-z0-9]+", " ", (s or "").lower()).strip()


def commons_second(q, p, primary):
    """Up to two other PD files of the same painting from its Commons category."""
    if not p["P373"]:
        return []
    r = get(COMMONS_API, params={"action": "query", "list": "categorymembers", "cmtitle": "Category:" + p["P373"][0],
                                 "cmtype": "file", "cmlimit": 40, "format": "json", "formatversion": 2}, pause=0.3)
    names = [m["title"][5:] for m in (r.json().get("query", {}).get("categorymembers", []) if r is not None else [])]
    names = [n for n in names if n.lower().endswith((".jpg", ".jpeg", ".png", ".tif", ".tiff")) and n != primary["title"]]
    recs = info(names)
    asp = primary["w"] / primary["h"]
    out, seen = [], {(primary["user"], norm(primary["credit"]))}
    for n, rec in sorted(recs.items(), key=lambda kv: -((kv[1] or {}).get("w") or 0) * ((kv[1] or {}).get("h") or 0)):
        if not rec or not rec.get("thumburl") or not is_open(rec) or rec["sha1"] == primary["sha1"]:
            continue
        if max(rec["w"], rec["h"]) < 1000 or abs(math.log((rec["w"] / rec["h"]) / asp)) > 0.05:
            continue
        if rec["user"] == primary["user"] or norm(rec["credit"]) == norm(primary["credit"]):
            continue
        if any(rec["user"] == u or norm(rec["credit"]) == c for u, c in seen):
            continue
        seen.add((rec["user"], norm(rec["credit"])))
        out.append(rec)
        if len(out) == 2:
            break
    return out


def main():
    meta = pd.read_csv(PILOT / "meta.csv", dtype=str).fillna("")
    meta["sl"] = meta["sitelinks"].astype(int)
    P = fetch_paintings(list(meta["qid"]))
    state = load_json(STATE, {})   # key "<qid>__<source>" -> {status, url, note, lab_diff, ...}
    if "--retry-failed" in sys.argv:  # forget everything that did not end in a stored image, and try it again
        state = {k: v for k, v in state.items() if v["status"] in ("ok", "searched")}
    NGA_WANT.extend(x for x in meta["nga_id"] if x)
    REPRO.mkdir(parents=True, exist_ok=True)

    def consider(q, source, url, note, extra=None):
        key = f"{q}__{source}"
        a = PILOT / "images" / f"{q}.jpg"
        dest = REPRO / f"{key}.jpg"
        hdr = {"AIC-User-Agent": UA} if source == "aic" else None  # AIC's IIIF server refuses requests without it
        # a museum image server that keeps timing out is given 4 minutes, not the hour a Commons outage gets
        st = fetch_image(url, dest, pause=0.5, headers=hdr, net_wait=3600 if source.startswith("commons") else 240)
        rec = {"status": st, "url": url, "note": note, **(extra or {})}
        if dest.exists():
            rec["lab_diff"] = round(lab_diff(a, dest), 3)
            rec["status"] = "ok"
        state[key] = rec
        save_json(STATE, state)

    # 1. museum APIs
    for source, col, fn in MUSEUMS:
        rows = meta[meta[col] != ""]
        print(f"{source}: {len(rows)} pilot paintings carry an id", flush=True)
        for q, i in zip(rows["qid"], rows[col]):
            key = f"{q}__{source}"
            if key in state:
                continue
            check_disk()
            got = fn(i)
            if not got:
                state[key] = {"status": "no_open_image", "id": i}
                save_json(STATE, state)
                continue
            consider(q, source, got[0], got[1], {"id": i})
    rj = meta[meta["collection_qid"].str.contains(RIJKS_QID) & meta["inventory_number"].str.contains("SK-")]
    print(f"rijksmuseum: {len(rj)} pilot paintings with an SK- inventory number", flush=True)
    for q, inv in zip(rj["qid"], rj["inventory_number"]):
        key = f"{q}__rijksmuseum"
        if key in state:
            continue
        ref = next(x for x in inv.split("|") if x.startswith("SK-"))
        got = rijks(ref)
        if not got:
            state[key] = {"status": "no_open_image", "id": ref}
            save_json(STATE, state)
            continue
        consider(q, "rijksmuseum", got[0], got[1], {"id": ref})

    cl = meta[meta["collection_name"].str.contains("Cleveland Museum of Art") & (meta["inventory_number"] != "")]
    print(f"cleveland (by accession number): {len(cl)} pilot paintings", flush=True)
    for q, inv in zip(cl["qid"], cl["inventory_number"]):
        key = f"{q}__cleveland"
        if key in state:
            continue
        got = cleveland(inv.split("|")[0])
        if not got:
            state[key] = {"status": "no_open_image", "id": inv}
            save_json(STATE, state)
            continue
        consider(q, "cleveland", got[0], got[1], {"id": inv})

    # 2. second (and third) Commons files, most-linked paintings first
    prim = info(list(meta["commons_file"]))
    todo = meta.sort_values("sl", ascending=False).head(COMMONS_LOOKUPS)
    for n, (q, f) in enumerate(zip(todo["qid"], todo["commons_file"])):
        if f"{q}__commons_searched" in state:
            continue
        cands = commons_second(q, P[q], prim[f]) if prim.get(f) else []
        for k, rec in enumerate(cands, start=2):
            consider(q, f"commons{k}", rec["thumburl"], rec["licence"],
                     {"file": rec["title"], "user": rec["user"], "credit": rec["credit"][:160]})
        state[f"{q}__commons_searched"] = {"status": "searched", "n": len(cands)}
        save_json(STATE, state)
        if n % 50 == 0:
            print(f"  commons second files: {n}/{len(todo)}", flush=True)

    finalise(meta, state)


def finalise(meta, state):
    """Apply the thresholds, delete rejected files, copy the pilot image in as <qid>__commons.jpg, write the CSV."""
    keep, c = {}, Counter()
    for key, rec in state.items():
        q, source = key.split("__")
        if source == "commons_searched":
            continue
        f = REPRO / f"{key}.jpg"
        if rec["status"] != "ok":
            c[f"{source.rstrip('23')}:{rec['status']}"] += 1
            continue
        d = rec["lab_diff"]
        if d < NEAR_IDENTICAL:
            c["dropped_near_identical"] += 1
            c[f"dropped_near_identical:{source.rstrip('23')}"] += 1
        elif source.startswith("commons") and d > COMMONS_MAX:
            c["dropped_commons_too_different"] += 1
        else:
            keep.setdefault(q, []).append((source, rec))
            continue
        f.unlink(missing_ok=True)
    rows = []
    order = {"met": 0, "aic": 0, "cleveland": 0, "nga": 0, "rijksmuseum": 0, "commons2": 1, "commons3": 2}
    title = dict(zip(meta["qid"], meta["title"]))
    for q, lst in keep.items():
        a = REPRO / f"{q}__commons.jpg"
        link_or_copy(PILOT / "images" / f"{q}.jpg", a)  # hard link: the pilot image costs no second copy
        lst.sort(key=lambda sr: order[sr[0]])
        files = [("commons", a, "")] + [(s, REPRO / f"{q}__{s}.jpg", r) for s, r in lst]
        for i in range(len(files)):
            for j in range(i + 1, len(files)):
                (sa, fa, _), (sb, fb, rb) = files[i], files[j]
                d = round(lab_diff(fa, fb), 3)
                ca, cb = chroma(fa), chroma(fb)
                flag = ("bw_reproduction" if min(ca, cb) < 0.3 * max(ca, cb) and max(ca, cb) > 5 else
                        "low_diff_maybe_same_master" if d < 2 else
                        "high_diff_check_frame_or_crop" if d > 12 else "")
                rows.append({"qid": q, "file_a": fa.name, "source_a": sa, "file_b": fb.name, "source_b": sb,
                             "lab_diff": d, "flag": flag, "chroma_a": ca, "chroma_b": cb, "pair_kind": "primary" if i == 0 and j == 1 else "extra",
                             "title": title.get(q, ""), "source_b_url": rb["url"], "source_b_note": rb.get("note", ""),
                             "source_b_file": rb.get("file", ""), "source_b_uploader": rb.get("user", "")})
    for path in (REPRO / "repro_pairs.csv", HERE / "repro_pairs.csv"):
        pd.DataFrame(rows).to_csv(path, index=False)
    for f in REPRO.glob("*__commons.jpg"):  # tidy copies whose pair was later rejected
        if f.name.split("__")[0] not in keep:
            f.unlink()
    c["paintings_with_a_pair"] = len(keep)
    c["paintings_with_three_reproductions"] = sum(len(v) >= 2 for v in keep.values())
    c["pair_rows"] = len(rows)
    for r in rows:
        if r["pair_kind"] == "primary":
            c["primary_pairs_flag:" + (r["flag"] or "none")] += 1
    for v in keep.values():
        c[f"kept_second_source:{v[0][0].rstrip('23')}"] += 1
    save_json(CACHE / "repro_summary.json", dict(c))
    print(dict(sorted(c.items())))


if __name__ == "__main__":
    if "--finalise" in sys.argv:
        m = pd.read_csv(PILOT / "meta.csv", dtype=str).fillna("")
        finalise(m, load_json(STATE, {}))
    else:
        main()
