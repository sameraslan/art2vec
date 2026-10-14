# Where the painting canon should come from

Research note for painting2vec, section 7 (canon) of `src/art2vec/painting2vec/FRAMEWORK.md`. Measured on 8 October 2026.
Nothing here is adopted. No images were downloaded. Reception is used only to decide which works are in the set (root Rule 1).

**How to read the figures.** Every number in sections A to H is *measured*: it is printed by a script in this folder from data fetched on the date above, and the query is in the script (the main ones are repeated in the appendix). Numbers in the survey (part 1) are marked *live* (checked against the source that day) or *secondary* (from memory or a third party, not checked). Three things are *proxies*, not measurements, and are named as such wherever they appear: tradition (from the creator's citizenship), copyright status (from the creator's death year), and open-image availability (from the presence of a Commons image).

Sections A to H are generated: `data/tables.md` by `05_analyse.py` and `data/recipe_tables.md` by `07_recipe.py`. The prose above them is `data/README_head.md`; this file is the four parts concatenated.

## Summary

- Wikidata has 1,084,295 items typed painting; 47,279 have any sitelink. Raw sitelinks >= 3 gives 10,004 and >= 8 gives 2,547, so the two target sizes fall on round thresholds.
- Raw sitelink count is inflated: 68% of the top 10,000 carry a Commons sitelink, 24% an Egyptian Arabic stub and 8% a Kotava stub. Counting Wikipedia editions only, without the stub editions, removes a fifth of the raw top 10,000 (1,954 works).
- The ranking is a fair stand-in for the famous end of the canon and a poor one for its breadth. All 130 Vital-article paintings are in the top 10,000 and 98% are in the top 2,500. But only 55% of the tagged "1001 Paintings" and 79% of the BBC's "100 Great Paintings" are in the top 10,000, and a third of the 1001 list has no Wikipedia article in any language.
- It is not swamped by Vermeer (36 works) but it is by a few painters with complete catalogues on Wikipedia: Goya 250, Van Gogh 207, Titian 194, El Greco 190, Rembrandt 184. Forty-one painters have 50 or more works. A cap is needed.
- It is 87% Western European by creator. China, Japan, Korea, South Asia, Persia, the Ottoman and Arab worlds, sub-Saharan Africa, Southeast Asia and Indigenous art together are about 130 works in 10,000. The whole pool of such works with even one Wikipedia article is under 900. A floor can make them visible; it cannot make them proportionate.
- Copyright (proxy): in the raw top 10,000, 84% of works are by painters who died before 1926, 9% by painters who died 1926 to 1955, 5% after 1955, 0.3% living. Editorial canons are slightly more modern (78% / 10% / 8% / 2%).
- Descriptions for the top 2,500: 97% have an English Wikipedia article and 87% a lead of 200 characters or more; 21% are held by a museum with openly licensed text; 89% have creator, date, collection, material and size on Wikidata.

## Recommendation

One list, built from Wikidata, with four ways in and three rules that take works out.

**Universe.** Wikidata items whose type (P31) is painting (Q3305213), any subclass of it (fresco, mural, icon, watercolour, emakimono, hanging scroll, miniature and so on), or a painted format that sits outside that tree: triptych, polyptych, diptych, altarpiece, winged altarpiece, byōbu, folding screen. The key is the QID.

**Fame score.** The number of Wikipedia language editions with an article on the work, not counting Commons, sister projects, or four machine-made stub editions (arz, avk, ceb, war). Ties are broken by 60-day pageviews summed over twelve large editions, then raw sitelinks, then the older QID. The score decides membership and tie order and nothing else.

**Ways in (any one).**

1. *Fame.* Score >= 3 for the canon; >= 6 for the POC.
2. *Editorial lists.* Named by any of: Wikipedia Vital articles level 5, "1001 Paintings You Must See Before You Die" (as tagged on Wikidata), the BBC's "100 Great Paintings", Smarthistory, AP Art History 250. In the POC this route also needs score >= 3.
3. *Museum highlights and state designations* (canon only): the Met's `isHighlight`, the Art Institute of Chicago's `is_boosted`, Cleveland's `highlight`, and National Treasures of Japan.
4. *Tradition floor.* For each under-represented tradition (China, Japan, Korea, South Asia, Persia and Central Asia, Ottoman and Turkey, Arab world, sub-Saharan Africa, Southeast Asia, Latin America, Indigenous and pre-Columbian), ranked by the same score within the tradition. Canon: every work with score >= 1 or on any list. POC: the top 60 for China and for Japan, the top 30 for each other tradition, or the whole pool where it is smaller.

**Ways out.**

1. *Not one flat painting.* Items also typed as sculpture, building, site, museum, cyclorama, print, drawing, collage, photograph, manuscript and the like.
2. *Series.* An item typed painting series, cycle or group is not a picture. Its best-known member stands for it and takes the series' score if that is higher (The Scream's 73 editions go to one of the five versions). Members with their own articles stay in on their own score. A panel whose polyptych is itself a candidate is dropped in favour of the whole.
3. *Painter cap.* At most 40 works per named painter in the canon and 12 in the POC, keeping works on an editorial list first and then by score. Anonymous works are not capped.

**Then the rights gate** of section 7, which is the other agent's to define. This note only flags each work with the death-year proxy and whether Commons has an image.

**What it yields (measured, section H).**

| | canon | POC |
|---|---|---|
| works | 8,851 | 2,410 |
| with a Commons image and a painter dead before 1926, or anonymous before 1850 | 6,670 (75%) | 1,929 (80%) |
| painter died 1926 to 1955 | 915 | 225 |
| painter died after 1955 or living | 943 | 192 |
| under-represented traditions | 1,253 (14%) | 334 (14%) |
| named painters | 1,871 | 712 |
| largest collection | Met, 575 (6.5%) | National Gallery, 134 (5.6%) |
| English Wikipedia article | 68% | 89% |

The canon stops at 8,851 on purpose. The next step down (score 2) adds about 5,000 works at once with no principled way to pick among them, and the room is better kept for additions.

**Append-only.** Each run writes a dated snapshot. A QID that has ever been in the canon stays in, with the date it entered and the gate that admitted it; later runs can add works and can never remove them. A merged QID is kept as an alias of its target. The thresholds are written in the snapshot. Scores are recomputed for tie order only.

**The main alternative, and why not.** Rank by Wikipedia pageviews instead of editions. It is the "popular interest" measure and it is what the one public ranking of paintings uses. Rejected as the primary score for four reasons. It agrees with the edition count on only 71% of the top 2,500 (section D), and the disagreements are mostly news and curiosity: an auction record, a painting with a lurid title, a meme. It needs one API call per article per edition and a choice of window; 60 days is what the batch API gives. It leans harder on English. And it moves week to week, which is the opposite of what an append-only list wants. It is kept as the tie-break, where it does useful work among the two thousand works that share a score of 3.

Two other alternatives fail on size. A meta-list of editorial canons, in the manner of TSPDT for film, would be the right thing, but the lists that exist in machine-readable form name only 967 distinct paintings between them, 84% of them on a single list. Museum highlight flags give about 700 paintings, all from three museums in the United States.

## What is weak

