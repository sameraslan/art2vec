"""Every measured table in the README, and the ranked candidate list. Reads only files under data/.
Out: data/tables.md, candidates.csv"""
import csv, os, re, sys
import pandas as pd
from common import load, tradition, TRAD, eligible

df, refs, L = load()
out = []
def P(*a): out.append(" ".join(str(x) for x in a))
def md(t, index=False):
    t = t.reset_index() if index else t
    P("| " + " | ".join(map(str, t.columns)) + " |"); P("|" + "---|" * len(t.columns))
    for r in t.itertuples(index=False): P("| " + " | ".join("" if (isinstance(x, float) and pd.isna(x)) else str(x) for x in r) + " |")
    P("")
pct = lambda a, b: f"{100 * a / b:.1f}%"

# ---------------------------------------------------------------- pageviews
pv = pd.read_csv("data/pageviews.csv") if os.path.exists("data/pageviews.csv") else pd.DataFrame(columns=["qid", "wiki", "views60"])
pv = pv.drop_duplicates(["qid", "wiki"])
pvsum = pv.groupby("qid").views60.sum()
df["pv60"] = df.qid.map(pvsum).fillna(0).astype(int)
df["pv_en"] = df.qid.map(pv[pv.wiki == "en"].set_index("qid").views60).fillna(0).astype(int)

U = df[df.in_base].copy()                  # typed painting, a subclass, or a format / aggregate class
D = U[U.direct]
base = pd.read_csv("data/paintings_sitelinks.csv")

# ---------------------------------------------------------------- A. thresholds
P("## A. Sitelink thresholds\n")
hist = pd.read_csv("data/sitelink_histogram.csv")
P(f"Items with P31 = painting: {hist.n_items.sum():,} (QLever snapshot); with 0 sitelinks: {hist[hist.sitelinks == 0].n_items.sum():,}.\n")
rows = []
for t in (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 15, 20, 30, 40):
    rows.append({"sitelinks >=": t, "P31 = painting (raw, incl. Commons)": int((base[base.direct_p31 == 1].sitelinks >= t).sum()),
                 "+ subclasses and format classes (raw)": int((base.sitelinks >= t).sum()),
                 "Wikipedia editions only (all classes)": int((U.wp >= t).sum()) if t >= 2 else "n/a",
                 "clean score (all classes)": int((U.clean >= t).sum()) if t >= 2 else "n/a"})
md(pd.DataFrame(rows))

T10 = D[D.raw >= 3]; T25 = D[D.raw >= 8]
P(f"Reference sets used below: **T10k** = P31 painting with raw sitelinks >= 3 (n = {len(T10):,}); **T2.5k** = raw sitelinks >= 8 (n = {len(T25):,}).\n")

# ---------------------------------------------------------------- B. composition
def comp(T, name):
    n = len(T)
    P(f"### {name} (n = {n:,})\n")
    r = [("image (P18)", T.image.sum()), ("English Wikipedia article", T.enwiki.notna().sum()),
         ("creator (P170) stated", T.creator.notna().sum()), ("inception (P571)", T.inception.notna().sum()),
         ("collection (P195) or location (P276)", T.collection.notna().sum()),
         ("depicts (P180), at least one", (T.depicts > 0).sum()), ("height and width (P2048 + P2049)", T.has_dims.sum()),
         ("material (P186)", T.has_material.sum()), ("part of (P361) something", (T.part_of.map(len) > 0).sum()),
         ("in a series (P179)", (T.series.map(len) > 0).sum()), ("has parts (P527)", (T.has_parts > 0).sum()),
         ("has a Commons sitelink", T.sl.map(lambda s: "commonswiki" in s).sum()),
         ("has an Egyptian Arabic (arz) sitelink", T.sl.map(lambda s: "arzwiki" in s).sum()),
         ("has a Kotava (avk) sitelink", T.sl.map(lambda s: "avkwiki" in s).sum()),
         ("also typed as something that is not a flat painting", T.not_painting.sum())]
    md(pd.DataFrame([(a, int(b), pct(b, n)) for a, b in r], columns=["property", "items", "share"]))
    c = T.inception.dropna().map(lambda y: "before 1300" if y < 1300 else f"{int(y) // 100 + 1}th c." if y < 2001 else "21st c.")
    order = ["before 1300"] + [f"{k}th c." for k in range(14, 21)] + ["21st c."]
    vc = c.value_counts().reindex(order).fillna(0).astype(int)
    t = pd.DataFrame({"century of inception": list(vc.index) + ["no date"], "items": list(vc.values) + [n - len(c)]})
    t["share"] = t["items"].map(lambda x: pct(x, n)); md(t)
    vc = T.tradition.value_counts(); t = pd.DataFrame({"tradition (creator citizenship, else origin)": vc.index, "items": vc.values})
    t["share"] = t["items"].map(lambda x: pct(x, n)); md(t)
    vc = T.copyright.value_counts(); t = pd.DataFrame({"creator's death (copyright proxy)": vc.index, "items": vc.values})
    t["share"] = t["items"].map(lambda x: pct(x, n)); md(t)
    for col, title in (("collection_label", "collection"), ("creator_label", "creator")):
        vc = T[col].value_counts()
        t = pd.DataFrame({title: vc.index[:30], "items": vc.values[:30]}); t["share"] = t["items"].map(lambda x: pct(x, n))
        P(f"Top 30 by {title}: together {pct(vc.values[:30].sum(), n)} of the set; top 10 {pct(vc.values[:10].sum(), n)}; "
          f"{len(vc)} distinct; {int((vc >= 20).sum())} with 20 or more works; {int((vc >= 50).sum())} with 50 or more.\n")
        md(t)

