"""Step 6: versions and copies. Pairs of DIFFERENT physical paintings (separate Wikidata items) that
share a composition.

Three sources of pairs:
  based_on_P144 / derivative_P4969   Wikidata says painting A is based on painting B. Kept only when both
      pass the pilot PD rule, both Commons files are PD/CC0 and the aspect ratios agree to within
      ASPECT_TOL (a loose "after X" that changes the format is not a copy of the composition).
  version   a curated list of compositions a painter (or workshop) repeated, found by Wikidata search.
  series_motif   Monet's series: the same motif from (nearly) the same spot, not a strict repeat.
Curated groups become star pairs: the most-linked member against each other member.
Curated groups only require that Commons marks the file public domain; the strict pilot PD rule is
recorded per painting in meta.csv (pd_basis is empty where it fails, e.g. Munch, d. 1944).
"""
import hashlib
import math
import re
import sys
from collections import Counter

import pandas as pd

from common import CACHE, DATA, HERE, WD_API, get, lab_diff, load_json, qid, save_json, sparql
from commons import info, is_open
from meta import build
from wd import PAINTING, fetch_creators, fetch_paintings, pd_basis

OUT = DATA / "versions"
ASPECT_TOL = 0.22       # |ln(aspect_a / aspect_b)|
N_P144 = 110            # cap on Wikidata-derived pairs
PER_TARGET = 3          # at most this many copies of one original
GROUP_CAP = 6

