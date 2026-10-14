"""Shared helpers: polite SPARQL / MediaWiki API access for the canon measurements."""
import time, json, sys
import requests

UA = "art2vec-research/0.1 (https://github.com/sameraslan/recmyrecord)"
SPARQL = "https://query.wikidata.org/sparql"
S = requests.Session()
S.headers.update({"User-Agent": UA})


def sparql(q, tries=5, timeout=75):
    """Run one SPARQL query; back off on 429/5xx. Returns list of dict rows (plain values)."""
    for i in range(tries):
        try:
            r = S.get(SPARQL, params={"query": q, "format": "json"}, timeout=timeout)
            if r.status_code == 200:
                out = []
                for b in r.json()["results"]["bindings"]:
                    out.append({k: v["value"] for k, v in b.items()})
                time.sleep(1.0)
                return out
            wait = int(r.headers.get("Retry-After", 5 * (i + 1)))
            print(f"  sparql {r.status_code}, wait {wait}s", file=sys.stderr)
            time.sleep(min(wait, 60))
        except requests.RequestException as e:
            print(f"  sparql error {e!r}", file=sys.stderr)
            time.sleep(20 * (i + 1))
        except ValueError as e:   # truncated JSON = server-side timeout mid-stream
            print(f"  sparql truncated {e!r}", file=sys.stderr)
            time.sleep(30 * (i + 1))
    raise RuntimeError("sparql failed: " + q[:200])


def api(url, params, tries=8):
    params = dict(params, format="json", formatversion=2)  # read-only: no maxlag (it tracks WDQS lag, which only matters for edits)
    for i in range(tries):
        try:
            # POST: 50 non-Latin titles overflow the URL length limit as a GET
            r = S.post(url, data=params, timeout=90)
            if r.status_code == 200:
                j = r.json()
                if "error" in j and j["error"].get("code") == "maxlag":
                    time.sleep(5); continue
                return j
            time.sleep(5 * (i + 1))
        except requests.RequestException as e:
            print(f"  api error {e!r}", file=sys.stderr)
            time.sleep(5 * (i + 1))
    raise RuntimeError("api failed")


def qid(uri):
    return uri.rsplit("/", 1)[-1]


QLEVER = "https://qlever.cs.uni-freiburg.de/api/wikidata"
PREFIXES = ("PREFIX xsd: <http://www.w3.org/2001/XMLSchema#> PREFIX wd: <http://www.wikidata.org/entity/> PREFIX wdt: <http://www.wikidata.org/prop/direct/> "
            "PREFIX wikibase: <http://wikiba.se/ontology#> PREFIX schema: <http://schema.org/> "
            "PREFIX p: <http://www.wikidata.org/prop/> PREFIX ps: <http://www.wikidata.org/prop/statement/> "
            "PREFIX pq: <http://www.wikidata.org/prop/qualifier/> PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> ")


def qlever(q, tries=4):
    """QLever's public Wikidata mirror (University of Freiburg). Used for scans over all 1.08M paintings,
    which time out on query.wikidata.org. Returns rows as lists of strings (TSV), header dropped."""
    for i in range(tries):
        try:
            r = S.get(QLEVER, params={"query": PREFIXES + q},
                      headers={"Accept": "text/tab-separated-values"}, timeout=180)
            if r.status_code == 200:
                lines = r.text.rstrip("\n").split("\n")[1:]
                time.sleep(1.0)
                return [[c.strip("<>").replace("http://www.wikidata.org/entity/", "").split("^^")[0].strip('"')
                         for c in l.split("\t")] for l in lines if l]
            print("  qlever", r.status_code, r.text[:200], file=sys.stderr)
        except requests.RequestException as e:
            print(f"  qlever error {e!r}", file=sys.stderr)
        time.sleep(10 * (i + 1))
    raise RuntimeError("qlever failed: " + q[:200])
