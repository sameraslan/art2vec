"""One table: the framework's section 9 pair types against the best variant of every block.

    .venv/bin/python -m storyblock.all_blocks --prose P --telling T --world W --story S --felt F
        [--felt87 F_PROJ]

Prose, Telling and World are scored on all 87 books; Story and Felt exist for the 24 books a
reader went through and are scored there (negatives and ranks among those 24). A second table
gives all five blocks on the 24 books. Marks against FRAMEWORK.md section 9:

    near    PASS when the bootstrap interval of the AUC lies above 0.5, FAIL when it lies
            below, otherwise WITHIN-NOISE
    apart   FAIL when the interval lies above 0.5 (the pair type is nearer than unrelated
            books), otherwise PASS
    fewer than 3 pairs: WITHIN-NOISE whatever the number
    halves  PASS when a book's other half is its nearest for more than half of the books

Writes results/all_blocks.md.
"""

from __future__ import annotations

import argparse

import numpy as np
import pandas as pd
from eval.blocks import RESULTS, load_block, load_testbed
from eval.score import md_table, score_blocks

from storyblock.subset import subset_blocks

ROWS = (
    (
        "Two halves of one book (a/b)",
        "split",
        {"Prose": "near", "Telling": "near", "World": "near"},
    ),
    (
        "Two translations of one novel",
        "translation_pair",
        {"Prose": "apart", "Telling": "near", "Story": "near", "World": "near"},
    ),
    ("Two editions of one novel", "edition_pair", {}),
    (
        "Two novels by one author, unrelated plots",
        "same_author_unrelated",
        {"Prose": "near", "Story": "apart"},
    ),
    ("Two books of one series", "series", {"Prose": "near", "Telling": "near", "World": "near"}),
    ("A retelling and its source", "retelling", {"Prose": "apart", "Story": "near"}),
    ("Same genre, different authors (control)", "same_genre", {}),
)


def mark(expect: str | None, auc: float, lo: float, hi: float, n: int) -> str:
    if expect is None:
        return ""
    if n < 3 or np.isnan(lo):
        return "WITHIN-NOISE"
    if expect == "near":
        return "PASS" if lo > 0.5 else "FAIL" if hi < 0.5 else "WITHIN-NOISE"
    return "FAIL" if lo > 0.5 else "PASS"


def table(res: dict[str, pd.DataFrame], cols: dict[str, str]) -> pd.DataFrame:
    s = res["scores"].set_index(["block", "set"])
    c = res["checks"].set_index("block")
    out = []
    for label, key, expect in ROWS:
        row = {"pair type": label}
        for col, block in cols.items():
            e = expect.get(col.split(" (")[0])
            want = f" (expects {e})" if e else ""
            if key == "split":
                acc = c.at[block, "split_ab_acc"]
                if np.isnan(acc):
                    row[col] = "not defined"
                else:
                    m = ("PASS" if acc > 0.5 else "FAIL") if e else ""
                    row[col] = f"accuracy {acc:.2f}, {int(c.at[block, 'n_books'])} books{want} {m}"
                continue
            r = s.loc[(block, key)]
            n = int(r["n_pairs"])
            if n == 0:
                row[col] = "no pairs"
                continue
            lo, hi = r.get("auc_lo", np.nan), r.get("auc_hi", np.nan)
            ci = f" [{lo:.2f}, {hi:.2f}]" if n > 1 else ""
            row[col] = f"{r['auc']:.2f}{ci}, n={n}{want} {mark(e, r['auc'], lo, hi, n)}".strip()
        out.append(row)
    return pd.DataFrame(out)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    for name in ("prose", "telling", "world", "story", "felt"):
        ap.add_argument(f"--{name}", required=True)
    ap.add_argument("--felt87", default=None, help="a Felt block that exists for all 87 books")
    ap.add_argument("--prose2", default=None, help="a second Prose block (style encoder)")
    args = ap.parse_args()
    tb = load_testbed()
    full_cols = {"Prose": args.prose}
    if args.prose2:
        full_cols["Prose (style encoder)"] = args.prose2
    full_cols |= {"Telling": args.telling, "World": args.world}
    if args.felt87:
        full_cols["Felt (no reader)"] = args.felt87
    sub_cols = {
        **{k: v for k, v in full_cols.items() if k != "Felt (no reader)"},
        "Story": args.story,
        "Felt": args.felt,
    }
    if args.felt87:
        sub_cols["Felt (no reader)"] = args.felt87
    full = score_blocks([load_block(b) for b in full_cols.values()], tb)
    sub = score_blocks(subset_blocks(list(sub_cols.values())), tb)
    t_full, t_sub = table(full, full_cols), table(sub, sub_cols)
    head = t_full[[c for c in t_full.columns if c != "Felt (no reader)"]].copy()
    head["Story (24 books)"] = t_sub["Story"]
    head["Felt (24 books)"] = t_sub["Felt"]
    n_neg_full, n_neg_sub = (
        int(full["scores"]["n_neg"].iloc[0]),
        int(sub["scores"]["n_neg"].iloc[0]),
    )
    lines = [
        "# All blocks against the framework's pair types",
        "",
        "Blocks: " + ", ".join(f"{k} = `{v}`" for k, v in sub_cols.items()) + ".",
        "",
        "Each cell: AUC that a labelled pair is closer than a negative pair [95% bootstrap "
        "interval over the labelled pairs], number of pairs, what FRAMEWORK.md section 9 "
        "expects, and the mark (rules in `storyblock/all_blocks.py`: near passes when the "
        "interval is above 0.5; apart fails when the interval is above 0.5; fewer than 3 "
        "pairs is always WITHIN-NOISE). The framework sets no expectation for Felt or for "
        "empty cells.",
        "",
        f"## Best variant of each block (Prose, Telling, World on 87 books, {n_neg_full} "
        f"negatives; Story and Felt on the 24-book reader subset, {n_neg_sub} negatives)",
        "",
        md_table(head),
        "",
        f"## The same five blocks on the 24-book subset only ({n_neg_sub} negatives)",
        "",
        md_table(t_sub),
        "",
        "## Cross-block Spearman of pair distances",
        "",
        f"24-book subset, all {24 * 23 // 2} pairs.",
        "",
        md_table(
            sub["cross"]
            .rename(
                index=dict(zip(sub_cols.values(), sub_cols, strict=True)),
                columns=dict(zip(sub_cols.values(), sub_cols, strict=True)),
            )
            .round(2)
            .reset_index(names="block")
        ),
        "",
        "24-book subset, different-author pairs only.",
        "",
        md_table(
            sub["cross_diff"]
            .rename(
                index=dict(zip(sub_cols.values(), sub_cols, strict=True)),
                columns=dict(zip(sub_cols.values(), sub_cols, strict=True)),
            )
            .round(2)
            .reset_index(names="block")
        ),
        "",
        "All 87 books (all pairs / different-author pairs only).",
        "",
    ]
    names = dict(zip(full_cols.values(), full_cols, strict=True))
    two = "{:.2f}".format
    both = full["cross"].map(two) + " / " + full["cross_diff"].map(two)
    lines += [md_table(both.rename(index=names, columns=names).reset_index(names="block")), ""]
    (RESULTS / "all_blocks.md").write_text("\n".join(lines))
    print("\n".join(lines))


if __name__ == "__main__":
    main()
