"""Apply the recommended recipe and write the ranked candidate list.
Out: candidates.csv, data/recipe_tables.md.   Usage: python 07_recipe.py [snapshot-date]"""
import os, sys
import pandas as pd
from common import load, eligible, ED, MUS, STATE

SNAP = sys.argv[1] if len(sys.argv) > 1 else "2026-10-08"
MAJORITY = {"Western Europe", "Russia / Eastern Europe", "North America (US/Canada)", "Oceania (settler)", "unknown", "Ancient / Byzantine"}
PD = ["died before 1926", "anonymous or undated creator, work before 1850"]
CANON = dict(min_clean=3, cap=40)
POC = dict(min_clean=6, cap=12, floor={"China": 60, "Japan": 60}, floor_default=30)

df, refs, L = load()
out = []
def P(*a): out.append(" ".join(str(x) for x in a))
def md(t):
    P("| " + " | ".join(map(str, t.columns)) + " |"); P("|" + "---|" * len(t.columns))
    for r in t.itertuples(index=False): P("| " + " | ".join(str(x) for x in r) + " |")
    P("")

E, X, REP = eligible(df)          # universe rules, series representatives, ranking (common.eligible)
E["under"] = ~E.tradition.isin(MAJORITY)
E["listed"] = (E.n_editorial + E.n_museum + E.n_state) > 0

def apply_cap(S, cap):
    """Keep at most `cap` works per named painter: works on an editorial list first, then by rank."""
    S = S.sort_values(["n_editorial", "rank"], ascending=[False, True])
    named = S.creator_human & S.creator.notna()
    pos = S[named].groupby("creator").cumcount()
    keep = pd.Series(True, index=S.index); keep.loc[pos.index] = pos < cap
    return keep.reindex(S.index)

def build(min_clean, cap, floor=None, floor_default=None, museum_everywhere=True):
    gate = pd.Series("", index=E.index)
    gate[E.score >= min_clean] = "fame"
    gate[(gate == "") & (E.n_editorial > 0)] = "editorial list"
    if museum_everywhere:
        gate[(gate == "") & ((E.n_museum > 0) | (E.n_state > 0))] = "museum highlight / state designation"
    keep = apply_cap(E[gate != ""], cap).reindex(E.index).fillna(False)
    if floor is None:      # canon: every work of an under-represented tradition with any Wikipedia article or any listing
        fl = E.under & (gate == "") & ((E.score >= 1) | E.listed)
        gate[fl] = "tradition floor"
        keep2 = apply_cap(E[gate != ""], cap).reindex(E.index).fillna(False)
        keep = keep2
    else:                  # POC: top-N per under-represented tradition by (listed, rank), wherever they sit
        for t, g in E[E.under & ((E.score >= 1) | E.listed)].groupby("tradition"):
            n = floor.get(t, floor_default)
            g = g.assign(_l=g.listed.astype(int)).sort_values(["score", "_l", "rank"], ascending=[False, False, True])
            g = g[apply_cap(g, cap).reindex(g.index)]
            pick = g.head(n).index
            gate[[i for i in pick if gate[i] == ""]] = "tradition floor"
            keep[pick] = True
    return gate, (gate != "") & keep

E["gate_canon"], E["in_canon"] = build(CANON["min_clean"], CANON["cap"])
E["gate_poc"], E["in_poc"] = build(POC["min_clean"], POC["cap"], POC["floor"], POC["floor_default"], museum_everywhere=False)
# the POC's editorial gate is narrower: on a list AND clean >= 3
drop = E.in_poc & (E.gate_poc == "editorial list") & (E.score < 3)
E.loc[drop, "in_poc"] = False
E["capped_out_canon"] = (E.gate_canon != "") & ~E.in_canon
E["pd_proxy"] = E.copyright.isin(PD)

def describe(S, name):
    n = len(S)
    P(f"### {name}: {n:,} works\n")
    r = [("by gate: " + k, v) for k, v in S["gate_poc" if name.startswith("POC") else "gate_canon"].value_counts().items()]
    r += [("has an image on Commons (P18)", int(S.image.sum())),
          ("image and creator died before 1926 or anonymous pre-1850 (public-domain proxy)", int((S.image & S.pd_proxy).sum())),
          ("creator died 1926-1955", int((S.copyright == "died 1926-1955").sum())),
          ("creator died after 1955 or living", int(S.copyright.isin(["died after 1955", "living (no death date, born 1920+)"]).sum())),
          ("copyright proxy unknown", int((S.copyright == "unknown").sum())),
          ("English Wikipedia article", int(S.enwiki.notna().sum())), ("no Wikipedia article in any language", int((S.wp == 0).sum())),
          ("wall paintings (fresco, mural, cave)", int(S.in_situ.sum())),
          ("under-represented traditions", int(S.under.sum())), ("distinct named painters", int(S[S.creator_human].creator.nunique())),
          ("largest single painter", int(S[S.creator_human].creator.value_counts().max())),
          ("largest single collection", f"{S.collection_label.value_counts().index[0]} {int(S.collection_label.value_counts().iloc[0])}"),
          ("20th- and 21st-century works", int((S.inception >= 1901).sum()))]
    md(pd.DataFrame([(a, b, f"{100 * b / n:.1f}%" if isinstance(b, (int,)) else "") for a, b in r], columns=["", "works", "share"]))
    vc = S.tradition.value_counts()
    md(pd.DataFrame({"tradition": vc.index, "works": vc.values, "share": [f"{100 * v / n:.1f}%" for v in vc.values],
                     "of which image + public-domain proxy": [int((S[S.tradition == t].image & S[S.tradition == t].pd_proxy).sum()) for t in vc.index]}))
    c = S.inception.dropna().map(lambda y: "before 1400" if y < 1400 else f"{int(y) // 100 + 1}th c." if y < 2001 else "21st c.")
    vc = c.value_counts().reindex(["before 1400"] + [f"{k}th c." for k in range(15, 21)] + ["21st c."]).fillna(0).astype(int)
    P("By century: " + ", ".join(f"{k} {v} ({100 * v / n:.0f}%)" for k, v in vc.items()) + f", undated {n - len(c)}.\n")
    vc = S.collection_label.value_counts().head(10)
    P("Top collections: " + ", ".join(f"{k} {v}" for k, v in vc.items()) + ".\n")

