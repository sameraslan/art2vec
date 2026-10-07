# art2vec: architecture

How the library is built. `FRAMEWORK.md` says why and what; this says how, and answers the questions its section 10 leaves to the design. When the two disagree, the framework wins until it is changed.

Status: layout adopted 6 October 2026. Code is being extracted from recmyrecord's `data-pipeline/` with no behaviour change. The module tables below list what exists and what is planned; a planned module does not exist as a file until its code does, so that `import art2vec.fusion` fails loudly rather than succeeding on a docstring.

## 1. Shape

One distribution, `art2vec`, with one package per concern at the top of the repository:

```
art2vec/            the core: works, blocks, the medium protocol, the registry, the cache
album2vec/          the first medium: its FRAMEWORK.md, its descriptor table, its code
tests/              mirrors the packages
```

Later media are siblings of `album2vec/` (`painting2vec/`, `film2vec/`, `book2vec/`), each a self-contained folder holding its framework extension, its committed tables and its code. The convention is the name: a top-level folder ending in `2vec` other than `art2vec` is a medium, and `tests/test_layering.py` finds media that way. The core never imports a medium except by name through the registry (section 3); the same test enforces the direction.

Why one distribution and not one per medium: at one to four media, separate packages add release and pinning work and give nothing that optional extras do not. `art2vec` alone depends on numpy and platformdirs; each medium's heavy dependencies arrive with its code as the extra of the same name (`art2vec[album]`). The cost of two top-level packages in one wheel is that `pip install art2vec` also claims the import name `album2vec`; accepted, because the folder is the unit a reader opens. If an outside party ever ships a medium, the registry grows an entry-point group; not before.

Why a flat layout and not `src/`: so that `album2vec/` is one folder a reader opens to find everything about albums, framework included.

## 2. The three questions, and one chore, as code

```python
class Medium(Protocol):
    name: str                                   # "album"
    version: str                                # bumps when encoder or descriptor table changes
    def canon(self) -> list[Work]: ...          # the only place reception data is read
    def fetch(self, works: Sequence[Work]) -> None: ...   # artefacts into the cache; network lives here
    def encode(self, works: Sequence[Work]) -> list[Block]: ...   # one or more content blocks
    def describe(self, works: Sequence[Work]) -> Block: ...       # the felt block
```

