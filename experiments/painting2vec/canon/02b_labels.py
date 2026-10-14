"""Fill English labels that came back empty because the item only has a 'mul' (default-for-all-languages)
label or no English one: ask again with language fallback. Rewrites the two jsonl files in place."""
import json, time
from wd import api

for path in ("data/items.jsonl", "data/refs.jsonl"):
    recs = [json.loads(l) for l in open(path)]
    todo = [r["id"] for r in recs if not r.get("label")]
    lab = {}
    for i in range(0, len(todo), 50):
        j = api("https://www.wikidata.org/w/api.php", {"action": "wbgetentities", "ids": "|".join(todo[i:i + 50]),
                "props": "labels", "languages": "en", "languagefallback": 1})
        for e in j.get("entities", {}).values():
            v = e.get("labels", {}).get("en", {}).get("value")
            if v: lab[e["id"]] = v
        time.sleep(0.3)
    # still nothing: the item has no English label at all; take one from another language and say which
    rest = [q for q in todo if q not in lab]
    for i in range(0, len(rest), 50):
        j = api("https://www.wikidata.org/w/api.php", {"action": "wbgetentities", "ids": "|".join(rest[i:i + 50]), "props": "labels"})
        for e in j.get("entities", {}).values():
            ls = e.get("labels", {})
            for lg in ["fr", "it", "es", "de", "nl", "pt", "ru", "ja", "zh", "ko"] + sorted(ls):
                if lg in ls:
                    lab[e["id"]] = ls[lg]["value"] + f" [{lg}]"; break
        time.sleep(0.3)
    for r in recs:
        if not r.get("label") and r["id"] in lab: r["label"] = lab[r["id"]]
    with open(path, "w") as f:
        for r in recs: f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(path, "missing", len(todo), "filled", len(lab))
