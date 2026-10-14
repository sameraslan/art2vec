"""Build the tables from results/*.json and fill README.tmpl.md into README.md.
Also writes results/all_candidates.md with every candidate and every column."""
import csv
import json
import re
import statistics as st

from lib import DATA, HERE, OUT

R = json.loads((OUT / "metrics.json").read_text())
SETUP = json.loads((OUT / "setup.json").read_text())
CH = SETUP["chance"]

NICE = {
    "dinov2_b__pad/cls": "DINOv2-B cls", "dinov2_b__pad/patch_mean": "DINOv2-B patch_mean",
    "dinov2_l__pad/cls": "DINOv2-L cls", "dinov2_l__pad/patch_mean": "DINOv2-L patch_mean",
    "dinov2_l__pad/mean_early": "DINOv2-L mean_early (1st order)", "dinov2_l__pad/mean_mid": "DINOv2-L mean_mid (1st order)",
    "dinov2_l__pad/meanstd_mid": "DINOv2-L meanstd_mid", "dinov2_l__pad/std_early": "DINOv2-L std_early (2nd order)",
    "dinov2_l__pad/std_mid": "DINOv2-L std_mid (2nd order)", "dinov2_l__pad/std_late": "DINOv2-L std_late (2nd order)",
    "dinov2_l__pad/gram_mid": "DINOv2-L gram_mid", "dinov2_l__pad/gramlog_early": "DINOv2-L gramlog_early",
    "dinov2_l__pad/gramlog_mid": "DINOv2-L gramlog_mid", "dinov2_l__pad/gramlog_late": "DINOv2-L gramlog_late",
    "comp/dl_stats": "DINOv2-L stats (gramlog+std, early+mid)",
    "siglip2_b__pad/embed": "SigLIP2-B embed (text)", "siglip2_b__pad/patch_mean": "SigLIP2-B patch_mean (text)",
    "clip_l__pad/embed": "CLIP-L embed (text)", "csd_l__pad/style": "CSD style (text+artist)",
    "csd_l__pad/content": "CSD content (text+artist)", "csd_l__pad/backbone": "CSD backbone (text+artist)",
    "colour__lstd/all": "colour (lstd, all parts)", "composition/all": "composition (all parts)",
    "random/gauss64": "random 64-d",
    "res/dl_cls _|_ csd_style": "DINOv2-L cls ⟂ CSD style", "res/dl_cls _|_ dl_stats": "DINOv2-L cls ⟂ DINOv2-L stats",
    "res/dl_cls _|_ dl_msmid": "DINOv2-L cls ⟂ meanstd_mid",
    "res/sig _|_ csd_style": "SigLIP2 ⟂ CSD style", "res/sig _|_ dl_stats": "SigLIP2 ⟂ DINOv2-L stats",
    "res/clip _|_ csd_style": "CLIP ⟂ CSD style", "res/csd_content _|_ csd_style": "CSD content ⟂ CSD style",
    "res/csd_style _|_ dl_cls": "CSD style ⟂ DINOv2-L cls", "res/csd_style _|_ sig": "CSD style ⟂ SigLIP2",
    "res/csd_style _|_ clip": "CSD style ⟂ CLIP", "res/csd_style _|_ csd_content": "CSD style ⟂ CSD content",
    "res/dl_msmid _|_ dl_cls": "meanstd_mid ⟂ DINOv2-L cls", "res/dl_stats _|_ dl_cls": "DINOv2-L stats ⟂ DINOv2-L cls",
    "res/dl_stats _|_ sig": "DINOv2-L stats ⟂ SigLIP2",
    "res/csd_style _|_ dl_cls+colour+comp": "CSD style ⟂ (DINOv2-L cls, colour, composition)",
    "res/dl_msmid _|_ dl_cls+colour+comp": "meanstd_mid ⟂ (DINOv2-L cls, colour, composition)",
    "res/sig _|_ dl_cls+dl_pm": "SigLIP2 ⟂ DINOv2-L (cls, patch_mean)", "res/clip _|_ dl_cls+dl_pm": "CLIP ⟂ DINOv2-L (cls, patch_mean)",
    "res/dl_cls _|_ sig": "DINOv2-L cls ⟂ SigLIP2", "res/dl_pm _|_ csd_style": "DINOv2-L patch_mean ⟂ CSD style",
}
MAIN = ["dinov2_b__pad/cls", "dinov2_l__pad/cls", "dinov2_l__pad/patch_mean", "dinov2_l__pad/mean_mid",
        "dinov2_l__pad/meanstd_mid", "dinov2_l__pad/std_early", "dinov2_l__pad/std_mid", "dinov2_l__pad/gram_mid",
        "dinov2_l__pad/gramlog_early", "dinov2_l__pad/gramlog_mid", "dinov2_l__pad/gramlog_late", "comp/dl_stats",
        "siglip2_b__pad/embed", "siglip2_b__pad/patch_mean", "clip_l__pad/embed", "csd_l__pad/style", "csd_l__pad/content",
        "colour__lstd/all", "composition/all", "random/gauss64"]