- The three questions are `canon`, `encode` and `describe`. `fetch` is the chore that makes `encode` possible offline; it answers nothing about the work.
- `Work` is a frozen dataclass: `id` (a string, the medium's stable key), `title`, `creator`, `year`, `medium`, `extras` (left out of equality and hashing). Nothing about ratings or counts; the canon may read them but does not pass them on.
- `Block` is a named matrix with its row ids: `name` ("sound", "words", "felt"), `kind` ("content" or "felt"), `medium`, `ids` (strings, the same as `Work.id`), `vectors` (float32, coerced), `model`, `version`, and a `LeakNote`. A work with no data for a block is simply absent from its `ids`; nothing is imputed (framework section 6).
- `LeakNote` records what the encoder or source saw besides the work ("Discogs genre and style labels", "crowd descriptors from RateYourMusic") and which leak checks were run.
- `fetch` is separate from `encode` so that `encode` is pure (cached artefact in, vector out), tests run on local files without the network, and fetching can retry and run in threads on its own.
- `encode` is called once per shard of about 1,000 works and must treat each work independently, so a shard can be written and a later run can skip shards already on disk. Anything that needs the whole set (centring, a frozen PCA basis, the variance scale) is a fitted, versioned transform stored beside the vectors and applied when blocks are loaded. Synchronous; no async.

A `Protocol` rather than a base class: a medium inherits nothing and the core only type-checks. scikit-learn's conventions apply to anything fitted in the core (`fit` returns `self`, fitted state ends in an underscore, parameters are plain constructor arguments).

## 3. Registry

```python
MEDIA = {"album": "album2vec.medium:AlbumMedium"}   # art2vec/registry.py
load_medium("album")                                # imports the dotted path on demand
```

A string per medium, imported lazily, so `import art2vec` never loads an audio model. A missing extra raises an `ImportError` that names the extra to install.

## 4. The core, module by module

Exists:

| Module | Does | Extracted from |
|---|---|---|
| `art2vec/work.py` | `Work` | `rmr_catalog` rows |
| `art2vec/medium.py` | `Medium`, `Block`, `LeakNote` | new |
| `art2vec/registry.py` | `MEDIA` and `load_medium` | new |
| `art2vec/cache.py` | `ART2VEC_HOME`, default from platformdirs, `CACHEDIR.TAG` | `.cache/` conventions |

Planned, in extraction order:

| Module | Does | Extracted from |
|---|---|---|
| `art2vec/store.py` | vectors on disk: safetensors shards of about 1,000 works per block with the ids in the shard's string metadata, a manifest naming medium, model and version, the fitted transform beside them; append-only, temp-file-then-rename | `rmr_pipeline/audio_store.py` (npz shards), `audio.py` (transform) |
| `art2vec/fusion.py` | load blocks, refuse mixed versions of one medium, scale every block to the same total variance, combine content blocks and the felt block with one weight, honour absent rows | `rmr_pipeline/audio.py site_matrix`, `table.py rec_matrix` (the same formula written twice; one copy survives) |
| `art2vec/neighbours.py` | k nearest by Euclidean distance; filters that never alter distances; optional hub correction | `rmr_pipeline/recs.py` |
| `art2vec/layout.py` | 2D projection per stop, aligned across stops; extra `layout` | `rmr_pipeline/layout.py` |
| `art2vec/export.py` | parquet for vectors and metadata; compact JSON of neighbours and positions for a site | `rmr_pipeline/build.py` (the general half) |
| `art2vec/cli.py` | `art2vec build`, `neighbours`, `export`; argparse; a re-run resumes by shard | `python -m rmr_pipeline` |

Later, when needed: `paths.py` (chains of small steps between works), `align.py` (cross-medium anchors). Configuration is environment variables read where they are needed (`ART2VEC_HOME`, later `ART2VEC_ALBUM_*`); there is no settings object and no config file until two modules need the same value.

## 5. album2vec, module by module

Exists (`canon`, `fetch` and `sound` raise `NotImplementedError` until extracted):

| Module | Does | Extracted from |
|---|---|---|
| `album2vec/FRAMEWORK.md` | the rules applied to albums | new |
| `album2vec/descriptors.csv` | every RateYourMusic descriptor sorted into the four kinds with a reason | new |
| `album2vec/medium.py` | `AlbumMedium` | new |
| `album2vec/felt.py` | read `descriptors.csv`, keep kind 1, weight by page position: the felt block | `rmr_pipeline/audio.py descriptors`, `vocab.py` |
| `album2vec/canon.py` | RateYourMusic chart sheet export to `Work`s; append-only order | `rmr_catalog/` |
| `album2vec/fetch.py` | find each track's preview on Deezer or Apple (text folding, fuzzy matching, HTTP cache); download clips and YouTube full-length windows into the artefact cache; never write audio elsewhere | `rmr_audio/match.py`, `matchnew.py`, `textnorm.py`, `embed.py` (download half), `fulllength.py`, `windows.py`, `clips.py` |
| `album2vec/sound.py` | Discogs-EffNet per clip, mean per album: the sound block; L2, centre, frozen PCA to 64 and the variance scale are its transform | `rmr_audio/embed.py` (model half), `rmr_pipeline/audio.py` (transform) |

Planned: `album2vec/words.py`, speech recognition over the clips and a text embedder on the words only (decided 6 October 2026, built after the extraction). Its dependencies and scikit-learn for the PCA join the `album` extra with the code.

What stays in recmyrecord and does not enter the library: cover sprites and atlases, slugs, ambient colours, clusters, the frontend data contract and its validator, the In Rainbows regression row, Spotify-era keys. The site calls `art2vec` for vectors, neighbours, positions and the felt words, and adds its own presentation on top. One wheel ships `album2vec/descriptors.csv` (the code reads it) and not the Markdown.

## 6. Storage

```
$ART2VEC_HOME/                      default: platformdirs user cache dir, e.g. ~/Library/Caches/art2vec
  CACHEDIR.TAG
  artefacts/album/<work id>/...     fetched clips, decoded on demand; never committed, never shipped
  vectors/album/<block>@<model>@<version>/
    part-0000.safetensors           vectors (float32), ~1,000 works; the ids as a JSON list in the string metadata
    transform.safetensors           the fitted centre, basis and scale, if the block has one
    manifest.json                   medium, model, version, dims, shard list, leak note
  http/                             request cache for matching
```

Model weights stay in their own hub caches; only derived data goes under `ART2VEC_HOME`. Resumability is by shard: a shard exists or it does not, and writes go to a temporary file then rename. Interrupted jobs restart where they stopped. Everything after `fetch` runs offline.

## 7. Versioning

- The framework has a status line with a date. The architecture has the same.
- A medium has a `version`. It changes when the encoder, the artefact definition or the descriptor table changes. Vectors carry `model@version`; the core refuses to fuse blocks from different versions of one medium.
- The distribution follows semantic versioning once it is on PyPI; before 1.0 the minor number may break.
- The artefact of a work is the release the canon lists. A remaster or deluxe edition is a different release and is not the work unless the canon says so.
- A canon refresh appends. Works that leave the chart stay in the catalog, flagged, so ids and order never shift.

## 8. Weights and dimensions

- Default felt weight: the medium's choice, recorded with its vectors. album2vec ships recmyrecord's three stops (`s` = 5, 1.765, 0.5 on a cube curve) until the experiments in `album2vec/FRAMEWORK.md` section 6 say otherwise.
- Dimension reduction is a medium's choice and part of its `encode`: the sound block is PCA to 64 with a frozen basis. The core never reduces.

## 9. Evaluation protocol

The protocol, to be expanded the first time an evaluation runs under it:

- Leak checks: genre make-up of the top 10 by family, source and store probe accuracy, same-artist share, hubness (lists per work, share in none, skew). Run on every new block; reported, never optimised.
- Listening and looking: a committed seed set per medium (recmyrecord's 21 and 38 seeds are the start), lists side by side with names hidden, one label per list, stored as a CSV in the experiment folder with the date and the listener's consent to be named or not.
- Path tests: a small step is one whose distance is under the median nearest-neighbour distance of the catalog; a crossing is a step between genre families. Both numbers are reported per path.
- Held-out splits are committed and marked spent once scored.

## 10. Accepting a medium

A pull request that adds a medium contains: its folder with `FRAMEWORK.md` (the extension), the committed descriptor table with reasons, a `LeakNote` for every encoder and source, a fixture of a dozen works with local artefacts so tests run offline, the regression set (seed works and their expected neighbours), and its row in the registry. Nothing in the core changes unless a new shared capability is needed.

## 11. Tooling

uv for environments (`uv.lock` is committed), hatchling to build, ruff to lint and format, pytest, mypy strict on `art2vec/` and basic on media, `py.typed` shipped. One GitHub Actions workflow: lint, type-check and test on Python 3.11 and 3.13. A job for the `album` extra is added when the extra has contents. No pre-commit.

## 12. Glossary

- **Canon**: the set of works a medium explores, chosen by reception.
- **Artefact**: the raw thing the encoder reads (clips, an image, text).
- **Block**: one named matrix of vectors over the works, content or felt.
- **Felt**: short for felt response, what a work does to a person; the one human-sourced block (FRAMEWORK.md section 5).
- **Descriptor**: a word a crowd attached to a work; sorted into four kinds, of which only the felt kind enters a distance.
- **Stop**: a preset value of the felt weight (sound, balanced, mood).
- **Leak**: human or textual information that enters a distance by a route other than the artefact.
- **Path**: a chain of small steps from one work to another.
