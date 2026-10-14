# painting2vec pilot dataset

Built 8 October 2026 for the experiments in `src/art2vec/painting2vec/FRAMEWORK.md` (sections 8 and 9). Nothing here is committed. Images live under `data/painting2vec/` (gitignored); this folder holds the scripts and copies of the CSVs.

## What is on disk

| set | path | paintings | pairs |
|---|---|---|---|
| A. pilot | `data/painting2vec/pilot/images/<qid>.jpg`, `pilot/meta.csv` | 2,000 | |
| B. reproductions | `data/painting2vec/repro/<qid>__<source>.jpg`, `repro/repro_pairs.csv` | 274 | 274 primary, 563 rows in all |
| C. versions and copies | `data/painting2vec/versions/images/<qid>.jpg`, `versions/version_pairs.csv`, `versions/meta.csv` | 304 in kept pairs (355 downloaded) | 195 kept, 27 rejected |

CSV copies without images are in this folder: `pilot_meta.csv`, `repro_pairs.csv`, `version_pairs.csv`, `versions_meta.csv`.

Total on disk: 675,498,825 bytes (675 MB) with hard links counted once. Pilot 481 MB, reproductions 168 MB, versions 87 MB, caches 25 MB. `repro/<qid>__commons.jpg` and the 58 version images that are also pilot paintings are hard links to the pilot file. `du` on one folder counts them again.

Every image is a JPEG at quality 90, long side 1,024 px or the original's size if smaller, decoded and re-encoded with Pillow. No download failed to decode.

## A. Pilot set

Source: Wikidata items that are instance of painting (Q3305213) with a P18 image.