# (group, search text, title regex, creator regex, relation)
CURATED = [
    ("vangogh_sunflowers", "Sunflowers van Gogh vase", r"^sunflowers|vase with .*sunflowers", r"van gogh", "version"),
    ("munch_scream", "The Scream Munch", r"^(the )?scream", r"munch", "version"),
    ("leonardo_virgin_rocks", "Virgin of the Rocks", r"virgin of the rocks", r"", "version"),
    ("vangogh_bedroom", "Bedroom in Arles", r"bedroom", r"van gogh", "version"),
    ("vangogh_arlesienne", "L'Arlésienne van Gogh", r"arl[eé]sienne", r"van gogh", "version"),
    ("vangogh_berceuse", "La Berceuse van Gogh", r"berceuse", r"van gogh", "version"),
    ("vangogh_gachet", "Portrait of Dr. Gachet", r"gachet", r"van gogh", "version"),
    ("vangogh_wheatfield_cypresses", "Wheat Field with Cypresses", r"wheat ?field with cypresses", r"van gogh", "version"),
    ("bocklin_isle_dead", "Isle of the Dead Böcklin", r"isle of the dead", r"b[oö]cklin", "version"),
    ("david_napoleon_alps", "Napoleon Crossing the Alps", r"napoleon crossing the alps|bonaparte crossing", r"david", "version"),
    ("cezanne_card_players", "The Card Players Cézanne", r"card players", r"c[eé]zanne", "version"),
    ("manet_maximilian", "Execution of Emperor Maximilian Manet", r"execution of (the )?emperor maximilian", r"manet", "version"),
    ("elgreco_temple", "El Greco Purification of the Temple", r"temple|money ?changers", r"greco", "version"),
    ("elgreco_disrobing", "Disrobing of Christ El Greco", r"disrobing", r"greco", "version"),
    ("hicks_peaceable", "Peaceable Kingdom Hicks", r"peaceable kingdom", r"hicks", "series_motif"),
    ("caravaggio_lizard", "Boy Bitten by a Lizard", r"bitten by a lizard", r"caravaggio", "version"),
    ("caravaggio_fortune_teller", "The Fortune Teller Caravaggio", r"fortune teller", r"caravaggio", "version"),
    ("caravaggio_lute", "The Lute Player Caravaggio", r"lute player", r"caravaggio", "version"),
    ("munch_madonna", "Madonna Munch", r"^madonna", r"munch", "version"),
    ("munch_sick_child", "The Sick Child Munch", r"sick child", r"munch", "version"),
    ("munch_vampire", "Vampire Munch", r"vampire|love and pain", r"munch", "version"),
    ("gentileschi_judith", "Judith Slaying Holofernes Gentileschi", r"judith (slaying|beheading)", r"gentileschi", "version"),
    ("chardin_soap_bubbles", "Soap Bubbles Chardin", r"soap bubbles", r"chardin", "version"),
    ("renoir_girls_piano", "Girls at the Piano Renoir", r"girls at the piano", r"renoir", "version"),
    ("titian_danae", "Danaë Titian", r"dana[eë]", r"titian", "version"),
    ("titian_venus_adonis", "Venus and Adonis Titian", r"venus and adonis", r"titian", "version"),
    ("titian_magdalene", "Penitent Magdalene Titian", r"magdalene", r"titian", "version"),
    ("leonardo_yarnwinder", "Madonna of the Yarnwinder", r"yarnwinder", r"", "version"),
    ("fuseli_nightmare", "The Nightmare Fuseli", r"nightmare", r"f[uü]ss?e?li", "version"),
    ("hunt_light_world", "The Light of the World Holman Hunt", r"light of the world", r"hunt", "version"),
    ("rossetti_proserpine", "Proserpine Rossetti", r"proserpine", r"rossetti", "version"),
    ("rossetti_beata", "Beata Beatrix Rossetti", r"beata beatrix", r"rossetti", "version"),
    ("friedrich_moon", "Contemplating the Moon Friedrich", r"contemplating the moon", r"friedrich", "version"),
    ("leutze_delaware", "Washington Crossing the Delaware", r"washington crossing the delaware", r"", "version"),
    ("constable_salisbury", "Salisbury Cathedral from the Bishop's Constable", r"salisbury cathedral from the bishop", r"constable", "version"),
    ("monet_haystacks", "Haystacks Monet", r"haystacks?|grainstacks?|wheatstacks?|stacks? of wheat|meules", r"monet", "series_motif"),
    ("monet_rouen", "Rouen Cathedral Monet", r"rouen cathedral", r"monet", "series_motif"),
    ("monet_parliament", "Houses of Parliament Monet", r"parliament", r"monet", "series_motif"),
    ("monet_poplars", "Poplars Monet", r"poplars", r"monet", "series_motif"),
    ("monet_charing_cross", "Charing Cross Bridge Monet", r"charing cross", r"monet", "series_motif"),
    ("monet_waterloo", "Waterloo Bridge Monet", r"waterloo bridge", r"monet", "series_motif"),
]
# ---- Review by eye (8 Oct 2026): every pair this script produced was looked at on contact sheets
# (07_contact_sheets.py versions). The tables below record the verdicts; anything not listed was judged
# to share its composition ("yes"). A rerun that produces a pair never reviewed marks it "unreviewed".
# Curated-group members that turned out to be a different composition, a study or another subject:
EXCLUDE = {
    "Q11770758",  # Van Gogh, vase with five sunflowers on blue: a different arrangement
    "Q64566887",  # Cezanne, study of a single card player
    "Q18891477",  # Munch, "Inheritance", not The Sick Child
    "Q15974339",  # Titian, the Pitti Magdalene: a different type from the Hermitage one
    "Q66286852", "Q64787476", "Q59782358",  # "Yarnwinder" items that are loose variants or another subject
    "Q3696343",   # Monet, poppy field with a haystack: not the stack motif
}
# Star pairs to drop because the hub is one composition and these members are another ...
PAIR_DROP = {frozenset(p) for p in [
    ("Q17519173", "Q17519174"), ("Q17519173", "Q17519249"), ("Q17519173", "Q17519255"),  # L'Arlesienne 1888 vs 1890 type
    ("Q1165042", "Q19911459"), ("Q1165042", "Q28126478"),                                # Card Players, 2 vs 4/5 figures
]}
# ... and the pairs among those members instead.
EXTRA = [
    ("Q17519174", "Q17519249", "version", "group=vangogh_arlesienne_1890"),
    ("Q17519174", "Q17519255", "version", "group=vangogh_arlesienne_1890"),
    ("Q19911459", "Q28126478", "version", "group=cezanne_card_players_multi"),
]
# Wikidata "based on" pairs that do NOT share a composition (loose homage, a detail, a study, another subject):
NO = {frozenset(p) for p in [
    ("Q1215604", "Q3498655"), ("Q3829346", "Q2308934"), ("Q7934007", "Q838074"), ("Q2909905", "Q1282978"),
    ("Q2909911", "Q2909905"), ("Q2290433", "Q5689366"), ("Q21406179", "Q4684623"), ("Q21606382", "Q2308934"),
    ("Q18118034", "Q880502"), ("Q18577992", "Q544488"), ("Q21372308", "Q21808563"), ("Q24283961", "Q56614340"),
    ("Q3937479", "Q3937482"), ("Q29016129", "Q3842443"), ("Q21899402", "Q3944474"), ("Q28035502", "Q1112863"),
    ("Q3698216", "Q3698209"), ("Q18749431", "Q21716705"), ("Q73128765", "Q9396824"), ("Q3820951", "Q12122363"),
    ("Q21607747", "Q19904878"), ("Q3937462", "Q3937461"), ("Q52083876", "Q20031614"), ("Q104371537", "Q636537"),
    ("Q521680", "Q427390"),
]}
# Pairs that share the composition with visible changes (figures added or dropped, format changed, a
# reworked variant, one member shown in its frame or unfinished):
VARIANT = {frozenset(p) for p in [
    ("Q580853", "Q1055111"), ("Q10296499", "Q24090"), ("Q3627380", "Q3627381"), ("Q19890804", "Q3701418"),
    ("Q29021053", "Q3769173"), ("Q29021098", "Q3769173"), ("Q7448169", "Q2872711"), ("Q27698013", "Q7920622"),
    ("Q49878096", "Q3464081"), ("Q16908837", "Q16954398"), ("Q20801666", "Q20801653"), ("Q17813694", "Q20767567"),
    ("Q27996276", "Q21685592"), ("Q13571543", "Q2270768"), ("Q47414451", "Q28796116"), ("Q62399736", "Q7718578"),
    ("Q19904792", "Q1113824"), ("Q29018356", "Q3978273"), ("Q18414562", "Q72554025"), ("Q11750094", "Q600033"),
    ("Q52212991", "Q52213499"), ("Q29855481", "Q19008597"), ("Q22329820", "Q22329818"), ("Q3842398", "Q106262020"),
    ("Q19911412", "Q50811851"), ("Q78163101", "Q123267361"), ("Q137125540", "Q1892745"), ("Q17885557", "Q661378"),
    ("Q105296832", "Q563727"),
    ("Q1683743", "Q18891339"), ("Q26756023", "Q26493276"), ("Q2712679", "Q58018788"),  # curated: Vampire in the forest, Maximilian fragments, framed Beata Beatrix
]}
REVIEWED = load_json(HERE / "versions_reviewed.json", [])  # every pair that was on the sheets, as sorted [a, b]
SAME_FILE = 1.0  # lab_diff under this: two Wikidata items illustrated with the same photograph


