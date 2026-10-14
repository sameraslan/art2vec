# Experiment 2: how much does the photograph move a painting?

Run 8 October 2026 on the precomputed vectors under `data/painting2vec/features/`. No model was run.
Nothing is committed. This answers FRAMEWORK section 9, experiment 2, and the first check of section 8:
two photographs of one painting must land next to each other in every block.

## Result in one table

Clean pairs: the 214 primary pairs with no dataset flag (428 queries, both directions). Gallery: about
2,400 other paintings. "Step" is the median nearest-neighbour distance in the pilot set.

| block | variant | R@1 (95 % CI) | R@10 | d(A,B) / d(A, nearest other): median, p90 | pairs under one step | top-10 list kept | verdict |
|---|---|---|---|---|---|---|---|
| subject | DINOv2-L `cls`, `tile`, L2 + centred, cosine | 0.993 (0.984-1.000) | 0.998 | 0.32, 0.54 | 98.6 % | 82 % | pass |
| manner | CSD `style`, `tile`, PCA-64 whitened | 0.932 (0.902-0.963) | 0.974 | 0.61, 0.92 | 94.4 % | 60 % | fail, narrowly |
| manner (alternative) | DINOv2-L `gram_late`, `tile`, cosine | 0.984 (0.965-0.998) | 0.993 | 0.38, 0.63 | 98.6 % | 73 % | pass |
| colour | `std` normalisation, `palette_hist` + `palette_sw`, PCA-64 whitened | 0.547 (0.481-0.610) | 0.647 | 0.96, 1.52 | 56.1 % | 32 % | fail |
| colour as built | `raw` `palette_hist`, Hellinger | 0.292 (0.234-0.355) | 0.428 | 1.41, 2.52 | 29.4 % | 21 % | fail |
| composition | `grid8_an`, PCA-128 whitened | 0.953 (0.925-0.979) | 0.977 | 0.39, 0.80 | 98.1 % | 71 % | pass, narrowly |
| composition as built | all parts, Euclidean | 0.925 (0.890-0.956) | 0.960 | 0.48, 0.92 | 92.5 % | 57 % | fail, narrowly |

The pass line is mine, since the framework gives none: R@1 of at least 0.95, at least 95 % of pairs
closer than one step, and the 90th percentile of d(A,B) / d(A, nearest other painting) under 1, all on
clean pairs.

On all 274 primary pairs, flagged ones included, R@1 is 0.969 / 0.885 / 0.922 / 0.529 / 0.872 for
subject / CSD style / DINOv2 gram / colour / composition. The gap is the 30 pairs where one file
includes a frame, a mount, a gallery wall or is a detail crop.

![margins](margins.png)

## Method

Code: `common.py` (universe, distances, treatments, metrics), `01_sweep.py` (every variant),
`02_analyse.py` (tables, breakdowns, sheets, plots), `sheets.py`, `extra.py`, `gates.py`, `sinkcheck.py`.
Outputs here: `results_{colour,composition,learned,autocrop}.csv` (one row per variant, 2,294 rows),
`tables.md` (all 51 tables; the ones below are excerpts), `worst_pairs.csv`, `autocrop_sheet_pairs.csv`,
two plots. Under `data/painting2vec/exp_invariance/` (gitignored): per-pair numbers for every variant
(`sweep_*.npz`, shape variants x 563 pairs x 9) and seven contact sheets.

```
cd experiments/painting2vec/exp_invariance
RUN="uv run --no-project --with numpy --with pandas --with scipy --with scikit-learn --with matplotlib --with pillow python"
$RUN 01_sweep.py composition   # 24 s; then colour (262 s), learned (122 s), autocrop (186 s)
$RUN 02_analyse.py --sheets --plots
```

**Gallery.** Rows are the 2,000 pilot paintings followed by the 689 reproduction files. A file
`<qid>__commons` is the pilot image itself (hard link; checked: its vector equals the pilot row exactly,
maximum difference 0.0 for four stores), so those rows are queries only and are never distractors. For a
query, every row with the same qid is removed from the pool of "other paintings", which leaves 1,999
pilot paintings and up to 414 museum or second-Commons photographs of other paintings.

**Pairs.** 563 rows of `repro_pairs.csv`: 274 primary (Commons against the first other source) and 289
extra. Headline numbers are on primary pairs; "clean" is primary with no flag (214). Bootstrap
intervals resample paintings, 1,000 draws.

