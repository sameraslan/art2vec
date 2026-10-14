"""How deep is Wikidata's pool of paintings per country of origin / creator citizenship, at any sitelink
count? One aggregate per signal on QLever. Out: data/pool_by_country.csv
(country, label, signal, n_all, n_with_image, n_sitelinks_ge1)"""
import csv, time
from wd import qlever

out = []
for sig, path in (("creator_citizenship", "wdt:P170/wdt:P27"), ("country_of_origin", "wdt:P495")):
    q = f"""SELECT ?c ?l (COUNT(DISTINCT ?p) AS ?n) (COUNT(DISTINCT ?pi) AS ?ni) (COUNT(DISTINCT ?ps) AS ?ns) WHERE {{
      ?p wdt:P31 wd:Q3305213 . ?p {path} ?c . ?c rdfs:label ?l . FILTER(LANG(?l) = "en")
      OPTIONAL {{ ?p wdt:P18 ?img . BIND(?p AS ?pi) }}
      OPTIONAL {{ ?p wikibase:sitelinks ?s . FILTER(xsd:integer(?s) >= 1) BIND(?p AS ?ps) }}
    }} GROUP BY ?c ?l ORDER BY DESC(?n)"""
    for c, l, n, ni, ns in qlever(q):
        out.append([c, l.replace('"@en', "").strip('"'), sig, n, ni, ns])
    time.sleep(5)
with open("data/pool_by_country.csv", "w", newline="") as f:
    w = csv.writer(f); w.writerow(["country", "label", "signal", "n_all", "n_with_image", "n_sitelinks_ge1"]); w.writerows(out)
print(len(out))