RES = ["res/dl_cls _|_ csd_style", "res/dl_cls _|_ dl_stats", "res/sig _|_ csd_style", "res/sig _|_ dl_stats",
       "res/csd_content _|_ csd_style", "res/csd_style _|_ dl_cls", "res/csd_style _|_ sig", "res/csd_style _|_ clip",
       "res/csd_style _|_ csd_content", "res/dl_msmid _|_ dl_cls", "res/dl_stats _|_ dl_cls",
       "res/csd_style _|_ dl_cls+colour+comp", "res/sig _|_ dl_cls+dl_pm", "res/clip _|_ dl_cls+dl_pm", "res/dl_cls _|_ sig"]
LEADERS = ["dinov2_l__pad/cls", "siglip2_b__pad/embed", "clip_l__pad/embed", "res/dl_cls _|_ csd_style",
           "comp/dl_stats", "dinov2_l__pad/meanstd_mid", "csd_l__pad/style", "res/csd_style _|_ dl_cls", "res/dl_msmid _|_ dl_cls",
           "colour__lstd/all", "composition/all", "random/gauss64"]

COLS = {
    "subject": [("genre_p10", "genre P@10", 2), ("genre_p10_otherpainter", "… other painters only", 2), ("depicts_j10", "depicts J@10", 3),
                ("depicts_j10_otherpainter", "… other painters only", 3),
                ("desc_subj", "checklist ρ", 2), ("desc_subj_nn3", "checklist nn3", 2), ("ver_top1_yes", "version top-1", 2),
                ("ver_top10_yes", "version top-10", 2), ("ver_ratio_yes", "version ratio", 2), ("ver_med_variant", "variant median rank", 0),
                ("ver_med_series", "series median rank", 0)],
    "manner": [("desc_man3", "manner ρ", 2), ("desc_man_given_subj", "manner ρ given subject", 2), ("desc_man3_nn3", "manner nn3", 2),
               ("read_abstraction", "read abstraction", 2), ("read_contour", "read contour", 2), ("read_finish", "read finish", 2),
               ("painter_auc_all", "painter AUC", 2), ("painter_auc_samegenre", "same genre", 2), ("painter_auc_diffgenre", "other genre", 2),
               ("painter_auc_diffgenre_era", "other genre, ±30 y", 2), ("painter_p10_diffgenre", "painter P@10 other genre", 3),
               ("move_auc_otherpainter_diffgenre", "movement AUC, other painter and genre", 2)],
    "copies": [("ver_top1_yes_same", "top-1 same hand", 2), ("ver_top1_yes_other", "top-1 other hand", 2),
               ("ver_ratio_yes_same", "ratio same hand", 2), ("ver_ratio_yes_other", "ratio other hand", 2), ("ver_ratio_yes_anon", "ratio anonymous", 2),
               ("ver_ratio_hand_auc", "AUC other > same", 2), ("ver_ratio_hand_p", "p", 3),
               ("ver_ratio_hand_auc_incl_anon", "AUC incl. anonymous", 2), ("ver_ratio_hand_p_incl_anon", "p", 3),
               ("ver_ratio_series", "ratio series", 2)],
    "leak": [("probe_painter_acc", "painter acc", 2), ("probe_year_r2_eu", "year R² (Eur.)", 2), ("probe_year_r2_all", "year R² (all)", 2),
             ("pc_year_maxabs", "max |r| PC1-4 vs year", 2), ("probe_move_acc", "movement acc", 2), ("probe_trad_bal", "tradition bal. acc", 2),
             ("probe_fame_r2", "fame R²", 2), ("probe_fame_rho", "fame ρ", 2), ("probe_fame_within_rho", "fame ρ within painter", 2),
             ("probe_museum_acc", "museum acc", 2), ("probe_museum_base_plus", "museum acc, year+country+16 dims", 2)],
    "neigh": [("painter_repeat10", "same painter in top 10", 3), ("year_spread10", "median |Δyear| top 10", 0), ("year_spread_ratio", "÷ random", 2),
              ("hub_skew", "hubness skew", 2), ("hub_zero", "in nobody's top 10", 3), ("hub_max", "max k-occurrence", 0)],
    "short": [("genre_p10", "genre P@10", 2), ("depicts_j10", "depicts J@10", 3), ("ver_top1_yes", "version top-1", 2),
              ("painter_auc_diffgenre", "painter AUC other genre", 2), ("painter_auc_diffgenre_era", "…±30 y", 2),
              ("probe_painter_acc", "painter probe", 2), ("probe_year_r2_eu", "year R²", 2), ("year_spread_ratio", "year spread ÷ random", 2),
              ("probe_fame_within_rho", "fame ρ within painter", 2), ("ver_ratio_hand_auc_incl_anon", "copies AUC", 2), ("hub_skew", "hub skew", 2)],
}