**Measures.**
1. Retrieval: rank of B among the other paintings with A as query, and the reverse, pooled.
2. Margin: d(A,B) / d(A, nearest different painting), and d(A,B) / the median nearest-neighbour
   distance among the 2,000 pilot paintings (the project's "small step").
3. Product view: the ten nearest pilot paintings from A and from B (own painting excluded): Jaccard,
   extrapolated rank-biased overlap (p = 0.9), and plain overlap. One minus the overlap is the share of
   a top-10 list that depends on which photograph we happened to get.

All distances are Euclidean in kind. Cosine is converted to the chord distance sqrt(2 - 2 cos), which
ranks identically and keeps ratios comparable between treatments.

**Treatments**, all fitted on pilot rows only: `euc` raw Euclidean; `cos` raw cosine; `cen`
L2-normalise, subtract the pilot mean, cosine; `zs` per-dimension z-score, Euclidean; `pca32/64/128`
and `pca..w` (whitened), on the centred unit vectors with cosine for learned parts and on the raw
vectors with Euclidean for colour and composition. Histogram parts also get: total variation and plain
Euclidean on the un-rooted histogram (the stored histograms are square-rooted, so `euc` is Hellinger),
1-D Wasserstein on lightness and chroma bins, circular Wasserstein on hue, and an entropic (Sinkhorn)
approximation of the exact EMD between k-means palettes (checked against the exact linear programme on
40 x 40 pilot pairs: Spearman 0.9999, median relative error 1.2 %). `palette_sw` is already a
sliced-Wasserstein embedding. Combined parts are each divided by the root of their total pilot
variance, as FRAMEWORK section 3 says.

**Discrimination guard.** For every variant: participation ratio of the pilot covariance; TwoNN
intrinsic dimension from pilot nearest-neighbour ratios (works for any distance); and from the versions
set, the AUC with which the distance puts a pair of different paintings sharing a composition
(`composition_match = yes`, 132 pairs; for colour, the 66 with the larger `lab_diff`) further apart
than a clean reproduction pair.

**Caveats that apply to everything below.**
- The pilot includes photograph A of every pair, and the pilot mean, variances and PCA are fitted on it.
  This is unsupervised and I expect the effect to be small, but it was not measured with a held-out fit.
- I chose each block's variant on the same pairs I report. Among 2,294 variants, differences of one or
  two points of R@1 are noise (the interval on 0.95 is about ±0.025).
- The dataset's flags are thresholds on `lab_diff`, not a review. Looking at the worst pairs (below)
  shows that "no flag" still contains sepia scans, framed gallery shots, and a few images that are not
  the same object, and that the flagged pairs are mostly detail crops.
- Top-10 overlap is against 2,000 paintings. A denser gallery has closer neighbours and less stable lists.

## Colour

R@1 on clean pairs, raw Euclidean, normalisation x part:

| part | raw | greyworld | lstd | std | rank |
|---|---|---|---|---|---|
| palette_hist | 0.292 | 0.287 | 0.386 | 0.470 | 0.470 |
| palette_sw | 0.175 | 0.161 | 0.376 | 0.463 | 0.439 |
| palette_kmeans (Euclidean) | 0.082 | 0.077 | 0.091 | 0.070 | 0.040 |
| palette_kmeans (Sinkhorn EMD) | 0.157 | | | 0.313 | |
| lightness | 0.101 | 0.096 | 0.248 | 0.248 | constant |
| chroma | 0.056 | 0.035 | 0.056 | 0.107 | 0.107 |
| hue | 0.194 | 0.210 | 0.194 | 0.178 | 0.178 |
| lightness + chroma + hue | 0.227 | 0.241 | 0.311 | 0.327 | 0.227 |
| hist + sw | 0.285 | 0.262 | 0.386 | 0.486 | 0.472 |
| hist + lightness + chroma + hue | 0.269 | 0.271 | 0.339 | 0.409 | 0.357 |
| all five | 0.269 | 0.266 | 0.357 | 0.437 | 0.381 |

Top-10 overlap for the same grid runs from 0.05 (`rank` k-means) to 0.33 (`std` `palette_sw`).

Discrimination for the same grid (TwoNN dimension on pilot; AUC colour-different versions against clean
reproduction pairs):

| part | raw | greyworld | lstd | std | rank |
|---|---|---|---|---|---|
| palette_hist | 11.3; 0.84 | 12.0; 0.80 | 11.7; 0.85 | 15.3; 0.86 | 16.0; 0.85 |
| palette_sw | 8.9; 0.79 | 8.8; 0.77 | 10.4; 0.86 | 12.1; 0.83 | 11.9; 0.83 |
| hist + sw | 10.9; 0.84 | 11.2; 0.80 | 11.7; 0.86 | 14.7; 0.85 | 14.5; 0.84 |
| chroma | 5.1; 0.76 | 4.9; 0.73 | 5.1; 0.76 | 7.5; 0.70 | 7.5; 0.70 |

Treatments and distances, R@1 on clean pairs:

| feature | euc | cen | zs | pca64 | pca64w | pca128w | TV (L1) | plain Euclidean |
|---|---|---|---|---|---|---|---|---|
| std palette_hist | 0.470 | 0.493 | 0.400 | 0.460 | 0.495 | 0.451 | 0.481 | 0.400 |
| std palette_sw | 0.463 | 0.484 | 0.453 | 0.463 | 0.542 | 0.505 | | |
| std hist + sw | 0.486 | 0.512 | 0.444 | 0.488 | 0.547 | 0.514 | | |
| rank hist + sw | 0.472 | 0.474 | 0.435 | 0.449 | 0.530 | 0.540 | | |
| raw palette_sw | 0.175 | 0.292 | 0.238 | 0.173 | 0.491 | 0.477 | | |
| raw palette_hist | 0.292 | 0.285 | 0.208 | 0.292 | 0.290 | 0.213 | 0.241 | 0.196 |

One-dimensional histograms (`std`): Hellinger beats Wasserstein on the same bins (lightness 0.238
against 0.213, chroma 0.105 against 0.086, hue 0.168 against 0.117 circular), and the five summary
numbers alone are near useless (0.035 to 0.121, TwoNN about 4: this is what a degenerate descriptor
looks like here). Mixing normalisations did not beat `std` alone (best cross combination,
`palette_sw` greyworld + std, PCA-64 whitened: 0.509).

What this says:

- **No colour variant passes.** The best of 596 is 0.547 (0.481-0.610). For 45 % of clean pairs the
  other photograph of the same painting is further away than some different painting, and two thirds of
  a top-10 colour list changes with the photograph.
- **Normalisation order: std ≈ rank > lstd > raw ≈ greyworld.** Standardising lightness is what helps;
  grey-world does nothing on real reproductions (0.287 against 0.292), although it fixed the synthetic
  warm cast in the features README. Real photographs differ in exposure, contrast and saturation far
  more than in a global cast.
- **Parts:** the two full-palette parts carry it; hue, chroma and lightness alone are weak; the k-means
  palette is the least stable under either distance.
- **Not degenerate.** The more photograph-proof normalisations also have the higher intrinsic dimension
  (14.7 for `std` hist + sw against 10.9 raw) and separate colour-different versions as well as raw
  does (AUC 0.85 against 0.84). There is no trade-off to pay; the block is simply noisy.
  ![trade-off](colour_tradeoff.png)
- **Whitening helps colour**, most of all the raw sliced-Wasserstein part (0.175 to 0.491): the leading
  pilot directions are overall lightness and saturation, which is exactly what photographs disagree on.
- **It scales with how different the two files are.** R@1 of the best variant by `lab_diff`: 0.98 at
  1-3, 0.65 at 3-6, 0.30 at 6-9, 0.20 at 9-12. By source: Commons against NGA 0.81, Rijksmuseum 0.86,
  AIC 1.00 (9 pairs), Met 0.38, second Commons file 0.45.

## Composition

Raw Euclidean, clean pairs:

| part | dim | TwoNN | R@1 | R@10 | d/NN-other median | under one step | top-10 kept |
|---|---|---|---|---|---|---|---|
| grid8_an (aspect-normalised) | 192 | 28.3 | 0.928 | 0.963 | 0.43 | 0.944 | 0.57 |
| grid8_ap (aspect-preserving) | 192 | 32.7 | 0.925 | 0.956 | 0.44 | 0.939 | 0.61 |
| grid4_an | 48 | 19.1 | 0.881 | 0.932 | 0.51 | 0.892 | 0.55 |
| grid4_ap | 48 | 18.6 | 0.867 | 0.914 | 0.51 | 0.851 | 0.54 |
| saliency | 67 | 21.7 | 0.944 | 0.970 | 0.41 | 0.921 | 0.60 |
| balance | 9 | 8.3 | 0.467 | 0.649 | 1.10 | 0.444 | 0.39 |
| edges | 13 | 6.8 | 0.437 | 0.615 | 1.15 | 0.411 | 0.39 |
| symmetry | 6 | 5.9 | 0.341 | 0.528 | 1.52 | 0.341 | 0.33 |
| spectrum | 3 | 2.9 | 0.259 | 0.619 | 1.97 | 0.224 | 0.46 |
| aspect | 1 | 2.1 | 0.236 | 0.325 | | 0.234 | 0.33 |
| grid8_an: lightness / chroma / edge channel only | 64 | 19 / 23 / 25 | 0.914 / 0.806 / 0.895 | | 0.36 / 0.56 / 0.40 | | 0.61 / 0.46 / 0.58 |
| grid8_an + saliency | 259 | 29.9 | 0.958 | 0.974 | 0.40 | 0.967 | 0.61 |
| grid8_an + grid8_ap | 384 | 30.0 | 0.944 | 0.967 | 0.42 | 0.953 | 0.60 |
| the five global parts | 98 | 19.1 | 0.851 | 0.921 | 0.56 | 0.851 | 0.51 |
| ALL (as built) | 579 | 23.4 | 0.925 | 0.960 | 0.48 | 0.925 | 0.57 |

Treatments (R@1; top-10 kept):

| part | euc | cen | zs | pca64w | pca128w |
|---|---|---|---|---|---|
| grid8_an | 0.928; 0.57 | 0.937; 0.54 | 0.937; 0.57 | 0.932; 0.61 | 0.953; 0.71 |
| grid8_ap | 0.925; 0.61 | 0.939; 0.57 | 0.914; 0.60 | 0.925; 0.65 | 0.928; 0.77 |
| grid8_an + saliency | 0.958; 0.61 | 0.960; 0.60 | 0.953; 0.61 | 0.960; 0.62 | 0.965; 0.68 |
| grid8_an + ap | 0.944; 0.60 | 0.944; 0.56 | 0.935; 0.60 | 0.930; 0.64 | 0.960; 0.72 |
| ALL | 0.925; 0.57 | 0.928; 0.57 | 0.944; 0.60 | 0.935; 0.57 | 0.956; 0.63 |

- The 8 x 8 grid and the saliency grid do the work. The small global parts (symmetry, balance, edges,
  spectrum) are each unstable and adding them to the grid lowers R@1 (0.928 to 0.902 unwhitened).
- Aspect-normalised and aspect-preserving grids are indistinguishable on retrieval (0.928 and 0.925);
  the letterboxed grid gives slightly steadier lists (0.61 against 0.57; 0.77 against 0.71 whitened).
- The chroma channel of the grid is the exposed one (0.806 against 0.914 lightness, 0.895 edges).
- Whitened PCA-128 is the one treatment that clearly helps: for `grid8_an`, top-10 kept rises from
  0.57 to 0.71 and R@1 from 0.928 to 0.953 (the second is inside the noise).
- Versions: composition should keep versions close. Median version-pair distance is 0.87 steps for
  `grid8_an` whitened, against 0.39 for a clean reproduction pair (AUC 0.91).

## Learned models

Cosine, clean pairs, R@1 / top-10 kept, by view:

| model | part | center | pad | tile |
|---|---|---|---|---|
| dinov2_l | cls | | 0.988 / 0.82 | 0.993 / 0.82 |
| dinov2_l | patch_mean | | 0.986 / 0.79 | 0.984 / 0.82 |
| dinov2_l | meanstd_late | | 0.986 / 0.81 | 0.986 / 0.82 |
| dinov2_l | gram_late | | 0.993 / 0.69 | 0.984 / 0.73 |
| dinov2_l | meanstd_mid | | 0.965 / 0.70 | 0.970 / 0.69 |
| dinov2_l | gram_mid | | 0.965 / 0.53 | 0.967 / 0.55 |
| dinov2_l | meanstd_early | | 0.822 / 0.49 | 0.755 / 0.45 |
| dinov2_l | gram_early | | 0.860 / 0.44 | 0.850 / 0.45 |
| dinov2_b | cls | 0.995 / 0.76 | 0.986 / 0.77 | 0.991 / 0.79 |
| dinov2_b | patch_mean | 0.991 / 0.79 | 0.986 / 0.79 | 0.986 / 0.80 |
| dinov2_b | meanstd_late | 0.988 / 0.79 | 0.988 / 0.78 | 0.986 / 0.80 |
| dinov2_b | gram_late | 0.977 / 0.63 | 0.979 / 0.61 | 0.972 / 0.64 |
| dinov2_b | meanstd_mid | 0.965 / 0.66 | 0.949 / 0.63 | 0.946 / 0.63 |
| dinov2_b | gram_mid | 0.939 / 0.48 | 0.906 / 0.45 | 0.886 / 0.48 |
| dinov2_b | meanstd_early | 0.797 / 0.46 | 0.790 / 0.45 | 0.755 / 0.44 |
| dinov2_b | gram_early | 0.862 / 0.42 | 0.818 / 0.41 | 0.813 / 0.43 |
| siglip2_b | embed | 0.991 / 0.78 | 0.986 / 0.77 | 0.988 / 0.78 |
| siglip2_b | patch_mean | 0.984 / 0.80 | 0.977 / 0.77 | 0.981 / 0.82 |
| clip_l | embed | | 0.984 / 0.77 | 0.984 / 0.82 |
| clip_l | backbone | | 0.981 / 0.77 | 0.979 / 0.81 |
| csd_l | style | | 0.890 / 0.54 | 0.911 / 0.58 |
| csd_l | content | | 0.904 / 0.54 | 0.914 / 0.58 |
| csd_l | backbone | | 0.881 / 0.54 | 0.895 / 0.56 |

Treatments, mean over the 56 store x part features (and for CSD `style`, `tile`):

| treatment | R@1 clean | R@1 all primary | under one step | top-10 kept | CSD style tile R@1 / kept |
|---|---|---|---|---|---|
| euc | 0.933 | 0.878 | 0.924 | 0.658 | |
| cos | 0.938 | 0.883 | 0.932 | 0.655 | 0.911 / 0.58 |
| cen | 0.940 | 0.887 | 0.949 | 0.648 | 0.906 / 0.57 |
| zs | 0.929 | 0.876 | 0.918 | 0.644 | |
| pca32 / pca32w | 0.884 / 0.899 | 0.828 / 0.842 | 0.895 / 0.911 | 0.633 / 0.606 | |
| pca64 / pca64w | 0.915 / 0.941 | 0.860 / 0.885 | 0.926 / 0.951 | 0.646 / 0.611 | whitened: 0.932 / 0.60 |
| pca128 / pca128w | 0.930 / 0.959 | 0.876 / 0.907 | 0.941 / 0.968 | 0.650 / 0.599 | |

- Every final-layer vector of DINOv2, SigLIP 2 and CLIP passes: R@1 0.98 to 0.995, and a reproduction
  sits at about a third of the distance to the nearest other painting.
- Depth orders it, as predicted: early-layer statistics are the most exposed (R@1 0.76 to 0.86, top-10
  kept 0.41 to 0.49), mid-layer in between, late-layer close to `cls`.
- **CSD is the least photograph-proof of the trained encoders**: R@1 0.89 to 0.91, 0.93 at best, with
  only 54 to 60 % of a top-10 list kept. All three of its parts behave alike, the tower output
  included, so this is the fine-tuned tower and not the style head.
- View: no reliable difference in retrieval. `tile` keeps slightly more of the list for most parts.
- Centring changes nothing. Unwhitened PCA costs about 1, 2 and 5 points of R@1 at 128, 64 and 32
  dimensions. Whitening buys 2 to 3 points of R@1 and costs about 5 points of top-10 overlap: the
  pair gets closer in rank while the neighbourhood around it gets noisier.

## Auto-crop

`border` changed 125 of 689 images and `frame` 137 (Met 50 of 66; the Met's files carry a black
surround). Both photographs of a pair and the other reproductions are cropped; **the pilot gallery is
not**, because no auto-cropped pilot store exists.

| feature | pairs | R@1 none / border / frame | top-10 kept none / border / frame |
|---|---|---|---|
| colour std hist + sw, PCA-64 whitened | all primary 274 | 0.529 / 0.553 / 0.564 | 0.323 / 0.341 / 0.350 |
| | Commons against Met, 66 | 0.379 / 0.477 / 0.508 | 0.255 / 0.312 / 0.326 |
| | high-difference flag, all rows, 70 | 0.043 / 0.050 / 0.079 | 0.089 / 0.089 / 0.099 |
| | either image cropped, 155 | 0.290 / 0.352 / 0.381 | 0.217 / 0.260 / 0.278 |
| composition grid8_an, Euclidean | all primary 274 | 0.841 / 0.858 / 0.874 | 0.538 / 0.558 / 0.568 |
| | clean 214 | 0.928 / 0.951 / 0.946 | 0.569 / 0.593 / 0.597 |
| | Commons against Met, 66 | 0.742 / 0.803 / 0.818 | 0.432 / 0.503 / 0.518 |
| | high-difference flag, all rows, 70 | 0.250 / 0.243 / 0.336 | 0.146 / 0.139 / 0.170 |
| | either image cropped, 155 | 0.690 / 0.729 / 0.771 | 0.367 / 0.426 / 0.451 |
| composition ALL, Euclidean | all primary 274 | 0.849 / 0.861 / 0.881 | 0.543 / 0.570 / 0.583 |
| DINOv2-B pad cls, centred | all primary 274 | 0.951 / - / 0.953 | 0.741 / - / 0.753 |
| | high-difference flag, all rows, 70 | 0.671 / - / 0.693 | 0.437 / - / 0.456 |
| | either image cropped, 155 | 0.913 / - / 0.926 | 0.680 / - / 0.699 |
| DINOv2-B pad meanstd_early, centred | all primary 274 | 0.735 / - / 0.776 | 0.445 / - / 0.459 |

NGA pairs do not change (no NGA image is cropped). Rows for Rijksmuseum, AIC and Cleveland and for
the other features are in `tables.md`.

Among the 155 pairs where `frame` cropped either image, the two photographs moved closer by more than
10 % in 44 % of pairs for composition and further apart in 10 % (39 % and 2 % for colour, 27 % and
17 % for DINOv2 `cls`). Pairs whose worse-direction rank went from above 1 to 1, and the reverse:
composition 16 fixed, 1 broken (`border`: 9, 0); colour 14, 0; DINOv2 `cls` 7, 2.

**What I saw** on the contact sheet of the ten most helped and ten most hurt pairs
(`autocrop_helped.jpg`, `autocrop_hurt.jpg`, crop boxes drawn: yellow `border`, red `frame`):

- Helped. Black surrounds on Met and Commons files trimmed by `border` (Night Watch, Memling's
  Annunciation, Madame X, Vermeer's Allegory). A gilt frame removed by `frame` and not by `border`
  (Wright's Air Pump, rank 40 to 1). A hanging scroll cut out of its mount (rank 607 to 1). A thin
  strip of frame edge on a Rijksmuseum file. A postage stamp reproducing a detail of Kramskoi's
  Unknown Woman, cropped to the picture inside the stamp (rank 542 to 1).
- Hurt. Three kinds. (a) Asymmetric crops: the mount or decorated album border is removed on one
  photograph and kept on the other (a hanging scroll, rank 1 to 385; a Mughal album page, rank 3 to 107;
  a Japanese painting with a brocade mount). (b) False crops of a few per cent into dark painted
  backgrounds (Zurbarán's Crucifixion again, by `border`; a Titian portrait by `frame`); the pair moved
  apart and stayed at rank 1. (c) Pairs auto-crop cannot be blamed for: two different screens of a
  pair filed as one painting, and a pair of scrolls photographed with and without mounts.

So auto-crop does what it says on plain surrounds and real frames, it does not rescue the
high-difference group (R@1 0.25 to 0.34 for composition; those are mostly detail crops, book pages and
gallery shots), and its damage is confined to mounted East Asian and album paintings and to a small
trim on dark pictures.

## Failure analysis

The fifteen worst pairs of each chosen variant over all 563 rows, one per painting (`worst_pairs.csv`),
viewed side by side.

**Subject (DINOv2-L cls).** None of the fifteen is a photographic difference.

| cause | n | which |
|---|---|---|
| one file is a detail crop of the painting | 8 | Bronzino's Allegory, David with the Head of Goliath, Wedding at Cana, La Balançoire, Raft of the Medusa, Portrait of a Musician, Music in the Tuileries, Sunset at Montmajour |
| one object against a set (wrong pairing) | 3 | Maria Portinari against the Met's image of both portraits; two Japanese scroll pairs shown as one scroll and as both |
| a different object (wrong pairing) | 2 | "When Will You Marry?" paired with another Gauguin; the other scroll of "Birds and Flowers of Summer and Autumn" |
| photograph of the installation | 2 | Old Plum in its room; Olympia in the gallery, at an angle, with the frame |

The only three failures among clean pairs (Maria Portinari, Birds and Flowers, Dragon; Tiger) are in
this table as wrong pairings. On correctly paired clean photographs the subject block did not fail once.

**Composition (grid8_an).** Detail crop 6; mount, frame, stamp or gallery shot 4 (two mounted scroll
pairs, Starry Night over the Rhône framed at an angle, the Kramskoi stamp); black-and-white book page
with wide margins 2 (Las Hilanderas, Whistler's Mother); wrong pairing 2 (Gauguin, Portinari diptych);
extreme aspect and a different arrangement of the object 1 (a manuscript cover, 1,024 px strip).

**Manner (CSD style).** Thirteen of fifteen are monochrome reproductions: black-and-white or sepia
photographs (Art of Painting, Yellow House, Rokeby Venus photographed after the 1914 attack, Benois
Madonna, Madonna Litta, Blue Boy, Venus and Mars, Girl Reading a Letter, which is also the painting
before the Cupid was uncovered) and engravings after the painting on a book page (Marriage of the
Virgin, The Swing, Ophelia, Las Hilanderas, Luncheon on the Grass). One detail crop (Bronzino). One
apparent wrong pairing (La velata: the second file shows a different arrangement of the hand and
sleeve). An engraving after a painting is a different manner, so CSD is arguably right about five of
these; the pipeline has to keep them out. Three of the thirteen carry no flag.

**Colour (std hist + sw).** Over all rows the fifteen worst are flagged black-and-white, framed or
mounted files (classified from the flags; I did not view that sheet). Among clean pairs, the fifteen
worst: surround included 7 (black Met border on four, a brocade mount, a frame in a gallery, a scroll
pair), large difference in exposure or saturation between two whole, correctly paired photographs 6
(Saturn, Denial of Saint Peter, Calling of Saint Matthew, Blind Leading the Blind, Red Vineyard, Black
Stork), unflagged monochrome scan 2. A random fifteen of the clean failures: tonal or colour difference
between two honest photographs 10 (Three Philosophers, Aristotle, Magpie on the Gallows, Las Meninas,
Painter's Studio and others), the same plus a black border 4, a different crop 1. **Colour is the one
block whose failures are the photograph and not the data.**

The DINOv2 gram_late sheet (`worst_manner_alt.jpg`) was written and not viewed; by flag, 13 of its 15
are high-difference pairs.

## Noise floor

Share of a top-10 pilot neighbour list that changes when the photograph changes (1 - overlap):

| block | clean, mean | clean, median | clean pairs losing 5 or more of 10 | all primary, mean | high-difference pairs | black-and-white pairs (17) |
|---|---|---|---|---|---|---|
| subject (DINOv2-L cls) | 18 % | 10 % | 6 % | 20 % | 44 % | 30 % |
| subject (SigLIP 2 embed) | 23 % | 20 % | 8 % | 26 % | 51 % | 50 % |
| manner (CSD style) | 40 % | 30 % | 39 % | 41 % | 71 % | 91 % |
| manner (DINOv2-L gram_late) | 27 % | 20 % | 15 % | 31 % | 66 % | 42 % |
| colour (best) | 68 % | 70 % | 79 % | 68 % | 91 % | 98 % |
| colour (as built) | 79 % | 90 % | 87 % | 76 % | 95 % | 100 % |
| composition (best) | 29 % | 30 % | 21 % | 31 % | 59 % | 53 % |
| composition (as built) | 43 % | 40 % | 42 % | 46 % | 85 % | 79 % |

Even the block that passes on retrieval loses about two of ten neighbours to the photograph.

## Recommendation

| block | use | verdict against section 8 |
|---|---|---|
| subject | DINOv2 `cls` (ViT-L if affordable: top-10 kept 0.82 against 0.79 for ViT-B; R@1 the same), `tile` view, L2-normalise, centre, cosine. PCA to 128 unwhitened is free; do not whiten. SigLIP 2 `embed` is as good on retrieval and a little less stable in lists. | **Pass.** R@1 0.993, 98.6 % of pairs under one step, p90 margin 0.54. |
| manner | On this test DINOv2 `gram_late` or `meanstd_late` are far steadier than CSD. Whether they are manner and not subject is experiment 1's question, and `meanstd_late` behaves like `cls`. If CSD is kept: `tile`, PCA-64 whitened, and monochrome reproductions refused. Do not use early-layer statistics. | **CSD fails narrowly** (R@1 0.932, 94.4 % under one step, 40 % of the list at the photograph's mercy). **DINOv2-L gram_late passes** (0.984, 98.6 %, p90 0.63). |
| colour | `std` normalisation (lightness standardised, a and b centred and scaled), `palette_hist` + `palette_sw`, each scaled to unit variance, PCA-64 whitened, Euclidean. Drop `palette_kmeans`, and the lightness, chroma and hue parts as separate parts. | **Fail.** R@1 0.547, 56 % under one step, p90 margin 1.52. Not fixable by any normalisation, part, distance or treatment tried. |
| composition | `grid8_an` (adding `saliency` or `grid8_ap` is within noise), PCA-128 whitened, Euclidean. Drop symmetry, balance, edges, spectrum and aspect as distance terms, or give them little weight. | **Passes narrowly on clean pairs** (R@1 0.953, 98.1 %, p90 0.80); fails as built (0.925) and on unfiltered pairs (0.872). |

**Colour.** As a similarity block it should not ship as is. Options, none tested here: take the
holding museum's colour-managed image only, as the framework already names as the artefact (NGA,
Rijksmuseum and AIC pairs reach 0.81 to 1.00 against Commons); give colour a low weight and say so; or
replace nearest-neighbour use of colour with coarse bins that a reproduction rarely crosses.

**Auto-crop.** Yes, `frame` mode, at intake. It fixed 16 composition pairs and broke 1, and helps
colour on Met files by 13 points. Two conditions: use the amount cropped as a signal to look for a
better file (a large crop means a frame, mount or stamp), and exempt or review mounted scrolls and
album pages, where it crops one photograph and not the other. The whole gallery must be cropped the
same way; here the pilot side was not, so the gain is probably understated.

**Reproductions to refuse.**
- Greyscale and sepia. Mean OKLab chroma under 0.01 catches 13 of the 17 flagged black-and-white rows
  with 2 other hits among 546 (`gates.py`); sepia scans and engravings pass that gate and need a
  hue-spread test or a source rule (no book scans). 17 pilot images are under the threshold.
- Framed, mounted, or photographed in the gallery, unless auto-crop reduces them to the picture.
- Detail crops and files showing a different or additional object. These were the largest cause of
  failure in every trained block and cannot be seen from one image. Comparing the image's aspect ratio
  with the catalogue's height and width catches few of them (a deviation over 0.05 in log aspect: 30 %
  of high-difference pairs, 11 % of unflagged ones), so this needs a second reproduction or a person.
- Sets filed as one item (scroll pairs, diptychs, screen pairs): decide per item which object the id means.
- Strips with a short side under 100 px.

## Verified, surprised, not tested

Verified by running: the Commons side of every pair equals its pilot row exactly; the Sinkhorn palette
distance against the exact one; every number in this file comes from `results_*.csv` or `tables.md`;
five of seven failure sheets and both auto-crop sheets were looked at.

Surprises: grey-world correction is worthless on real reproductions; CSD is the weakest trained encoder
on this test, by a wide margin; whitening raises retrieval and lowers list stability for trained
vectors, and raises both for the hand-built blocks; the flagged "frame or crop" pairs are mostly
detail crops and mispairings, so the dataset's own labels understate how clean the remaining pairs are
and overstate what auto-crop could fix.

Not tested: a PCA or mean fitted without the query paintings; an auto-cropped pilot gallery;
auto-crop with any trained model except DINOv2-B `pad`; `squash` and `native` views (not in the
stores); exact EMD on the 3-D palette histogram; combinations of trained parts; a gallery larger than
2,400; whether the vector predicts the holding museum (section 8's leak check); any manual relabelling
of the 563 pairs. One machine rule was broken: the colour sweep peaked at 1.41 GB resident (the
Sinkhorn step); the chunk size is now four times smaller, and the sweep was not re-run to confirm the
new peak. Every other run stayed under 0.7 GB.
