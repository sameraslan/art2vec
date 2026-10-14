# painting2vec feature runs on the pilot dataset

Run on 8 October 2026, 18:57 to 22:26 local time, on the shared M1 Pro (16 GB), one job at a time.
Nothing is committed. No analysis of the vectors was done; this file records what was computed,
where it is, and what was checked.

## Where the outputs are

All under `data/painting2vec/features/` (gitignored):

| directory | images | what |
|---|---|---|
| `pilot/` | 2,000 (`data/painting2vec/pilot/images`) | every block, `--autocrop none` |
| `repro/` | 689 (`data/painting2vec/repro`, ids are `<qid>__<source>`; pairing is in `repro/repro_pairs.csv`) | every block, `--autocrop none` |
| `versions/` | 355 (`data/painting2vec/versions/images`) | every block, `--autocrop none` |
| `repro_autocrop_border/` | 689 | colour and composition only, `--autocrop border` |
| `repro_autocrop_frame/` | 689 | colour, composition, and `dinov2_b__pad`, `--autocrop frame` |
| `logs/` | | one log per job, `verify.jsonl` (every check below, machine-readable), `scripts/` (the runner, the checker and the job lists) |

The versions directory holds 355 images, not 304: the dataset README says 355 were downloaded and
304 are in kept pairs. All 355 were embedded; filter by `versions/version_pairs.csv`. The repro directory's 689 files are
exactly the files named in `repro_pairs.csv`.

Each store is `<name>.npz` (one array per part, rows aligned), `<name>.ids.txt`, `<name>.json`.
In every store the rows are in sorted file-stem order, the same order in every store of a set.
Read with `features.store.load_features(dir, name, parts=[...])`.

## Stores and array shapes

| store | parts: name (dim) | dtype | sets |
|---|---|---|---|
| `clip_l__pad` | embed (768), backbone (1024) | float16 | pilot (2000), repro (689), versions (355) |
| `clip_l__tile` | embed (768), backbone (1024) | float16 | pilot (2000), repro (689), versions (355) |
| `colour__greyworld` | palette_hist (486), palette_sw (384), palette_kmeans (24), lightness (21), chroma (21), hue (25) | float32 | pilot (2000), repro (689), repro_autocrop_border (689), repro_autocrop_frame (689), versions (355) |
| `colour__lstd` | palette_hist (486), palette_sw (384), palette_kmeans (24), lightness (21), chroma (21), hue (25) | float32 | pilot (2000), repro (689), repro_autocrop_border (689), repro_autocrop_frame (689), versions (355) |
| `colour__rank` | palette_hist (486), palette_sw (384), palette_kmeans (24), lightness (21), chroma (21), hue (25) | float32 | pilot (2000), repro (689), repro_autocrop_border (689), repro_autocrop_frame (689), versions (355) |
| `colour__raw` | palette_hist (486), palette_sw (384), palette_kmeans (24), lightness (21), chroma (21), hue (25) | float32 | pilot (2000), repro (689), repro_autocrop_border (689), repro_autocrop_frame (689), versions (355) |
| `colour__std` | palette_hist (486), palette_sw (384), palette_kmeans (24), lightness (21), chroma (21), hue (25) | float32 | pilot (2000), repro (689), repro_autocrop_border (689), repro_autocrop_frame (689), versions (355) |
| `composition` | grid8_an (192), grid8_ap (192), grid4_an (48), grid4_ap (48), symmetry (6), balance (9), edges (13), spectrum (3), saliency (67), aspect (1) | float32 | pilot (2000), repro (689), repro_autocrop_border (689), repro_autocrop_frame (689), versions (355) |
| `csd_l__pad` | style (768), content (768), backbone (1024) | float16 | pilot (2000), repro (689), versions (355) |
| `csd_l__tile` | style (768), content (768), backbone (1024) | float16 | pilot (2000), repro (689), versions (355) |
| `dinov2_b__center` | cls (768), patch_mean (768), meanstd_early (1536), gram_early (300), meanstd_mid (1536), gram_mid (300), meanstd_late (1536), gram_late (300) | float16 | pilot (2000), repro (689), versions (355) |
| `dinov2_b__pad` | cls (768), patch_mean (768), meanstd_early (1536), gram_early (300), meanstd_mid (1536), gram_mid (300), meanstd_late (1536), gram_late (300) | float16 | pilot (2000), repro (689), repro_autocrop_frame (689), versions (355) |
| `dinov2_b__tile` | cls (768), patch_mean (768), meanstd_early (1536), gram_early (300), meanstd_mid (1536), gram_mid (300), meanstd_late (1536), gram_late (300) | float16 | pilot (2000), repro (689), versions (355) |
| `dinov2_l__pad` | cls (1024), patch_mean (1024), meanstd_early (2048), gram_early (300), meanstd_mid (2048), gram_mid (300), meanstd_late (2048), gram_late (300) | float16 | pilot (2000), repro (689), versions (355) |
| `dinov2_l__tile` | cls (1024), patch_mean (1024), meanstd_early (2048), gram_early (300), meanstd_mid (2048), gram_mid (300), meanstd_late (2048), gram_late (300) | float16 | pilot (2000), repro (689), versions (355) |
| `siglip2_b__center` | embed (768), patch_mean (768) | float16 | pilot (2000), repro (689), versions (355) |
| `siglip2_b__pad` | embed (768), patch_mean (768) | float16 | pilot (2000), repro (689), versions (355) |
| `siglip2_b__tile` | embed (768), patch_mean (768) | float16 | pilot (2000), repro (689), versions (355) |

67 stores in all. Learned embeddings are float16; the largest absolute element anywhere is 8,456
(`pilot/dinov2_l__pad`, `gram_late`) against a float16 limit of 65,504, so nothing overflowed.
Nothing is scaled across the dataset: `gram_late` norms are in the thousands, CSD heads are unit
length. Standardise per part before combining.

`clip_l` has a part the README does not list: `backbone` (1024), the tower output before CLIP's
1024 to 768 projection. It was added so that CSD's `backbone` has a like-for-like CLIP counterpart.

## Runs

Wall time covers the model load and, where the weights were not yet on disk, the download (see
notes). Peak RSS and MPS memory are what the code reports for the Python process (last attempt);
for the colour and composition jobs peak RSS is from `/usr/bin/time -l`. Swap is the whole
machine's, shared with other sessions.

