# Describer study: can a model mark felt words and subject tags from the picture alone?

Run 8 October 2026 for experiment 3 of `src/art2vec/painting2vec/FRAMEWORK.md` (section 9) and for the tags-only question. Nothing here is committed. Stimuli are in `data/painting2vec/describer/` (gitignored).

The describer is Claude (Opus 5.5), run as 20 separate subagents that each viewed 12 image files and wrote one JSON file. No other model was used and nothing was loaded locally.

## Answers

**Q1. Is a predicted felt block viable?** Repeatable, yes. Shown to be reading the picture and not the reputation, no: this study could not test it, and the test the framework proposes cannot work with this describer.

- Two independent describers given the same picture agree closely. Per felt word, ICC is 0.82 to 0.97 (median 0.92), exact agreement 86 per cent, mean difference 0.15 of a point on a 0 to 3 scale (T1). A painting's 24-word profile from one describer is nearer to the same painting's profile from the other than to any of the other 59 paintings in 58 of 60 cases (T5).
- Telling the describer the title, painter and year changes nothing measurable. The told presentation differs from a plain one by 0.139 per word; two plain presentations differ by 0.145 (T6). No word shifts after correction for 24 tests; the largest is `uneasy`, down 0.11 (p = 0.01 uncorrected).
- That null is not reassuring, because the describer already knows the name. It named the painting and the right painter, unaided, for 49 of 60 paintings in all three untold presentations: 20 of 20 famous, 19 or 20 of 20 mid, and 8 of 8 from the floor of the sitelink-rank stratum (8 Wikipedia sitelinks). 148 recognitions were claimed and none named the wrong painter (T7). Only the non-European paintings with two sitelinks or fewer went unrecognised (10 of 12).
- Mirroring with a 6 per cent crop did not reduce recognition at all (same counts, same confidence), and felt marks under mirroring are as close to the original as a retest is (T5, T6). So the check in framework section 4 ("do the felt words change when the picture is mirrored or cropped into something it no longer recognises") has no unrecognised arm. With this describer, a painting with a Wikipedia article cannot be made unrecognisable by a transformation that keeps its mood.
- For the 10 paintings never recognised, telling the name also moved nothing beyond noise (0.096 against 0.108, T8). That is the one clean case and it is 10 paintings.
- Recognised paintings get more felt marks (sum of 24 ratings 18.1 against 12.9) and more `tender`, `intimate`, `warm`, `hopeful` (T9). This cannot be read as reputation: the unrecognised set is ink landscapes, manuscript leaves and court portraits, and the recognised set is mostly European figure painting. Within the 48 rank-stratum paintings, fame against felt intensity is rho = 0.19, p = 0.19.
- Felt marks are not a re-encoding of colour or darkness. Leave-one-out R² from measured colour statistics is below zero for 22 of 24 words, and from another describer's colour marks it is about zero (mean -0.03), against 0.82 from another describer's mark of the same word (T11). They do follow subject: `alarming` with a dead or wounded body (rho 0.76), `still` with crowding (-0.64), `energetic` with a crowd (0.62), `festive` with a musical instrument (0.61), `calm` with the number of people (-0.60) (T11b). Part of the felt block is the subject block seen again; how large a part needs more than 60 paintings to say.

**Q2. Is a tags route viable?** Yes for controlled fields, and it is much denser than Wikidata depicts. It still needs a model to look at the image.

- The 46-item checklist repeats almost exactly: pooled kappa 0.96, 43 of 46 items at kappa 0.8 or above, mean Jaccard 0.94 between two describers (T3). People count agrees in 98 per cent of paintings, animal count 98, setting 92 (T4). Manner, colour and composition scales have ICC 0.89 to 0.98 (T2).
- Free tags do not repeat: Jaccard 0.44 between two describers on the same picture (T4). Use the controlled fields only.
- Free text stayed at the first level. One painting's records put a name in `main_action` or `tags` ("crucifixion", 3 of 240 records), although the describer knew what nearly every scene was (T10). The name list searched is in `04_analyse.py` and is not exhaustive.
- Against Wikidata depicts (52 of 60 paintings have any): only 45 per cent of depicts statements name a visible thing that maps to the checklist. The rest are identities (Lisa del Giocondo, Saint Barbara), body parts, and ideas (beauty, sadness, Wanderlust). Of the 158 that map, the describers marked 149 (recall 0.94). Of the 9 misses, 4 are my mapping (glade, girl, bodyguard, oil lamp), 1 is a doubtful depicts statement (robed skeletons entered as "monk"), 1 is arguable (bed, where only sheets show), and 3 are small details in the Bosch triptych that a 1,024 px file does not resolve. None is a clear describer error.
- The describers made 461 marks on those categories and depicts confirms 149 (32 per cent). I opened 5 of a random 14 of the unconfirmed marks and all 5 were plainly in the picture (a crucifix, a river, trees, a horse, armed figures). Depicts is incomplete by roughly a factor of three on visible things, and it is thinner still off the canon (13 of 20 obscure paintings have any, 20 of 20 famous).

**Recommendation.**

- Tags route: worth building. Controlled checklist, counts, setting and the fixed scales; no free tags. Check first whether "cannot process the image" really applies, because a tags route built on Wikidata depicts alone would be about a third as dense and would mix in identities the framework excludes.
- Predicted felt block: do not build on it yet. It is stable enough to be a block. What is missing is any evidence that it tracks what people feel, and any way of showing it is independent of reputation for the paintings the library is mostly made of. Two things would settle it: agreement with ArtEmis, and a run on paintings the describer cannot know.

## What this study cannot show

- One model family is the describer and its only comparison. High test-retest is self-consistency. It is not agreement with people, and two samples of one model can share the same error.
- No human felt-response ground truth was available. ArtEmis was not on the machine. Nothing here says the felt marks are right.
- n = 60, and only 10 unrecognised paintings, all from the non-European strata. Recognition, tradition and subject type are confounded.
- The redundancy check has 60 paintings against up to 61 predictors. "Not predicted from manner and subject" is weak; "not predicted from five colour marks" is fair.
- Blinding was by instruction. Describers were told to open only their manifest, the instrument and their 12 images; the key and the metadata were on the same disk. The pattern of recognition argues against peeking (non-European obscure works stayed unrecognised and their centuries were sometimes wrong), but it was not enforced.
- Each describer saw 12 pictures in one session, so marks may be anchored by the rest of the batch.
- Every depicts adjudication is mine, from the picture, on a small sample.
- The "obscure" European paintings are not obscure. The pilot's rank stratum has a floor of 8 sitelinks, and the describer knew all 8.

## Design as run

**Sample** (`01_sample.py`, seed 20261008, `sample.csv`). 60 paintings from the pilot with a title and a year, aspect ratio 0.5 to 2.0, short side at least 450 px, mean channel spread at least 8 of 255 (drops greyscale files).

- famous, 20: top of the rank stratum by sitelinks (43 to 134), at most two per painter.
- mid, 20: rank stratum, 12 to 20 sitelinks, drawn at random, one per painter.
- obscure, 20: two per non-European stratum with two sitelinks or fewer (12), plus 8 drawn at random from the rank stratum's floor of 8 sitelinks. Reported as two groups throughout.

