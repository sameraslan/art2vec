# Experiment 3: colour, fusion, lenses, period, map, and a page to look at

Run 8 October 2026. Nothing is committed. No model was run: every learned vector comes from the stores in `data/painting2vec/features/`; the only new features are colour descriptors computed from the images with numpy and Pillow. Peak memory of any step was 835 MB. Contact sheets, per-lens lists and the demo are under `data/painting2vec/exp_fusion/` and `data/painting2vec/demo/` (gitignored).

1,972 paintings: the 2,000 pilot paintings minus the 20 handscroll strips and 8 greyscale images, as in the separation experiment. Every fit (mean, scale, PCA) is on those rows.

## The answers

1. **Colour cannot be rescued as a similarity block.** About 70 descriptors and combinations under three chromatic adaptations, two crops and up to six treatments (716 variants, plus 40 hybrids). Nothing that still looks like colour gets past R@1 0.63 on two photographs of one painting. Everything above 0.85 is a low-resolution colour *layout*, and its neighbours share no more palette than random paintings do. The failure is the photograph, not the descriptor. Verdict: colour ships as a low-weight block inside the default lens, as a labelled Colour lens that says it depends on the photograph, and as a swatch shown beside the painting. It should not be a filter with hard bins.
2. **The composition recipe from the invariance experiment has to change.** `grid8_an` PCA-128 whitened with *Euclidean* distance is a hub machine: 63 % of paintings appear in nobody's top 10 and one painting appears in 1,723 of 1,972 lists. Its "71 % of the list kept" was the hubs. The same vectors with unit rows (cosine) have no hubs, a better R@1 (0.972) and find 83 % of version pairs at rank 1 against 61 %.
3. **Scaling.** With every block ending in unit rows, equal total variance (the root's rule) is automatic and works. Multiple Factor Analysis scaling is wrong here (the picture block ends up controlling 14 % of a list at equal weights). Equal weights do not mean equal control, so the weights are set from measured control.
4. **Lenses.** Whole picture (picture 1, composition 1, colour 0.5), Picture only, Composition, Colour, and Form (composition 1.4, colour 1). Whole picture is the best lens measured: 93 % of version pairs at rank 1, against 89 % for the picture block alone. Form is the weakest by eye.
5. **Hubness correction is not needed** once the hand-built blocks use cosine. Skewness is 0.4 to 1.1 and at most 1.6 % of paintings are in nobody's list.
6. **Period.** Half of a default top 10 is within 50 years of the seed (22 % at random). Lists restricted to paintings at least 150 years away are still coherent: 62 % share the seed's broad genre against 72 % unrestricted and 26 % at random, at 4 % more distance. By eye they are good for common subjects and thin for singular paintings. The filter approach works.
7. **Map.** 40 % of a true top 10 survives as 2D top-10 neighbours under the default lens, 50 % under Picture only, and 18 to 29 % under Form, Composition and Colour. The list has to stay the truth.
8. **A page exists**: `data/painting2vec/demo/index.html`. How to open it is at the end.

## Part 1. Colour

### What was computed

`colour2.py`, for all pilot, reproduction and versions images (`01_colour_features.py`, 3,044 images, twice: as is, and after the feature code's `frame` auto-crop).

| family | parts | idea |
|---|---|---|
| full palette | `hist_*`, `histc_*` (coarse 3x5x5), `sw_*` | the invariance experiment's two best parts under new normalisations |
| chromatic adaptation | `raw`, `sog` (shades-of-grey, p = 6), `wp` (white patch on the 97th percentile) | linear-RGB gains before OKLab |
| standardisation | `std` (lightness standardised, a and b centred and scaled), `sca` (a and b scaled, not centred, so the overall tint stays), `rank` (each channel replaced by its rank) | |
| hue families | `hue12_*`, `hue12w_*`, `hue6_*`, `hue6xL3_*` | proportions of 12 or 6 hue families among sufficiently chromatic pixels; by lightness tercile |
| warm and cool | `warm_*` | balance, warm share, whether the lights are the warm part, achromatic share |
| tone bands | `tb8_*`, `tb5_std` | the colour of each lightness-rank band: unchanged by any monotone tone curve |
| ranks and quantiles | `lq`, `cq`, `lc_copula`, `copula3/4`, `hist_rank` | lightness and chroma as within-image quantiles; joint rank histograms |
| small palette | `pal4/5_std`, `pal4/5_spacing` | k-means colours ordered by lightness, relative to the image's mean and scale; the sorted spacing between them |
| spatial layout | `layout4/6_*` | n x n grid of mean L, a, b after per-image normalisation |

Invariance is the invariance experiment's protocol (`fz.InvEval`: rank of the other photograph among about 2,400 other paintings, both directions; overlap of the two top-10 lists), on the 214 unflagged primary pairs, with the 28 excluded rows out of every pool. The old best (`std` hist + sw, PCA-64 whitened) scores 0.537 here against 0.547 there; the difference is the exclusion.

Discrimination: participation ratio; TwoNN dimension; **palette agreement** = sliced-Wasserstein distance between the *unnormalised* OKLab pixel distributions of a painting and its 10 neighbours, over the same to random paintings (1.0 means neighbours share no more palette than chance; the raw palette histogram itself scores 0.48); AUC with which colour-different versions sit further apart than two photographs of one painting; and looking.

### Result (`results/colour_grid.csv`, 716 rows; best treatment per descriptor)

| descriptor | crop | treatment | R@1 | top 10 kept | TwoNN | palette agreement | looks like colour |
|---|---|---|---|---|---|---|---|
| layout 6x6 L,a,b | frame | PCA-32 w | 0.953 | 0.68 | 20 | 0.99 | no |
| layout 4x4 L,a,b | frame | PCA-32 w | 0.925 | 0.62 | 21 | 0.99 | no |
| palette + 6x6 a,b layout, 1:1 (`02b_hybrids.py`) | frame | PCA-64 w | 0.900 | 0.51 | 26 | 0.76 | weakly |
| palette + 4x4 a,b layout, 1:1 | frame | PCA-32 w | 0.853 | 0.50 | 19 | 0.68 | weakly |
| layout 4x4 a,b only | frame | Euclidean | 0.820 | 0.51 | 17 | 1.01 | no |
| greedy best without spatial parts (`sw_wp_std`, `hist_sog_std`, `lq`) | frame | PCA-64 w | 0.631 | 0.37 | 18 | 0.59 | partly |
| hist + sw, shades-of-grey, `std` | frame | PCA-64 w | 0.622 | 0.36 | 18 | 0.59 | partly (tint gone) |
| old best: hist + sw, `std` | none | PCA-64 w | 0.537 | 0.32 | 18 | 0.57 | partly (tint gone) |
| **shipped: hist + sw, `sog,std` and `raw,sca` together** | frame | PCA-64 w | 0.554 | 0.35 | | | **yes** |
| hist + sw, tint kept (`sog,sca`) | frame | PCA-64 w | 0.528 | 0.33 | 19 | 0.61 | yes |
| tone bands + hue families | frame | PCA-32 w | 0.449 | 0.29 | 15 | 0.66 | yes |
| relational, tint kept (tone bands, hue families, warm/cool, rank tables) | frame | PCA-64 w | 0.430 | 0.28 | 17 | 0.60 | not viewed |
| rank only (`copula4`, `lc_copula`, `hist_rank`) | frame | PCA-64 w | 0.416 | 0.26 | 23 | 0.69 | not viewed |
| tone bands, 8 | frame | PCA-16 w | 0.406 | 0.31 | 11 | 0.64 | not viewed |
| small palette k = 5, ordered | frame | PCA-16 w | 0.250 | 0.21 | 10 | 0.62 | not viewed |
| hue families + warm/cool | frame | PCA-16 w | 0.203 | 0.21 | 8 | 0.69 | coarsely |
| 12 hue families | frame | z | 0.16 to 0.22 | 0.19 | 7 | 0.78 to 0.86 | not viewed |
| warm/cool, 5 numbers | frame | whitened | 0.13 | 0.20 | 4 | 0.68 | not viewed |
| palette spacing only | frame | z | 0.11 | 0.13 | 10 | 0.88 | not viewed |

![trade-off](results/colour_tradeoff.png)

Reading.

- **There is no descriptor with R@1 of 0.85 that is still visibly colour.** Right of the 0.85 line every point is a spatial layout and sits at palette agreement 0.9 or worse. The hybrids pass the line because the layout half recognises the painting; their lists are still half photograph (0.50 kept) and on the sheets they do not read as palette neighbours.
- The coarser and more relational a descriptor, the *worse* it does. Hue families, warm/cool balance, palette order and spacing, and rank-only descriptors score 0.07 to 0.42. They throw away information without throwing away the photograph's contribution. R@1 among 2,400 is a hard test for a 5-number descriptor, but their lists are no steadier either (0.13 to 0.31 kept against 0.36).
- What helped, modestly: the `frame` auto-crop on both sides (+4 to +7 points; the invariance experiment could not crop the pilot side), and shades-of-grey or white-patch adaptation before standardising (+3 to +5; grey-world did nothing there). Together 0.537 to 0.622.
- Keeping the overall tint costs 9 points (0.62 to 0.53) and is what makes a list look like colour. On the sheets, *The Starry Night* under tint-removed palettes returns a brown Pietà and a Goya; under tint-kept palettes it returns blue pictures (Sisley's bridge, Marc's blue horses, Road with Cypress, Cabanel's Venus, Café Terrace). The shipped block joins both.
- The final block uses cosine after whitening (see Part 2): R@1 0.572, 0.31 of the list kept. The grid above is Euclidean, where mild hubs flatter "kept" by a few points.

### Is it the photograph or the descriptor? (`results/colour_source.json`)

For hist + sw (`sog,std`), unflagged pairs:

| pairs | n | R@1 |
|---|---|---|
| pilot Commons file against the museum's image | 102 | 0.69 |
| ... National Gallery of Art / Rijksmuseum / Art Institute of Chicago / Met | 27 / 16 / 7 / 50 | 0.85 / 0.81 / 0.86 / 0.56 |
| pilot Commons file against another Commons file | 225 | 0.54 |
| two other Commons files, neither the pilot image | 98 | 0.45 |
| museum image against a second Commons file | 14 | 0.57 |

By how different the two files are (`lab_diff`), all rows:

| lab_diff | 1 to 3 | 3 to 6 | 6 to 9 | 9 to 12 | over 12 |
|---|---|---|---|---|---|
| all pairs (n = 98 / 156 / 136 / 90 / 80) | 0.97 | 0.64 | 0.41 | 0.32 | 0.07 |
| Commons against museum (47 / 41 / 18 / 18) | 0.99 | 0.72 | 0.50 | 0.39 | |
| Commons against Commons (47 / 108 / 113 / 72) | 0.96 | 0.62 | 0.39 | 0.30 | |

- **It is the photograph.** When two files agree (lab_diff under 3) every palette descriptor finds the pair 93 to 99 % of the time. R@1 falls with the size of the difference and nothing else.
- Museum pairs do better mostly because they are closer files (47 of 134 Commons-against-museum rows are under 3, against 47 of 410 Commons-against-Commons rows), not because a museum image is a different kind of thing: at matched lab_diff the gap is 3 to 11 points.
- The difference is not a source signature. The mean museum-minus-Commons shift explains 2 to 10 % of the pair difference; removing it (leave-one-out) moves R@1 on museum pairs from 0.686 to 0.686.
- It is not a few bad directions either. Learning "photograph directions" from held-out pairs (5 folds by painting) and projecting out the top 2, 4 or 8, or whitening by the within-pair covariance, moves R@1 from 0.621 to at most 0.640.
- **Museum against museum cannot be tested**: no painting in the set has images from two museums. So the single-source hypothesis is supported only indirectly: the three museums with colour-managed IIIF images agree with Commons at 0.81 to 0.86, and the dataset step found that 104 of 239 museum images *were* the Commons file. A catalogue built from one museum's own photography would be consistent within itself; a catalogue across museums is the Commons-against-Commons row.

### Would coarse colour properties work as a filter? (`results/colour_props.json`)

Agreement between two photographs of one painting, clean pairs:

| property | rank correlation | same tercile | same or adjacent quintile |
|---|---|---|---|
| mean lightness | 0.86 | 0.72 | 0.91 |
| lights warmer than darks | 0.85 | 0.72 | 0.92 |
| warm share of coloured pixels | 0.72 | 0.68 | 0.86 |
| achromatic share | 0.70 | 0.67 | 0.86 |
| mean chroma | 0.69 | 0.64 | 0.85 |
| warm/cool balance | 0.69 | 0.66 | 0.83 |
| dominant hue family of 6 | | 0.74 same (the largest family alone holds 68 % of paintings); 0.95 in the other photograph's top two | |

A three-way bin puts the two photographs of a painting in different bins about a third of the time. Colour properties are fine to *show* and to sort by loosely; a hard "warm only" filter would wrongly drop one painting in three near the edges.

### What I saw (12 sheets written, 4 viewed; 6 tint sheets written, 2 viewed)

- Tint-removed palettes (rows A, B): *Arnolfini Portrait* returns green drapery with red and black (Holbein's sitters, the Ambassadors, Rossetti's Beloved): convincing. *Third of May* returns dark pictures with a warm lit patch: convincing as light, not as hue. *Starry Night*: one hit (Starry Night over the Rhône), then brown and grey pictures.
- Tone bands + hue families (row C): the most colour-like of the relational ones. *Starry Night* returns blue and yellow pictures (Sisley, Noon Rest, Turner).
- Hue families + warm/cool (row D): plausible at a coarse level (blue-and-pale pictures for *Starry Night*, dark ones for Goya), with no finer agreement.
- Layout only (row E): not colour. Rows fill with brown scrolls, manuscripts and low-chroma pictures.
- Hybrids (rows F, G): mixed. Some rows share a palette, most share a rough arrangement of warm and cool areas. Not something a person would call "the same colours".
- Tint kept (rows H, I, J on the tint sheets): the only rows where *Starry Night* is surrounded by blue. *Birth of Venus* returns muted green-ochre crowd scenes (Triumph of Death, Bruegel): a real palette match that crosses subject.

### Verdict

Demote, but do not drop. Colour as a block fails the test at 0.57, against a pass line of 0.85 here and 0.95 in the invariance experiment.

- **In the default lens: weight 0.5.** At that weight colour decides 19 % of a list (Part 2) and costs 4 points of list stability (0.747 to 0.707 kept).
- **As its own lens: yes, labelled.** The owner wants it, the lists do look like colour, and the page says that about two thirds of each list depends on the photograph.
- **As a displayed property: yes** (a five-colour swatch, in the demo). **As a hard filter: no.**
- The real fix is the artefact: the holding museum's own image, auto-cropped. That is a data decision, not a descriptor.

Recipe: OKLab, `frame` auto-crop; parts `hist_sog_std`, `sw_sog_std`, `hist_raw_sca`, `sw_raw_sca` (histograms square-rooted), each divided by the root of its total variance, joined, PCA 64, whitened, unit rows, cosine.

## Part 2. Fusion

### Blocks

| block | recipe | dim | R@1, two photographs | top 10 kept | version pairs at rank 1 | broad genre P@10 | same painter in top 10 | median year gap (random 174) | hub skew / in no list |
|---|---|---|---|---|---|---|---|---|---|
| picture | DINOv2-L `cls`, `tile`, L2, centre, PCA 64, unit rows | 64 | 0.991 | 0.83 | 0.89 | 0.78 | 12.5 % | 58 | 0.85 / 1.6 % |
| composition | `grid8_an`, PCA 128 whitened, **unit rows** | 128 | 0.972 | 0.56 | 0.83 | 0.42 | 2.6 % | 146 | 1.13 / 0 % |
| colour | above | 64 | 0.572 | 0.31 | 0.05 | 0.45 | 5.9 % | 119 | 0.42 / 0.1 % |
| texture (optional) | DINOv2-L `gram_late`, `tile`, L2, centre, PCA 64, unit rows | 64 | 0.979 | 0.71 | 0.83 | 0.70 | 10.8 % | 69 | 1.09 / 0.9 % |

Same-painter chance is 1.1 %; broad-genre chance about 0.29.

### The hub problem (`04b_hub_treatments.py`, `results/hub_treatments.csv`)

| composition treatment | R@1 | top 10 kept | hub skew | in no list | largest hub | version pairs at rank 1 |
|---|---|---|---|---|---|---|
| as stored, Euclidean | 0.932 | 0.57 | 10.1 | 22 % | 634 lists | 0.61 |
| PCA-128 whitened, Euclidean (the invariance experiment's recipe) | 0.956 | 0.71 | 16.4 | 63 % | 1,723 lists | 0.61 |
| PCA-128 whitened, unit rows | 0.972 | 0.56 | 1.1 | 0 % | 40 lists | 0.83 |
| PCA-64 whitened, unit rows | 0.949 | 0.56 | 0.8 | 0 % | 34 lists | 0.77 |
| PCA-32 whitened, unit rows | 0.911 | 0.54 | 0.7 | 0 % | 30 lists | 0.61 |

Whitening spreads a block over 128 equal directions, and in that space the paintings near the mean are everyone's neighbour. Normalising the rows removes the effect entirely. The invariance experiment's 0.71 "kept" was two lists sharing the same hubs; the honest figure is 0.56. The same holds for colour, less severely (skew 3.8 to 0.4).

### Making blocks comparable (`04_fusion.py`, `results/fusion.json`)

Fused squared distance = sum over blocks of (weight / scale)² x squared block distance. *Control* of a block = the share of the top 10 that changes when its weight goes to 0.

| scaling rule | control at equal weights: picture / composition / colour | Form at 1:1: composition / colour | composition : colour ratio that balances Form |
|---|---|---|---|
| equal total variance (the root's rule; automatic with unit rows) | 0.70 / 0.32 / 0.57 | 0.47 / 0.87 | 1.37 |
| first singular value (MFA) | 0.14 / 0.72 / 0.64 | 0.74 / 0.66 | 0.94 |
| equal median nearest-neighbour distance | 0.86 / 0.14 / 0.36 | 0.32 / 0.92 | 1.75 |
| equal median 10th-neighbour distance | 0.83 / 0.20 / 0.42 | 0.38 / 0.90 | 1.57 |
| equal sd of squared distance over all pairs | 0.47 / 0.52 / 0.65 | 0.61 / 0.79 | 1.14 |

- No rule makes equal weights mean equal control. Control follows how much a block's distances *vary* among near candidates, which total variance does not measure: the picture block has a few strong directions (participation ratio 16 of 64) and so a wide spread of distances; a whitened block has nearly the same distance to everything.
- MFA is the wrong rule for this mix: dividing by the first singular value punishes the one block with structure.
- Equalising the spread of squared distances is the most even, and is the rule to use if weights are ever exposed as sliders. For fixed lenses it does not matter: keep the root's rule and set weights from the control table.

Control under equal total variance, picture weight 1 (picture / composition / colour):

| composition weight | colour 0 | colour 0.35 | colour 0.5 | colour 0.71 | colour 1 |
|---|---|---|---|---|---|
| 0 | | 0.94 / 0 / 0.13 | 0.92 / 0 / 0.25 | 0.86 / 0 / 0.43 | 0.74 / 0 / 0.65 |
| 0.5 | 0.95 / 0.17 / 0 | 0.92 / 0.16 / 0.13 | 0.90 / 0.15 / 0.24 | 0.84 / 0.13 / 0.42 | 0.73 / 0.09 / 0.64 |
| 0.71 | 0.93 / 0.30 / 0 | 0.90 / 0.29 / 0.12 | 0.88 / 0.27 / 0.22 | 0.83 / 0.24 / 0.39 | 0.72 / 0.18 / 0.62 |
| **1** | 0.87 / 0.49 / 0 | 0.86 / 0.48 / 0.10 | **0.84 / 0.45 / 0.19** | 0.79 / 0.41 / 0.34 | 0.70 / 0.32 / 0.57 |
| 1.41 | 0.77 / 0.69 / 0 | 0.76 / 0.68 / 0.07 | 0.74 / 0.66 / 0.14 | 0.71 / 0.62 / 0.27 | 0.64 / 0.54 / 0.47 |

Composition at half weight, as the draft framework had it, controls 15 % of the list: close to decoration. At full weight it controls 45 % and the lens gets better (below).

### Texture

Adding `gram_late` at 0.7 to the default lens changes 27 % of the top 10. It raises version pairs at rank 1 from 0.93 to 0.97 and list stability from 0.71 to 0.75, and it raises painter repeats from 12.4 to 13.6 % and narrows the year gap from 56 to 52 years. Alone it is a weaker picture block (genre 0.48 against 0.58; 25 % of its list shared with picture). It adds stability and period, and nothing with a name. Not shipped. I did not look at a texture sheet.

## Part 3. Lenses (`05_lenses.py`, `results/lenses.json`)

| lens | weights | broad genre P@10 | same painter | median year gap | version pairs: rank 1 / top 10 | two photographs: R@1 / top 10 kept | hub skew / in no list / largest |
|---|---|---|---|---|---|---|---|
| **Whole picture** (default) | picture 1, composition 1, colour 0.5 | 0.77 | 12.4 % | 57 | 0.93 / 1.00 | 0.986 / 0.71 | 0.74 / 1.0 % / 35 |
| **Picture only** | picture 1 | 0.78 | 12.5 % | 58 | 0.89 / 0.99 | 0.991 / 0.83 | 0.85 / 1.6 % / 38 |
| **Form** | composition 1.4, colour 1 | 0.46 | 5.2 % | 122 | 0.75 / 0.89 | 0.977 / 0.42 | 0.71 / 0.1 % / 28 |
| **Composition** | composition 1 | 0.42 | 2.6 % | 146 | 0.83 / 0.91 | 0.972 / 0.56 | 1.13 / 0 % / 40 |
| **Colour** | colour 1 | 0.45 | 5.9 % | 119 | 0.05 / 0.30 | 0.572 / 0.31 | 0.42 / 0.1 % / 24 |
| not shipped: whole, colour at 1 | 1, 1, 1 | 0.74 | 12.4 % | 58 | 0.89 / 0.99 | 0.979 / 0.54 | 0.85 |
| not shipped: whole, no colour | 1, 1, 0 | 0.77 | 11.8 % | 58 | 0.96 / 1.00 | 0.986 / 0.75 | 0.69 |

On all 274 primary pairs, flagged ones included, top 10 kept is 0.68 / 0.81 / 0.41 / 0.52 / 0.32.

Overlap of top-10 lists:

| | whole | picture | form | composition | colour |
|---|---|---|---|---|---|
| whole | 1 | 0.50 | 0.17 | 0.12 | 0.08 |
| picture | | 1 | 0.04 | 0.03 | 0.04 |
| form | | | 1 | 0.31 | 0.28 |
| composition | | | | 1 | 0.02 |
| colour | | | | | 1 |

- The lenses are different lists. Picture shares 3 to 4 % with composition and colour, and composition shares 2 % with colour, so the three blocks are close to independent.
- Whole picture beats Picture only on the copies test (0.93 against 0.89 at rank 1) with the same painter repeats and year gap, and loses 12 points of list stability, 8 of them to composition and 4 to colour.
- Form does what it says on the measures (it crosses period: 122 years; it crosses subject: broad genre 0.46 against 0.29 at chance; it still finds 75 % of versions) and is the least stable lens after Colour (0.42 kept). By eye it is the weakest: *Mona Lisa* under Form returns its two copies, then *L'Absinthe*, *Irises* and a battle scene.
- Colour finds almost no version pairs (5 %), as the framework expected of copies.

Leaks (linear probes on the fused vector's first 64 principal components, folds grouped by painter; European rank stratum for year, fame and museum):

| lens | year R² | fame R² / rank correlation | fame within painter | museum accuracy (year + country alone 0.40; majority 0.18) | painter accuracy, 53 painters |
|---|---|---|---|---|---|
| Whole picture | 0.53 | -0.06 / 0.04 | 0.20 | 0.24 | 0.37 |
| Picture only | 0.57 | -0.06 / 0.05 | 0.23 | 0.20 | 0.38 |
| Form | 0.12 | -0.06 / 0.04 | 0.05 | 0.24 | 0.20 |
| Composition | -0.08 | -0.05 / 0.01 | 0.05 | 0.18 | 0.09 |
| Colour | 0.20 | -0.06 / 0.05 | 0.03 | 0.27 | 0.22 |

- Fame: not predictable across painters in any lens. Within a painter the picture block has a weak signal (0.20 to 0.23, standard error about 0.03), as the separation experiment found.
- Museum: no lens beats the year-and-country baseline. Colour is the highest (0.27) and adding it to the baseline gives 0.42 against 0.40: a hint of the photography, not a finding.
- Period lives in the picture block (year R² 0.57) and is absent from composition (-0.08).

Genre make-up, share of neighbours sharing the seed's broad genre (base rate in the set):

| lens | narrative (0.41) | portrait (0.21) | genre scene (0.14) | landscape (0.08) | nude (0.07) | still life (0.02) |
|---|---|---|---|---|---|---|
| Whole picture | 0.76 | 0.65 | 0.38 | 0.64 | 0.59 | 0.40 |
| Picture only | 0.77 | 0.68 | 0.38 | 0.65 | 0.61 | 0.49 |
| Form | 0.53 | 0.31 | 0.18 | 0.26 | 0.14 | 0.07 |
| Composition | 0.48 | 0.31 | 0.15 | 0.15 | 0.09 | 0.04 |
| Colour | 0.53 | 0.27 | 0.17 | 0.27 | 0.14 | 0.08 |

Worst hubs. Whole picture: an 1895 river landscape by Castagneto (35 lists), *La Belle Ferronnière* (34), Rubens's *Death of Adonis* and *Susanna* (33), Titian's *La Bella* (33). Picture only: Titian's *La Bella* (38) and *Violante*, a Rubens portrait, Botticelli's *Lamentation*. Form and Composition: *Quail and Millet*, an Amitabha assembly, a Pichvai diagram, a Mughal fable page, a Vasudhara mandala. So the picture lenses' hubs are generic half-length portraits and the form lenses' hubs are flat, evenly filled non-European works. With a maximum of 35 to 40 lists in 1,972 neither is a problem.

Hubness correction on the default lens:

| | skew | in no list | largest | broad genre P@10 | list shared with uncorrected |
|---|---|---|---|---|---|
| none | 0.74 | 1.0 % | 35 | 0.765 | 1 |
| local scaling (k = 10) | 0.12 | 0 % | 22 | 0.754 | 0.82 |
| CSLS (k = 10) | 0.47 | 0 % | 25 | 0.755 | 0.80 |
| mutual proximity (Gaussian) | 0.50 | 0.1 % | 29 | 0.762 | 0.82 |

Each correction changes about a fifth of every list to fix something that is already small, and costs a point of genre agreement. **Not worth it.** Centring and unit rows are enough. The correction that mattered was the one in Part 2.

## Part 4. Period (`results/period.json`)

| lens | top 10 within 25 / 50 / 100 years | at least 150 years away | lists entirely within 50 years | lists with at least one neighbour 150 years away |
|---|---|---|---|---|
| random | 22 % within 50 | | | |
| Whole picture | 35 / 49 / 64 % | 28 % | 7 % | 80 % |
| Picture only | 35 / 49 / 64 % | 28 % | 9 % | 76 % |
| Form | 22 / 34 / 48 % | 44 % | 0.3 % | 98 % |
| Composition | 18 / 28 / 42 % | 49 % | 0 % | 99.7 % |
| Colour | 23 / 35 / 48 % | 44 % | 1 % | 96 % |

What the filter costs under Whole picture:

| list | same broad genre | same Wikidata genre | distance of the 10th neighbour against unrestricted | rank of the 1st / 10th in the full ordering | same tradition |
|---|---|---|---|---|---|
| unrestricted | 0.72 | 0.53 | 1 | 1 / 10 | 0.78 |
| at least 50 years away | 0.67 | 0.47 | 1.02 | 2 / 18 | 0.75 |
| at least 150 years away | 0.62 | 0.38 | 1.04 | 4 / 35 | 0.71 |
| at least 300 years away | 0.52 | 0.29 | 1.09 | 14 / 99 | 0.57 |
| random painting 150 years away | 0.26 | | | | |

- The default lens is period-bound but not period-locked: half the list is within 50 years, yet four lists in five already contain a neighbour from 150 years away, and the first such neighbour is typically at rank 4.
- Excluding the seed's era costs little: the 10th neighbour from 150 or more years away is 4 % further than the 10th overall, and 62 % still share the seed's broad genre. For 94 % of paintings those ten are inside the top 100. At 300 years the lists thin out (rank 99 for the 10th; half the paintings need more than the top 100).
- Picture only pays more for the same crossing (16 % further at 150 years) because it has nothing but the period-carrying block; the composition block is what makes far neighbours cheap.

What I saw (29 sheets written, 4 viewed; each shows every lens unrestricted and at 150 years).

- *Mona Lisa* (1503) at 150 years, Whole picture: eight half-length portraits of women from 1665 to 1874 (a Rossetti, a Reynolds-style head, a Corot-like sitter). Coherent and a real crossing.
- *Third of May 1808* (1814): the Triumph of Death, the Night Watch, the Peasant Dance, the Cripples, a militia company: crowded figure scenes from 1560 to 1642. Coherent.
- An El Greco portrait (1600): male and female half-length portraits around 1800 to 1832, then a Renoir seaside sitter. Coherent.
- *The Starry Night* (1889): View of Toledo, a Japanese screen of waves, an Indian page with scrolling clouds, a Leonardo-like deluge drawing: these share the swirl and are the best kind of crossing. The other four (a map scroll, a bird on a branch, a hanging scroll) share little.
- Under Form and Composition the 150-year lists look like the unrestricted ones, which is to say loose.

So the promise holds where a painting has kin (portraits, crowds, landscapes) and weakens for one-of-a-kind pictures. Four sheets is a small sample.

**For the product:** do not try to remove period from the vectors. Keep it as a filter, and offer the crossing directly: the demo's "other eras only" switch reads a second precomputed list per lens (the ten nearest at least 150 years away), since a top-100 list is not deep enough for everyone.

## Part 5. Map (`06_map.py`, `results/map.json`)

openTSNE, exact neighbours, Euclidean on the fused vectors, perplexity 30, seed 0. The default lens starts from PCA (250 iterations of early exaggeration, 500 more). Every other lens starts from the default lens's finished layout and runs 500 iterations with no early exaggeration (`aligned`); `fresh` is the same lens from its own PCA start, for comparison.

| lens | true top 10 found in 2D top 10 / top 30 / top 100 | trustworthiness (k = 10) | median move from the default map, share of map span | fresh layout: top 10 in 2D top 10 / move |
|---|---|---|---|---|
| Whole picture | 0.40 / 0.56 / 0.75 | 0.967 | | |
| Picture only | 0.50 / 0.68 / 0.81 | 0.978 | 2 % | 0.51 / 7 % |
| Form | 0.21 / 0.26 / 0.35 | 0.727 | 12 % | 0.27 / 22 % |
| Composition | 0.18 / 0.21 / 0.27 | 0.667 | 12 % | 0.25 / 24 % |
| Colour | 0.29 / 0.35 / 0.43 | 0.818 | 14 % | 0.38 / 23 % |

- Under the default lens four of a painting's ten true neighbours are among its ten nearest on the map. Perplexity 10 or 50 gives the same (0.40, 0.39).
- Form, Composition and Colour barely fit in two dimensions: a whitened block has 60 to 130 equal directions, and a quarter or less of a list survives. Their maps show broad regions only.
- Alignment halves how far a painting moves when the lens changes (12 to 14 % of the map against 22 to 24 %) and costs 6 to 10 points of neighbour preservation on those three lenses. Picture only keeps the default map almost as it is (2 %).
- The root's rule stands: the list is the truth. The page draws lines from the selected painting to its listed neighbours so the distortion is visible.

UMAP was not tried.

## Part 6. The page

`data/painting2vec/demo/` (113 MB): `index.html` (plain HTML, CSS and JavaScript, no build, no external request), `data/*.json`, `thumbs/` (256 px), `large/` (512 px, for the detail view), `atlas.jpg` (64 px cells, to draw 1,972 thumbnails per frame). The page source is kept at `demo_page/index.html` and copied by `07_export.py`.

To open it, from the repository root (this worktree):

```
python3 -m http.server 8765 --directory data/painting2vec/demo
```

then open <http://localhost:8765/>. Opening the file directly will not work: a browser does not let a page read JSON from a `file://` address, and the page says so if you try.

What it does: a map with zoom and pan and a lens switch (positions glide between lenses); click a painting for a larger image, title, painter, year, medium, size, collection, a five-colour swatch and a link to its Wikidata page; its ten neighbours under the current lens, each clickable, with a trail of visited paintings and browser back; a year-range filter and "not this painter again", which hide entries of the precomputed list and show each survivor's true rank; "other eras only", which switches to the precomputed 150-year list; search by title or painter. The browser computes no distance.

Checked by `08_verify_demo.sh`: served on a free port, the page, the atlas and all seven JSON files fetched with curl (HTTP 200), JSON parsed and checked for consistency (lengths, index ranges, no self-neighbours, the 150-year rule), all 3,944 images present, no external URL in the page; server stopped. I also loaded it in a browser at 1400 x 900, switched lens, applied each filter, walked to a neighbour: no console errors. One bug found and fixed that way (the map was empty when the pane had no size at load).

## Recommendation

**Blocks**

| block | recipe |
|---|---|
| picture | DINOv2-L `cls`, `tile` view, L2, centre on the canon mean, PCA 64, no whitening, unit rows, cosine |
| composition | `grid8_an`, PCA 128, whitened, **unit rows, cosine** |
| colour | OKLab after `frame` auto-crop; `hist` + `sw` under shades-of-grey + `std`, and under `sca` (tint kept); each part to unit total variance; PCA 64, whitened, unit rows, cosine |
| texture | not shipped |

**Scaling rule.** Equal total variance, which unit rows give for free. Weights multiply the vectors. Check control (the share of a list a block decides) whenever a block or weight changes; do not read weights as shares.

**Lenses**

| lens | picture | composition | colour | control of each block |
|---|---|---|---|---|
| Whole picture (default) | 1 | 1 | 0.5 | 0.84 / 0.45 / 0.19 |
| Picture only | 1 | | | |
| Form | | 1.4 | 1 | 0.70 / 0.70 |
| Composition | | 1 | | |
| Colour, labelled as photograph-dependent | | | 1 | |

Composition is listed as its own lens because it is the half of Form that survives a second photograph. If five is one too many, drop Form.

**Hubness.** No correction. Never use Euclidean distance on a whitened block.

**Colour.** Fails as a block; low weight in the default lens, a labelled lens, a displayed swatch; no hard filter. Fix it at intake with the museum's own image.

**Period.** A filter, plus a precomputed "other eras" list per lens. Cross-period neighbours are good enough to ship for most paintings.

**Export.** `paintings.json`: column-wise metadata. `lenses.json`: lens ids, names, weights, scaling rule, list depth. `lens_<id>.json`: `xy` (flat, two numbers per painting, in [-1, 1]), `nn` (ordered top 100 as row indices), `far` (ordered top 10 at least 150 years away). About 1 MB per lens for 1,972 paintings; for a larger canon cut `nn` to 50 and send it as a typed array.

## Solid, marginal, not tested

Solid.

- No palette descriptor survives a second photograph, and the ones that pass are layouts. 700 variants, one direction of effect, consistent with the sheets.
- The failure tracks the size of the photographic difference and is neither a source offset nor a few directions.
- Whitened Euclidean composition is a hub artefact; cosine removes it and improves every other measure.
- The three blocks are near-independent (2 to 4 % shared lists).
- MFA scaling is wrong for this mix; equal weights are not equal control under any rule.
- No hubness correction is needed after that.
- Period sits in the picture block and not in composition; cross-era lists cost 4 % in distance.

Marginal.

- The shipped colour recipe (tint kept and removed together) was chosen by eye on six seeds. It scores 0.55 to 0.57 against 0.62 for the tint-removed one.
- Whole picture beating Picture only on version pairs: 0.93 against 0.89 on 132 pairs.
- The lens weights. They come from control shares on this set, not from anyone's judgement of the lists.
- Texture: a real gain on copies and stability, a real cost in period and painter. I did not look at it.
- Museum probe for colour (0.27; 0.42 against a 0.40 baseline).
- Cross-period coherence by eye: four seeds viewed.
- Form as a lens: passes the numbers, weak on the sheets.
- Every choice was made on the pairs and paintings it is reported on. There is no held-out set.

Not tested.

- Museum against museum for the same painting (the data has none), so the single-source hypothesis is indirect.
- Any human judgement, any second viewer.
- Auto-cropped inputs for the picture and composition blocks (only colour was cropped here).
- UMAP; any map for more than 1,972 points; paths between paintings.
- A learned or adaptive colour correction, colour from a museum-only catalogue, or colour restricted to paintings whose reproductions agree.
- Hubness and control at a larger canon, where both change.
- The page in browsers other than the one in this app, on a phone, or with a keyboard only.
- The 28 excluded images.

## Files

| file | what |
|---|---|
| `colour2.py`, `01_colour_features.py` | the new colour descriptors; computes them (about 30 minutes, 260 MB) |
| `fz.py` | paths, stores, the fit (scale, centre, PCA, whiten, unit rows), the invariance protocol |
| `blocks.py` | block recipes, the colour recipe, scaling rules, the lens set, contact sheets |
| `leak.py` | list checks, hubs, version pairs, probes (uses `exp_separation/evals.py`) |
| `02_colour_eval.py`, `02b_hybrids.py` | Part 1 grid, greedy selection, palette + layout hybrids |
| `03_colour_pick.py`, `03b_tint_sheets.py` | trade-off plot, source and photograph-direction tests, property agreement, colour sheets |
| `04_fusion.py`, `04b_hub_treatments.py` | Part 2 |
| `05_lenses.py` | Parts 3 and 4, period sheets, per-lens lists |
| `06_map.py` | Part 5 |
| `07_export.py`, `demo_page/index.html`, `08_verify_demo.sh` | Part 6 |
| `results/` | every table's source |

Run from the repository root, one at a time, in numeric order:

```
U="uv run --no-project --with numpy --with pandas --with scipy --with scikit-learn --with matplotlib --with pillow --with openTSNE python experiments/painting2vec/exp_fusion"
$U/01_colour_features.py; $U/02_colour_eval.py; $U/02b_hybrids.py; $U/03_colour_pick.py; $U/03b_tint_sheets.py
$U/04_fusion.py; $U/04b_hub_treatments.py; $U/05_lenses.py; $U/06_map.py; $U/07_export.py
experiments/painting2vec/exp_fusion/08_verify_demo.sh
```

Order matters in one place: `02_colour_eval.py` was run before the colour and composition blocks were switched to unit rows, and nothing in it depends on that; `04_fusion.py` onwards use the final recipes in `blocks.py`.
