"""Gather independent canon lists that exist in machine-readable form and resolve them to QIDs.
Out: data/lists.csv (list, qid, note). Facts only (identifiers); no text or images are copied."""
import csv, re, sys, time
from wd import sparql, api, S, qid

EN = "https://en.wikipedia.org/w/api.php"
out = []


def titles_to_qids(titles):
    res = {}
    for i in range(0, len(titles), 50):
        j = api(EN, {"action": "query", "prop": "pageprops", "ppprop": "wikibase_item", "redirects": 1,
                     "titles": "|".join(titles[i:i + 50])})
        for p in j["query"].get("pages", []):
            q = p.get("pageprops", {}).get("wikibase_item")
            if q: res[p["title"]] = q
        time.sleep(0.3)
    return res


def raw(title):
    return S.get("https://en.wikipedia.org/w/index.php", params={"title": title, "action": "raw"}, timeout=60).text


# 1. Wikipedia Vital articles level 5, "Specific works of visual art" > Painting (level 4 is a subset, marked)
t = raw("Wikipedia:Vital_articles/Level_5/Arts/Audiovisual_arts")
m = re.search(r"=+\s*Painting\s*=+\n(.*?)\n=+\s*Sculpture\s*=+", t[t.index("Specific works of visual art"):], re.S)
sec = m.group(1)
ts, lvl = [], {}
for line in sec.split("\n"):
    if line.startswith("#"):
        mm = re.search(r"\[\[([^\]|#]+)", line)
        if mm:
            ts.append(mm.group(1).strip()); lvl[ts[-1]] = "L4" if "{{Icon|L4}}" in line or "'''" in line else "L5"
qs = titles_to_qids(ts)
for k, q in qs.items(): out.append(("vital5", q, k))
print("vital5", len(ts), len(qs), file=sys.stderr)

# 2. "1001 Paintings You Must See Before You Die" as tagged on Wikidata (partial: 581 of ~1001)
for x in sparql("SELECT ?i WHERE { ?i wdt:P1343 wd:Q66362718 }"): out.append(("1001paintings", qid(x["i"]), ""))
# 3. BBC "100 Great Paintings" (Mullins 1981), catalogue code qualifier
for x in sparql("SELECT DISTINCT ?i WHERE { ?i p:P528 ?s. ?s pq:P972 wd:Q121297196 }"): out.append(("bbc100", qid(x["i"]), ""))
# 4. Smarthistory: any item with a Smarthistory ID
for x in sparql("SELECT DISTINCT ?i WHERE { ?i wdt:P6405 [] }"): out.append(("smarthistory", qid(x["i"]), ""))
# 5. AP Art History 250: every wikilink in the "Works studied" section of the Wikipedia article
t = raw("AP_Art_History")
i0 = t.index("Works studied") if "Works studied" in t else 0
sec = t[i0:]
ts = []
for line in sec.split("\n"):
    if line.startswith("*") or line.startswith("#"):
        mm = re.search(r"\[\[([^\]|#]+)", line)
        if mm: ts.append(mm.group(1).strip())
qs = titles_to_qids(sorted(set(ts)))
for k, q in qs.items(): out.append(("ap250", q, k))
print("ap250 links", len(set(ts)), len(qs), file=sys.stderr)

# 6. Museum highlight flags, joined through the museum's Wikidata external-id property
def by_ids(prop, ids, name):
    n = 0
    for i in range(0, len(ids), 200):
        vals = " ".join('"%s"' % v for v in ids[i:i + 200])
        for x in sparql(f"SELECT ?i ?v WHERE {{ VALUES ?v {{ {vals} }} ?i wdt:{prop} ?v }}"):
            out.append((name, qid(x["i"]), x["v"])); n += 1
    print(name, len(ids), "->", n, file=sys.stderr)

# Met: isHighlight & medium=Paintings (v1.1 search, paged)
ids, off = [], 0
while True:
    j = S.get("https://collectionapi.metmuseum.org/public/collection/v1.1/search",
              params={"isHighlight": "true", "medium": "Paintings", "q": "*", "offset": off, "limit": 100}, timeout=60).json()
    got = j.get("objectIDs") or [o.get("objectID") for o in j.get("data", [])]
    if not got: 
        if off == 0: print("met raw", str(j)[:300], file=sys.stderr)
        break
    ids += [str(g) for g in got]; off += len(got); time.sleep(0.5)
    if off >= j.get("total", 0): break
by_ids("P3634", sorted(set(ids)), "met_highlight")

# AIC: is_boosted & artwork_type Painting
ids, page = [], 1
while True:
    j = S.get("https://api.artic.edu/api/v1/artworks/search", params={
        "query[bool][must][0][term][is_boosted]": "true", "query[bool][must][1][term][artwork_type_id]": 1,
        "fields": "id", "limit": 100, "page": page}, timeout=60).json()
    if not j.get("data"): break
    ids += [str(d["id"]) for d in j["data"]]; page += 1; time.sleep(0.5)
    if page > j["pagination"]["total_pages"]: break
by_ids("P4610", ids, "aic_boosted")

# Cleveland: highlight paintings; the record itself carries a Wikidata link
j = S.get("https://openaccess-api.clevelandart.org/api/artworks/", params={
    "type": "Painting", "highlight": 1, "limit": 200, "fields": "id,accession_number,external_resources"}, timeout=60).json()
n = 0
for d in j.get("data", []):
    for u in (d.get("external_resources") or {}).get("wikidata", []) or []:
        out.append(("cma_highlight", u.rsplit("/", 1)[-1], d.get("accession_number", ""))); n += 1
print("cma", len(j.get("data", [])), "->", n, file=sys.stderr)

# 7. National Treasures of Japan (paintings): the designation is on Wikidata
for x in sparql("""SELECT DISTINCT ?i WHERE { ?i wdt:P1435 wd:Q1188622 . ?i wdt:P31/wdt:P279* wd:Q3305213 }"""):
    out.append(("jp_national_treasure", qid(x["i"]), ""))

with open("data/lists.csv", "w", newline="") as f:
    w = csv.writer(f); w.writerow(["list", "qid", "note"]); w.writerows(sorted(set(out)))
import collections
print(collections.Counter(o[0] for o in set(out)), file=sys.stderr)