**Stimuli** (`02_stimuli.py`, `key.csv`). Four presentations per painting, each re-encoded from pixels only under a random seven-character name:

- `orig`: the picture as stored.
- `retest`: the same pixels under another name, for a different describer.
- `mirror`: 6 per cent cropped from each edge, then flipped left to right.
- `told`: the picture as stored, with title, painter and year given in the manifest ("unknown" where Wikidata has no painter).

**Batches.** 20 batches of 12, one describer each, two running at a time. Every batch holds three presentations of each kind, one from each fame level, and never two presentations of one painting.

**Instrument.** `instrument.md`, the same for every describer, reproduced below. Output validated by `03_validate.py`.

**Changes to the draft design.**

1. Conditions are mixed inside every batch. In the draft, a describer per condition would have confounded describer with condition. Cost: every describer saw three told items.
2. The recognition question comes last, so naming the painting does not precede the marks.
3. Six scales added to manner: saturation, colour temperature, contrast, crowding, symmetry, closeness.
4. Colour statistics measured from the pixels (`image_stats.csv`), so the redundancy check does not rest on the describer's own colour marks.
5. In the redundancy check the predictors come from a different describer than the felt marks, so a describer's own consistency is not counted as prediction.
6. The obscure group is split, because the rank-stratum floor turned out not to be obscure.

**Failures.** None. 20 of 20 batches returned valid JSON at the first attempt; 240 of 240 records.

## Files

| file | what |
|---|---|
| `01_sample.py`, `sample.csv` | the sample |
| `02_stimuli.py`, `key.csv`, `image_stats.csv` | stimuli, the code-to-painting key, measured colour |
| `instrument.md`, `descriptors_draft.csv` | the instrument and the draft four-kinds table |
| `03_validate.py`, `raw/batch_00.json` to `batch_19.json` | validator and the raw describer output |
| `04_analyse.py`, `tables.md`, `records_long.csv` | analysis, its printed tables, one row per record |
| `depicts_disagreements.csv`, `recognition_by_painting.csv` | every checklist/depicts disagreement; recognition per painting |

## Example outputs

Felt marks are shown as word and rating; zeros are left out.

Mona Lisa (famous, recognised in every presentation)

| presentation | main_action | felt |
|---|---|---|
| orig | woman sits with folded hands, faintly smiling | calm3 tender1 eerie1 melancholy1 awed1 intimate2 solemn1 sensual1 dreamlike2 still3 warm1 mysterious3 |
| retest | seated woman faces viewer, hands folded | calm2 tender1 eerie1 awed1 intimate1 solemn1 dreamlike1 still2 warm1 mysterious3 |
| mirror | seated woman with folded hands looks at viewer | calm3 tender1 eerie1 melancholy1 awed1 intimate2 solemn1 sensual1 dreamlike2 still3 warm1 mysterious3 |
| told | seated woman faces viewer, hands folded | calm3 tender1 eerie1 intimate2 solemn1 dreamlike1 still2 warm1 mysterious3 |

Rainy Landscape with Travelers (Korean stratum, never recognised)

| presentation | main_action | felt |
|---|---|---|
| orig | tiny travellers walk beneath misty peaks | calm3 eerie1 desolate2 melancholy2 awed2 solemn2 lonely2 dreamlike3 still3 cold1 mysterious3 |
| retest | tiny travellers cross footbridge beneath misty peaks | calm2 eerie1 desolate1 melancholy2 awed1 solemn1 lonely2 dreamlike2 still3 cold1 mysterious3 |
| mirror | tiny travellers walk beneath misty peaks | calm3 eerie1 desolate2 melancholy2 awed2 solemn2 lonely2 dreamlike3 still3 cold1 mysterious3 |
| told | tiny figures cross below misty peaks | calm2 eerie1 desolate2 melancholy2 awed1 solemn2 lonely2 dreamlike2 still2 cold2 mysterious3 |

The Blood Compact (Juan Luna, never recognised). The one case I found where the title changed what was seen: untold, the describers saw men round a document; told the title, the describer saw a cup raised.

| presentation | main_action | felt |
|---|---|---|
| orig | armoured men gather round a document on table | tense2 eerie1 uneasy2 intimate1 solemn3 oppressive2 energetic1 still1 cold1 mysterious2 |
| retest | armoured men gather round document on table | tense2 eerie1 uneasy1 solemn2 oppressive1 energetic1 mysterious2 |
| mirror | armoured men gather round a document on table | tense2 eerie1 melancholy1 uneasy2 solemn3 oppressive2 still2 cold1 mysterious2 |
| told | bearded man raises cup at a table | tense2 eerie1 uneasy1 solemn2 oppressive1 still1 cold1 mysterious2 |

Free tags often describe the object and not the picture ("ink on silk", "hanging scroll", "brocade mount", "craquelure"). Several pilot files include the scroll mount or a frame, and the describer marks it.

One complete record (Rainy Landscape with Travelers, `orig`):

```json
{"code": "eslg3rv", "felt": {"calm": 3, "tense": 0, "tender": 0, "eerie": 1, "festive": 0, "desolate": 2, "joyful": 0, "melancholy": 2, "awed": 2, "uneasy": 0, "intimate": 0, "playful": 0, "solemn": 2, "alarming": 0, "sensual": 0, "lonely": 2, "hopeful": 0, "oppressive": 0, "dreamlike": 3, "energetic": 0, "still": 3, "warm": 0, "cold": 1, "mysterious": 3}, "subject": {"people": "3-5", "animals": "0", "setting": "landscape", "things": {"sky": 1, "clouds": 0, "sun_or_moon": 0, "water": 0, "trees": 1, "mountains_or_hills": 1, "rocks": 1, "field_or_grass": 0, "flowers": 0, "fruit_or_food": 0, "snow_or_ice": 0, "fire_or_smoke": 0, "buildings": 0, "window_or_door": 0, "furniture": 0, "bridge": 1, "road_or_path": 1, "boat_or_ship": 0, "cart_or_carriage": 0, "horse": 0, "dog": 0, "cattle_or_sheep": 0, "bird": 0, "fish": 0, "other_animal": 0, "man": 1, "woman": 0, "child": 0, "old_person": 0, "nude": 0, "crowd": 0, "dead_or_wounded_body": 0, "soldier_or_armour": 0, "weapon": 0, "book_or_paper": 0, "musical_instrument": 0, "vessel_or_tableware": 0, "curtain_or_drapery": 0, "hat_or_headdress": 0, "jewellery_or_crown": 0, "flag_or_banner": 0, "halo": 0, "wings": 0, "cross": 0, "skull_or_skeleton": 0, "written_text": 0}, "main_action": "tiny travellers walk beneath misty peaks", "tags": ["mist", "towering peaks", "windblown trees", "ink on silk", "hanging scroll", "tiny figures", "darkened silk", "brocade mount"]}, "manner": {"abstraction": 1, "contour": 3, "finish": 2, "detail": 1, "depth": 3, "palette_breadth": 0, "saturation": 0, "colour_temperature": 3, "darkness": 3, "contrast": 0, "crowding": 1, "symmetry": 0, "closeness": 0}, "recognition": {"recognised": false, "title": "", "painter": "", "confidence": 0, "guess_school": "East Asian ink landscape in the Southern Song academy manner (Chinese, Korean or Muromachi Japanese)", "guess_century": 15}}
```

