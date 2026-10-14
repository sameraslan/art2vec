"""Step 2: fetch the candidates' Wikidata records, apply the public-domain rule, pick the pilot set.

Writes data/painting2vec/cache/eligible.json: [{qid, tradition}] for every candidate that is an
instance of painting, has a raster P18 image and passes the PD rule, ordered by Wikipedia sitelink
count descending, ties in md5(QID) order. Step 3 checks Commons licences and makes the final pick.
"""
import hashlib
import importlib
from collections import Counter

from common import CACHE, load_json, save_json
from wd import PAINTING, fetch_creators, fetch_labels, fetch_paintings, pd_basis

REGIONS = importlib.import_module("01_candidates").REGIONS
COUNTRY_TRAD = {c: t for t, cs in REGIONS.items() for c in cs}
ZERO_SAMPLE = 700
IMAGE_EXT = (".jpg", ".jpeg", ".png", ".tif", ".tiff", ".webp")


def tradition_of(p, creators):
    """(tradition, country qid, basis). Painting's country of origin wins over creator citizenship."""
    for c in p["P495"]:
        if c in COUNTRY_TRAD:
            return COUNTRY_TRAD[c], c, "country_of_origin"
    cits = [c for a in p["P170"] if creators.get(a) for c in creators[a]["P27"]]
    for c in cits:
        if c in COUNTRY_TRAD:
            return COUNTRY_TRAD[c], c, "creator_citizenship"
    if p["P495"] and p["P495"][0] != "UNKNOWN":
        return "european_american", p["P495"][0], "country_of_origin"
    if cits and cits[0] != "UNKNOWN":
        return "european_american", cits[0], "creator_citizenship"
    return "unknown", "", ""


def h(q):
    return hashlib.md5(q.encode()).hexdigest()


def key(q, P):
    """Wikipedia sitelinks descending; ties in a fixed pseudo-random order (md5 of the QID), so that a
    tie is not broken by import order, which would favour whichever museum was bulk-loaded first."""
    return (-P[q]["wp_sitelinks"], h(q))


def main():
    g = load_json(CACHE / "cand_global.json")["items"]
    r = load_json(CACHE / "cand_regional.json")["items"]
    z = load_json(CACHE / "cand_regional_zero.json")["items"]
    zsample = []
    for t in REGIONS:  # a fixed pseudo-random sample of each tradition's wider pool
        zsample += sorted((q for q, tt in z.items() if tt == t and q not in g and q not in r), key=h)[:ZERO_SAMPLE]
    print("pools: global", len(g), "regional", len(r), "zero-sitelink pool", len(z), "sampled", len(zsample))
    want = set(g) | set(r) | set(zsample)
    P = fetch_paintings(sorted(want))
    P = {q: p for q, p in P.items() if p and q in want}
    C = fetch_creators([a for p in P.values() for a in p["P170"]])
    fetch_labels(list(COUNTRY_TRAD))

    ok, why = [], Counter()
    for q, p in P.items():
        if PAINTING not in p["P31"]:
            why["not_instance_of_painting"] += 1
        elif not p["P18"] or not p["P18"][0].lower().endswith(IMAGE_EXT):
            why["no_usable_P18"] += 1
        elif not pd_basis(p, C):
            why["fails_pd_rule"] += 1
        else:
            ok.append(q)
    print("pool", len(P), "eligible", len(ok), dict(why))

    ranked = sorted(ok, key=lambda q: key(q, P))
    out = [{"qid": q, "tradition": tradition_of(P[q], C)[0]} for q in ranked]
    print("eligible by tradition:", Counter(o["tradition"] for o in out))
    save_json(CACHE / "eligible.json", out)


if __name__ == "__main__":
    main()
