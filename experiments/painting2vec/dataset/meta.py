"""Download a list of paintings' Commons images one at a time and write the metadata CSV for them."""
from __future__ import annotations

import csv
import importlib
from collections import Counter
from pathlib import Path

from PIL import Image

from common import link_or_copy
from commons import fetch_image, info, is_open
from wd import COLUMNS, base_row, fetch_creators, fetch_labels, fetch_paintings

CANON = Path(__file__).resolve().parents[1] / "canon" / "candidates.csv"
tradition_of = importlib.import_module("02_select").tradition_of


def build(entries, images_dir: Path, out_csvs, require_open=True, link_from: Path | None = None):
    """entries: [{qid, stratum}]. Downloads <qid>.jpg into images_dir (resumable) and writes the CSV(s).
    Returns the rows written; paintings whose image could not be had are left out and counted."""
    qids = [e["qid"] for e in entries]
    P = fetch_paintings(qids)
    C = fetch_creators([a for q in qids if P.get(q) for a in P[q]["P170"]])
    recs = info([P[q]["P18"][0] for q in qids if P.get(q) and P[q]["P18"]])
    status = Counter()
    rows = []
    for n, e in enumerate(entries):
        q = e["qid"]
        p = P.get(q)
        rec = recs.get(p["P18"][0]) if p and p["P18"] else None
        if not rec or not rec.get("thumburl"):
            status["no_commons_record"] += 1
            continue
        if require_open and not is_open(rec):
            status["licence_not_pd_or_cc0"] += 1
            continue
        dest = images_dir / f"{q}.jpg"
        if link_from is not None and (link_from / f"{q}.jpg").exists():
            link_or_copy(link_from / f"{q}.jpg", dest)  # already downloaded for the pilot set
        st = fetch_image(rec["thumburl"], dest)
        status[st] += 1
        if n % 100 == 0:
            print(f"  images {n}/{len(entries)} {dict(status)}", flush=True)
        if not dest.exists():
            continue
        try:
            with Image.open(dest) as im:
                px = im.size
        except Exception:  # noqa: BLE001
            dest.unlink()
            status["stored_file_unreadable"] += 1
            continue
        rows.append((q, e, rec, px))
    lab_ids = set()
    for q, *_ in rows:
        p = P[q]
        for k in ("P135", "P136", "P186", "P195", "P276", "P495"):
            lab_ids.update(p[k])
        lab_ids.update(p["P180"][:30])
        lab_ids.update(c for a in p["P170"] if C.get(a) for c in C[a]["P27"])
    L = fetch_labels(sorted(i for i in lab_ids if i != "UNKNOWN"))
    canon = {}
    if CANON.exists():  # the canon agent's ranked list; joined on qid, blank where the qid is not in it
        with open(CANON, newline="", encoding="utf-8") as f:
            canon = {r["qid"]: r for r in csv.DictReader(f)}
    out = []
    for q, e, rec, px in rows:
        row = base_row(q, P[q], C, L, tradition_of)
        row.update({"stratum": e["stratum"], "commons_file": rec["title"], "image_source_url": rec["thumburl"],
                    "commons_page_url": rec["descurl"], "licence": rec["licence"], "licence_detail": rec["licence_detail"],
                    "px_width": px[0], "px_height": px[1], "orig_px_width": rec["w"], "orig_px_height": rec["h"]})
        row["fame_score"] = canon.get(q, {}).get("fame_score", "")
        row["in_poc"] = canon.get(q, {}).get("in_poc", "")
        out.append(row)
    for path in out_csvs:
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=COLUMNS, extrasaction="ignore")
            w.writeheader()
            w.writerows(out)
    print("download status:", dict(status), "| rows written:", len(out), flush=True)
    return out