## Tables

Printed by `04_analyse.py`. `orig` and `retest` are the two plain presentations; in every table the two members of a pair were marked by different describers.

records: 240 of 240; batches valid: 20 of 20

## T1. Test-retest, felt words (orig vs retest, two different describers, n = 60)

| item | mean | icc | spearman | w_kappa | exact | mad |
|---|---|---|---|---|---|---|
| calm | 1.01 | 0.93 | 0.92 | 0.93 | 0.85 | 0.15 |
| tense | 1.00 | 0.90 | 0.91 | 0.90 | 0.77 | 0.23 |
| tender | 0.65 | 0.94 | 0.93 | 0.94 | 0.90 | 0.10 |
| eerie | 0.48 | 0.91 | 0.88 | 0.91 | 0.90 | 0.10 |
| festive | 0.26 | 0.94 | 0.90 | 0.94 | 0.95 | 0.05 |
| desolate | 0.38 | 0.85 | 0.89 | 0.84 | 0.83 | 0.17 |
| joyful | 0.25 | 0.96 | 0.95 | 0.96 | 0.97 | 0.03 |
| melancholy | 0.83 | 0.93 | 0.94 | 0.93 | 0.87 | 0.13 |
| awed | 1.00 | 0.90 | 0.90 | 0.89 | 0.80 | 0.20 |
| uneasy | 0.94 | 0.92 | 0.89 | 0.92 | 0.85 | 0.15 |
| intimate | 0.82 | 0.93 | 0.89 | 0.92 | 0.83 | 0.17 |
| playful | 0.36 | 0.91 | 0.89 | 0.91 | 0.92 | 0.08 |
| solemn | 1.30 | 0.87 | 0.87 | 0.87 | 0.70 | 0.30 |
| alarming | 0.47 | 0.97 | 0.97 | 0.97 | 0.95 | 0.05 |
| sensual | 0.52 | 0.94 | 0.94 | 0.94 | 0.90 | 0.10 |
| lonely | 0.47 | 0.88 | 0.88 | 0.88 | 0.85 | 0.15 |
| hopeful | 0.33 | 0.82 | 0.79 | 0.82 | 0.87 | 0.13 |
| oppressive | 0.57 | 0.87 | 0.86 | 0.87 | 0.83 | 0.17 |
| dreamlike | 0.82 | 0.92 | 0.93 | 0.92 | 0.83 | 0.17 |
| energetic | 0.93 | 0.94 | 0.94 | 0.94 | 0.85 | 0.15 |
| still | 1.43 | 0.90 | 0.90 | 0.89 | 0.78 | 0.23 |
| warm | 0.58 | 0.88 | 0.77 | 0.88 | 0.83 | 0.17 |
| cold | 0.66 | 0.87 | 0.76 | 0.87 | 0.78 | 0.22 |
| mysterious | 1.11 | 0.96 | 0.96 | 0.96 | 0.92 | 0.08 |

median ICC 0.92, mean 0.91, range 0.82 to 0.97; mean exact agreement 0.86; mean absolute difference 0.15 scale points

## T2. Test-retest, manner, colour and composition scales (0-4)

| item | mean | icc | spearman | w_kappa | exact | mad |
|---|---|---|---|---|---|---|
| abstraction | 0.62 | 0.95 | 0.96 | 0.95 | 0.95 | 0.05 |
| contour | 1.08 | 0.91 | 0.93 | 0.91 | 0.80 | 0.20 |
| finish | 1.42 | 0.96 | 0.94 | 0.96 | 0.87 | 0.13 |
| detail | 2.65 | 0.96 | 0.95 | 0.96 | 0.93 | 0.07 |
| depth | 2.23 | 0.90 | 0.86 | 0.90 | 0.77 | 0.23 |
| palette_breadth | 2.04 | 0.93 | 0.93 | 0.93 | 0.82 | 0.18 |
| saturation | 1.87 | 0.94 | 0.95 | 0.94 | 0.87 | 0.13 |
| colour_temperature | 2.42 | 0.95 | 0.94 | 0.95 | 0.92 | 0.08 |
| darkness | 2.24 | 0.89 | 0.91 | 0.89 | 0.82 | 0.18 |
| contrast | 2.48 | 0.95 | 0.93 | 0.95 | 0.92 | 0.08 |
| crowding | 2.79 | 0.94 | 0.94 | 0.94 | 0.88 | 0.12 |
| symmetry | 1.27 | 0.90 | 0.89 | 0.90 | 0.82 | 0.18 |
| closeness | 1.99 | 0.98 | 0.96 | 0.98 | 0.95 | 0.05 |

median ICC 0.94, mean 0.93; mean exact agreement 0.87; mean absolute difference 0.13

## T3. Test-retest, subject checklist (Cohen's kappa per item)

| item | mean | n_pos | agree | kappa |
|---|---|---|---|---|
| sky | 0.52 | 31 | 0.97 | 0.93 |
| clouds | 0.33 | 20 | 1.00 | 1.00 |
| sun_or_moon | 0.07 | 4 | 1.00 | 1.00 |
| water | 0.21 | 14 | 0.92 | 0.75 |
| trees | 0.40 | 24 | 1.00 | 1.00 |
| mountains_or_hills | 0.33 | 20 | 1.00 | 1.00 |
| rocks | 0.28 | 17 | 1.00 | 1.00 |
| field_or_grass | 0.27 | 17 | 0.97 | 0.91 |
| flowers | 0.18 | 12 | 0.97 | 0.89 |
| fruit_or_food | 0.12 | 7 | 1.00 | 1.00 |
| snow_or_ice | 0.03 | 2 | 1.00 | 1.00 |
| fire_or_smoke | 0.08 | 5 | 1.00 | 1.00 |
| buildings | 0.33 | 20 | 0.98 | 0.96 |
| window_or_door | 0.24 | 15 | 0.95 | 0.86 |
| furniture | 0.30 | 19 | 0.97 | 0.92 |
| bridge | 0.05 | 3 | 1.00 | 1.00 |
| road_or_path | 0.14 | 9 | 0.98 | 0.93 |
| boat_or_ship | 0.07 | 4 | 1.00 | 1.00 |
| cart_or_carriage | 0.02 | 1 | 1.00 | 1.00 |
| horse | 0.13 | 8 | 1.00 | 1.00 |
| dog | 0.10 | 6 | 1.00 | 1.00 |
| cattle_or_sheep | 0.02 | 1 | 1.00 | 1.00 |
| bird | 0.08 | 5 | 1.00 | 1.00 |
| fish | 0.03 | 2 | 1.00 | 1.00 |
| other_animal | 0.15 | 9 | 1.00 | 1.00 |
| man | 0.72 | 43 | 1.00 | 1.00 |
| woman | 0.57 | 35 | 0.98 | 0.97 |
| child | 0.23 | 14 | 1.00 | 1.00 |
| old_person | 0.28 | 17 | 0.98 | 0.96 |
| nude | 0.33 | 20 | 1.00 | 1.00 |
| crowd | 0.21 | 13 | 0.98 | 0.95 |
| dead_or_wounded_body | 0.25 | 15 | 1.00 | 1.00 |
| soldier_or_armour | 0.26 | 16 | 0.98 | 0.96 |
| weapon | 0.25 | 15 | 1.00 | 1.00 |
| book_or_paper | 0.17 | 11 | 0.98 | 0.94 |
| musical_instrument | 0.15 | 9 | 1.00 | 1.00 |
| vessel_or_tableware | 0.25 | 15 | 1.00 | 1.00 |
| curtain_or_drapery | 0.37 | 23 | 0.90 | 0.78 |
| hat_or_headdress | 0.68 | 41 | 0.92 | 0.81 |
| jewellery_or_crown | 0.19 | 12 | 0.95 | 0.84 |
| flag_or_banner | 0.12 | 7 | 1.00 | 1.00 |
| halo | 0.08 | 5 | 0.97 | 0.78 |
| wings | 0.10 | 6 | 1.00 | 1.00 |
| cross | 0.12 | 7 | 1.00 | 1.00 |
| skull_or_skeleton | 0.03 | 2 | 1.00 | 1.00 |
| written_text | 0.32 | 20 | 0.97 | 0.92 |