P("## H. What the recipe yields\n")
P(f"Universe: {len(X):,} painting-like items fetched; excluded: " + ", ".join(f"{k} {v}" for k, v in X[X.excluded != ""].excluded.value_counts().items())
  + f"; eligible {len(E):,}. Series represented by their best-known member: {len(REP)}; members whose score was raised to the group's: {int((E.represents_group.str.startswith('Q')).sum())}; "
  f"groups typed painting with no member item (kept, flagged): {int((E.represents_group.str.startswith('unresolved')).sum())}.\n")
describe(E[E.in_canon], f"Canon (clean >= {CANON['min_clean']}, cap {CANON['cap']} per painter)")
P(f"Removed from the canon by the cap of {CANON['cap']}: {int(E.capped_out_canon.sum()):,} works by {E[E.capped_out_canon].creator.nunique()} painters.\n")
describe(E[E.in_poc], f"POC (clean >= {POC['min_clean']}, cap {POC['cap']} per painter)")
P("POC size under other settings (fame gate + editorial list with clean >= 3 + floors), before / after the public-domain proxy:\n")
rows = []
for mc in (5, 6, 7, 8):
    for cap in (8, 12, 15, 25, 10**6):
        g, k = build(mc, cap, POC["floor"], POC["floor_default"], museum_everywhere=False)
        k = k & ~((g == "editorial list") & (E.score < 3))
        rows.append({"clean >=": mc, "cap": "none" if cap > 10**5 else cap, "works": int(k.sum()),
                     "with image + public-domain proxy": int((k & E.image & E.pd_proxy).sum()),
                     "under-represented traditions": int((k & E.under).sum())})
md(pd.DataFrame(rows))
P("Per-tradition floor in the POC: pool and what was taken.\n")
rows = []
for t, g in E[E.under].groupby("tradition"):
    rows.append({"tradition": t, "in POC by fame alone": int(((g.score >= POC["min_clean"])).sum()),
                 "pool: any Wikipedia article or any listing": int(((g.score >= 1) | g.listed).sum()),
                 "pool with image + public-domain proxy": int((((g.score >= 1) | g.listed) & g.image & g.pd_proxy).sum()),
                 "floor asked": POC["floor"].get(t, POC["floor_default"]), "in POC": int(g.in_poc.sum()), "in canon": int(g.in_canon.sum())})
md(pd.DataFrame(rows))

cols = dict(rank="rank", qid="qid", label="label", creator_label="creator", creator="creator_qid", inception="year",
            score="fame_score", clean="own_clean_editions", represents_group="represents_group", raw="sitelinks_raw", wp="wikipedia_editions", pv60="pageviews_60d_12wikis",
            n_editorial="n_editorial_lists", lists="lists", tradition="tradition", copyright="copyright_proxy", image="has_image",
            enwiki="enwiki_title", collection_label="collection", in_situ="wall_painting", format_class="format_typed",
            gate_canon="gate_canon", in_canon="in_canon", capped_out_canon="capped_out_canon", gate_poc="gate_poc", in_poc="in_poc")
C = E[(E.score >= 2) | E.listed | E.in_canon | E.in_poc][list(cols)].rename(columns=cols)
C["year"] = C.year.map(lambda y: "" if pd.isna(y) else int(y))
C.insert(0, "snapshot", SNAP)
C.to_csv("candidates.csv", index=False)
Xx = X[X.excluded != ""][["qid", "label", "clean", "excluded"]].sort_values("clean", ascending=False)
Xx[Xx.clean >= 3].to_csv("excluded.csv", index=False)
P(f"`candidates.csv`: {len(C):,} rows (every eligible item with clean >= 2, or on any list, or in either set). `excluded.csv`: {int((Xx.clean >= 3).sum())} items with clean >= 3 that the universe rules removed.\n")
open("data/recipe_tables.md", "w").write("\n".join(out)); print("\n".join(out))
