"""film2vec experiments: static figures for the GitHub gallery (figures/README.md).

Throwaway experiment code. Reads results/results.json, results/neighbours.json, catalog.csv and the frame
thumbnails written by thumbs.py (<cache>/experiments/film2vec/thumbs/<id>/NN.jpg). Runs no model.

    uv run --with matplotlib --with pillow python experiments/film2vec/figures/make_figures.py

Writes into this folder:
    neighbours_war.jpg      look-block neighbours of All Quiet on the Western Front
    neighbours_failure.jpg  look-block neighbours of Diary of a Lost Girl (a hub-driven list)
    block_agreement.png     top-10 overlap of look:mean with the other blocks (experiment 1)
    stills_needed.png       top-10 overlap from n frames or windows against the full film (experiment 3)
    leaks.png               look:mean neighbours sharing a label, as a multiple of chance (experiment 5)

Frames are small thumbnails (176 x 132 cells), as approved for committing.
"""

from __future__ import annotations

import csv
import json
import os
from collections import Counter
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
EXP = HERE.parent
RESULTS = json.loads((EXP / "results" / "results.json").read_text())
NEIGHBOURS = json.loads((EXP / "results" / "neighbours.json").read_text())
CATALOG = {r["id"]: r for r in csv.DictReader((EXP / "catalog.csv").open(encoding="utf-8"))}

# Palette (dataviz reference instance, light surface).
SURFACE = "#fcfcfb"
INK = "#0b0b0b"
INK_2 = "#52514e"
GRID = "#e4e3df"
BLUE = "#2a78d6"
ORANGE = "#eb6834"
NEUTRAL = "#a3a29c"

# Contact sheets.
PICK = [0, 2, 5, 7]  # four of the eight thumbnails, spread over the running time
CELL_W, CELL_H = 176, 132
GAP = 4
LABEL_W = 300
PAD = 16
ROW_GAP = 10


def cache_home() -> Path:
    env = os.environ.get("ART2VEC_HOME")
    return Path(env).expanduser() if env else Path.home() / "Library" / "Caches" / "art2vec"


THUMBS = cache_home() / "experiments" / "film2vec" / "thumbs"


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    path = font_manager.findfont(font_manager.FontProperties(family="DejaVu Sans", weight="bold" if bold else "normal"))
    return ImageFont.truetype(path, size)


