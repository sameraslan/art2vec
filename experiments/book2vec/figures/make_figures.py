"""Draw the book2vec gallery figures from the committed results.

Reads only files under ../results/ and writes PNGs next to this script. No model runs.

    uv run --with matplotlib --with pandas python experiments/book2vec/figures/make_figures.py
"""

from __future__ import annotations

import re
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from matplotlib.colors import LinearSegmentedColormap  # noqa: E402

HERE = Path(__file__).resolve().parent
RESULTS = HERE.parent / "results"
TESTBED = HERE.parent / "testbed.csv"
DPI = 150

INK = "#0b0b0b"
INK2 = "#52514e"
MUTED = "#8a8984"
GRID = "#e4e3df"
BLUE = "#2a78d6"
ORANGE = "#eb6834"
SEQ = LinearSegmentedColormap.from_list(
    "seq_blue", ["#f4f8fd", "#cde2fb", "#86b6ef", "#3987e5", "#1c5cab", "#0d366b"]
)

# The block variants the round-two summary (all_blocks.md) reports as the best of each kind.
BLOCKS = {
    "P4_mfw500_tag3_rhythm": "Prose\n(counts)",
    "P5_style_clean_c": "Prose\n(style encoder)",
    "T3_scalars_dtw20_sd": "Telling",
    "W1_qwen_maskB_c": "World",
}

plt.rcParams.update(
    {
        "figure.facecolor": "white",
        "axes.facecolor": "white",
        "savefig.facecolor": "white",
        "font.family": "DejaVu Sans",
        "font.size": 10,
        "text.color": INK,
        "axes.labelcolor": INK2,
        "axes.edgecolor": MUTED,
        "xtick.color": INK2,
        "ytick.color": INK2,
        "axes.titlesize": 12,
        "axes.titleweight": "bold",
        "axes.titlelocation": "left",
    }
)


def md_tables(path: Path) -> dict[str, list[list[str]]]:
    """Every pipe table in a markdown file, keyed by the heading or text line above it."""
    tables: dict[str, list[list[str]]] = {}
    label, rows, last_text = None, [], ""
    for line in path.read_text().splitlines() + [""]:
        if line.startswith("|"):
            if label is None:
                label = last_text
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if not all(set(c) <= set("-: ") for c in cells):
                rows.append(cells)
        else:
            if label is not None:
                tables[label] = rows
                label, rows = None, []
            if line.strip():
                last_text = line.strip().lstrip("#").strip()
    return tables


def save(fig, name: str) -> None:
    out = HERE / name
    fig.savefig(out, dpi=DPI, bbox_inches="tight", pad_inches=0.15)
    plt.close(fig)
    print(f"{out.name}: {out.stat().st_size / 1024:.0f} KB")


# 1. Each block against the framework's pair tests ------------------------------------------


def fig_scorecard() -> None:
    tables = md_tables(RESULTS / "all_blocks.md")
    rows = next(v for k, v in tables.items() if k.startswith("Best variant of each block"))
    header = rows[0]
    cols = ["Prose", "Prose (style encoder)", "Telling", "World"]
    idx = [header.index(c) for c in cols]
    wanted = {
        "Two halves of one book (a/b)": "Two halves of one book\n(retrieval accuracy)",
        "Two translations of one novel": "Two translations of one novel",
        "Two novels by one author, unrelated plots": "Two novels by one author",
        "Two books of one series": "Two books of one series",
        "A retelling and its source": "A retelling and its source",
        "Same genre, different authors (control)": "Same genre, different authors",
    }
    labels, vals, notes = [], [], []
    for r in rows[1:]:
        if r[0] not in wanted:
            continue
        labels.append(wanted[r[0]])
        vrow, nrow = [], []
        for i in idx:
            cell = r[i]
            m = re.search(r"(?:accuracy )?(\d\.\d\d)", cell)
            vrow.append(float(m.group(1)))
            exp = re.search(r"expects (near|apart)\) (PASS|FAIL)", cell)
            nrow.append(f"should be {exp.group(1)}: {exp.group(2).lower()}" if exp else "")
        vals.append(vrow)
        notes.append(nrow)
    v = np.array(vals)

    fig, ax = plt.subplots(figsize=(8.6, 5.0))
    ax.imshow(v, cmap=SEQ, vmin=0.5, vmax=1.0, aspect="auto")
    for i in range(v.shape[0]):
        for j in range(v.shape[1]):
            dark = v[i, j] > 0.82
            colour = "white" if dark else INK
            ax.text(j, i - 0.12, f"{v[i, j]:.2f}", ha="center", va="center",
                    fontsize=12, fontweight="bold", color=colour)
            note = notes[i][j]
            if note:
                fail = note.endswith("fail")
                ax.text(j, i + 0.24, note, ha="center", va="center", fontsize=7.5,
                        color=colour, fontweight="bold" if fail else "normal")
    ax.set_xticks(range(len(cols)), [BLOCKS[k] for k in BLOCKS])
    ax.set_yticks(range(len(labels)), labels)
    ax.xaxis.tick_top()
    ax.tick_params(length=0)
    for s in ax.spines.values():
        s.set_visible(False)
    ax.set_xticks(np.arange(-0.5, len(cols)), minor=True)
    ax.set_yticks(np.arange(-0.5, len(labels)), minor=True)
    ax.grid(which="minor", color="white", linewidth=2)
    ax.tick_params(which="minor", length=0)
    fig.suptitle("Each block answers a different question", x=0.02, ha="left",
                 fontsize=13, fontweight="bold", y=1.04)
    fig.text(0.02, 0.985,
             "AUC that a pair of this kind is closer than a random pair of books (0.5 = chance, "
             "1 = always closer). 87 novels.",
             ha="left", fontsize=9, color=INK2)
    fig.text(0.02, -0.03,
             "Source: results/all_blocks.md (best variant of each block). Expectations from "
             "FRAMEWORK.md section 9; blank where it sets none.",
             ha="left", fontsize=8, color=MUTED)
    save(fig, "block_scorecard.png")


