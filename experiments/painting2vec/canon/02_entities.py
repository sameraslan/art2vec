"""Fetch compact facts for every candidate (sitelinks >= MIN) through wbgetentities (50 ids per call),
then for every creator, collection, country etc. referenced. Resumable. No images are fetched.
Out: data/items.jsonl, data/refs.jsonl"""
import csv, json, os, sys, time
from wd import api

WD = "https://www.wikidata.org/w/api.php"
MIN = int(sys.argv[1]) if len(sys.argv) > 1 else 2
ITEM_PROPS = ["P31", "P18", "P571", "P170", "P195", "P276", "P180", "P2048", "P2049", "P186", "P361",
              "P179", "P136", "P135", "P1343", "P17", "P495", "P527", "P6216", "P144", "P1071", "P2596", "P127"]
PV_WIKIS = ["en", "es", "fr", "de", "it", "ru", "ja", "zh", "pt", "ar", "ko", "fa"]  # titles kept for the pageview score
REF_PROPS = ["P31", "P569", "P570", "P27", "P19", "P17", "P131", "P279", "P135", "P2596", "P172", "P21"]


def val(snak):
    if snak.get("snaktype") != "value":
        return None
    d = snak["datavalue"]; t = d["type"]; v = d["value"]
    if t == "wikibase-entityid": return v["id"]
    if t == "time": return v["time"]
    if t == "quantity": return v["amount"] + "|" + v.get("unit", "").rsplit("/", 1)[-1]
    if t == "string": return v
    if t == "monolingualtext": return v["text"]
    return None


def compact(e, props):
    out = {"id": e["id"], "label": e.get("labels", {}).get("en", {}).get("value"),
           "desc": e.get("descriptions", {}).get("en", {}).get("value")}
    c = e.get("claims", {})
    for p in props:
        if p in c:
            vs = [val(s["mainsnak"]) for s in c[p] if s.get("rank") != "deprecated"]
            vs = [v for v in vs if v is not None]
            if p == "P18": vs = vs[:1]
            if vs: out[p] = vs
    if "sitelinks" in e:
        out["sl"] = sorted(e["sitelinks"].keys())
        if "enwiki" in e["sitelinks"]: out["en"] = e["sitelinks"]["enwiki"]["title"]
        out["titles"] = {w: e["sitelinks"][w + "wiki"]["title"] for w in PV_WIKIS if w + "wiki" in e["sitelinks"]}
    return out


def fetch(ids, path, props, sitelinks):
    done = set()
    if os.path.exists(path):
        with open(path) as f:
            done = {json.loads(l)["id"] for l in f}
    todo = [i for i in ids if i not in done]
    print(path, "todo", len(todo), file=sys.stderr)
    # three polite workers (each batch is a ~1-2 MB JSON response; one worker takes over an hour)
    from concurrent.futures import ThreadPoolExecutor
    batches = [todo[i:i + 50] for i in range(0, len(todo), 50)]

    def one(b):
        j = api(WD, {"action": "wbgetentities", "ids": "|".join(b),
                     "props": "labels|descriptions|claims" + ("|sitelinks" if sitelinks else ""),
                     "languages": "en"})
        recs = []
        for e in j.get("entities", {}).values():
            if "missing" in e: continue
            rec = compact(e, props)
            if rec["id"] not in b: rec["redirect_target"] = True
            recs.append(rec)
        time.sleep(0.2)
        return recs

    with open(path, "a") as f, ThreadPoolExecutor(3) as ex:
        for n, recs in enumerate(ex.map(one, batches)):
            for rec in recs:
                f.write(json.dumps(rec, ensure_ascii=False) + "\n")
            if n % 40 == 0: print(" ", n * 50, file=sys.stderr); f.flush()


ids = [r["qid"] for r in csv.DictReader(open("data/paintings_sitelinks.csv")) if int(r["sitelinks"]) >= MIN]
if os.path.exists("data/lists.csv"):   # also every member of the independent canon lists, whatever its type
    ids += sorted({r["qid"] for r in csv.DictReader(open("data/lists.csv"))} - set(ids))
if os.path.exists("data/nonwestern_ids.txt"):   # under-represented traditions are fetched down to 1 sitelink
    ids += sorted(set(open("data/nonwestern_ids.txt").read().split()) - set(ids))
if os.path.exists("data/member_ids.txt"):       # members of series / cycle / group items, at any sitelink count
    ids += sorted(set(open("data/member_ids.txt").read().split()) - set(ids))
fetch(ids, "data/items.jsonl", ITEM_PROPS, True)
refs = set()
for l in open("data/items.jsonl"):
    d = json.loads(l)
    for p in ("P170", "P195", "P276", "P17", "P495", "P186", "P136", "P135", "P31", "P361", "P179", "P1343", "P6216"):
        refs.update(v for v in d.get(p, []) if isinstance(v, str) and v.startswith("Q"))
fetch(sorted(refs), "data/refs.jsonl", REF_PROPS, False)
# second hop: countries / places / classes of the refs (labels only matter)
refs2 = set()
for l in open("data/refs.jsonl"):
    d = json.loads(l)
    for p in ("P27", "P17", "P19", "P131", "P31", "P135", "P172"):
        refs2.update(v for v in d.get(p, []) if isinstance(v, str) and v.startswith("Q"))
fetch(sorted(refs2), "data/refs.jsonl", REF_PROPS, False)