- **The score measures what Wikipedia editors wrote about.** The top 10,000 is 87% Western European, 3.4% by women (337 works), and has one Hokusai, because prints are out of the medium and his paintings have no articles.
- **The floor is a patch.** After it, under-represented traditions are 14% of the set, a third of that Latin American. The pool is the limit: 204 Chinese and 334 Japanese works with any article or listing, 36 Korean, 35 Persian, 15 sub-Saharan African, 3 Indigenous. The bottom of each pool is whatever happened to get one article: the African list includes a mural in Portland, Oregon. Real coverage needs lists this survey could not obtain in open form: designated cultural properties of China and Korea, the Palace Museums' own selections, a curated list of Mughal and Persian manuscript painting. Wikidata holds 111,197 paintings with country of origin China and only 208 of them have a sitelink.
- **Tradition is a regex over citizenship labels.** "Western Europe" is the default for any labelled state that no other pattern matches. 3.7% of the canon is "unknown", mostly anonymous icons. Use the column for shares, not for single works.
- **Copyright is a death-year proxy.** It ignores country, publication date and the photograph's own rights. A Commons image is not proof of an open licence; 20th-century works on Commons are often there under fair-use exceptions on a local wiki and absent from Commons.
- **The editorial lists are thin and partial.** The 1001 Paintings tagging on Wikidata covers 581 of about 1,001, with the 20th century under-tagged. The AP 250 list was resolved through links in a Wikipedia article and yields only 45 paintings. None of the textbook canons (Gombrich, Gardner, Janson) exists as an open list.
- **Museum highlights tilt the canon toward the Met**, which becomes the largest holder (575). 914 works in the canon (10%) have no Wikipedia article in any language and so no description unless the museum supplies one; the Met's label text has no stated open licence.
- **The threshold is a cliff.** 2,675 works have a score of exactly 3 and 4,967 a score of exactly 2. One translated stub moves a work in. Translation drives in particular editions (Malayalam 1,027 articles in the top 10,000, Armenian 1,321) were not excluded because they are written by people; they still shape the bottom of the list.
- **Series representatives are sometimes arbitrary.** Where no version has its own article the earliest is taken. Four series typed as paintings have no member items at all and are kept with a flag for a hand choice.
- **Pageviews are a 60-day window** (9 August to 7 October 2026) in twelve editions.
- **Scans of all paintings ran on QLever**, a public mirror a few days behind Wikidata, because they time out on the official endpoint. Per-band counts agreed with the official endpoint to within 3 items in 30,588.

## Files

| file | what |
|---|---|
| `candidates.csv` | 15,044 ranked candidates: snapshot, rank, qid, label, creator, year, fame score, raw sitelinks, pageviews, lists, tradition, copyright proxy, flags, and membership of the canon and the POC with the gate that admitted each |
| `excluded.csv` | 381 items with a score of 3 or more that the universe rules removed, with the reason |
| `data/lists.csv` | the nine independent lists resolved to QIDs |
| `data/paintings_sitelinks.csv`, `data/sitelink_histogram.csv` | every painting-like item with a sitelink, and the full histogram |
| `data/pageviews.csv`, `data/lead_lengths.csv`, `data/pool_by_country.csv`, `data/group_members.csv` | inputs to the tables |
| `data/items.jsonl`, `data/refs.jsonl` | fetched Wikidata facts (18 MB, git-ignored; rebuilt by `02_entities.py`) |

Scripts, in run order. All use `uv run --no-project --with requests --with pandas python <script>` and the User-Agent `art2vec-research/0.1 (https://github.com/sameraslan/recmyrecord)`.

| script | does | endpoint |
|---|---|---|
| `wd.py`, `common.py` | polite HTTP helpers; derived columns, universe rules and ranking | |
| `01_sitelinks.py` | histogram and list of every painting or subclass with a sitelink | QLever; total cross-checked on query.wikidata.org |
| `01b_format_classes.py` | adds triptychs, polyptychs, screens, series items | QLever |
| `01c_tradition_pool.py` | paintings per country, with image, with sitelink | QLever |
| `01d_nonwestern_one_sitelink.py` | under-represented traditions down to one sitelink | QLever |
| `03_lists.py` | the nine independent lists | Wikipedia API, query.wikidata.org, Met, AIC and Cleveland APIs |
| `02_entities.py`, `02b_labels.py`, `02c_group_members.py` | facts for 22,770 items and 23,134 referenced entities; series members | `wbgetentities`, 50 per call, three workers |
| `04_pageviews.py` | 60-day views in 12 editions | `prop=pageviews`, 50 titles per call |
| `06_leads.py` | length of the English lead paragraph (length only is stored) | `prop=extracts` |
| `05_analyse.py` | sections A to G | local |
| `07_recipe.py` | section H, `candidates.csv`, `excluded.csv` | local |

# Part 1. Survey of sources

Marked *live* where checked against the source on 8 October 2026, *secondary* where not. "WD" is the number of Wikidata paintings carrying that source's identifier (live, SPARQL).

## Wikidata and Wikipedia

| source | what and how many | obtainable | verdict |
|---|---|---|---|
| Wikidata sitelinks | 1,084,295 paintings, 47,279 with a sitelink (measured, section A) | CC0; SPARQL, API, dumps | the backbone: the only source that reaches 10,000 and is keyed by QID |
| Wikipedia pageviews | any article, any edition | public API, CC0 | tie-break only (see the alternative above) |
| Vital articles level 5 | 142 paintings chosen by editor consensus with quotas; level 4 has 19 (live) | wikitext, CC BY-SA; all 142 resolve to QIDs | a test set for the famous end; not independent of Wikipedia |
| BBC "100 Great Paintings" (Mullins, 1980 to 1982) | 100, in 20 themes, avoiding the most famous works (live) | on Wikidata as a catalogue qualifier | small, deliberately anti-fame, European |
| "List of most expensive paintings" | 122 rows (live) | wikitext | measures the market; not used |
| WikiProject Visual arts importance ratings | do not exist; quality classes only (live) | | nothing to use |
| "described by source" (P1343) | 1001 Paintings: 581 items. Heilbrunn Timeline: 1,279 paintings, all at the Met. Everything else is single-museum or single-artist (live) | CC0 | 1001 Paintings used; Heilbrunn is one museum |
| catalog (P972) | catalogues raisonnés and inventories, apart from the BBC list (live) | | not canon material |
| Sum of All Paintings project | fills in every painting of chosen museums and painters | | the cause of the complete-catalogue painters in section B, not a list |

## Museum-declared highlights

| museum | highlights that are paintings | data and text licence | images | WD |
|---|---|---|---|---|
| Metropolitan Museum | 420 of 2,311 highlights (live, v1.1 search; the v1 search was retired on 1 October 2026) | data CC0; label text has no stated open licence (secondary) | CC0 where public domain | P3634: 12,886 |
| Art Institute of Chicago | 236 `is_boosted`, 120 of them public domain (live). A search-ranking flag, not a declared list | data CC0, descriptions CC BY 4.0 (live) | CC0 via IIIF where public domain | P4610: 3,012 |
| Cleveland Museum of Art | 73, of which 62 CC0; a third East Asian (live) | CC0; records carry QIDs | CC0 | few |
| National Gallery of Art, Washington | no highlight flag (live) | CC0 dump with a `wikidataid` column and text entries | CC0 | P4683: 4,270 |
| Rijksmuseum | the old API and its top-pieces flag are gone (HTTP 410, live); no flag found in the new services | CC0 or CC BY | public domain | P13234: 5,163 |
| National Gallery, London | "30 must-see" is a web page only (not verified) | data CC0, text CC BY 4.0 (live) | CC BY-NC-ND: fails the open-image rule | P13325: 2,538 |
| Louvre | "Masterpieces" album of 40 works of all kinds (live) | entry text under the Etalab open licence, in French; export disallowed by robots.txt | restricted | P9394: 10,422 |
| Prado, Uffizi, Hermitage | no open data or flag found (Prado not reachable; others secondary) | none | restricted | P8905: 6,330; P8335: 189; P10270: 7,787 |
| Getty, SMK Copenhagen, Nationalmuseum Sweden | open APIs, no highlight flag (live) | CC0 | open | P2582: 454; none; P2539: 16,740 |
| Smithsonian Asian Art, V&A | 1,417 paintings in the open subset (live, uncertain); 15,944 objects typed painting, rich in Indian miniatures (live) | CC0; V&A data only | CC0; V&A non-commercial (secondary) | P3929: 208 |
| National Palace Museum, Taipei | open-data notice (live): low-resolution images CC0, text CC BY 4.0 | no QIDs | | P14787: 0 |
| Tokyo National Museum / ColBase | terms not verifiable by script; CC BY-compatible (secondary) | | | P14394: 11 |
| Palace Museum, Beijing | no terms found | | assume reserved | |

