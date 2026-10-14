"""Wikidata entity fetching (wbgetentities, 50 per call), trimmed and cached, plus the metadata row builder."""
from __future__ import annotations

import time

from common import CACHE, WD_API, get, load_json, save_json

PAINTING = "Q3305213"
NON_WIKIPEDIA = {"commonswiki", "wikidatawiki", "specieswiki", "metawiki", "mediawikiwiki", "sourceswiki",
                 "incubatorwiki", "outreachwiki", "foundationwiki", "wikimaniawiki", "wikifunctionswiki"}
MUSEUM_IDS = {
    "P3634": "met_id", "P4610": "aic_id", "P4683": "nga_id", "P11110": "cleveland_id", "P13234": "rijksmuseum_id",
    "P4643": "philadelphia_id", "P4713": "walters_id", "P4712": "mia_id", "P2582": "getty_id",
    "P2539": "nationalmuseum_se_id", "P4704": "saam_id", "P8583": "yale_gallery_id", "P10121": "harvard_id",
    "P8905": "prado_id", "P4659": "orsay_id", "P9394": "louvre_ark", "P4625": "mfa_boston_id",
    "P4738": "ycba_id", "P4611": "lacma_id", "P1679": "artuk_id", "P350": "rkdimages_id", "P347": "joconde_id",
    "P10297": "google_arts_id",
}
ITEM_PROPS = ["P31", "P170", "P135", "P136", "P180", "P186", "P195", "P276", "P495", "P144", "P4969", "P179", "P361"]
UNIT_CM = {"Q174728": 1.0, "Q11573": 100.0, "Q174789": 0.1, "Q218593": 2.54, "Q3710": 30.48}

PCACHE = CACHE / "paintings.json"
CCACHE = CACHE / "creators.json"
LCACHE = CACHE / "labels.json"


def _best(claims, prop):
    st = [s for s in claims.get(prop, []) if s.get("rank") != "deprecated"]
    pref = [s for s in st if s.get("rank") == "preferred"]
    return pref or st


def _items(claims, prop):
    out = []
    for s in _best(claims, prop):
        snak = s["mainsnak"]
        if snak.get("snaktype") == "value" and snak["datavalue"]["type"] == "wikibase-entityid":
            out.append(snak["datavalue"]["value"]["id"])
        elif snak.get("snaktype") == "somevalue":
            out.append("UNKNOWN")
    return out


def _strings(claims, prop):
    return [s["mainsnak"]["datavalue"]["value"] for s in _best(claims, prop)
            if s["mainsnak"].get("snaktype") == "value" and isinstance(s["mainsnak"]["datavalue"]["value"], str)]


def _year(claims, prop):
    ys = []
    for s in _best(claims, prop):
        snak = s["mainsnak"]
        if snak.get("snaktype") != "value":
            continue
        t = snak["datavalue"]["value"]["time"]  # e.g. +1503-00-00T00:00:00Z
        sign = -1 if t[0] == "-" else 1
        try:
            ys.append(sign * int(t[1:].split("-")[0]))
        except ValueError:
            pass
    return ys


def _cm(claims, prop):
    for s in _best(claims, prop):
        snak = s["mainsnak"]
        if snak.get("snaktype") != "value":
            continue
        v = snak["datavalue"]["value"]
        f = UNIT_CM.get(v.get("unit", "").rsplit("/", 1)[-1])
        if f:
            return round(float(v["amount"]) * f, 2)
    return None


def _label(ent):
    labs = ent.get("labels", {})
    for lang in ("en", "mul", "fr", "de", "it", "es", "nl"):
        if lang in labs:
            return labs[lang]["value"]
    return next(iter(labs.values()))["value"] if labs else ""


def trim_painting(ent):
    c = ent.get("claims", {})
    d = {"label": _label(ent), "P18": _strings(c, "P18"), "P373": _strings(c, "P373"), "P217": _strings(c, "P217"),
         "inception": _year(c, "P571"), "h_cm": _cm(c, "P2048"), "w_cm": _cm(c, "P2049"),
         "wp_sitelinks": sum(1 for k in ent.get("sitelinks", {}) if k.endswith("wiki") and k not in NON_WIKIPEDIA),
         "ids": {name: _strings(c, p)[0] for p, name in MUSEUM_IDS.items() if _strings(c, p)}}
    for p in ITEM_PROPS:
        d[p] = _items(c, p)
    return d


def trim_creator(ent):
    c = ent.get("claims", {})
    return {"label": _label(ent), "birth": _year(c, "P569"), "death": _year(c, "P570"),
            "P27": _items(c, "P27"), "P31": _items(c, "P31")}


