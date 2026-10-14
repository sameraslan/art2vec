# art2vec

Content-only similarity for art. Start from a work you love, see what sits next to it in the work itself, and walk outward one small step at a time.

Two rules and one exception: reception picks the set, the work picks the neighbours, and the one human signal allowed in a distance is how the work makes people feel. Every work gets two positions, one by what it is made of and one by what it does to people (for an album, **sounds like** and **feels like**), and one control between them. The reasoning is in [FRAMEWORK.md](FRAMEWORK.md); the design is in [ARCHITECTURE.md](ARCHITECTURE.md).

Media are plugins that answer three questions: `canon()` which works are in the set, `encode()` what a work is as content vectors, `describe()` how it makes people feel. One chore, `fetch()`, puts the artefacts in the cache first. The first medium is [album2vec](src/art2vec/album2vec/FRAMEWORK.md), extracted from [recmyrecord](https://github.com/sameraslan/recmyrecord).

## film2vec proof of concept

film2vec places films by their frames, motion, sound and transcript. A first test ran on 128 films from 1916 to 1968 that are in the US public domain.

![Look-block neighbours of All Quiet on the Western Front](experiments/film2vec/figures/neighbours_war.jpg)

By look alone, the three nearest films to All Quiet on the Western Front are First World War films by other directors.

![Top-10 overlap of look neighbours with each other block](experiments/film2vec/figures/block_agreement.png)

Words, motion, sound, colour and time each share only 16% to 35% of the look block's top-10 neighbours, so each block gives its own list.

More figures, including a neighbour list that fails, are in the [gallery](experiments/film2vec/figures/README.md). The full tables are in [RESULTS.md](experiments/film2vec/results/RESULTS.md).

## Status

Early. The framework, the layout, the medium protocol and the descriptor table are in place; the album code is being extracted from recmyrecord's pipeline with no behaviour change, and `canon`, `fetch` and `sound` raise until it lands. Nothing is on PyPI yet and the licence is still to be chosen.

## Install

```bash
uv pip install -e ".[album,dev]"
```

`art2vec` alone is light (numpy, platformdirs). `art2vec[album]` will add the audio stack as the album code lands.

## Use

What works today:

```python
from art2vec import load_medium
from art2vec.album2vec import felt

album = load_medium("album")      # the Medium protocol, lazily imported
felt.felt_words()                 # the descriptors that enter the distance
```

The target, once fusion and neighbours are extracted:

```python
works = album.canon()
album.fetch(works)
blocks = album.encode(works) + [album.describe(works)]
space = fuse(blocks, felt_weight=0.5)
neighbours(space, work_id=..., k=10)
```

## Layout

```
FRAMEWORK.md              the rules
ARCHITECTURE.md           the design
src/art2vec/              the core
src/art2vec/album2vec/    the first medium: its framework, its descriptor table, its code
tests/                    mirrors the package
```

## Contributing

Read `FRAMEWORK.md` first; `ARCHITECTURE.md` section 10 says what a new medium needs. Changes to either document go in their own pull request with the reason.
