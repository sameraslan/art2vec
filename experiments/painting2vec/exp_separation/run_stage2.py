"""Stage 2: derived candidates. Composites of statistics parts, and linear residuals in both directions.

`A _|_ B` is A (PCA 64) minus its ridge prediction from B (PCA 64, or several blocks side by side),
fitted on the kept pilot rows. No labels are used anywhere in this file.
"""
import numpy as np

from run_sweep import C, ev, run

B = C.base
S = {  # subject-side blocks
    "dl_cls": B("dinov2_l__pad", "cls"),
    "dl_pm": B("dinov2_l__pad", "patch_mean"),
    "db_cls": B("dinov2_b__pad", "cls"),
    "sig": B("siglip2_b__pad", "embed"),
    "clip": B("clip_l__pad", "embed"),
    "csd_content": B("csd_l__pad", "content"),
}
STATS_B = [("dinov2_b__pad", p) for p in ("gramlog_early", "gramlog_mid", "std_early", "std_mid")]
STATS_L = [("dinov2_l__pad", p) for p in ("gramlog_early", "gramlog_mid", "std_early", "std_mid")]
M = {  # manner-side blocks
    "dl_msmid": B("dinov2_l__pad", "meanstd_mid"),
    "db_msmid": B("dinov2_b__pad", "meanstd_mid"),
    "dl_stats": C.composite(STATS_L),
    "db_stats": C.composite(STATS_B),
    "dl_early": C.composite([("dinov2_l__pad", p) for p in ("meanstd_early", "gramlog_early")]),
    "csd_style": B("csd_l__pad", "style"),
}
COL = C.colour("lstd")
COMP = C.composition()

if __name__ == "__main__":
    for k in ("dl_stats", "db_stats", "dl_early"):
        run(f"comp/{k}", M[k])
    # residual manner: manner minus what subject predicts
    for mk in M:
        for sk in ("dl_cls", "sig", "clip", "csd_content"):
            if mk != "csd_style" and sk in ("clip", "csd_content"):
                continue
            run(f"res/{mk} _|_ {sk}", C.resid(M[mk], [S[sk]]))
    run("res/dl_msmid _|_ dl_cls+dl_pm", C.resid(M["dl_msmid"], [S["dl_cls"], S["dl_pm"]]))
    run("res/csd_style _|_ dl_cls+dl_pm", C.resid(M["csd_style"], [S["dl_cls"], S["dl_pm"]]))
    run("res/csd_style _|_ sig+dl_cls", C.resid(M["csd_style"], [S["sig"], S["dl_cls"]]))
    run("res/dl_msmid _|_ dl_cls+colour+comp", C.resid(M["dl_msmid"], [S["dl_cls"], COL, COMP]))
    run("res/csd_style _|_ dl_cls+colour+comp", C.resid(M["csd_style"], [S["dl_cls"], COL, COMP]))
    run("res/dl_stats _|_ dl_cls+colour+comp", C.resid(M["dl_stats"], [S["dl_cls"], COL, COMP]))
    # residual subject: subject minus what manner predicts
    for sk in ("dl_cls", "dl_pm", "sig", "clip", "csd_content"):
        for mk in ("dl_msmid", "dl_stats", "csd_style"):
            if sk == "csd_content" and mk != "csd_style":
                continue
            run(f"res/{sk} _|_ {mk}", C.resid(S[sk], [M[mk]]))
    run("res/dl_cls _|_ dl_stats+colour", C.resid(S["dl_cls"], [M["dl_stats"], COL]))
    run("res/sig _|_ dl_stats+colour", C.resid(S["sig"], [M["dl_stats"], COL]))
    # text-trained minus not-text-trained: what does SigLIP know that DINOv2 does not?
    run("res/sig _|_ dl_cls+dl_pm", C.resid(S["sig"], [S["dl_cls"], S["dl_pm"]]))
    run("res/clip _|_ dl_cls+dl_pm", C.resid(S["clip"], [S["dl_cls"], S["dl_pm"]]))
    run("res/dl_cls _|_ sig", C.resid(S["dl_cls"], [S["sig"]]))