def frame_cell(fid: str, i: int) -> Image.Image:
    cell = Image.new("RGB", (CELL_W, CELL_H), "black")
    p = THUMBS / fid / f"{i:02d}.jpg"
    if not p.exists():
        return cell
    im = Image.open(p).convert("RGB")
    im.thumbnail((CELL_W, CELL_H), Image.LANCZOS)
    cell.paste(im, ((CELL_W - im.width) // 2, (CELL_H - im.height) // 2))
    return cell


def director(fid: str) -> str:
    return CATALOG[fid]["director"].replace(";", ", ")


def contact_sheet(query: str, n: int, title: str, note: str, out: Path, block: str = "look") -> None:
    entry = NEIGHBOURS["blocks"][block][query]
    rows = [(query, None, None)] + [(x["id"], r, x["distance"]) for r, x in enumerate(entry["neighbours"][:n], 1)]
    width = PAD * 2 + LABEL_W + len(PICK) * CELL_W + (len(PICK) - 1) * GAP
    nf = font(13)
    probe = ImageDraw.Draw(Image.new("RGB", (1, 1)))
    lines, cur = [], ""
    for word in note.split():
        trial = (cur + " " + word).strip()
        if probe.textlength(trial, font=nf) > width - 2 * PAD and cur:
            lines.append(cur)
            cur = word
        else:
            cur = trial
    lines.append(cur)
    head_h = 40 + 18 * len(lines) + 12
    sep = 16
    height = PAD + head_h + len(rows) * CELL_H + (len(rows) - 1) * ROW_GAP + sep + PAD
    img = Image.new("RGB", (width, height), SURFACE)
    d = ImageDraw.Draw(img)
    d.text((PAD, PAD), title, font=font(20, bold=True), fill=INK)
    for j, line in enumerate(lines):
        d.text((PAD, PAD + 32 + 18 * j), line, font=nf, fill=INK_2)
    y = PAD + head_h
    for fid, rank, dist in rows:
        c = CATALOG[fid]
        if rank is None:
            d.text((PAD, y + 4), "QUERY", font=font(12, bold=True), fill=INK_2)
        else:
            d.text((PAD, y + 4), f"NEIGHBOUR {rank}", font=font(12, bold=True), fill=INK_2)
        tf = font(16, bold=True)
        name = c["title"]
        while d.textlength(name, font=tf) > LABEL_W - 12 and len(name) > 4:
            name = name[:-2].rstrip() + "…" if not name.endswith("…") else name[:-3].rstrip() + "…"
        d.text((PAD, y + 24), name, font=tf, fill=INK)
        d.text((PAD, y + 48), f"{c['year']}, {director(fid)}", font=font(13), fill=INK_2)
        d.text((PAD, y + 68), f"{c['country']}, {c['silent_or_sound']}", font=font(13), fill=INK_2)
        if dist is not None:
            d.text((PAD, y + 96), f"similarity {1 - dist:.2f}", font=font(15, bold=True), fill=INK)
        x = PAD + LABEL_W
        for i in PICK:
            img.paste(frame_cell(fid, i), (x, y))
            x += CELL_W + GAP
        y += CELL_H + ROW_GAP
        if rank is None:
            d.line([(PAD, y + sep // 2 - 4), (width - PAD, y + sep // 2 - 4)], fill=GRID, width=2)
            y += sep
    img.save(out, "JPEG", quality=80, optimize=True, progressive=True)


def hub_counts(block: str = "look") -> Counter:
    return Counter(x["id"] for e in NEIGHBOURS["blocks"][block].values() for x in e["neighbours"])


def style_axes(ax) -> None:
    ax.set_facecolor(SURFACE)
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    ax.spines["bottom"].set_color(NEUTRAL)
    ax.tick_params(colors=INK_2, length=0)
    ax.grid(axis="x", color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)


def save_checked(fig, out: Path) -> None:
    """Save, and warn about any text that falls outside the figure (the figures are not re-viewed by eye)."""
    fig.canvas.draw()
    r = fig.canvas.get_renderer()
    W, H = fig.bbox.width, fig.bbox.height
    for t in fig.findobj(matplotlib.text.Text):
        if not t.get_visible() or not t.get_text() or not t.get_window_extent(r).width:
            continue
        b = t.get_window_extent(r)
        if b.x0 < -1 or b.y0 < -1 or b.x1 > W + 1 or b.y1 > H + 1:
            print(f"  WARNING {out.name}: text clipped: {t.get_text()[:50]!r}")
    texts = [t for t in fig.findobj(matplotlib.text.Text) if t.get_visible() and t.get_text()]
    boxes = [(t.get_text(), t.get_window_extent(r)) for t in texts]
    for i, (a, ba) in enumerate(boxes):
        for c, bc in boxes[i + 1:]:
            if ba.overlaps(bc):
                print(f"  note {out.name}: text overlap {a[:30]!r} / {c[:30]!r}")
    fig.savefig(out, facecolor=SURFACE)
    plt.close(fig)


def fig_block_agreement(out: Path) -> None:
    rows = {(r["a"], r["b"]): r for r in RESULTS["exp1_block_agreement"]}
    pairs = [
        ("look_grid", "look from a different frame set (every 20 s)"),
        ("words", "words (transcript)"),
        ("motion:mid:mean", "motion (V-JEPA 2 clips)"),
        ("sound:mid:mean", "sound (EAT audio)"),
        ("colour", "colour and light statistics"),
        ("time", "time (shot lengths, cutting, motion energy)"),
    ]
    data = [(label, rows[("look:mean", b)]) for b, label in pairs]
    fig, ax = plt.subplots(figsize=(8.6, 4.0), dpi=110)
    fig.patch.set_facecolor(SURFACE)
    style_axes(ax)
    ys = list(range(len(data)))[::-1]
    for y, (label, r) in zip(ys, data):
        ax.barh(y, r["overlap"], height=0.55, color=BLUE, zorder=2)
        ax.plot([r["overlap_chance"]] * 2, [y - 0.36, y + 0.36], color=INK, linewidth=1.6, zorder=3)
        ax.text(r["overlap"] + 0.012, y, f"{r['overlap']:.2f}", va="center", ha="left", fontsize=10, color=INK)
        n = f"  ({r['n']} films)" if r["n"] != 128 else ""
        ax.text(-0.012, y, label + n, va="center", ha="right", fontsize=10, color=INK)
    ax.set_yticks([])
    ax.set_xlim(0, 1)
    ax.set_xlabel("top-10 overlap with the look block's neighbour lists", fontsize=9.5, color=INK_2)
    ax.set_title("How far look neighbours agree with each other block", loc="left", fontsize=13, color=INK,
                  fontweight="bold", x=-0.62, pad=24)
    ax.text(-0.62, 1.03, "Blue bar: measured overlap. Black tick: chance (k / (n - 1)). 1.0 would mean identical lists.",
            transform=ax.transAxes, fontsize=9.5, color=INK_2)
    fig.subplots_adjust(left=0.40, right=0.97, top=0.82, bottom=0.14)
    save_checked(fig, out)


def fig_stills_needed(out: Path) -> None:
    sub = RESULTS["exp3_subsampling"]
    series = [
        ("look:mean", "look: n shot frames per film", BLUE, "o"),
        ("sound:mid:mean", "sound: n 10-s windows per film (72 films)", ORANGE, "s"),
    ]
    fig, ax = plt.subplots(figsize=(8.0, 4.4), dpi=110)
    fig.patch.set_facecolor(SURFACE)
    style_axes(ax)
    ax.grid(axis="y", color=GRID, linewidth=0.8)
    for key, label, col, mk in series:
        rows = sub[key]["rows"]
        xs = [r["n_requested"] for r in rows]
        ys = [r["overlap_mean"] for r in rows]
        sd = [r["overlap_sd"] for r in rows]
        ax.errorbar(xs, ys, yerr=sd, color=col, marker=mk, markersize=7, linewidth=2, capsize=3,
                    markeredgecolor=SURFACE, markeredgewidth=1.5, label=label, zorder=3)
        chance = rows[0]["overlap_chance"]
        ax.axhline(chance, color=NEUTRAL, linestyle=(0, (4, 3)), linewidth=1.2, zorder=1)
    ax.text(330, sub["look:mean"]["rows"][0]["overlap_chance"] - 0.035, "chance, 128 films", fontsize=9,
            color=INK_2, ha="right")
    ax.text(330, sub["sound:mid:mean"]["rows"][0]["overlap_chance"] + 0.015, "chance, 72 films", fontsize=9,
            color=INK_2, ha="right")
    look10 = next(r for r in sub["look:mean"]["rows"] if r["n_requested"] == 10)
    ax.annotate(f"10 stills: {look10['overlap_mean']:.2f}", (10, look10["overlap_mean"]), xytext=(14, 0.36),
                fontsize=9.5, color=INK, arrowprops=dict(arrowstyle="-", color=NEUTRAL, linewidth=1))
    ax.set_xscale("log", base=2)
    ax.set_xticks([3, 5, 10, 20, 40, 80, 160, 320])
    ax.set_xticklabels(["3", "5", "10", "20", "40", "80", "160", "320"])
    ax.set_ylim(0, 1.02)
    ax.set_yticks([0, 0.2, 0.4, 0.6, 0.8, 1.0])
    ax.set_xlabel("frames or windows sampled per film (5 random draws; bars are 1 sd)", fontsize=9.5, color=INK_2)
    ax.set_ylabel("top-10 overlap with the whole-film list", fontsize=9.5, color=INK_2)
    ax.set_title("How much of a film is needed to recover its neighbours", loc="left", fontsize=13, color=INK,
                 fontweight="bold")
    ax.legend(loc="upper left", frameon=False, fontsize=9.5, labelcolor=INK)
    fig.subplots_adjust(left=0.10, right=0.97, top=0.90, bottom=0.14)
    save_checked(fig, out)


def fig_leaks(out: Path) -> None:
    share = RESULTS["exp5_leaks"]["look:mean"]["share"]
    attrs = [
        ("lead_actor", "same lead actor"),
        ("director", "same director"),
        ("decade", "same decade"),
        ("silent_or_sound", "both silent or both sound"),
        ("country", "same country"),
        ("colour_class", "same colour process"),
        ("kind", "same kind (fiction, documentary, ...)"),
    ]
    fig, ax = plt.subplots(figsize=(8.6, 4.0), dpi=110)
    fig.patch.set_facecolor(SURFACE)
    style_axes(ax)
    ys = list(range(len(attrs)))[::-1]
    for y, (key, label) in zip(ys, attrs):
        v, c = share[key]["top_k"], share[key]["chance"]
        lift = v / c
        ax.barh(y, lift, height=0.55, color=BLUE, zorder=2)
        ax.text(lift + 0.08, y, f"{lift:.1f}x   ({v:.1%} vs {c:.1%})", va="center", ha="left", fontsize=9.5,
                color=INK)
        ax.text(-0.1, y, label, va="center", ha="right", fontsize=10, color=INK)
    ax.axvline(1, color=INK, linewidth=1.4, zorder=3)
    ax.set_ylim(-1.1, len(attrs) - 0.5)
    ax.text(1.08, -0.85, "chance = 1x", fontsize=9, color=INK_2, va="center")
    ax.set_yticks([])
    ax.set_xlim(0, 10)
    ax.set_xlabel("share of the 10 nearest look neighbours with the same label, divided by chance", fontsize=9.5,
                  color=INK_2)
    ax.text(-0.52, 1.04, "In brackets: share of neighbours with the label vs share of all other films with it.",
            transform=ax.transAxes, fontsize=9.5, color=INK_2)
    ax.set_title("What the look block's neighbours share (128 films)", loc="left", fontsize=13, color=INK,
                 fontweight="bold", x=-0.52, pad=26)
    fig.subplots_adjust(left=0.36, right=0.97, top=0.82, bottom=0.14)
    save_checked(fig, out)


def main() -> None:
    k = NEIGHBOURS["k"]
    hubs = hub_counts()
    contact_sheet(
        "Q272599", 4,
        "Look neighbours of All Quiet on the Western Front (1930)",
        "Four of eight frames per film, spread over the running time. Look block (DINOv2, mean over shots), 128 films. "
        "Similarity = 1 - cosine distance.",
        HERE / "neighbours_war.jpg",
    )
    diary = [x["id"] for x in NEIGHBOURS["blocks"]["look"]["Q569699"]["neighbours"][:4]]
    hub_note = ", ".join(f"{CATALOG[i]['title']} {hubs[i]}" for i in diary)
    contact_sheet(
        "Q569699", 4,
        "A weak list: look neighbours of Diary of a Lost Girl (1929)",
        f"Times each neighbour appears in the {len(NEIGHBOURS['blocks']['look'])} look top-{k} lists "
        f"(mean {k}): {hub_note}.",
        HERE / "neighbours_failure.jpg",
    )
    fig_block_agreement(HERE / "block_agreement.png")
    fig_stills_needed(HERE / "stills_needed.png")
    fig_leaks(HERE / "leaks.png")
    total = 0
    for p in sorted(HERE.glob("*.[jp][pn]g")):
        total += p.stat().st_size
        print(f"{p.name:24s} {p.stat().st_size / 1024:7.1f} KB")
    print(f"{'total':24s} {total / 1024:7.1f} KB")


if __name__ == "__main__":
    main()