def table(rows, cols, src=R, names=None):
    names = names or NICE
    head = "| candidate | " + " | ".join(c[1] for c in COLS[cols]) + " |"
    out = [head, "|" + "---|" * (len(COLS[cols]) + 1)]
    for k in rows:
        if k not in src:
            continue
        r = src[k]
        cells = []
        for key, _, nd in COLS[cols]:
            v = r.get(key)
            cells.append("" if v is None else f"{v:.{nd}f}")
        out.append(f"| {names.get(k, k)} | " + " | ".join(cells) + " |")
    return "\n".join(out)


def redundancy():
    d = json.loads((OUT / "redundancy.json").read_text())
    names = d["names"]
    short = ["S-dino", "S-siglip", "S-res", "M-stats", "M-mid", "M-csd", "M-res-csd", "M-res-mid", "colour", "compos."]
    out = []
    for key, title, nd in (("shared_mean", "Mean number of shared paintings in the two top-10 lists (0 to 10)", 2),
                           ("jaccard_zero", "Share of paintings whose two top-10 lists share nothing", 2),
                           ("cka", "Linear CKA", 2),
                           ("r2", "Cross-validated R² of the column block predicted linearly from the row block", 2)):
        out.append(f"**{title}**\n")
        out.append("| | " + " | ".join(short) + " |")
        out.append("|" + "---|" * (len(short) + 1))
        for a, sa in zip(names, short):
            out.append(f"| {sa} | " + " | ".join("–" if a == b else f"{d[key][f'{a}|{b}']:.{nd}f}" for b in names) + " |")
        out.append("")
    out.append("Key: " + "; ".join(f"{s} = {n}" for s, n in zip(short, names)) + ".")
    return "\n".join(out)


def label_assisted():
    d = json.loads((OUT / "label_assisted.json").read_text())
    rows = [k for k in d if not k.startswith("_")]
    return table(rows, "short", src=d, names={k: k.replace(" (label-assisted, ", " (LA, ").replace("_|_", "⟂").replace(" | ", ": ") for k in rows})


def ablation(kind):
    if kind == "view":
        rows = [f"{m}__{v}/{p}" for p in ("cls", "meanstd_mid") for m, vs in (("dinov2_b", ("center", "pad", "tile")), ("dinov2_l", ("pad", "tile"))) for v in vs]
        rows += [f"abl/{m}__{v}/stats" for m, vs in (("dinov2_b", ("center", "pad", "tile")), ("dinov2_l", ("pad", "tile"))) for v in vs]
        rows += [f"siglip2_b__{v}/embed" for v in ("center", "pad", "tile")] + [f"clip_l__{v}/embed" for v in ("pad", "tile")] + [f"csd_l__{v}/style" for v in ("pad", "tile")]
        rows += [k for k in R if k.startswith("abl/csd_style[") or k.startswith("abl/dinov2_l_cls[")]
    elif kind == "dim":
        rows = []
        for st_, p in (("dinov2_l__pad", "cls"), ("siglip2_b__pad", "embed"), ("csd_l__pad", "style"), ("dinov2_l__pad", "meanstd_mid"), ("dinov2_l__pad", "gramlog_mid")):
            for k in (16, 32, 64, 128):
                for w in ("", " white"):
                    rows.append(f"{st_}/{p}" if (k == 64 and not w) else f"abl/{st_}/{p} k={k}{w}")
    else:
        rows = [k for k in R if " pre=" in k or " nuis k=" in k]
    nm = {k: k.replace("abl/", "").replace("__", " ").replace("_|_", "⟂") + ("  k=64" if kind == "dim" and "k=" not in k else "") for k in rows}
    return table(rows, "short", names=nm)