P("## B. Composition of the top by raw sitelinks\n")
comp(T10, "T10k: raw sitelinks >= 3"); comp(T25, "T2.5k: raw sitelinks >= 8")

# ---------------------------------------------------------------- C. quirks
P("## C. Quirks\n")
wk = pd.Series([s for sl in T10.sl for s in sl]).value_counts()
P("Sitelinks in T10k by site, top 25: " + ", ".join(f"{k} {v:,}" for k, v in wk.head(25).items()) + "\n")
lost = T10[T10.clean < 3]
P(f"T10k items that fall below 3 once Commons, sister projects and the stub editions (arz, avk, ceb, war) are not counted: "
  f"**{len(lost):,} of {len(T10):,}** ({pct(len(lost), len(T10))}). Their top collections: "
  + ", ".join(f"{k} {v}" for k, v in lost.collection_label.value_counts().head(8).items())
  + ". Their top creators: " + ", ".join(f"{k} {v}" for k, v in lost.creator_label.value_counts().head(8).items()) + ".\n")
P(f"T10k items whose only Wikipedia editions are arz and/or avk: {int((T10.clean == 0).sum())}; with no Wikipedia edition at all (Commons only etc.): {int((T10.wp == 0).sum())}.\n")
allc = U[U.clean >= 3]
vc = pd.Series([c for cs in allc.p31 for c in cs]).map(L).value_counts()
P("P31 values among all candidates with clean score >= 3 (n = %d), top 40: " % len(allc) + ", ".join(f"{k} {v}" for k, v in vc.head(40).items()) + "\n")
uq = set(U.qid)
parent_in = U.part_of.map(lambda ps: any(p in uq for p in ps))
P(f"Candidates (clean >= 3) that are part of another candidate (a panel of a polyptych, a scene of a cycle, a version in a group): {int((parent_in & (U.clean >= 3)).sum())}; "
  f"items typed series / cycle / group: {int((allc.is_aggregate).sum())}, of which also typed painting {int((allc.is_aggregate & allc.direct).sum())}; "
  f"wall paintings (fresco, mural, cave, rock): {int(allc.in_situ.sum())}; flagged not-a-flat-painting: {int(allc.not_painting.sum())}.\n")
gtop = allc[allc.is_aggregate].sort_values("clean", ascending=False).head(20)
P("Best-known series / group items (clean score): " + "; ".join(f"{a} {b}" for a, b in zip(gtop.label, gtop.clean)) + "\n")

# ---------------------------------------------------------------- D. cleaner score
P("## D. Raw sitelinks against the clean score and against pageviews\n")
E, X, REP = eligible(df)      # universe rules + ranking by the clean score (common.eligible)
R = E.copy(); R["rank_clean"] = R["rank"]
Rr = R.sort_values(["raw", "pv60", "qid"], ascending=[False, False, True]).reset_index(drop=True)
R["rank_raw"] = R.qid.map(dict(zip(Rr.qid, Rr.index + 1)))
have_pv = R[R.score >= 3]
Rp = have_pv.sort_values(["pv60", "clean"], ascending=False).reset_index(drop=True)
R["rank_pv"] = R.qid.map(dict(zip(Rp.qid, Rp.index + 1)))
rows = []
for k in (500, 1000, 2500, 5000, 9000):
    a, b, c = set(R[R.rank_raw <= k].qid), set(R[R.rank_clean <= k].qid), set(R[R.rank_pv <= k].qid)
    rows.append({"top k": k, "raw vs clean: shared": len(a & b), "share": pct(len(a & b), k),
                 "clean vs pageviews: shared": len(b & c) if k <= len(Rp) else "n/a", "share ": pct(len(b & c), k) if k <= len(Rp) else "n/a"})
