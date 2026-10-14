"""film2vec experiments: contact sheets of seed films and their neighbours, for judging by eye.

Throwaway experiment code. Reads results/neighbours.json (analyse.py) and the thumbs directory (thumbs.py) and
writes ONE self-contained HTML file with the frames embedded, so it can be moved or sent.

    sheets.py [--neighbours results/neighbours.json] [--thumbs DIR] [--out FILE] [--seeds id1,id2,...]
              [--max-seeds 16] [--max-neighbours 5] [--max-mb 15]

Default output: <home>/experiments/film2vec/sheets.html. Frames of public-domain films; the file stays in the
cache and never goes in the repository. Each frame is embedded once however often its film appears. If the
file would pass --max-mb the frames are re-encoded smaller. A film without thumbs shows its title only.
"""

from __future__ import annotations

import argparse
import base64
import html
import io
import json
import os
from pathlib import Path

HERE = Path(__file__).resolve().parent
BLOCKS = ["look", "time", "sound", "fused"]
FALLBACK = {"fused": "fused:look+time"}  # silents have no sound, so no three-block fusion
LABELS = {
    "look": "Look",
    "time": "Time",
    "sound": "Sound",
    "fused": "Fused (look + time + sound)",
    "fused:look+time": "Fused (look + time; this film has no sound block)",
}
PICK = [0, 2, 5, 7]  # four of the eight frames, spread over the running time
SHRINK = [(180, 70), (144, 65), (120, 60), (96, 55), (72, 50)]  # (height, JPEG quality) tried in turn

CSS = """
:root { color-scheme: light dark; --bg:#fafafa; --fg:#1a1a1a; --dim:#666; --line:#d8d8d8; --card:#fff; }
@media (prefers-color-scheme: dark) {
  :root { --bg:#141414; --fg:#e8e8e8; --dim:#9a9a9a; --line:#333; --card:#1c1c1c; }
}
* { box-sizing: border-box; }
body { margin: 0; padding: 16px; background: var(--bg); color: var(--fg);
       font: 14px/1.4 -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; }
h1 { font-size: 20px; margin: 0 0 4px; }
p.note { color: var(--dim); margin: 0 0 20px; max-width: 80ch; }
nav { margin: 0 0 24px; display: flex; flex-wrap: wrap; gap: 4px 14px; }
a { color: inherit; }
section { border-top: 2px solid var(--line); padding: 18px 0 26px; }
h2 { font-size: 18px; margin: 0 0 8px; }
h2 span, .cap span { color: var(--dim); font-weight: normal; }
h3 { font-size: 13px; text-transform: uppercase; letter-spacing: .06em; color: var(--dim); margin: 0 0 8px; }
.blocks { display: grid; grid-template-columns: repeat(auto-fit, minmax(min(100%, 430px), 1fr)); gap: 18px 24px;
          margin-top: 16px; }
.block { background: var(--card); border: 1px solid var(--line); border-radius: 6px; padding: 10px 12px; }
.row { display: flex; flex-wrap: wrap; align-items: center; gap: 4px 10px; margin: 0 0 8px; }
.strip { display: flex; gap: 2px; flex: none; max-width: 100%; overflow-x: auto; }
.t { display: block; height: 66px; flex: none; background: #000 center / 100% 100% no-repeat; border-radius: 2px; }
.seed .t { height: 132px; }
.cap { flex: 1 1 120px; min-width: 120px; }
.cap small { color: var(--dim); display: block; }
.none { color: var(--dim); font-style: italic; }
"""


def cache_home() -> Path:
    env = os.environ.get("ART2VEC_HOME")
    return Path(env).expanduser() if env else Path.home() / "Library" / "Caches" / "art2vec"


class Images:
    """Each film's frames, read once and referenced by CSS class."""

    def __init__(self, thumbs: Path) -> None:
        self.thumbs = thumbs
        self.items: dict[tuple[str, int], dict] = {}

    def film(self, fid: str) -> list[dict]:
        out = []
        for i in PICK:
            key = (fid, i)
            if key not in self.items:
                path = self.thumbs / fid / f"{i:02d}.jpg"
                if not path.is_file() or path.stat().st_size < 600:
                    continue
                data = path.read_bytes()
                try:
                    from PIL import Image

                    with Image.open(io.BytesIO(data)) as im:
                        w, h = im.size
                except Exception:
                    continue  # not a picture
                self.items[key] = {"cls": f"i{len(self.items)}", "data": data, "w": w, "h": h}
            out.append(self.items[key])
        return out

    def total_bytes(self) -> int:
        return sum(len(v["data"]) for v in self.items.values()) * 4 // 3

    def shrink(self, height: int, quality: int) -> None:
        from PIL import Image

        for v in self.items.values():
            with Image.open(io.BytesIO(v["data"])) as im:
                if im.height > height:
                    im = im.convert("RGB").resize((max(1, round(im.width * height / im.height)), height), Image.LANCZOS)
                buf = io.BytesIO()
                im.convert("RGB").save(buf, "JPEG", quality=quality, optimize=True)
            if len(buf.getvalue()) < len(v["data"]):
                v["data"] = buf.getvalue()

    def css(self) -> str:
        return "\n".join(
            f".{v['cls']}{{background-image:url(data:image/jpeg;base64,{base64.b64encode(v['data']).decode()})}}"
            for v in self.items.values()
        )


