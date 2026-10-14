"""Supplement to 01: painted works typed only by FORMAT (triptych, polyptych, diptych, altarpiece, folding
screen) or as an aggregate (painting series / cycle / group), none of which sit under 'painting' in the
Wikidata class tree. Appended to data/paintings_sitelinks.csv with direct_p31 = 0."""
import csv, time
from wd import qlever

FORMAT = ["Q79218", "Q1278452", "Q475476", "Q15711026", "Q11801536", "Q741226", "Q1144689"]
AGG = ["Q15727816", "Q16905563", "Q18573970"]
have = {r["qid"] for r in csv.DictReader(open("data/paintings_sitelinks.csv"))}
new = {}
for c in FORMAT + AGG:
    for p, s in qlever(f"SELECT ?p ?s WHERE {{ ?p wdt:P31 wd:{c} . ?p wikibase:sitelinks ?s . FILTER(xsd:integer(?s) >= 1) }}"):
        if p not in have and p not in new: new[p] = (int(s), 0, c)
    time.sleep(3)
with open("data/paintings_sitelinks.csv", "a", newline="") as f:
    w = csv.writer(f)
    for k, v in sorted(new.items(), key=lambda kv: -kv[1][0]): w.writerow([k, *v])
print("added", len(new), "of which >=2 sitelinks:", sum(v[0] >= 2 for v in new.values()))