Countable highlight flags come to about 730 paintings, all from three museums in the United States. No open list was found for African, pre-Columbian or Indigenous painting.

## Platforms

| platform | size | terms | verdict |
|---|---|---|---|
| Google Arts & Culture | not stated; WD P4701 on 16,883 paintings | no API, robots.txt disallows `/api/` (live) | the identifier is a weak membership signal; nothing else is usable |
| Web Gallery of Art | 52,867 images (live page, January 2022) | catalogue file downloadable, © WGA, no licence | one curator's European selection to 1900; not a canon |
| Art UK | over 600,000 works (secondary); WD P1679 on 214,906 paintings | blocks scripts; mostly non-commercial | every painting in British public ownership: the opposite of a filter |
| Europeana | 403,888 paintings (live) | API key; metadata CC0; mixed image rights | no canon signal |
| WikiArt | about 250,000 works (secondary) | no data licence; "fair use" claim; popularity lists not verified | not usable as a list; also the source of ArtEmis, which may be used for labels only |
| Smarthistory, Khan Academy | 467 items on Wikidata, 348 paintings (measured) | CC BY-NC-SA (secondary); site blocks scripts | used as a list through Wikidata; the essays cannot be shown commercially |
| Artsy Art Genome | public API being retired (secondary) | | unusable |
| The Art Story | proprietary; robots.txt blocks feeds (live) | | unusable |
| Wikimedia Commons | featured pictures; Google Art Project uploads | per-file | an image source, not a list |

## Books and curricula

| source | size | digitised list |
|---|---|---|
| "1001 Paintings You Must See Before You Die" (Farthing) | about 1,001 | 581 tagged on Wikidata (live); no other open copy. A user list on ListChallenges exists, unlicensed and unverified |
| AP Art History, 250 required works | 250, about a third non-European by design; 55 to 65 paintings (estimate) | the Wikipedia article lists all 250 (live); 45 resolve to eligible paintings (measured) |
| Gombrich, *The Story of Art* | about 413 illustrations (secondary) | none found |
| Gardner, Janson, Stokstad | over 1,000 illustrations each (secondary) | none; the indexes are the publishers' |
| Sister Wendy; Phaidon *The Art Book*, *30,000 Years of Art* | | none found |
| National Treasures of Japan, paintings | about 160 designations (secondary); 254 items on Wikidata (measured) | P1435 on Wikidata |

**Aggregated "greatest paintings" list.** None of real quality exists. The nearest is a 2023 ranking of 400 paintings by all-language Wikipedia pageviews (Cultural Index, live), whose author reports that all but five are Western. A rank-aggregated list built from the sources above would be the first.

**Academic work.** Galenson's counts of textbook illustrations (NBER w12058 and related papers) are the method precedent, a poll of art historians, but each ranks 10 to 50 modern Western works and the tables are only in the PDFs. Elkins, *Stories of Art*, compares textbooks without data. Fraiberger and others (*Science*, 2018) and MIT's Pantheon rank artists, not works. No peer-reviewed ranking of individual paintings by sitelinks or pageviews was found (secondary: search was partly unavailable).

**Research datasets as lists.** None is a canon. ArtEmis, ArtBench and WikiArt Refined inherit WikiArt's upload-driven selection and have no QIDs. OmniArt, Art500k, the Rijksmuseum Challenge and the MET dataset are museum dumps. SemArt is 21,384 WGA records with comments under a non-commercial licence. Artpedia (2,930 paintings with English Wikipedia text split into visual and contextual sentences) is the one worth keeping in mind, as a test of whether a describer looks or remembers; as a list it is a subset of English Wikipedia and adds nothing to sitelinks.

# Part 2 and 3. Measurements

## A. Sitelink thresholds

Items with P31 = painting: 1,084,294 (QLever snapshot); with 0 sitelinks: 1,037,015.

| sitelinks >= | P31 = painting (raw, incl. Commons) | + subclasses and format classes (raw) | Wikipedia editions only (all classes) | clean score (all classes) |
|---|---|---|---|---|
| 1 | 47279 | 53955 | n/a | n/a |
| 2 | 16694 | 18697 | 14121 | 13840 |
| 3 | 10004 | 11120 | 9192 | 8873 |
| 4 | 7038 | 7778 | 6502 | 6198 |
| 5 | 5239 | 5767 | 4899 | 4598 |
| 6 | 4080 | 4482 | 3809 | 3518 |
| 7 | 3214 | 3545 | 2976 | 2725 |
| 8 | 2547 | 2829 | 2357 | 2168 |
| 9 | 2012 | 2246 | 1906 | 1731 |
| 10 | 1637 | 1833 | 1597 | 1427 |
| 15 | 689 | 790 | 684 | 620 |
| 20 | 333 | 390 | 352 | 310 |
| 30 | 108 | 129 | 111 | 100 |
| 40 | 38 | 47 | 42 | 41 |

Reference sets used below: **T10k** = P31 painting with raw sitelinks >= 3 (n = 10,009); **T2.5k** = raw sitelinks >= 8 (n = 2,551).

## B. Composition of the top by raw sitelinks

### T10k: raw sitelinks >= 3 (n = 10,009)

| property | items | share |
|---|---|---|
| image (P18) | 9536 | 95.3% |
| English Wikipedia article | 7148 | 71.4% |
| creator (P170) stated | 9804 | 98.0% |
| inception (P571) | 9917 | 99.1% |
| collection (P195) or location (P276) | 9514 | 95.1% |
| depicts (P180), at least one | 7940 | 79.3% |
| height and width (P2048 + P2049) | 9253 | 92.4% |
| material (P186) | 9248 | 92.4% |
| part of (P361) something | 388 | 3.9% |
| in a series (P179) | 232 | 2.3% |
| has parts (P527) | 92 | 0.9% |
| has a Commons sitelink | 6840 | 68.3% |
| has an Egyptian Arabic (arz) sitelink | 2355 | 23.5% |
| has a Kotava (avk) sitelink | 771 | 7.7% |
| also typed as something that is not a flat painting | 28 | 0.3% |

| century of inception | items | share |
|---|---|---|
| before 1300 | 86 | 0.9% |
| 14th c. | 89 | 0.9% |
| 15th c. | 920 | 9.2% |
| 16th c. | 1693 | 16.9% |
| 17th c. | 1716 | 17.1% |
| 18th c. | 804 | 8.0% |
| 19th c. | 3174 | 31.7% |
| 20th c. | 1409 | 14.1% |
| 21st c. | 19 | 0.2% |
| no date | 92 | 0.9% |

| tradition (creator citizenship, else origin) | items | share |
|---|---|---|
| Western Europe | 8733 | 87.3% |
| Russia / Eastern Europe | 498 | 5.0% |
| North America (US/Canada) | 371 | 3.7% |
| unknown | 159 | 1.6% |
| Latin America | 75 | 0.7% |
| China | 44 | 0.4% |
| Oceania (settler) | 35 | 0.3% |
| Japan | 29 | 0.3% |
| South Asia | 21 | 0.2% |
| Ottoman / Turkey | 11 | 0.1% |
| Southeast Asia | 10 | 0.1% |
| Korea | 6 | 0.1% |
| Ancient / Byzantine | 5 | 0.0% |
| Persia / Iran / Central Asia | 5 | 0.0% |
| Arab world | 4 | 0.0% |
| Sub-Saharan Africa | 3 | 0.0% |