md(pd.DataFrame(rows))
sub = R[R.score >= 3]
P(f"Spearman rank correlation over candidates with clean >= 3 (n = {len(sub):,}): raw vs clean {sub.raw.corr(sub.clean, method='spearman'):.3f}; "
  f"clean vs 60-day pageviews in 12 editions {sub.clean.corr(sub.pv60, method='spearman'):.3f}; clean vs English pageviews alone {sub.clean.corr(sub.pv_en, method='spearman'):.3f}.\n")
P(f"Pageview coverage: {int((sub.pv60 > 0).sum()):,} of {len(sub):,} candidates have a view count in at least one of the 12 editions.\n")
top = R[R.rank_raw <= 2500]
mv = top.assign(drop=top.rank_clean - top.rank_raw).sort_values("drop", ascending=False).head(15)
P("Largest falls from the raw top 2,500 when the clean score is used:\n")
md(mv[["label", "creator_label", "raw", "clean", "rank_raw", "rank_clean"]])
hi = sub.sort_values("pv60", ascending=False).head(2500)
miss = hi[hi.rank_clean > 2500].sort_values("pv60", ascending=False).head(15)
P("Most-viewed works that the clean score leaves outside its top 2,500:\n")
md(miss[["label", "creator_label", "clean", "pv60", "rank_clean", "rank_pv"]])
lo = R[R.rank_clean <= 2500].sort_values("pv60").head(15)
P("Least-viewed works inside the clean top 2,500 (many editions, few readers):\n")
md(lo[["label", "creator_label", "clean", "pv60", "rank_clean"]])

# ---------------------------------------------------------------- E. overlap with independent lists
P("## E. Overlap with independent canon lists\n")
lists = pd.read_csv("data/lists.csv")
info = df.set_index("qid")
rk = R.set_index("qid")
rows = []
for name, g in lists.groupby("list"):
    q = {REP.get(x, x) for x in g.qid.unique()}      # a listed series is counted through its representative
    paint = [x for x in q if x in rk.index]
    n = len(paint)
    r_clean = [rk.loc[x, "rank_clean"] if x in rk.index else 10**9 for x in paint]
    r_raw = [rk.loc[x, "rank_raw"] if x in rk.index else 10**9 for x in paint]
    wp0 = sum(info.loc[x, "wp"] == 0 for x in paint)
    rows.append({"list": name, "QIDs": g.qid.nunique(), "of which eligible paintings": n,
                 "in raw top 2,500": sum(r <= 2500 for r in r_raw), "in raw top 10,000": sum(r <= 10000 for r in r_raw),
                 "in clean top 2,500": f"{sum(r <= 2500 for r in r_clean)} ({pct(sum(r <= 2500 for r in r_clean), max(n, 1))})",
                 "in clean top 10,000": f"{sum(r <= 10000 for r in r_clean)} ({pct(sum(r <= 10000 for r in r_clean), max(n, 1))})",
                 "no Wikipedia article anywhere": wp0,
                 "median clean score": int(pd.Series([info.loc[x, 'clean'] for x in paint]).median()) if n else ""})
md(pd.DataFrame(rows))
# what the lists have that the top 10,000 lacks
allp = set()
for name, g in lists.groupby("list"):
    if name in ("vital5", "1001paintings", "bbc100", "smarthistory", "ap250"):
        allp |= {REP.get(x, x) for x in g.qid.unique() if REP.get(x, x) in rk.index}
missing = [x for x in allp if x not in rk.index or rk.loc[x, "rank_clean"] > 10000]
P(f"Union of the five editorial lists (vital5, 1001paintings, bbc100, smarthistory, ap250): {len(allp)} distinct paintings; "
  f"{len(missing)} are outside the clean top 10,000. By tradition: "
  + ", ".join(f"{k} {v}" for k, v in info.loc[missing].tradition.value_counts().items()) + "\n")
P("Examples (first 25 by label): " + "; ".join(str(x) for x in info.loc[missing].label.dropna().sort_values().head(25)) + "\n")
cnt = rk.loc[sorted(allp)].n_editorial
P("Paintings named by k of the five editorial lists: " + ", ".join(f"k={k}: {v}" for k, v in cnt.value_counts().sort_index().items()) + "\n")

