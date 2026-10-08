# Album audio to vector: design

Date: 8 October 2026. Status: awaiting review.

## 1. Goal

Anyone can install art2vec from PyPI, hand it an album as audio files, and get a vector back, with a few functions for comparing vectors. The code is the sound encoder from recmyrecord's pipeline, carried over so that its vectors stay interchangeable with recmyrecord's existing store, and published to the standard of a library many people will read.

Success means:

1. `pip install "art2vec[album]"` works on Linux, macOS and Windows with no system packages and no compiler.
2. `album2vec.embed(folder)` returns a 1,280-number vector for a folder of ordinary audio files.
3. For the same audio, the vector matches recmyrecord's Essentia pipeline closely enough that the ten nearest neighbours in the 10k catalogue are unchanged (section 9).
4. The repository carries the files, checks and conventions expected of a public library (section 8).

## 2. Scope

In scope: the path from local audio files to a vector, two functions on vectors, a command line, packaging, and the repository standards.

Out of scope, each a later piece built on this one:

- The catalogue path: `canon`, `fetch`, preview matching on Deezer and Apple, full-length fetching. No audio-acquisition code ships in this piece.
- `sound.block`, the store, fusion, the felt block, layouts and export. `sound.block` stays a stub and will call the encoder introduced here.
- The 64-dimension reduction. Its fitted transform was derived from store previews and its redistribution status is unsettled.
- CLAP and any second encoder.
- Trying a higher-quality resampler (section 5.3).

## 3. Decisions

| Decision | Choice | Reason |
|---|---|---|
| Model | Discogs-EffNet, MTG's official ONNX export `discogs-effnet-bsdynamic-1` | The encoder recmyrecord uses; same network as its TensorFlow graph |
| Runtime | `onnxruntime` with our own numpy front end | Essentia is AGPL-3.0, has no Windows or Linux ARM wheels, and its current Apple Silicon wheels need macOS 15 |
| Decoder | PyAV (`av`) | Wheels bundle the decoder, so no system ffmpeg; reads every format tested |
| Resampler to 16 kHz | A numpy copy of Essentia's `Resample(quality=4)` | The only choice that keeps vectors interchangeable with the store (section 9) |
| Weights | Downloaded from MTG's host on first use; never bundled, never mirrored | The weights are non-commercial and UPF's; the library stays permissive and redistributes nothing |
| Code licence | Apache-2.0 | `FRAMEWORK.md` section 11 recommendation |
| Output | The raw 1,280-dimension album mean, float32 | Needs no fitted artefact |

## 4. Public API

```python
from art2vec import album2vec

v = album2vec.embed("~/Music/In Rainbows")
library = album2vec.embed_many({"in rainbows": "~/Music/In Rainbows", "kid a": "~/Music/Kid A"})
album2vec.similarity(v, library.vectors[1])
album2vec.neighbours(library, "in rainbows", k=10)
```

```python
Source = str | Path | Sequence[str | Path]

def embed(source: Source) -> np.ndarray: ...
def embed_many(sources: Mapping[str, Source], *, errors: Literal["raise", "skip"] = "raise") -> Block: ...
def similarity(a: np.ndarray, b: np.ndarray) -> float: ...
def neighbours(block: Block, query: str | np.ndarray, k: int = 10) -> list[tuple[str, float]]: ...
```

- `embed` takes a folder, one file, or a list of files, and returns a float32 array of shape `(1280,)`. A folder is read recursively; files are ordered by natural sort of their relative path, which stands for track order. Files with extensions outside `.mp3 .m4a .flac .wav .ogg .opus .aiff .aif` are ignored in a folder and rejected in an explicit list.
- `embed_many` returns a `Block` named `sound`, kind `content`, medium `album`, with the model name, `AlbumMedium.version` and the existing `sound.LEAK` note. With `errors="skip"` an album that fails is absent from the block and logged; nothing is imputed.
- `similarity` is the cosine of two vectors.
- `neighbours` unit-normalises the block's rows and returns the `k` nearest by Euclidean distance as `(id, distance)`, nearest first, ties broken by row order. A query given as an id is excluded from its own result. These are neighbours in the raw space, not the catalogue's fused space; the docstring says so.

`similarity` and `neighbours` are defined in the core at `art2vec/neighbours.py`, exported from `art2vec`, and re-exported by `album2vec`.

Command line:

```bash
art2vec album embed PATH [PATH ...] [-o OUT.npy]
```

All paths form one album. With `-o` the vector is saved as `.npy`; without it the vector is printed as a JSON array.

## 5. Pipeline

```
files -> durations -> window plan -> for each window: decode -> mono 44.1 kHz
      -> 16 kHz -> mel patches -> model -> mean over patches
      -> mean over windows -> float32 (1280,)
```

### 5.1 Windows (`windows.py`)

Ported from recmyrecord `rmr_audio/windows.py` and `clips.priority_order` without change to the arithmetic:

