# Experiment 1: can subject and manner be kept apart?

Run 8 October 2026 for experiment 1 of `src/art2vec/painting2vec/FRAMEWORK.md` (section 9). Nothing here is committed. This file is generated: the prose is in `README.tmpl.md`, the tables are filled in by `report.py` from `results/*.json`. Contact sheets are in `data/painting2vec/exp_separation/` (gitignored).

No model was run. Every number comes from the feature stores in `data/painting2vec/features/{pilot,versions}/`.

## The answer

**The split the framework asks for is not there. A different split is.**

- What separates cleanly is *what is shown* from *who and when*. A DINOv2 embedding gives neighbours that share what is depicted. CSD, CLIP and SigLIP 2 give neighbours by the same painter, school and decade, whatever is depicted. The two kinds of list share 1 to 3 paintings in 10.
- What does not separate is *what is shown* from *how it is rendered*, in the framework's sense of manner (how abstract, line or paint, smooth or broken). No candidate manner block follows the describer's manner scales better than the subject block already does, and once the subject block is regressed out of a manner candidate, nothing of those scales is left.
- Second-order statistics of DINOv2 tokens (Gram, per-channel sd) are not a manner block. On every measure they are a weaker copy of the first-order tokens.
- CSD is not a manner block either. On this corpus it behaves as a painter and period model: its two heads, `style` and `content`, return the same neighbours (9.1 of 10 shared), and plain CLIP beats it at finding the same painter.
- A text-trained encoder is not needed for subject. SigLIP 2 gains 0.04 on same-genre retrieval and ties on version pairs and on the describer's checklist. It carries more of the painter, the year and fame, and by eye it puts *The Starry Night* next to the *Mona Lisa*.

Recommendation in one line: ship one learned block, DINOv2-L, and call it the picture; keep colour and composition as the explicit blocks; do not ship a learned manner block; if manner is wanted, measure it directly. Details are in "Recommendation" below.

## Method

### Data and exclusions

The 2,000 pilot paintings, minus 28: the 20 handscroll strips with a short side under 100 px and the 8 greyscale images the dataset README lists (ids in `results/setup.json`). The 28 are left out of every fit (means, z-scores, PCA, residual regressions) and every evaluation. [[N_KEPT]] paintings remain. Another 32 scrolls wider than 3:1 with a short side of 100 px or more were kept; a few turn up in the contact sheets.

The versions set (355 images, 195 kept pairs) is transformed with the pilot's fit and used only for the version and copy tests.

### Candidates and treatment

Every stored part of every learned store was run in the `pad` view, and every colour and composition part except `palette_kmeans` (not meaningful under a vector distance; colour parts singly from the `lstd` store only, the five normalisations as composites). The tables below show a selection; all candidates with every column are in `results/all_candidates.md`. Derived parts:

- `mean_<layer>` and `std_<layer>`: the two halves of `meanstd_<layer>`, so first-order and second-order can be compared at the same layer.
- `gramlog_<layer>`: the matrix logarithm of the stored 24 x 24 covariance, so Euclidean distance is the log-Euclidean distance between covariances.
- "DINOv2-L stats": `gramlog_early`, `gramlog_mid`, `std_early`, `std_mid`, each reduced to 64 dimensions, scaled to equal total variance, joined, and reduced to 64 again. This is the purest second-order candidate.
- Colour and composition composites, built the same way from their parts (colour from the `lstd` store).
- Residuals, written `A ⟂ B`: A (64 dimensions) minus its ridge prediction from B (64 dimensions, or several blocks side by side), fitted on the kept pilot rows. Linear, no labels.

Default treatment: L2-normalise rows for tokens and heads, z-score per dimension for statistics parts; centre on the pilot mean; PCA to 64; cosine distance. Variants are in Part E.

### Measures

Subject.

