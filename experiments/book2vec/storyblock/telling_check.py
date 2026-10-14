"""Does the reader's ``telling`` field agree with the counted Telling features of round one?

    .venv/bin/python -m storyblock.telling_check

Reader: person (first / third / mixed), frame, order. Counted (data/blocks/_T_raw.npz):
first-person-singular and third-person pronouns per 1,000 narration words, dialogue share.
The counted call is "first" when first-singular pronouns in narration exceed 10 per 1,000
words. Writes results/telling_reader_vs_counts.md.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from eval.blocks import BLOCK_DIR, RESULTS, load_testbed
from eval.score import frac_negatives_farther, md_table

from storyblock.digests import ids, load

THRESHOLD = 10.0


def main() -> None:
    z = np.load(BLOCK_DIR / "_T_raw.npz")
    names, keys = list(z["scalar_names"]), list(z["keys"])
    S = z["scalars"]
    tb = load_testbed()
    rows = []
    for bid, key in zip(ids()["bid"], ids()["key"], strict=True):
        t = load("out", bid)["telling"]
        r = S[keys.index(key)]
        fsg = float(r[names.index("narr_first_sg")])
        rows.append(
            {
                "id": bid,
                "key": key,
                "reader person": t["person"],
                "reader frame": t["frame"],
                "reader order": t["order"],
                "first-sg / 1000 narration": fsg,
                "third / 1000 narration": float(r[names.index("narr_third")]),
                "dialogue share": float(r[names.index("dialogue_share")]),
                "counted person": "first" if fsg > THRESHOLD else "third",
                "quote flag": tb.at[key, "quote_flag"],
            }
        )
    d = pd.DataFrame(rows)
    d["agree"] = [
        "mixed" if rp == "mixed" else ("yes" if rp == cp else "NO")
        for rp, cp in zip(d["reader person"], d["counted person"], strict=True)
    ]
    first = d.loc[d["reader person"] == "first", "first-sg / 1000 narration"].to_numpy()
    third = d.loc[d["reader person"] == "third", "first-sg / 1000 narration"].to_numpy()
    auc = float(frac_negatives_farther(-first, -third).mean())
    by = d.groupby("reader person")[
        ["first-sg / 1000 narration", "third / 1000 narration", "dialogue share"]
    ].agg(["mean", "min", "max"])
    by.columns = [" ".join(c) for c in by.columns]
    md = "\n".join(
        [
            "## Reader's telling field against the counted Telling features (24 books)",
            "",
            md_table(d, "{:.2f}"),
            "",
            f"Reader says first: {len(first)} books; third: {len(third)}; mixed: "
            f"{int((d['reader person'] == 'mixed').sum())}. Probability that a book the reader "
            f"calls first-person has a higher counted first-singular rate than one it calls "
            f"third-person: {auc:.2f}. Agreement of the thresholded count with the reader on "
            f"the first / third books: {int((d['agree'] == 'yes').sum())} of "
            f"{len(first) + len(third)}.",
            "",
            md_table(by.reset_index(), "{:.2f}"),
            "",
        ]
    )
    (RESULTS / "telling_reader_vs_counts.md").write_text(md)
    print(md)


if __name__ == "__main__":
    main()