| creator's death (copyright proxy) | items | share |
|---|---|---|
| died before 1926 | 8370 | 83.6% |
| died 1926-1955 | 875 | 8.7% |
| died after 1955 | 489 | 4.9% |
| anonymous or undated creator, work before 1850 | 197 | 2.0% |
| unknown | 47 | 0.5% |
| living (no death date, born 1920+) | 31 | 0.3% |

Top 30 by collection: together 45.2% of the set; top 10 29.1%; 1422 distinct; 78 with 20 or more works; 32 with 50 or more.

| collection | items | share |
|---|---|---|
| Department of Paintings of the Louvre | 526 | 5.3% |
| Museo del Prado | 440 | 4.4% |
| Metropolitan Museum of Art | 377 | 3.8% |
| National Gallery | 337 | 3.4% |
| Uffizi Gallery | 240 | 2.4% |
| Musée d'Orsay | 240 | 2.4% |
| Hermitage Museum | 223 | 2.2% |
| National Gallery of Art | 219 | 2.2% |
| Tretyakov Gallery | 161 | 1.6% |
| Tate | 146 | 1.5% |
| Kunsthistorisches Museum | 143 | 1.4% |
| Gemäldegalerie Berlin | 127 | 1.3% |
| Bavarian State Painting Collections | 114 | 1.1% |
| Rijksmuseum | 112 | 1.1% |
| Museo di Capodimonte | 99 | 1.0% |
| Gallerie dell'Accademia | 80 | 0.8% |
| Pinacoteca di Brera | 79 | 0.8% |
| Russian Museum | 78 | 0.8% |
| Royal Collection | 78 | 0.8% |
| Museum of Fine Arts of Lyon | 77 | 0.8% |
| Museum of Modern Art | 72 | 0.7% |
| Art Institute of Chicago | 70 | 0.7% |
| Pushkin Museum of Fine Arts | 69 | 0.7% |
| Galleria Palatina | 64 | 0.6% |
| J. Paul Getty Museum | 63 | 0.6% |
| Museu Nacional d'Art de Catalunya | 62 | 0.6% |
| Thyssen-Bornemisza Museum | 60 | 0.6% |
| Staatliche Kunstsammlungen Dresden | 59 | 0.6% |
| Royal Museum of Fine Arts Antwerp | 58 | 0.6% |
| Nationalmuseum | 56 | 0.6% |

Top 30 by creator: together 30.6% of the set; top 10 16.1%; 1503 distinct; 113 with 20 or more works; 41 with 50 or more.

| creator | items | share |
|---|---|---|
| Francisco Goya | 250 | 2.5% |
| Vincent van Gogh | 207 | 2.1% |
| Titian | 194 | 1.9% |
| El Greco | 190 | 1.9% |
| Rembrandt | 184 | 1.8% |
| Peter Paul Rubens | 159 | 1.6% |
| Pierre-Auguste Renoir | 111 | 1.1% |
| Claude Monet | 109 | 1.1% |
| Raphael | 105 | 1.0% |
| Diego Velázquez | 99 | 1.0% |
| Édouard Manet | 98 | 1.0% |
| Amedeo Modigliani | 86 | 0.9% |
| Sandro Botticelli | 85 | 0.8% |
| Paul Gauguin | 85 | 0.8% |
| Caravaggio | 82 | 0.8% |
| Gustave Courbet | 80 | 0.8% |
| Jean-Auguste-Dominique Ingres | 80 | 0.8% |
| Giovanni Bellini | 80 | 0.8% |
| Lorenzo Lotto | 77 | 0.8% |
| Anthony van Dyck | 74 | 0.7% |
| Pablo Picasso | 68 | 0.7% |
| Jacques-Louis David | 65 | 0.6% |
| Paul Cézanne | 65 | 0.6% |
| Salvador Dalí | 64 | 0.6% |
| Bartolomé Esteban Murillo | 64 | 0.6% |
| Pietro Perugino | 62 | 0.6% |
| Jean-Léon Gérôme | 61 | 0.6% |
| Wassily Kandinsky | 60 | 0.6% |
| Gustav Klimt | 58 | 0.6% |
| Andrea Mantegna | 58 | 0.6% |

### T2.5k: raw sitelinks >= 8 (n = 2,551)

| property | items | share |
|---|---|---|
| image (P18) | 2460 | 96.4% |
| English Wikipedia article | 2457 | 96.3% |
| creator (P170) stated | 2522 | 98.9% |
| inception (P571) | 2546 | 99.8% |
| collection (P195) or location (P276) | 2478 | 97.1% |
| depicts (P180), at least one | 2322 | 91.0% |
| height and width (P2048 + P2049) | 2472 | 96.9% |
| material (P186) | 2491 | 97.6% |
| part of (P361) something | 152 | 6.0% |
| in a series (P179) | 68 | 2.7% |
| has parts (P527) | 43 | 1.7% |
| has a Commons sitelink | 2212 | 86.7% |
| has an Egyptian Arabic (arz) sitelink | 1469 | 57.6% |
| has a Kotava (avk) sitelink | 294 | 11.5% |
| also typed as something that is not a flat painting | 9 | 0.4% |

| century of inception | items | share |
|---|---|---|
| before 1300 | 12 | 0.5% |
| 14th c. | 11 | 0.4% |
| 15th c. | 270 | 10.6% |
| 16th c. | 526 | 20.6% |
| 17th c. | 449 | 17.6% |
| 18th c. | 136 | 5.3% |
| 19th c. | 871 | 34.1% |
| 20th c. | 265 | 10.4% |
| 21st c. | 4 | 0.2% |
| no date | 5 | 0.2% |

| tradition (creator citizenship, else origin) | items | share |
|---|---|---|
| Western Europe | 2334 | 91.5% |
| Russia / Eastern Europe | 92 | 3.6% |
| North America (US/Canada) | 84 | 3.3% |
| unknown | 15 | 0.6% |
| Latin America | 10 | 0.4% |
| China | 4 | 0.2% |
| Japan | 3 | 0.1% |
| Southeast Asia | 2 | 0.1% |
| Korea | 2 | 0.1% |
| South Asia | 2 | 0.1% |
| Ottoman / Turkey | 1 | 0.0% |
| Ancient / Byzantine | 1 | 0.0% |
| Arab world | 1 | 0.0% |

| creator's death (copyright proxy) | items | share |
|---|---|---|
| died before 1926 | 2256 | 88.4% |
| died 1926-1955 | 160 | 6.3% |
| died after 1955 | 99 | 3.9% |
| anonymous or undated creator, work before 1850 | 27 | 1.1% |
| unknown | 5 | 0.2% |
| living (no death date, born 1920+) | 4 | 0.2% |

Top 30 by collection: together 57.0% of the set; top 10 38.4%; 483 distinct; 22 with 20 or more works; 9 with 50 or more.