- Windows are 30 s, kept 15 s clear of each file's ends.
- Up to eight windows are laid out, shared among files in proportion to duration and capped by how many fit.
- `n = clamp(round(total runtime / 5 min), 4, 8)` of them are used, chosen as the first `n` in bit-reversal priority order, so a smaller sample is always a spread subset of a larger one.
- A file of 30 to 60 s gets one centred window; a file under 30 s is its own window; a file under 5 s is skipped.

Only the `n` chosen windows are decoded and embedded. A single track follows the same rule.

### 5.2 Decoding (`audio.py`)

- Duration is read from the container, without decoding.
- A window is decoded sample-accurately: seek to the nearest earlier keyframe, decode forward, and discard samples before the window's first sample. recmyrecord's fast-seek ffmpeg call corrupts the first MP3 frame after a seek; this does not.
- Channels are averaged to mono. No loudness normalisation and no silence trimming, as in recmyrecord.
- A source that is not 44.1 kHz is brought to 44.1 kHz with `soxr` at its HQ setting.

### 5.3 Encoder (`effnet.py`)

The recipe verified in section 9:

1. 44.1 kHz to 16 kHz by linear interpolation that reproduces Essentia's `Resample(quality=4)`: the ratio held in float32, reading one input sample late, returning `floor(n * 160 / 441) + 1` samples.
2. Frames of 512 with hop 256, zero-padded by half a frame at the start, symmetric unnormalised Hann window, power spectrum.
3. 96 mel bands from 0 to 8,000 Hz, Slaney warping, unit-area triangles, then `log10(1 + 10000 * mel)`.
4. Patches of 128 frames with hop 62; frames that do not fill a patch are dropped.
5. Patches go to the ONNX graph in batches of 16: input `melspectrogram`, output `embeddings`, 1,280 numbers per patch.
6. The window's vector is the mean over its patches. The album's vector is the mean over its windows, taken in float64 and returned as float32.

recmyrecord rounds each stored vector to float16. This path does not; the difference is a cosine of 0.999999996 and changes no neighbour.

A proper anti-aliasing resampler moves vectors enough to change one or two of an album's ten neighbours. Whether it is better for the model is unknown and is a later experiment that would bump the medium version.

The session is created once per process and reused. `ART2VEC_ALBUM_THREADS` sets onnxruntime's thread count; unset, onnxruntime decides. One window is held in memory at a time; peak memory is about 300 MB.

### 5.4 Weights (`weights.py`)

- File: `https://essentia.upf.edu/models/feature-extractors/discogs-effnet/discogs-effnet-bsdynamic-1.onnx`, 18,027,718 bytes, SHA-256 `a280825b334797cf677939db8cd5762c0392aedd0ca6415dbc1cd083f045e43c`.
- Stored at `<ART2VEC_HOME>/models/`. Downloaded to a temporary name, checksum verified, then renamed into place. A file already present with the right checksum is used as it is, so a user can place it by hand and work offline.
- On download, a `WeightsLicenceNotice` warning states that the weights are copyright Universitat Pompeu Fabra, licensed for non-commercial use, with a link to `WEIGHTS-LICENSE.md` and to MTG's contact for a commercial licence.
- The tensor names are fixed in code. MTG's `.json` beside the ONNX file lists the TensorFlow names and is not used.

`cache.py`'s note that weights "stay in their own hub caches" is amended: this model has no hub, so it lives under `models/`.

## 6. Modules

| File | Purpose | Imports beyond numpy |
|---|---|---|
| `src/art2vec/album2vec/windows.py` | Which windows to sample | none |
| `src/art2vec/album2vec/audio.py` | Durations and decoding | `av`, `soxr` |
| `src/art2vec/album2vec/effnet.py` | Resampler, mel front end, model session | `onnxruntime` |
| `src/art2vec/album2vec/weights.py` | Fetch, verify and cache the model | standard library |
| `src/art2vec/album2vec/__init__.py` | `embed`, `embed_many`, re-exports | the above, lazily |
| `src/art2vec/neighbours.py` | `similarity`, `neighbours` | none |
| `src/art2vec/cli.py` | The `art2vec` command, on argparse | none |

Heavy imports stay inside functions, so `import art2vec.album2vec` works without the extra and the registry test keeps passing in the core job. A missing dependency raises `ImportError` naming `pip install "art2vec[album]"`.

`pyproject.toml`: the `album` extra becomes `onnxruntime`, `av` and `soxr`, each with a floor set to the oldest version the CI matrix passes on; `[project.scripts] art2vec = "art2vec.cli:main"`; the mypy override that relaxes `art2vec.album2vec.*` is removed, with missing-stub exemptions only for third-party modules that need them.

## 7. Errors

Messages follow the repository's convention: lowercase, no trailing full stop, naming the fix.

