# art2vec

Content-only similarity for art. Start from a work you love, see what sits next to it in the work itself, and walk outward one small step at a time.

Two rules and one exception: reception picks the set, the work picks the neighbours, and the one human signal allowed in a distance is how the work makes people feel. Every work gets two positions, one by what it is made of and one by what it does to people (for an album, **sounds like** and **feels like**), and one control between them. The reasoning is in [FRAMEWORK.md](FRAMEWORK.md); the design is in [ARCHITECTURE.md](ARCHITECTURE.md).

Media are plugins that answer three questions: `canon()` which works are in the set, `encode()` what a work is as content vectors, `describe()` how it makes people feel. One chore, `fetch()`, puts the artefacts in the cache first. The first medium is [album2vec](src/art2vec/album2vec/FRAMEWORK.md), extracted from [recmyrecord](https://github.com/sameraslan/recmyrecord).

## book2vec proof of concept

book2vec is the novels medium. A proof of concept on 87 public-domain novels compares separate blocks: Prose, Telling, World, Story and Felt. Story and Felt cover 24 of the novels. The setup and results are in [experiments/book2vec](experiments/book2vec/README.md), and more figures are in the [gallery](experiments/book2vec/figures/README.md).

![Heatmap of AUC by pair type for four book2vec blocks](experiments/book2vec/figures/block_scorecard.png)

Each block passes different tests: two translations of one novel are near in Telling and World, and the style encoder puts them apart.

![Position of the other translation in each novel's neighbour list, by block](experiments/book2vec/figures/translation_ranks.png)

Where a novel's other translation ranks among the 86 other novels, under each block.

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