| collection | items | share |
|---|---|---|
| Department of Paintings of the Louvre | 158 | 6.2% |
| Museo del Prado | 156 | 6.1% |
| National Gallery | 135 | 5.3% |
| Metropolitan Museum of Art | 118 | 4.6% |
| Musée d'Orsay | 85 | 3.3% |
| Uffizi Gallery | 78 | 3.1% |
| National Gallery of Art | 76 | 3.0% |
| Kunsthistorisches Museum | 64 | 2.5% |
| Hermitage Museum | 62 | 2.4% |
| Gemäldegalerie Berlin | 47 | 1.8% |
| Bavarian State Painting Collections | 45 | 1.8% |
| Tretyakov Gallery | 42 | 1.6% |
| Tate | 41 | 1.6% |
| Rijksmuseum | 33 | 1.3% |
| Museo di Capodimonte | 27 | 1.1% |
| Gallerie dell'Accademia | 26 | 1.0% |
| Galleria Palatina | 25 | 1.0% |
| Staatliche Kunstsammlungen Dresden | 23 | 0.9% |
| Pinacoteca di Brera | 23 | 0.9% |
| Museum of Modern Art | 22 | 0.9% |
| Van Gogh Museum | 22 | 0.9% |
| Art Institute of Chicago | 21 | 0.8% |
| Museum of Fine Arts Boston | 19 | 0.7% |
| Philadelphia Museum of Art | 18 | 0.7% |
| Russian Museum | 17 | 0.7% |
| J. Paul Getty Museum | 15 | 0.6% |
| Pushkin Museum of Fine Arts | 15 | 0.6% |
| Statens Museum for Kunst | 14 | 0.5% |
| Royal Museums of Fine Arts of Belgium | 13 | 0.5% |
| Galleria Borghese | 13 | 0.5% |

Top 30 by creator: together 48.7% of the set; top 10 26.0%; 422 distinct; 34 with 20 or more works; 10 with 50 or more.

| creator | items | share |
|---|---|---|
| Vincent van Gogh | 91 | 3.6% |
| Raphael | 85 | 3.3% |
| Titian | 76 | 3.0% |
| Rembrandt | 70 | 2.7% |
| Caravaggio | 69 | 2.7% |
| El Greco | 59 | 2.3% |
| Francisco Goya | 55 | 2.2% |
| Peter Paul Rubens | 55 | 2.2% |
| Diego Velázquez | 52 | 2.0% |
| Édouard Manet | 50 | 2.0% |
| Pierre-Auguste Renoir | 45 | 1.8% |
| Pieter Brueghel the Elder | 38 | 1.5% |
| Johannes Vermeer | 36 | 1.4% |
| Sandro Botticelli | 36 | 1.4% |
| Claude Monet | 36 | 1.4% |
| Gustave Courbet | 32 | 1.3% |
| Jacques-Louis David | 32 | 1.3% |
| Jean-Auguste-Dominique Ingres | 32 | 1.3% |
| Albrecht Dürer | 29 | 1.1% |
| Paul Gauguin | 28 | 1.1% |
| Hieronymus Bosch | 27 | 1.1% |
| William-Adolphe Bouguereau | 27 | 1.1% |
| Salvador Dalí | 25 | 1.0% |
| Giovanni Bellini | 25 | 1.0% |
| Artemisia Gentileschi | 23 | 0.9% |
| Paul Cézanne | 22 | 0.9% |
| John William Waterhouse | 22 | 0.9% |
| Jean-Léon Gérôme | 22 | 0.9% |
| Dante Gabriel Rossetti | 22 | 0.9% |
| Leonardo da Vinci | 21 | 0.8% |

## C. Quirks

Sitelinks in T10k by site, top 25: enwiki 7,148, commonswiki 6,840, frwiki 6,536, itwiki 4,585, eswiki 4,177, jawiki 3,272, ruwiki 3,086, arzwiki 2,355, plwiki 1,804, nlwiki 1,476, hewiki 1,429, kowiki 1,422, cawiki 1,340, ptwiki 1,336, hywiki 1,321, ukwiki 1,185, dewiki 1,180, svwiki 1,071, mlwiki 1,027, fawiki 950, zhwiki 904, avkwiki 771, arwiki 708, euwiki 705, slwiki 646

T10k items that fall below 3 once Commons, sister projects and the stub editions (arz, avk, ceb, war) are not counted: **1,954 of 10,009** (19.5%). Their top collections: Department of Paintings of the Louvre 115, National Gallery 51, Musée d'Orsay 50, Uffizi Gallery 48, Museo del Prado 48, National Gallery of Art 43, Gemäldegalerie Berlin 33, Metropolitan Museum of Art 32. Their top creators: Francisco Goya 71, Vincent van Gogh 66, Amedeo Modigliani 46, Gustave Courbet 36, Rembrandt 35, Titian 30, Moretto da Brescia 28, Peter Paul Rubens 20.

T10k items whose only Wikipedia editions are arz and/or avk: 1; with no Wikipedia edition at all (Commons only etc.): 0.

P31 values among all candidates with clean score >= 3 (n = 8873), top 40: painting 8058, painting series 257, fresco 215, icon 104, triptych 102, polyptych 69, altarpiece 62, mural 59, group of paintings 44, cycle of paintings 37, watercolor painting 36, reredos 32, emakimono 26, diptych 25, wall painting 19, tondo 19, study 14, sculpture 14, winged altarpiece 12, unfinished creative work 12, artwork copy 12, destroyed artwork 12, work of art 10, painted crucifix 10, devotional panel 10, cyclorama 10, prime version 9, lost painting 8, archaeological site 8, drawing 8, visual artwork 8, title of Mary, mother of Jesus 7, panoramic painting 7, byōbu 7, collage 7, artistic theme 6, pastel artwork 6, fresco-secco 6, panel 5, literary work 5

Candidates (clean >= 3) that are part of another candidate (a panel of a polyptych, a scene of a cycle, a version in a group): 177; items typed series / cycle / group: 332, of which also typed painting 19; wall paintings (fresco, mural, cave, rock): 287; flagged not-a-flat-painting: 66.

Best-known series / group items (clean score): The Scream 73; Sunflowers 46; Virgin of the Rocks 44; Portrait paintings of Dr. Gachet 42; Bedroom in Arles 41; The Tower of Babel 36; The Card Players 33; Kondoa Rock Art Sites 33; Napoleon Crossing the Alps 32; Madonna 32; Water Lilies 31; Isle of the Dead 28; Black Paintings 27; Rock Paintings of Sierra de San Francisco 26; paintings by Adolf Hitler 24; Isenheim Altarpiece 23; Rouen Cathedral Series 23; Adam and Eve 23; The Last Judgment 23; The Four Apostles 23

## D. Raw sitelinks against the clean score and against pageviews

| top k | raw vs clean: shared | share | clean vs pageviews: shared | share  |
|---|---|---|---|---|
| 500 | 461 | 92.2% | 319 | 63.8% |
| 1000 | 906 | 90.6% | 653 | 65.3% |
| 2500 | 2332 | 93.3% | 1776 | 71.0% |
| 5000 | 4600 | 92.0% | 4125 | 82.5% |
| 9000 | 8818 | 98.0% | n/a | n/a |

Spearman rank correlation over candidates with clean >= 3 (n = 8,645): raw vs clean 0.959; clean vs 60-day pageviews in 12 editions 0.608; clean vs English pageviews alone 0.608.

Pageview coverage: 8,627 of 8,645 candidates have a view count in at least one of the 12 editions.

Largest falls from the raw top 2,500 when the clean score is used:

| label | creator_label | raw | clean | rank_raw | rank_clean |
|---|---|---|---|---|---|
| Susanna and the Elders | Artemisia Gentileschi | 8 | 5 | 2432 | 3832 |
| The Crowning with Thorns | Caravaggio | 8 | 5 | 2393 | 3763 |
| Portrait of Fra Antonio Martelli | Caravaggio | 8 | 5 | 2376 | 3739 |
| Christ on the Mount of Olives | Caravaggio | 8 | 5 | 2346 | 3702 |
| Aurora Borealis | Frederic Edwin Church | 8 | 5 | 2246 | 3567 |
| The Crucifixion of Saint Andrew | Caravaggio | 8 | 5 | 2236 | 3549 |
| Cart with Red and White Ox | Vincent van Gogh | 9 | 6 | 2111 | 3403 |
| A Road at Saint-Remy with Female Figure | Vincent van Gogh | 9 | 6 | 2107 | 3387 |
| Bonaparte, First Consul | Jean-Auguste-Dominique Ingres | 9 | 6 | 1854 | 2801 |
| Cairn in Snow | Caspar David Friedrich | 9 | 6 | 1939 | 2883 |
| Portrait of Alof de Wignacourt and his Page | Caravaggio | 9 | 6 | 1848 | 2791 |
| The Port of Greifswald | Caspar David Friedrich | 10 | 7 | 1686 | 2526 |
| Cleopatra | Artemisia Gentileschi | 10 | 7 | 1666 | 2470 |
| Madonna and Child | Artemisia Gentileschi | 10 | 7 | 1625 | 2406 |
| Portrait de Madame de Senonnes | Jean-Auguste-Dominique Ingres | 10 | 7 | 1623 | 2397 |

