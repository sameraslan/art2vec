"""Measure: every item typed painting (P31 = Q3305213) with >= 1 sitelink, and every item typed as a
SUBCLASS of painting (fresco, watercolour, hanging scroll, miniature ...) with >= 1 sitelink.
Scans run on QLever (they time out on WDQS); the headline total is cross-checked on WDQS.
Out: data/paintings_sitelinks.csv (qid, sitelinks, direct_p31, cls), data/sitelink_histogram.csv"""
import csv, sys
from wd import qlever, sparql

print("WDQS total P31=painting:", sparql("SELECT (COUNT(*) AS ?n) WHERE { ?p wdt:P31 wd:Q3305213 }"), file=sys.stderr)
hist = qlever("SELECT ?s (COUNT(?p) AS ?n) WHERE { ?p wdt:P31 wd:Q3305213 . ?p wikibase:sitelinks ?s } GROUP BY ?s ORDER BY ?s")
with open("data/sitelink_histogram.csv", "w", newline="") as f:
    w = csv.writer(f); w.writerow(["sitelinks", "n_items"]); w.writerows(hist)

rows = {}
for p, s in qlever("SELECT ?p ?s WHERE { ?p wdt:P31 wd:Q3305213 . ?p wikibase:sitelinks ?s . FILTER(xsd:integer(?s) >= 1) }"):
    rows[p] = [int(s), 1, "Q3305213"]
print("direct", len(rows), file=sys.stderr)
sub = qlever("""SELECT ?p ?s ?c WHERE { ?c wdt:P279+ wd:Q3305213 . ?p wdt:P31 ?c . ?p wikibase:sitelinks ?s . FILTER(xsd:integer(?s) >= 1) }""")
n = 0
for p, s, c in sub:
    if p not in rows:
        rows[p] = [int(s), 0, c]; n += 1
print("via subclass only", n, file=sys.stderr)
with open("data/paintings_sitelinks.csv", "w", newline="") as f:
    w = csv.writer(f); w.writerow(["qid", "sitelinks", "direct_p31", "cls"])
    for k, v in sorted(rows.items(), key=lambda kv: (-kv[1][0], int(kv[0][1:]))):
        w.writerow([k] + v)