pooled over all 60 x 46 cells: agreement 0.985, kappa 0.96; per-painting Jaccard of the marked sets: mean 0.94, median 1.00; items with kappa >= 0.8: 43 of 46 that have any positive; mean marks per painting 10.2

## T4. Subject fields by pair of presentations

| pair | people_exact | people_w_kappa | animals_exact | animals_w_kappa | setting_exact | setting_kappa | checklist_kappa | checklist_jaccard | free_tag_jaccard |
|---|---|---|---|---|---|---|---|---|---|
| orig vs retest | 0.98 | 1.00 | 0.98 | 0.99 | 0.92 | 0.90 | 0.96 | 0.94 | 0.44 |
| orig vs mirror | 0.98 | 1.00 | 0.92 | 0.92 | 0.92 | 0.89 | 0.92 | 0.89 | 0.39 |
| orig vs told | 0.97 | 0.99 | 1.00 | 1.00 | 0.88 | 0.85 | 0.96 | 0.94 | 0.43 |

## T5. Whole-section agreement per painting, by pair of presentations

felt (24 words, 0-3)

| pair | profile_r | centred_r | mad_same | mad_other_painting | top1_match |
|---|---|---|---|---|---|
| orig vs retest | 0.931 | 0.913 | 0.145 | 0.897 | 0.967 |
| orig vs mirror | 0.944 | 0.931 | 0.117 | 0.899 | 0.917 |
| retest vs mirror | 0.935 | 0.916 | 0.139 | 0.897 | 0.900 |
| orig vs told | 0.933 | 0.918 | 0.139 | 0.897 | 0.933 |
| retest vs told | 0.935 | 0.924 | 0.140 | 0.895 | 0.967 |

manner (13 scales, 0-4)

| pair | profile_r | centred_r | mad_same | mad_other_painting | top1_match |
|---|---|---|---|---|---|
| orig vs retest | 0.951 | 0.928 | 0.131 | 1.089 | 0.983 |
| orig vs mirror | 0.938 | 0.908 | 0.171 | 1.095 | 0.950 |
| retest vs mirror | 0.945 | 0.921 | 0.153 | 1.093 | 0.950 |
| orig vs told | 0.947 | 0.923 | 0.137 | 1.081 | 0.950 |
| retest vs told | 0.956 | 0.932 | 0.124 | 1.077 | 1.000 |

checklist (46 items, 0/1)

| pair | profile_r | centred_r | mad_same | mad_other_painting | top1_match |
|---|---|---|---|---|---|
| orig vs retest | 0.956 | 0.946 | 0.015 | 0.296 | 0.983 |
| orig vs mirror | 0.926 | 0.912 | 0.025 | 0.287 | 0.950 |
| retest vs mirror | 0.927 | 0.913 | 0.026 | 0.287 | 0.967 |
| orig vs told | 0.955 | 0.950 | 0.015 | 0.295 | 0.967 |
| retest vs told | 0.953 | 0.946 | 0.015 | 0.295 | 0.983 |

## T6. Signed shift per felt word against the mean of the two plain presentations (n = 60)

| word | noise_mad | retest_minus_orig | mirror_shift | mirror_p | mirror_mad_vs_orig | told_shift | told_p | told_mad_vs_orig |
|---|---|---|---|---|---|---|---|---|
| calm | 0.15 | 0.02 | -0.01 | 0.80 | 0.10 | -0.07 | 0.06 | 0.17 |
| tense | 0.23 | -0.07 | 0.02 | 0.72 | 0.08 | -0.07 | 0.17 | 0.27 |
| tender | 0.10 | 0.07 | 0.00 | 1.00 | 0.10 | 0.05 | 0.29 | 0.15 |
| eerie | 0.10 | 0.00 | -0.02 | 0.53 | 0.08 | -0.03 | 0.37 | 0.13 |
| festive | 0.05 | 0.02 | 0.01 | 0.78 | 0.05 | 0.01 | 0.56 | 0.02 |
| desolate | 0.17 | 0.00 | -0.03 | 0.52 | 0.17 | 0.02 | 0.79 | 0.15 |
| joyful | 0.03 | -0.03 | 0.00 | 1.00 | 0.05 | 0.00 | 1.00 | 0.02 |
| melancholy | 0.13 | 0.00 | 0.05 | 0.29 | 0.15 | 0.00 | 0.96 | 0.13 |
| awed | 0.20 | 0.00 | -0.03 | 0.43 | 0.17 | -0.08 | 0.11 | 0.18 |
| uneasy | 0.15 | 0.05 | 0.03 | 0.58 | 0.12 | -0.11 | 0.01 | 0.15 |
| intimate | 0.17 | -0.03 | 0.00 | 0.92 | 0.18 | 0.05 | 0.20 | 0.13 |
| playful | 0.08 | -0.02 | -0.04 | 0.10 | 0.08 | 0.01 | 0.77 | 0.10 |
| solemn | 0.30 | -0.03 | 0.03 | 0.51 | 0.22 | -0.07 | 0.17 | 0.22 |
| alarming | 0.05 | -0.02 | 0.03 | 0.41 | 0.05 | 0.03 | 0.45 | 0.05 |
| sensual | 0.10 | -0.03 | 0.02 | 0.56 | 0.10 | 0.05 | 0.16 | 0.10 |
| lonely | 0.15 | 0.05 | -0.01 | 0.82 | 0.15 | 0.03 | 0.67 | 0.15 |
| hopeful | 0.13 | 0.10 | 0.00 | 1.00 | 0.08 | 0.02 | 0.56 | 0.07 |
| oppressive | 0.17 | 0.00 | 0.03 | 0.65 | 0.17 | -0.05 | 0.15 | 0.08 |
| dreamlike | 0.17 | 0.03 | 0.05 | 0.21 | 0.10 | 0.00 | 1.00 | 0.18 |
| energetic | 0.15 | -0.08 | 0.04 | 0.28 | 0.10 | -0.03 | 0.66 | 0.20 |
| still | 0.23 | 0.03 | 0.05 | 0.32 | 0.17 | -0.03 | 0.62 | 0.25 |
| warm | 0.17 | 0.03 | -0.03 | 0.47 | 0.12 | 0.02 | 0.61 | 0.13 |
| cold | 0.22 | -0.05 | 0.04 | 0.40 | 0.18 | 0.06 | 0.26 | 0.23 |
| mysterious | 0.08 | 0.02 | 0.04 | 0.16 | 0.05 | -0.04 | 0.16 | 0.07 |

