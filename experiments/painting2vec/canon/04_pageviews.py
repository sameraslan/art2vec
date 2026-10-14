"""Pageviews for the last 60 days (MediaWiki PageViewInfo, prop=pageviews, 50 titles per call) in 12 large
Wikipedias, for every candidate with >= MIN Wikipedia editions. Resumable per wiki.
Out: data/pageviews.csv (qid, wiki, views60)"""
import csv, json, os, sys, time
from wd import api
from concurrent.futures import ThreadPoolExecutor
import threading
LOCK = threading.Lock()

MIN = int(sys.argv[1]) if len(sys.argv) > 1 else 3
WIKIS = ["en", "es", "fr", "de", "it", "ru", "ja", "zh", "pt", "ar", "ko", "fa"]
items = [json.loads(l) for l in open("data/items.jsonl")]
items = [d for d in items if sum(1 for s in d.get("sl", []) if s.endswith("wiki") and s not in ("commonswiki", "specieswiki", "metawiki", "wikidatawiki", "sourceswiki")) >= MIN]
print("items", len(items), file=sys.stderr)
done = set()
if os.path.exists("data/pageviews.csv"):
    done = {(r["qid"], r["wiki"]) for r in csv.DictReader(open("data/pageviews.csv"))}
else:
    open("data/pageviews.csv", "w").write("qid,wiki,views60\n")


def run(w):
    todo = [(d["id"], d["titles"][w]) for d in items if w in d.get("titles", {}) and (d["id"], w) not in done]
    url = f"https://{w}.wikipedia.org/w/api.php"
    res = []
    for i in range(0, len(todo), 50):
        chunk = todo[i:i + 50]; t2q = {}
        for q, t in chunk: t2q.setdefault(t, q)
        views, cont = {}, {}
        while True:
            j = api(url, dict({"action": "query", "prop": "pageviews", "pvipdays": 60,
                               "titles": "|".join(t2q)}, **cont))
            norm = {n["to"]: n["from"] for n in j["query"].get("normalized", []) + j["query"].get("converted", [])}
            for p in j["query"].get("pages", []):
                if "pageviews" in p:
                    t = norm.get(p["title"], p["title"])
                    views[t] = sum(v or 0 for v in p["pageviews"].values())
            if "continue" in j:
                cont = j["continue"]; time.sleep(0.1)
            else:
                break
        with LOCK, open("data/pageviews.csv", "a", newline="") as f:   # written per batch, so a crash loses nothing
            csv.writer(f).writerows((q, w, views.get(t, "")) for t, q in t2q.items())
        res.append(len(t2q))
        time.sleep(0.2)
    return w, sum(res)


with ThreadPoolExecutor(4) as ex:      # one worker per wiki host, four hosts at a time
    for res in ex.map(run, WIKIS):
        print(*res, file=sys.stderr)
