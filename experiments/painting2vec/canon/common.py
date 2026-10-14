"""Load the fetched facts into one pandas frame with every derived column used by the tables and the recipe."""
import csv, json, re
import pandas as pd

NON_WP = {"commonswiki", "specieswiki", "metawiki", "wikidatawiki", "sourceswiki", "mediawikiwiki", "outreachwiki", "incubatorwiki"}
STUB_WIKIS = {"arzwiki", "avkwiki", "cebwiki", "warwiki"}   # machine-made stub editions (see README, quirks)
IN_SITU = {"Q22669139", "Q219423", "Q99516640", "Q214334", "Q1269827", "Q1181933", "Q29000611", "Q12370453"}
AGG = {"Q15727816", "Q16905563", "Q18573970"}               # series / cycle / group of paintings
FORMAT = {"Q79218", "Q1278452", "Q475476", "Q15711026", "Q11801536", "Q741226", "Q1144689"}
# P31 values that mean "this item is not one flat painting" when they sit beside (or instead of) painting
NOT_PAINTING = re.compile(r"archaeological site|sculpture|statue|carving|museum|^human$|church|chapel|basilica|mosque|temple|tomb|"
                          r"cathedral|building|ruins|cave with|installation|religious ceramic|cyclorama|rotunda|monument|collage|"
                          r"print$|^drawing$|photograph|tapestry|mosaic|stained|manuscript$|book|film|album|sarcophagus|vase|pottery|"
                          r"model railroad|miniature park|relic|veil|Wikimedia list|garden|palace|villa|monastery|castle|"
                          r"exhibition|event|genre|art movement", re.I)

TRAD = [  # (tradition, regex over a country / state / culture label), first match wins
    ("China", r"China|Chinese|dynasty|Southern Tang|Taiwan|Hong Kong|Liao|Northern Wei|Tibet"),
    ("Japan", r"Japan|Tokugawa|shogunate|Ryukyu"),
    ("Korea", r"Korea|Joseon|Goryeo|Silla|Goguryeo|Baekje"),
    ("South Asia", r"India|Mughal|British Raj|Thiruvithamkoor|Travancore|Pakistan|Bangladesh|Sri Lanka|Nepal|Rajput|Mewar|Sikh|Bengal|Mysore|Maratha|Deccan"),
    ("Persia / Iran / Central Asia", r"Iran|Persia|Safavid|Qajar|Timurid|Afghan|Uzbek|Ilkhan|Sasanian|Pahlavi|Zand"),
    ("Ottoman / Turkey", r"Ottoman|Turkey|Turkish"),
    ("Arab world", r"Egypt(?!.*Ancient)|Iraq|Syria|Lebanon|Morocco|Algeria|Tunisia|Saudi|Palestin|Jordan|Abbasid|Mamluk|Kuwait|Sudan|Libya|Yemen|Emirates"),
    ("Sub-Saharan Africa", r"Nigeria|South Africa|Ethiopia|Ghana|Senegal|Congo|Kenya|Tanzania|Mali|Zimbabwe|Uganda|Mozambique|Angola|Benin|Cameroon|Ivory|Côte|Namibia|Botswana|Zambia"),
    ("Southeast Asia", r"Philippines|Indonesia|Dutch East Indies|Vietnam|Thailand|Siam|Malaysia|Singapore|Cambodia|Myanmar|Burma|Laos"),
    ("Latin America", r"Mexico|Brazil|Cuba|Chile|Peru|Argentina|Colombia|Uruguay|Venezuela|Ecuador|Bolivia|Guatemala|New Spain|Haiti|Puerto Rico|Paraguay|Dominican|Nicaragua|Costa Rica|Honduras|Panama|Salvador"),
    ("Ancient / Byzantine", r"Ancient|Classical Athens|^Roman Empire$|Roman Republic|Byzantine|Minoan|Etrus|Pompeii|ancient"),
    ("Russia / Eastern Europe", r"Russia|Soviet|Poland|Ukrain|Czech|Hungary|Romania|Serbia|Bulgaria|Lithuania|Latvia|Estonia|Moscow|Croatia|Sloven|Slovak|Belarus|Georgia$|Armenia|Yugoslav|Bohemia|Moldova|Albania|Montenegro|Macedonia|Bosnia|Novgorod|Polish"),
    ("North America (US/Canada)", r"United States|Canada|Thirteen Colonies|Confederate"),
    ("Oceania (settler)", r"Australia|New Zealand"),
]
INDIG = re.compile(r"Aboriginal|Indigenous|Native American|First Nations|Inuit|Maya|Aztec|Inca|Navajo|Hopi|Māori|Maori|Torres Strait|Mixtec|Moche|Nazca|Olmec|Teotihuac|Haida|Cree|Lakota|Cherokee|Anishinaabe|Pueblo|San people|Yolngu|Pre-Columbian", re.I)