# ---------------------------------------------------------------- F. non-European coverage
P("## F. Non-European coverage\n")
Rn = R
trs = [t for t, _ in TRAD] + ["Indigenous / pre-Columbian", "Western Europe", "unknown"]
rows = []
for t in trs:
    g = Rn[Rn.tradition == t]
    rows.append({"tradition": t, "in clean top 2,500": int((g.rank_clean <= 2500).sum()), "clean >= 5": int((g.score >= 5).sum()),
                 "clean >= 3": int((g.score >= 3).sum()), "clean >= 2": int((g.score >= 2).sum()),
                 "clean >= 2 with image": int(((g.score >= 2) & g.image).sum()),
                 "clean >= 2, image, creator died before 1926 or anonymous pre-1850": int(((g.score >= 2) & g.image & g.copyright.isin(["died before 1926", "anonymous or undated creator, work before 1850"])).sum())})
md(pd.DataFrame(rows))
pool = pd.read_csv("data/pool_by_country.csv")
pool["tradition"] = pool.label.map(lambda l: tradition([l]))
P("Depth of the whole Wikidata pool (P31 = painting, any sitelink count), summed over the countries and states each tradition's regex matches. "
  "A work can be counted under two states of one tradition, so read these as upper bounds:\n")
t = pool.groupby(["tradition", "signal"])[["n_all", "n_with_image", "n_sitelinks_ge1"]].sum().reset_index()
md(t[t.tradition != "Western Europe"])

# ---------------------------------------------------------------- G. descriptions and facts (Part 3)
P("## G. Descriptions and facts for the clean top 2,500\n")
G = Rn.sort_values("rank_clean").head(2500)
n = len(G)
lead = pd.read_csv("data/lead_lengths.csv").drop_duplicates("qid").set_index("qid").lead_chars if os.path.exists("data/lead_lengths.csv") else pd.Series(dtype=float)
ll = G.qid.map(lead).fillna(G.represents_group.map(lead))   # a representative is described by its series' article
OPEN = {"Metropolitan Museum of Art": "Met (data CC0; label text has no stated open licence)", "Art Institute of Chicago": "AIC (description CC BY 4.0)",
        "Cleveland Museum of Art": "Cleveland (CC0)", "National Gallery of Art": "NGA Washington (CC0 open data)",
        "Rijksmuseum": "Rijksmuseum (CC0 / CC BY)", "National Gallery": "National Gallery London (text CC BY 4.0)",
        "Louvre Museum": "Louvre (Etalab open licence, French)", "Department of Paintings of the Louvre": "Louvre (Etalab open licence, French)",
        "J. Paul Getty Museum": "Getty (open content)", "Statens Museum for Kunst": "SMK (CC0)", "Nationalmuseum": "Nationalmuseum Sweden"}
mus = G.collection_label.map(OPEN)
r = [("English Wikipedia article exists", G.enwiki.notna().sum()),
     ("English lead paragraph of 200 characters or more", int((ll >= 200).sum())),
     ("English lead paragraph of 500 characters or more", int((ll >= 500).sum())),
     ("an article in at least one of en, es, fr, de, it, ru, ja, zh, pt, ar, ko, fa", int(G.titles.map(len).gt(0).sum())),
     ("held by a museum with an open API or dump that carries text", int(mus.notna().sum())),
     ("neither an English article nor such a museum", int((G.enwiki.isna() & mus.isna()).sum())),
     ("Wikidata: creator", G.creator.notna().sum()), ("Wikidata: inception", G.inception.notna().sum()),
     ("Wikidata: collection or location", G.collection.notna().sum()), ("Wikidata: material", G.has_material.sum()),
     ("Wikidata: height and width", G.has_dims.sum()), ("Wikidata: depicts", int((G.depicts > 0).sum())),
     ("Wikidata: image (P18)", G.image.sum()),
     ("Wikidata: creator + inception + collection + material + dimensions all present", int((G.creator.notna() & G.inception.notna() & G.collection.notna() & G.has_material & G.has_dims).sum()))]
md(pd.DataFrame([(a, int(b), pct(b, n)) for a, b in r], columns=["available", "works", "share of 2,500"]))
vc = mus.value_counts(); md(pd.DataFrame({"museum with open text": vc.index, "works in the top 2,500": vc.values}))

open("data/tables.md", "w").write("\n".join(out))
print("\n".join(out))