- **genre P@10**: share of a painting's 10 nearest neighbours that share a Wikidata genre (P136) with it. Chance [[CH_GENRE]]. "Other painters only" removes the painting's own painter from the pool first.
- **depicts J@10**: mean Jaccard overlap of depicts (P180) labels with the 10 nearest. Chance [[CH_DEP]]. Depicts mixes visible things with identities (Jesus, Lisa del Giocondo), so it rewards an encoder that knows who is in the picture.
- **checklist ρ**: over the 1,770 pairs of the 60 describer paintings, rank correlation between the candidate's distance and the distance between the two paintings' subject checklists (46 items, mean of the two plain presentations). A permutation null gives a standard deviation of 0.03. **checklist nn3**: the checklist distance to a painting's 3 nearest among the 60, divided by the mean checklist distance; under 1 is good, a random block gives 1.0.
- **version top-1, top-10, ratio**: for each version pair, the rank of the partner among the 1,972 pilot paintings plus the partner (both directions, averaged), on the 132 pairs judged to share a composition. Ratio is the distance to the partner over the distance to the nearest other painting; under 1 means the partner is the nearest thing there is. "Variant" is the 32 pairs with visible changes, "series" the 31 Monet and Hicks series pairs.

Manner.

- **manner ρ**, **manner nn3**: as for the checklist, against the Euclidean distance between the describer's abstraction, contour and finish marks. "Given subject" is the partial correlation with the checklist distance held fixed.
- **read abstraction / contour / finish**: leave-one-out rank correlation of a ridge readout of that scale from the block's first 16 dimensions, on the 60. This asks whether the block carries the scale at all, not whether distance follows it. A random block scores between -0.3 and -0.15 here, so treat anything under about 0.4 as nothing.
- **painter AUC**: for each painting by one of the 53 painters with 8 or more works, the probability that another painting by the same painter is nearer than a painting by someone else. 0.5 is chance. Computed four ways: all candidates; only candidates in the same broad genre; only candidates in a *different* broad genre; and different genre and within 30 years of the query. The broad genres are portrait, narrative (religious, mythological, history, allegory), genre scene, landscape, still life and animal, nude (mapping in `lib.py`).
- **movement AUC, other painter and genre**: the same for movement (P135), with the query's own painter and its broad genre both removed from the pool.

Leaks. Linear probes are ridge regressions (one-vs-rest on one-hot targets for classes) on the block's first 64 dimensions, cross-validated five-fold. Year, movement, fame and museum folds are grouped by painter, so a probe cannot score by recognising a painter it has seen.

- **painter acc**: 53 painters, 1,174 paintings, stratified folds; the largest class is 6 per cent.
- **year R²**: within the sitelink-rank (European) stratum, and over all paintings. A random block scores -0.12 because of the grouped folds; read that as the floor.
- **movement acc**: 14 movements with 20 or more paintings; majority 0.13.
- **tradition bal. acc**: 7 traditions; chance 0.14.
- **fame R², fame ρ**: log sitelinks within the rank stratum, unseen painters. **Fame ρ within painter**: both the vector and log sitelinks have the painter's mean removed (1,101 paintings by painters with 8 or more works), so the probe has to say which of a painter's works are the famous ones. Standard error about 0.03.
- **museum**: 10 museums with 25 or more rank-stratum paintings (594 paintings; majority 0.18). The second column adds the block's first 16 dimensions to a baseline of year (cubic) and country, which alone scores 0.40.
- **Neighbour lists**: share of the top 10 by the same painter (chance [[CH_PAINTER]]); median year gap to the top 10, and that over the gap to random paintings (179 years); skewness of the k-occurrence counts; share of paintings in nobody's top 10.

### How labels were used

Painter, year, movement, genre, depicts, fame and museum labels appear only in `evals.py`, to score. The one exception is the section "Label-assisted removal", which is marked as such. Choices made after seeing scores (which candidates to carry into the residuals, the ablations and the contact sheets) were made on the whole pilot set; there is no held-out split, so the tables describe this set and are not an estimate for a new one.

## Part A and B. What each candidate carries

### Subject signal

{{subject_main}}

Residual candidates:

{{subject_res}}

Reading.

- First-order beats second-order at every layer. At the middle layer the token mean scores 0.43 on genre and the token sd 0.41; at the early layer the sd is at 0.33 and puts a second version of the same composition at a median rank of 175.
- Subject signal rises with depth and is highest in the final `cls` and `patch_mean`. `patch_mean` follows the describer's checklist best (0.52); `cls` is best on genre.
- Text-trained encoders lead on genre (0.62 against 0.57) and depicts (0.111 against 0.099). With the painting's own painter removed from the pool the gap is the same size (0.59 against 0.55), so it is not only painter repeats. They do not lead on the checklist (0.44 against 0.43 to 0.52) or on version pairs (0.88 against 0.89 to 0.91). Genre and depicts are labels written by people who know the painting; the checklist and the version pairs are about what is visibly there.
- Every learned block ranks a version of the same composition first or nearly so. This test does not separate the leading candidates; it only rules out early layers, statistics parts, colour and CSD (0.53).
- Composition alone finds 61 per cent of version partners at rank 1; colour finds 2 per cent. That is section 8's expectation for copies ("close under subject and composition, need not be under colour").