def tradition(labels):
    """Majority vote over one source's labels; unmatched but labelled values vote 'Western Europe'."""
    votes = []
    for lab in labels:
        if not lab or re.fullmatch(r"Q\d+", lab): continue
        for name, rx in TRAD:
            if re.search(rx, lab):
                votes.append(name); break
        else:
            votes.append("Western Europe")
    if not votes: return None
    return max(dict.fromkeys(votes), key=votes.count)   # mode, first-listed wins ties


def year(t):
    m = re.match(r"([+-])(\d+)-", t or "")
    return (int(m.group(2)) * (1 if m.group(1) == "+" else -1)) if m else None


def load():
    refs = {}
    for l in open("data/refs.jsonl"):
        d = json.loads(l); refs[d["id"]] = d
    L = lambda q: (refs.get(q, {}).get("label") or q)
    base = {r["qid"]: r for r in csv.DictReader(open("data/paintings_sitelinks.csv"))}
    rows, seen = [], set()
    for l in open("data/items.jsonl"):
        d = json.loads(l)
        if d["id"] in seen: continue
        seen.add(d["id"])
        sl = d.get("sl", [])
        wp = [s for s in sl if s.endswith("wiki") and s not in NON_WP]
        p31 = d.get("P31", [])
        cr = (d.get("P170") or [None])[0]
        c = refs.get(cr, {}) if cr else {}
        cb, cd = year((c.get("P569") or [None])[0]), year((c.get("P570") or [None])[0])
        inc = year((d.get("P571") or [None])[0])
        is_human = "Q5" in c.get("P31", [])
        insitu = bool(set(p31) & IN_SITU)
        sources = [[L(x) for x in c.get("P27", [])], [L(x) for x in d.get("P495", [])],
                   [L(x) for x in d.get("P2596", [])],
                   [L(x) for bp in c.get("P19", []) for x in refs.get(bp, {}).get("P17", [])[:1]]]
        if insitu or not cr:
            sources.append([L(x) for x in d.get("P17", [])])
        indig = any(INDIG.search(x or "") for x in [L(x) for x in d.get("P2596", [])] + [L(x) for x in c.get("P172", [])] + [L(x) for x in d.get("P135", [])])
        tr = "Indigenous / pre-Columbian" if indig else next((t for t in map(tradition, sources) if t), "unknown")
        # copyright proxy from the creator's death year
        if cd is not None:
            cp = "died before 1926" if cd < 1926 else ("died 1926-1955" if cd <= 1955 else "died after 1955")
        elif cb is not None and cb >= 1920: cp = "living (no death date, born 1920+)"
        elif cb is not None: cp = "died before 1926" if cb < 1830 else "unknown"
        elif inc is not None and inc < 1850: cp = "anonymous or undated creator, work before 1850"
        else: cp = "unknown"
        other = [L(x) for x in p31 if x != "Q3305213"]
        rows.append(dict(
            qid=d["id"], label=d.get("label"), desc=d.get("desc"), raw=len(sl), wp=len(wp),
            clean=len([s for s in wp if s not in STUB_WIKIS]), sl=sl,
            direct="Q3305213" in p31, p31=p31, p31_other="|".join(other),
            in_situ=insitu, is_aggregate=bool(set(p31) & AGG), format_class=bool(set(p31) & FORMAT),
            not_painting=any(NOT_PAINTING.search(o) for o in other) and not insitu and "Q18761202" not in p31,
            creator=cr, creator_label=L(cr) if cr else None, creator_human=is_human, creator_death=cd, creator_birth=cb,
            n_creators=len(d.get("P170", [])), inception=inc, tradition=tr, copyright=cp,
            collection=(d.get("P195") or d.get("P276") or [None])[0],
            image="P18" in d, enwiki=d.get("en"), titles=d.get("titles", {}),
            depicts=len(d.get("P180", [])), has_dims=("P2048" in d and "P2049" in d), has_material="P186" in d,
            part_of=d.get("P361", []), parts=d.get("P527", []), series=d.get("P179", []), has_parts=len(d.get("P527", [])),
            genre="|".join(L(x) for x in d.get("P136", [])), copyright_status="|".join(L(x) for x in d.get("P6216", [])),
            in_base=d["id"] in base))
    df = pd.DataFrame(rows)
    df["collection_label"] = df.collection.map(lambda q: L(q) if q else None)
    return df, refs, L


