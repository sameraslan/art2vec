"""Part 3(a): does each candidate have a usable Wikipedia lead paragraph? Fetches the plain-text intro of the
English article (TextExtracts, 20 titles per call) and records ONLY ITS LENGTH; no text is stored.
Out: data/lead_lengths.csv (qid, en_title, lead_chars)"""
import csv, os, time
from common import load
from wd import api

df, _, _ = load()
todo = df[df.in_base & (df.clean >= 3) & df.enwiki.notna()][["qid", "enwiki"]].values.tolist()
done = set()
if os.path.exists("data/lead_lengths.csv"):
    done = {r["qid"] for r in csv.DictReader(open("data/lead_lengths.csv"))}
else:
    open("data/lead_lengths.csv", "w").write("qid,en_title,lead_chars\n")
todo = [t for t in todo if t[0] not in done]
print("todo", len(todo))
with open("data/lead_lengths.csv", "a", newline="") as f:
    w = csv.writer(f)
    for i in range(0, len(todo), 20):
        chunk = dict((t, q) for q, t in todo[i:i + 20])
        res, cont = {}, {}
        while True:
            j = api("https://en.wikipedia.org/w/api.php", dict({"action": "query", "prop": "extracts", "exintro": 1,
                    "explaintext": 1, "exlimit": 20, "redirects": 1, "titles": "|".join(chunk)}, **cont))
            back = {n["to"]: n["from"] for n in j["query"].get("normalized", []) + j["query"].get("redirects", [])}
            for p in j["query"].get("pages", []):
                if "extract" in p:
                    t = p["title"]
                    while t not in chunk and t in back: t = back[t]
                    res[t] = len(p["extract"])
            if "continue" in j: cont = j["continue"]
            else: break
        for t, q in chunk.items(): w.writerow([q, t, res.get(t, "")])
        time.sleep(0.2)