# 2. How much the blocks agree ---------------------------------------------------------------


def _spearman(rows: list[list[str]], keep: list[str], part: int | None = None) -> np.ndarray:
    header = rows[0]
    ci = [header.index(k) for k in keep]
    byname = {r[0]: r for r in rows[1:]}
    m = np.zeros((len(keep), len(keep)))
    for a, ka in enumerate(keep):
        for b, i in enumerate(ci):
            cell = byname[ka][i]
            m[a, b] = float(cell.split("/")[part].strip() if part is not None else cell)
    return m


def fig_agreement() -> None:
    tables = md_tables(RESULTS / "all_blocks.md")
    sub = next(v for k, v in tables.items() if k.startswith("24-book subset, all 276 pairs"))
    full = next(v for k, v in tables.items() if k.startswith("All 87 books"))
    k87 = ["Prose", "Prose (style encoder)", "Telling", "World", "Felt (no reader)"]
    k24 = ["Prose", "Prose (style encoder)", "Telling", "World", "Story", "Felt"]
    short = {"Prose": "Prose", "Prose (style encoder)": "Prose (style enc.)",
             "Telling": "Telling", "World": "World", "Story": "Story",
             "Felt": "Felt (reader)", "Felt (no reader)": "Felt (no reader)"}
    panels = [
        (_spearman(full, k87, part=0), k87, "87 novels, all 3,741 pairs"),
        (_spearman(sub, k24), k24, "24-novel reader subset, all 276 pairs"),
    ]
    fig, axes = plt.subplots(1, 2, figsize=(10.2, 4.6), gridspec_kw={"wspace": 0.55})
    for ax, (m, keys, title) in zip(axes, panels):
        n = len(keys)
        show = np.where(np.tril(np.ones((n, n)), k=-1) > 0, m, np.nan)
        ax.imshow(show, cmap=SEQ, vmin=0, vmax=1, aspect="equal")
        for i in range(n):
            for j in range(i):
                ax.text(j, i, f"{m[i, j]:.2f}", ha="center", va="center", fontsize=9.5,
                        color="white" if m[i, j] > 0.6 else INK)
        ax.set_xticks(range(n - 1), [short[k] for k in keys[:-1]], rotation=35, ha="right")
        ax.set_yticks(range(1, n), [short[k] for k in keys[1:]])
        ax.set_xlim(-0.5, n - 1.5)
        ax.set_ylim(n - 0.5, 0.5)
        ax.tick_params(length=0)
        for s in ax.spines.values():
            s.set_visible(False)
        ax.set_title(title, fontsize=10, fontweight="normal", color=INK2, pad=8)
    fig.suptitle("The blocks mostly disagree about which books are close", x=0.07,
                 ha="left", fontsize=13, fontweight="bold", y=1.06)
    fig.text(0.07, 0.975,
             "Spearman correlation between two blocks' distances over the same book pairs. "
             "1 would mean the same ordering.",
             ha="left", fontsize=9, color=INK2)
    fig.text(0.07, -0.08, "Source: results/all_blocks.md (cross-block Spearman of pair distances).",
             ha="left", fontsize=8, color=MUTED)
    save(fig, "block_agreement.png")


# 3. What masking names does to World ---------------------------------------------------------