| Situation | Behaviour |
|---|---|
| Extra not installed | `ImportError` with the install command |
| Path does not exist, or a folder holds no audio | `FileNotFoundError` with the path |
| A file cannot be decoded | `AudioError` (a `ValueError`) naming the file and the decoder's reason |
| No file is long enough to embed | `AudioError` stating the 5 s minimum |
| Download fails | `OSError` with the URL, the destination path and the manual-placement instruction |
| Checksum mismatch | `OSError`; the bad file is removed, never used |
| Unknown id passed to `neighbours` | `KeyError` naming the id |

## 8. Repository standards

Added files:

- `CLAUDE.md`: states that art2vec is a public library held to a high open-source standard, and what that requires of every change: a typed and documented public surface, mypy strict, ruff clean, tests with the change, no media, weights or secrets committed, a changelog entry for anything a user can see, the repository's writing and naming conventions, and `FRAMEWORK.md` and `ARCHITECTURE.md` updated in the same change when a decision changes.
- `LICENSE` (Apache-2.0), `NOTICE`, and `WEIGHTS-LICENSE.md`, which gives the weights' terms, UPF's copyright, the two papers to cite, and the fact that MTG's pages name both CC BY-NC-SA 4.0 and CC BY-NC-ND 4.0.
- `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `SECURITY.md`, `CHANGELOG.md` (Keep a Changelog, semantic versioning), `CITATION.cff`, issue and pull-request templates.

Changed files:

- `pyproject.toml`: `license`, classifiers, URLs, version `0.1.0`. `AlbumMedium.version` becomes `0.1.0`.
- `README.md`: a quickstart built on section 4, and the weights notice.
- `FRAMEWORK.md`, `ARCHITECTURE.md`, `album2vec/FRAMEWORK.md`: the licence choice, the runtime decision, and the extraction rule restated as a measured tolerance (section 9).

Prose published under the author's name (`README.md`, the framework documents) is shown to him for approval before it is committed.

CI:

- The existing `core` job is unchanged.
- An `album` job installs the extra and runs the tests that need no model, on Linux, macOS and Windows with Python 3.11 and 3.13.
- A `model` job on Linux downloads the weights into a cache keyed by their checksum and runs the tests that need the model.
- A `package` job builds the wheel and sdist, installs the wheel into a clean environment, and runs `embed` on a generated file.
- A `release` workflow publishes to PyPI on a version tag by trusted publishing. The first publish is done by the author.

## 9. Parity with recmyrecord

Measured on 8 October 2026 against recmyrecord's Essentia environment (`essentia-tensorflow 2.1b6.dev1177`), on eight albums, 64 thirty-second windows, covering FLAC, ALAC and MP3 at 44.1, 48 and 96 kHz.

| Replaced | Cosine, minimum over 64 windows |
|---|---|
| TensorFlow graph by the ONNX graph, same mel patches | 1.000000000 |
| Essentia mel by the numpy front end | 1.000000000 |
| Essentia resampler by its numpy copy | 1.000000000 |
| Essentia resampler by soxr HQ | 0.963 |
| Whole pipeline, this design | 0.99991 |

At album level this design gave the same ten neighbours in the same order for seven albums and one swap of adjacent neighbours for the eighth, an MP3 album, traced to recmyrecord's fast-seek decode. With soxr in place of the resampler copy, seven of eight albums changed one or two neighbours.

The extraction rule in `album2vec/FRAMEWORK.md` (identical neighbours, no tolerance) is therefore restated: the encoder is reproduced exactly from identical samples; decoding differs from recmyrecord's by a measured amount, with the cause recorded.

Not yet verified, and covered by tests in this piece where a fixture can be generated: AAC, Ogg, Opus and WAV decoding, mono and multichannel sources, and windows shorter than 30 s. Platforms other than macOS arm64 are verified by the CI matrix.

## 10. Tests

No copyrighted audio enters the repository. Fixtures are synthetic signals with reference values produced once by Essentia.

- `windows`: the planning rules, ported from recmyrecord's `test_windows.py` and `test_clips.py`.
- `effnet` front end, no model: the resampler and the mel patches against stored Essentia references for synthetic signals.
- `audio`: generated WAV, FLAC, MP3, Ogg and M4A files; sample-accurate windows; mono, stereo and multichannel; 44.1, 48 and 96 kHz.
- `embed`, `embed_many`, CLI: the whole flow with a stub encoder, including every row of the error table.
- `weights`: download, checksum failure and reuse, against a local file server.
- `neighbours`: ordering, ties, self-exclusion, unknown ids.
- With the model: embeddings of the synthetic fixtures against stored reference vectors, and batch size independence.
- The real-music parity check stays a documented local script, since it needs private audio and the Essentia environment.

## 11. Open item

MTG's pages disagree on whether the weights are CC BY-NC-SA 4.0 or CC BY-NC-ND 4.0. Nothing here depends on the answer, because the library never modifies or redistributes the weights. The author will ask MTG which governs and what attribution they prefer; `WEIGHTS-LICENSE.md` is updated when they reply.