Most-viewed works that the clean score leaves outside its top 2,500:

| label | creator_label | clean | pv60 | rank_clean | rank_pv |
|---|---|---|---|---|---|
| Untitled | Jean-Michel Basquiat | 3 | 29132 | 6056 | 102.0 |
| Number 17A | Jackson Pollock | 3 | 24115 | 6057 | 129.0 |
| The Dream (The Bed) | Frida Kahlo | 5 | 22866 | 3441 | 137.0 |
| Interchange | Willem de Kooning | 6 | 22295 | 2662 | 140.0 |
| Man at the Crossroads | Diego Rivera | 6 | 22256 | 2663 | 142.0 |
| Hellelil and Hildebrand, the meeting on the turret stairs | Frederic William Burton | 3 | 18738 | 6058 | 175.0 |
| Hōryū-ji Kondō Hekiga |  | 3 | 17631 | 6059 | 186.0 |
| Independence or Death | Pedro Américo | 6 | 17476 | 2664 | 187.0 |
| The Sin | Heinrich Lossow | 3 | 17442 | 6060 | 189.0 |
| Shot Sage Blue Marilyn | Andy Warhol | 0 | 17386 | 2665 | 190.0 |
| Pope Makes Love To Lady Mary Wortley Montagu | William Powell Frith | 3 | 16572 | 6061 | 204.0 |
| The Corpses of the De Witt Brothers | Jan de Baen | 4 | 14958 | 4500 | 229.0 |
| Blue Poles | Jackson Pollock | 6 | 14691 | 2666 | 237.0 |
| Study after Velázquez's Portrait of Pope Innocent X | Francis Bacon | 6 | 14674 | 2667 | 238.0 |
| Pandemonium | John Martin | 3 | 13841 | 6062 | 256.0 |

Least-viewed works inside the clean top 2,500 (many editions, few readers):

| label | creator_label | clean | pv60 | rank_clean |
|---|---|---|---|---|
| An Italian Woman with Children by a Stream | Johann Köler | 8 | 44 | 2115 |
| Boys drawing | Sofie Ribbing | 12 | 48 | 982 |
| Karin by the shore | Carl Larsson | 8 | 50 | 2114 |
| Yperite | Jan Theuninck | 8 | 54 | 2113 |
| Midsummer Night near Vejle Fjord | Harald Slott-Møller | 11 | 59 | 1173 |
| The Forest. La Granja | Joaquín Sorolla | 8 | 64 | 2112 |
| Sunrise at Spluga | Carlo Bazzi | 8 | 67 | 2111 |
| The Artist's Mother Ane Hedvig Brøndum in the Red Room | Anna Ancher | 9 | 75 | 1688 |
| Young Gypsy Woman | Carl Huns | 8 | 84 | 2110 |
| Portrait of Diego de Covarrubias y Leiva | El Greco | 8 | 86 | 2109 |
| Pavilion by the Lake |  | 9 | 91 | 1687 |
| murals in Kyiv |  | 12 | 96 | 981 |
| Allegory of the Dutch victory over the Spanish fleet at Gibraltar, 25 April 1607 | Adam Willaerts | 9 | 100 | 1686 |
| Anne Borrow (d.1799) | Joseph Wright of Derby | 0 | 103 | 2108 |
| Refugees | Jēkabs Kazaks | 8 | 108 | 2107 |

## E. Overlap with independent canon lists

| list | QIDs | of which eligible paintings | in raw top 2,500 | in raw top 10,000 | in clean top 2,500 | in clean top 10,000 | no Wikipedia article anywhere | median clean score |
|---|---|---|---|---|---|---|---|---|
| 1001paintings | 581 | 568 | 210 | 305 | 208 (36.6%) | 315 (55.5%) | 197 | 3 |
| aic_boosted | 232 | 231 | 16 | 40 | 18 (7.8%) | 41 (17.7%) | 162 | 0 |
| ap250 | 212 | 45 | 31 | 39 | 35 (77.8%) | 41 (91.1%) | 2 | 17 |
| bbc100 | 100 | 96 | 59 | 74 | 58 (60.4%) | 76 (79.2%) | 10 | 9 |
| cma_highlight | 73 | 70 | 4 | 9 | 3 (4.3%) | 9 (12.9%) | 52 | 0 |
| jp_national_treasure | 254 | 246 | 4 | 37 | 4 (1.6%) | 28 (11.4%) | 160 | 0 |
| met_highlight | 426 | 403 | 61 | 125 | 59 (14.6%) | 125 (31.0%) | 242 | 0 |
| smarthistory | 467 | 348 | 204 | 262 | 212 (60.9%) | 269 (77.3%) | 45 | 9 |
| vital5 | 142 | 130 | 115 | 123 | 128 (98.5%) | 130 (100.0%) | 3 | 28 |

Union of the five editorial lists (vital5, 1001paintings, bbc100, smarthistory, ap250): 967 distinct paintings; 350 are outside the clean top 10,000. By tradition: Western Europe 244, North America (US/Canada) 44, unknown 23, Russia / Eastern Europe 12, Latin America 7, Japan 5, Oceania (settler) 4, South Asia 3, Ottoman / Turkey 2, Ancient / Byzantine 1, Sub-Saharan Africa 1, China 1, Arab world 1, Persia / Iran / Central Asia 1, Korea 1

Examples (first 25 by label): 10pm Saturday; 1943-45 (St Ives, Cornwall); 2. De español y mestiza, castiza. [es]; A Country Home; A Gondola; A Lady and Gentleman Taking Coffee with Children in a Garden; A Norwegian Fishing Village; A Ride for Liberty; A View at the Entrance of the Grand Canal, Venice; A View of Deventer seen from the North-West; A View through a House; A view of the artist's house and garden, in Mills Plains, Van Diemen's Land; Adam and Eve; Adam and Eve; Adoration of the Child Jesus; Adoration of the Shepherds; After the sitting; Akbar celebrates the birth of his second son; Altarpiece of the Church Fathers; American Lake Scene; An Allegory with Venus and Time; Annunciation; Annunciazione [it]; Apple Tree in Blossom; Ariadne Asleep on the Island of Naxos

Paintings named by k of the five editorial lists: k=1: 808, k=2: 110, k=3: 38, k=4: 10, k=5: 1

## F. Non-European coverage