mean over words of |shift|: mirror 0.025, told 0.038, retest minus orig 0.033; words with p < 0.05 (uncorrected, 24 tests each): mirror 0, told 1; with p < 0.05/24: mirror 0, told 0; mean absolute difference from orig: retest 0.145, mirror 0.117, told 0.139

Same for the manner scales

| scale | retest_minus_orig | mirror_shift | mirror_p | told_shift | told_p |
|---|---|---|---|---|---|
| abstraction | 0.02 | 0.07 | 0.02 | -0.01 | 0.75 |
| contour | 0.00 | 0.03 | 0.38 | 0.00 | 1.00 |
| finish | 0.03 | -0.05 | 0.38 | 0.00 | 1.00 |
| detail | -0.03 | -0.02 | 0.67 | -0.03 | 0.33 |
| depth | 0.00 | -0.05 | 0.28 | 0.02 | 0.64 |
| palette_breadth | 0.05 | -0.07 | 0.12 | -0.07 | 0.09 |
| saturation | -0.03 | 0.08 | 0.08 | 0.03 | 0.39 |
| colour_temperature | -0.02 | 0.06 | 0.08 | 0.03 | 0.47 |
| darkness | 0.02 | -0.04 | 0.37 | -0.01 | 0.82 |
| contrast | 0.02 | 0.01 | 0.72 | 0.01 | 0.86 |
| crowding | 0.02 | 0.17 | 0.01 | 0.03 | 0.67 |
| symmetry | -0.02 | -0.09 | 0.13 | 0.07 | 0.15 |
| closeness | 0.02 | 0.17 | 0.00 | 0.06 | 0.14 |

## T7. Recognition by fame group (untold presentations)

| group | paintings | orig_recognised | orig_right_painter | orig_conf | retest_recognised | retest_right_painter | retest_conf | mirror_recognised | mirror_right_painter | mirror_conf | century_exact | century_within_1 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| famous | 20 | 20/20 | 20/20 | 3.00 | 20/20 | 20/20 | 3.00 | 20/20 | 20/20 | 3.00 | 1.00 | 1.00 |
| mid | 20 | 19/20 | 19/20 | 2.75 | 20/20 | 20/20 | 2.85 | 19/20 | 19/20 | 2.70 | 0.93 | 1.00 |
| obscure_european_floor | 8 | 8/8 | 8/8 | 2.62 | 8/8 | 8/8 | 2.62 | 8/8 | 8/8 | 2.62 | 1.00 | 1.00 |
| obscure_non_european | 12 | 2/12 | 2/12 | 0.42 | 2/12 | 2/12 | 0.42 | 2/12 | 2/12 | 0.42 | 0.75 | 1.00 |

claimed recognitions with the wrong painter (untold): 0 of 148

recognition across the three untold presentations: recognised 3/3: 49, never recognised: 10, mixed: 1

## T8. Effect of telling the name, split by whether the painting was recognised unaided

| paintings | n | felt_noise | felt_told | felt_mirror | felt_told_p | manner_noise | manner_told | manner_mirror | manner_told_p | checklist_noise | checklist_told | checklist_mirror | checklist_told_p |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| recognised 3/3 | 49 | 0.151 | 0.149 | 0.132 | 0.444 | 0.137 | 0.130 | 0.159 | 0.413 | 0.013 | 0.014 | 0.025 | 0.586 |
| never recognised | 10 | 0.108 | 0.096 | 0.113 | 0.406 | 0.100 | 0.127 | 0.173 | 0.469 | 0.017 | 0.020 | 0.026 | 0.812 |
| mixed | 1 | 0.208 | 0.104 | 0.104 |  | 0.154 | 0.231 | 0.154 |  | 0.065 | 0.033 | 0.054 |  |

Values are mean absolute differences per item between two presentations of one painting. noise = orig vs retest; told = told vs each plain presentation, averaged; mirror likewise. p: Wilcoxon signed-rank, told against noise.

Largest told-minus-plain shifts among never-recognised paintings

| word | never_recognised_shift | recognised_shift |
|---|---|---|
| calm | -0.15 | -0.06 |
| uneasy | -0.15 | -0.10 |
| cold | 0.15 | 0.04 |
| warm | -0.10 | 0.04 |
| still | -0.10 | -0.02 |
| energetic | -0.10 | -0.02 |
| alarming | -0.10 | 0.04 |
| tense | -0.10 | -0.07 |

## T9. Mean felt profile, recognised against never recognised (plain presentations)

| word | recognised | never_recognised | diff | p_mannwhitney |
|---|---|---|---|---|
| calm | 0.98 | 1.25 | -0.27 | 0.53 |
| tense | 0.97 | 1.00 | -0.03 | 1.00 |
| tender | 0.78 | 0.00 | 0.78 | 0.00 |
| eerie | 0.54 | 0.25 | 0.29 | 0.36 |
| festive | 0.28 | 0.20 | 0.08 | 0.96 |
| desolate | 0.42 | 0.25 | 0.17 | 0.52 |
| joyful | 0.31 | 0.00 | 0.31 | 0.13 |
| melancholy | 0.89 | 0.45 | 0.44 | 0.26 |
| awed | 1.05 | 0.80 | 0.25 | 0.56 |
| uneasy | 0.96 | 0.75 | 0.21 | 0.48 |
| intimate | 0.97 | 0.15 | 0.82 | 0.04 |
| playful | 0.38 | 0.30 | 0.08 | 1.00 |
| solemn | 1.39 | 0.80 | 0.59 | 0.10 |
| alarming | 0.45 | 0.50 | -0.05 | 0.45 |
| sensual | 0.56 | 0.25 | 0.31 | 0.20 |
| lonely | 0.48 | 0.50 | -0.02 | 0.91 |
| hopeful | 0.41 | 0.00 | 0.41 | 0.02 |
| oppressive | 0.58 | 0.45 | 0.13 | 0.52 |
| dreamlike | 0.80 | 0.95 | -0.15 | 0.56 |
| energetic | 0.86 | 1.10 | -0.24 | 0.46 |
| still | 1.47 | 1.40 | 0.07 | 0.86 |
| warm | 0.69 | 0.10 | 0.59 | 0.02 |
| cold | 0.73 | 0.35 | 0.38 | 0.32 |
| mysterious | 1.13 | 1.10 | 0.03 | 0.98 |

