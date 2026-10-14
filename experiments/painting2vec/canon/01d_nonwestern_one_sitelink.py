"""The floor for under-represented traditions has to reach below the general threshold, so list every painting
with >= 1 sitelink whose creator citizenship or country of origin maps to one of those traditions.
Out: data/nonwestern_ids.txt (QIDs; 02_entities.py fetches their facts when run with the 'extra' argument)."""
import time
import pandas as pd
from common import tradition
from wd import qlever

WEST = {"Western Europe", "Russia / Eastern Europe", "North America (US/Canada)", "Oceania (settler)", None}
pool = pd.read_csv("data/pool_by_country.csv")
pool["tradition"] = pool.label.map(lambda l: tradition([l]))
cs = sorted(set(pool[~pool.tradition.isin(WEST)].country))
ids = set()
for path in ("wdt:P170/wdt:P27", "wdt:P495"):
    for i in range(0, len(cs), 80):
        vals = " ".join("wd:" + c for c in cs[i:i + 80])
        q = f"""SELECT DISTINCT ?p WHERE {{ VALUES ?c {{ {vals} }} ?p {path} ?c . ?p wdt:P31/wdt:P279* wd:Q3305213 .
                ?p wikibase:sitelinks ?s . FILTER(xsd:integer(?s) >= 1) }}"""
        ids.update(r[0] for r in qlever(q)); time.sleep(4)
open("data/nonwestern_ids.txt", "w").write("\n".join(sorted(ids)))
print(len(cs), "countries;", len(ids), "paintings")