def _fetch(qids, props, trim, path, what):
    cache = load_json(path, {})
    for attempt in range(4):  # a batch that fails after backoff is retried on the next pass, never dropped
        todo = [q for q in dict.fromkeys(qids) if q not in cache and q.startswith("Q")]
        if not todo:
            break
        if attempt:
            print(f"  {what}: pass {attempt + 1}, {len(todo)} still missing", flush=True)
            time.sleep(30)
        for i in range(0, len(todo), 50):
            batch = todo[i:i + 50]
            r = get(WD_API, params={"action": "wbgetentities", "ids": "|".join(batch), "props": props,
                                    "languages": "en|mul|fr|de|it|es|nl", "format": "json"}, pause=0.5)
            try:
                js = r.json() if r is not None else {}
            except ValueError:
                js = {}
            if "entities" not in js:
                print(f"  {what}: bad response {str(js)[:200]}", flush=True)
                time.sleep(6)
                continue
            for q, ent in js["entities"].items():
                cache[q] = trim(ent) if "missing" not in ent else None
            for q in batch:  # redirects come back under the target id
                cache.setdefault(q, None)
            if (i // 50) % 10 == 0:
                save_json(path, cache)
                print(f"  {what}: {i + len(batch)}/{len(todo)}", flush=True)
    save_json(path, cache)
    return cache


def fetch_paintings(qids):
    return _fetch(qids, "claims|labels|sitelinks", trim_painting, PCACHE, "paintings")


def fetch_creators(qids):
    return _fetch(qids, "claims|labels", trim_creator, CCACHE, "creators")


def fetch_labels(qids):
    return _fetch(qids, "labels", _label, LCACHE, "labels")


COLUMNS = ["qid", "title", "creator_qid", "creator_name", "creator_birth_year", "creator_death_year",
           "inception_year", "movements", "genres", "depicts", "materials", "height_cm", "width_cm",
           "collection_qid", "collection_name", "country_qid", "country_name", "country_basis", "tradition",
           "sitelinks", "stratum", "commons_file", "image_source_url", "commons_page_url", "licence",
           "licence_detail", "px_width", "px_height", "orig_px_width", "orig_px_height", "pd_basis",
           "inventory_number", "fame_score", "in_poc"] + list(MUSEUM_IDS.values())


def pd_basis(p, creators):
    """Return the reason the work passes the pilot's worldwide-PD rule, or '' if it does not."""
    cq = [c for c in p["P170"] if c != "UNKNOWN" and c != "Q4233718"]
    deaths = [max(creators[c]["death"]) for c in cq if creators.get(c) and creators[c]["death"]]
    inc = min(p["inception"]) if p["inception"] else None
    if cq and len(deaths) == len(cq):
        return "creator_died_before_1926" if max(deaths) < 1926 else ""
    if inc is not None and inc < 1870:
        return "no_creator_death_date_inception_before_1870"
    return ""


def base_row(q, p, creators, labels, tradition_of):
    cq = [c for c in p["P170"] if c != "UNKNOWN"]
    lab = lambda ids, n=None: "|".join(labels.get(i) or i for i in (ids[:n] if n else ids) if i != "UNKNOWN")
    cr = [creators.get(c) or {"label": c, "birth": [], "death": []} for c in cq]
    trad, cqid, basis = tradition_of(p, creators)
    coll = p["P195"] or p["P276"]
    row = {
        "qid": q, "title": p["label"], "creator_qid": "|".join(cq), "creator_name": "|".join(c["label"] for c in cr),
        "creator_birth_year": "|".join(str(min(c["birth"])) for c in cr if c["birth"]),
        "creator_death_year": "|".join(str(max(c["death"])) for c in cr if c["death"]),
        "inception_year": min(p["inception"]) if p["inception"] else "",
        "movements": lab(p["P135"]), "genres": lab(p["P136"]), "depicts": lab(p["P180"], 30), "materials": lab(p["P186"]),
        "height_cm": p["h_cm"] if p["h_cm"] is not None else "", "width_cm": p["w_cm"] if p["w_cm"] is not None else "",
        "collection_qid": "|".join(c for c in coll if c != "UNKNOWN"), "collection_name": lab(coll),
        "country_qid": cqid, "country_name": labels.get(cqid, cqid) if cqid else "", "country_basis": basis,
        "tradition": trad, "sitelinks": p["wp_sitelinks"], "pd_basis": pd_basis(p, creators),
        "inventory_number": "|".join(p["P217"]),
    }
    row.update(p["ids"])
    return row