total felt marks per painting (sum of 24 ratings): recognised 18.1, never recognised 12.9; count of non-zero words: recognised 11.4, never recognised 8.9. By fame: famous 19.2, mid 17.5, obscure European floor 17.1, obscure non-European 13.3

## T10. Names in the subject free text (main_action and tags)

| cond | records | with_a_name |
|---|---|---|
| orig | 60 | 1 |
| retest | 60 | 1 |
| mirror | 60 | 0 |
| told | 60 | 1 |

names found: orig: crucifixion; retest: crucifixion; mirror: ; told: crucifixion

## T11. Are felt marks predictable from colour and manner? Leave-one-out R2, target = felt mark from the orig describer (n = 60)

| word | sd | measured_colour | colour_marks_other_describer | all_manner_other_describer | all_manner_same_describer | subject_marks_other_describer | manner_plus_subject_other | same_word_other_describer |
|---|---|---|---|---|---|---|---|---|
| calm | 1.08 | -0.17 | 0.01 | -0.08 | -0.10 | 0.17 | 0.45 | 0.86 |
| tense | 1.12 | -0.23 | 0.07 | 0.10 | 0.05 | 0.55 | 0.53 | 0.81 |
| tender | 0.86 | -0.15 | -0.11 | -0.27 | -0.18 | -0.21 | -0.19 | 0.88 |
| eerie | 0.76 | -0.13 | -0.05 | -0.09 | 0.03 | -0.42 | -0.44 | 0.82 |
| festive | 0.67 | -0.15 | -0.00 | -0.13 | -0.10 | 0.01 | 0.16 | 0.87 |
| desolate | 0.73 | -0.07 | -0.13 | -0.04 | 0.04 | 0.05 | 0.07 | 0.66 |
| joyful | 0.68 | -0.27 | 0.06 | -0.11 | -0.15 | -0.15 | -0.10 | 0.93 |
| melancholy | 0.99 | -0.11 | -0.12 | -0.08 | -0.12 | 0.03 | -0.19 | 0.86 |
| awed | 0.93 | -0.36 | -0.25 | 0.13 | 0.12 | -0.41 | -0.02 | 0.79 |
| uneasy | 0.99 | -0.18 | 0.03 | 0.10 | 0.04 | 0.27 | 0.16 | 0.84 |
| intimate | 1.05 | -0.04 | -0.07 | -0.02 | -0.08 | 0.22 | 0.16 | 0.85 |
| playful | 0.68 | -0.31 | -0.13 | -0.32 | -0.44 | -0.69 | -0.78 | 0.81 |
| solemn | 1.10 | -0.07 | -0.07 | -0.04 | -0.02 | 0.17 | 0.26 | 0.75 |
| alarming | 0.88 | -0.12 | -0.00 | -0.02 | -0.05 | 0.25 | 0.14 | 0.93 |
| sensual | 0.96 | -0.08 | -0.14 | -0.23 | -0.28 | 0.29 | 0.00 | 0.88 |
| lonely | 0.76 | -0.22 | 0.13 | 0.19 | 0.18 | -0.09 | -0.21 | 0.77 |
| hopeful | 0.55 | 0.12 | 0.01 | -0.13 | -0.12 | -0.37 | -0.61 | 0.69 |
| oppressive | 0.76 | -0.01 | 0.20 | 0.13 | 0.23 | 0.28 | 0.29 | 0.74 |
| dreamlike | 1.01 | -0.01 | -0.10 | 0.02 | 0.06 | -0.51 | -0.11 | 0.84 |
| energetic | 1.20 | -0.06 | -0.10 | 0.19 | 0.22 | -0.06 | 0.29 | 0.89 |
| still | 1.10 | -0.17 | 0.02 | 0.29 | 0.27 | -0.20 | 0.29 | 0.79 |
| warm | 0.80 | -0.25 | -0.01 | -0.14 | -0.21 | -0.40 | -0.45 | 0.75 |
| cold | 0.92 | 0.01 | -0.03 | -0.08 | -0.05 | -0.21 | 0.17 | 0.74 |
| mysterious | 1.06 | -0.19 | 0.09 | 0.16 | 0.08 | -1.07 | -0.24 | 0.92 |

mean over words: measured_colour -0.13, colour_marks_other_describer -0.03, all_manner_other_describer -0.02, all_manner_same_describer -0.02, subject_marks_other_describer -0.10, manner_plus_subject_other -0.02, same_word_other_describer 0.82

Describer colour marks against measured image statistics (Spearman, orig describer, n = 60): darkness vs mean luma -0.82; saturation vs mean saturation 0.32; colour_temperature vs red minus blue 0.64; palette_breadth vs hue spread 0.46; contrast vs luma sd 0.09

## T11b. Strongest single correlate of each felt word among another describer's subject and manner marks (Spearman, n = 60)

| word | first | second | third | darkness | saturation | colour_temperature | measured_luma |
|---|---|---|---|---|---|---|---|
| calm | people -0.60 | man -0.54 | dead_or_wounded_body -0.51 | 0.01 | -0.17 | -0.10 | 0.18 |
| tense | dead_or_wounded_body +0.61 | people +0.57 | crowd +0.55 | 0.08 | 0.10 | 0.17 | -0.18 |
| tender | woman +0.39 | weapon -0.39 | soldier_or_armour -0.33 | 0.04 | 0.21 | -0.11 | -0.04 |
| eerie | darkness +0.34 | skull_or_skeleton +0.33 | dead_or_wounded_body +0.29 | 0.34 | -0.17 | 0.07 | -0.19 |
| festive | musical_instrument +0.61 | soldier_or_armour +0.47 | buildings +0.42 | -0.21 | 0.38 | 0.05 | 0.10 |
| desolate | woman -0.41 | snow_or_ice +0.38 | depth +0.38 | 0.13 | -0.34 | -0.14 | 0.02 |
| joyful | saturation +0.48 | palette_breadth +0.48 | wings +0.43 | -0.24 | 0.48 | -0.11 | 0.22 |
| melancholy | weapon -0.33 | old_person +0.30 | soldier_or_armour -0.29 | 0.04 | -0.14 | -0.17 | -0.04 |
| awed | closeness -0.47 | clouds +0.41 | rocks +0.40 | 0.03 | 0.03 | 0.07 | 0.10 |
| uneasy | dead_or_wounded_body +0.54 | nude +0.49 | people +0.44 | 0.13 | -0.07 | 0.15 | -0.22 |
| intimate | sky -0.52 | closeness +0.52 | weapon -0.51 | 0.31 | 0.07 | -0.05 | -0.34 |
| playful | boat_or_ship +0.29 | vessel_or_tableware +0.27 | fruit_or_food +0.27 | -0.08 | 0.06 | -0.02 | 0.03 |
| solemn | depth +0.42 | old_person +0.34 | bird -0.31 | 0.28 | -0.07 | -0.03 | -0.30 |
| alarming | dead_or_wounded_body +0.76 | crowd +0.51 | people +0.44 | -0.16 | 0.06 | 0.30 | 0.10 |
| sensual | nude +0.45 | woman +0.42 | curtain_or_drapery +0.35 | -0.03 | 0.17 | 0.03 | 0.05 |
| lonely | people -0.38 | woman -0.38 | crowding -0.37 | -0.04 | -0.37 | -0.27 | 0.23 |
| hopeful | clouds +0.36 | sun_or_moon +0.34 | saturation +0.33 | -0.18 | 0.33 | -0.14 | 0.20 |
| oppressive | man +0.51 | crowd +0.51 | people +0.48 | 0.30 | -0.05 | 0.16 | -0.36 |
| dreamlike | trees +0.42 | closeness -0.41 | old_person -0.40 | -0.04 | -0.16 | 0.03 | 0.31 |
| energetic | crowd +0.62 | crowding +0.59 | soldier_or_armour +0.52 | -0.19 | 0.29 | 0.14 | 0.14 |
| still | crowding -0.64 | crowd -0.61 | soldier_or_armour -0.57 | 0.17 | -0.39 | -0.09 | -0.07 |
| warm | woman +0.40 | closeness +0.38 | dead_or_wounded_body -0.34 | 0.03 | 0.24 | 0.12 | -0.01 |
| cold | woman -0.40 | snow_or_ice +0.34 | contrast +0.30 | 0.23 | -0.12 | -0.24 | -0.17 |
| mysterious | palette_breadth -0.46 | darkness +0.39 | saturation -0.39 | 0.39 | -0.39 | 0.05 | -0.12 |