### Manner signal

{{manner_main}}

Residual candidates:

{{manner_res}}

Reading.

- **The describer's manner scales are followed weakly by everything and best by the semantic embeddings.** Manner ρ is 0.18 for DINOv2-L `cls`, 0.19 for CSD style, 0.21 for CLIP, and 0.09 for the second-order statistics. The local version says the same (0.81, 0.77, 0.79 against 0.88). No "manner" candidate beats the subject candidates on manner.
- **After subject is regressed out, no manner candidate follows the scales at all** (nn3 between 0.90 and 1.00, ρ at zero). Whatever the manner candidates know about abstraction, contour and finish, the subject block knows too.
- **Finding the same painter in a different genre** is the one thing the manner candidates do that subject candidates should not. The order is CLIP 0.89, CSD 0.86, SigLIP 2 0.81, DINOv2-L `meanstd_mid` 0.74, `cls` 0.72, second-order statistics 0.65, colour 0.62. Second-order statistics are *worse* at this than the subject block they are meant to complement.
- About a third of that is the period and not the hand: restricting the pool to paintings within 30 years of the query brings CLIP to 0.78, CSD to 0.75 and DINOv2 `cls` to 0.64.
- The residuals behave as designed on this measure. DINOv2-L `cls` ⟂ CSD style is at chance for the painter across genres (0.50) and keeps genre P@10 at 0.41 and version top-1 at 0.73. CSD style ⟂ DINOv2-L `cls` finds the painter across genres at 0.70 (0.67 within 30 years) with genre P@10 down to 0.25. That is a real separation, of depicted content from painter.
- CLIP ⟂ DINOv2-L still finds the painter at 0.74. What CLIP knows beyond DINOv2 is largely who painted it.

Limits of the describer comparison: 60 paintings; the describer is a model and recognised 49 of them; abstraction has almost no range in this set (31 at 0, 21 at 1, 8 at 2 on a 0 to 4 scale); the marks were made from 1,024 px files, the encoders saw 224 px.

### The copies test

How the 195 pairs divide. "Same hand" means both paintings have the same Wikidata creator; "other hand" means two different named creators; "unknown" means one of the two has no creator recorded, which in practice is an anonymous copy after a named painter.

{{hands}}

So among the 132 pairs with the same composition: 89 same hand, 21 other hand, 22 anonymous.

{{copies}}

AUC is the probability that an other-hand copy sits farther from its original (as a ratio to the nearest unrelated painting) than a same-hand version does. 0.5 means the block cannot tell.

- Subject blocks rank both kinds first and cannot tell them apart (0.50 to 0.53; 0.56 to 0.60 with the anonymous copies added). That is what a subject block should do.
- CSD style separates them weakly (0.63, p = 0.07; 0.67, p = 0.002 with the anonymous copies), and its residual a little better (0.68, p = 0.009; 0.70). `meanstd_mid` ⟂ `cls` reaches 0.61 to 0.64. The second-order statistics do not (0.52).
- The effect is in the right direction and small: 21 other-hand pairs. And a copy by another hand also differs in size, support, condition and photograph, so this cannot be credited to the hand alone.

### CSD style, CSD content, plain CLIP

{{csd_heads}}

CSD's two heads give the same neighbours (9.1 of 10; 8.7 of 10 on the raw 768-dimensional vectors with no PCA). Every column in every table is the same for `style` and `content` to two digits, and `style` ⟂ `content` is noise. On this corpus the content head is not a subject block and the style head is not separated from it. CSD is about as far from plain CLIP as SigLIP 2 is from DINOv2 (3.3 of 10 shared). Against plain CLIP, CSD is worse at subject (version top-1 0.53 against 0.87), slightly worse at painter (0.86 against 0.89), and no better on the describer's scales. Caveat from `features/RUNS.md`: the CSD re-implementation was not checked against the authors' code on the same image.

## Part C. Are the blocks different?

{{redundancy}}