def sheets():
    d = json.loads((OUT / "sheets_neighbours.json").read_text())
    m = {x["qid"]: x for x in csv.DictReader(open(DATA / "pilot" / "meta.csv"))}
    out = ["| row | block | same painter (of 8) | same tradition (of 8) | median abs. year gap | shared with row A (of 8) | shares a P136 genre (of 8) |", "|---|---|---|---|---|---|---|"]
    for L, desc in d["rows"].items():
        sp, tr, dy, ov, sg = [], [], [], [], []
        for s, rows in d["seeds"].items():
            ids, A = rows[L], set(rows["A"])
            sp.append(sum(1 for q in ids if m[q]["creator_qid"] and m[q]["creator_qid"] == m[s]["creator_qid"]))
            tr.append(sum(1 for q in ids if m[q]["tradition"] == m[s]["tradition"]))
            ys = [abs(float(m[q]["inception_year"]) - float(m[s]["inception_year"])) for q in ids if m[q]["inception_year"] and m[s]["inception_year"]]
            if ys:
                dy.append(st.median(ys))
            ov.append(len(A & set(ids)))
            g = set(m[s]["genres"].split("|")) - {""}
            if g:
                sg.append(sum(1 for q in ids if g & set(m[q]["genres"].split("|"))))
        out.append(f"| {L} | {desc} | {st.mean(sp):.2f} | {st.mean(tr):.2f} | {st.median(dy):.0f} | {st.mean(ov):.2f} | {st.mean(sg):.2f} |")
    return "\n".join(out)


def seeds():
    rows = list(csv.DictReader(open(OUT / "seeds.csv")))
    out = ["| # | qid | title | painter | year | tradition | genre |", "|---|---|---|---|---|---|---|"]
    for i, r in enumerate(rows, 1):
        y = r["inception_year"]
        out.append(f"| {i} | {r['qid']} | {r['title'][:48]} | {r['creator_name'].replace('|', '; ')[:28]} | {y[:-2] if y.endswith('.0') else y} | {r['tradition']} | {r['genres'].replace('|', '; ')[:32]} |")
    return "\n".join(out)


def csd_heads():
    d = json.loads((OUT / "csd_heads.json").read_text())
    out = ["| pair | shared in top 10 | linear CKA | R² of the second from the first |", "|---|---|---|---|"]
    for r in d:
        out.append(f"| {r['a']} / {r['b']} | {r['shared_top10']:.1f} | {r['cka']:.2f} | {r['r2_b_from_a']:.2f} |")
    return "\n".join(out)


def hands():
    out = ["| relation | composition_match | hand | pairs |", "|---|---|---|---|"]
    for r in SETUP["hand_counts"]:
        out.append(f"| {r['relation']} | {r['composition_match']} | {r['hand']} | {r['n']} |")
    return "\n".join(out)


TABLES = {
    "subject_main": lambda: table(MAIN, "subject"), "subject_res": lambda: table(RES, "subject"),
    "manner_main": lambda: table(MAIN, "manner"), "manner_res": lambda: table(RES, "manner"),
    "copies": lambda: table(LEADERS + ["res/dl_pm _|_ csd_style", "res/csd_style _|_ sig"], "copies"),
    "leak_main": lambda: table(MAIN, "leak"), "leak_res": lambda: table(RES, "leak"),
    "neigh_main": lambda: table(MAIN, "neigh"), "neigh_res": lambda: table(RES, "neigh"),
    "redundancy": redundancy, "label_assisted": label_assisted,
    "abl_view": lambda: ablation("view"), "abl_dim": lambda: ablation("dim"), "abl_other": lambda: ablation("other"),
    "sheets": sheets, "seeds": seeds, "hands": hands, "csd_heads": csd_heads,
}

if __name__ == "__main__":
    full = []
    for sec in ("subject", "manner", "copies", "leak", "neigh"):
        full.append(f"## {sec}\n\n" + table(list(R), sec, names={}) + "\n")
    (OUT / "all_candidates.md").write_text("# Every candidate, every column\n\nGenerated by report.py from metrics.json. Column meanings are in ../README.md.\n\n" + "\n".join(full))
    tmpl = (HERE / "README.tmpl.md").read_text() if (HERE / "README.tmpl.md").exists() else ""
    if tmpl:
        def sub(mo):
            return TABLES[mo.group(1)]()
        text = re.sub(r"\{\{(\w+)\}\}", sub, tmpl)
        for k, v in {"CH_GENRE": f"{CH['genre_p10']:.3f}", "CH_DEP": f"{CH['depicts_j10']:.3f}", "CH_MOVE": f"{CH['move_p10']:.3f}",
                     "CH_PAINTER": f"{CH['painter_p10']:.3f}", "N_KEPT": str(SETUP["n_kept"])}.items():
            text = text.replace(f"[[{k}]]", v)
        (HERE / "README.md").write_text(text)
        print("README.md written,", len(text), "chars")
    else:
        for k, f in TABLES.items():
            print(f"\n### {k}\n")
            print(f())