## T12. Subject checklist against Wikidata depicts (P180)

paintings with any depicts statement: 52 of 60 (famous 20/20, mid 19/20, obscure 13/20); statements: 482, median per painting 6; distinct labels 372, of which mapped to a checklist category 145; statements that map 219 (45%)

| category | depicts_yes | describer_yes | both | depicts_only | describer_only | single_describer_both |
|---|---|---|---|---|---|---|
| sky | 8 | 28 | 8 | 0 | 20 | 8 |
| clouds | 6 | 18 | 5 | 1 | 13 | 5 |
| sun_or_moon | 1 | 3 | 1 | 0 | 2 | 1 |
| water | 6 | 10 | 6 | 0 | 4 | 6 |
| trees | 7 | 20 | 7 | 0 | 13 | 7 |
| mountains_or_hills | 5 | 17 | 5 | 0 | 12 | 5 |
| rocks | 5 | 15 | 5 | 0 | 10 | 5 |
| field_or_grass | 3 | 14 | 2 | 1 | 12 | 2 |
| flowers | 3 | 10 | 3 | 0 | 7 | 3 |
| fruit_or_food | 6 | 7 | 6 | 0 | 1 | 6 |
| snow_or_ice | 2 | 2 | 2 | 0 | 0 | 2 |
| fire_or_smoke | 2 | 5 | 1 | 1 | 4 | 1 |
| window_or_door | 1 | 11 | 1 | 0 | 10 | 1 |
| furniture | 4 | 15 | 3 | 1 | 12 | 3 |
| bridge | 1 | 3 | 1 | 0 | 2 | 1 |
| boat_or_ship | 2 | 4 | 2 | 0 | 2 | 2 |
| cart_or_carriage | 1 | 1 | 1 | 0 | 0 | 1 |
| horse | 1 | 7 | 1 | 0 | 6 | 1 |
| dog | 2 | 6 | 2 | 0 | 4 | 2 |
| bird | 3 | 5 | 3 | 0 | 2 | 3 |
| other_animal | 5 | 8 | 5 | 0 | 3 | 5 |
| man | 20 | 38 | 19 | 1 | 19 | 19 |
| woman | 15 | 32 | 15 | 0 | 17 | 15 |
| child | 5 | 14 | 4 | 1 | 10 | 4 |
| nude | 8 | 19 | 8 | 0 | 11 | 8 |
| crowd | 1 | 11 | 1 | 0 | 10 | 1 |
| dead_or_wounded_body | 4 | 14 | 4 | 0 | 10 | 4 |
| soldier_or_armour | 5 | 12 | 4 | 1 | 8 | 4 |
| weapon | 4 | 13 | 4 | 0 | 9 | 4 |
| book_or_paper | 3 | 8 | 2 | 1 | 6 | 2 |
| musical_instrument | 3 | 7 | 3 | 0 | 4 | 3 |
| curtain_or_drapery | 1 | 18 | 1 | 0 | 17 | 1 |
| hat_or_headdress | 4 | 37 | 4 | 0 | 33 | 4 |
| jewellery_or_crown | 5 | 10 | 4 | 1 | 6 | 4 |
| halo | 1 | 4 | 1 | 0 | 3 | 1 |
| wings | 2 | 6 | 2 | 0 | 4 | 2 |
| cross | 1 | 7 | 1 | 0 | 6 | 1 |
| skull_or_skeleton | 2 | 2 | 2 | 0 | 0 | 2 |

majority of three untold describers against depicts, over 38 mapped categories x 52 paintings: recall of depicts 149/158 = 0.94; share of describer marks that depicts confirms 149/461 = 0.32; single describer recall 149/158 = 0.94


## The instrument, verbatim

````markdown
# Painting description instrument (v1)

You will be given a list of image files. Each is a photograph of a painting. For every image, look at the picture and fill in the record below. Describe what you see in this picture, not what you know about it. If you think you know the painting, set that aside while you mark the first three sections; the last section is where you say so.

Some entries in the list come with a `told` field giving a title, painter and year. That is all the context you get for that image. Fill in the same record.

Mark every field for every image. Use the whole range of each scale across the batch; most felt words should be 0 for most pictures.

## Record

Return one JSON object per image with exactly these keys.

### `felt` : what the picture does to a viewer

Rate each word 0 to 3 for how strongly the picture, as it looks, produces that feeling or atmosphere in someone looking at it. 0 = not at all, 1 = slightly, 2 = clearly, 3 = strongly. Integers only. Rate the feeling, not the subject: a picture of a party can feel desolate.

`calm`, `tense`, `tender`, `eerie`, `festive`, `desolate`, `joyful`, `melancholy`, `awed`, `uneasy`, `intimate`, `playful`, `solemn`, `alarming`, `sensual`, `lonely`, `hopeful`, `oppressive`, `dreamlike`, `energetic`, `still`, `warm`, `cold`, `mysterious`

(`awed` = it inspires awe; `alarming` = violent or frightening; `still` = a hush, a sense that nothing moves; `warm` and `cold` are feelings of emotional warmth or chill, not colour temperature.)

### `subject` : what is visibly there

Only what can be seen. Not who the figures are, not what the scene means, not the story it illustrates. A woman holding a wheel is "woman, wheel", not a named saint. If the picture depicts nothing, say so with zeros and `"setting": "none"`.

