# Describer blocks: can Subject and Form be built from the describer's fixed fields?

Run 8 to 9 October 2026 as a follow-up to `exp_separation` (a learned manner block was not there to be had) and `describer` (the describer's fixed fields repeat almost exactly). Nothing here is committed. Stimuli and contact sheets are in `data/painting2vec/exp_describer_blocks/` (gitignored).

The describer is Claude (Opus 5.5), run as 30 subagents that each viewed 11 or 12 anonymised image files and wrote one JSON file. No model was run locally; the comparison blocks are read from `data/painting2vec/features/`. This file is the prose followed by `tables.md` as printed by `04_analyse.py`.

## The answer

**Yes for manner, yes with a reservation for subject, no for colour.**

- **The two describer blocks give different lists.** Describer-subject and describer-manner share 1.1 of a painting's 10 nearest among the 300 (chance 0.33). Each shares about 2 of 10 with the picture embedding (2.2 and 1.6). Distances in the two blocks correlate at 0.14 over all pairs (T2).
- **Describer-manner is the first candidate that behaves as a manner block.** Its neighbours are only a little nearer in subject than random paintings are (subject distance to its top 10 is 0.88 of the average, against 0.77 for the picture embedding's neighbours, T3), and by eye the rows hold one handling across subjects, centuries and traditions: Rousseau next to Jakuchū, a Mughal procession and an Upper Rhenish garden; a Caravaggio next to Courbet, Goya, Rubens and Rembrandt.
- **It is also a painter model, as strong as CSD, and it is much less of a calendar.** 13 per cent of its neighbours are by the same painter (CSD 14, picture 7, chance 1.4) and it separates a painter's works from everyone else's with AUC 0.87, the highest of any block here (CSD 0.80, picture 0.75), and 0.85 when the candidates are in a different genre from the query. A linear probe reads the year from it with R² 0.26 on the European paintings, against 0.66 for CSD and 0.32 for the picture embedding (T3). A painter's handling is consistent, so a manner block that works has to find painters. What cannot be settled here is whether the describer marked what it saw or what it knows the painter does: it recognised 229 of the 230 European paintings (T8).
- **Describer-subject crosses handling and period more than the picture embedding does, and groups less well by eye.** Its neighbours are a median 131 years from the seed (picture 102, random 167) and 5 per cent are by the same painter (picture 7). It finds the other version of a composition first in 88 per cent of cases whether the same hand or another painted it (T4). But it matches on shared items and misses the gist: a boy peeling fruit gets fruit pictures and figure pictures, where the embedding gets half-length figures looking down at their hands. Same-genre share in the top 10 is 0.32 against 0.44 for the embedding (chance 0.14).
- **Describer colour does not survive a second photograph.** On 30 pairs of photographs with visibly different colour, the second photograph is the nearest neighbour for 35 per cent under describer-colour and 28 per cent under pixel colour on the same pool; 39 and 26 per cent of the top 10 is kept. Subject is at 92 and 87 per cent, manner at 75 and 69, the picture embedding at 98 and 82 (T7). Telling the describer to judge the painting and not the photograph did not help.
- **The embedding and the describer hold different information.** A linear readout of the picture embedding recovers a quarter to a third of the variance of the describer's marks (subject 0.23, manner 0.36, colour 0.10); the describer's 152 columns recover 37 per cent of the embedding's first 64 components (T5). Two describers agree at 0.9 or better on these marks, so the unrecovered part is not noise. With 300 paintings the readouts are short of data and these are floors.
- **Granularity is fine at 300 and is the limit at 10,000.** Only 12 of the 300 share a subject vector with another painting and 4 share a manner vector (T6). But the tenth neighbour is 8 or 9 marks away now and would be about 2 marks away in a library of 10,000, and two describers already differ by 0.9 marks on the subject of one photograph and by 2.9 on the manner of two photographs. At that size the order of the top ten would be describer noise.

## Recommendation

1. **Form lens: build the manner block from describer fields.** Use the 13 rendering scales and 7 depth cues of instrument v2, z-scored. Do not use the five v1 scales alone: 208 of the 300 paintings share a five-scale vector with another (largest group 15), and they fail the photograph test (R@1 0.28). Before the 2,500 library, either mark every painting twice and average, or add scales until the tenth neighbour is clear of the 2.9-mark noise; about twice the present number of independent scales is the order needed for 10,000.
2. **Subject lens: put describer-subject beside the picture embedding, not in place of it.** The embedding is better at the gist, at versions (top-1 1.00) and at the same painting photographed twice. Describer-subject adds reach across handling, period and tradition, is readable, and is the tags route for works with no hostable image. A Subject lens made of both at equal block variance is the thing to try by eye next. The checklist needs fields for what the figures are doing and how they are placed (pose, gaze, relation between figures, scale of figure in frame) before it can stand alone.
3. **Colour: do not build the colour block from describer fields.** Keep value key, colour temperature and contrast (agreement 0.70 to 0.80 across photographs) as facets or filters. For a ranked colour list the problem is still the photograph, and neither route solves it.
4. **How the blocks combine: extra blocks beside the picture embedding.** Not a replacement: the describer predicts about a third of the embedding and is worse on every retrieval check. Not only a re-ranker: the manner neighbours are not in the embedding's shortlist to be re-ranked (1.6 of 10 shared). The embedding is the fine-grained block and breaks the ties the coarse blocks leave; inside the Form lens, where the embedding would bring subject back in, ties fall to pixel composition and to whatever colour block survives.
5. **Felt** was kept apart as asked. It shares 1.1 of 10 with subject and with manner, and it is as photograph-stable as manner (0.75).

## What remains unproven

- **One model family is the describer and its own check.** Agreement between two samples of one model is self-consistency. No human judgement of subject, manner or similarity was used anywhere.
- **The describer recognises the paintings.** 263 of 300 in this run, 229 of 230 European. Manner marks may be partly recall of the painter's reputation, and stability across photographs may be partly recall of the painting. 36 of the 37 unrecognised paintings are non-European, so recognition and tradition cannot be pulled apart. A set the describer cannot know is the test.
- **n = 300, chosen to make the question answerable.** Twelve painters with 8 or more works, seven genres spread over periods, 26 version pairs. Painter and genre statistics are inflated against a random draw, and every block was fitted and scored on the same 300.
- **The added fields have no same-photograph retest.** Their only reliability figure is across two photographs (manner scales: exact agreement 0.78, mean difference 0.22 of a point).
- **Other-hand copies are not farther than same-hand versions under manner** (p = 0.39; partner in the top 10 for 100 and 88 per cent). Either copies reproduce the handling at this resolution, or the scales are too coarse to see the difference. Thirteen pairs each way cannot say which.
- **Batch anchoring.** Each describer saw 11 or 12 pictures and was told to use the whole range of each scale across the batch.
- **Blinding was by instruction**, as in the earlier study.
- **Scaling estimates come from the pair-distance distribution of this clustered sample** and lean pessimistic.

## Design as run

**Sample** (`01_sample.py`, seed 20261009, `sample.csv`). 300 pilot paintings. Excluded: the 28 handscroll strips and greyscale files listed in `exp_separation/results/setup.json`, files with mean channel spread under 8, aspect ratio outside 1:3 to 3:1, short side under 300 px.

| group | paintings |
|---|---|
| the original 60 of the describer study | 60 |
| pilot members of the 26 version pairs | 30 |
| paintings with a second photograph | 30 |
| 12 painters, 8 or more works each, spread over genres (van Gogh, Rembrandt, Goya, Manet, Rubens, Titian, Courbet, Velázquez, Brueghel, Dürer, Gauguin, Jakuchū) | 96 (some already in the groups above) |
| 7 genres, one painter each, non-European first then spread over six periods (portrait, landscape, still life, religious, interior, crowd, animal) | 94 |
| fill, least-represented non-European tradition first | 24 |

A painting can be in more than one group. 230 European and American, 70 other: 16 Japanese and 9 each Chinese, Korean, Persian and Ottoman, South Asian, other non-European, and tradition unknown.

**Version pairs** (`version_pairs_used.csv`). 26 pairs judged to share a composition, 13 by the same hand and 13 by another (6 with a named other painter, 7 anonymous copies). Six pairs have both paintings in the pilot; the other partner of the rest (22 paintings, `version_extras.csv`) was described from `data/painting2vec/versions/images` and is outside the 300.

**Photographs** (`photo_pairs_used.csv`). The 30 unflagged primary pairs of `repro_pairs.csv` with the largest `lab_diff` (9.4 to 11.9) that are not in the original 60. The first photograph is the pilot image; the second was described in a different batch.

**Stimuli and batches** (`02_stimuli.py`, `key.csv`). 352 images, each re-encoded from pixels only under a random seven-character name: 240 new pilot paintings, the original 60, 22 version partners, 30 second photographs. 30 batches of 11 or 12, one describer each, two at a time. Two photographs of one painting, or two versions of one composition, never share a batch.

**The original 60.** Their v1 marks (`orig` presentation of the earlier study) are the ones used for every v1 field, as instructed. They were shown again here because the added fields did not exist for them; the second pass also gives a check that the longer instrument does not move the old fields (T0). It does not: checklist kappa 0.95 between the v1 and v2 passes against 0.96 between two v1 passes, scales ICC 0.92 against 0.94, no scale mean moved by more than 0.13 of a point. The data pool.

**Failures.** 30 of 30 batches returned valid JSON at the first attempt and none was re-run. Three records gave `people` as `"3"` where the instrument asks for `"3-5"`; the validator maps an exact count to its bin and logs it (`normalised.csv`). After the first four batches one sentence was added to the describer prompt asking for the listed strings exactly; it happened once more.

## Instrument changes (v1 to v2)

`instrument_v2.md`. Nothing was removed or reworded except the two sentences about the `told` condition, which this run does not have. Added:

- **Eight manner scales, 0 to 4:** `edge_hardness`, `outline`, `stroke_direction`, `flat_colour`, `modelling`, `ornament`, `idealisation`, `distortion`.
- **`space.depth_cues`,** a checklist of seven: linear perspective, atmospheric perspective, overlap, size diminution, cast shadows, foreshortening, stacked space.
- **`colour`:** `hues` (checklist of 12 families covering a tenth of the surface or more), `main_hue`, `accent_hue`, `value_key` (high, mid, low), with an instruction to judge the painting's colours and ignore frame, mount and the tint of the photograph.

`overlap` was marked on 98 per cent of paintings and carries nothing. `contour` and `edge_hardness` are one scale (rho -0.87), and so are `finish` and `stroke_direction` (0.87). `abstraction`, `outline`, `flat_colour`, `distortion` and the absence of `modelling` move together (0.6 to 0.8). The 13 scales hold perhaps five independent directions (T1).

## Blocks

| block | built from | distance |
|---|---|---|
| subject | 46 checklist items, setting (9, one-hot), people and animals as four thresholds each: 63 binary marks | Jaccard; cosine on IDF-weighted marks (the one used in sheets and headline numbers); Euclidean on 12 principal components of the IDF-weighted marks |
| manner | abstraction, contour, finish, detail, depth and the 8 added scales, z-scored; 7 depth cues z-scored and scaled to the variance of two scales | Euclidean |
| colour | palette breadth, saturation, colour temperature, darkness, contrast, value key, z-scored; hue checklist (variance of 4 scales), main hue (2), accent hue (1) | Euclidean |
| composition | crowding, symmetry, closeness, z-scored (three marks; reported for completeness) | Euclidean |
| felt | 24 words, 0 to 3 | Euclidean |
| picture | DINOv2-L `cls`, `tile`, L2 and centred on the pilot | cosine |
| CSD style | `style`, `tile`, PCA-64 whitened on the pilot | cosine |
| pixel composition | `grid8_an`, PCA-128 whitened | cosine |
| pixel colour | `std` `palette_hist` + `palette_sw`, PCA-64 whitened | cosine |

`depth` (flat pattern against deep modelled space) is in manner here; the framework lists it under composition. Every statistic is fitted on the 300; version partners and second photographs are transformed with that fit.

Of the three subject variants, Jaccard and IDF cosine behave alike (5.5 of 10 neighbours shared) and PCA-12 is worse on versions and photographs. IDF cosine keeps most of a top-10 list across two photographs (87 per cent against 74 for Jaccard).

## What the sheets showed

`05_sheets.py`; 12 seeds drawn by rule (`seeds.csv`), seed and its 8 nearest among the 300, no names. I looked at subject, manner, colour, picture and pixel composition.

**Describer-subject.** Good where the subject is a common type. The mountain landscape (Bierstadt) gets Brueghel's snow scenes, an American naive view, an East Asian landscape and two dark seventeenth-century ones: one subject across four centuries and two traditions. A Rembrandt half-length gets single-figure portraits from Dürer to Goya and a Japanese court portrait. Chardin's still life gets kitchen and fruit pieces from Aertsen to Cézanne and Gauguin. Poor where the subject is a combination. The boy peeling fruit splits into fruit still lifes and figures. Piero's Baptism gets a swan, a lake, a Goya game and the Déjeuner sur l'herbe: trees, water, a bird, figures outdoors. A flower still life gets furnished interiors. The checklist says what is present and not what the picture is of.

**Describer-manner.** Most rows read as one handling. Rousseau's tiger: ink plum blossom, Jakuchū twice, an East Asian landscape, the Upper Rhenish paradise garden, a gold screen, an Indian procession; flat, outlined, patterned, stacked. Jakuchū's rooster: Jakuchū, three Mughal leaves, the paradise garden. Alma-Tadema: Veronese, David's coronation, an orientalist interior, Titian, Raphael, Rigaud; finished, detailed, ornamented, idealised, 1500 to 1900. Bierstadt: Giorgione, Copley, Gérôme, a Mona Lisa copy; smooth deep space whatever the subject. Rembrandt, Chardin and Caravaggio seeds each get a mix of Courbet, Velázquez, Goya, Rubens and Rembrandt across nude, portrait, still life and landscape. Two rows are a period: van Gogh's roses get van Gogh, Gauguin and Cézanne only, and Piero gets mostly the Italian Renaissance (with Ingres and the Fontainebleau double portrait). One row shows the coarseness: a monochrome ink grapevine is put with Gauguin and Franz Marc, because all are summary, outlined and flat and the block has no colour in it.

**Describer-colour.** About half the rows hold: dark brown pictures with a light accent, high-key blue-green ones (Kuroda's lakeside, almond blossom, a Courbet sea, Whistler's white girl), pale ink and paper. The rest drift after three or four neighbours.

**Picture embedding.** The tightest groups: half-lengths looking down, panoramic landscapes, still lifes, multi-figure altarpieces, reclining women, hanging scrolls. It keeps format and tradition with the subject: the East Asian seeds get only East Asian hanging scrolls and the Jakuchū seed gets six more Jakuchū.

**Pixel composition.** Nothing I could name in any row at this pool size.

## Cost

Measured on the 30 runs (`usage.csv`): 2.94 million tokens as the harness reports them for 352 descriptions, 8,355 per description; 73.5 minutes of describer time, 12.5 seconds per description, half that on the clock with two running.

| | 300 (this run, 352 images) | 2,500 | 10,000 |
|---|---|---|---|
| subagents as run, tokens | 2.9 M | 21 M | 84 M |
| subagents as run, describer time (one stream) | 1.2 h | 8.7 h | 35 h |
| API, one image per call, estimate: input tokens | | 7.5 M (5 M of it the cached instrument) | 30 M (20 M cached) |
| API estimate: output tokens | | 2.4 M | 9.5 M |

The API rows are estimates, not measurements: about 1,000 tokens for a 0.74-megapixel image, about 2,000 for the instrument (identical every call, so cacheable), about 950 for the 2,370-character record. The subagent figure is three times that because each run carries the agent's own overhead. A production run would call the API with images at one fixed resolution, one painting per call so that no batch anchors another, and would drop the free-text and recognition fields from the output. Marking each painting twice, which the granularity result argues for, doubles every row. I did not look up prices.

## Files

| file | what |
|---|---|
| `01_sample.py`, `sample.csv`, `version_pairs_used.csv`, `version_extras.csv`, `photo_pairs_used.csv` | the sample |
| `02_stimuli.py`, `key.csv` | stimuli, batch plan, code-to-painting key |
| `instrument_v2.md`, `03_validate.py`, `normalised.csv`, `raw/batch_00.json` to `batch_29.json` | instrument, validator, raw describer output |
| `lib.py`, `04_analyse.py`, `tables.md`, `neighbours.json`, `cost.json`, `usage.csv` | blocks, analysis, tables, top-10 lists per block |
| `05_sheets.py`, `seeds.csv` | contact sheets (written to `data/painting2vec/exp_describer_blocks/sheets/`) |

```
RUN="uv run --no-project --with pillow --with numpy --with pandas --with scipy --with scikit-learn python"
$RUN experiments/painting2vec/exp_describer_blocks/04_analyse.py   # about 20 s
$RUN experiments/painting2vec/exp_describer_blocks/05_sheets.py
```

# Tables

paintings 300; version partners outside the pilot 22; second photographs 30; records analysed 352
subject vector: 63 binary marks (62 ever set); manner vector 20 columns (13 scales + 7 depth cues); colour vector 43 columns; felt 24

## T0. Pooling check: the original 60 under instrument v1 (earlier study, `orig`) against v2 (this run)

| field group | agreement | kappa or ICC | mean abs diff | earlier study, two v1 describers |
|---|---|---|---|---|
| checklist (46) | 0.98 | 0.95 | 0.02 | kappa 0.96, Jaccard 0.94 |
| checklist Jaccard per painting | 0.93 |  |  | 0.94 |
| people | 0.97 |  |  | 0.98 |
| animals | 0.98 |  |  | 0.98 |
| setting | 0.97 |  |  | 0.92 |
| 13 scales (0-4) | 0.83 | 0.92 | 0.17 | ICC median 0.94, MAD 0.13 |
| 24 felt words (0-3) | 0.84 | 0.89 | 0.16 | ICC median 0.92, MAD 0.15 |

| scale | v1 mean | v2 mean | v2 minus v1 | ICC | MAD |
|---|---|---|---|---|---|
| abstraction | 0.62 | 0.68 | 0.07 | 0.91 | 0.10 |
| contour | 1.08 | 1.08 | 0.00 | 0.92 | 0.17 |
| finish | 1.40 | 1.33 | -0.07 | 0.93 | 0.27 |
| detail | 2.67 | 2.60 | -0.07 | 0.92 | 0.13 |
| depth | 2.23 | 2.30 | 0.07 | 0.94 | 0.13 |
| palette_breadth | 2.02 | 2.15 | 0.13 | 0.91 | 0.27 |
| saturation | 1.88 | 1.90 | 0.02 | 0.92 | 0.18 |
| colour_temperature | 2.43 | 2.43 | 0.00 | 0.94 | 0.10 |
| darkness | 2.23 | 2.23 | 0.00 | 0.90 | 0.17 |
| contrast | 2.47 | 2.57 | 0.10 | 0.87 | 0.20 |
| crowding | 2.78 | 2.78 | 0.00 | 0.87 | 0.23 |
| symmetry | 1.28 | 1.22 | -0.07 | 0.87 | 0.23 |
| closeness | 1.98 | 1.97 | -0.02 | 0.98 | 0.05 |

## T1. The added fields: distribution over the 300

| scale | mean | sd | share at 0 | share at 1 | share at 2 | share at 3 | share at 4 |
|---|---|---|---|---|---|---|---|
| edge_hardness | 2.36 | 1.02 | 0.01 | 0.22 | 0.34 | 0.28 | 0.16 |
| outline | 0.99 | 1.27 | 0.53 | 0.18 | 0.10 | 0.14 | 0.05 |
| stroke_direction | 1.02 | 1.13 | 0.43 | 0.29 | 0.16 | 0.10 | 0.03 |
| flat_colour | 0.89 | 1.08 | 0.50 | 0.24 | 0.15 | 0.09 | 0.02 |
| modelling | 2.36 | 1.16 | 0.06 | 0.22 | 0.20 | 0.36 | 0.17 |
| ornament | 0.96 | 1.23 | 0.52 | 0.19 | 0.13 | 0.11 | 0.05 |
| idealisation | 1.98 | 1.30 | 0.16 | 0.25 | 0.15 | 0.31 | 0.12 |
| distortion | 0.90 | 0.99 | 0.46 | 0.26 | 0.20 | 0.08 | 0.00 |

depth cues, share marked: linear_perspective 0.19, atmospheric_perspective 0.40, overlap 0.98, size_diminution 0.51, cast_shadows 0.50, foreshortening 0.39, stacked_space 0.18

hue families, share marked: red 0.29, orange 0.16, yellow 0.23, green 0.44, blue 0.40, purple 0.03, pink 0.14, brown 0.85, gold 0.04, black 0.54, white 0.57, grey 0.50

main hue: brown 122, black 39, green 34, blue 25, grey 25, white 23, red 18, gold 6, yellow 3, orange 2, pink 2, purple 1; accent hue: red 135, none 30, orange 28, blue 27, yellow 21, white 20, green 20, pink 11, purple 4, gold 3, black 1; value key: mid 166, low 97, high 37

Spearman correlation between the manner scales (300 paintings)

|  | abstraction | contour | finish | detail | depth | edge_hardness | outline | stroke_direction | flat_colour | modelling | ornament | idealisation | distortion |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| abstraction | 1.00 | -0.09 | 0.31 | -0.22 | -0.49 | 0.10 | 0.69 | 0.34 | 0.74 | -0.80 | 0.17 | 0.27 | 0.71 |
| contour | -0.09 | 1.00 | 0.68 | -0.59 | 0.22 | -0.87 | -0.48 | 0.57 | -0.34 | 0.12 | -0.44 | -0.26 | -0.33 |
| finish | 0.31 | 0.68 | 1.00 | -0.64 | -0.09 | -0.65 | -0.05 | 0.87 | 0.05 | -0.23 | -0.28 | -0.30 | 0.02 |
| detail | -0.22 | -0.59 | -0.64 | 1.00 | 0.21 | 0.64 | 0.14 | -0.57 | -0.08 | 0.13 | 0.35 | 0.13 | 0.06 |
| depth | -0.49 | 0.22 | -0.09 | 0.21 | 1.00 | -0.16 | -0.48 | -0.16 | -0.56 | 0.48 | -0.38 | -0.17 | -0.41 |
| edge_hardness | 0.10 | -0.87 | -0.65 | 0.64 | -0.16 | 1.00 | 0.48 | -0.55 | 0.38 | -0.15 | 0.41 | 0.18 | 0.31 |
| outline | 0.69 | -0.48 | -0.05 | 0.14 | -0.48 | 0.48 | 1.00 | 0.01 | 0.75 | -0.65 | 0.37 | 0.30 | 0.75 |
| stroke_direction | 0.34 | 0.57 | 0.87 | -0.57 | -0.16 | -0.55 | 0.01 | 1.00 | 0.07 | -0.24 | -0.21 | -0.20 | 0.08 |
| flat_colour | 0.74 | -0.34 | 0.05 | -0.08 | -0.56 | 0.38 | 0.75 | 0.07 | 1.00 | -0.77 | 0.30 | 0.18 | 0.59 |
| modelling | -0.80 | 0.12 | -0.23 | 0.13 | 0.48 | -0.15 | -0.65 | -0.24 | -0.77 | 1.00 | -0.24 | -0.22 | -0.58 |
| ornament | 0.17 | -0.44 | -0.28 | 0.35 | -0.38 | 0.41 | 0.37 | -0.21 | 0.30 | -0.24 | 1.00 | 0.26 | 0.25 |
| idealisation | 0.27 | -0.26 | -0.30 | 0.13 | -0.17 | 0.18 | 0.30 | -0.20 | 0.18 | -0.22 | 0.26 | 1.00 | 0.37 |
| distortion | 0.71 | -0.33 | 0.02 | 0.06 | -0.41 | 0.31 | 0.75 | 0.08 | 0.59 | -0.58 | 0.25 | 0.37 | 1.00 |

## T2. Shared neighbours: mean number of paintings two blocks' top-10 lists have in common (of 10, among the 300)

|  | subject (Jaccard) | subject | subject (IDF, PCA-12) | manner | manner (v1 scales only) | colour | composition | felt | picture | CSD style | pixel composition | pixel colour | random 64-d |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| subject (Jaccard) | 10.0 | 5.5 | 4.3 | 1.3 | 0.9 | 0.7 | 0.8 | 1.1 | 2.3 | 1.9 | 0.6 | 0.7 | 0.4 |
| subject | 5.5 | 10.0 | 5.7 | 1.1 | 0.8 | 0.6 | 0.7 | 1.1 | 2.2 | 1.9 | 0.5 | 0.7 | 0.4 |
| subject (IDF, PCA-12) | 4.3 | 5.7 | 10.0 | 1.0 | 0.8 | 0.6 | 0.7 | 1.0 | 1.9 | 1.6 | 0.5 | 0.6 | 0.4 |
| manner | 1.3 | 1.1 | 1.0 | 10.0 | 4.2 | 0.8 | 0.8 | 1.1 | 1.6 | 1.9 | 0.5 | 0.7 | 0.3 |
| manner (v1 scales only) | 0.9 | 0.8 | 0.8 | 4.2 | 10.0 | 0.6 | 0.8 | 0.8 | 1.2 | 1.4 | 0.5 | 0.6 | 0.3 |
| colour | 0.7 | 0.6 | 0.6 | 0.8 | 0.6 | 10.0 | 0.4 | 0.7 | 0.8 | 1.2 | 0.5 | 1.4 | 0.3 |
| composition | 0.8 | 0.7 | 0.7 | 0.8 | 0.8 | 0.4 | 10.0 | 0.6 | 0.9 | 0.8 | 0.5 | 0.5 | 0.3 |
| felt | 1.1 | 1.1 | 1.0 | 1.1 | 0.8 | 0.7 | 0.6 | 10.0 | 1.4 | 1.4 | 0.5 | 0.6 | 0.4 |
| picture | 2.3 | 2.2 | 1.9 | 1.6 | 1.2 | 0.8 | 0.9 | 1.4 | 10.0 | 3.2 | 0.6 | 0.8 | 0.3 |
| CSD style | 1.9 | 1.9 | 1.6 | 1.9 | 1.4 | 1.2 | 0.8 | 1.4 | 3.2 | 10.0 | 0.7 | 1.2 | 0.4 |
| pixel composition | 0.6 | 0.5 | 0.5 | 0.5 | 0.5 | 0.5 | 0.5 | 0.5 | 0.6 | 0.7 | 10.0 | 0.6 | 0.3 |
| pixel colour | 0.7 | 0.7 | 0.6 | 0.7 | 0.6 | 1.4 | 0.5 | 0.6 | 0.8 | 1.2 | 0.6 | 10.0 | 0.3 |
| random 64-d | 0.4 | 0.4 | 0.4 | 0.3 | 0.3 | 0.3 | 0.3 | 0.4 | 0.3 | 0.4 | 0.3 | 0.3 | 10.0 |

chance: 0.33

Rank correlation between two blocks' distances over all pairs of the 300 (Spearman)

|  | subject | manner | colour | composition | felt | picture | CSD style |
|---|---|---|---|---|---|---|---|
| subject | 1.00 | 0.14 | 0.12 | 0.19 | 0.11 | 0.29 | 0.18 |
| manner | 0.14 | 1.00 | 0.26 | 0.14 | 0.06 | 0.27 | 0.14 |
| colour | 0.12 | 0.26 | 1.00 | 0.12 | 0.13 | 0.13 | 0.13 |
| composition | 0.19 | 0.14 | 0.12 | 1.00 | 0.08 | 0.15 | 0.08 |
| felt | 0.11 | 0.06 | 0.13 | 0.08 | 1.00 | 0.18 | 0.11 |
| picture | 0.29 | 0.27 | 0.13 | 0.15 | 0.18 | 1.00 | 0.24 |
| CSD style | 0.18 | 0.14 | 0.13 | 0.08 | 0.11 | 0.24 | 1.00 |

## T3. What the top-10 neighbours share (labels used only here)

| block | same painter | ÷ chance | median Δyear | ÷ random | same genre (P136) | same broad genre | other painter and 50+ years away | same tradition | painter AUC | … same broad genre | … different broad genre | in nobody's top 10 | max k-occurrence |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| subject (Jaccard) | 0.05 | 3.99 | 128.00 | 0.77 | 0.35 | 0.51 | 0.68 | 0.66 | 0.62 | 0.60 | 0.59 | 0.01 | 33 |
| subject (IDF cosine) | 0.05 | 3.55 | 131.00 | 0.78 | 0.32 | 0.47 | 0.69 | 0.63 | 0.61 | 0.59 | 0.59 | 0.00 | 26 |
| subject (IDF, PCA-12) | 0.05 | 3.42 | 122.00 | 0.73 | 0.30 | 0.45 | 0.67 | 0.63 | 0.63 | 0.60 | 0.62 | 0.01 | 32 |
| manner | 0.13 | 9.66 | 77.00 | 0.46 | 0.24 | 0.40 | 0.56 | 0.71 | 0.87 | 0.87 | 0.85 | 0.01 | 27 |
| manner (v1 scales only) | 0.09 | 6.89 | 103.00 | 0.62 | 0.22 | 0.38 | 0.64 | 0.68 | 0.81 | 0.79 | 0.78 | 0.00 | 25 |
| colour | 0.04 | 2.66 | 144.00 | 0.86 | 0.18 | 0.32 | 0.72 | 0.66 | 0.65 | 0.62 | 0.64 | 0.01 | 37 |
| composition (3 scales) | 0.03 | 1.93 | 148.00 | 0.89 | 0.20 | 0.36 | 0.73 | 0.62 | 0.60 | 0.57 | 0.59 | 0.01 | 21 |
| felt | 0.06 | 4.29 | 145.00 | 0.87 | 0.28 | 0.42 | 0.71 | 0.62 | 0.63 | 0.65 | 0.65 | 0.00 | 25 |
| picture (DINOv2-L cls) | 0.07 | 5.40 | 102.00 | 0.61 | 0.44 | 0.62 | 0.63 | 0.73 | 0.75 | 0.71 | 0.75 | 0.01 | 36 |
| CSD style | 0.14 | 10.20 | 72.00 | 0.43 | 0.34 | 0.48 | 0.56 | 0.73 | 0.80 | 0.79 | 0.80 | 0.00 | 19 |
| pixel composition (grid8_an) | 0.02 | 1.52 | 159.00 | 0.95 | 0.16 | 0.30 | 0.75 | 0.61 | 0.52 | 0.46 | 0.53 | 0.00 | 21 |
| pixel colour (std hist+sw) | 0.04 | 2.98 | 133.00 | 0.80 | 0.18 | 0.32 | 0.69 | 0.65 | 0.60 | 0.56 | 0.61 | 0.00 | 23 |
| random 64-d | 0.02 | 1.25 | 175.00 | 1.05 | 0.15 | 0.27 | 0.77 | 0.60 | 0.48 | 0.48 | 0.48 | 0.00 | 23 |

chance: same painter 0.014 (273 paintings with a painter); same genre 0.14; same broad genre 0.26; random pair median year gap 167; painter AUC over the 12 painters with 8 or more works here (110 paintings), chance 0.5. Earlier figures on the 1,972: CSD style same painter 0.248 (23 x chance), median Δyear 28 (0.16 of random); DINOv2-L cls 0.121, 62 (0.36).

Painter AUC by painter (the 12 painters with 8 or more works among the 300)

| painter | works | subject | manner | manner (v1 scales only) | colour | picture | CSD style |
|---|---|---|---|---|---|---|---|
| Vincent van Gogh | 11 | 0.50 | 0.93 | 0.91 | 0.46 | 0.82 | 0.86 |
| Rembrandt | 10 | 0.48 | 0.84 | 0.76 | 0.92 | 0.63 | 0.87 |
| Diego Velázquez | 10 | 0.62 | 0.79 | 0.70 | 0.67 | 0.68 | 0.62 |
| Édouard Manet | 10 | 0.56 | 0.90 | 0.83 | 0.55 | 0.81 | 0.75 |
| Pieter Brueghel the Elder | 10 | 0.82 | 0.96 | 0.85 | 0.68 | 0.85 | 0.88 |
| Francisco Goya | 9 | 0.51 | 0.73 | 0.66 | 0.65 | 0.63 | 0.73 |
| Titian | 9 | 0.64 | 0.91 | 0.86 | 0.81 | 0.83 | 0.83 |
| Paul Gauguin | 9 | 0.56 | 0.87 | 0.90 | 0.59 | 0.86 | 0.96 |
| Gustave Courbet | 8 | 0.55 | 0.85 | 0.76 | 0.48 | 0.59 | 0.61 |
| Albrecht Dürer | 8 | 0.63 | 0.87 | 0.82 | 0.57 | 0.69 | 0.75 |
| Peter Paul Rubens | 8 | 0.66 | 0.83 | 0.71 | 0.68 | 0.68 | 0.76 |
| Itō Jakuchū | 8 | 0.89 | 0.98 | 0.96 | 0.77 | 0.98 | 0.99 |

Linear probes on the 300 (ridge, 5-fold, folds grouped by painter): year of the painting, R2

| block | columns | year R2, all 296 dated | year R2, European 230 |
|---|---|---|---|
| subject marks | 62 | 0.14 | 0.14 |
| manner | 20 | 0.18 | 0.26 |
| manner (v1 scales only) | 5 | 0.12 | 0.23 |
| colour | 43 | 0.02 | 0.05 |
| composition (3 scales) | 3 | -0.05 | -0.03 |
| felt | 24 | 0.06 | -0.01 |
| picture (DINOv2-L cls, PCA-64) | 64 | 0.26 | 0.32 |
| CSD style (PCA-64) | 64 | 0.48 | 0.66 |
| random 64-d | 64 | -0.04 | -0.03 |

Cross-reading: how far apart are a block's neighbours in the other describer blocks (mean distance to the top-10 ÷ mean distance to all; 1.0 = no relation)

| neighbours taken from | in subject | in manner | in colour | in composition | in felt |
|---|---|---|---|---|---|
| subject (IDF cosine) | 0.47 | 0.90 | 0.94 | 0.85 | 0.87 |
| manner | 0.88 | 0.48 | 0.90 | 0.82 | 0.90 |
| colour | 0.95 | 0.89 | 0.58 | 0.93 | 0.95 |
| felt | 0.89 | 0.89 | 0.92 | 0.87 | 0.51 |
| picture (DINOv2-L cls) | 0.77 | 0.80 | 0.91 | 0.80 | 0.84 |
| CSD style | 0.81 | 0.77 | 0.87 | 0.85 | 0.86 |
| pixel composition (grid8_an) | 0.97 | 0.96 | 0.95 | 0.94 | 0.97 |
| random 64-d | 1.00 | 1.00 | 0.99 | 1.00 | 1.00 |

## T4. Version pairs (same composition): where the partner falls

| block | same hand: top-1 | same hand: top-10 | same hand: median rank | same hand: d ÷ nearest other | other hand: top-1 | other hand: top-10 | other hand: median rank | other hand: d ÷ nearest other | partner percentile, same | partner percentile, other | p (other farther) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| subject (Jaccard) | 0.96 | 1.00 | 1.00 | 0.26 | 0.88 | 1.00 | 1.00 | 0.36 | 0.00 | 0.00 | 0.27 |
| subject (IDF cosine) | 0.88 | 0.92 | 1.00 | 0.24 | 0.88 | 1.00 | 1.00 | 0.25 | 0.00 | 0.00 | 0.56 |
| subject (IDF, PCA-12) | 0.77 | 0.88 | 1.00 | 0.47 | 0.77 | 0.96 | 1.00 | 0.35 | 0.00 | 0.00 | 0.60 |
| manner | 0.42 | 1.00 | 2.00 | 1.03 | 0.46 | 0.88 | 2.00 | 1.00 | 0.01 | 0.00 | 0.39 |
| manner (v1 scales only) | 0.27 | 0.69 | 5.00 | 1.00 | 0.12 | 0.46 | 11.00 | 35231455.35 | 0.02 | 0.05 | 0.03 |
| colour | 0.23 | 0.65 | 4.50 | 1.17 | 0.31 | 0.65 | 3.00 | 1.26 | 0.02 | 0.01 | 0.64 |
| composition (3 scales) | 0.08 | 0.46 | 15.00 | 1.00 | 0.12 | 0.31 | 37.50 | inf | 0.04 | 0.14 | 0.08 |
| felt | 0.77 | 0.96 | 1.00 | 0.72 | 0.62 | 0.85 | 1.00 | 0.97 | 0.00 | 0.00 | 0.09 |
| picture (DINOv2-L cls) | 1.00 | 1.00 | 1.00 | 0.38 | 1.00 | 1.00 | 1.00 | 0.28 | 0.00 | 0.00 | 1.00 |
| CSD style | 1.00 | 1.00 | 1.00 | 0.51 | 1.00 | 1.00 | 1.00 | 0.54 | 0.00 | 0.00 | 1.00 |
| pixel composition (grid8_an) | 0.92 | 0.92 | 1.00 | 0.63 | 0.92 | 1.00 | 1.00 | 0.46 | 0.00 | 0.00 | 0.54 |
| pixel colour (std hist+sw) | 0.08 | 0.69 | 5.00 | 1.39 | 0.12 | 0.50 | 9.00 | 1.84 | 0.01 | 0.02 | 0.41 |
| random 64-d | 0.00 | 0.12 | 207.50 | 1.58 | 0.00 | 0.00 | 171.50 | 1.54 | 0.70 | 0.57 | 0.73 |

13 same-hand and 13 other-hand pairs, both directions; the pool is the other 299 paintings plus the partner. Rank 1 = the partner is the nearest painting. "d ÷ nearest other" under 1 means the partner is nearer than every other painting. Partner percentile = share of the pool nearer than the partner (median over pairs); p is a one-sided Mann-Whitney test that other-hand partners are farther.

## T5. Linear prediction between the describer's marks and the picture embedding (ridge, 5-fold, folds grouped by painter)

| block | R2 from picture (DINOv2 PCA-64), mean | R2 from picture (DINOv2 PCA-64), median | R2 from pixel colour + composition, mean | R2 from pixel colour + composition, median |
|---|---|---|---|---|
| subject | 0.23 | 0.24 | 0.01 | -0.01 |
| manner | 0.36 | 0.34 | 0.05 | 0.06 |
| colour | 0.10 | 0.03 | 0.19 | 0.22 |
| composition | 0.41 | 0.42 | 0.03 | 0.06 |
| felt | 0.23 | 0.24 | -0.00 | 0.00 |

Per field, manner and colour:

| block | field | R2 from picture (DINOv2 PCA-64) | R2 from pixel colour + composition |
|---|---|---|---|
| manner | abstraction | 0.40 | 0.12 |
| manner | contour | 0.29 | 0.00 |
| manner | finish | 0.30 | -0.01 |
| manner | detail | 0.31 | 0.03 |
| manner | depth | 0.56 | 0.11 |
| manner | edge_hardness | 0.33 | 0.00 |
| manner | outline | 0.49 | 0.10 |
| manner | stroke_direction | 0.33 | -0.00 |
| manner | flat_colour | 0.52 | 0.08 |
| manner | modelling | 0.58 | 0.21 |
| manner | ornament | 0.48 | 0.08 |
| manner | idealisation | 0.32 | -0.07 |
| manner | distortion | 0.38 | 0.07 |
| manner | cue:linear_perspective | 0.18 | 0.04 |
| manner | cue:atmospheric_perspective | 0.47 | 0.18 |
| manner | cue:overlap | -0.09 | -0.10 |
| manner | cue:size_diminution | 0.38 | 0.08 |
| manner | cue:cast_shadows | 0.26 | 0.06 |
| manner | cue:foreshortening | 0.31 | 0.06 |
| manner | cue:stacked_space | 0.34 | 0.04 |
| colour | palette_breadth | 0.33 | 0.38 |
| colour | saturation | 0.36 | 0.34 |
| colour | colour_temperature | 0.12 | 0.27 |
| colour | darkness | 0.38 | 0.44 |
| colour | contrast | 0.39 | 0.33 |
| colour | hue:red | 0.03 | 0.25 |
| colour | hue:orange | -0.11 | 0.01 |
| colour | hue:yellow | -0.05 | 0.09 |
| colour | hue:green | 0.10 | 0.22 |
| colour | hue:blue | -0.01 | 0.25 |
| colour | hue:pink | -0.10 | 0.02 |
| colour | hue:brown | -0.06 | -0.04 |
| colour | hue:black | 0.15 | 0.17 |
| colour | hue:white | 0.02 | 0.10 |
| colour | hue:grey | -0.10 | 0.08 |
| composition | crowding | 0.42 | 0.14 |
| composition | symmetry | 0.14 | -0.11 |
| composition | closeness | 0.67 | 0.06 |

Per field, subject (items marked on 15 or more of the 300) and felt: best and worst predicted from the picture embedding

subject: people (0-4) 0.62, animals (0-4) 0.47, nude 0.47, setting=landscape 0.46, horse 0.45, man 0.44, setting=interior 0.42, boat_or_ship 0.41, rocks 0.40, mountains_or_hills 0.39, trees 0.39, buildings 0.39, furniture 0.38, crowd 0.37, sky 0.36, soldier_or_armour 0.36, water 0.33, woman 0.32, bird 0.31, field_or_grass 0.31, wings 0.26, vessel_or_tableware 0.26, curtain_or_drapery 0.26, weapon 0.26, road_or_path 0.24, flowers 0.24, clouds 0.23, halo 0.22, window_or_door 0.21, setting=plain_background 0.21, child 0.19, setting=townscape 0.19, musical_instrument 0.18, hat_or_headdress 0.17, cart_or_carriage 0.17, old_person 0.15, jewellery_or_crown 0.13, sun_or_moon 0.12, other_animal 0.07, fruit_or_food 0.06, flag_or_banner 0.06, cattle_or_sheep 0.06, dead_or_wounded_body 0.06, cross 0.04, book_or_paper -0.02, setting=mixed -0.02, dog -0.03, bridge -0.07, written_text -0.10, fire_or_smoke -0.20

felt: intimate 0.48, tense 0.44, energetic 0.41, alarming 0.39, sensual 0.39, awed 0.37, still 0.35, calm 0.33, dreamlike 0.31, oppressive 0.30, uneasy 0.28, mysterious 0.24, tender 0.24, solemn 0.23, festive 0.18, playful 0.13, joyful 0.13, lonely 0.11, eerie 0.11, warm 0.07, desolate 0.06, hopeful 0.02, cold 0.01, melancholy -0.06

The other way: how much of the picture embedding the describer's marks predict (variance-weighted R2 over the first k principal components of DINOv2-L cls, which hold the stated share of its variance)

| predictors | columns | first 4 PCs | first 16 PCs | first 64 PCs | PC1 | PC2 | PC3 |
|---|---|---|---|---|---|---|---|
| subject marks | 62 | 0.45 | 0.37 | 0.26 | 0.40 | 0.60 | 0.33 |
| manner | 20 | 0.35 | 0.26 | 0.17 | 0.41 | 0.33 | 0.15 |
| colour | 43 | 0.17 | 0.12 | 0.07 | 0.28 | 0.06 | 0.05 |
| felt | 24 | 0.39 | 0.27 | 0.17 | 0.45 | 0.39 | 0.33 |
| subject + manner | 82 | 0.61 | 0.50 | 0.35 | 0.62 | 0.65 | 0.46 |
| every describer field | 152 | 0.64 | 0.52 | 0.37 | 0.68 | 0.64 | 0.48 |
| pixel colour + composition (64-d) | 64 | 0.13 | 0.08 | 0.05 | 0.21 | 0.03 | 0.03 |

share of DINOv2-L cls variance (L2-normalised, pilot fit) in the first 4 / 16 / 64 components: 0.30 / 0.51 / 0.73

## T6. Granularity

pairs of paintings with identical subject vectors: Girl with a Pearl Earring (Johannes Vermeer) = Portrait of the Actress Antonia Zarate (Francisco Goya); Wanderer above the Sea of Fog (Caspar David Friedrich) = Jacob’s Dream (Jusepe de Ribera); Grapevine in the Wind (nan) = nan (Süleyman Seyyid); Portrait of the Infanta Maria Theresa of Spain (Diego Velázquez) = Girl with a Red Hat (Johannes Vermeer); Portrait of Maria Portinari (Hans Memling) = La velata (Raphael); Rose mallows and fowl (Itō Jakuchū) = Rooster and Hen with Hydrangeas (Itō Jakuchū)

|  | subject | manner (13 scales + 7 cues) | manner (5 v1 scales) | colour | felt | subject + manner + colour |
|---|---|---|---|---|---|---|
| columns | 63 | 20 | 5 | 43 | 24 | 126 |
| sum of field entropies (bits) | 39.3 | 30.8 | 9.62 | 27.8 | 34.2 | 97.9 |
| distinct vectors | 294 | 298 | 154 | 297 | 300 | 300 |
| paintings sharing a vector | 12 | 4 | 208 | 6 | 0 | 0 |
| largest identical group | 2 | 2 | 15 | 2 | 1 | 1 |
| pairs identical | 0.000134 | 4.46e-05 | 0.00905 | 6.69e-05 | 0 | 0 |
| pairs within 1 mark | 0.000624 | 0.000357 | 0.0454 | 0.000535 | 6.69e-05 | 0 |
| pairs within 2 marks | 0.00201 | 0.00125 | 0.124 | 0.00239 | 0.000223 | 0 |
| distinct distance values (pairs) | 3.93e+04 | 4.4e+04 | 1.18e+03 | 4.37e+04 | 118 | 4.4e+04 |
| paintings whose 1st and 2nd neighbour tie | 0.0233 | 0.01 | 0.64 | 0.0133 | 0.287 | 0.01 |
| mean paintings at or inside the 10th neighbour's distance | 10 | 10 | 12.7 | 10 | 11.4 | 10 |
| median NN distance ÷ median pair distance | 0.31 | 0.371 | 0 | 0.456 | 0.373 | 0.371 |
| expected identical twins per painting at 2500 | 0.334 | 0.111 | 22.6 | 0.167 | 0 | 0 |
| expected within 1 mark at 2500 | 1.56 | 0.892 | 113 | 1.34 | 0.167 | 0 |
| expected within 2 marks at 2500 | 5.01 | 3.12 | 309 | 5.96 | 0.557 | 0 |
| expected identical twins per painting at 10000 | 1.34 | 0.446 | 90.5 | 0.669 | 0 | 0 |
| expected within 1 mark at 10000 | 6.24 | 3.57 | 454 | 5.35 | 0.669 | 0 |
| expected within 2 marks at 10000 | 20.1 | 12.5 | 1.24e+03 | 23.9 | 2.23 | 0 |

"Within k marks" is the sum of absolute differences over the block's raw fields (a 0/1 item that differs is 1; a scale that differs by one step is 1; a different main or accent hue is 1). Expected counts at 2,500 and 10,000 scale the share of pairs in this sample, which over-represents clusters (12 painters, 7 genres, 26 version pairs), so they lean high. The combined row's distance columns are not meaningful and repeat manner's.

How many raw marks apart is the 10th neighbour, now and in a larger library, against how many marks two describers differ on one painting

| block | median marks to nearest neighbour (300) | to 10th neighbour (300) | to 10th neighbour at 2,500 (scaled) | to 10th neighbour at 10,000 (scaled) | two describers, same photograph (60) | two describers, two photographs (30) |
|---|---|---|---|---|---|---|
| subject (63 marks) | 5.0 | 9.0 | 3.0 | 2.0 | 0.9 | 1.5 |
| manner (13 scales + 7 cues) | 4.0 | 8.0 | 4.0 | 2.0 |  | 2.9 |
| colour (5 scales, 12 hues, key, main, accent) | 3.0 | 6.0 | 3.0 | 2.0 |  | 4.8 |
| felt (24 words) | 5.0 | 9.0 | 5.0 | 3.0 | 3.9 | 4.0 |

The scaled columns read the pair-distance distribution of this sample at the quantile 10 / (library size): the distance inside which a painting would find ten others if the larger library were drawn like this sample. Where that distance is at or below the describer-to-describer difference, the order of the top ten is set by describer noise.

subject: pair distance 0.1 / 1 / 5 / 50 per cent quantiles 0.144 / 0.337 / 0.506 / 0.852; nearest-neighbour distance median 0.264, 10th-neighbour median 0.470
manner: pair distance 0.1 / 1 / 5 / 50 per cent quantiles 1.392 / 2.117 / 2.824 / 5.169; nearest-neighbour distance median 1.916, 10th-neighbour median 2.852
colour: pair distance 0.1 / 1 / 5 / 50 per cent quantiles 1.625 / 2.378 / 3.007 / 4.818; nearest-neighbour distance median 2.196, 10th-neighbour median 2.990
felt: pair distance 0.1 / 1 / 5 / 50 per cent quantiles 1.732 / 2.646 / 3.464 / 6.000; nearest-neighbour distance median 2.236, 10th-neighbour median 3.464
picture: pair distance 0.1 / 1 / 5 / 50 per cent quantiles 0.283 / 0.516 / 0.692 / 1.025; nearest-neighbour distance median 0.462, 10th-neighbour median 0.668

## T7. Two photographs of one painting (30 pairs, lab_diff 9.4 to 11.9)

| block | R@1 (ties split) | R@1 strictly nearest | R@10 | d(A,B) ÷ d(A, nearest other): median | p90 | pairs with d(A,B) = 0 | pairs under one step | top-10 kept |
|---|---|---|---|---|---|---|---|---|
| subject (Jaccard) | 0.93 | 0.92 | 1.00 | 0.25 | 0.84 | 0.27 | 0.97 | 0.74 |
| subject (IDF cosine) | 0.92 | 0.90 | 1.00 | 0.23 | 0.91 | 0.27 | 1.00 | 0.87 |
| subject (IDF, PCA-12) | 0.83 | 0.82 | 1.00 | 0.43 | 1.21 | 0.17 | 0.93 | 0.89 |
| manner | 0.75 | 0.75 | 0.98 | 0.82 | 1.31 | 0.00 | 0.80 | 0.69 |
| manner (v1 scales only) | 0.28 | 0.15 | 0.82 | 1.00 |  | 0.37 | 0.00 | 0.63 |
| colour | 0.35 | 0.35 | 0.58 | 1.17 | 1.99 | 0.00 | 0.23 | 0.39 |
| composition (3 scales) | 0.11 | 0.00 | 0.70 | 1.00 |  | 0.57 | 0.00 | 0.54 |
| felt | 0.75 | 0.68 | 0.97 | 0.80 | 1.29 | 0.03 | 0.57 | 0.65 |
| picture (DINOv2-L cls) | 0.98 | 0.98 | 1.00 | 0.13 | 0.34 | 0.00 | 1.00 | 0.82 |
| CSD style | 0.90 | 0.90 | 0.93 | 0.47 | 0.97 | 0.00 | 0.93 | 0.49 |
| pixel composition (grid8_an) | 0.93 | 0.93 | 0.97 | 0.32 | 0.86 | 0.00 | 0.93 | 0.42 |
| pixel colour (std hist+sw) | 0.28 | 0.28 | 0.55 | 1.45 | 2.94 | 0.00 | 0.23 | 0.26 |
| random 64-d | 0.00 | 0.00 | 0.08 | 1.51 | 1.82 | 0.00 | 0.00 | 0.04 |

Pool: the other 299 paintings (the invariance experiment used about 2,400, so its pixel-colour figure of 0.547 / 32 % is on a harder pool; the pixel-colour row here is the same block on this pool and these 30 high-difference pairs). "Step" is the median nearest-neighbour distance among the 300.

Field-level agreement between the two photographs (different describers), next to the same-photograph, different-describer figure from T0 where one exists

| fields | exact | mean abs diff | kappa / median ICC | same photograph (T0): exact | same photograph (T0): mean abs diff | Jaccard per painting |
|---|---|---|---|---|---|---|
| manner, v1 scales | 0.87 | 0.14 | 0.94 | 0.84 | 0.16 |  |
| manner, added scales | 0.78 | 0.22 | 0.92 |  |  |  |
| colour scales | 0.63 | 0.41 | 0.75 | 0.82 | 0.18 |  |
| composition scales | 0.82 | 0.19 | 0.86 | 0.83 | 0.17 |  |
| felt words | 0.83 | 0.17 | 0.90 | 0.84 | 0.16 |  |
| checklist | 0.97 | 0.03 | 0.91 | 0.98 | 0.02 | 0.87 |
| depth cues | 0.93 | 0.07 | 0.87 |  |  | 0.87 |
| hue families | 0.85 | 0.15 | 0.68 |  |  | 0.69 |

Colour fields one by one (ICC column holds Cohen's kappa for the hue items)

| field | exact | mean abs diff | ICC | mean B minus A |
|---|---|---|---|---|
| palette_breadth | 0.57 | 0.53 | 0.71 | -0.13 |
| saturation | 0.53 | 0.53 | 0.66 | 0.00 |
| colour_temperature | 0.70 | 0.30 | 0.81 | 0.17 |
| darkness | 0.60 | 0.40 | 0.75 | 0.20 |
| contrast | 0.73 | 0.27 | 0.80 | 0.07 |
| main_hue | 0.63 |  |  |  |
| accent_hue | 0.60 |  |  |  |
| value_key | 0.80 |  |  |  |
| setting | 1.00 |  |  |  |
| people | 0.93 |  |  |  |
| animals | 0.93 |  |  |  |
| hue:red | 0.87 |  | 0.70 | 0.00 |
| hue:orange | 0.90 |  | 0.75 | 0.03 |
| hue:yellow | 0.80 |  | 0.61 | -0.20 |
| hue:green | 0.90 |  | 0.79 | -0.03 |
| hue:blue | 0.83 |  | 0.67 | -0.17 |
| hue:purple | 0.90 |  | -0.05 | -0.03 |
| hue:pink | 0.90 |  | 0.35 | 0.03 |
| hue:brown | 0.90 |  | 0.67 | -0.10 |
| hue:gold | 0.90 |  | 0.52 | 0.03 |
| hue:black | 0.80 |  | 0.60 | 0.07 |
| hue:white | 0.73 |  | 0.45 | -0.07 |
| hue:grey | 0.73 |  | 0.44 | -0.13 |

## T8. Recognition

recognised (v2 pass, the 300): 263 of 300 (0.88); by tradition: european_american 229/230, unknown 9/9, chinese 4/9, japanese 13/16, korean 1/9, other_non_european 3/9, persian_ottoman 3/9, south_asian 1/9

of those recognised, painter's surname matches Wikidata: 219 of 263 (string match on the last word of the name, so an undercount)

## T9. Cost

subagent runs: 30 batches, 352 descriptions, 2,940,836 tokens as reported by the harness (8,355 per description), 73.5 minutes of describer time (12.5 s per description; two ran at a time, so about half that on the clock)

record size: mean 2,367 characters of JSON per description (min 2,294, max 2,453); instrument 7,905 characters; mean stimulus 0.74 megapixels