def h(q):
    return hashlib.md5(q.encode()).hexdigest()


def search(text):
    r = get(WD_API, params={"action": "query", "list": "search", "srnamespace": 0, "srlimit": 50, "format": "json",
                            "srsearch": f"haswbstatement:P31={PAINTING} {text}"}, pause=0.5)
    return [x["title"] for x in r.json().get("query", {}).get("search", [])] if r is not None else []


def wikidata_pairs():
    path = CACHE / "version_wd_pairs.json"
    got = load_json(path)
    if got is None:
        got = []
        for prop, rel, a, b in (("P144", "based_on_P144", "?a", "?b"), ("P4969", "derivative_P4969", "?b", "?a")):
            q = (f"SELECT DISTINCT ?a ?b WHERE {{ {a} wdt:{prop} {b} . ?a wdt:P31 wd:{PAINTING} ; wdt:P18 ?ia . "
                 f"?b wdt:P31 wd:{PAINTING} ; wdt:P18 ?ib . }} LIMIT 6000")
            rows = sparql(q)
            print(rel, len(rows), flush=True)
            got += [[qid(r["a"]["value"]), qid(r["b"]["value"]), rel] for r in rows]  # a = the later work, b = its model
        save_json(path, got)
    return got


def main():
    gpath = CACHE / "version_groups.json"
    groups = load_json(gpath, {})
    for name, text, *_ in CURATED:
        if name not in groups:
            groups[name] = search(text)
            save_json(gpath, groups)
    wd_pairs = [p for p in wikidata_pairs() if p[0] != p[1]]
    all_q = sorted({q for g in groups.values() for q in g} | {q for a, b, _ in wd_pairs for q in (a, b)})
    P = fetch_paintings(all_q)
    C = fetch_creators([a for q in all_q if P.get(q) for a in P[q]["P170"]])
    recs = info([P[q]["P18"][0] for q in all_q if P.get(q) and P[q]["P18"]])

    def rec(q):
        p = P.get(q)
        return recs.get(p["P18"][0]) if p and p["P18"] else None

    def creators(q):
        return " ".join(C[a]["label"] for a in P[q]["P170"] if C.get(a)).lower()

    def usable(q):
        r = rec(q)
        return bool(P.get(q) and PAINTING in P[q]["P31"] and r and r.get("thumburl") and is_open(r)
                    and max(r["w"], r["h"]) >= 600)

    def aspect_gap(a, b):
        ra, rb = rec(a), rec(b)
        return abs(math.log((ra["w"] / ra["h"]) / (rb["w"] / rb["h"])))

    pairs, seen = [], set()

    def add(a, b, rel, note):
        k = frozenset((a, b))
        if a != b and k not in seen:
            seen.add(k)
            pairs.append({"qid_a": a, "qid_b": b, "relation": rel, "note": note})

    for name, text, title_re, creator_re, rel in CURATED:
        mem = [q for q in groups[name] if usable(q) and re.search(title_re, P[q]["label"], re.I)
               and (not creator_re or re.search(creator_re, creators(q)))]
        mem = sorted(mem, key=lambda q: (-P[q]["wp_sitelinks"], h(q)))
        hub = mem[0] if mem else None
        mem = [hub] + [q for q in mem[1:] if aspect_gap(hub, q) <= ASPECT_TOL][:GROUP_CAP - 1] if hub else []
        mem = [q for q in mem if q not in EXCLUDE]  # after the cap, so an exclusion never pulls in an unreviewed member
        print(f"{name}: {len(mem)} | " + "; ".join(f"{q} {P[q]['label'][:38]}" for q in mem), flush=True)
        for q in mem[1:]:
            if frozenset((hub, q)) not in PAIR_DROP:
                add(hub, q, rel, f"group={name}")
    for a, b, rel, note in EXTRA:
        if usable(a) and usable(b):
            add(a, b, rel, note)

    cand, per_target, drop = [], Counter(), Counter()
    for a, b, rel in wd_pairs:
        if not (usable(a) and usable(b)):
            drop["image_missing_or_not_pd_cc0"] += 1
        elif not (pd_basis(P[a], C) and pd_basis(P[b], C)):
            drop["fails_pilot_pd_rule"] += 1
        elif aspect_gap(a, b) > ASPECT_TOL:
            drop["aspect_ratio_differs"] += 1
        else:
            cand.append((a, b, rel))
    cand.sort(key=lambda t: (-min(P[t[0]]["wp_sitelinks"], P[t[1]]["wp_sitelinks"]),
                             -max(P[t[0]]["wp_sitelinks"], P[t[1]]["wp_sitelinks"]), h(t[0] + t[1])))
    n = 0
    for a, b, rel in cand:
        if n >= N_P144 or per_target[b] >= PER_TARGET:
            continue
        same = bool(set(P[a]["P170"]) & set(P[b]["P170"]) - {"UNKNOWN"})
        before = len(pairs)
        add(a, b, rel, "same_creator" if same else "different_creator")
        if len(pairs) > before:
            per_target[b] += 1
            n += 1
    print("wikidata pairs: found", len(wd_pairs), "usable", len(cand), "taken", n, "dropped", dict(drop), flush=True)

    qids = sorted({q for p in pairs for q in (p["qid_a"], p["qid_b"])}, key=h)
    rows = build([{"qid": q, "stratum": "versions"} for q in qids], OUT / "images",
                 [OUT / "meta.csv", HERE / "versions_meta.csv"], require_open=True,
                 link_from=DATA / "pilot" / "images")
    have = {r["qid"] for r in rows}
    for f in (OUT / "images").glob("*.jpg"):  # images left by an earlier run whose painting is in no pair now
        if f.stem not in have:
            f.unlink()
    final, rejected = [], []
    reviewed = {frozenset(x) for x in REVIEWED}
    for p in pairs:
        if not (p["qid_a"] in have and p["qid_b"] in have):
            continue
        k = frozenset((p["qid_a"], p["qid_b"]))
        d = lab_diff(OUT / "images" / f"{p['qid_a']}.jpg", OUT / "images" / f"{p['qid_b']}.jpg")
        p["lab_diff"] = round(d, 2)
        p["note"] += f"; a={P[p['qid_a']]['label'][:60]}; b={P[p['qid_b']]['label'][:60]}"
        p["composition_match"] = ("same_image_file" if d < SAME_FILE else "no" if k in NO else
                                  "variant" if k in VARIANT or p["relation"] == "series_motif" else
                                  "yes" if (k in reviewed or not reviewed) else "unreviewed")
        (rejected if p["composition_match"] in ("no", "same_image_file") else final).append(p)
    if "--mark-reviewed" in sys.argv:  # run once, after looking at every pair on the contact sheets
        save_json(HERE / "versions_reviewed.json", sorted(sorted((p["qid_a"], p["qid_b"])) for p in final + rejected))
    cols = ["qid_a", "qid_b", "relation", "note", "composition_match", "lab_diff"]
    for path in (OUT / "version_pairs.csv", HERE / "version_pairs.csv"):
        pd.DataFrame(final, columns=cols).to_csv(path, index=False)
    pd.DataFrame(rejected, columns=cols).to_csv(OUT / "version_pairs_rejected.csv", index=False)
    print("pairs written:", len(final), dict(Counter(p["relation"] for p in final)),
          dict(Counter(p["composition_match"] for p in final)), "| rejected:", len(rejected),
          dict(Counter(p["composition_match"] for p in rejected)), "| paintings downloaded:", len(have))
    used = {q for p in final for q in (p["qid_a"], p["qid_b"])}
    print("paintings in kept pairs:", len(used))


if __name__ == "__main__":
    main()
