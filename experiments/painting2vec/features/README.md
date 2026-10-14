# painting2vec feature extraction

Every candidate way of computing the four content blocks of `src/art2vec/painting2vec/FRAMEWORK.md`
(subject, manner, colour, composition) from an image alone, runnable on the M1 Pro laptop.
Written 8 October 2026. Nothing here is committed or adopted; it is experiment code.

**Update, later on 8 October:** every block, CSD included, has since been run on the pilot, repro and
versions sets. See `RUNS.md` in this directory for the outputs, the checks, and three code changes
(a `pad` fix for very thin strips, a `backbone` part on `clip_l`, and a stricter CSD allow-list).
The paragraph below and the "not run" notes further down describe the state before that.

Status in one paragraph: colour, composition, DINOv2 ViT-B and SigLIP 2 base were run on all 30
sample paintings and their altered copies. DINOv2 ViT-L and CLIP ViT-L/14 were run on 6 sample
paintings and the 10 altered copies only. **CSD was not run**: its only checkpoint is a pickle that
`torch.load(weights_only=True)` refuses (details under "What did not work"). The code for it is
written and partly checked, but no CSD vector has been produced.

## How to run

```
cd experiments/painting2vec          # standalone uv project; the repo root is not touched
uv sync
uv run python -m features.run --images <image dir> --out <output dir> --blocks <list>
```

`--blocks` is a comma list from `colour, composition, dinov2_b, dinov2_l, siglip2_b, clip_l, csd_l`.
The image id is the file stem (`Q12418.jpg` -> `Q12418`). Images are read from the top level of
`--images` (jpg, jpeg, png, webp, tif). Put outputs under `data/painting2vec/features/`.

Typical calls for the full run, one model at a time:

```
D=../../data/painting2vec
uv run python -m features.run --images $D/pilot/images --out $D/features/pilot --blocks colour,composition
uv run python -m features.run --images $D/pilot/images --out $D/features/pilot --blocks dinov2_b --views pad,tile --cleanup-weights
uv run python -m features.run --images $D/pilot/images --out $D/features/pilot --blocks siglip2_b --views squash,pad --cleanup-weights
uv run python -m features.run --images $D/pilot/images --out $D/features/pilot --blocks dinov2_l --views pad --fp16 --cleanup-weights
uv run python -m features.run --images $D/pilot/images --out $D/features/pilot --blocks clip_l --views pad --fp16 --cleanup-weights
```