| job | set (out dir under data/painting2vec/features/) | settings | images | attempts | wall s (all attempts) | s/image per store | peak RSS MB | MPS MB | swap used MB, before -> after, per attempt | free mem % before | guard trips | stores |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| j1_cc_versions | versions | `--autocrop none` | 355 | 1 | 141 (141) | all six stores together 0.3928 | 244 | - | 10202->10130 | 48 | 0 | colour__greyworld, colour__lstd, colour__rank, colour__raw, colour__std, composition |
| j1_cc_repro | repro | `--autocrop none` | 689 | 1 | 312 (312) | all six stores together 0.4507 | 241 | - | 10130->11226 | 45 | 0 | colour__greyworld, colour__lstd, colour__rank, colour__raw, colour__std, composition |
| j1_cc_repro_autocrop_border | repro_autocrop_border | `--autocrop border` | 689 | 1 | 321 (321) | all six stores together 0.4628 | 294 | - | 11226->11255 | 72 | 0 | colour__greyworld, colour__lstd, colour__rank, colour__raw, colour__std, composition |
| j1_cc_repro_autocrop_frame | repro_autocrop_frame | `--autocrop frame` | 689 | 1 | 314 (314) | all six stores together 0.4528 | 227 | - | 11255->11116 | 28 | 0 | colour__greyworld, colour__lstd, colour__rank, colour__raw, colour__std, composition |
| j1_cc_pilot | pilot | `--autocrop none` | 2000 | 1 | 899 (899) | all six stores together 0.4486 | 269 | - | 11116->11600 | 31 | 0 | colour__greyworld, colour__lstd, colour__rank, colour__raw, colour__std, composition |
| j2_dinov2b_versions | versions | `--views center,pad,tile --autocrop none` | 355 | 1 | 181 (181) | center 0.0865; pad 0.0843; tile 0.1144 | 782 | 464 | 11576->10950 | 55 | 0 | dinov2_b__center, dinov2_b__pad, dinov2_b__tile |
| j2_dinov2b_repro | repro | `--views center,pad,tile --autocrop none` | 689 | 2 | 192 (161+31) | center 0.0937; pad 0.0978; tile 0.111 | 440 | 464 | 10950->12236; 12703->12866 | 42, 32 | 1 (+1076 MB) | dinov2_b__center, dinov2_b__pad, dinov2_b__tile |
| j2_dinov2b_repro_autocrop_frame | repro_autocrop_frame | `--views pad --autocrop frame` | 689 | 1 | 89 (89) | pad 0.1019 | 533 | 397 | 12866->13729 | 34 | 0 | dinov2_b__pad |
| j2_dinov2b_pilot | pilot | `--views center,pad,tile --autocrop none` | 2000 | 2 | 625 (465+160) | center 0.0746; pad 0.0776; tile 0.1173 | 801 | 1504 | 13729->15825; 11784->11648 | 57, 58 | 1 (+2264 MB) | dinov2_b__center, dinov2_b__pad, dinov2_b__tile |
| j3_siglip2b_versions | versions | `--views center,pad,tile --autocrop none` | 355 | 2 | 449 (381+68) | center 0.0442; pad 0.0454; tile 0.0651 | 425 | 450 | 11648->14702; 14039->14662 | 51, 32 | 1 (+3118 MB) | siglip2_b__center, siglip2_b__pad, siglip2_b__tile |
| j3_siglip2b_repro | repro | `--views center,pad,tile --autocrop none` | 689 | 1 | 121 (121) | center 0.047; pad 0.046; tile 0.0622 | 484 | 450 | 14662->14380 | 32 | 0 | siglip2_b__center, siglip2_b__pad, siglip2_b__tile |
| j3_siglip2b_pilot | pilot | `--views center,pad,tile --autocrop none` | 2000 | 1 | 332 (332) | center 0.0456; pad 0.0436; tile 0.0653 | 545 | 1557 | 14380->11137 | 34 | 0 | siglip2_b__center, siglip2_b__pad, siglip2_b__tile |
| j4_dinov2l_versions | versions | `--views pad,tile --autocrop none --fp16` | 355 | 2 | 434 (332+102) | pad 0.0998; tile 0.1497 | 1486 | 733 | 11121->15394; 15114->14747 | 52, 40 | 1 (+4305 MB) | dinov2_l__pad, dinov2_l__tile |
| j4_dinov2l_repro | repro | `--views pad,tile --autocrop none --fp16` | 689 | 1 | 174 (174) | pad 0.0942; tile 0.139 | 2259 | 733 | 14747->10988 | 75 | 0 | dinov2_l__pad, dinov2_l__tile |
| j4_dinov2l_pilot | pilot | `--views pad,tile --autocrop none --fp16` | 2000 | 1 | 501 (501) | pad 0.0944; tile 0.1451 | 2268 | 800 | 10972->10440 | 78 | 0 | dinov2_l__pad, dinov2_l__tile |
| j5_clipl_versions | versions | `--views pad,tile --autocrop none --fp16` | 355 | 1 | 112 (112) | pad 0.1053; tile 0.172 | 1775 | 682 | 10288->10494 | 43 | 0 | clip_l__pad, clip_l__tile |
| j5_clipl_repro | repro | `--views pad,tile --autocrop none --fp16` | 689 | 1 | 152 (152) | pad 0.0768; tile 0.123 | 1771 | 682 | 10494->10462 | 42 | 0 | clip_l__pad, clip_l__tile |
| j5_clipl_pilot | pilot | `--views pad,tile --autocrop none --fp16` | 2000 | 1 | 343 (343) | pad 0.0577; tile 0.1024 | 1812 | 1756 | 10462->10278 | 68 | 0 | clip_l__pad, clip_l__tile |
| j6_csdl_versions | versions | `--views pad,tile --autocrop none --fp16 --csd-allow-listed-globals` | 355 | 2 | 130 (65+65) | pad 0.0568; tile 0.0984 | 2582 | 693 | 9806->9790; 10334->10310 | 62, 71 | 0 | csd_l__pad, csd_l__tile |
| j6_csdl_repro | repro | `--views pad,tile --autocrop none --fp16 --csd-allow-listed-globals` | 689 | 1 | 116 (116) | pad 0.057; tile 0.0967 | 2746 | 686 | 10302->10246 | 66 | 0 | csd_l__pad, csd_l__tile |
| j6_csdl_pilot | pilot | `--views pad,tile --autocrop none --fp16 --csd-allow-listed-globals` | 2000 | 1 | 346 (346) | pad 0.058; tile 0.1057 | 2453 | 1769 | 10246->10241 | 67 | 0 | csd_l__pad, csd_l__tile |

Weights were kept between the three sets of one model and removed after the pilot job
(`--cleanup-weights`); `data/painting2vec/models` holds only `hf/hub/CACHEDIR.TAG` (191 bytes) at
the end. Sources: `facebook/dinov2-with-registers-base`, `google/siglip2-base-patch16-224`,
`facebook/dinov2-with-registers-large`, `openai/clip-vit-large-patch14`, `tomg-group-umd/CSD-ViT-L`.

### Guard trips

Four, all the swap guard (`--max-swap-growth-mb 1024`), all resumed once and completed. None hit
three trips, so no model was skipped.

| job | stopped at | swap growth reported | what was happening |
|---|---|---|---|
| j2_dinov2b_repro | 620 / 689 | 1,076 MB | mid-run; process was 0.6 GB RSS + 0.46 GB MPS |
| j2_dinov2b_pilot | 1,780 / 2,000 | 2,264 MB | mid-run; MPS allocation had grown to 1.5 GB. The trip also triggered `--cleanup-weights`, so the resume downloaded the 346 MB again |
| j3_siglip2b_versions | 3 / 355 | 3,118 MB | the guard's baseline is taken before the download; swap rose during the 5-minute download |
| j4_dinov2l_versions | 3 / 355 | 4,305 MB | the same, during the 1.2 GB download |

System swap moved between 9.8 and 15.8 GB over the evening with other sessions' Python, Node and
Chrome processes running, so these cannot be pinned on the feature jobs; the last two clearly were
not, since only three images had been embedded. From job 5 on the runner fetched the weights in a
separate step before the guarded run, and there were no further trips. The guards were never
disabled or loosened.

### Other incidents