Rule for inclusion (the pilot's public-domain rule): every named creator has a death date and died before 1926 (1,872 paintings); or no creator death date is recorded and inception is before 1870 (128). The Commons file must also be marked Public domain, CC0 or Public Domain Mark by Commons (1,894 / 103 / 3). Files with a CC BY or BY-SA licence were skipped (109 of the 3,812 candidates checked), as were originals under 600 px (87).

Ranking: number of Wikipedia sitelinks (Wikipedia language editions only; Commons, Wikiquote and the like are not counted). Ties are broken by md5 of the QID, not by QID order, so a tie does not favour whichever museum was bulk-loaded first.

| stratum | n | sitelinks min / median / max | with zero sitelinks |
|---|---|---|---|
| sitelink_rank | 1,600 | 8 / 12 / 134 | 0 |
| non_european:japanese | 100 | 0 / 1 / 6 | 10 |
| non_european:chinese | 100 | 0 / 1 / 7 | 17 |
| non_european:south_asian | 60 | 0 / 0 / 5 | 54 |
| non_european:persian_ottoman | 50 | 0 / 0 / 3 | 35 |
| non_european:other_non_european | 50 | 1 / 2 / 6 | 0 |
| non_european:korean | 40 | 0 / 0 / 4 | 35 |

A painting's tradition is its country of origin (P495) if that is one of the non-European countries or states listed in `01_candidates.py`, else its creator's citizenship (P27). `tradition`, `country_name` and `country_basis` record the result. The non-European strata take the best-linked paintings of each tradition that are not already in the rank stratum.

| tradition (whole set) | n |
|---|---|
| european_american | 1,540 |
| japanese | 103 |
| chinese | 103 |
| south_asian | 60 |
| other_non_european | 52 |
| persian_ottoman | 51 |
| korean | 41 |
| unknown (no country on the painting or its creator) | 50 |

| century of inception | n | | century | n |
|---|---|---|---|---|
| 7th to 11th | 18 | | 17th | 350 |
| 12th | 15 | | 18th | 148 |
| 13th | 15 | | 19th | 684 |
| 14th | 23 | | 20th | 76 |
| 15th | 196 | | 21st | 1 (a Wikidata date error) |
| 16th | 406 | | unknown | 68 |

Countries with most paintings: France 316, Republic of Venice 125, Spain 111, Dutch Republic 109, Japan 99, Italy 73, Holy Roman Empire 71, United Kingdom 68, Duchy of Milan 62, Kingdom of the Netherlands 60. Wikidata gives historical states, so "Italy" is split across Venice, Milan, Florence, the Papal States and others. The full table is printed by `08_stats.py`.

Holding collections (441 distinct; first one listed on the item): Metropolitan Museum of Art 144, Museo del Prado 114, National Gallery (London) 105, Louvre paintings department 102, Musée d'Orsay 65, Uffizi 49, Kunsthistorisches Museum 49, National Gallery of Art 48, Hermitage 35, Gemäldegalerie Berlin 34, Palace Museum 29, Tate 28, Rijksmuseum 26, Bavarian State Painting Collections 24, National Palace Museum 24, Tretyakov 20. No collection recorded: 68.

Painters: 463 distinct, 96 paintings with no creator. 53 painters have 8 or more paintings (target 40): Raphael 69, Van Gogh 66, Titian 61, Caravaggio 60, Rembrandt 53, Manet 39, El Greco 38, Rubens 38, Goya 37, Vermeer 36, Velázquez 36, Bruegel the Elder 35, Renoir 32, Courbet 28, Botticelli 25, David 23, Bosch 23, Bouguereau 21, Waterhouse 21, Ingres 20, Gauguin 20, Leonardo 19, Van Eyck 19, Dürer 19, Van der Weyden 17, Artemisia Gentileschi 17, Giovanni Bellini 17, Osman Hamdi Bey 16, Gérôme 16, Friedrich 15, Mantegna 15, Cézanne 15, Itō Jakuchū 15, Millais 14, Rossetti 14, Jan Rustem 14, Klimt 13, Tintoretto 13, Kuroda Seiki 13, Degas 12, Memling 11, Murillo 11, Delacroix 10, Veronese 10, Correggio 10, Giorgione 9, Hals 9, Zurbarán 9, Juan Luna 9, Sargent 8, Matejko 8, Holman Hunt 8, Victor Meirelles 8.

### meta.csv columns

`qid, title, creator_qid, creator_name, creator_birth_year, creator_death_year, inception_year, movements, genres, depicts, materials, height_cm, width_cm, collection_qid, collection_name, country_qid, country_name, country_basis, tradition, sitelinks, stratum, commons_file, image_source_url, commons_page_url, licence, licence_detail, px_width, px_height, orig_px_width, orig_px_height, pd_basis, inventory_number, fame_score, in_poc`, then museum identifiers: `met_id` (P3634), `aic_id` (P4610), `nga_id` (P4683), `cleveland_id` (P11110), `rijksmuseum_id` (P13234), `philadelphia_id`, `walters_id`, `mia_id`, `getty_id`, `nationalmuseum_se_id`, `saam_id`, `yale_gallery_id`, `harvard_id`, `prado_id`, `orsay_id`, `louvre_ark`, `mfa_boston_id`, `ycba_id`, `lacma_id`, `artuk_id`, `rkdimages_id`, `joconde_id`, `google_arts_id`.

Multiple values are pipe-joined. `depicts` is capped at 30 labels. `sitelinks` is the Wikipedia-only count. `licence` is Commons' LicenseShortName and `licence_detail` its License, UsageTerms and Copyrighted fields. `px_*` is the stored file, `orig_px_*` the Commons original.

Coverage out of 2,000: title 1,983, creator 1,904, inception year 1,932, genre 1,710, depicts 1,729, material 1,743, height 1,823, width 1,813, collection 1,932, country 1,950, inventory number 1,708, movement 979. Museum ids: Met 146, Prado 115, Louvre 108, NGA 48, Rijksmuseum 26, MFA Boston 15, AIC 13, Philadelphia 8, Getty 7, Walters 4, MIA 4, Cleveland 0 (P11110 is not used on these items; the 12 Cleveland paintings were matched by accession number instead), `google_arts_id` 0 (the property I mapped is wrong or unused; treat that column as empty).

`fame_score` and `in_poc` are joined by QID from `experiments/painting2vec/canon/candidates.csv`. 1,844 of the 2,000 pilot paintings appear in that file and 1,025 are in its proof-of-concept set (932 from the rank stratum, 93 from the non-European strata). Its `in_poc` set has 2,410 paintings, so the pilot covers 43 % of it. The two sets rank differently: 668 of my 1,600 rank-stratum paintings are not in `in_poc`, and 1,385 `in_poc` paintings are not in the pilot (387 of them by painters who died in 1926 or later, 171 without an image).

## B. Reproduction pairs

A second photograph of 274 pilot paintings (target 120), and a third for 134 of them. `file_a` is always the pilot's Commons image.

| second source (primary pair) | paintings | how |
|---|---|---|
| another Commons file | 139 | a PD/CC0 file in the painting's Commons category with a different uploader and a different source line, aspect ratio within 5 % of the P18 file |
| Metropolitan Museum | 66 | collection API, `isPublicDomain` true |
| National Gallery of Art | 36 | open-data image table, `openaccess` 1, IIIF at 1,024 px |
| Rijksmuseum | 21 | Linked Art records by object number, rights = Public Domain Mark, IIIF at 1,024 px |
| Art Institute of Chicago | 9 | API, `is_public_domain` true, IIIF at 1,024 px |
| Cleveland Museum of Art | 3 | open-access API by accession number, CC0, the 900 px "web" image |

So 135 primary pairs are Commons against the holding museum's own image and 139 are Commons against Commons. The Commons search covered only the 160 best-linked pilot paintings.

`lab_diff` is the mean absolute difference of the two 64x64 CIELAB thumbnails (aspect ratio ignored), in LAB units. Candidates under 1.0 were dropped as the same file re-encoded: 112 dropped (Met 76, NGA 12, Cleveland 9, Commons 8, AIC 4, Rijksmuseum 3). That is the main finding of this step: for 104 of 239 museum images fetched, the Commons file is the museum's own photograph. Two Commons candidates over 22 were dropped as not the same picture. None was byte-identical after re-encoding; the 1.0 threshold stands in for that test.

Primary-pair `lab_diff`: min 1.01, quartiles 3.06 / 5.56 / 9.02, max 29.22.

`flag` on each row:

- `low_diff_maybe_same_master` (27 primary pairs, lab_diff 1 to 2): probably one photograph with different colour handling or a border added. Not good evidence of an independent reproduction.
- `high_diff_check_frame_or_crop` (30, lab_diff over 12): the museum image usually includes the frame, the scroll mount or a backdrop.
- `bw_reproduction` (3 primary, 17 of all rows): one file is a black-and-white scan.
- no flag: 214 primary pairs.

By stratum: 255 from the rank stratum, 19 from the non-European strata (Japanese 10, South Asian 4, Chinese 3, Korean 2).

Columns: `qid, file_a, source_a, file_b, source_b, lab_diff, flag, chroma_a, chroma_b, pair_kind, title, source_b_url, source_b_note, source_b_file, source_b_uploader`. `pair_kind` is `primary` for Commons against the first second source and `extra` for rows involving a third reproduction.

## C. Versions and copies

195 pairs of different physical paintings that share a composition (target 60), over 304 paintings.

| relation | pairs | composition_match yes | variant |
|---|---|---|---|
| version (a painter or workshop repeats a composition; curated list) | 81 | 78 | 3 |
| based_on_P144 (Wikidata: A is based on B) | 82 | 54 | 28 |
| derivative_P4969 | 1 | 0 | 1 |
| series_motif (Monet's Haystacks, Rouen Cathedral, Houses of Parliament, Poplars, Charing Cross Bridge, Waterloo Bridge; Hicks's Peaceable Kingdom) | 31 | 0 | 31 |

Curated groups: Van Gogh's Sunflowers, Bedroom, L'Arlésienne (two types), La Berceuse, Dr Gachet; Munch's Scream, Madonna, Sick Child, Vampire; Leonardo's Virgin of the Rocks and the Yarnwinder Madonnas; Böcklin's Isle of the Dead; David's Napoleon Crossing the Alps; Cézanne's Card Players; Manet's Execution of Maximilian; El Greco's Disrobing of Christ; Caravaggio's Boy Bitten by a Lizard, Fortune Teller and Lute Player; Gentileschi's Judith; Renoir's Girls at the Piano; Titian's Danaë, Venus and Adonis and Magdalene; Holman Hunt's Light of the World; Rossetti's Proserpine and Beata Beatrix; Friedrich's moon-watchers; Leutze's Washington Crossing the Delaware; Constable's Salisbury Cathedral. Each group is a star: the best-linked member against each other member. Wikidata P144 pairs include Van Gogh after Jordaens, Manet after Delacroix and Titian, Rubens after Titian, and copies of the Mona Lisa, Las Meninas, the Venus of Urbino, the Death of Marat and Leonardo's Saint Anne. No Van Gogh after Millet pair came through: Wikidata's Millet originals did not pass the image and aspect filters.

`composition_match` is my judgement from looking at every pair side by side: `yes` (same composition), `variant` (same composition with visible changes: figures added or dropped, a reworked version, one member framed or unfinished; all series_motif pairs are marked variant). 25 Wikidata pairs judged not to share a composition (a loose homage, a head detail, a study) and 2 pairs where two Wikidata items carry the same photograph are in `versions/version_pairs_rejected.csv`. The verdicts are written into `06_versions.py`.

The strict pilot PD rule was applied to Wikidata pairs but not to curated groups, which need only a Commons file marked public domain. 50 of the 304 paintings fail the strict rule and have an empty `pd_basis` in `versions/meta.csv`: Munch (died 1944) and Monet (died December 1926).

## Shortfalls

- Non-European strata are thin by the reception measure. Korean, South Asian and Persian/Ottoman paintings mostly have no Wikipedia article at all (35 of 40, 54 of 60, 35 of 50 have zero sitelinks), so within those strata the pick among zero-sitelink items is a fixed pseudo-random sample of up to 700 candidates per tradition, not a ranking.
- The tradition rule (country of origin, else creator citizenship) misfiles painters by passport. "persian_ottoman" (50) is Ottoman Empire 35, Iran 11, Turkey 2, Syria 2; 15 are Osman Hamdi Bey's academic oils and 14 are by Jan Rustem, who was born in Constantinople and worked in Vilnius in a European manner (11 of them are in the National Museum in Warsaw). Persian painting proper is about 11 works, because Wikidata rarely types miniatures as paintings. "south_asian" (60) includes 3 by Arthur Boyd Houghton, a British illustrator born in India. "other_non_european" (50) is Latin American and Philippine academic painting: Brazil 22, Philippines 8 (Juan Luna), Mexico 5, Chile 4, Venezuela 4, Peru 3. There is one ancient Egyptian painting and no other pre-colonial work.
- The non-European strata lean on a few museums' photography: Korean is Met 23 and Harvard 9 of 40; South Asian is Met 27 of 60; Chinese is the Palace Museum 29 and National Palace Museum 22 of 100. Any "can the vector predict the museum" check will be confounded with tradition here.
- Monet is absent from the pilot (died 1926, one year outside the rule), as are Munch, Matisse, Picasso and everything later.
- The intended B pairing (Commons against the museum's own image) reached 135 paintings, not all 274, and 27 of all primary pairs are probably not independent (flagged).
- No Van Gogh after Millet pair in C.
- The pilot image is the Commons P18 file, not the holding museum's image, which is what the framework names as the artefact.

## Data-quality problems seen

I looked at 48 pilot images on contact sheets (a fixed sample, 24 per stratum group), 4 at full size, 12 flagged ones, 18 reproduction pairs across the lab_diff range and every version pair the script produced (232 at the time; the 3 pairs added afterwards for the second L'Arlésienne and Card Players types were seen as images but not side by side).

- Rank stratum sample (24): all whole paintings in colour, no frames. One is not a painting: Q2072801 "Portrait of a Young Fiancée" is chalk and ink on vellum. Three pastels are typed as paintings (Q445627, Q2912117, Q17510059).
- Non-European sample (24): 6 hanging scrolls photographed with their silk mount or a grey backdrop; 2 handscrolls reduced to a thin strip; 1 album spread that is half calligraphy; 1 black-and-white photograph of an ink drawing (Q78727757); 1 image with a printed caption under the picture (Q122888933, 704 px wide); about half have no English title (Chinese or Japanese only, or none).
- Long scrolls: 52 stored images are wider than 3:1; 20 have a short side under 100 px (the extreme is about 1,024 x 21). These are useless at this size.
- 8 stored images are greyscale: black-and-white photographs of lost paintings (Q1778000 Baronci Altarpiece, Q2395137 Caravaggio's Portrait of a Courtesan), museum archive negatives of Asian works (Q78834676, Q78761942, Q106864313, Q12615728), and Q78875327 "Pali Manuscript", which is a photograph of the object, not a painting.
- 131 images are under 1,024 px because the Commons original is smaller (minimum 600).
- 15 Commons file names contain "cropped", "detail" or "frame"; the ones I viewed (Q11695670, Q2873059, Q3715966, Q123843154) are whole paintings.
- Reproductions: museum images often include the frame or mount where the Commons file is cropped to the picture (Met scrolls and panels especially); some second Commons files are black-and-white book scans or a photograph of a book page (Q152509).
- Versions: Wikidata's "based on" is loose (25 of 110 pairs rejected); drawings typed as paintings appear (Q2308934 Leda, Q2045726 Anghiari copy); two version images include a frame (Q58018788, Q79139231), one a colour chart (Q47414451), one a scale card (Q20787925); three are black-and-white photographs of lost works.
- One inception date in the 21st century on a painting whose creator died before 1926 (Wikidata error).

Not checked: the other 1,950 pilot images were not viewed; licence statements were taken from Commons and the museum APIs as given and not verified against the museums' terms; `tradition` was assigned by rule and not reviewed.

## Scripts

Run from the repository root, one at a time. All are resumable: API answers are cached in `data/painting2vec/cache/`, existing images are skipped, connection errors are retried with back-off for up to an hour.

```
uv run --no-project --with requests --with pillow --with pandas python experiments/painting2vec/dataset/01_candidates.py
```

| script | does |
|---|---|
| `01_candidates.py` | candidate QIDs from the Wikidata SPARQL endpoint, one exact sitelink count or one country per query |
| `02_select.py` | Wikidata records (wbgetentities), PD rule, ranking, tradition |
| `03_commons_select.py` | Commons licence check, final pick of 1,600 + 400 |
| `04_download_pilot.py` | pilot images and `meta.csv` |
| `05_repro.py` | reproduction pairs; `--finalise` reapplies thresholds, `--retry-failed` refetches failures |
| `06_versions.py` | version pairs, images, `versions/meta.csv`; holds the review verdicts |
| `07_contact_sheets.py` | contact sheets for spot checks |
| `08_stats.py` | the numbers in this file |
| `common.py`, `wd.py`, `commons.py`, `meta.py` | shared helpers |

Image requests are sequential, one image in memory at a time, with a 60-megapixel Pillow guard. Commons images are standard-width thumbnails. Museum images are IIIF at 1,024 px, except the Met (its only sizes are about 600 px or the original, so the original is fetched and decoded reduced) and Cleveland (900 px).