| tradition | in clean top 2,500 | clean >= 5 | clean >= 3 | clean >= 2 | clean >= 2 with image | clean >= 2, image, creator died before 1926 or anonymous pre-1850 |
|---|---|---|---|---|---|---|
| China | 6 | 19 | 40 | 60 | 53 | 47 |
| Japan | 6 | 14 | 36 | 76 | 76 | 67 |
| Korea | 2 | 2 | 6 | 9 | 9 | 7 |
| South Asia | 2 | 8 | 22 | 39 | 34 | 14 |
| Persia / Iran / Central Asia | 0 | 1 | 5 | 10 | 9 | 6 |
| Ottoman / Turkey | 1 | 1 | 3 | 13 | 13 | 11 |
| Arab world | 1 | 2 | 5 | 7 | 5 | 4 |
| Sub-Saharan Africa | 0 | 0 | 4 | 5 | 1 | 0 |
| Southeast Asia | 3 | 6 | 10 | 20 | 18 | 14 |
| Latin America | 14 | 25 | 61 | 124 | 75 | 22 |
| Ancient / Byzantine | 4 | 4 | 8 | 13 | 13 | 9 |
| Russia / Eastern Europe | 97 | 194 | 447 | 734 | 626 | 347 |
| North America (US/Canada) | 91 | 171 | 334 | 579 | 424 | 292 |
| Oceania (settler) | 0 | 5 | 34 | 56 | 31 | 8 |
| Indigenous / pre-Columbian | 0 | 0 | 0 | 1 | 0 | 0 |
| Western Europe | 2226 | 3967 | 7387 | 11235 | 10628 | 9690 |
| unknown | 47 | 80 | 243 | 466 | 410 | 297 |

Depth of the whole Wikidata pool (P31 = painting, any sitelink count), summed over the countries and states each tradition's regex matches. A work can be counted under two states of one tradition, so read these as upper bounds:

| tradition | signal | n_all | n_with_image | n_sitelinks_ge1 |
|---|---|---|---|---|
| Ancient / Byzantine | country_of_origin | 2 | 1 | 0 |
| Ancient / Byzantine | creator_citizenship | 14 | 13 | 10 |
| Arab world | country_of_origin | 315 | 238 | 8 |
| Arab world | creator_citizenship | 975 | 497 | 16 |
| China | country_of_origin | 111197 | 9467 | 208 |
| China | creator_citizenship | 28018 | 8571 | 340 |
| Japan | country_of_origin | 1406 | 1205 | 182 |
| Japan | creator_citizenship | 5263 | 2958 | 191 |
| Korea | country_of_origin | 52 | 50 | 5 |
| Korea | creator_citizenship | 101 | 35 | 13 |
| Latin America | country_of_origin | 1499 | 898 | 335 |
| Latin America | creator_citizenship | 6788 | 3622 | 665 |
| North America (US/Canada) | country_of_origin | 24046 | 10673 | 1226 |
| North America (US/Canada) | creator_citizenship | 75386 | 22470 | 2049 |
| Oceania (settler) | country_of_origin | 20 | 13 | 1 |
| Oceania (settler) | creator_citizenship | 16707 | 1298 | 119 |
| Ottoman / Turkey | country_of_origin | 23 | 11 | 8 |
| Ottoman / Turkey | creator_citizenship | 2005 | 379 | 130 |
| Persia / Iran / Central Asia | country_of_origin | 43 | 29 | 8 |
| Persia / Iran / Central Asia | creator_citizenship | 538 | 194 | 28 |
| Russia / Eastern Europe | country_of_origin | 390 | 276 | 108 |
| Russia / Eastern Europe | creator_citizenship | 78204 | 29189 | 5658 |
| South Asia | country_of_origin | 209 | 198 | 8 |
| South Asia | creator_citizenship | 16530 | 319 | 76 |
| Southeast Asia | country_of_origin | 86 | 14 | 3 |
| Southeast Asia | creator_citizenship | 785 | 98 | 42 |
| Sub-Saharan Africa | country_of_origin | 19 | 9 | 0 |
| Sub-Saharan Africa | creator_citizenship | 581 | 28 | 12 |

## G. Descriptions and facts for the clean top 2,500

| available | works | share of 2,500 |
|---|---|---|
| English Wikipedia article exists | 2427 | 97.1% |
| English lead paragraph of 200 characters or more | 2181 | 87.2% |
| English lead paragraph of 500 characters or more | 1349 | 54.0% |
| an article in at least one of en, es, fr, de, it, ru, ja, zh, pt, ar, ko, fa | 2498 | 99.9% |
| held by a museum with an open API or dump that carries text | 527 | 21.1% |
| neither an English article nor such a museum | 67 | 2.7% |
| Wikidata: creator | 2425 | 97.0% |
| Wikidata: inception | 2478 | 99.1% |
| Wikidata: collection or location | 2401 | 96.0% |
| Wikidata: material | 2396 | 95.8% |
| Wikidata: height and width | 2364 | 94.6% |
| Wikidata: depicts | 2193 | 87.7% |
| Wikidata: image (P18) | 2384 | 95.4% |
| Wikidata: creator + inception + collection + material + dimensions all present | 2235 | 89.4% |

| museum with open text | works in the top 2,500 |
|---|---|
| Louvre (Etalab open licence, French) | 139 |
| National Gallery London (text CC BY 4.0) | 127 |
| Met (data CC0; label text has no stated open licence) | 105 |
| NGA Washington (CC0 open data) | 65 |
| Rijksmuseum (CC0 / CC BY) | 26 |
| AIC (description CC BY 4.0) | 22 |
| Getty (open content) | 13 |
| SMK (CC0) | 13 |
| Nationalmuseum Sweden | 12 |
| Cleveland (CC0) | 5 |

## H. What the recipe yields

Universe: 22,344 painting-like items fetched; excluded: series / cycle / group item 499, panel of a polyptych that is itself a candidate 292, typed as something that is not one flat painting 168; eligible 21,385. Series represented by their best-known member: 322; members whose score was raised to the group's: 252; groups typed painting with no member item (kept, flagged): 4.

### Canon (clean >= 3, cap 40 per painter): 8,851 works

|  | works | share |
|---|---|---|
| by gate: fame | 7073 | 79.9% |
| by gate: tradition floor | 706 | 8.0% |
| by gate: museum highlight / state designation | 705 | 8.0% |
| by gate: editorial list | 367 | 4.1% |
| has an image on Commons (P18) | 7884 | 89.1% |
| image and creator died before 1926 or anonymous pre-1850 (public-domain proxy) | 6670 | 75.4% |
| creator died 1926-1955 | 915 | 10.3% |
| creator died after 1955 or living | 943 | 10.7% |
| copyright proxy unknown | 270 | 3.1% |
| English Wikipedia article | 6016 | 68.0% |
| no Wikipedia article in any language | 914 | 10.3% |
| wall paintings (fresco, mural, cave) | 350 | 4.0% |
| under-represented traditions | 1253 | 14.2% |
| distinct named painters | 1871 | 21.1% |
| largest single painter | 40 | 0.5% |
| largest single collection | Metropolitan Museum of Art 575 |  |
| 20th- and 21st-century works | 1783 | 20.1% |

| tradition | works | share | of which image + public-domain proxy |
|---|---|---|---|
| Western Europe | 6232 | 70.4% | 5427 |
| North America (US/Canada) | 527 | 6.0% | 215 |
| Russia / Eastern Europe | 460 | 5.2% | 232 |
| Latin America | 419 | 4.7% | 82 |
| Japan | 334 | 3.8% | 221 |
| unknown | 326 | 3.7% | 219 |
| China | 204 | 2.3% | 139 |
| South Asia | 76 | 0.9% | 30 |
| Ottoman / Turkey | 66 | 0.7% | 20 |
| Southeast Asia | 46 | 0.5% | 21 |
| Oceania (settler) | 39 | 0.4% | 7 |
| Korea | 36 | 0.4% | 22 |
| Persia / Iran / Central Asia | 35 | 0.4% | 18 |
| Arab world | 19 | 0.2% | 6 |
| Sub-Saharan Africa | 15 | 0.2% | 0 |
| Ancient / Byzantine | 14 | 0.2% | 11 |
| Indigenous / pre-Columbian | 3 | 0.0% | 0 |