- Raw subject (S-dino) and raw CSD (M-csd): 1.7 neighbours in 10 shared, CKA 0.55, and 43 to 57 per cent of each predictable from the other. Different lists, half-shared geometry.
- Raw subject and second-order statistics (M-stats): 1.05 in 10 shared, CKA 0.24. The lists differ most here, but the tables above say the statistics lists are a noisier subject list and not a manner list.
- The residual pairs share under 0.5 in 10 and have CKA near zero, by construction.
- Colour and composition are close to independent of everything (0.2 to 0.8 shared in 10) and of each other (0.28). CSD is the block most entangled with colour (R² 0.53 of colour from CSD; 0.19 from DINOv2 `cls`).
- SigLIP 2 and DINOv2-L `cls` share 3.3 in 10.

## Part D. Leaks

{{leak_main}}

{{leak_res}}

Neighbour-list statistics:

{{neigh_main}}

{{neigh_res}}

Which leaks matter.

- **Year is the large one, and every learned block has it.** The neighbours of a painting under DINOv2-L `cls` are a median 62 years from it, against 179 for random paintings. Under SigLIP 2 it is 36, CSD 28, CLIP 22. A linear probe reads the year of an unseen painter's work with R² 0.55 (DINOv2), 0.73 (SigLIP 2), 0.74 (CSD), 0.81 (CLIP). The first four principal components of CLIP correlate with year at up to 0.74; of DINOv2 at 0.45. Elgammal's 0.69 to 0.81 is reproduced for the text-trained models. Much of this is honest: a 15th-century panel looks like one. But the text-trained models carry roughly a third more than the picture-only model does.
- **Painter.** 12 per cent of DINOv2's top-10 neighbours are by the same painter (chance 1.1 per cent), 18 per cent of SigLIP 2's, 25 per cent of CSD's, 26 per cent of CLIP's. Probe accuracy over 53 painters: 0.39, 0.50, 0.61, 0.63.
- **Fame through the back door: present in CLIP and CSD, marginal in SigLIP 2, absent in DINOv2.** For unseen painters, log sitelinks is predicted with R² 0.11 from CLIP, 0.07 from CSD, 0.03 from SigLIP 2 and -0.06 from DINOv2-L (the random block is at -0.07). Within a painter, the probe ranks that painter's works by fame at ρ 0.31 (CLIP), 0.27 (CSD), 0.22 (SigLIP 2), 0.21 (DINOv2 `cls`), 0.15 (DINOv2 `patch_mean`), 0.02 (colour). So some of "which of a painter's works are famous" is visible in the picture (DINOv2 gets 0.15 to 0.21 with no text), and CLIP adds about 0.1 on top. The SigLIP 2 number does not show a fame leak on this probe; the contact sheets do (seeds 4 and 7 below).
- **Museum: no evidence of a photography signature.** Inside the European stratum a block predicts the museum at 0.19 to 0.36, but year and country alone predict it at 0.40, and adding any block to those moves it by 0.03 at most (standard error 0.02). Marginal at best. This is one stratum, ten museums and a linear probe on 16 dimensions.
- **Tradition** is readable from every learned block (balanced accuracy 0.28 to 0.50 on seven classes; chance 0.14) and that is not a leak: ink on silk does not look like oil on canvas.
- **Hubness** is mild for tokens and heads (skew 0.8 to 1.1, about 1 per cent of paintings in nobody's top 10) and bad for second-order statistics (skew 2.5 to 2.7; one painting in 110 lists) and for their residuals (4.5).
- The residual subject block (DINOv2-L `cls` ⟂ CSD style) is the cleanest block measured: painter probe 0.15, year at the floor, year gap 110 of 179, painter repeats 7 per cent, fame R² at the floor. It pays for that in subject (Part B) and by eye (Part F).

## Part E. Ablations

Columns as above; "copies AUC" includes the anonymous copies.

View and model size:

{{abl_view}}

PCA dimension and whitening:

{{abl_dim}}

Pre-treatment of statistics parts, and the width of the nuisance in the residuals:

{{abl_other}}

- **View**: the three views are within 0.03 of each other on every column, with no consistent winner. `tile` is marginally ahead for DINOv2-L, CLIP and CSD (version top-1 0.92 against 0.87 for CLIP). The pilot is mostly near-square paintings and the strips were excluded, so this set cannot say much about views.
- **Model size**: large over base by 0.03 on genre and 0.02 on version top-1 for `cls`; no difference for the statistics parts.
- **PCA dimension**: 32 and 64 and 128 are within 0.01 on neighbour measures. 16 loses version top-1 (0.89 to 0.69). More dimensions raise the painter probe (0.27 at 16, 0.42 at 128 for DINOv2) because the probe has more to read, not because neighbours change.
- **Whitening** lowers hubness a little and lowers everything else: genre by 0.04, painter AUC by 0.09, and the describer correlations by half. It does not reduce the year leak (0.36 to 0.39 of random). Not worth it.
- **Statistics pre-treatment** (z-score, L2, none) makes no difference. Log-Euclidean Gram is slightly better than raw Gram.
- **Residual width**: regressing out 32, 64 or 128 dimensions of the nuisance trades subject for cleanliness monotonically. At 128, DINOv2 `cls` ⟂ CSD has genre P@10 0.35 and the painter probe at 0.09.

## Label-assisted removal (uses labels to build the vector)

The one place labels shape a vector. Least-squares concept erasure (whiten, project out the directions that covary with the label, unwhiten) fitted on half of the painters (862 paintings, 39 painters with 5 or more works) and evaluated only on the other half (1,110 paintings), next to the untouched vector on that same half. "LA" marks the label-assisted rows.

{{label_assisted}}

- **Removing year (2 directions) removes the linear probe and not the leak.** Year R² goes to zero; the year gap of neighbours barely moves (DINOv2 0.30 to 0.34 of random, SigLIP 2 0.18 to 0.23, CLIP 0.11 to 0.14). The period is in the local structure of the space, not along a direction. Subject is untouched (genre 0.58 to 0.57).
- It does bring the painter-across-genres AUC down to its within-30-years value (DINOv2 0.72 to 0.63, CLIP 0.91 to 0.83): the part of "same painter" that was "same period" is what a year direction can remove.
- **Removing painter (38 of 64 directions) costs too much.** Genre falls from 0.58 to 0.45 and version top-1 from 0.89 to 0.79 for DINOv2, and unseen painters are still found (CLIP 0.67).
- Not recommended. The year variant is harmless and nearly useless; the painter variant damages the subject block. A filter in the interface ("not this painter again", "any period") does the job without touching the distance, as the framework already says.

## Part F. Looking

24 fixed seeds, chosen by hand from the metadata before any sheet was made, to cover periods, traditions, genres and degrees of abstraction:

{{seeds}}

One sheet per seed (`data/painting2vec/exp_separation/sheet_NN_<qid>.jpg`): the seed on the left, eight nearest neighbours per row, eight rows, no names. Neighbour ids are in `results/sheets_neighbours.json`. Rows:

{{sheets}}

The pairings looked at: A with D (both DINOv2, no text, no labels: the framework's first choice); A with F (DINOv2 for subject, CSD for manner); C with G (the residual pair); B with E and H (SigLIP 2 for subject, mid-layer statistics for manner).

### What the rows show, by block

**A, DINOv2-L `cls` as subject.** In 16 of 24 seeds the row shares what is depicted and the handling varies visibly. Botticelli's *Birth of Venus* gets standing nudes by the sea from Bouguereau, Cabanel, Titian and a Leonardo drawing. The Persian drawing of a lion and a deer gets animals from Rousseau, a Japanese elephant screen, a Mughal page and a Chinese ox. *The City Rises* gets Bruegel's rebel angels, a Rubens hunt and *Liberty Leading the People*: turbulent masses of bodies. Cézanne's onions get still lifes by Caravaggio, Manet, Gauguin and Van Gogh. The *Girl with a Pearl Earring* gets heads in headdresses from Van Eyck, Rogier, Manet and Van Gogh. In the other 8 the row is also the seed's painter or tradition, because in this set that subject only comes in that handling: gold-ground Madonnas, Chinese ink landscapes, a Korean scroll on brown silk, Klimt, Van Gogh's cypresses, Bruegel's snow scenes (six of the eight are Bruegels), Friedrich's empty shore, Parisian café crowds.

**B, SigLIP 2 as subject.** The same kind of list as A, with more of the seed's own painter (all 8 of *The Starry Night*'s neighbours are Van Goghs, including *Irises* and *Almond Blossom*, which share nothing depicted) and with links that are reputation and iconography, not appearance. The *Mona Lisa*'s neighbours include *The Starry Night*, a Van Gogh self-portrait and the *Girl with a Pearl Earring*. The *Girl with a Pearl Earring*'s first, second and fifth neighbours are three versions of the *Mona Lisa*. Bouguereau's *Birth of Venus* gets other Births of Venus and Botticelli's gets *Primavera*: SigLIP 2 knows the name of the scene. For Turner's *Rain, Steam and Speed* the SigLIP 2 row (Goya's dog, Friedrich's monk, *The Slave Ship*) is closer to a manner row than a subject row.

**D, DINOv2-L second-order statistics as manner.** The best cross-painter handling matches on the sheets are in this row, and so are the worst misses. Good: *The City Rises* gets six Van Goghs and Boccioni's cyclist, all broken directional strokes in high colour, none sharing its subject. Turner gets two more Turners, then Friedrich, Whistler, Aivazovsky, Kuroda's volcano and Goya's dog: forms dissolved in atmosphere, by five other painters. The Persian drawing gets flat, outlined, patterned pages from Persia, India and an icon. Hokusai's tiger gets flat linear pictures from four traditions, Botticelli's *Venus* among them. Caravaggio gets candlelit dark scenes. Klimt's *Kiss* gets a Byzantine mosaic fragment and gold-ground screens. That is 9 seeds. In the rest the row matches scene type and density, not handling: the *Grande Jatte*, the *Moulin de la Galette* and *The Hunters in the Snow* all get "many small figures" (Bruegel's proverbs, altarpiece triptychs, Zoffany's *Tribuna*), and Seurat's dots get no dotted neighbour. Empty seas get empty seas, as under A.

**E, DINOv2-L `meanstd_mid`.** Between A and D. For Cézanne's still life it returns six Cézannes across subjects (the boy in the red waistcoat, a portrait, Mont Sainte-Victoire, bathers), which is his handling and nothing else. For most seeds it is a subject row with the period tightened.

**F, CSD style as manner.** In 16 of the 19 European seeds the row is the seed's painter and school across subjects: four Botticellis for the *Birth of Venus* (*Venus and Mars*, an annunciation, a nativity, a centaur), three Leonardos and three Raphael Madonnas for the *Mona Lisa*, six Caravaggios, four Vermeers, six Seurats, eight Van Goghs, eighteenth-century court portraits for *The Swing*, Romantic history painting for the *Third of May*. The handling is shared because the hand is. Where the painter is rare in the set it has less to say: *The City Rises* gets a mixed nineteenth-century row. For non-European seeds it returns the tradition and the support (Japanese gold-ground screens for the Persian drawing on gold). Median year gap on the sheets: 19 years, against 96 for row A.

**C and G, the residual pair.** C (subject with CSD regressed out) is the row that most often does what the subject lens is meant to do: the *Grande Jatte* gets standing women in full skirts from Goya, Liotard, Vermeer and Klimt; *The Starry Night* loses half its Van Goghs for a Japanese wave screen, El Greco's Toledo and a rainbow landscape; *The Hunters in the Snow* gets a Chinese mountain scroll. But for about half the seeds it falls apart after two or three neighbours (Caravaggio, Ruisdael, Fragonard, Goya, Klimt, the Mughal page): when the seed's look is most of what the embedding had, removing the look leaves noise. G (CSD with subject regressed out) is coherent for painters with an unmistakable hand (Seurat 5 of 8, Van Gogh 7, Cézanne 4, Klimt 6; Goya gets two Goyas, a Delacroix and a Turner) and for the Mughal page, and is unrelated pictures for 14 seeds (a Giotto Madonna gets *Watson and the Shark* and a Boucher). **H** (`meanstd_mid` residual) is unrelated pictures for 19 seeds.

### Where the rows collapse into one list

Seeds 1 (Giotto), 21 (Chen Shizeng), 24 (the Korean grapevine), 19 (Klimt) and 12 (Friedrich) give the same kind of picture in rows A to F. Gold-ground altarpieces, ink landscapes, scrolls on brown silk: subject, handling, support and tradition are one cluster in this set, and no pair of blocks pulls them apart. For these, a subject lens and a form lens will show the same list whatever the features.

### Verdict by pairing

| pairing | subject rows share what is shown, handling varies | manner rows share handling across subjects | collapse |
|---|---|---|---|
| A + D (DINOv2 `cls` + second-order statistics) | yes, 16 of 24 | sometimes, 9 of 24; otherwise scene type and density | 5 seeds |
| A + F (DINOv2 `cls` + CSD style) | yes, 16 of 24 | yes in the sense of same painter and school, 16 of 19 European seeds; not handling across painters | 5 seeds |
| C + G (the two residuals) | when it works it is the best subject row (about 11 of 24), otherwise noise | only for six or seven distinctive painters | none, but half the rows are unrelated pictures |
| B + E or H (SigLIP 2 + mid-layer statistics) | yes, with more same-painter and reputation links | E is a second subject row; H is noise | 5 seeds |

### Limits of this looking

One viewer, a model, looking at 160 px thumbnails. At that size finish and brushwork are not visible, so "shares handling" here means tonality, contour, flatness and stroke direction at the scale of the whole picture. I recognised most of the European paintings and their painters, which is how "five Botticellis" got counted; a viewer who did not know them would have had to judge handling by eye alone and might have scored row F lower or higher. No names were on the sheets, but I chose the seeds and knew the row order. The counts above are my judgement and were not repeated.

## Recommendation

**Subject block: DINOv2-L `cls`, `tile` view (or `pad`), L2, centre on the canon mean, PCA to 64, no whitening, cosine distance.** Call it the picture block, because it is not only subject: it carries period (year R² 0.55) and some painter (12 per cent repeats). It is the block whose neighbours share what is depicted in the tables (genre 0.57, version top-1 0.89, checklist 0.43) and on the sheets (16 of 24). Joining `patch_mean` to it is worth trying by eye; it follows the describer's checklist better (0.52) and `cls` follows genre better.

**A text-trained encoder is not needed for subject.** SigLIP 2 buys 0.04 on genre and 0.012 on depicts, both of them labels written with knowledge of the painting, and nothing on version pairs or the describer's checklist. It costs: painter probe 0.50 against 0.39, year R² 0.73 against 0.55, neighbours 36 years away against 62, painter repeats 18 per cent against 12, and reputation links visible on two of 24 sheets. CLIP is worse on every leak (fame R² 0.11).

**Manner block: none of the candidates. Do not ship one yet.**

- CSD is not worth its leak. What it adds over DINOv2 is the painter and the decade, which the root framework lists under "never part of a distance". It does not follow abstraction, contour or finish better than DINOv2 `cls` (0.19 against 0.18). Its style and content heads are one block here. Plain CLIP does the same job slightly better.
- Gram-style statistics from DINOv2 are not worth shipping either, for the opposite reason: they leak least (year R² 0.20 to 0.33) because they carry least. They follow the manner scales worse than `cls` (0.09), find the painter across genres worse than `cls` (0.65 against 0.72), and have the worst hubness. Nine good rows in 24 is the case for them, and it is a case for looking further, not for shipping.
- The honest comparison is that CSD finds the hand and the statistics find the texture of the whole picture, and neither finds manner as the framework defines it.

**Is the split real?** Partly, and not as drawn.

For: the lists differ (1 to 2 shared in 10); the subject rows do vary in handling; CSD rows do hold handling across subjects; a linear residual can make a subject block that is at chance for the painter and a second block that finds the painter across genres at 0.70 with genre near chance; CSD ranks other-hand copies farther than same-hand versions.

Against: the second block in every one of those is painter and period, not manner; on the only direct measure of manner (the describer's scales, n = 60) the manner candidates add nothing to the subject block; half of each raw block is predictable from the other; the residual manner rows are unrelated pictures for most seeds; and for a fifth of the seeds subject, handling and tradition are one cluster.

**What the design should change.**

1. Four content blocks become three now: picture (DINOv2-L), colour, composition. The whole-picture lens is all three; the subject lens is the picture block alone; the form lens is colour and composition; the colour lens is unchanged. That form lens already puts a landscape next to an abstraction without any learned style model, and colour and composition are close to independent of the picture block (0.3 to 0.4 shared in 10) and of each other.
2. Manner comes back as an explicit, measured block or not at all. Two routes, both untested here: (a) the describer's manner scales themselves (abstraction, contour, finish, detail, depth), which the describer study found repeatable at ICC 0.90 to 0.96, as a five-number predicted block; (b) direct texture measures on full-resolution tiles (stroke scale, edge sharpness, local contrast), the direction the composition block's `edges` and `spectrum` parts already point. Either would be a block whose meaning is stated, which a learned style embedding is not.
3. Rename. If a learned second block is ever added, it should not be called manner unless it passes the describer test with subject held fixed. `meanstd_mid` from DINOv2-L is the candidate to try first (painter across genres 0.74, no text, no labels), under a name like "surface".
4. An "across periods" subject lens (DINOv2 `cls` ⟂ a period-heavy block) is possible and is the cleanest block measured, but it uses CSD as the thing removed, loses a fifth of the version pairs, and fails by eye for half the seeds. Keep it as an experiment.
5. Period should be handled where the framework already puts it: as a filter. Linear removal does not take it out of the neighbour lists.

## Solid, marginal, not tested

Solid (large effects, consistent across measures and with the sheets):

- First-order tokens carry more subject and more painter than second-order statistics at every layer.
- Text-trained encoders carry more painter and year than DINOv2; CLIP and CSD carry the most.
- CSD `style` and `content` are the same block on this corpus.
- Every learned block ranks a second version of a composition first; colour does not.
- Linear residuals move painter retrieval to chance on the subject side and keep it on the other side.
- Year is in the neighbour lists of every learned block and a linear projection does not remove it.

Marginal (small, or one measure, or small n):

- The copies test: right direction, 21 other-hand pairs, p between 0.07 and 0.002 depending on whether anonymous copies count, and confounded with photograph and condition.
- Everything from the describer's 60 paintings. Correlations of 0.1 to 0.2 with a null spread of 0.03 are real but small, the abstraction scale has almost no range, and the describer is a model that recognised most of the paintings.
- Fame: CLIP's R² of 0.11 is clear, SigLIP 2's 0.03 is not; the within-painter gap between CLIP and DINOv2 is about three standard errors.
- Museum: nothing found, with a weak test.
- View, model size, PCA dimension: differences of 0.01 to 0.03.
- All the sheet counts.

Not tested:

- Any human judgement. No odd-one-out, no second viewer.
- Brushwork at a resolution where it exists. Every encoder saw 224 px; `tile` only helps elongated paintings.
- Non-linear separation (adversarial removal, a trained disentangler), CCA or partial least squares in place of ridge residuals, and any combination of blocks into a weighted lens.
- SigLIP 2 large or NaFlex, DINOv3, and CSD run with the authors' own code.
- The describer's manner scales or direct texture measures as a block, which is what the recommendation leans on.
- Robustness to the photograph (experiment 2), and whether the residual blocks survive it.
- A held-out set. Candidates, pairings and seeds were chosen on the same 2,000 paintings the tables describe.
- The 28 excluded images, and what any block does with a handscroll.

## Files

| file | what |
|---|---|
| `lib.py` | paths, metadata, exclusions, derived parts, treatments (with a cache in `data/painting2vec/exp_separation/cand/`), residuals |
| `cands.py` | default pre-treatment per part, composites, residual helper |
| `evals.py` | every measure; the only place labels are read for scoring |
| `run_sweep.py` | stage 1: every stored and derived part in the `pad` view |
| `run_stage2.py` | stage 2: composites and residuals |
| `run_stage3.py` | `abl` ablations, `red` redundancy, `null` permutation null, `lab` label-assisted removal, `csd` CSD heads |
| `sheets.py` | the 24 contact sheets and `results/seeds.csv`, `results/sheets_neighbours.json` |
| `report.py`, `README.tmpl.md` | tables and this file |
| `show.py` | prints columns of `results/metrics.json` at the terminal |
| `results/metrics.json` | every candidate, every measure |
| `results/all_candidates.md` | the same as tables |
| `results/redundancy.json`, `label_assisted.json`, `csd_heads.json`, `mantel_null.json`, `setup.json` | the other tables' sources |

Run from the repository root, one at a time (peak memory about 0.6 GB as measured on the two largest steps; the whole thing takes about ten minutes):

```
U="uv run --no-project --with numpy --with pandas --with scipy --with scikit-learn --with matplotlib --with pillow python experiments/painting2vec/exp_separation"
$U/run_sweep.py; $U/run_stage2.py
$U/run_stage3.py abl; $U/run_stage3.py red; $U/run_stage3.py null; $U/run_stage3.py lab; $U/run_stage3.py csd
$U/sheets.py; $U/report.py
```