def fig_masking() -> None:
    s = pd.read_csv(RESULTS / "world_all_scores.csv")
    variants = ["W1_qwen_clean_c", "W1_qwen_maskA_c", "W1_qwen_maskB_c"]
    xlab = ["Names left in", "Person names\nmasked", "Persons and places\nmasked"]
    series = [
        ("same_translator_diff_author", "Same translator, different author", ORANGE),
        ("same_author_orig_en", "Same author, English originals", BLUE),
    ]
    fig, ax = plt.subplots(figsize=(7.2, 4.4))
    x = np.arange(3)
    for key, label, colour in series:
        sub = s[(s["set"] == key)].set_index("block").loc[variants]
        y, lo, hi = sub["auc"].to_numpy(), sub["auc_lo"].to_numpy(), sub["auc_hi"].to_numpy()
        n = int(sub["n_pairs"].iloc[0])
        ax.fill_between(x, lo, hi, color=colour, alpha=0.12, linewidth=0)
        ax.plot(x, y, color=colour, linewidth=2, marker="o", markersize=8,
                markeredgecolor="white", markeredgewidth=2, zorder=3)
        for xi, yi in zip(x, y):
            above = (xi == 0) != key.startswith("same_author")
            ax.text(xi, yi + (0.022 if above else -0.045), f"{yi:.2f}", ha="center",
                    fontsize=9.5, color=INK)
        ax.text(2.08, y[-1], f"{label}\n({n} pairs)", va="center", fontsize=9, color=INK)
    ax.axhline(0.5, color=MUTED, linewidth=1, linestyle=(0, (3, 3)))
    ax.text(-0.15, 0.51, "chance", fontsize=8, color=MUTED, va="bottom")
    ax.set_xticks(x, xlab)
    ax.set_xlim(-0.2, 2.9)
    ax.set_ylim(0.45, 1.02)
    ax.set_ylabel("World AUC (pair closer than a random pair)")
    ax.grid(axis="y", color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    ax.tick_params(length=0)
    fig.suptitle("Names made different authors look alike, but only in translation", x=0.02,
                 ha="left", fontsize=13, fontweight="bold", y=1.04)
    fig.text(0.02, 0.975,
             "World block, 87 novels. Shaded: 95% bootstrap interval over the labelled pairs.",
             ha="left", fontsize=9, color=INK2)
    fig.text(0.02, -0.04, "Source: results/world_all_scores.csv (W1_qwen_*_c, clean / maskA / maskB).",
             ha="left", fontsize=8, color=MUTED)
    save(fig, "name_masking.png")


# 4. Where a novel's other translation lands in its neighbour list --------------------------


def fig_translation_ranks() -> None:
    sources = {
        "P4_mfw500_tag3_rhythm": "p5_style_pairs.csv",
        "P5_style_clean_c": "p5_style_pairs.csv",
        "T3_scalars_dtw20_sd": "telling_all_pairs.csv",
        "W1_qwen_maskB_c": "world_all_pairs.csv",
    }
    titles = pd.read_csv(TESTBED).set_index("key")
    hl_a, hl_b = "fathers_garnett", "fathers_hogarth"
    fig, ax = plt.subplots(figsize=(8.2, 4.2))
    rng = np.random.default_rng(0)
    order = list(BLOCKS)
    for row, block in enumerate(order):
        p = pd.read_csv(RESULTS / sources[block])
        p = p[(p["block"] == block) & (p["set"] == "translation_pair")]
        # Ranks are 0 for the nearest other book (eval/score.py); show 1 = nearest.
        pos = np.concatenate([p["rank_b_from_a"], p["rank_a_from_b"]]) + 1
        jitter = rng.uniform(-0.17, 0.17, size=len(pos))
        ax.scatter(pos, row + jitter, s=46, color=MUTED, alpha=0.55, edgecolor="white",
                   linewidth=1, zorder=2)
        h = p[(p["a"] == hl_a) & (p["b"] == hl_b)].iloc[0]
        hp = h["rank_b_from_a"] + 1
        ax.scatter([hp], [row], s=90, color=ORANGE, edgecolor="white", linewidth=2, zorder=3)
        ax.text(hp, row - 0.3, f"{hp:.0f}", ha="center", va="bottom", fontsize=9,
                color=INK, fontweight="bold")
        med = np.median(pos)
        ax.plot([med, med], [row - 0.3, row + 0.3], color=INK, linewidth=2, zorder=4)
    ax.set_yticks(range(len(order)), [BLOCKS[b].replace("\n", " ") for b in order])
    ax.invert_yaxis()
    ax.set_xscale("log")
    ax.set_xticks([1, 2, 5, 10, 20, 50, 86], ["1", "2", "5", "10", "20", "50", "86"])
    ax.set_xlim(0.8, 100)
    ax.set_xlabel("Position of the other translation among the 86 other novels (1 = nearest)")
    ax.grid(axis="x", color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
    ax.tick_params(length=0)
    a, b = titles.loc[hl_a], titles.loc[hl_b]
    fig.suptitle("Two translations of one novel: together in World and Telling, apart in style",
                 x=0.02, ha="left", fontsize=12.5, fontweight="bold", y=1.11)
    fig.text(0.02, 0.985,
             f"10 translation pairs, both directions (grey); black tick = median. Orange: where "
             f"Turgenev's {b['title']} ({b['translator']})\nlands from {a['title']} "
             f"({a['translator']}).",
             ha="left", fontsize=9, color=INK2, va="bottom")
    fig.text(0.02, -0.06,
             "Source: results/p5_style_pairs.csv (Prose), telling_all_pairs.csv (Telling), "
             "world_all_pairs.csv (World); translation_pair rows.",
             ha="left", fontsize=8, color=MUTED)
    save(fig, "translation_ranks.png")


if __name__ == "__main__":
    fig_scorecard()
    fig_agreement()
    fig_masking()
    fig_translation_ranks()