- CSD download: the first attempt (Hugging Face's xet transport) ran 19 minutes, failed with
  "CAS Client Error ... error decoding response body" and discarded 1.2 GB. Retried over plain HTTP
  (`HF_HUB_DISABLE_XET=1`, resumable), which took 68 minutes for 2.4 GB at about 0.6 MB/s. The link
  was that slow for the rest of the evening.
- `siglip2_so400m` (optional job 7) was not run and no block was added. Its checkpoint is 4.54 GB
  (`google/siglip2-so400m-patch14-384`, Apache-2.0, one safetensors file with both towers); a probe
  measured 0.35 MB/s, about three hours. The condition that memory had been calm was also not
  clearly met (four swap-guard trips, swap near its ceiling all evening).

## Code changes made for these runs

1. `preprocess.model_views`, `pad` view: a strip thinner than one patch covered no patch by half,
   which left the patch statistics empty (NaN). Now the patches it covers most are kept. Affects
   15 pilot handscrolls at patch 14 and 16 at patch 16 (listed below); no other image.
2. `embed.py`, `clip_l`: the extra `backbone` part, with a one-time check that projecting it
   reproduces `image_embeds` (passed in every run).
3. `embed._load_csd`: see the next section.

## CSD

Loaded with `--csd-allow-listed-globals`: `torch.load(weights_only=True, mmap=True)` with exactly
four names allow-listed, `argparse.Namespace`, `numpy.core.multiarray.scalar`, `numpy.dtype`,
`_codecs.encode`. It loaded on the first try under that list; the file needs no other global.

One change from the code as written. The earlier version also allow-listed two concrete NumPy dtype
classes (`Float64DType`, `Int64DType`), which torch needs before it will restore a real
`numpy.dtype`'s state, and under NumPy 2 `numpy.core` has moved. Rather than widen the list,
three of the four names now resolve to do-nothing stand-ins (`_InertPickled`, `_inert_pickled_call`)
registered under the pickle's own names; `argparse.Namespace` is the real class. So the NumPy
scalars in the training record are discarded unread and only tensors are loaded. `weights_only=False`
was never used.

What the load reported: top-level keys `args, fp16_scaler, iter, model_state_dict, opt_bb, opt_proj`;
297 tensors loaded with `strict=True`, none missing, none unused.

Sanity check on the versions set (355 images), cosine per image:

| view | CSD `backbone` vs CLIP `backbone`, min / mean / max | CSD `style` vs `content` | `style` vs CLIP `embed`, mean | `content` vs CLIP `embed`, mean |
|---|---|---|---|---|
| pad | 0.525 / 0.703 / 0.850 | 0.673 / 0.776 / 0.851 | 0.509 | 0.732 |
| tile | 0.533 / 0.725 / 0.859 | 0.686 / 0.783 / 0.885 | 0.527 | 0.755 |

So CSD's tower output is related to plain CLIP ViT-L/14 and not equal to it, the two heads differ
from each other, and both are saved (`style`, `content`, plus `backbone`). This was checked on the
versions set only, not repeated on repro or pilot. Under `tile`, `style` and `content` are means
of unit vectors over tiles, so their norms fall below 1 (minimum 0.82, on the pilot set); renormalise if needed.
CSD's weights are CC-BY-4.0 and need attribution.

## Odd images

No image failed or was skipped in any job: no `errors.txt` was written in any output directory.

Handscroll strips (20 pilot images with a short side under 100 px; 17 are beyond 14:1, the extreme
is `Q121362966` at 1,024 x 21):

- colour, composition: the statistics image keeps the aspect ratio (about 1,788 x 37 for the
  extreme case, upsampled). Finite values for all 20.
- `center`: the short side is upsampled to 224 (10.7 times for the extreme) and the middle square
  kept, so the model sees about 2 per cent of the scroll.
- `tile`: the same upsampling, then 5 tiles spread end to end (the cap); most of a long scroll
  falls between tiles.
- `pad`: the scroll becomes a band 5 to 14 px high on a 224 px square. With the fix above its
  patch statistics come from the one row of 16 patches it overlaps most. Images using that
  fallback at patch 14 (DINOv2, CLIP, CSD): Q10881982, Q11135165, Q112971367, Q113167718,
  Q113180355, Q113260443, Q121362966, Q121363572, Q15592269, Q15904093, Q24833100, Q4807363,
  Q59168132, Q59208406, Q706846; at patch 16 (SigLIP 2) also Q10296754.

These rows exist and are finite, but as the dataset README says the images are useless at this
size. Excluding them is a decision for the analysis.

Greyscale: every file is stored as a 3-channel JPEG, so nothing special happens at load. Six pilot
images have equal channels (Q106864313, Q1778000, Q2395137, Q78727757, Q78834676, Q78875327); for
those the colour block's near-grey share is 1.000, mean chroma 0, and the hue histogram is all
zero. The dataset README counts 8 greyscale images; the other two (Q78761942, Q12615728) are not
neutral by this test (channels differ by more than 2 levels) and were not looked at.

Square images give `composition.aspect` = 0 (15 pilot, 7 repro, 2 versions). That is the only
zero-norm part anywhere.

## Auto-crop on the repro set

How many of the 689 images each mode actually cropped (recomputed afterwards with
`preprocess.autocrop_box`; not judged for correctness, nobody looked at the crops):

| mode | cropped | area removed where cropped, median / max | by source, cropped / total |
|---|---|---|---|
| border | 125 | 3.6 % / 54.9 % | commons 68/554, met 50/66, cleveland 3/3, rijksmuseum 3/21, aic 1/9, nga 0/36 |
| frame | 137 | 6.0 % / 61.7 % | commons 79/554, met 50/66, cleveland 3/3, rijksmuseum 4/21, aic 1/9, nga 0/36 |

For the other 564 (border) or 552 (frame) images the auto-cropped features are the same input as
`repro/`.

## What was verified, and what was not

Verified after every job, by `logs/scripts/verify.py`, for all 67 stores:

- row count equals the number of image files in the set, for every part;
- the ids are exactly the file stems, with no duplicates, in sorted order;
- no NaN or inf in any row of any part;
- per-part vector norms (minimum, median, maximum; full table below) and zero-norm rows.

Also checked: the CLIP `backbone` consistency check; the CSD comparison above; float16 headroom;
`data/painting2vec/models` empty at the end.

Not verified:

- that any vector is good for anything. No neighbours, distances between pairs or plots were looked at.
- norms were read for gross faults (zeros, blow-ups, a constant part) and nothing more. `colour__rank`
  `lightness` is constant by construction (norm 1.577 for every row), as the README says.
- resumed jobs against a single uninterrupted pass. The README reports byte-identical results for
  a 10-image test; that was not repeated here.
- `dinov2_l`, `clip_l`, `csd_l` in float16 against float32.
- the auto-crop boxes by eye.
- the CSD re-implementation against the authors' own code on the same image. What is known: the
  tower matches transformers' CLIP when given OpenAI's weights (earlier check, `features.checks`),
  and the CSD state dict loads strictly.

## Appendix: norms of every part

| set | store | part | norm min | median | max | zero-norm rows | non-finite rows |
|---|---|---|---|---|---|---|---|
| pilot | clip_l__pad | embed | 15 | 17.97 | 21.07 | 0 | 0 |
| pilot | clip_l__pad | backbone | 30.86 | 32.82 | 34.1 | 0 | 0 |
| pilot | clip_l__tile | embed | 14.92 | 17.25 | 20.89 | 0 | 0 |
| pilot | clip_l__tile | backbone | 26.59 | 32.47 | 33.8 | 0 | 0 |
| pilot | colour__greyworld | palette_hist | 1 | 1 | 1 | 0 | 0 |
| pilot | colour__greyworld | palette_sw | 0.07117 | 0.2172 | 0.4001 | 0 | 0 |
| pilot | colour__greyworld | palette_kmeans | 0.8554 | 1.392 | 2.15 | 0 | 0 |
| pilot | colour__greyworld | lightness | 1.055 | 1.445 | 2.048 | 0 | 0 |
| pilot | colour__greyworld | chroma | 1 | 1.003 | 1.029 | 0 | 0 |
| pilot | colour__greyworld | hue | 1 | 1.092 | 1.414 | 0 | 0 |
| pilot | colour__lstd | palette_hist | 1 | 1 | 1 | 0 | 0 |
| pilot | colour__lstd | palette_sw | 0.2176 | 0.2347 | 0.2482 | 0 | 0 |
| pilot | colour__lstd | palette_kmeans | 1.1 | 1.477 | 1.93 | 0 | 0 |
| pilot | colour__lstd | lightness | 1.413 | 1.512 | 1.612 | 0 | 0 |
| pilot | colour__lstd | chroma | 1 | 1.005 | 1.033 | 0 | 0 |
| pilot | colour__lstd | hue | 1 | 1.027 | 1.414 | 0 | 0 |
| pilot | colour__rank | palette_hist | 1 | 1 | 1 | 0 | 0 |
| pilot | colour__rank | palette_sw | 0.2529 | 0.2588 | 0.2669 | 0 | 0 |
| pilot | colour__rank | palette_kmeans | 1.188 | 1.493 | 1.945 | 0 | 0 |
| pilot | colour__rank | lightness | 1.577 | 1.577 | 1.577 | 0 | 0 |
| pilot | colour__rank | chroma | 1 | 1.024 | 1.053 | 0 | 0 |
| pilot | colour__rank | hue | 1 | 1.002 | 1.414 | 0 | 0 |
| pilot | colour__raw | palette_hist | 1 | 1 | 1 | 0 | 0 |
| pilot | colour__raw | palette_sw | 0.07412 | 0.2196 | 0.4011 | 0 | 0 |
| pilot | colour__raw | palette_kmeans | 0.8981 | 1.41 | 2.177 | 0 | 0 |
| pilot | colour__raw | lightness | 1.061 | 1.455 | 2.068 | 0 | 0 |
| pilot | colour__raw | chroma | 1 | 1.005 | 1.033 | 0 | 0 |
| pilot | colour__raw | hue | 1 | 1.027 | 1.414 | 0 | 0 |
| pilot | colour__std | palette_hist | 1 | 1 | 1 | 0 | 0 |
| pilot | colour__std | palette_sw | 0.2191 | 0.2425 | 0.2526 | 0 | 0 |
| pilot | colour__std | palette_kmeans | 1.095 | 1.478 | 2.01 | 0 | 0 |
| pilot | colour__std | lightness | 1.413 | 1.512 | 1.612 | 0 | 0 |
| pilot | colour__std | chroma | 1 | 1.024 | 1.053 | 0 | 0 |
| pilot | colour__std | hue | 1 | 1.002 | 1.414 | 0 | 0 |
| pilot | composition | grid8_an | 3.611 | 8.708 | 13.14 | 0 | 0 |
| pilot | composition | grid8_ap | 0.2619 | 6.86 | 10.99 | 0 | 0 |
| pilot | composition | grid4_an | 1.126 | 3.39 | 6.014 | 0 | 0 |
| pilot | composition | grid4_ap | 0.06881 | 2.452 | 4.726 | 0 | 0 |
| pilot | composition | symmetry | 0.1077 | 0.8277 | 2.384 | 0 | 0 |
| pilot | composition | balance | 1.138 | 1.381 | 1.58 | 0 | 0 |
| pilot | composition | edges | 1.585 | 1.741 | 1.942 | 0 | 0 |
| pilot | composition | spectrum | 6.726 | 10.12 | 11.69 | 0 | 0 |
| pilot | composition | saliency | 1.234 | 1.391 | 1.417 | 0 | 0 |
| pilot | composition | aspect | 0 | 0.3035 | 3.878 | 15 | 0 |
| pilot | csd_l__pad | style | 0.9996 | 1 | 1 | 0 | 0 |
| pilot | csd_l__pad | content | 0.9996 | 1 | 1 | 0 | 0 |
| pilot | csd_l__pad | backbone | 31.22 | 32.51 | 33.49 | 0 | 0 |
| pilot | csd_l__tile | style | 0.8168 | 0.9891 | 1 | 0 | 0 |
| pilot | csd_l__tile | content | 0.9093 | 0.994 | 1 | 0 | 0 |
| pilot | csd_l__tile | backbone | 29.21 | 32.41 | 33.42 | 0 | 0 |
| pilot | dinov2_b__center | cls | 19.37 | 24.48 | 26.89 | 0 | 0 |
| pilot | dinov2_b__center | patch_mean | 11.07 | 14.23 | 22.18 | 0 | 0 |
| pilot | dinov2_b__center | meanstd_early | 2.522 | 3.046 | 3.604 | 0 | 0 |
| pilot | dinov2_b__center | gram_early | 0.5288 | 1.49 | 2.7 | 0 | 0 |
| pilot | dinov2_b__center | meanstd_mid | 5.154 | 5.481 | 5.932 | 0 | 0 |
| pilot | dinov2_b__center | gram_mid | 3.856 | 5.624 | 8.636 | 0 | 0 |
| pilot | dinov2_b__center | meanstd_late | 106.3 | 141.7 | 160.3 | 0 | 0 |
| pilot | dinov2_b__center | gram_late | 799 | 2975 | 6746 | 0 | 0 |
| pilot | dinov2_b__pad | cls | 21.05 | 24.46 | 26.91 | 0 | 0 |
| pilot | dinov2_b__pad | patch_mean | 11.18 | 14.37 | 24.11 | 0 | 0 |
| pilot | dinov2_b__pad | meanstd_early | 2.624 | 3.127 | 3.796 | 0 | 0 |
| pilot | dinov2_b__pad | gram_early | 0.5695 | 1.598 | 3.275 | 0 | 0 |
| pilot | dinov2_b__pad | meanstd_mid | 5.197 | 5.554 | 6.22 | 0 | 0 |
| pilot | dinov2_b__pad | gram_mid | 3.671 | 5.87 | 10.08 | 0 | 0 |
| pilot | dinov2_b__pad | meanstd_late | 109.7 | 141.2 | 168.3 | 0 | 0 |
| pilot | dinov2_b__pad | gram_late | 656.1 | 2919 | 6261 | 0 | 0 |
| pilot | dinov2_b__tile | cls | 15.91 | 23.79 | 26.49 | 0 | 0 |
| pilot | dinov2_b__tile | patch_mean | 10.74 | 13.89 | 18.76 | 0 | 0 |
| pilot | dinov2_b__tile | meanstd_early | 2.537 | 3.031 | 3.535 | 0 | 0 |
| pilot | dinov2_b__tile | gram_early | 0.6765 | 1.457 | 2.864 | 0 | 0 |
| pilot | dinov2_b__tile | meanstd_mid | 5.16 | 5.483 | 5.859 | 0 | 0 |
| pilot | dinov2_b__tile | gram_mid | 4.032 | 5.551 | 8.354 | 0 | 0 |
| pilot | dinov2_b__tile | meanstd_late | 118.6 | 141.3 | 162 | 0 | 0 |
| pilot | dinov2_b__tile | gram_late | 1328 | 2922 | 5957 | 0 | 0 |
| pilot | dinov2_l__pad | cls | 18.36 | 22.78 | 24.82 | 0 | 0 |
| pilot | dinov2_l__pad | patch_mean | 9.191 | 11.45 | 19.59 | 0 | 0 |
| pilot | dinov2_l__pad | meanstd_early | 4.437 | 5.46 | 6.712 | 0 | 0 |
| pilot | dinov2_l__pad | gram_early | 1.426 | 5.749 | 13.12 | 0 | 0 |
| pilot | dinov2_l__pad | meanstd_mid | 11.24 | 12.04 | 13.58 | 0 | 0 |
| pilot | dinov2_l__pad | gram_mid | 18.14 | 32.94 | 47.85 | 0 | 0 |
| pilot | dinov2_l__pad | meanstd_late | 209.8 | 266.9 | 291.2 | 0 | 0 |
| pilot | dinov2_l__pad | gram_late | 4509 | 1.183e+04 | 2.508e+04 | 0 | 0 |
| pilot | dinov2_l__tile | cls | 13.83 | 22.27 | 24.7 | 0 | 0 |
| pilot | dinov2_l__tile | patch_mean | 8.758 | 11.11 | 13.97 | 0 | 0 |
| pilot | dinov2_l__tile | meanstd_early | 4.307 | 5.291 | 6.291 | 0 | 0 |
| pilot | dinov2_l__tile | gram_early | 2.134 | 5.174 | 8.632 | 0 | 0 |
| pilot | dinov2_l__tile | meanstd_mid | 11.14 | 11.88 | 12.64 | 0 | 0 |
| pilot | dinov2_l__tile | gram_mid | 21 | 31.36 | 44.16 | 0 | 0 |
| pilot | dinov2_l__tile | meanstd_late | 201.8 | 266.6 | 295.5 | 0 | 0 |
| pilot | dinov2_l__tile | gram_late | 5318 | 1.148e+04 | 2.868e+04 | 0 | 0 |
| pilot | siglip2_b__center | embed | 9.54 | 10.89 | 14.05 | 0 | 0 |
| pilot | siglip2_b__center | patch_mean | 25.87 | 30.45 | 37.35 | 0 | 0 |
| pilot | siglip2_b__pad | embed | 8.968 | 10.83 | 14.23 | 0 | 0 |
| pilot | siglip2_b__pad | patch_mean | 24.73 | 30.76 | 37.68 | 0 | 0 |
| pilot | siglip2_b__tile | embed | 9.048 | 10.65 | 14.05 | 0 | 0 |
| pilot | siglip2_b__tile | patch_mean | 25.81 | 29.95 | 35.97 | 0 | 0 |
| repro | clip_l__pad | embed | 15.08 | 18.18 | 21.07 | 0 | 0 |
| repro | clip_l__pad | backbone | 31.17 | 32.91 | 33.92 | 0 | 0 |
| repro | clip_l__tile | embed | 15.34 | 17.52 | 20.89 | 0 | 0 |
| repro | clip_l__tile | backbone | 30.23 | 32.7 | 34.07 | 0 | 0 |
| repro | colour__greyworld | palette_hist | 1 | 1 | 1 | 0 | 0 |
| repro | colour__greyworld | palette_sw | 0.07111 | 0.2076 | 0.3742 | 0 | 0 |
| repro | colour__greyworld | palette_kmeans | 0.8042 | 1.358 | 1.867 | 0 | 0 |
| repro | colour__greyworld | lightness | 1.062 | 1.416 | 1.933 | 0 | 0 |
| repro | colour__greyworld | chroma | 1 | 1.002 | 1.029 | 0 | 0 |
| repro | colour__greyworld | hue | 1 | 1.11 | 1.414 | 0 | 0 |
| repro | colour__lstd | palette_hist | 1 | 1 | 1 | 0 | 0 |
| repro | colour__lstd | palette_sw | 0.2215 | 0.2347 | 0.2459 | 0 | 0 |
| repro | colour__lstd | palette_kmeans | 1.154 | 1.493 | 1.958 | 0 | 0 |
| repro | colour__lstd | lightness | 1.414 | 1.511 | 1.612 | 0 | 0 |
| repro | colour__lstd | chroma | 1 | 1.005 | 1.025 | 0 | 0 |
| repro | colour__lstd | hue | 1 | 1.038 | 1.414 | 0 | 0 |
| repro | colour__rank | palette_hist | 1 | 1 | 1 | 0 | 0 |
| repro | colour__rank | palette_sw | 0.2533 | 0.2589 | 0.2661 | 0 | 0 |
| repro | colour__rank | palette_kmeans | 1.271 | 1.505 | 1.775 | 0 | 0 |
| repro | colour__rank | lightness | 1.577 | 1.577 | 1.577 | 0 | 0 |
| repro | colour__rank | chroma | 1 | 1.024 | 1.041 | 0 | 0 |
| repro | colour__rank | hue | 1 | 1.002 | 1.414 | 0 | 0 |
| repro | colour__raw | palette_hist | 1 | 1 | 1 | 0 | 0 |
| repro | colour__raw | palette_sw | 0.07323 | 0.2094 | 0.3783 | 0 | 0 |
| repro | colour__raw | palette_kmeans | 0.8325 | 1.375 | 1.986 | 0 | 0 |
| repro | colour__raw | lightness | 1.067 | 1.425 | 1.956 | 0 | 0 |
| repro | colour__raw | chroma | 1 | 1.005 | 1.025 | 0 | 0 |
| repro | colour__raw | hue | 1 | 1.038 | 1.414 | 0 | 0 |
| repro | colour__std | palette_hist | 1 | 1 | 1 | 0 | 0 |
| repro | colour__std | palette_sw | 0.2264 | 0.2425 | 0.2518 | 0 | 0 |
| repro | colour__std | palette_kmeans | 1.123 | 1.494 | 2.039 | 0 | 0 |
| repro | colour__std | lightness | 1.414 | 1.511 | 1.612 | 0 | 0 |
| repro | colour__std | chroma | 1 | 1.024 | 1.041 | 0 | 0 |
| repro | colour__std | hue | 1 | 1.002 | 1.414 | 0 | 0 |
| repro | composition | grid8_an | 3.611 | 8.782 | 13.14 | 0 | 0 |
| repro | composition | grid8_ap | 1.585 | 7.047 | 10.79 | 0 | 0 |
| repro | composition | grid4_an | 1.095 | 3.421 | 6.014 | 0 | 0 |
| repro | composition | grid4_ap | 0.4385 | 2.562 | 4.505 | 0 | 0 |
| repro | composition | symmetry | 0.2013 | 0.839 | 2.305 | 0 | 0 |
| repro | composition | balance | 1.144 | 1.384 | 1.58 | 0 | 0 |
| repro | composition | edges | 1.541 | 1.732 | 1.942 | 0 | 0 |
| repro | composition | spectrum | 7.145 | 10.11 | 11.27 | 0 | 0 |
| repro | composition | saliency | 1.287 | 1.388 | 1.416 | 0 | 0 |
| repro | composition | aspect | 0 | 0.2843 | 1.099 | 8 | 0 |
| repro | csd_l__pad | style | 0.9996 | 1 | 1 | 0 | 0 |
| repro | csd_l__pad | content | 0.9996 | 1 | 1 | 0 | 0 |
| repro | csd_l__pad | backbone | 31.43 | 32.57 | 33.63 | 0 | 0 |
| repro | csd_l__tile | style | 0.8918 | 0.9915 | 1 | 0 | 0 |
| repro | csd_l__tile | content | 0.948 | 0.9953 | 1 | 0 | 0 |
| repro | csd_l__tile | backbone | 31.06 | 32.5 | 33.55 | 0 | 0 |
| repro | dinov2_b__center | cls | 21.6 | 24.42 | 26.71 | 0 | 0 |
| repro | dinov2_b__center | patch_mean | 11.65 | 14 | 18.15 | 0 | 0 |
| repro | dinov2_b__center | meanstd_early | 2.608 | 3.032 | 3.57 | 0 | 0 |
| repro | dinov2_b__center | gram_early | 0.8053 | 1.487 | 2.878 | 0 | 0 |
| repro | dinov2_b__center | meanstd_mid | 5.146 | 5.479 | 5.932 | 0 | 0 |
| repro | dinov2_b__center | gram_mid | 4.206 | 5.65 | 9.675 | 0 | 0 |
| repro | dinov2_b__center | meanstd_late | 120.3 | 141.3 | 161 | 0 | 0 |
| repro | dinov2_b__center | gram_late | 1637 | 3029 | 5759 | 0 | 0 |
| repro | dinov2_b__pad | cls | 21.5 | 24.31 | 26.54 | 0 | 0 |
| repro | dinov2_b__pad | patch_mean | 11.73 | 14.22 | 18.39 | 0 | 0 |
| repro | dinov2_b__pad | meanstd_early | 2.682 | 3.096 | 3.796 | 0 | 0 |
| repro | dinov2_b__pad | gram_early | 0.7961 | 1.577 | 3.07 | 0 | 0 |
| repro | dinov2_b__pad | meanstd_mid | 5.156 | 5.541 | 6.026 | 0 | 0 |
| repro | dinov2_b__pad | gram_mid | 4.037 | 5.875 | 9.8 | 0 | 0 |
| repro | dinov2_b__pad | meanstd_late | 121.3 | 141.1 | 163.9 | 0 | 0 |
| repro | dinov2_b__pad | gram_late | 1532 | 2917 | 5534 | 0 | 0 |
| repro | dinov2_b__tile | cls | 18.46 | 23.81 | 26.15 | 0 | 0 |
| repro | dinov2_b__tile | patch_mean | 11.36 | 13.75 | 17.67 | 0 | 0 |
| repro | dinov2_b__tile | meanstd_early | 2.601 | 3.025 | 3.51 | 0 | 0 |
| repro | dinov2_b__tile | gram_early | 0.7874 | 1.452 | 2.809 | 0 | 0 |
| repro | dinov2_b__tile | meanstd_mid | 5.146 | 5.484 | 5.859 | 0 | 0 |
| repro | dinov2_b__tile | gram_mid | 4.206 | 5.596 | 9.291 | 0 | 0 |
| repro | dinov2_b__tile | meanstd_late | 122 | 141 | 162 | 0 | 0 |
| repro | dinov2_b__tile | gram_late | 1637 | 2916 | 5143 | 0 | 0 |
| repro | dinov2_l__pad | cls | 18.98 | 22.67 | 24.22 | 0 | 0 |
| repro | dinov2_l__pad | patch_mean | 9.323 | 11.42 | 13.71 | 0 | 0 |
| repro | dinov2_l__pad | meanstd_early | 4.577 | 5.394 | 6.465 | 0 | 0 |
| repro | dinov2_l__pad | gram_early | 3.391 | 5.582 | 9.023 | 0 | 0 |
| repro | dinov2_l__pad | meanstd_mid | 11.34 | 12.02 | 12.79 | 0 | 0 |
| repro | dinov2_l__pad | gram_mid | 26.91 | 32.81 | 47 | 0 | 0 |
| repro | dinov2_l__pad | meanstd_late | 230.9 | 266.3 | 290.1 | 0 | 0 |
| repro | dinov2_l__pad | gram_late | 7556 | 1.17e+04 | 1.963e+04 | 0 | 0 |
| repro | dinov2_l__tile | cls | 17.83 | 22.26 | 24 | 0 | 0 |
| repro | dinov2_l__tile | patch_mean | 9.086 | 11.2 | 13.17 | 0 | 0 |
| repro | dinov2_l__tile | meanstd_early | 4.444 | 5.264 | 6.344 | 0 | 0 |
| repro | dinov2_l__tile | gram_early | 2.989 | 5.164 | 8.632 | 0 | 0 |
| repro | dinov2_l__tile | meanstd_mid | 11.17 | 11.89 | 12.65 | 0 | 0 |
| repro | dinov2_l__tile | gram_mid | 25.94 | 31.51 | 42.19 | 0 | 0 |
| repro | dinov2_l__tile | meanstd_late | 236.2 | 267.1 | 284.6 | 0 | 0 |
| repro | dinov2_l__tile | gram_late | 7046 | 1.153e+04 | 1.961e+04 | 0 | 0 |
| repro | siglip2_b__center | embed | 9.613 | 10.81 | 14.06 | 0 | 0 |
| repro | siglip2_b__center | patch_mean | 25.18 | 30.14 | 34.24 | 0 | 0 |
| repro | siglip2_b__pad | embed | 9.289 | 10.81 | 14.23 | 0 | 0 |
| repro | siglip2_b__pad | patch_mean | 23.59 | 30.51 | 35.54 | 0 | 0 |
| repro | siglip2_b__tile | embed | 9.306 | 10.63 | 14.06 | 0 | 0 |
| repro | siglip2_b__tile | patch_mean | 24.85 | 29.7 | 34.53 | 0 | 0 |
| repro_autocrop_border | colour__greyworld | palette_hist | 1 | 1 | 1 | 0 | 0 |
| repro_autocrop_border | colour__greyworld | palette_sw | 0.07111 | 0.2087 | 0.3741 | 0 | 0 |
| repro_autocrop_border | colour__greyworld | palette_kmeans | 0.8576 | 1.363 | 1.953 | 0 | 0 |
| repro_autocrop_border | colour__greyworld | lightness | 1.062 | 1.419 | 1.926 | 0 | 0 |
| repro_autocrop_border | colour__greyworld | chroma | 1 | 1.002 | 1.029 | 0 | 0 |
| repro_autocrop_border | colour__greyworld | hue | 1 | 1.11 | 1.414 | 0 | 0 |
| repro_autocrop_border | colour__lstd | palette_hist | 1 | 1 | 1 | 0 | 0 |
| repro_autocrop_border | colour__lstd | palette_sw | 0.2215 | 0.2347 | 0.2459 | 0 | 0 |
| repro_autocrop_border | colour__lstd | palette_kmeans | 1.154 | 1.496 | 1.958 | 0 | 0 |
| repro_autocrop_border | colour__lstd | lightness | 1.414 | 1.512 | 1.612 | 0 | 0 |
| repro_autocrop_border | colour__lstd | chroma | 1 | 1.005 | 1.025 | 0 | 0 |
| repro_autocrop_border | colour__lstd | hue | 1 | 1.037 | 1.414 | 0 | 0 |
| repro_autocrop_border | colour__rank | palette_hist | 1 | 1 | 1 | 0 | 0 |
| repro_autocrop_border | colour__rank | palette_sw | 0.2528 | 0.2589 | 0.2659 | 0 | 0 |
| repro_autocrop_border | colour__rank | palette_kmeans | 1.271 | 1.502 | 1.775 | 0 | 0 |
| repro_autocrop_border | colour__rank | lightness | 1.577 | 1.577 | 1.577 | 0 | 0 |
| repro_autocrop_border | colour__rank | chroma | 1 | 1.024 | 1.041 | 0 | 0 |
| repro_autocrop_border | colour__rank | hue | 1 | 1.002 | 1.414 | 0 | 0 |
| repro_autocrop_border | colour__raw | palette_hist | 1 | 1 | 1 | 0 | 0 |
| repro_autocrop_border | colour__raw | palette_sw | 0.07323 | 0.2099 | 0.3782 | 0 | 0 |
| repro_autocrop_border | colour__raw | palette_kmeans | 0.8759 | 1.38 | 2.003 | 0 | 0 |
| repro_autocrop_border | colour__raw | lightness | 1.067 | 1.429 | 1.955 | 0 | 0 |
| repro_autocrop_border | colour__raw | chroma | 1 | 1.005 | 1.025 | 0 | 0 |
| repro_autocrop_border | colour__raw | hue | 1 | 1.037 | 1.414 | 0 | 0 |
| repro_autocrop_border | colour__std | palette_hist | 1 | 1 | 1 | 0 | 0 |
| repro_autocrop_border | colour__std | palette_sw | 0.2264 | 0.2424 | 0.2491 | 0 | 0 |
| repro_autocrop_border | colour__std | palette_kmeans | 1.123 | 1.496 | 2.039 | 0 | 0 |
| repro_autocrop_border | colour__std | lightness | 1.414 | 1.512 | 1.612 | 0 | 0 |
| repro_autocrop_border | colour__std | chroma | 1 | 1.024 | 1.041 | 0 | 0 |
| repro_autocrop_border | colour__std | hue | 1 | 1.002 | 1.414 | 0 | 0 |
| repro_autocrop_border | composition | grid8_an | 3.442 | 8.827 | 13.25 | 0 | 0 |
| repro_autocrop_border | composition | grid8_ap | 1.721 | 7.109 | 10.79 | 0 | 0 |
| repro_autocrop_border | composition | grid4_an | 1.081 | 3.453 | 6.014 | 0 | 0 |
| repro_autocrop_border | composition | grid4_ap | 0.4664 | 2.573 | 4.505 | 0 | 0 |
| repro_autocrop_border | composition | symmetry | 0.2013 | 0.8167 | 2.283 | 0 | 0 |
| repro_autocrop_border | composition | balance | 1.144 | 1.384 | 1.578 | 0 | 0 |
| repro_autocrop_border | composition | edges | 1.573 | 1.734 | 1.942 | 0 | 0 |
| repro_autocrop_border | composition | spectrum | 7.145 | 10.16 | 11.46 | 0 | 0 |
| repro_autocrop_border | composition | saliency | 1.287 | 1.388 | 1.416 | 0 | 0 |
| repro_autocrop_border | composition | aspect | 0 | 0.2843 | 1.099 | 7 | 0 |
| repro_autocrop_frame | colour__greyworld | palette_hist | 1 | 1 | 1 | 0 | 0 |
| repro_autocrop_frame | colour__greyworld | palette_sw | 0.07111 | 0.2077 | 0.3741 | 0 | 0 |
| repro_autocrop_frame | colour__greyworld | palette_kmeans | 0.8576 | 1.364 | 1.953 | 0 | 0 |
| repro_autocrop_frame | colour__greyworld | lightness | 1.062 | 1.418 | 1.926 | 0 | 0 |
| repro_autocrop_frame | colour__greyworld | chroma | 1 | 1.002 | 1.029 | 0 | 0 |
| repro_autocrop_frame | colour__greyworld | hue | 1 | 1.11 | 1.414 | 0 | 0 |
| repro_autocrop_frame | colour__lstd | palette_hist | 1 | 1 | 1 | 0 | 0 |
| repro_autocrop_frame | colour__lstd | palette_sw | 0.2215 | 0.2346 | 0.2459 | 0 | 0 |
| repro_autocrop_frame | colour__lstd | palette_kmeans | 1.154 | 1.498 | 1.958 | 0 | 0 |
| repro_autocrop_frame | colour__lstd | lightness | 1.414 | 1.512 | 1.612 | 0 | 0 |
| repro_autocrop_frame | colour__lstd | chroma | 1 | 1.005 | 1.025 | 0 | 0 |
| repro_autocrop_frame | colour__lstd | hue | 1 | 1.037 | 1.414 | 0 | 0 |
| repro_autocrop_frame | colour__rank | palette_hist | 1 | 1 | 1 | 0 | 0 |
| repro_autocrop_frame | colour__rank | palette_sw | 0.2528 | 0.2589 | 0.2659 | 0 | 0 |
| repro_autocrop_frame | colour__rank | palette_kmeans | 1.271 | 1.501 | 1.775 | 0 | 0 |
| repro_autocrop_frame | colour__rank | lightness | 1.577 | 1.577 | 1.577 | 0 | 0 |
| repro_autocrop_frame | colour__rank | chroma | 1 | 1.024 | 1.041 | 0 | 0 |
| repro_autocrop_frame | colour__rank | hue | 1 | 1.002 | 1.414 | 0 | 0 |
| repro_autocrop_frame | colour__raw | palette_hist | 1 | 1 | 1 | 0 | 0 |
| repro_autocrop_frame | colour__raw | palette_sw | 0.07323 | 0.2097 | 0.3782 | 0 | 0 |
| repro_autocrop_frame | colour__raw | palette_kmeans | 0.8759 | 1.381 | 2.003 | 0 | 0 |
| repro_autocrop_frame | colour__raw | lightness | 1.067 | 1.429 | 1.955 | 0 | 0 |
| repro_autocrop_frame | colour__raw | chroma | 1 | 1.005 | 1.025 | 0 | 0 |
| repro_autocrop_frame | colour__raw | hue | 1 | 1.037 | 1.414 | 0 | 0 |
| repro_autocrop_frame | colour__std | palette_hist | 1 | 1 | 1 | 0 | 0 |
| repro_autocrop_frame | colour__std | palette_sw | 0.2264 | 0.2424 | 0.2491 | 0 | 0 |
| repro_autocrop_frame | colour__std | palette_kmeans | 1.123 | 1.498 | 2.039 | 0 | 0 |
| repro_autocrop_frame | colour__std | lightness | 1.414 | 1.512 | 1.612 | 0 | 0 |
| repro_autocrop_frame | colour__std | chroma | 1 | 1.024 | 1.041 | 0 | 0 |
| repro_autocrop_frame | colour__std | hue | 1 | 1.002 | 1.414 | 0 | 0 |
| repro_autocrop_frame | composition | grid8_an | 3.442 | 8.864 | 13.25 | 0 | 0 |
| repro_autocrop_frame | composition | grid8_ap | 1.721 | 7.143 | 10.79 | 0 | 0 |
| repro_autocrop_frame | composition | grid4_an | 1.081 | 3.474 | 6.014 | 0 | 0 |
| repro_autocrop_frame | composition | grid4_ap | 0.4664 | 2.598 | 4.505 | 0 | 0 |
| repro_autocrop_frame | composition | symmetry | 0.2013 | 0.8069 | 2.305 | 0 | 0 |
| repro_autocrop_frame | composition | balance | 1.144 | 1.381 | 1.527 | 0 | 0 |
| repro_autocrop_frame | composition | edges | 1.541 | 1.734 | 1.942 | 0 | 0 |
| repro_autocrop_frame | composition | spectrum | 7.942 | 10.17 | 11.27 | 0 | 0 |
| repro_autocrop_frame | composition | saliency | 1.287 | 1.388 | 1.416 | 0 | 0 |
| repro_autocrop_frame | composition | aspect | 0 | 0.2843 | 1.164 | 7 | 0 |
| repro_autocrop_frame | dinov2_b__pad | cls | 21.5 | 24.33 | 26.59 | 0 | 0 |
| repro_autocrop_frame | dinov2_b__pad | patch_mean | 11.73 | 14.22 | 18.32 | 0 | 0 |
| repro_autocrop_frame | dinov2_b__pad | meanstd_early | 2.668 | 3.089 | 3.719 | 0 | 0 |
| repro_autocrop_frame | dinov2_b__pad | gram_early | 0.7961 | 1.544 | 2.636 | 0 | 0 |
| repro_autocrop_frame | dinov2_b__pad | meanstd_mid | 5.156 | 5.532 | 5.939 | 0 | 0 |
| repro_autocrop_frame | dinov2_b__pad | gram_mid | 4.037 | 5.844 | 8.894 | 0 | 0 |
| repro_autocrop_frame | dinov2_b__pad | meanstd_late | 121.3 | 141.2 | 163.9 | 0 | 0 |
| repro_autocrop_frame | dinov2_b__pad | gram_late | 1532 | 2909 | 5534 | 0 | 0 |
| versions | clip_l__pad | embed | 15.22 | 18.04 | 20.41 | 0 | 0 |
| versions | clip_l__pad | backbone | 31.22 | 32.9 | 34.04 | 0 | 0 |
| versions | clip_l__tile | embed | 15.5 | 17.39 | 20.51 | 0 | 0 |
| versions | clip_l__tile | backbone | 29.98 | 32.57 | 33.78 | 0 | 0 |
| versions | colour__greyworld | palette_hist | 1 | 1 | 1 | 0 | 0 |
| versions | colour__greyworld | palette_sw | 0.09715 | 0.2038 | 0.3442 | 0 | 0 |
| versions | colour__greyworld | palette_kmeans | 0.8554 | 1.368 | 1.93 | 0 | 0 |
| versions | colour__greyworld | lightness | 1.126 | 1.424 | 1.852 | 0 | 0 |
| versions | colour__greyworld | chroma | 1 | 1.003 | 1.021 | 0 | 0 |
| versions | colour__greyworld | hue | 1 | 1.1 | 1.414 | 0 | 0 |
| versions | colour__lstd | palette_hist | 1 | 1 | 1 | 0 | 0 |
| versions | colour__lstd | palette_sw | 0.2222 | 0.2346 | 0.2436 | 0 | 0 |
| versions | colour__lstd | palette_kmeans | 1.124 | 1.511 | 1.832 | 0 | 0 |
| versions | colour__lstd | lightness | 1.443 | 1.525 | 1.614 | 0 | 0 |
| versions | colour__lstd | chroma | 1 | 1.005 | 1.035 | 0 | 0 |
| versions | colour__lstd | hue | 1 | 1.035 | 1.414 | 0 | 0 |
| versions | colour__rank | palette_hist | 1 | 1 | 1 | 0 | 0 |
| versions | colour__rank | palette_sw | 0.2535 | 0.2586 | 0.2652 | 0 | 0 |
| versions | colour__rank | palette_kmeans | 1.28 | 1.503 | 1.744 | 0 | 0 |
| versions | colour__rank | lightness | 1.577 | 1.577 | 1.577 | 0 | 0 |
| versions | colour__rank | chroma | 1 | 1.024 | 1.04 | 0 | 0 |
| versions | colour__rank | hue | 1 | 1.001 | 1.414 | 0 | 0 |
| versions | colour__raw | palette_hist | 1 | 1 | 1 | 0 | 0 |
| versions | colour__raw | palette_sw | 0.09616 | 0.2058 | 0.3459 | 0 | 0 |
| versions | colour__raw | palette_kmeans | 0.9346 | 1.391 | 1.963 | 0 | 0 |
| versions | colour__raw | lightness | 1.127 | 1.432 | 1.852 | 0 | 0 |
| versions | colour__raw | chroma | 1 | 1.005 | 1.035 | 0 | 0 |
| versions | colour__raw | hue | 1 | 1.035 | 1.414 | 0 | 0 |
| versions | colour__std | palette_hist | 1 | 1 | 1 | 0 | 0 |
| versions | colour__std | palette_sw | 0.2263 | 0.2424 | 0.2481 | 0 | 0 |
| versions | colour__std | palette_kmeans | 1.151 | 1.522 | 1.945 | 0 | 0 |
| versions | colour__std | lightness | 1.443 | 1.525 | 1.614 | 0 | 0 |
| versions | colour__std | chroma | 1 | 1.024 | 1.04 | 0 | 0 |
| versions | colour__std | hue | 1 | 1.001 | 1.414 | 0 | 0 |
| versions | composition | grid8_an | 5.408 | 8.768 | 11.76 | 0 | 0 |
| versions | composition | grid8_ap | 3.868 | 7.137 | 10.36 | 0 | 0 |
| versions | composition | grid4_an | 1.751 | 3.386 | 5.209 | 0 | 0 |
| versions | composition | grid4_ap | 1.237 | 2.589 | 4.126 | 0 | 0 |
| versions | composition | symmetry | 0.1991 | 0.81 | 2.073 | 0 | 0 |
| versions | composition | balance | 1.197 | 1.373 | 1.598 | 0 | 0 |
| versions | composition | edges | 1.637 | 1.742 | 1.869 | 0 | 0 |
| versions | composition | spectrum | 7.347 | 10.1 | 11.07 | 0 | 0 |
| versions | composition | saliency | 1.305 | 1.39 | 1.414 | 0 | 0 |
| versions | composition | aspect | 0 | 0.2764 | 0.8558 | 2 | 0 |
| versions | csd_l__pad | style | 0.9996 | 1 | 1 | 0 | 0 |
| versions | csd_l__pad | content | 0.9996 | 1 | 1 | 0 | 0 |
| versions | csd_l__pad | backbone | 31.26 | 32.57 | 33.63 | 0 | 0 |
| versions | csd_l__tile | style | 0.9292 | 0.9912 | 1 | 0 | 0 |
| versions | csd_l__tile | content | 0.9652 | 0.9952 | 1 | 0 | 0 |
| versions | csd_l__tile | backbone | 31.04 | 32.48 | 33.37 | 0 | 0 |
| versions | dinov2_b__center | cls | 21.99 | 24.69 | 26.68 | 0 | 0 |
| versions | dinov2_b__center | patch_mean | 11.63 | 14.41 | 19.21 | 0 | 0 |
| versions | dinov2_b__center | meanstd_early | 2.55 | 3.027 | 3.51 | 0 | 0 |
| versions | dinov2_b__center | gram_early | 0.6947 | 1.455 | 2.445 | 0 | 0 |
| versions | dinov2_b__center | meanstd_mid | 5.135 | 5.459 | 5.811 | 0 | 0 |
| versions | dinov2_b__center | gram_mid | 4.218 | 5.474 | 7.558 | 0 | 0 |
| versions | dinov2_b__center | meanstd_late | 120.6 | 142.1 | 157.4 | 0 | 0 |
| versions | dinov2_b__center | gram_late | 1573 | 2973 | 5262 | 0 | 0 |
| versions | dinov2_b__pad | cls | 21.76 | 24.63 | 26.32 | 0 | 0 |
| versions | dinov2_b__pad | patch_mean | 11.92 | 14.45 | 17.92 | 0 | 0 |
| versions | dinov2_b__pad | meanstd_early | 2.579 | 3.095 | 3.535 | 0 | 0 |
| versions | dinov2_b__pad | gram_early | 0.7125 | 1.531 | 2.65 | 0 | 0 |
| versions | dinov2_b__pad | meanstd_mid | 5.171 | 5.522 | 5.858 | 0 | 0 |
| versions | dinov2_b__pad | gram_mid | 4.164 | 5.686 | 8.559 | 0 | 0 |
| versions | dinov2_b__pad | meanstd_late | 120.3 | 141.7 | 157.6 | 0 | 0 |
| versions | dinov2_b__pad | gram_late | 1745 | 2972 | 5168 | 0 | 0 |
| versions | dinov2_b__tile | cls | 20.38 | 24.05 | 26.12 | 0 | 0 |
| versions | dinov2_b__tile | patch_mean | 11.62 | 14.11 | 17.69 | 0 | 0 |
| versions | dinov2_b__tile | meanstd_early | 2.55 | 3.02 | 3.488 | 0 | 0 |
| versions | dinov2_b__tile | gram_early | 0.6937 | 1.428 | 2.35 | 0 | 0 |
| versions | dinov2_b__tile | meanstd_mid | 5.169 | 5.463 | 5.807 | 0 | 0 |
| versions | dinov2_b__tile | gram_mid | 4.168 | 5.41 | 7.263 | 0 | 0 |
| versions | dinov2_b__tile | meanstd_late | 120.1 | 141.8 | 157.5 | 0 | 0 |
| versions | dinov2_b__tile | gram_late | 1775 | 2939 | 5106 | 0 | 0 |
| versions | dinov2_l__pad | cls | 19.78 | 23 | 24.22 | 0 | 0 |
| versions | dinov2_l__pad | patch_mean | 9.763 | 11.39 | 13.49 | 0 | 0 |
| versions | dinov2_l__pad | meanstd_early | 4.329 | 5.406 | 6.285 | 0 | 0 |
| versions | dinov2_l__pad | gram_early | 2.79 | 5.638 | 9.097 | 0 | 0 |
| versions | dinov2_l__pad | meanstd_mid | 11.16 | 11.99 | 12.75 | 0 | 0 |
| versions | dinov2_l__pad | gram_mid | 24.75 | 32.47 | 41.93 | 0 | 0 |
| versions | dinov2_l__pad | meanstd_late | 233 | 269.4 | 294.4 | 0 | 0 |
| versions | dinov2_l__pad | gram_late | 7994 | 1.228e+04 | 2.014e+04 | 0 | 0 |
| versions | dinov2_l__tile | cls | 19.12 | 22.5 | 24.19 | 0 | 0 |
| versions | dinov2_l__tile | patch_mean | 9.172 | 11.09 | 13.33 | 0 | 0 |
| versions | dinov2_l__tile | meanstd_early | 4.29 | 5.262 | 6.229 | 0 | 0 |
| versions | dinov2_l__tile | gram_early | 2.646 | 5.098 | 8.22 | 0 | 0 |
| versions | dinov2_l__tile | meanstd_mid | 11.13 | 11.83 | 12.55 | 0 | 0 |
| versions | dinov2_l__tile | gram_mid | 24.6 | 31.01 | 39.06 | 0 | 0 |
| versions | dinov2_l__tile | meanstd_late | 232.5 | 268.2 | 290.9 | 0 | 0 |
| versions | dinov2_l__tile | gram_late | 8010 | 1.198e+04 | 1.963e+04 | 0 | 0 |
| versions | siglip2_b__center | embed | 7.893 | 10.88 | 14.36 | 0 | 0 |
| versions | siglip2_b__center | patch_mean | 24.64 | 30.39 | 34.73 | 0 | 0 |
| versions | siglip2_b__pad | embed | 8.3 | 10.86 | 13.48 | 0 | 0 |
| versions | siglip2_b__pad | patch_mean | 24.5 | 30.65 | 34.92 | 0 | 0 |
| versions | siglip2_b__tile | embed | 7.854 | 10.64 | 13.42 | 0 | 0 |
| versions | siglip2_b__tile | patch_mean | 24.37 | 29.84 | 33.94 | 0 | 0 |