def strip(images: Images, fid: str) -> str:
    frames = images.film(fid)
    if not frames:
        return ""
    cells = "".join(f'<i class="t {v["cls"]}" style="aspect-ratio:{v["w"]}/{v["h"]}"></i>' for v in frames)
    return f'<div class="strip">{cells}</div>'


def title_of(entry: dict) -> str:
    year = f" <span>({html.escape(str(entry['year']))})</span>" if entry.get("year") else ""
    return f"{html.escape(str(entry.get('title') or entry.get('id') or ''))}{year}"


def choose_seeds(nb: dict, thumbs: Path, wanted: list[str] | None, max_seeds: int) -> list[str]:
    blocks = nb["blocks"]
    known: dict[str, dict] = {}
    for b in BLOCKS + list(FALLBACK.values()):
        for fid, e in blocks.get(b, {}).items():
            known.setdefault(fid, e)
    if wanted:
        return [i for i in wanted if i in known][:max_seeds]
    with_thumbs = [i for i in known if (thumbs / i / f"{PICK[0]:02d}.jpg").is_file()]
    pool = with_thumbs if len(with_thumbs) >= min(max_seeds, len(known)) else list(known)
    pool.sort(key=lambda i: (str(known[i].get("year") or ""), i))  # by year, so the seeds span the catalog
    if len(pool) <= max_seeds:
        return pool
    return [pool[round(j * (len(pool) - 1) / (max_seeds - 1))] for j in range(max_seeds)]


def build(nb: dict, images: Images, seeds: list[str], max_neighbours: int) -> str:
    blocks = nb["blocks"]
    sections, nav = [], []
    for fid in seeds:
        entry = next(blocks[b][fid] for b in blocks if fid in blocks[b])
        nav.append(f'<a href="#{html.escape(fid)}">{html.escape(str(entry.get("title") or fid))}</a>')
        seed_strip = strip(images, fid) or '<span class="none">no thumbs</span>'
        parts = [f'<section id="{html.escape(fid)}"><h2>{title_of(entry)}</h2><div class="row seed">{seed_strip}</div>',
                 '<div class="blocks">']  # fmt: skip
        for b in BLOCKS:
            name = b if fid in blocks.get(b, {}) else FALLBACK.get(b, b)
            parts.append(f'<div class="block"><h3>{html.escape(LABELS.get(name, name))}</h3>')
            if fid not in blocks.get(name, {}):
                parts.append('<div class="none">this film is not in this block</div></div>')
                continue
            for rank, n in enumerate(blocks[name][fid]["neighbours"][:max_neighbours], 1):
                cap = f'<div class="cap">{rank}. {title_of(n)}<small>distance {n["distance"]:.3f}</small></div>'
                parts.append(f'<div class="row">{strip(images, n["id"])}{cap}</div>')
            parts.append("</div>")
        parts.append("</div></section>")
        sections.append("".join(parts))
    return "\n".join(["<nav>" + "".join(nav) + "</nav>", *sections])


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    exp = cache_home() / "experiments" / "film2vec"
    ap.add_argument("--neighbours", default=str(HERE / "results" / "neighbours.json"))
    ap.add_argument("--thumbs", default=str(exp / "thumbs"))
    ap.add_argument("--out", default=str(exp / "sheets.html"))
    ap.add_argument("--seeds", help="comma list of seed film ids; default: spread over the catalog by year")
    ap.add_argument("--max-seeds", type=int, default=16)
    ap.add_argument("--max-neighbours", type=int, default=5)
    ap.add_argument("--max-mb", type=float, default=15.0)
    args = ap.parse_args()

    nb = json.loads(Path(args.neighbours).read_text())
    thumbs = Path(args.thumbs)
    wanted = [x.strip() for x in args.seeds.split(",") if x.strip()] if args.seeds else None
    seeds = choose_seeds(nb, thumbs, wanted, args.max_seeds)
    if not seeds:
        print("no seed films: neighbours.json has none of the blocks " + ", ".join(BLOCKS))
        return 1
    images = Images(thumbs)
    body = build(nb, images, seeds, args.max_neighbours)
    budget = args.max_mb * 1e6 - len(body) - 20_000
    for height, quality in SHRINK:
        if images.total_bytes() <= budget:
            break
        images.shrink(height, quality)
    n_films = len({k[0] for k in images.items})
    note = (f"{len(seeds)} seed films; for each, its nearest {min(args.max_neighbours, nb.get('k', 0))} films in each "
            f"block. Four frames per film, from 10 %, 33 %, 67 % and 90 % of the running time. Smaller distance = "
            f"nearer (cosine).")  # fmt: skip
    doc = (f'<!doctype html>\n<html lang="en"><head><meta charset="utf-8">'
           f'<meta name="viewport" content="width=device-width, initial-scale=1">'
           f"<title>film2vec contact sheets</title>\n<style>{CSS}\n{images.css()}</style></head>\n<body>"
           f'<h1>film2vec contact sheets</h1><p class="note">{note}</p>\n{body}\n</body></html>\n')  # fmt: skip
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(doc, encoding="utf-8")
    size = out.stat().st_size / 1e6
    print(f"wrote {out}: {size:.2f} MB, {len(seeds)} seeds, {len(images.items)} frames of {n_films} films")
    if size > args.max_mb:
        print(f"WARNING: over the {args.max_mb} MB limit even at the smallest frame size")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
