import json, sys, re
from lib import OUT
res = json.loads((OUT / "metrics.json").read_text())
SETS = {
 "key": ["genre_p10","depicts_j10","desc_subj","ver_top1_yes","ver_ratio_yes","painter_auc_diffgenre","painter_auc_samegenre","painter_auc_diffgenre_era","move_auc_otherpainter_diffgenre","desc_man3","read_abstraction","read_contour","read_finish","probe_painter_acc","probe_year_r2_eu","year_spread_ratio","probe_fame_r2","probe_fame_within_rho","hub_skew"],
 "copies": ["ver_ratio_yes_same","ver_ratio_yes_other","ver_ratio_yes_anon","ver_ratio_hand_auc","ver_ratio_hand_p","ver_ratio_hand_auc_incl_anon","ver_ratio_hand_p_incl_anon","ver_ratio_series","ver_ratio_variant","ver_top1_yes_same","ver_top1_yes_other"],
 "leak": ["probe_painter_acc","probe_year_r2_eu","probe_year_r2_all","pc_year_maxabs","probe_move_acc","probe_trad_bal","probe_trad_noneu_bal","probe_fame_r2","probe_fame_within_rho","probe_museum_acc","probe_museum_base","probe_museum_base_plus"],
}
which = sys.argv[1]; pat = sys.argv[2] if len(sys.argv) > 2 else "."
cols = SETS[which]
short = lambda c: c.replace("probe_","").replace("painter","pt").replace("genre","g").replace("ver_","v").replace("desc_","d").replace("otherpainter","op").replace("ratio","r").replace("_","")[:8]
print(f"{'name':36s} " + " ".join(f"{short(c):>8s}" for c in cols))
for n, r in res.items():
    if not re.search(pat, n): continue
    print(f"{n[:36]:36s} " + " ".join(f"{r.get(c, float('nan')):8.3f}" for c in cols))