- `people`: one of `"0"`, `"1"`, `"2"`, `"3-5"`, `"6+"` (human or human-like figures, including tiny distant ones)
- `animals`: one of `"0"`, `"1"`, `"2"`, `"3-5"`, `"6+"` (real or imaginary creatures)
- `setting`: one of `"interior"`, `"landscape"`, `"townscape"`, `"seascape"`, `"garden"`, `"sky_or_heaven"`, `"plain_background"`, `"mixed"`, `"none"`
- `things`: an object with every one of the following keys set to 1 (visibly present) or 0 (not visible):
  `sky`, `clouds`, `sun_or_moon`, `water`, `trees`, `mountains_or_hills`, `rocks`, `field_or_grass`, `flowers`, `fruit_or_food`, `snow_or_ice`, `fire_or_smoke`, `buildings`, `window_or_door`, `furniture`, `bridge`, `road_or_path`, `boat_or_ship`, `cart_or_carriage`, `horse`, `dog`, `cattle_or_sheep`, `bird`, `fish`, `other_animal`, `man`, `woman`, `child`, `old_person`, `nude`, `crowd`, `dead_or_wounded_body`, `soldier_or_armour`, `weapon`, `book_or_paper`, `musical_instrument`, `vessel_or_tableware`, `curtain_or_drapery`, `hat_or_headdress`, `jewellery_or_crown`, `flag_or_banner`, `halo`, `wings`, `cross`, `skull_or_skeleton`, `written_text`
  (`nude` = an unclothed or mostly unclothed human body; `crowd` = more than about ten figures; `child` includes infants; `halo`, `wings`, `cross` are marked only as visible things; `written_text` = legible or illegible writing, inscription, seal or signature large enough to notice.)
- `main_action`: free text, 8 words at most, what is happening (e.g. "woman pours milk from a jug", "nothing; empty landscape")
- `tags`: up to 8 short free tags, lower case, for visible things not covered above

### `manner` : how it is rendered

Integers 0 to 4.

- `abstraction`: 0 lifelike, 4 non-representational
- `contour`: 0 forms bounded by clear line or edge, 4 forms dissolved into paint or atmosphere
- `finish`: 0 smooth with no visible strokes, 4 broken with visible strokes or marks throughout
- `detail`: 0 sparse and summary, 4 minute detail everywhere
- `depth`: 0 flat pattern on the surface, 4 deep modelled space
- `palette_breadth`: 0 one hue or monochrome, 4 many distinct hues
- `saturation`: 0 grey or muted, 4 vivid
- `colour_temperature`: 0 cool (blue, green, grey), 2 balanced, 4 warm (red, orange, brown, gold)
- `darkness`: 0 very light overall, 4 very dark overall
- `contrast`: 0 even light, 4 strong light against dark
- `crowding`: 0 mostly empty, 4 packed edge to edge
- `symmetry`: 0 strongly asymmetric, 4 strictly symmetric
- `closeness`: 0 distant view, 4 close-up

### `recognition` : answered last

- `recognised`: true or false. Do you recognise this specific painting?
- `title`: your title for it if recognised, else `""`
- `painter`: the painter if recognised, else `""`
- `confidence`: 0 to 3 (0 = not recognised, 1 = a guess, 2 = fairly sure, 3 = certain)
- `guess_school`: your best guess at the painter or school from the look of it (always answer)
- `guess_century`: an integer century, e.g. 17 (always answer)

For an image with a `told` field, answer `recognised` as you would have without being told.

## Output

Write one JSON file to the output path you are given, and nothing else to disk:

```json
{"batch": 0, "records": [
  {"code": "abc1234",
   "felt": {"calm": 0, "tense": 0, "...": 0},
   "subject": {"people": "1", "animals": "0", "setting": "interior",
               "things": {"sky": 0, "...": 0},
               "main_action": "", "tags": []},
   "manner": {"abstraction": 0, "...": 0},
   "recognition": {"recognised": false, "title": "", "painter": "", "confidence": 0,
                   "guess_school": "", "guess_century": 17}}
]}
```

One record per image, in the order given, every key present, valid JSON.
````

## Draft descriptor table

`descriptors_draft.csv`. The first 24 kind 1 words are the instrument's vocabulary; the four kind 1 words after them (from `nocturnal`) were considered and left out.

| word | kind | reason |
|---|---|---|
| calm | 1 | calm induced in the viewer |
| tense | 1 | tension felt |
| tender | 1 | tenderness felt towards what is shown |
| eerie | 1 | uncanny atmosphere |
| festive | 1 | celebratory mood; a feast as subject is kind 3 and is not what is rated |
| desolate | 1 | bleakness felt; an empty land as subject is kind 3 |
| joyful | 1 | joy felt |
| melancholy | 1 | sadness the picture puts you in |
| awed | 1 | awe felt; borderline with scale and grandeur (kind 2) |
| uneasy | 1 | unease felt; overlaps tense and eerie and is kept to see whether a describer separates them |
| intimate | 1 | closeness felt; a close viewpoint is kind 2 and is in the closeness scale |
| playful | 1 | lightness and play felt |
| solemn | 1 | gravity felt; a religious subject is kind 3 |
| alarming | 1 | fear or shock felt; depicted violence is kind 3 and is in the weapon and body marks |
| sensual | 1 | bodily or erotic charge felt; a nude as subject is kind 3 and is in the checklist |
| lonely | 1 | loneliness felt; a single figure is kind 3 (the people count) |
| hopeful | 1 | hope felt |
| oppressive | 1 | weight or confinement felt |
| dreamlike | 1 | unreality felt; borderline with fantastical subject |
| energetic | 1 | energy felt; borderline with broken handling (kind 2) |
| still | 1 | hush felt; borderline with a static composition (kind 2) |
| warm | 1 | emotional warmth; warm colour is kind 2 and is in the colour_temperature scale |
| cold | 1 | emotional chill; cool colour is kind 2 |
| mysterious | 1 | sense of something withheld |
| nocturnal | 1 | night as an atmosphere; left out of the instrument because darkness (kind 2) and sun_or_moon (kind 3) already carry most of it |
| serene | 1 | same as calm; dropped as a duplicate |
| disturbing | 1 | same as alarming and uneasy together; dropped as a duplicate |
| nostalgic | 1 | felt |
| dark | 2 | how light the picture is; colour block |
| bright | 2 | lightness; colour block |
| colourful | 2 | palette breadth and saturation; colour block |
| muted | 2 | saturation; colour block |
| crowded | 2 | how full the surface is; composition block |
| empty | 2 | composition block |
| rough | 2 | surface and handling; manner block |
| smooth | 2 | finish; manner block |
| flat | 2 | depth against surface; composition and manner |
| detailed | 2 | manner block |
| linear | 2 | contour; manner block |
| painterly | 2 | contour and finish; manner block |
| symmetrical | 2 | composition block |
| monumental | 2 | scale of forms in the frame; composition (also carries standing |
| religious | 3 | what it is about |
| mythological | 3 | what it is about; needs knowledge beyond the first level |
| pastoral | 3 | rural subject; also a genre word (kind 4) |
| maritime | 3 | sea as subject |
| erotic | 3 | nude or sexual subject; the felt side is sensual |
| violent | 3 | depicted violence; the felt side is alarming |
| domestic | 3 | household subject |
| portrait | 4 | genre |
| still life | 4 | genre; its content is in the checklist |
| baroque | 4 | movement and period |
| impressionist | 4 | movement |
| naive | 4 | a judgement of schooling |
| academic | 4 | school and standing |
| iconic | 4 | standing |
| masterful | 4 | judgement of quality |
| modern | 4 | era |