ED = ["vital5", "1001paintings", "bbc100", "smarthistory", "ap250"]      # editorial canons
MUS = ["met_highlight", "aic_boosted", "cma_highlight"]                  # museum-declared highlights
STATE = ["jp_national_treasure"]                                         # state designations


def eligible(df):
    """The universe rules and the ranking, in one place.
    Returns (E, X, rep): E = eligible works with `score` and `rank`; X = every fetched painting-like item with an
    `excluded` reason; rep = {group or replaced qid -> the qid that stands for it}."""
    import os
    pv = pd.read_csv("data/pageviews.csv").drop_duplicates(["qid", "wiki"]) if os.path.exists("data/pageviews.csv") else pd.DataFrame(columns=["qid", "wiki", "views60"])
    df = df.copy()
    df["pv60"] = df.qid.map(pv.groupby("qid").views60.sum()).fillna(0).astype(int)
    df["pv_en"] = df.qid.map(pv[pv.wiki == "en"].set_index("qid").views60).fillna(0).astype(int)
    lists = pd.read_csv("data/lists.csv")
    lmap = lists.groupby("qid").list.agg(lambda s: set(s)).to_dict()
    X = df[df.direct | df.in_base | df.in_situ | df.format_class].copy()
    X["is_group"] = X.is_aggregate & ~X.format_class          # a polyptych typed 'cycle' is still one object
    X["lists_set"] = X.qid.map(lambda q: set(lmap.get(q, set())))
    X["score"] = X.clean
    X["represents_group"] = ""
    X["excluded"] = ""
    whole = set(X[X.format_class & ~X.not_painting].qid)
    X.loc[X.part_of.map(lambda ps: any(p in whole for p in ps)), "excluded"] = "panel of a polyptych that is itself a candidate"
    X.loc[X.is_group, "excluded"] = "series / cycle / group item"
    X.loc[X.not_painting, "excluded"] = "typed as something that is not one flat painting"
    X = X.set_index("qid", drop=False)
    ok = set(X[X.excluded == ""].qid)
    gm = pd.read_csv("data/group_members.csv")
    members = gm[gm.member.isin(ok)].groupby("group").member.agg(list).to_dict()
    rep = {}
    for g in X[X.is_group & ~X.not_painting].sort_values("clean", ascending=False).qid:
        ms = members.get(g, [])
        if re.search(r"^(paintings by|list of|works by)|\bperiod\b|Wikimedia list", f"{X.at[g, 'label']}|{X.at[g, 'p31_other']}", re.I):
            continue          # an oeuvre or a period is not a series: nothing stands for it
        if ms:   # the best-known member stands for the group and carries the group's score
            m = X.loc[ms].sort_values(["clean", "pv60", "inception"], ascending=[False, False, True]).qid.iloc[0]
            if X.at[g, "clean"] > X.at[m, "score"]:
                X.at[m, "score"] = X.at[g, "clean"]; X.at[m, "represents_group"] = g
                X.at[m, "pv60"] = max(X.at[m, "pv60"], X.at[g, "pv60"])
            X.at[m, "lists_set"] = X.at[m, "lists_set"] | X.at[g, "lists_set"]
            if not isinstance(X.at[m, "enwiki"], str) and isinstance(X.at[g, "enwiki"], str):
                X.at[m, "enwiki"] = X.at[g, "enwiki"]; X.at[m, "titles"] = X.at[g, "titles"]   # the article is about the series
            rep[g] = m
        elif X.at[g, "direct"]:   # typed painting AND group, with no member item: keep it, flagged
            X.at[g, "excluded"] = ""; X.at[g, "represents_group"] = "unresolved: pick a version by hand"
    for name, group in (("n_editorial", ED), ("n_museum", MUS), ("n_state", STATE)):
        X[name] = X.lists_set.map(lambda s: len(s & set(group)))
    X["lists"] = X.lists_set.map(lambda s: "|".join(sorted(s)))
    E = X[X.excluded == ""].copy()
    E["qnum"] = E.qid.str[1:].astype(int)
    E = E.sort_values(["score", "pv60", "raw", "qnum"], ascending=[False, False, False, True]).reset_index(drop=True)
    E["rank"] = E.index + 1
    return E, X.reset_index(drop=True), rep
