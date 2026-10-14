"""Step 1: candidate painting QIDs from the Wikidata SPARQL endpoint.

Two pools, both cached in data/painting2vec/cache/ so reruns are free:
  cand_global.json   {qid: sitelinks} for instance-of painting with sitelinks >= MIN_SL,
                     fetched one exact sitelink count (or a small group of counts) at a time; the endpoint times out at 60 s.
  cand_regional.json {qid: sitelinks} for paintings whose country of origin (P495), or whose
                     creator's citizenship (P27), is one of the non-European countries/states below.
"""
from common import CACHE, load_json, qid, save_json, sparql

MIN_SL = 5  # global pool floor (all sitelinks, any project; step 2 recounts Wikipedia-only)
ZERO_LIMIT = 6000  # per country and relation, for the no-sitelink pool

# Non-European countries and historical states, grouped into the traditions the pilot stratifies on.
# Labels are re-read from Wikidata in step 2 and printed, so a wrong QID here is visible.
REGIONS = {
    "japanese": ["Q17", "Q188712", "Q205662"],
    "chinese": ["Q148", "Q8733", "Q9903", "Q7462", "Q9683", "Q7313", "Q13426199", "Q865", "Q29520"],
    "korean": ["Q18097", "Q884", "Q28179", "Q423", "Q28233"],
    "south_asian": ["Q668", "Q33296", "Q129286", "Q843", "Q902", "Q854", "Q837"],
    "persian_ottoman": ["Q794", "Q12560", "Q43", "Q161205", "Q83311", "Q796", "Q858", "Q265", "Q889"],
    "other_non_european": ["Q79", "Q96", "Q419", "Q115", "Q869", "Q881", "Q252", "Q17252", "Q11768", "Q155",
                           "Q414", "Q298", "Q739", "Q736", "Q750", "Q241", "Q1033", "Q258", "Q928",
                           "Q836", "Q424", "Q711", "Q1028", "Q262", "Q948", "Q717", "Q77", "Q733"],
}


def run(query):
    return {qid(b["p"]["value"]): int(b["sl"]["value"]) for b in sparql(query)}


def main():
    gpath = CACHE / "cand_global.json"
    state = load_json(gpath, {"done": [], "items": {}})
    # An exact sitelink count is an index lookup; a FILTER(?sl >= n) range scan is not and times out.
    groups = [[n] for n in range(MIN_SL, 16)] + [list(range(a, a + 5)) for a in range(16, 61, 5)] \
        + [list(range(a, a + 20)) for a in range(61, 301, 20)]
    for grp in groups:
        name = f"{grp[0]}-{grp[-1]}"
        if name in state["done"]:
            continue
        vals = " ".join(str(n) for n in grp)
        got = run(f"SELECT ?p ?sl WHERE {{ VALUES ?sl {{ {vals} }} ?p wikibase:sitelinks ?sl ; wdt:P31 wd:Q3305213 . }}")
        print(f"global sitelinks {name}: {len(got)}", flush=True)
        state["items"].update(got)
        state["done"].append(name)
        save_json(gpath, state)
    print("global pool:", len(state["items"]))

    rpath = CACHE / "cand_regional.json"
    rstate = load_json(rpath, {"done": [], "items": {}})
    for trad, countries in REGIONS.items():
        for c in countries:
            for kind, pat in (("origin", f"?p wdt:P495 wd:{c} ."), ("citizen", f"?a wdt:P27 wd:{c} . ?p wdt:P170 ?a .")):
                key = f"{c}:{kind}"
                if key in rstate["done"]:
                    continue
                q = (f"SELECT DISTINCT ?p ?sl WHERE {{ {pat} ?p wdt:P31 wd:Q3305213 ; wdt:P18 ?img ; "
                     f"wikibase:sitelinks ?sl . FILTER(?sl >= 1) }}")
                try:
                    got = run(q)
                except RuntimeError as e:
                    print(f"regional {trad} {key}: FAILED {e}", flush=True)
                    continue
                print(f"regional {trad} {key}: {len(got)}", flush=True)
                rstate["items"].update(got)
                rstate["done"].append(key)
                save_json(rpath, rstate)
    print("regional pool:", len(rstate["items"]))

    # Paintings with no sitelinks at all: needed because Korean, South Asian and Persian painting is
    # nearly absent from Wikipedia. Step 2 samples these in a fixed pseudo-random order.
    zpath = CACHE / "cand_regional_zero.json"
    zstate = load_json(zpath, {"done": [], "items": {}})
    for trad, countries in REGIONS.items():
        for c in countries:
            for kind, pat in (("origin", f"?p wdt:P495 wd:{c} ."), ("citizen", f"?a wdt:P27 wd:{c} . ?p wdt:P170 ?a .")):
                key = f"{c}:{kind}"
                if key in zstate["done"]:
                    continue
                q = f"SELECT DISTINCT ?p WHERE {{ {pat} ?p wdt:P31 wd:Q3305213 ; wdt:P18 ?img . }} LIMIT {ZERO_LIMIT}"
                try:
                    got = [qid(b["p"]["value"]) for b in sparql(q)]
                except RuntimeError as e:
                    print(f"zero-pool {trad} {key}: FAILED {e}", flush=True)
                    continue
                print(f"zero-pool {trad} {key}: {len(got)}", flush=True)
                for g in got:
                    zstate["items"].setdefault(g, trad)
                zstate["done"].append(key)
                save_json(zpath, zstate)
    print("zero pool:", len(zstate["items"]))


if __name__ == "__main__":
    main()