| option | meaning |
|---|---|
| `--views a,b` | how a painting becomes ViT input: `center`, `squash`, `pad`, `tile`, `native` (DINOv2 only). One output file per view; the model is loaded once. Default: `pad`, except SigLIP 2 `squash` (its own processor's behaviour). |
| `--size N` | ViT input side, default 224. DINOv2 accepts others (448 tested). SigLIP 2, CLIP and CSD are fixed at 224. |
| `--autocrop none\|border\|frame` | trim flat margins, or margins and a frame, before anything else. Default `none`. |
| `--colour-norms a,b` | which colour normalisations to write. Default all five: `raw,greyworld,lstd,std,rank`. |
| `--device auto\|mps\|cpu`, `--fp16` | MPS by default. `--fp16` loads and runs in half precision on MPS; use it for the ViT-L models. |
| `--cleanup-weights` | delete the model's weights when it finishes (only ever under `data/painting2vec/models`). |
| `--min-free-mem-pct 25` | before loading a model, wait until `memory_pressure` reports at least this much free; gives up after 15 minutes. |
| `--max-swap-growth-mb 1024` | stop a model run if system swap grows by more than this while it runs. |
| `--limit N` | first N images only. |
| `--csd-allow-listed-globals` | `csd_l` only; see "What did not work". Not used so far. |

Behaviour worth knowing:

- Resumable. Outputs are rewritten atomically every 50 images; a rerun skips ids already present.
  Checked: a run stopped at 10 images and resumed gives byte-identical arrays to one pass.
- An image that fails to load is logged to `<out>/errors.txt` and skipped.
- Weights go to `data/painting2vec/models/` (gitignored). `HF_HOME` and `TORCH_HOME` are forced
  there, so nothing is written to `~/.cache/huggingface`. Only the files a model needs are fetched
  (`config.json` + one weights file; never the Flax/TF copies).
- A download is refused if it would leave less than 1.5 GB of free disk.
- One model is in memory at a time; a painting is one forward pass (1 view, or up to 5 tiles).

Other entry points:

```
uv run python -m features.fetch_sample            # 30 public-domain AIC paintings -> data/painting2vec/sample
uv run python -m features.sanity make             # altered copies and framed test images
uv run python -m features.sanity autocrop         # auto-crop report
uv run python -m features.sanity table --orig <features dir> --alt <features dir>
uv run python -m features.checks --images <dir> --fp16   # CLIP tower check; needs clip_l weights
```

## Output format

For each store `<name>` there are three files in `--out`:

- `<name>.npz`: one array per part, shape `[N, dim]`, rows aligned with the ids file. float32 for
  colour and composition, float16 for learned embeddings.
- `<name>.ids.txt`: one id per line.
- `<name>.json`: part names and dimensions in order, the settings used, and for models the repo,
  licence, device, seconds per image and memory.

Store names: `colour__<norm>`, `composition`, `<model>__<view>`.

```python
from features.store import load_features
ids, x = load_features(out_dir, "composition", parts=["grid8_an", "symmetry"])   # [N, 198] float32
```

Nothing is scaled across the dataset. Parts have very different scales (DINOv2 `gram_late` has a
norm in the thousands), so standardise per part before combining, as FRAMEWORK section 3 requires.

## Preprocessing (`preprocess.py`)

`load_image(path, autocrop)` is the only loader. It applies the EXIF rotation, flattens alpha onto
white, converts through an embedded ICC profile to sRGB (untagged files are taken as sRGB) and
returns 8-bit RGB.

`stats_array(img, budget=65536)` gives the image used by colour and composition: about 256 x 256
pixels in total with the aspect ratio kept, box-filtered. Averaging is done on sRGB-encoded values,
not in linear light.

`model_views(img, size, view, ...)` gives ViT inputs:

| view | what it does | cost |
|---|---|---|
| `center` | short side to 224, centre crop | cuts the ends off wide and tall paintings |
| `squash` | resize to 224 x 224 ignoring aspect | sees everything, distorted |
| `pad` | long side to 224, centred on a square of the model's mean colour; padding patches are left out of patch statistics | sees everything, at lower resolution for elongated paintings |
| `tile` | short side to 224, then n square crops end to end along the long side, n = ceil(aspect - 0.15), 1 to 5; CLS-type outputs are averaged, patch statistics pool all tiles | full resolution everywhere; no single view sees the whole; n forward passes' worth of work |
| `native` | aspect kept, about 256 patches in total, sides rounded to the patch size (DINOv2 only, which interpolates its position embeddings) | no distortion, no padding; resolution is off the training grid |

How the views compare on the 30 samples (7 have aspect over 1.8). Cosine to the `pad` vector:

| vector | view | ordinary paintings | elongated paintings |
|---|---|---|---|
| DINOv2-B `cls` | center | 0.912 | 0.788 |
| DINOv2-B `cls` | squash | 0.946 | 0.873 |
| DINOv2-B `cls` | tile | 0.930 | 0.857 |
| DINOv2-B `cls` | native | 0.939 | 0.870 |
| DINOv2-B `gram_mid` | center | 0.916 | 0.778 |
| DINOv2-B `gram_mid` | tile | 0.931 | 0.802 |
| SigLIP 2 `embed` | center | 0.952 | 0.906 |
| SigLIP 2 `embed` | squash | 0.965 | 0.943 |

The choice of view matters: the three nearest neighbours of a painting agree between two views only
66 to 82 per cent of the time (DINOv2-B `cls`: center/pad 0.66, the lowest; squash/native and
tile/native 0.80). `center` is the outlier for elongated paintings, as expected. On the altered
copies, `tile` was the most stable under a 3 per cent crop and `pad` the least (table below), but
that is five paintings. Which view gives better neighbours is a question for the looking sessions;
this code only makes each one available.

### Auto-crop

`border` trims margins that are flat and one colour (scanner white, black bars, a plain wall). A
margin is trimmed only if it ends at a full-length edge, which protects paintings with a dark
painted background. `frame` also looks for a frame's straight inner edge at a similar depth on at
least three sides. A crop that would remove more than 60 per cent of either dimension is refused.

Tested on 8 sample paintings pasted into synthetic surrounds with a known inner box (a side counts
as right within 1.5 per cent of the short side):

| surround | `border` | `frame` |
|---|---|---|
| white margin | 8/8 | 8/8 |
| black margin | 8/8 | 8/8 |
| plain wall with noise and a lighting gradient, no frame | 7/8 | 7/8 |
| wall + ridged gold frame with a dark inner lip | 0/8 (trims the wall, keeps the frame) | 8/8 |

On the 30 unframed sample paintings both modes cropped 2 (a thin mount edge on a handscroll, and a
real margin on a papyrus, 8.1 per cent of its area) and left 28 alone, mean area removed 0.45 per
cent. An earlier version cut 69 per cent from Zurbarán's Crucifixion (dark background); the
full-length-edge rule fixed that. The shaped gilt panel photographed on black (`aic16231`) is left
untouched, because no rectangle crops it.

Limits: the frames were synthetic. No real photograph of a framed painting on a wall was tested,
and the dataset agent's images had not arrived when this was written, so the false-crop rate on the
real set is unknown. Run `features.sanity autocrop` once `data/painting2vec/pilot/images` exists
(it reports on the first 150 files) before turning the flag on. Default is off.

## Colour block (`colour.py`), no trained model

Pixels of the statistics image in OKLab. One store per normalisation, 961 dimensions each:

| part | dim | contents |
|---|---|---|
| `palette_hist` | 486 | soft 6 x 9 x 9 histogram over L (0..1), a, b (±0.32), trilinear binning, square-rooted. Euclidean distance is Hellinger distance times √2. |
| `palette_sw` | 384 | sliced-Wasserstein embedding: pixels projected on 24 fixed directions, 16 quantiles each, divided by √384. Euclidean distance approximates the sliced 2-Wasserstein distance between the two colour distributions: an earth mover's distance that fits in a vector. |
| `palette_kmeans` | 24 | 6 k-means colours (L, a, b, weight), heaviest first, deterministic. Compare with `colour.palette_emd(p, q)` (exact EMD by linear programme). Not meaningful under plain Euclidean distance. |
| `lightness` | 21 | soft 16-bin histogram of L, square-rooted; then mean, sd, 5th, 50th, 95th percentile. |
| `chroma` | 21 | the same for chroma (0..0.32). |
| `hue` | 25 | soft circular 24-bin hue histogram weighted by chroma, square-rooted; then the share of near-grey pixels (C < 0.02). |

Normalisations (`--colour-norms`):

| name | what it removes |
|---|---|
| `raw` | nothing |
| `greyworld` | linear-RGB channel gains so the three channel means are equal (gains capped 0.5 to 2). Removes a colour cast; also removes a painting's own overall tint. |
| `lstd` | lightness standardised per image to mean 0.5, sd 0.2. Removes exposure and contrast. a, b untouched. |
| `std` | `lstd`, plus a, b centred on the image mean and scaled to RMS chroma 0.1 (gain capped at 4). Removes cast, exposure, contrast and overall saturation. |
| `rank` | lightness replaced by its rank in the image, a and b as in `std`. Removes any monotone tone curve. The `lightness` part is then constant by construction and carries nothing. |

## Composition block (`composition.py`), no trained model

One store, `composition`, 579 dimensions. Maps: lightness L and chroma C, each standardised per
image, and edge energy E (Sobel gradient of standardised L). So the block is indifferent to
exposure and contrast by construction; absolute levels belong to colour.

| part | dim | contents |
|---|---|---|
| `grid8_an`, `grid4_an` | 192, 48 | cell means of L, C, E on an 8 x 8 / 4 x 4 grid stretched over the painting (aspect-normalised). Order: L row-major, then C, then E. |
| `grid8_ap`, `grid4_ap` | 192, 48 | the same after letterboxing onto a square (aspect-preserving; padding is 0, the image mean). |
| `symmetry` | 6 | correlation of a 16 x 16 map with its mirror: left-right for L, C, E, then up-down. |
| `balance` | 9 | centre of mass x, y (-1..1) and radial spread, for edge energy, chroma, and \|L - mean\|. |
| `edges` | 13 | mean gradient; share of pixels over 0.2; 8-bin orientation histogram (square root); orientation entropy; share of empty 8 x 8 cells; entropy of edge energy over cells. |
| `spectrum` | 3 | Fourier power-spectrum slope (0.02 to 0.35 cycles/pixel); log power at 0.1; log ratio of horizontal to vertical structure. |
| `saliency` | 67 | spectral-residual saliency (Hou and Zhang 2007) on an 8 x 8 grid (square root), its centre of mass, its entropy. |
| `aspect` | 1 | log(width / height). |

Not covered: depth against flatness, which FRAMEWORK section 3 lists under composition. It needs a
trained depth model and none was added.

Colour and composition together take about 0.44 s per image on CPU (about 18 minutes for 2,500),
almost all of it k-means and the five normalisations.

## Learned embeddings (`embed.py`)

| block | model, source | licence | download | parts (dim) | candidate for |
|---|---|---|---|---|---|
| `dinov2_b` | DINOv2 ViT-B/14 with 4 registers, `facebook/dinov2-with-registers-base`, safetensors | Apache-2.0 | 346 MB | `cls` 768, `patch_mean` 768, `meanstd_{early,mid,late}` 1536 each, `gram_{early,mid,late}` 300 each; 7,044 in all | subject (`cls`, `patch_mean`); manner (`meanstd_*`, `gram_*`) |
| `dinov2_l` | DINOv2 ViT-L/14 with registers, `facebook/dinov2-with-registers-large`, safetensors | Apache-2.0 | 1,218 MB | `cls` 1024, `patch_mean` 1024, `meanstd_*` 2048 each, `gram_*` 300 each; 9,092 in all | as above |
| `siglip2_b` | SigLIP 2 base patch16 224, `google/siglip2-base-patch16-224`, safetensors; only the vision tower is loaded | Apache-2.0 | 1,501 MB (includes the text tower) | `embed` 768 (the image embedding), `patch_mean` 768 | subject (text-trained) |
| `clip_l` | OpenAI CLIP ViT-L/14, `openai/clip-vit-large-patch14`, safetensors; vision tower and projection | MIT (openai/CLIP repository; the Hub card states none) | 1,711 MB (includes the text tower) | `embed` 768 | manner / baseline |
| `csd_l` | Contrastive Style Descriptors ViT-L, `tomg-group-umd/CSD-ViT-L`, `pytorch_model.bin` (pickle only) | weights CC-BY-4.0 (Hub card); code MIT | 2,438 MB | `style` 768, `content` 768, `backbone` 1024. **Not produced; see below.** | manner (`style`); the model exposes a content head too |

Details:

- DINOv2 layers: early, mid, late are the hidden states after block n/4, n/2 and n (3, 6, 12 of 12
  for B; 6, 12, 24 of 24 for L), before the final layer norm. `cls` and `patch_mean` are from the
  final normalised output. Register tokens are excluded from all patch statistics.
- `meanstd_*`: per-channel mean then per-channel sd of the patch tokens.
- `gram_*`: tokens centred, projected to 24 dimensions by a fixed seeded Gaussian matrix, then the
  24 x 24 covariance; upper triangle with off-diagonals times √2 (so Euclidean distance equals the
  Frobenius distance between the projected covariances). 300 numbers.
- With `tile`, CLS-type vectors are the mean over tiles and patch statistics pool every tile's
  patches. With `pad`, padding patches are excluded.
- SigLIP 2 large (3.5 GB) and so400m (4.5 GB) were not used: neither fitted the disk limit in
  force when the choice was made.
- SigLIP 2's NaFlex variant (native aspect ratio) was not tried.

### Speed and memory on this machine (M1 Pro, 16 GB, MPS, 224 px)

The machine was shared and already 8 to 12 GB into swap for the whole session, so times vary by a
factor of two or more between runs; the range seen is given. Seconds per image exclude decoding
the file. Peak RSS is the Python process; MPS memory is the driver's allocation at the end of the
run and is extra.

| model | precision | images run | s/image, one view | s/image, `tile` | peak RSS | MPS memory | load time |
|---|---|---|---|---|---|---|---|
| `dinov2_b` | float32 | 30 + 10 | 0.05 to 0.06 | 0.08 to 0.10 | 0.49 GB | 0.50 GB | 55 s incl. download |
| `dinov2_b`, 448 px | float32 | 8 | 0.15 (`pad`), 0.43 (`native`) | not run | 0.34 GB | 1.49 GB | |
| `dinov2_b`, CPU | float32 | 6 | 0.22 | 0.32 | 0.69 GB | none | |
| `dinov2_l` | float32 | 6 + 10 | 0.12 to 0.19 | 0.19 to 0.28 | 1.00 GB | 2.23 GB | |
| `siglip2_b` | float32 | 30 + 10 | 0.02 to 0.11 | 0.04 to 0.18 | 0.57 GB | 0.48 GB | 231 s incl. download |
| `clip_l` | float16 | 6 + 10 | 0.06 to 0.09 | 0.10 to 0.16 | 2.25 GB | 0.65 GB | |
| `csd_l` | | 0 | not measured | | | | |

For scheduling: allow about 1 GB for the ViT-B models and about 3.5 GB for a ViT-L model in
float32 (DINOv2-L measured 1.0 + 2.2). `dinov2_l` was not run in float16; `clip_l` was not run in
float32. CLIP's 2.25 GB peak RSS is a transient while the checkpoint, which includes the text
tower, is read. MPS and CPU agree: DINOv2-B vectors have cosine 1.00000 between the two devices on
6 images, every part.

Swap: while DINOv2-L ran in float32, system swap rose by about 2.5 GB (two new 1 GB swap files,
which also come out of free disk) and fell back afterwards. Other sessions were active, one of
them holding 2 GB, so this cannot be pinned on the model, but it is the reason for the `--fp16`
recommendation and the swap guard. SigLIP 2 base and CLIP-L in float16 showed no such rise.

Disk for the full run of 2,500 images, per view: `dinov2_b` about 35 MB, `dinov2_l` about 45 MB,
`siglip2_b` 8 MB, `clip_l` 4 MB; colour 10 MB per normalisation; composition 6 MB.

## Sanity check: altered copies

Five sample paintings, two altered copies each. `warm+crop`: sRGB R x 1.08, B x 0.86, and 3 per
cent cut from every side. `bright/contrast+q60`: contrast x 1.2 about mid-grey, brightness +0.06,
JPEG quality 60. For each feature: in how many of the five cases the copy is nearer to its
original than any of the 29 other paintings is, and the ratio d(original, copy) / d(original,
nearest other painting), mean and worst. Under 1 passes. Euclidean distance for colour and
composition (EMD for `palette_kmeans`), cosine distance for learned embeddings. "ALL" joins the
Euclidean parts after dividing each by its mean pairwise distance on the sample.

These are synthetic alterations of five paintings among thirty. They show the code behaves; they
do not measure how real reproductions differ, which is FRAMEWORK experiment 2.

### Colour, by normalisation

| norm | part | warm+crop nearest | ratio mean | worst | bright/contrast+q60 nearest | ratio mean | worst |
|---|---|---|---|---|---|---|---|
| raw | palette_hist | 5/5 | 0.81 | 0.96 | 5/5 | 0.56 | 0.77 |
| raw | palette_sw | 4/5 | 0.80 | 1.07 | 1/5 | 0.98 | 1.25 |
| raw | palette_kmeans (EMD) | 4/5 | 0.80 | 1.15 | 2/5 | 1.06 | 1.37 |
| raw | lightness | 5/5 | 0.25 | 0.41 | 1/5 | 1.49 | 2.56 |
| raw | chroma | 1/5 | 1.68 | 2.59 | 4/5 | 0.90 | 1.02 |
| raw | hue | 1/5 | 1.21 | 1.55 | 5/5 | 0.19 | 0.22 |
| raw | ALL | 3/5 | 0.87 | 1.10 | 5/5 | 0.57 | 0.70 |
| greyworld | palette_hist | 5/5 | 0.13 | 0.16 | 4/5 | 0.68 | 1.08 |
| greyworld | palette_sw | 5/5 | 0.20 | 0.31 | 2/5 | 1.25 | 1.82 |
| greyworld | palette_kmeans (EMD) | 5/5 | 0.48 | 0.69 | 2/5 | 1.05 | 1.28 |
| greyworld | lightness | 5/5 | 0.23 | 0.42 | 1/5 | 1.50 | 2.52 |
| greyworld | chroma | 5/5 | 0.24 | 0.53 | 2/5 | 1.23 | 2.07 |
| greyworld | hue | 5/5 | 0.24 | 0.48 | 5/5 | 0.26 | 0.38 |
| greyworld | ALL | 5/5 | 0.14 | 0.18 | 5/5 | 0.57 | 0.71 |
| lstd | palette_hist | 5/5 | 0.83 | 0.99 | 5/5 | 0.23 | 0.29 |
| lstd | palette_sw | 2/5 | 0.94 | 1.16 | 5/5 | 0.19 | 0.24 |
| lstd | palette_kmeans (EMD) | 3/5 | 0.85 | 1.06 | 4/5 | 0.64 | 1.23 |
| lstd | lightness | 5/5 | 0.25 | 0.40 | 5/5 | 0.05 | 0.09 |
| lstd | chroma | 1/5 | 1.68 | 2.59 | 4/5 | 0.90 | 1.02 |
| lstd | hue | 1/5 | 1.21 | 1.55 | 5/5 | 0.19 | 0.22 |
| lstd | ALL | 4/5 | 0.83 | 1.03 | 5/5 | 0.27 | 0.29 |
| std | palette_hist | 5/5 | 0.51 | 0.67 | 5/5 | 0.12 | 0.28 |
| std | palette_sw | 5/5 | 0.48 | 0.74 | 5/5 | 0.10 | 0.31 |
| std | palette_kmeans (EMD) | 5/5 | 0.68 | 0.96 | 5/5 | 0.65 | 0.82 |
| std | lightness | 5/5 | 0.25 | 0.40 | 5/5 | 0.05 | 0.09 |
| std | chroma | 4/5 | 0.63 | 1.02 | 4/5 | 0.36 | 1.16 |
| std | hue | 3/5 | 0.89 | 1.40 | 5/5 | 0.16 | 0.24 |
| std | ALL | 5/5 | 0.51 | 0.69 | 5/5 | 0.13 | 0.34 |
| rank | palette_hist | 5/5 | 0.53 | 0.70 | 5/5 | 0.13 | 0.29 |
| rank | palette_sw | 5/5 | 0.61 | 0.96 | 5/5 | 0.12 | 0.34 |
| rank | palette_kmeans (EMD) | 1/5 | 1.18 | 1.44 | 3/5 | 0.84 | 1.57 |
| rank | lightness | constant | | | | | |
| rank | chroma | 4/5 | 0.63 | 1.02 | 4/5 | 0.36 | 1.16 |
| rank | hue | 3/5 | 0.89 | 1.40 | 5/5 | 0.16 | 0.24 |
| rank | ALL | 5/5 | 0.56 | 0.78 | 5/5 | 0.14 | 0.36 |

Reading it: the raw colour block fails, as FRAMEWORK section 8 expects. A mild warm cast moves
`chroma` and `hue` further than the nearest different painting (1/5), and a contrast change does
the same to `lightness`. Each normalisation fixes the thing it targets and nothing else:
`greyworld` handles the cast (ratio 0.14) and not the tone change; `lstd` the reverse. `std` and
`rank` are the only ones that pass both, 5/5 with every copy at most 0.78 of the way to the
nearest other painting, at the price of discarding overall saturation and tint. `palette_hist` is
the steadiest single part; the k-means palette is the least stable under any setting. Grey-world
followed by `lstd` was not built as a combination.

### Composition

| part | warm+crop nearest | ratio mean | worst | bright/contrast+q60 nearest | ratio mean | worst |
|---|---|---|---|---|---|---|
| grid8_an | 5/5 | 0.37 | 0.66 | 5/5 | 0.02 | 0.03 |
| grid8_ap | 5/5 | 0.42 | 0.73 | 5/5 | 0.03 | 0.04 |
| grid4_an | 5/5 | 0.40 | 0.71 | 5/5 | 0.02 | 0.05 |
| grid4_ap | 5/5 | 0.47 | 0.94 | 5/5 | 0.03 | 0.04 |
| symmetry | 5/5 | 0.49 | 0.95 | 5/5 | 0.03 | 0.05 |
| balance | 5/5 | 0.39 | 0.65 | 5/5 | 0.02 | 0.04 |
| edges | 5/5 | 0.15 | 0.32 | 5/5 | 0.05 | 0.18 |
| spectrum | 5/5 | 0.30 | 0.46 | 5/5 | 0.03 | 0.06 |
| saliency | 5/5 | 0.32 | 0.39 | 5/5 | 0.03 | 0.04 |
| aspect | 4/5 | 0.20 | 1.00 | 5/5 | 0.00 | 0.00 |
| ALL | 5/5 | 0.32 | 0.58 | 5/5 | 0.02 | 0.03 |

Tone changes barely move it. The 3 per cent crop is what moves it, up to 0.94 of the distance to
the nearest other painting for the coarse letterboxed grid: composition will be sensitive to how
tightly each museum crops, which matters for experiment 2. (`aspect` alone ties when another
painting has the same shape.) Before `edges` and `spectrum` were switched to standardised
lightness they failed the contrast change (3/5, ratios 0.83 and 1.23).

### Learned embeddings

All 30 originals, 5 copies of each kind. Every part of every view was nearest 5/5 for both
alterations. Ratio mean (worst) for `warm+crop`; the tone change gave 0.00 to 0.06 everywhere
except SigLIP 2 `embed` with `center` (mean 0.06, worst 0.19).

| model, part | center | squash | pad | tile | native |
|---|---|---|---|---|---|
| DINOv2-B `cls` | 0.05 (0.09) | 0.07 (0.11) | 0.09 (0.26) | 0.04 (0.06) | 0.05 (0.10) |
| DINOv2-B `patch_mean` | 0.05 (0.08) | 0.06 (0.09) | 0.07 (0.15) | 0.04 (0.05) | 0.06 (0.08) |
| DINOv2-B `meanstd_early` | 0.22 (0.33) | 0.23 (0.33) | 0.25 (0.37) | 0.21 (0.34) | 0.26 (0.40) |
| DINOv2-B `gram_early` | 0.35 (0.51) | 0.43 (0.59) | 0.40 (0.46) | 0.30 (0.44) | 0.38 (0.48) |
| DINOv2-B `meanstd_mid` | 0.09 (0.11) | 0.10 (0.12) | 0.10 (0.14) | 0.08 (0.10) | 0.11 (0.14) |
| DINOv2-B `gram_mid` | 0.20 (0.26) | 0.23 (0.28) | 0.21 (0.25) | 0.17 (0.24) | 0.22 (0.25) |
| DINOv2-B `meanstd_late` | 0.06 (0.09) | 0.07 (0.10) | 0.08 (0.16) | 0.04 (0.06) | 0.06 (0.08) |
| DINOv2-B `gram_late` | 0.16 (0.26) | 0.16 (0.22) | 0.13 (0.24) | 0.12 (0.21) | 0.13 (0.19) |
| SigLIP 2 `embed` | 0.08 (0.15) | 0.12 (0.19) | 0.10 (0.15) | 0.09 (0.16) | n/a |
| SigLIP 2 `patch_mean` | 0.06 (0.10) | 0.06 (0.10) | 0.06 (0.10) | 0.04 (0.06) | n/a |

The early-layer statistics are the most exposed to the colour cast, as a low-level descriptor
should be.

ViT-L models, weaker check: only 6 originals were embedded, so only 2 of the 5 altered paintings
have their original present and there are 5 other paintings to be confused with, not 29. Within
that, DINOv2-L (`pad`, `tile`, `native`, every part) and CLIP-L (`center`, `squash`, `pad`, `tile`)
were nearest 2/2 for both alterations; worst ratios 0.42 (DINOv2-L `gram_early`) and 0.13 (CLIP-L).

## What did not work, and what was done instead

**CSD: the checkpoint is an unsafe-format pickle and was not loaded.** `tomg-group-umd/CSD-ViT-L`
ships one file, `pytorch_model.bin`, 2.44 GB, no safetensors. It was downloaded and
`torch.load(..., weights_only=True)` was run on it; torch refused ("Weights only load failed"), and
the file was deleted without being unpickled any other way. The reason, found by listing the
pickle's opcodes without executing them: it is a training checkpoint, `{"model_state_dict": ...,
"args": argparse.Namespace(...), ...}`, with NumPy scalars inside. The globals it references are
`collections.OrderedDict`, `torch.FloatStorage`, `torch._utils._rebuild_tensor_v2` (all allowed by
torch) and `argparse.Namespace`, `numpy.core.multiarray.scalar`, `numpy.dtype`, `_codecs.encode`
(not allowed). Nothing else.

What exists for CSD:

- `embed._CSD` re-implements the model (OpenAI CLIP ViT-L/14 visual tower, two 1024 x 768 linear
  heads for style and content, both L2-normalised), following `model.py` in
  github.com/learn2phoenix/CSD. No `clip` or `open_clip` dependency.
- The 297 tensor names in the checkpoint match the module's exactly (static comparison). The
  checkpoint's `args` record `content_proj_head: default`, so the content head is the linear one.
- The tower itself was checked numerically: with OpenAI's own ViT-L/14 weights loaded into it,
  its output matches the transformers CLIP image embedding (cosine 1.000000, 4 images, float16 on
  MPS; `features.checks`).
- `--csd-allow-listed-globals` keeps `weights_only=True` and adds exactly those four names to
  torch's allow-list. **This path has never been run.** It may need a small fix for NumPy 2 (the
  pickle names `numpy.core`, which NumPy 2 renamed), and whether to use it is a decision for
  whoever owns the safety rule. The alternative is to ask the authors for a safetensors file.
- The memory-mapped load, the `module.` prefix stripping, and CSD's speed and memory are untested.

Also note the licence split: CSD's weights are CC-BY-4.0, which requires attribution; the others
are Apache-2.0 or MIT.

**Disk and swap.** Free disk moved between 0.18 GB and 5 GB for most of the session for reasons
outside this task (macOS swap files are 1 GB each and live on the same volume), then the owner
freed space. Two consequences are in the code: the 1.5 GB download floor, and the swap guard.

**Weight removal bug, fixed.** huggingface_hub 1.33 keeps the bytes in `hub/blobs/`, beside the
repo directories, with symlinks in the snapshot. The first version of `--cleanup-weights` removed
only the repo directory, so 1.5 GB of DINOv2 weights stayed on disk until this was noticed. It now
deletes the link targets first. `data/painting2vec/models` is empty as left.

**A stalled download.** The first CSD download hung at 67 MB for over an hour with no error.
Killing it and rerunning with `HF_HUB_DOWNLOAD_TIMEOUT=30` completed normally. Worth setting for
the full run.

**MPS.** No failures. DINOv2 with a non-square input (`native`) and position-embedding
interpolation works on MPS. float16 on MPS works for CLIP-L. No CPU fallback was needed.

**Not built.** A depth feature for composition; SigLIP 2 larger than base; NaFlex; batching across
paintings (each painting is its own forward pass, which is simple and keeps memory flat but leaves
speed on the table); linear-light downscaling for the statistics image.

## Verified by running, and not

Run and checked:

- colour (5 normalisations) and composition on 30 + 10 images; resume; the sanity tables above.
- auto-crop on 32 synthetic cases and 30 unframed paintings.
- `dinov2_b`: all 5 views on 30 + 10 images, MPS and CPU, 224 and 448 px.
- `siglip2_b`: 4 views on 30 + 10 images, MPS.
- `dinov2_l`: 3 views on 6 + 10 images, MPS float32.
- `clip_l`: 4 views on 6 + 10 images, MPS float16.
- download, disk guard, memory gate, weight removal (after the fix) for those four models.
- odd files: CMYK JPEG, greyscale PNG, 16-bit TIFF, RGBA PNG and palette PNG all load and give
  features; a corrupt file is logged to `errors.txt` and skipped.
- `--autocrop frame` inside the pipeline: composition of the 32 synthetically framed images,
  auto-cropped, lands on the unframed original (`grid8_an` distance 0.3 to 0.4 on average against
  9.5 to the nearest other painting; one wall case missed, 8.7).

Not run:

- `csd_l`, beyond the refused load and the checks listed above.
- anything on the real dataset: `data/painting2vec/pilot`, `repro` and `versions` did not exist yet.
- any run longer than 32 images, so the every-50-images flush and the swap guard firing are
  exercised only by reading the code.
- `dinov2_l` in float16, `clip_l` in float32, `siglip2_b` and the ViT-L models on CPU.
- `--autocrop` together with a model run (it was run with composition only).