By century: before 1400 414 (5%), 15th c. 812 (9%), 16th c. 1119 (13%), 17th c. 1143 (13%), 18th c. 654 (7%), 19th c. 2457 (28%), 20th c. 1725 (19%), 21st c. 82 (1%), undated 427.

Top collections: Metropolitan Museum of Art 575, Department of Paintings of the Louvre 355, National Gallery 287, Museo del Prado 242, Art Institute of Chicago 218, Uffizi Gallery 171, Tretyakov Gallery 154, Musée d'Orsay 150, Hermitage Museum 149, National Gallery of Art 137.

Removed from the canon by the cap of 40: 1,626 works by 48 painters.

### POC (clean >= 6, cap 12 per painter): 2,410 works

|  | works | share |
|---|---|---|
| by gate: fame | 2015 | 83.6% |
| by gate: tradition floor | 277 | 11.5% |
| by gate: editorial list | 118 | 4.9% |
| has an image on Commons (P18) | 2239 | 92.9% |
| image and creator died before 1926 or anonymous pre-1850 (public-domain proxy) | 1929 | 80.0% |
| creator died 1926-1955 | 225 | 9.3% |
| creator died after 1955 or living | 192 | 8.0% |
| copyright proxy unknown | 61 | 2.5% |
| English Wikipedia article | 2150 | 89.2% |
| no Wikipedia article in any language | 55 | 2.3% |
| wall paintings (fresco, mural, cave) | 110 | 4.6% |
| under-represented traditions | 334 | 13.9% |
| distinct named painters | 712 | 29.5% |
| largest single painter | 12 | 0.5% |
| largest single collection | National Gallery 134 |  |
| 20th- and 21st-century works | 412 | 17.1% |

| tradition | works | share | of which image + public-domain proxy |
|---|---|---|---|
| Western Europe | 1743 | 72.3% | 1562 |
| Russia / Eastern Europe | 135 | 5.6% | 76 |
| North America (US/Canada) | 130 | 5.4% | 63 |
| unknown | 61 | 2.5% | 44 |
| China | 60 | 2.5% | 47 |
| Japan | 60 | 2.5% | 53 |
| Latin America | 30 | 1.2% | 5 |
| Ottoman / Turkey | 30 | 1.2% | 12 |
| Korea | 30 | 1.2% | 18 |
| Southeast Asia | 30 | 1.2% | 15 |
| Persia / Iran / Central Asia | 30 | 1.2% | 15 |
| South Asia | 29 | 1.2% | 10 |
| Arab world | 18 | 0.7% | 5 |
| Sub-Saharan Africa | 14 | 0.6% | 0 |
| Ancient / Byzantine | 4 | 0.2% | 3 |
| Oceania (settler) | 3 | 0.1% | 1 |
| Indigenous / pre-Columbian | 3 | 0.1% | 0 |

By century: before 1400 130 (5%), 15th c. 268 (11%), 16th c. 331 (14%), 17th c. 281 (12%), 18th c. 156 (6%), 19th c. 745 (31%), 20th c. 399 (17%), 21st c. 20 (1%), undated 77.

Top collections: National Gallery 134, Department of Paintings of the Louvre 130, Metropolitan Museum of Art 126, Museo del Prado 83, Uffizi Gallery 62, Musée d'Orsay 53, Tretyakov Gallery 51, National Gallery of Art 50, Tate 43, Museum of Modern Art 34.

POC size under other settings (fame gate + editorial list with clean >= 3 + floors), before / after the public-domain proxy:

| clean >= | cap | works | with image + public-domain proxy | under-represented traditions |
|---|---|---|---|---|
| 5 | 8 | 2493 | 1965 | 334 |
| 5 | 12 | 2915 | 2344 | 334 |
| 5 | 15 | 3147 | 2551 | 335 |
| 5 | 25 | 3717 | 3075 | 335 |
| 5 | none | 4840 | 4107 | 335 |
| 6 | 8 | 2089 | 1642 | 334 |
| 6 | 12 | 2410 | 1929 | 334 |
| 6 | 15 | 2595 | 2097 | 335 |
| 6 | 25 | 3050 | 2513 | 335 |
| 6 | none | 3836 | 3240 | 335 |
| 7 | 8 | 1805 | 1406 | 334 |
| 7 | 12 | 2059 | 1638 | 334 |
| 7 | 15 | 2210 | 1777 | 335 |
| 7 | 25 | 2566 | 2100 | 335 |
| 7 | none | 3114 | 2612 | 335 |
| 8 | 8 | 1608 | 1241 | 334 |
| 8 | 12 | 1813 | 1430 | 334 |
| 8 | 15 | 1937 | 1542 | 335 |
| 8 | 25 | 2232 | 1808 | 335 |
| 8 | none | 2603 | 2162 | 335 |

Per-tradition floor in the POC: pool and what was taken.

| tradition | in POC by fame alone | pool: any Wikipedia article or any listing | pool with image + public-domain proxy | floor asked | in POC | in canon |
|---|---|---|---|---|---|---|
| Arab world | 1 | 19 | 6 | 30 | 18 | 19 |
| China | 13 | 204 | 139 | 60 | 60 | 204 |
| Indigenous / pre-Columbian | 0 | 3 | 0 | 30 | 3 | 3 |
| Japan | 9 | 334 | 221 | 60 | 60 | 334 |
| Korea | 2 | 36 | 22 | 30 | 30 | 36 |
| Latin America | 19 | 419 | 82 | 30 | 30 | 419 |
| Ottoman / Turkey | 1 | 66 | 20 | 30 | 30 | 66 |
| Persia / Iran / Central Asia | 1 | 35 | 18 | 30 | 30 | 35 |
| South Asia | 4 | 76 | 30 | 30 | 29 | 76 |
| Southeast Asia | 5 | 46 | 21 | 30 | 30 | 46 |
| Sub-Saharan Africa | 0 | 15 | 0 | 30 | 14 | 15 |

`candidates.csv`: 15,044 rows (every eligible item with clean >= 2, or on any list, or in either set). `excluded.csv`: 381 items with clean >= 3 that the universe rules removed.

# Appendix: the queries

Total (query.wikidata.org): `SELECT (COUNT(*) AS ?n) WHERE { ?p wdt:P31 wd:Q3305213 }` gives 1,084,295.

Histogram (QLever): `SELECT ?s (COUNT(?p) AS ?n) WHERE { ?p wdt:P31 wd:Q3305213 . ?p wikibase:sitelinks ?s } GROUP BY ?s ORDER BY ?s`

Candidates (QLever): `SELECT ?p ?s WHERE { ?p wdt:P31 wd:Q3305213 . ?p wikibase:sitelinks ?s . FILTER(xsd:integer(?s) >= 1) }`, and the same with `?c wdt:P279+ wd:Q3305213 . ?p wdt:P31 ?c` for subclasses.

Lists (query.wikidata.org): `?i wdt:P1343 wd:Q66362718` (1001 Paintings); `?i p:P528 ?s . ?s pq:P972 wd:Q121297196` (BBC 100); `?i wdt:P6405 []` (Smarthistory); `?i wdt:P1435 wd:Q1188622 . ?i wdt:P31/wdt:P279* wd:Q3305213` (National Treasures of Japan); museum flags joined on P3634 and P4610.

Pool by country (QLever): paintings grouped by `wdt:P170/wdt:P27` and by `wdt:P495`, counting all, those with P18, and those with a sitelink.

Facts: `wbgetentities` with `props=labels|descriptions|claims|sitelinks`. The clean score is the count of sitelink keys ending in `wiki`, less `commonswiki`, other non-Wikipedia projects, and `arzwiki`, `avkwiki`, `cebwiki`, `warwiki`.

Pageviews: `action=query&prop=pageviews&pvipdays=60` on each of en, es, fr, de, it, ru, ja, zh, pt, ar, ko, fa.
