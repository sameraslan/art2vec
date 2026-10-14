# Prose and Telling: which measurements pass their rows

Experiments 1 and 2 of FRAMEWORK.md section 11, on the 87 public-domain novels of
`testbed.csv`. Everything here is counted from the prepared token tables; no neural model is
used. Code: `eval/` (the scoring harness, shared with the other experiments), `prose/`,
`telling/`. Block files: `data/blocks/`. Per-run CSVs sit next to this file.

## How to read the numbers

- **AUC** is the probability that a labelled pair is closer than a negative pair. Negatives are
  the 3,663 pairs of books by different authors that are not related by translation, edition,
  series or retelling. 0.5 is chance. Brackets are a 95% bootstrap over the labelled pairs
  only; pairs that share a book are not independent, so the brackets are somewhat too narrow.
- Pair sets are small: 10 translation pairs (8 works; Don Quixote gives 3), 1 edition pair, 52
  same-author pairs with unrelated plots (33 of them written in English), 7 series pairs, 8
  retelling pairs, 11 same-translator pairs (all Garnett), 261 same-genre pairs. With 7 to 10
  pairs an AUC moves by about 0.1 when one pair changes. Differences smaller than that are
  noise unless the paired interval says otherwise.
- **Split a/b** and **h1/h2**: a book's odd-numbered 1,000-word chunks must retrieve its
  even-numbered chunks among all 87 books (a/b), or its first half its second (h1/h2).
  Accuracy; chance is 1/87.
- "Flagged" books are the three whose quotation marks the prep could not read:
  `joyce_ulysses` (dash dialogue, dialogue share 0.00), `wells_time` (framed narration, 0.87),
  `wyss_swiss` (0.02). They are kept in every table; the Telling tables are given a second time
  without them.

## Headline

| | Prose: `P4_mfw500_tag3_rhythm` | Telling: `T3_scalars_dtw20_sd` | Framework expects (Prose / Telling) |
|---|---|---|---|
| Split halves a/b, accuracy (87 books) | 0.97 | 0.74 | near / near |
| Split halves h1/h2, accuracy | 0.91 | not defined for curves; 0.71 for the scalars alone | near / near |
| Translation pairs, AUC (10 pairs) | 1.00 [1.00, 1.00] | 0.99 [0.97, 1.00] | **apart** / near |
| Same author, unrelated plots, AUC (52 pairs) | 0.99 [0.98, 0.99] | 0.72 [0.65, 0.79] | near / (none) |
| Series, AUC (7 pairs) | 1.00 [0.99, 1.00] | 0.78 [0.61, 0.92] | near / near |
| Retelling, AUC (8 pairs) | 0.73 [0.44, 0.95] | 0.45 [0.23, 0.69] | apart / (none) |
| Same genre, different author, AUC (261 pairs) | 0.61 [0.57, 0.65] | 0.52 [0.49, 0.56] | control |
| Spearman with abs. year difference, English originals, different authors | 0.31 | 0.05 | |
| Spearman with abs. log word-count difference | 0.05 | 0.05 | |
| Spearman between the two blocks' pair distances (3,741 pairs) | 0.32 | | |

Three things stand out.

1. **Prose does not put two translations of one novel apart.** Every Prose candidate ranks a
   second translation of the same novel as the nearest or second-nearest book (table
   "Translation pairs, rank of the partner"). A translation pair is closer than a same-author
   pair with probability 0.76 to 0.85 for the word and tag blocks (10 against 52 pairs); the
   median translation-pair distance is 0.5 to 0.7 of the median same-author distance. The
   framework's row "two translations: apart" fails for every count-based Prose measurement
   tried. Only the rhythm block (punctuation, sentence and word lengths) moves in the expected
   direction (0.58; AUC against negatives 0.87 [0.72, 0.99]), and it is the weakest block on
   every other row.
2. **The published claim holds: translations group by original author before translator.**
   For the six Garnett books, the nearest book that is not the same work is by the same
   original author in 6 of 6 cases for the word and tag blocks (5 of them also Garnett; for
   Anna Karenina it is a Maude Tolstoy, ahead of every Garnett Dostoevsky and Turgenev). The
   pair-level contest is weaker than that sounds: a same-author / different-translator pair
   (14) beats a same-translator / different-author pair (11) with probability 0.75 for the
   500-word and trigram blocks, 0.60 for the 100-word block. Garnett pairs by different
   authors are themselves very close (AUC 0.95 against negatives), so both signatures are
   present; the author's is the stronger of the two.
3. **Telling is two things.** The scalars (person, tense, dialogue share, questions) overlap
   with Prose (Spearman 0.41 with P4) and their same-author signal is mostly Prose again: with
   the Prose distance regressed out it falls from 0.76 to 0.58. The curves over the book
   (dialogue, sentence length, sentiment, new vocabulary) are almost unrelated to Prose
   (Spearman 0.11), carry no author signal (0.60 [0.52, 0.68]) and no genre signal (0.48),
   and still find translation pairs (0.97 [0.94, 1.00]; 0.92 with Prose regressed out). The
   curves are close to a fingerprint of the particular work; they say little about which other
   works are told alike.

## Prose

### What was built

| Block | What it is | Input level |
|---|---|---|
| `P1_mfw{100,200,500}_{all,narr}_{raw,noprop}_{cull,nocull}` (24) | Cosine Delta: z-scored relative frequencies of the N most frequent words, cosine distance. narr = narration only; noprop = proper nouns and words capitalised mid-sentence removed first; cull = word must occur in at least half of the books | `all_raw`: book bag. Everything else: ordered text (quotation marks, sentence position) |
| `P2_tag3_{500,1000}[_words]` | z-scored frequencies of the most frequent fine-tag trigrams, cosine; `_words` drops punctuation from the sequence | ordered text |
| `P3_rhythm` and its parts `P3_punct`, `P3_sentence`, `P3_lexical` | 40 z-scored numbers: 10 punctuation rates (quote marks left out), sentence-length mean / sd / quantiles / lag-1 autocorrelation, paragraph length, MTLD, MATTR-500, word-length distribution; Euclidean | ordered text (punctuation rates and word lengths alone would be a bag) |
| `P4_mfw500_tag3`, `P4_mfw500_tag3_rhythm`, `P4_mfw100_tag3_rhythm` | mean of the parts' distance matrices, each divided by its median | ordered text |

### Reading

- **Word profiles (P1).** All 24 variants score between 0.96 and 0.99 on same-author pairs
  and 1.00 on translation pairs. Culling changes nothing (the top 500 words are in more than
  half of the books already). Removing proper nouns changes nothing measurable (same-author
  AUC 0.990 against 0.990 at 500 words): names are too rare individually to reach the list.
  So the plain version, which needs only a bag of words per book, is as good as the ones that
  need running text. Narration-only is slightly worse on same-author pairs (-0.012, interval
  [-0.025, 0.000]) and is the variant that the quotation failures damage; nothing argues for
  it.
- **More words bring topic in.** Going from 100 to 500 words raises same-author AUC by 0.01
  (within noise) but raises retelling from 0.88 to 0.97 (paired difference 0.09, interval
  [0.03, 0.16], 8 pairs) and same-genre from 0.63 to 0.68 (interval [0.04, 0.07], 261 pairs).
  The framework wants Prose to leave a retelling apart from its source; the 500-word list
  does the opposite. Retelling AUCs are high for every word list partly because five of the
  eight retelling pairs are Robinsonades, all first-person journals of survival: the person
  and tense of the narration sit in the most frequent words.
- **Tag trigrams (P2)** are a little weaker on authors (0.97 [0.95, 0.99]; -0.02 against
  P1-500, interval [-0.03, -0.00]) and clearly lower on retellings (0.77 [0.59, 0.92]) and on
  same-translator pairs (0.88). They agree with the word profile (Spearman 0.79) without
  repeating it. Keeping punctuation in the sequence helps slightly.
- **Rhythm (P3)** is the weakest author signal (0.90 [0.85, 0.93]), ignores retellings (0.50)
  and genre (0.51), and is the one most tied to period over all 87 books (Spearman 0.39 with
  year difference). Its a/b split accuracy is 0.97 but h1/h2 only 0.85: rhythm drifts within
  a book. The sentence-length part alone is poor (a/b 0.79, h1/h2 0.43).
- **Combination (P4).** Averaging word profile, trigrams and rhythm keeps same-author at 0.99
  and series at 1.00, and lowers retelling to 0.73 [0.44, 0.95] and same-genre to 0.61
  (against P1-500: -0.24 [-0.52, -0.02] and -0.07 [-0.10, -0.05]). That is the profile the
  framework's table asks for, apart from the translation row. `P4_mfw100_tag3_rhythm` is
  indistinguishable from it. I would take `P4_mfw500_tag3_rhythm` forward as the count-based
  Prose block, with `P1_mfw500_all_raw_nocull` as the fallback where only word counts exist.
- **Period.** Among books written in English by different authors, Spearman between Prose
  distance and year difference is 0.21 for the word profile, 0.25 for trigrams and rhythm,
  0.31 for P4: between 4% and 9% of the variance of the ranks. A book's five nearest
  neighbours are on average 27 to 34 years away from it; a random book is 56 years away. The
  period is in the block, as section 8 says it will be, and it is not most of the block. The
  `year` column is the year of the original for translations (1605 for an 1885 Don Quixote),
  so the all-books figures understate or misstate the period effect for translated books;
  the English-only figures are the ones to trust.
- **Length** does not separate books: Spearman with log word-count difference is 0.08 or less
  for every Prose block.
- **Neighbours.** 40% of top-5 neighbours are by the same author (chance 2.5%); 38% to 47%
  share a genre tag (chance 12%). Hubness is mild: skew of the 5-nearest in-degree 0.3 for the
  word profile and 1.0 for P4; 2% of books are in nobody's top 5.

### How many words

80 books of at least 50,000 words; random non-contiguous samples made of runs of whole
sentences of about 100 words; vectors z-scored across the sampled books; 5 seeds. Full table
below. For P4:

| Words sampled | Spearman with whole-book distances | Same-author AUC (45 pairs) | Translation AUC (10 pairs) | A second disjoint sample of the same book is the nearest |
|---|---|---|---|---|
| 1,000 | 0.64 | 0.84 | 0.81 | 0.58 |
| 2,000 | 0.77 | 0.92 | 0.92 | 0.83 |
| 5,000 | 0.89 | 0.96 | 0.99 | 0.94 |
| 10,000 | 0.94 | 0.975 | 1.00 | 0.975 |
| 20,000 | 0.97 | 0.98 | 1.00 | 0.98 |
| 50,000 | 0.99 | 0.985 | 1.00 | |
| whole book | 1 | 0.986 | 1.00 | |

Seed-to-seed sd is 0.02 at 1,000 words and 0.003 or less from 10,000. **About 10,000 sampled
words give essentially the whole-book result** (same-author AUC within 0.01, Spearman 0.94);
5,000 is usable; below 2,000 the block is mostly noise. The word profile and the trigrams
converge at the same rate. The vocabulary was chosen on the whole corpus, which flatters the
small sizes slightly.

## Telling

### What was built

| Block | What it is | Input level |
|---|---|---|
| `T1_scalars` | 12 z-scored numbers: dialogue share; first-singular, first-plural, second and third person pronouns per 1,000 narration words; past share of finite verbs in narration (VBD against VBP + VBZ); share of sentences ending in ? and in !; log mean chapter length; share of paragraphs of 20 words or fewer; clock / calendar words and sequence words per 1,000 narration words. Euclidean | ordered text |
| `T1_scalars_noquote` | the same with every narration-only count replaced by the all-text count and no dialogue share | ordered text |
| `T1_bag` | 9 numbers from word and tag totals only: person, tense, ? and ! per 1,000 words, time words | **book bag** |
| `T2_curves{20,50}_euc`, `_dtw` | six curves over the book in 20 or 50 equal segments (dialogue share, mean log sentence length, VADER mean valence, mean absolute valence as an arousal proxy, first-person rate in narration, share of new word types), each z-normalised within the book; Euclidean on the concatenation, or DTW with a band of a tenth of the length | ordered text |
| `T2_{curve}20` | one curve at a time | ordered text |
| `T2_shape`, `T2_shape_nosd` | per 50-segment curve: slope, sd, position of min and max, DCT coefficients 1 to 4; z-scored, Euclidean. `_nosd` leaves the sd out | ordered text |
| `T3_*` | means of scaled distance matrices; `_sd` scales each part by the sd of its distances instead of the median | ordered text |

Chapter headings were found by pattern in the clean text; fewer than three were found for
`burnett_sara_crewe`, `faulkner_sound`, `oz_land` and `woolf_dalloway`, which get the median.
`joyce_ulysses` gets four "chapters" (its three parts), which is wrong for a book of eighteen
episodes.

### Reading

- **Scalars survive translation.** `T1_scalars` puts translation pairs at 0.98 [0.95, 1.00]
  (the partner is the nearest book for 88% of the 17 books involved), `T1_bag` at 1.00
  [0.99, 1.00]. They also carry author (0.76 [0.68, 0.83]) and series (0.86 [0.74, 0.98]),
  and almost no genre (0.56). The a/b split is 0.90, h1/h2 0.71 for the full set and 0.49 for
  the bag: how a book is told changes between its halves more than how its sentences are
  written.
- **The bag version loses nothing measurable.** `T1_bag` against `T1_scalars`: translation
  +0.02, same-author +0.03, series +0.01, all inside the paired intervals. Person, tense,
  question and exclamation rates and time words can therefore be computed for in-copyright
  books from per-page word and tag counts. Dialogue share and chapter length cannot.
- **Curves survive translation and carry nothing else.** DTW on 20 segments: translation 0.97
  [0.94, 1.00], same-author 0.60, series 0.56 [0.33, 0.76], genre 0.48. 50 segments is not
  better than 20, and DTW is not reliably better than Euclidean (0.97 against 0.95 on 10
  pairs). Single curves each reach 0.77 to 0.92 on translation pairs with intervals 0.25 wide;
  the first-person curve is the worst (0.77), because in a third-person novel it is the
  z-normalised noise of a handful of tokens. The shape summary (`T2_shape`) reaches 1.00
  [1.00, 1.00] on translation pairs.
- **A length leak, found and removed.** `T2_shape` has Spearman 0.22 with word-count
  difference: the sd of a raw curve grows as segments get shorter, so short books look alike.
  Without the sd features (`T2_shape_nosd`) the figure is 0.12 and translation AUC is still
  1.00 [0.99, 1.00]. The remaining 0.12 comes from the new-vocabulary curve, whose shape
  depends on length by Heaps' law (0.16 on its own). Translations of one work have nearly the
  same length, so part of the curves' success on translation pairs may be length; I did not
  separate the two.
- **Split halves are weak for curves** (a/b 0.55 for DTW-20, 0.75 for Euclidean-50): a curve
  estimated from every other 1,000-word chunk is noisy at 20 to 50 segments. The curves are
  not a stable measurement of a book at this resolution, even though two translations (twice
  the data, same order of events) agree.
- **Hubness** is worse than in Prose: `T2_shape_nosd` has one book (`fathers_garnett`) in 35
  top-5 lists and 15% of books in none; single curves with flat profiles (dialogue, first
  person) have in-degree skew above 7 when the flagged books are in.
- **Combination.** With median scaling the scalars swamp the curves (the combination
  correlates 0.96 with the scalars), because DTW distances are all nearly equal. Scaling by
  sd gives `T3_scalars_dtw20_sd`, which correlates 0.74 with the scalars and 0.77 with the
  curves: translation 0.99 [0.97, 1.00], same-author 0.72 [0.65, 0.79], series 0.78, genre
  0.52, Spearman with Prose 0.32.
- **Flagged books.** Leaving out the three flagged books changes translation, same-author and
  series AUCs by 0.02 or less. It changes retelling (8 pairs to 5, since `wyss_swiss` is in
  three): 0.41 to 0.60 for the scalars, both with intervals 0.5 wide. `T1_scalars_noquote`,
  which never uses quotation marks, is as good as `T1_scalars` or slightly better (same-author
  +0.07, interval [+0.02, +0.13]).

### Is Telling just Prose again?

Partly. From the table "Telling against Prose" below (3,741 pairs):

| Telling block | Spearman with P4 | Translation AUC, raw / with Prose regressed out | Same-author AUC, raw / with Prose regressed out |
|---|---|---|---|
| `T1_scalars` | 0.41 | 0.98 / 0.82 | 0.76 / 0.58 |
| `T1_bag` | 0.45 | 1.00 / 0.83 | 0.79 / 0.59 |
| `T2_curves20_dtw` | 0.11 | 0.97 / 0.92 | 0.60 / 0.55 |
| `T2_shape_nosd` | 0.14 | 1.00 / 0.94 | 0.58 / 0.51 |
| `T3_scalars_dtw20_sd` | 0.32 | 0.99 / 0.86 | 0.72 / 0.57 |

The scalars share 15% to 20% of their rank variance with Prose and the curves 1% to 2%, mostly through the rhythm block
(Spearman 0.47 between `T1_scalars` and `P3_rhythm`, 0.2 with the word and tag blocks). What
is left after Prose still finds translation pairs and no longer finds authors. In the other
direction, Prose with Telling regressed out keeps same-author at 0.90. So the two blocks are
distinguishable, and the part of Telling that is not Prose is about the work.

The weak side: Telling's own row in the framework's table has only "translations near" and
"series near" to pass, and nothing here shows that Telling neighbours which are not the same
work are told alike in a way a reader would recognise. The pair sets cannot test that. Series
at 0.78 to 0.86 on 7 pairs is the only evidence, and Prose scores 1.00 on the same pairs.

## What I would take forward

- **Prose:** `P4_mfw500_tag3_rhythm` (ordered text; about 10,000 sampled words suffice), and
  `P1_mfw500_all_raw_nocull` or the 100-word version as the book-bag fallback. Drop
  narration-only, culling and name removal: no measurable gain. A style encoder still has to
  be tried by the later job; it is the only candidate left that might put translations apart.
- **Telling:** `T1_scalars_noquote` or `T1_bag` as the scalar part (robust to the quotation
  failures, the bag one computable for in-copyright books), plus `T2_curves20_dtw` as a
  separate, clearly labelled part. I would not ship the median-scaled combinations.
- **The framework's table needs one cell changed or one measurement added.** "Two
  translations of one novel: Prose apart" is false for function words, tag sequences and
  rhythm. Relative to the other block it half-holds: against same-author pairs, translation
  pairs win with probability 0.76 in Prose and 0.94 in Telling.

## What failed or is within noise

- Prose "translations apart": failed for every candidate.
- 100 against 200 against 500 words on same-author pairs: within noise (0.98 to 0.99).
- Culling, name removal: no effect. Narration-only: slightly worse.
- DTW against Euclidean, 20 against 50 segments: within noise on 10 translation pairs.
- Retelling AUCs for every block: intervals 0.3 to 0.5 wide on 8 pairs, 5 of which are one
  cluster of Robinsonades. Only the P1-500 against P4 difference clears its own interval.
- The edition pair (two Frankensteins) is one pair; every block puts it at 1.00 and it tests
  nothing.
- `same_author_same_translator` (5 pairs) and the Garnett counts (6 books) are too small for
  more than a direction.
- The first-person curve and the 50-segment curves add noise.

## Data notes

- `dq_smollett` still has footnote paragraphs ("Footnote 13:") in the clean text; the prep
  was not touched. It did not stop any block from pairing it with the other two Quixotes.
- `dq_motteux` is an edited, shorter text (221k words against 411k and 420k); its curves align
  worst (rank 6 to 18 in DTW).
- `journey_1871` is tagged as a rewrite, yet every block puts it nearest to `journey_malleson`.
- Typography differs by source (curly against straight quotes); apostrophes are folded before
  counting and quote marks are left out of the punctuation rates.
- `vaderSentiment` (lexicon only, pure Python) was added to the venv and to
  `requirements.txt`. No model was downloaded.

## Reproduce

    .venv/bin/python -m eval.test_harness      # synthetic check of the harness
    .venv/bin/python -m prose.tokens           # data/feat/<key>.npz, one book at a time
    .venv/bin/python -m prose.build            # P1, P2, P3
    .venv/bin/python -m telling.build          # T1, T2
    .venv/bin/python -m eval.combine P4_mfw500_tag3_rhythm P1_mfw500_all_noprop_nocull P2_tag3_1000 P3_rhythm
    .venv/bin/python -m eval.combine T3_scalars_dtw20_sd T1_scalars T2_curves20_dtw --scale sd
    .venv/bin/python -m eval.score BLOCK ... --tag NAME [--ref BLOCK] [--exclude-flagged]
    .venv/bin/python -m prose.convergence
    .venv/bin/python -m prose.translator BLOCK ...
    .venv/bin/python -m telling.vs_prose P4_mfw500_tag3_rhythm BLOCK ...

Each step is a single process and holds one book at a time; the whole chain takes about four
minutes.

# Full tables

## Translation pairs, rank of the partner

Rank of each book's partner among the other 86 books, in both directions (1 = nearest).

| pair | P1 mfw500 | P2 tag3 | P3 rhythm | P4 | T1 scalars | T2 dtw20 | T2 shape | T3 |
|---|---|---|---|---|---|---|---|---|
| charterhouse_loyd ~ charterhouse_moncrieff | 1/1 | 1/1 | 2/2 | 1/1 | 1/1 | 1/1 | 1/1 | 1/1 |
| dq_motteux ~ dq_ormsby | 2/1 | 2/1 | 2/3 | 1/1 | 1/2 | 15/6 | 3/2 | 2/3 |
| dq_motteux ~ dq_smollett | 1/1 | 1/1 | 11/2 | 2/1 | 7/2 | 18/11 | 2/2 | 7/5 |
| dq_ormsby ~ dq_smollett | 2/2 | 2/2 | 11/4 | 2/2 | 1/1 | 1/1 | 1/1 | 1/1 |
| fathers_garnett ~ fathers_hogarth | 6/1 | 7/1 | 2/1 | 5/1 | 1/1 | 1/1 | 1/1 | 1/1 |
| gentlefolk_garnett ~ gentlefolk_ralston | 1/1 | 1/1 | 1/2 | 1/1 | 2/2 | 1/1 | 1/1 | 1/1 |
| journey_1871 ~ journey_malleson | 1/1 | 1/1 | 1/1 | 1/1 | 1/1 | 1/1 | 1/1 | 1/1 |
| lesmis_hapgood ~ lesmis_wraxall | 1/1 | 1/1 | 1/1 | 1/1 | 1/1 | 1/1 | 1/1 | 1/1 |
| mystisland_kingston ~ mystisland_white | 1/1 | 1/1 | 1/1 | 1/1 | 1/1 | 1/1 | 1/1 | 1/1 |
| tolstoy_res_maude ~ tolstoy_res_smith | 1/1 | 1/1 | 1/1 | 1/1 | 1/1 | 1/2 | 1/1 | 1/1 |

## Prose and Telling side by side, all 87 books

AUC that a labelled pair is closer than a negative pair (3663 negatives; [95% bootstrap interval over the labelled pairs]). n = labelled pairs.

| block | translation_pair (n=10) | edition_pair (n=1) | same_author_unrelated (n=52) | same_author_orig_en (n=33) | same_author_same_translator (n=5) | same_author_diff_translator (n=14) | series (n=7) | retelling (n=8) | same_translator_diff_author (n=11) | same_genre (n=261) |
|---|---|---|---|---|---|---|---|---|---|---|
| P1_mfw100_all_noprop_nocull | 1.00 [1.00, 1.00] | 1.00 | 0.98 [0.97, 0.99] | 0.98 [0.96, 0.99] | 1.00 [1.00, 1.00] | 0.97 [0.95, 0.99] | 1.00 [0.99, 1.00] | 0.88 [0.78, 0.96] | 0.91 [0.81, 0.98] | 0.63 [0.59, 0.67] |
| P1_mfw500_all_noprop_nocull | 1.00 [1.00, 1.00] | 1.00 | 0.99 [0.98, 0.99] | 0.99 [0.99, 1.00] | 1.00 [1.00, 1.00] | 0.98 [0.96, 1.00] | 1.00 [1.00, 1.00] | 0.97 [0.94, 0.99] | 0.95 [0.90, 0.99] | 0.68 [0.65, 0.72] |
| P2_tag3_1000 | 1.00 [0.99, 1.00] | 1.00 | 0.97 [0.95, 0.99] | 0.98 [0.96, 0.99] | 1.00 [1.00, 1.00] | 0.95 [0.89, 0.99] | 1.00 [0.99, 1.00] | 0.77 [0.59, 0.92] | 0.88 [0.79, 0.95] | 0.65 [0.61, 0.68] |
| P3_rhythm | 0.87 [0.72, 0.98] | 1.00 | 0.90 [0.85, 0.93] | 0.87 [0.80, 0.93] | 0.98 [0.97, 0.99] | 0.93 [0.90, 0.96] | 0.85 [0.64, 0.99] | 0.50 [0.25, 0.77] | 0.85 [0.78, 0.90] | 0.51 [0.48, 0.55] |
| P4_mfw500_tag3_rhythm | 1.00 [1.00, 1.00] | 1.00 | 0.99 [0.98, 0.99] | 0.99 [0.98, 0.99] | 1.00 [1.00, 1.00] | 0.98 [0.96, 1.00] | 1.00 [0.99, 1.00] | 0.73 [0.44, 0.95] | 0.94 [0.89, 0.98] | 0.61 [0.57, 0.65] |
| T1_scalars | 0.98 [0.95, 1.00] | 1.00 | 0.76 [0.68, 0.83] | 0.78 [0.70, 0.86] | 0.64 [0.29, 0.96] | 0.75 [0.58, 0.89] | 0.86 [0.74, 0.97] | 0.41 [0.17, 0.67] | 0.61 [0.41, 0.80] | 0.56 [0.52, 0.59] |
| T1_bag | 1.00 [0.99, 1.00] | 1.00 | 0.79 [0.73, 0.85] | 0.82 [0.75, 0.88] | 0.80 [0.66, 0.93] | 0.73 [0.61, 0.85] | 0.87 [0.78, 0.97] | 0.38 [0.12, 0.67] | 0.63 [0.49, 0.77] | 0.55 [0.52, 0.59] |
| T2_curves20_dtw | 0.97 [0.94, 1.00] | 1.00 | 0.60 [0.52, 0.68] | 0.63 [0.51, 0.73] | 0.62 [0.34, 0.85] | 0.52 [0.38, 0.67] | 0.56 [0.33, 0.76] | 0.51 [0.33, 0.68] | 0.65 [0.49, 0.80] | 0.48 [0.45, 0.52] |
| T2_shape_nosd | 1.00 [0.99, 1.00] | 1.00 | 0.58 [0.51, 0.64] | 0.63 [0.55, 0.71] | 0.38 [0.18, 0.61] | 0.52 [0.41, 0.63] | 0.58 [0.31, 0.83] | 0.50 [0.31, 0.71] | 0.60 [0.41, 0.78] | 0.48 [0.45, 0.52] |
| T3_scalars_dtw20_sd | 0.99 [0.97, 1.00] | 1.00 | 0.72 [0.65, 0.79] | 0.73 [0.64, 0.82] | 0.62 [0.36, 0.88] | 0.72 [0.58, 0.84] | 0.78 [0.61, 0.92] | 0.45 [0.23, 0.69] | 0.64 [0.46, 0.81] | 0.52 [0.49, 0.56] |

Mean percentile rank of the partner (0 = nearest book) / recall@1 / recall@5.

| block | translation_pair (n=10) | edition_pair (n=1) | same_author_unrelated (n=52) | same_author_orig_en (n=33) | same_author_same_translator (n=5) | same_author_diff_translator (n=14) | series (n=7) | retelling (n=8) | same_translator_diff_author (n=11) | same_genre (n=261) |
|---|---|---|---|---|---|---|---|---|---|---|
| P1_mfw100_all_noprop_nocull | 0.00 / 0.88 / 1.00 | 0.00 / 1.00 / 1.00 | 0.03 / 0.65 / 0.98 | 0.02 / 0.72 / 0.97 | 0.01 / 0.86 / 1.00 | 0.04 / 0.12 / 0.94 | 0.00 / 1.00 / 1.00 | 0.13 / 0.30 / 0.80 | 0.11 / 0.00 / 0.83 | 0.38 / 0.13 / 0.75 |
| P1_mfw500_all_noprop_nocull | 0.00 / 0.94 / 0.94 | 0.00 / 1.00 / 1.00 | 0.02 / 0.69 / 1.00 | 0.01 / 0.81 / 1.00 | 0.01 / 0.71 / 1.00 | 0.03 / 0.12 / 0.94 | 0.00 / 1.00 / 1.00 | 0.04 / 0.50 / 0.80 | 0.07 / 0.00 / 1.00 | 0.33 / 0.19 / 0.79 |
| P2_tag3_1000 | 0.01 / 0.94 / 0.94 | 0.00 / 1.00 / 1.00 | 0.03 / 0.62 / 0.96 | 0.02 / 0.72 / 0.97 | 0.01 / 0.71 / 1.00 | 0.05 / 0.12 / 0.88 | 0.00 / 0.93 / 1.00 | 0.24 / 0.30 / 0.60 | 0.14 / 0.00 / 0.83 | 0.37 / 0.11 / 0.75 |
| P3_rhythm | 0.02 / 0.59 / 1.00 | 0.00 / 1.00 / 1.00 | 0.12 / 0.48 / 0.73 | 0.14 / 0.56 / 0.75 | 0.03 / 0.57 / 0.57 | 0.10 / 0.06 / 0.62 | 0.10 / 0.50 / 0.71 | 0.43 / 0.20 / 0.60 | 0.20 / 0.17 / 0.67 | 0.49 / 0.09 / 0.43 |
| P4_mfw500_tag3_rhythm | 0.00 / 0.94 / 1.00 | 0.00 / 1.00 / 1.00 | 0.02 / 0.69 / 0.98 | 0.02 / 0.81 / 0.97 | 0.01 / 0.71 / 1.00 | 0.03 / 0.12 / 0.94 | 0.00 / 0.86 / 1.00 | 0.24 / 0.30 / 0.50 | 0.09 / 0.00 / 0.83 | 0.38 / 0.09 / 0.72 |
| T1_scalars | 0.01 / 0.88 / 1.00 | 0.00 / 1.00 / 1.00 | 0.24 / 0.25 / 0.48 | 0.23 / 0.22 / 0.50 | 0.31 / 0.00 / 0.43 | 0.23 / 0.31 / 0.44 | 0.10 / 0.43 / 0.71 | 0.48 / 0.20 / 0.20 | 0.37 / 0.00 / 0.50 | 0.42 / 0.26 / 0.57 |
| T1_bag | 0.00 / 0.94 / 1.00 | 0.00 / 1.00 / 1.00 | 0.19 / 0.17 / 0.52 | 0.19 / 0.16 / 0.53 | 0.16 / 0.00 / 0.43 | 0.20 / 0.19 / 0.44 | 0.10 / 0.43 / 0.64 | 0.45 / 0.20 / 0.30 | 0.37 / 0.00 / 0.50 | 0.44 / 0.11 / 0.43 |
| T2_curves20_dtw | 0.03 / 0.88 / 0.94 | 0.00 / 1.00 / 1.00 | 0.40 / 0.04 / 0.33 | 0.36 / 0.06 / 0.41 | 0.39 / 0.00 / 0.00 | 0.50 / 0.00 / 0.19 | 0.42 / 0.00 / 0.00 | 0.40 / 0.00 / 0.10 | 0.41 / 0.17 / 0.17 | 0.50 / 0.08 / 0.57 |
| T2_shape_nosd | 0.00 / 0.94 / 1.00 | 0.00 / 1.00 / 1.00 | 0.45 / 0.02 / 0.17 | 0.38 / 0.03 / 0.25 | 0.61 / 0.00 / 0.00 | 0.55 / 0.00 / 0.00 | 0.42 / 0.00 / 0.07 | 0.45 / 0.00 / 0.00 | 0.44 / 0.33 / 0.33 | 0.50 / 0.19 / 0.49 |
| T3_scalars_dtw20_sd | 0.01 / 0.94 / 1.00 | 0.00 / 1.00 / 1.00 | 0.29 / 0.15 / 0.52 | 0.27 / 0.22 / 0.62 | 0.37 / 0.00 / 0.29 | 0.31 / 0.00 / 0.25 | 0.18 / 0.14 / 0.29 | 0.42 / 0.00 / 0.30 | 0.38 / 0.17 / 0.67 | 0.45 / 0.17 / 0.55 |

Split-half self-retrieval (accuracy; chance is 1/n), and Spearman of distance with |year difference| and |log word-count difference| (Mantel p in brackets; en = both books written in English; diff = different authors only).

| block | n | input | split a/b | split h1/h2 | rho year | rho year en | rho year en diff | rho logwords | rho logwords diff |
|---|---|---|---|---|---|---|---|---|---|
| P1_mfw100_all_noprop_nocull | 87 | ordered text | 0.97 | 0.89 | 0.15 (0.005) | 0.19 (0.005) | 0.15 | 0.04 (0.020) | 0.02 |
| P1_mfw500_all_noprop_nocull | 87 | ordered text | 0.97 | 0.92 | 0.18 (0.005) | 0.24 (0.005) | 0.21 | 0.06 (0.005) | 0.04 |
| P2_tag3_1000 | 87 | ordered text | 0.97 | 0.90 | 0.21 (0.005) | 0.28 (0.005) | 0.25 | 0.06 (0.005) | 0.05 |
| P3_rhythm | 87 | ordered text | 0.97 | 0.85 | 0.39 (0.005) | 0.27 (0.010) | 0.24 | 0.01 (0.815) | 0.00 |
| P4_mfw500_tag3_rhythm | 87 | ordered text | 0.97 | 0.91 | 0.36 (0.005) | 0.34 (0.005) | 0.31 | 0.05 (0.130) | 0.03 |
| T1_scalars | 87 | ordered text | 0.90 | 0.71 | 0.17 (0.015) | 0.11 (0.140) | 0.08 | 0.02 (0.585) | 0.01 |
| T1_bag | 87 | book bag | 0.90 | 0.49 | 0.19 (0.005) | 0.12 (0.055) | 0.09 | 0.05 (0.340) | 0.04 |
| T2_curves20_dtw | 87 | ordered text | 0.55 |  | 0.05 (0.190) | 0.02 (0.760) | 0.01 | 0.06 (0.140) | 0.05 |
| T2_shape_nosd | 87 | ordered text | 0.57 |  | 0.08 (0.155) | 0.06 (0.390) | 0.05 | 0.12 (0.035) | 0.11 |
| T3_scalars_dtw20_sd | 87 | ordered text | 0.74 |  | 0.14 (0.020) | 0.07 (0.220) | 0.05 | 0.05 (0.240) | 0.04 |

Top-5 neighbour make-up (observed / chance) and hubness (skew of the 5-nearest in-degree; share of books in nobody's top 5; largest in-degree and the book).

| block | same author | same genre | mean abs year diff | mean abs log-words diff | hub skew | in no top 5 | max in-degree |
|---|---|---|---|---|---|---|---|
| P1_mfw100_all_noprop_nocull | 0.39 / 0.02 | 0.42 / 0.12 | 34 / 56 | 0.66 / 0.78 | 0.25 | 0.02 | 11 (barsoom_gods) |
| P1_mfw500_all_noprop_nocull | 0.41 / 0.02 | 0.47 / 0.12 | 32 / 56 | 0.63 / 0.78 | 0.33 | 0.02 | 11 (austen_emma) |
| P2_tag3_1000 | 0.38 / 0.02 | 0.37 / 0.12 | 34 / 56 | 0.62 / 0.78 | 0.84 | 0.02 | 15 (wells_worlds) |
| P3_rhythm | 0.27 / 0.02 | 0.20 / 0.12 | 29 / 56 | 0.67 / 0.78 | 1.23 | 0.09 | 21 (woolf_voyage) |
| P4_mfw500_tag3_rhythm | 0.40 / 0.02 | 0.38 / 0.12 | 27 / 56 | 0.64 / 0.78 | 1.00 | 0.02 | 17 (wells_worlds) |
| T1_scalars | 0.20 / 0.02 | 0.25 / 0.12 | 39 / 56 | 0.67 / 0.78 | 0.63 | 0.09 | 15 (hardy_mayor) |
| T1_bag | 0.21 / 0.02 | 0.23 / 0.12 | 38 / 56 | 0.64 / 0.78 | 0.69 | 0.06 | 13 (twain_yankee) |
| T2_curves20_dtw | 0.11 / 0.02 | 0.14 / 0.12 | 46 / 56 | 0.75 / 0.78 | 0.45 | 0.05 | 13 (fathers_garnett) |
| T2_shape_nosd | 0.09 / 0.02 | 0.14 / 0.12 | 43 / 56 | 0.68 / 0.78 | 2.57 | 0.15 | 35 (fathers_garnett) |
| T3_scalars_dtw20_sd | 0.18 / 0.02 | 0.21 / 0.12 | 38 / 56 | 0.69 / 0.78 | 0.82 | 0.08 | 16 (twain_yankee) |

Spearman between the pair distances of two blocks, all pairs.

| block | P1_mfw100_all_noprop_nocull | P1_mfw500_all_noprop_nocull | P2_tag3_1000 | P3_rhythm | P4_mfw500_tag3_rhythm | T1_scalars | T1_bag | T2_curves20_dtw | T2_shape_nosd | T3_scalars_dtw20_sd |
|---|---|---|---|---|---|---|---|---|---|---|
| P1_mfw100_all_noprop_nocull | 1.00 | 0.87 | 0.79 | 0.28 | 0.71 | 0.21 | 0.31 | 0.03 | 0.03 | 0.15 |
| P1_mfw500_all_noprop_nocull | 0.87 | 1.00 | 0.79 | 0.27 | 0.74 | 0.19 | 0.26 | 0.03 | 0.04 | 0.13 |
| P2_tag3_1000 | 0.79 | 0.79 | 1.00 | 0.33 | 0.79 | 0.21 | 0.29 | 0.03 | 0.04 | 0.15 |
| P3_rhythm | 0.28 | 0.27 | 0.33 | 1.00 | 0.79 | 0.47 | 0.44 | 0.13 | 0.17 | 0.38 |
| P4_mfw500_tag3_rhythm | 0.71 | 0.74 | 0.79 | 0.79 | 1.00 | 0.41 | 0.45 | 0.11 | 0.14 | 0.32 |
| T1_scalars | 0.21 | 0.19 | 0.21 | 0.47 | 0.41 | 1.00 | 0.78 | 0.18 | 0.27 | 0.74 |
| T1_bag | 0.31 | 0.26 | 0.29 | 0.44 | 0.45 | 0.78 | 1.00 | 0.10 | 0.15 | 0.55 |
| T2_curves20_dtw | 0.03 | 0.03 | 0.03 | 0.13 | 0.11 | 0.18 | 0.10 | 1.00 | 0.64 | 0.77 |
| T2_shape_nosd | 0.03 | 0.04 | 0.04 | 0.17 | 0.14 | 0.27 | 0.15 | 0.64 | 1.00 | 0.59 |
| T3_scalars_dtw20_sd | 0.15 | 0.13 | 0.15 | 0.38 | 0.32 | 0.74 | 0.55 | 0.77 | 0.59 | 1.00 |

Spearman between the pair distances of two blocks, different-author pairs only.

| block | P1_mfw100_all_noprop_nocull | P1_mfw500_all_noprop_nocull | P2_tag3_1000 | P3_rhythm | P4_mfw500_tag3_rhythm | T1_scalars | T1_bag | T2_curves20_dtw | T2_shape_nosd | T3_scalars_dtw20_sd |
|---|---|---|---|---|---|---|---|---|---|---|
| P1_mfw100_all_noprop_nocull | 1.00 | 0.86 | 0.78 | 0.25 | 0.69 | 0.18 | 0.28 | 0.01 | 0.01 | 0.12 |
| P1_mfw500_all_noprop_nocull | 0.86 | 1.00 | 0.78 | 0.24 | 0.72 | 0.16 | 0.24 | 0.02 | 0.02 | 0.11 |
| P2_tag3_1000 | 0.78 | 0.78 | 1.00 | 0.31 | 0.78 | 0.18 | 0.27 | 0.01 | 0.02 | 0.12 |
| P3_rhythm | 0.25 | 0.24 | 0.31 | 1.00 | 0.78 | 0.46 | 0.43 | 0.12 | 0.17 | 0.37 |
| P4_mfw500_tag3_rhythm | 0.69 | 0.72 | 0.78 | 0.78 | 1.00 | 0.39 | 0.43 | 0.09 | 0.13 | 0.31 |
| T1_scalars | 0.18 | 0.16 | 0.18 | 0.46 | 0.39 | 1.00 | 0.77 | 0.17 | 0.26 | 0.73 |
| T1_bag | 0.28 | 0.24 | 0.27 | 0.43 | 0.43 | 0.77 | 1.00 | 0.09 | 0.14 | 0.54 |
| T2_curves20_dtw | 0.01 | 0.02 | 0.01 | 0.12 | 0.09 | 0.17 | 0.09 | 1.00 | 0.64 | 0.77 |
| T2_shape_nosd | 0.01 | 0.02 | 0.02 | 0.17 | 0.13 | 0.26 | 0.14 | 0.64 | 1.00 | 0.59 |
| T3_scalars_dtw20_sd | 0.12 | 0.11 | 0.12 | 0.37 | 0.31 | 0.73 | 0.54 | 0.77 | 0.59 | 1.00 |


## Prose and Telling side by side, flagged books left out (without joyce_ulysses, wells_time, wyss_swiss)

AUC that a labelled pair is closer than a negative pair (3413 negatives; [95% bootstrap interval over the labelled pairs]). n = labelled pairs.

| block | translation_pair (n=10) | edition_pair (n=1) | same_author_unrelated (n=50) | same_author_orig_en (n=31) | same_author_same_translator (n=5) | same_author_diff_translator (n=14) | series (n=7) | retelling (n=5) | same_translator_diff_author (n=11) | same_genre (n=231) |
|---|---|---|---|---|---|---|---|---|---|---|
| P1_mfw100_all_noprop_nocull | 1.00 [1.00, 1.00] | 1.00 | 0.98 [0.96, 0.99] | 0.98 [0.96, 0.99] | 1.00 [1.00, 1.00] | 0.97 [0.95, 0.99] | 1.00 [0.99, 1.00] | 0.83 [0.70, 0.95] | 0.91 [0.82, 0.98] | 0.63 [0.59, 0.67] |
| P1_mfw500_all_noprop_nocull | 1.00 [1.00, 1.00] | 1.00 | 0.99 [0.98, 0.99] | 0.99 [0.99, 1.00] | 1.00 [1.00, 1.00] | 0.98 [0.96, 1.00] | 1.00 [1.00, 1.00] | 0.96 [0.91, 1.00] | 0.95 [0.90, 0.99] | 0.68 [0.65, 0.72] |
| P2_tag3_1000 | 1.00 [0.99, 1.00] | 1.00 | 0.97 [0.95, 0.99] | 0.98 [0.96, 0.99] | 1.00 [1.00, 1.00] | 0.95 [0.89, 0.99] | 1.00 [0.99, 1.00] | 0.73 [0.49, 0.98] | 0.88 [0.79, 0.95] | 0.65 [0.62, 0.69] |
| P3_rhythm | 0.86 [0.71, 0.98] | 1.00 | 0.90 [0.85, 0.94] | 0.87 [0.80, 0.93] | 0.98 [0.97, 0.99] | 0.93 [0.90, 0.95] | 0.84 [0.69, 0.99] | 0.57 [0.18, 0.96] | 0.84 [0.78, 0.90] | 0.52 [0.49, 0.56] |
| P4_mfw500_tag3_rhythm | 1.00 [1.00, 1.00] | 1.00 | 0.99 [0.98, 0.99] | 0.99 [0.98, 0.99] | 1.00 [1.00, 1.00] | 0.98 [0.96, 1.00] | 1.00 [0.99, 1.00] | 0.63 [0.28, 0.98] | 0.94 [0.89, 0.98] | 0.62 [0.58, 0.66] |
| T1_scalars | 0.98 [0.95, 1.00] | 1.00 | 0.77 [0.69, 0.84] | 0.81 [0.73, 0.88] | 0.63 [0.26, 0.96] | 0.73 [0.58, 0.87] | 0.85 [0.70, 0.97] | 0.60 [0.31, 0.88] | 0.59 [0.39, 0.78] | 0.59 [0.55, 0.62] |
| T1_bag | 0.99 [0.99, 1.00] | 1.00 | 0.78 [0.72, 0.84] | 0.81 [0.73, 0.88] | 0.79 [0.63, 0.92] | 0.72 [0.59, 0.85] | 0.87 [0.76, 0.96] | 0.58 [0.25, 0.92] | 0.62 [0.46, 0.77] | 0.57 [0.54, 0.61] |
| T2_curves20_dtw | 0.97 [0.92, 1.00] | 1.00 | 0.58 [0.50, 0.67] | 0.62 [0.50, 0.73] | 0.61 [0.33, 0.84] | 0.50 [0.37, 0.65] | 0.55 [0.33, 0.75] | 0.64 [0.43, 0.77] | 0.63 [0.47, 0.78] | 0.49 [0.45, 0.53] |
| T2_shape_nosd | 1.00 [0.99, 1.00] | 1.00 | 0.56 [0.49, 0.64] | 0.63 [0.53, 0.71] | 0.36 [0.16, 0.59] | 0.50 [0.38, 0.60] | 0.57 [0.29, 0.82] | 0.64 [0.42, 0.79] | 0.58 [0.39, 0.75] | 0.50 [0.46, 0.53] |
| T3_scalars_dtw20_sd | 0.99 [0.97, 1.00] | 1.00 | 0.72 [0.64, 0.79] | 0.74 [0.65, 0.84] | 0.59 [0.32, 0.87] | 0.70 [0.55, 0.83] | 0.76 [0.59, 0.91] | 0.66 [0.48, 0.87] | 0.61 [0.43, 0.80] | 0.55 [0.51, 0.58] |

Mean percentile rank of the partner (0 = nearest book) / recall@1 / recall@5.

| block | translation_pair (n=10) | edition_pair (n=1) | same_author_unrelated (n=50) | same_author_orig_en (n=31) | same_author_same_translator (n=5) | same_author_diff_translator (n=14) | series (n=7) | retelling (n=5) | same_translator_diff_author (n=11) | same_genre (n=231) |
|---|---|---|---|---|---|---|---|---|---|---|
| P1_mfw100_all_noprop_nocull | 0.00 / 0.88 / 1.00 | 0.00 / 1.00 / 1.00 | 0.03 / 0.64 / 0.98 | 0.03 / 0.71 / 0.97 | 0.01 / 0.86 / 1.00 | 0.04 / 0.12 / 0.94 | 0.00 / 1.00 / 1.00 | 0.17 / 0.33 / 0.44 | 0.12 / 0.00 / 0.83 | 0.39 / 0.16 / 0.70 |
| P1_mfw500_all_noprop_nocull | 0.00 / 0.94 / 0.94 | 0.00 / 1.00 / 1.00 | 0.02 / 0.66 / 0.98 | 0.01 / 0.77 / 0.97 | 0.01 / 0.71 / 1.00 | 0.03 / 0.12 / 0.94 | 0.00 / 1.00 / 1.00 | 0.05 / 0.44 / 0.67 | 0.07 / 0.00 / 1.00 | 0.33 / 0.20 / 0.76 |
| P2_tag3_1000 | 0.01 / 0.94 / 0.94 | 0.00 / 1.00 / 1.00 | 0.03 / 0.60 / 0.94 | 0.02 / 0.68 / 0.94 | 0.01 / 0.71 / 1.00 | 0.05 / 0.12 / 0.88 | 0.00 / 0.93 / 1.00 | 0.27 / 0.22 / 0.44 | 0.14 / 0.00 / 0.83 | 0.36 / 0.08 / 0.74 |
| P3_rhythm | 0.02 / 0.76 / 1.00 | 0.00 / 1.00 / 1.00 | 0.11 / 0.47 / 0.72 | 0.13 / 0.55 / 0.74 | 0.03 / 0.57 / 0.57 | 0.10 / 0.06 / 0.62 | 0.10 / 0.50 / 0.71 | 0.40 / 0.22 / 0.56 | 0.21 / 0.17 / 0.67 | 0.48 / 0.10 / 0.46 |
| P4_mfw500_tag3_rhythm | 0.00 / 0.94 / 1.00 | 0.00 / 1.00 / 1.00 | 0.02 / 0.66 / 0.96 | 0.02 / 0.77 / 0.94 | 0.01 / 0.71 / 1.00 | 0.03 / 0.12 / 0.94 | 0.00 / 0.86 / 1.00 | 0.29 / 0.33 / 0.44 | 0.09 / 0.00 / 0.83 | 0.38 / 0.12 / 0.72 |
| T1_scalars | 0.01 / 0.88 / 1.00 | 0.00 / 1.00 / 1.00 | 0.23 / 0.26 / 0.49 | 0.21 / 0.23 / 0.52 | 0.31 / 0.00 / 0.43 | 0.24 / 0.31 / 0.44 | 0.10 / 0.43 / 0.71 | 0.35 / 0.22 / 0.22 | 0.38 / 0.00 / 0.50 | 0.41 / 0.26 / 0.56 |
| T1_bag | 0.00 / 0.94 / 1.00 | 0.00 / 1.00 / 1.00 | 0.20 / 0.17 / 0.49 | 0.20 / 0.16 / 0.48 | 0.17 / 0.00 / 0.43 | 0.21 / 0.19 / 0.44 | 0.10 / 0.43 / 0.64 | 0.32 / 0.22 / 0.33 | 0.38 / 0.00 / 0.50 | 0.43 / 0.12 / 0.42 |
| T2_curves20_dtw | 0.03 / 0.88 / 0.94 | 0.00 / 1.00 / 1.00 | 0.41 / 0.04 / 0.32 | 0.36 / 0.06 / 0.39 | 0.40 / 0.00 / 0.00 | 0.51 / 0.00 / 0.19 | 0.43 / 0.00 / 0.00 | 0.29 / 0.00 / 0.11 | 0.42 / 0.17 / 0.17 | 0.49 / 0.06 / 0.54 |
| T2_shape_nosd | 0.00 / 0.94 / 1.00 | 0.00 / 1.00 / 1.00 | 0.46 / 0.02 / 0.17 | 0.39 / 0.03 / 0.26 | 0.63 / 0.00 / 0.00 | 0.56 / 0.00 / 0.00 | 0.43 / 0.00 / 0.07 | 0.35 / 0.00 / 0.00 | 0.46 / 0.33 / 0.33 | 0.50 / 0.18 / 0.50 |
| T3_scalars_dtw20_sd | 0.01 / 0.94 / 1.00 | 0.00 / 1.00 / 1.00 | 0.29 / 0.15 / 0.53 | 0.27 / 0.23 / 0.65 | 0.38 / 0.00 / 0.29 | 0.32 / 0.00 / 0.25 | 0.18 / 0.14 / 0.29 | 0.28 / 0.00 / 0.33 | 0.40 / 0.17 / 0.67 | 0.44 / 0.16 / 0.54 |

Split-half self-retrieval (accuracy; chance is 1/n), and Spearman of distance with |year difference| and |log word-count difference| (Mantel p in brackets; en = both books written in English; diff = different authors only).

| block | n | input | split a/b | split h1/h2 | rho year | rho year en | rho year en diff | rho logwords | rho logwords diff |
|---|---|---|---|---|---|---|---|---|---|
| P1_mfw100_all_noprop_nocull | 84 | ordered text | 0.96 | 0.88 | 0.14 (0.005) | 0.18 (0.005) | 0.15 | 0.04 (0.030) | 0.02 |
| P1_mfw500_all_noprop_nocull | 84 | ordered text | 0.96 | 0.92 | 0.17 (0.005) | 0.24 (0.005) | 0.20 | 0.06 (0.005) | 0.04 |
| P2_tag3_1000 | 84 | ordered text | 0.96 | 0.89 | 0.20 (0.005) | 0.27 (0.005) | 0.24 | 0.06 (0.005) | 0.04 |
| P3_rhythm | 84 | ordered text | 0.97 | 0.86 | 0.40 (0.005) | 0.29 (0.005) | 0.26 | 0.01 (0.910) | -0.01 |
| P4_mfw500_tag3_rhythm | 84 | ordered text | 0.96 | 0.91 | 0.36 (0.005) | 0.34 (0.005) | 0.32 | 0.04 (0.240) | 0.03 |
| T1_scalars | 84 | ordered text | 0.90 | 0.70 | 0.17 (0.005) | 0.13 (0.050) | 0.11 | 0.00 (0.980) | -0.01 |
| T1_bag | 84 | book bag | 0.90 | 0.49 | 0.18 (0.010) | 0.14 (0.050) | 0.12 | 0.03 (0.465) | 0.02 |
| T2_curves20_dtw | 84 | ordered text | 0.54 |  | 0.05 (0.255) | 0.03 (0.530) | 0.02 | 0.04 (0.355) | 0.03 |
| T2_shape_nosd | 84 | ordered text | 0.57 |  | 0.08 (0.190) | 0.08 (0.260) | 0.07 | 0.09 (0.080) | 0.09 |
| T3_scalars_dtw20_sd | 84 | ordered text | 0.74 |  | 0.14 (0.015) | 0.10 (0.080) | 0.08 | 0.03 (0.550) | 0.01 |

Top-5 neighbour make-up (observed / chance) and hubness (skew of the 5-nearest in-degree; share of books in nobody's top 5; largest in-degree and the book).

| block | same author | same genre | mean abs year diff | mean abs log-words diff | hub skew | in no top 5 | max in-degree |
|---|---|---|---|---|---|---|---|
| P1_mfw100_all_noprop_nocull | 0.39 / 0.03 | 0.40 / 0.11 | 34 / 56 | 0.65 / 0.76 | 0.19 | 0.02 | 10 (bovary_marx_aveling) |
| P1_mfw500_all_noprop_nocull | 0.40 / 0.03 | 0.45 / 0.11 | 31 / 56 | 0.63 / 0.76 | 0.35 | 0.02 | 11 (austen_emma) |
| P2_tag3_1000 | 0.37 / 0.03 | 0.37 / 0.11 | 34 / 56 | 0.60 / 0.76 | 0.80 | 0.01 | 14 (wells_worlds) |
| P3_rhythm | 0.28 / 0.03 | 0.20 / 0.11 | 29 / 56 | 0.66 / 0.76 | 1.27 | 0.08 | 21 (woolf_voyage) |
| P4_mfw500_tag3_rhythm | 0.40 / 0.03 | 0.39 / 0.11 | 27 / 56 | 0.63 / 0.76 | 0.89 | 0.01 | 16 (wells_worlds) |
| T1_scalars | 0.21 / 0.03 | 0.25 / 0.11 | 37 / 56 | 0.65 / 0.76 | 0.64 | 0.07 | 15 (hardy_mayor) |
| T1_bag | 0.20 / 0.03 | 0.22 / 0.11 | 37 / 56 | 0.64 / 0.76 | 0.74 | 0.05 | 15 (twain_yankee) |
| T2_curves20_dtw | 0.11 / 0.03 | 0.12 / 0.11 | 46 / 56 | 0.75 / 0.76 | 0.45 | 0.04 | 13 (fathers_garnett) |
| T2_shape_nosd | 0.09 / 0.03 | 0.14 / 0.11 | 43 / 56 | 0.67 / 0.76 | 2.56 | 0.13 | 34 (fathers_garnett) |
| T3_scalars_dtw20_sd | 0.18 / 0.03 | 0.20 / 0.11 | 38 / 56 | 0.69 / 0.76 | 0.82 | 0.06 | 15 (hardy_madding) |

Spearman between the pair distances of two blocks, all pairs.

| block | P1_mfw100_all_noprop_nocull | P1_mfw500_all_noprop_nocull | P2_tag3_1000 | P3_rhythm | P4_mfw500_tag3_rhythm | T1_scalars | T1_bag | T2_curves20_dtw | T2_shape_nosd | T3_scalars_dtw20_sd |
|---|---|---|---|---|---|---|---|---|---|---|
| P1_mfw100_all_noprop_nocull | 1.00 | 0.87 | 0.79 | 0.29 | 0.71 | 0.23 | 0.32 | 0.03 | 0.03 | 0.16 |
| P1_mfw500_all_noprop_nocull | 0.87 | 1.00 | 0.79 | 0.28 | 0.74 | 0.21 | 0.27 | 0.03 | 0.03 | 0.15 |
| P2_tag3_1000 | 0.79 | 0.79 | 1.00 | 0.34 | 0.79 | 0.23 | 0.30 | 0.03 | 0.04 | 0.16 |
| P3_rhythm | 0.29 | 0.28 | 0.34 | 1.00 | 0.79 | 0.46 | 0.46 | 0.10 | 0.14 | 0.36 |
| P4_mfw500_tag3_rhythm | 0.71 | 0.74 | 0.79 | 0.79 | 1.00 | 0.42 | 0.46 | 0.09 | 0.11 | 0.32 |
| T1_scalars | 0.23 | 0.21 | 0.23 | 0.46 | 0.42 | 1.00 | 0.80 | 0.10 | 0.18 | 0.69 |
| T1_bag | 0.32 | 0.27 | 0.30 | 0.46 | 0.46 | 0.80 | 1.00 | 0.05 | 0.10 | 0.53 |
| T2_curves20_dtw | 0.03 | 0.03 | 0.03 | 0.10 | 0.09 | 0.10 | 0.05 | 1.00 | 0.61 | 0.76 |
| T2_shape_nosd | 0.03 | 0.03 | 0.04 | 0.14 | 0.11 | 0.18 | 0.10 | 0.61 | 1.00 | 0.55 |
| T3_scalars_dtw20_sd | 0.16 | 0.15 | 0.16 | 0.36 | 0.32 | 0.69 | 0.53 | 0.76 | 0.55 | 1.00 |

Spearman between the pair distances of two blocks, different-author pairs only.

| block | P1_mfw100_all_noprop_nocull | P1_mfw500_all_noprop_nocull | P2_tag3_1000 | P3_rhythm | P4_mfw500_tag3_rhythm | T1_scalars | T1_bag | T2_curves20_dtw | T2_shape_nosd | T3_scalars_dtw20_sd |
|---|---|---|---|---|---|---|---|---|---|---|
| P1_mfw100_all_noprop_nocull | 1.00 | 0.86 | 0.78 | 0.26 | 0.70 | 0.21 | 0.29 | 0.02 | 0.01 | 0.14 |
| P1_mfw500_all_noprop_nocull | 0.86 | 1.00 | 0.78 | 0.25 | 0.73 | 0.19 | 0.24 | 0.02 | 0.02 | 0.13 |
| P2_tag3_1000 | 0.78 | 0.78 | 1.00 | 0.31 | 0.78 | 0.20 | 0.28 | 0.01 | 0.02 | 0.14 |
| P3_rhythm | 0.26 | 0.25 | 0.31 | 1.00 | 0.78 | 0.45 | 0.45 | 0.09 | 0.13 | 0.35 |
| P4_mfw500_tag3_rhythm | 0.70 | 0.73 | 0.78 | 0.78 | 1.00 | 0.40 | 0.45 | 0.08 | 0.10 | 0.30 |
| T1_scalars | 0.21 | 0.19 | 0.20 | 0.45 | 0.40 | 1.00 | 0.79 | 0.09 | 0.17 | 0.69 |
| T1_bag | 0.29 | 0.24 | 0.28 | 0.45 | 0.45 | 0.79 | 1.00 | 0.04 | 0.09 | 0.52 |
| T2_curves20_dtw | 0.02 | 0.02 | 0.01 | 0.09 | 0.08 | 0.09 | 0.04 | 1.00 | 0.61 | 0.75 |
| T2_shape_nosd | 0.01 | 0.02 | 0.02 | 0.13 | 0.10 | 0.17 | 0.09 | 0.61 | 1.00 | 0.54 |
| T3_scalars_dtw20_sd | 0.14 | 0.13 | 0.14 | 0.35 | 0.30 | 0.69 | 0.52 | 0.75 | 0.54 | 1.00 |


## Author or translator (6 Garnett books)

| block | nearest: author+translator | author only | translator only | neither | AUC author beats translator (14 vs 11) | AUC translation pair closer than same-author pair (10 vs 52) | ... than orig-English same-author pair (10 vs 33) | median d translation pair / median d same-author |
|---|---|---|---|---|---|---|---|---|
| P1_mfw100_all_noprop_nocull | 5 | 1 | 0 | 0 | 0.60 | 0.82 | 0.79 | 0.47 |
| P1_mfw500_all_noprop_nocull | 5 | 1 | 0 | 0 | 0.75 | 0.85 | 0.83 | 0.48 |
| P1_mfw500_narr_noprop_nocull | 5 | 1 | 0 | 0 | 0.66 | 0.83 | 0.78 | 0.53 |
| P2_tag3_1000 | 5 | 1 | 0 | 0 | 0.75 | 0.80 | 0.77 | 0.66 |
| P2_tag3_1000_words | 5 | 1 | 0 | 0 | 0.70 | 0.84 | 0.84 | 0.55 |
| P3_rhythm | 4 | 0 | 1 | 1 | 0.75 | 0.58 | 0.55 | 0.80 |
| P4_mfw500_tag3 | 5 | 1 | 0 | 0 | 0.74 | 0.83 | 0.80 | 0.62 |
| P4_mfw500_tag3_rhythm | 5 | 1 | 0 | 0 | 0.75 | 0.76 | 0.72 | 0.70 |
| T1_scalars | 0 | 3 | 0 | 3 | 0.64 | 0.86 | 0.87 | 0.48 |
| T1_bag | 0 | 2 | 1 | 3 | 0.66 | 0.94 | 0.95 | 0.35 |
| T2_curves20_dtw | 0 | 0 | 1 | 5 | 0.38 | 0.94 | 0.92 | 0.61 |
| T2_shape_nosd | 0 | 0 | 2 | 4 | 0.43 | 0.99 | 0.99 | 0.53 |
| T3_scalars_dtw20_sd | 0 | 0 | 2 | 4 | 0.55 | 0.94 | 0.92 | 0.60 |

Nearest book that is not the same work, per Garnett book (ranks count from 1).

| block | anchor | nearest_not_same_work | shares | rank_nearest_same_author_other_translator | rank_nearest_garnett_other_author |
|---|---|---|---|---|---|
| P1_mfw100_all_noprop_nocull | dost_cp_garnett | dost_bk_garnett | author+translator | 2 | 3 |
| P1_mfw100_all_noprop_nocull | dost_bk_garnett | dost_cp_garnett | author+translator | 2 | 3 |
| P1_mfw100_all_noprop_nocull | dost_notes_garnett | dost_bk_garnett | author+translator | 3 | 17 |
| P1_mfw100_all_noprop_nocull | tolstoy_ak_garnett | tolstoy_wp_maude | author only | 1 | 2 |
| P1_mfw100_all_noprop_nocull | fathers_garnett | gentlefolk_garnett | author+translator | 2 | 3 |
| P1_mfw100_all_noprop_nocull | gentlefolk_garnett | fathers_garnett | author+translator | 10 | 2 |
| P1_mfw500_all_noprop_nocull | dost_cp_garnett | dost_bk_garnett | author+translator | 2 | 3 |
| P1_mfw500_all_noprop_nocull | dost_bk_garnett | dost_cp_garnett | author+translator | 2 | 4 |
| P1_mfw500_all_noprop_nocull | dost_notes_garnett | dost_bk_garnett | author+translator | 3 | 4 |
| P1_mfw500_all_noprop_nocull | tolstoy_ak_garnett | tolstoy_wp_maude | author only | 1 | 2 |
| P1_mfw500_all_noprop_nocull | fathers_garnett | gentlefolk_garnett | author+translator | 4 | 2 |
| P1_mfw500_all_noprop_nocull | gentlefolk_garnett | fathers_garnett | author+translator | 11 | 2 |
| P1_mfw500_narr_noprop_nocull | dost_cp_garnett | dost_bk_garnett | author+translator | 5 | 2 |
| P1_mfw500_narr_noprop_nocull | dost_bk_garnett | dost_cp_garnett | author+translator | 2 | 3 |
| P1_mfw500_narr_noprop_nocull | dost_notes_garnett | dost_bk_garnett | author+translator | 20 | 35 |
| P1_mfw500_narr_noprop_nocull | tolstoy_ak_garnett | tolstoy_wp_maude | author only | 1 | 3 |
| P1_mfw500_narr_noprop_nocull | fathers_garnett | gentlefolk_garnett | author+translator | 2 | 3 |
| P1_mfw500_narr_noprop_nocull | gentlefolk_garnett | fathers_garnett | author+translator | 6 | 2 |
| P2_tag3_1000 | dost_cp_garnett | dost_bk_garnett | author+translator | 2 | 4 |
| P2_tag3_1000 | dost_bk_garnett | dost_cp_garnett | author+translator | 2 | 4 |
| P2_tag3_1000 | dost_notes_garnett | dost_bk_garnett | author+translator | 3 | 10 |
| P2_tag3_1000 | tolstoy_ak_garnett | tolstoy_res_maude | author only | 1 | 4 |
| P2_tag3_1000 | fathers_garnett | gentlefolk_garnett | author+translator | 4 | 2 |
| P2_tag3_1000 | gentlefolk_garnett | fathers_garnett | author+translator | 29 | 2 |
| P2_tag3_1000_words | dost_cp_garnett | dost_bk_garnett | author+translator | 2 | 4 |
| P2_tag3_1000_words | dost_bk_garnett | dost_cp_garnett | author+translator | 2 | 4 |
| P2_tag3_1000_words | dost_notes_garnett | dost_bk_garnett | author+translator | 3 | 13 |
| P2_tag3_1000_words | tolstoy_ak_garnett | tolstoy_wp_maude | author only | 1 | 3 |
| P2_tag3_1000_words | fathers_garnett | gentlefolk_garnett | author+translator | 4 | 2 |
| P2_tag3_1000_words | gentlefolk_garnett | fathers_garnett | author+translator | 23 | 3 |
| P3_rhythm | dost_cp_garnett | dost_bk_garnett | author+translator | 2 | 4 |
| P3_rhythm | dost_bk_garnett | dost_cp_garnett | author+translator | 2 | 4 |
| P3_rhythm | dost_notes_garnett | dost_bk_garnett | author+translator | 6 | 8 |
| P3_rhythm | tolstoy_ak_garnett | dost_bk_garnett | translator only | 2 | 1 |
| P3_rhythm | fathers_garnett | gentlefolk_garnett | author+translator | 4 | 3 |
| P3_rhythm | gentlefolk_garnett | tolstoy_res_maude | neither | 28 | 16 |
| P4_mfw500_tag3 | dost_cp_garnett | dost_bk_garnett | author+translator | 2 | 4 |
| P4_mfw500_tag3 | dost_bk_garnett | dost_cp_garnett | author+translator | 2 | 4 |
| P4_mfw500_tag3 | dost_notes_garnett | dost_bk_garnett | author+translator | 3 | 6 |
| P4_mfw500_tag3 | tolstoy_ak_garnett | tolstoy_wp_maude | author only | 1 | 3 |
| P4_mfw500_tag3 | fathers_garnett | gentlefolk_garnett | author+translator | 3 | 2 |
| P4_mfw500_tag3 | gentlefolk_garnett | fathers_garnett | author+translator | 14 | 2 |
| P4_mfw500_tag3_rhythm | dost_cp_garnett | dost_bk_garnett | author+translator | 2 | 4 |
| P4_mfw500_tag3_rhythm | dost_bk_garnett | dost_cp_garnett | author+translator | 2 | 4 |
| P4_mfw500_tag3_rhythm | dost_notes_garnett | dost_bk_garnett | author+translator | 3 | 6 |
| P4_mfw500_tag3_rhythm | tolstoy_ak_garnett | tolstoy_wp_maude | author only | 1 | 3 |
| P4_mfw500_tag3_rhythm | fathers_garnett | gentlefolk_garnett | author+translator | 3 | 2 |
| P4_mfw500_tag3_rhythm | gentlefolk_garnett | fathers_garnett | author+translator | 15 | 2 |
| T1_scalars | dost_cp_garnett | dost_idiot_martin | author only | 1 | 4 |
| T1_scalars | dost_bk_garnett | dost_idiot_martin | author only | 1 | 5 |
| T1_scalars | dost_notes_garnett | zamyatin_we | neither | 48 | 32 |
| T1_scalars | tolstoy_ak_garnett | tolstoy_res_smith | author only | 1 | 6 |
| T1_scalars | fathers_garnett | james_ambassadors | neither | 12 | 5 |
| T1_scalars | gentlefolk_garnett | james_washington | neither | 16 | 3 |
| T1_bag | dost_cp_garnett | dost_idiot_martin | author only | 1 | 3 |
| T1_bag | dost_bk_garnett | dost_idiot_martin | author only | 1 | 2 |
| T1_bag | dost_notes_garnett | collins_moonstone | neither | 8 | 21 |
| T1_bag | tolstoy_ak_garnett | woolf_voyage | neither | 4 | 12 |
| T1_bag | fathers_garnett | dost_bk_garnett | translator only | 14 | 1 |
| T1_bag | gentlefolk_garnett | wharton_innocence | neither | 52 | 6 |
| T2_curves20_dtw | dost_cp_garnett | hardy_madding | neither | 30 | 9 |
| T2_curves20_dtw | dost_bk_garnett | wells_tono | neither | 76 | 10 |
| T2_curves20_dtw | dost_notes_garnett | conrad_almayer | neither | 70 | 7 |
| T2_curves20_dtw | tolstoy_ak_garnett | gentlefolk_garnett | translator only | 33 | 1 |
| T2_curves20_dtw | fathers_garnett | sinclair_olivier | neither | 59 | 16 |
| T2_curves20_dtw | gentlefolk_garnett | lesmis_wraxall | neither | 23 | 6 |
| T2_shape_nosd | dost_cp_garnett | tolstoy_res_maude | neither | 29 | 6 |
| T2_shape_nosd | dost_bk_garnett | fathers_garnett | translator only | 63 | 1 |
| T2_shape_nosd | dost_notes_garnett | fathers_garnett | translator only | 26 | 1 |
| T2_shape_nosd | tolstoy_ak_garnett | dubois_fleece | neither | 29 | 10 |
| T2_shape_nosd | fathers_garnett | burnett_princess | neither | 66 | 8 |
| T2_shape_nosd | gentlefolk_garnett | lesmis_wraxall | neither | 28 | 9 |
| T3_scalars_dtw20_sd | dost_cp_garnett | fathers_hogarth | neither | 3 | 6 |
| T3_scalars_dtw20_sd | dost_bk_garnett | hardy_madding | neither | 26 | 5 |
| T3_scalars_dtw20_sd | dost_notes_garnett | zamyatin_we | neither | 69 | 16 |
| T3_scalars_dtw20_sd | tolstoy_ak_garnett | gentlefolk_garnett | translator only | 5 | 1 |
| T3_scalars_dtw20_sd | fathers_garnett | dubois_fleece | neither | 30 | 3 |
| T3_scalars_dtw20_sd | gentlefolk_garnett | tolstoy_ak_garnett | translator only | 15 | 1 |

## Telling against Prose

rho = Spearman between the Telling and the Prose pair distances (3741 pairs; 3670 with different authors). "A minus B" = A with B regressed out.

| distance | rho | rho diff-author | AUC translation_pair (n=10) | AUC same_author_unrelated (n=52) | AUC series (n=7) | AUC retelling (n=8) | AUC same_genre (n=261) |
|---|---|---|---|---|---|---|---|
| T1_scalars | 0.41 | 0.39 | 0.98 | 0.76 | 0.86 | 0.41 | 0.56 |
| T1_scalars minus P4_mfw500_tag3_rhythm | 0.41 | 0.39 | 0.82 | 0.58 | 0.69 | 0.36 | 0.52 |
| P4_mfw500_tag3_rhythm | 0.41 | 0.39 | 1.00 | 0.99 | 1.00 | 0.73 | 0.61 |
| P4_mfw500_tag3_rhythm minus T1_scalars | 0.41 | 0.39 | 0.86 | 0.90 | 0.90 | 0.75 | 0.59 |
| T1_bag | 0.45 | 0.43 | 1.00 | 0.79 | 0.87 | 0.38 | 0.55 |
| T1_bag minus P4_mfw500_tag3_rhythm | 0.45 | 0.43 | 0.83 | 0.59 | 0.68 | 0.35 | 0.51 |
| P4_mfw500_tag3_rhythm | 0.45 | 0.43 | 1.00 | 0.99 | 1.00 | 0.73 | 0.61 |
| P4_mfw500_tag3_rhythm minus T1_bag | 0.45 | 0.43 | 0.84 | 0.90 | 0.89 | 0.75 | 0.59 |
| T2_curves20_dtw | 0.11 | 0.09 | 0.97 | 0.60 | 0.56 | 0.51 | 0.48 |
| T2_curves20_dtw minus P4_mfw500_tag3_rhythm | 0.11 | 0.09 | 0.92 | 0.55 | 0.51 | 0.49 | 0.47 |
| P4_mfw500_tag3_rhythm | 0.11 | 0.09 | 1.00 | 0.99 | 1.00 | 0.73 | 0.61 |
| P4_mfw500_tag3_rhythm minus T2_curves20_dtw | 0.11 | 0.09 | 0.96 | 0.97 | 0.98 | 0.73 | 0.61 |
| T2_shape_nosd | 0.14 | 0.13 | 1.00 | 0.58 | 0.58 | 0.50 | 0.48 |
| T2_shape_nosd minus P4_mfw500_tag3_rhythm | 0.14 | 0.13 | 0.94 | 0.51 | 0.52 | 0.47 | 0.47 |
| P4_mfw500_tag3_rhythm | 0.14 | 0.13 | 1.00 | 0.99 | 1.00 | 0.73 | 0.61 |
| P4_mfw500_tag3_rhythm minus T2_shape_nosd | 0.14 | 0.13 | 0.94 | 0.97 | 0.97 | 0.73 | 0.61 |
| T3_scalars_dtw20_sd | 0.32 | 0.31 | 0.99 | 0.72 | 0.78 | 0.45 | 0.52 |
| T3_scalars_dtw20_sd minus P4_mfw500_tag3_rhythm | 0.32 | 0.31 | 0.86 | 0.57 | 0.63 | 0.41 | 0.49 |
| P4_mfw500_tag3_rhythm | 0.32 | 0.31 | 1.00 | 0.99 | 1.00 | 0.73 | 0.61 |
| P4_mfw500_tag3_rhythm minus T3_scalars_dtw20_sd | 0.32 | 0.31 | 0.88 | 0.92 | 0.93 | 0.73 | 0.60 |

## Prose convergence

80 books with at least 50,000 words; 45 same-author pairs, 10 translation pairs, 3092 negatives; mean ± sd over 5 random samples. P1 = P1_mfw500_all_noprop_nocull, P2 = P2_tag3_1000, P3 = P3_rhythm, P4 = mean of the three median-scaled distances.

| block | words | rho_full | auc_author | auc_transl | self_acc |
|---|---|---|---|---|---|
| P1 | 1,000 | 0.483 ± 0.024 | 0.827 ± 0.028 | 0.907 ± 0.052 | 0.406 ± 0.054 |
| P1 | 2,000 | 0.656 ± 0.016 | 0.893 ± 0.019 | 0.957 ± 0.015 | 0.695 ± 0.027 |
| P1 | 5,000 | 0.829 ± 0.007 | 0.952 ± 0.008 | 0.989 ± 0.004 | 0.887 ± 0.033 |
| P1 | 10,000 | 0.907 ± 0.004 | 0.975 ± 0.004 | 0.996 ± 0.002 | 0.959 ± 0.014 |
| P1 | 20,000 | 0.953 ± 0.001 | 0.983 ± 0.002 | 0.997 ± 0.001 | 0.972 ± 0.006 |
| P1 | 50,000 | 0.985 ± 0.001 | 0.987 ± 0.001 | 0.998 ± 0.000 |  |
| P1 | whole book | 1.000 | 0.988 | 0.998 |  |
| P2 | 1,000 | 0.508 ± 0.035 | 0.786 ± 0.018 | 0.887 ± 0.024 | 0.378 ± 0.030 |
| P2 | 2,000 | 0.684 ± 0.014 | 0.868 ± 0.010 | 0.949 ± 0.018 | 0.565 ± 0.048 |
| P2 | 5,000 | 0.848 ± 0.011 | 0.919 ± 0.007 | 0.986 ± 0.005 | 0.860 ± 0.008 |
| P2 | 10,000 | 0.920 ± 0.006 | 0.944 ± 0.003 | 0.993 ± 0.001 | 0.944 ± 0.024 |
| P2 | 20,000 | 0.961 ± 0.002 | 0.954 ± 0.004 | 0.996 ± 0.002 | 0.968 ± 0.008 |
| P2 | 50,000 | 0.987 ± 0.001 | 0.967 ± 0.003 | 0.997 ± 0.001 |  |
| P2 | whole book | 1.000 | 0.969 | 0.997 |  |
| P3 | 1,000 | 0.693 ± 0.028 | 0.756 ± 0.026 | 0.674 ± 0.042 | 0.326 ± 0.020 |
| P3 | 2,000 | 0.807 ± 0.016 | 0.832 ± 0.025 | 0.778 ± 0.035 | 0.578 ± 0.050 |
| P3 | 5,000 | 0.911 ± 0.010 | 0.873 ± 0.018 | 0.836 ± 0.024 | 0.868 ± 0.022 |
| P3 | 10,000 | 0.952 ± 0.005 | 0.882 ± 0.011 | 0.867 ± 0.041 | 0.959 ± 0.006 |
| P3 | 20,000 | 0.976 ± 0.001 | 0.890 ± 0.004 | 0.871 ± 0.021 | 0.982 ± 0.010 |
| P3 | 50,000 | 0.991 ± 0.001 | 0.896 ± 0.004 | 0.883 ± 0.016 |  |
| P3 | whole book | 1.000 | 0.899 | 0.867 |  |
| P4 | 1,000 | 0.639 ± 0.016 | 0.835 ± 0.021 | 0.814 ± 0.041 | 0.575 ± 0.041 |
| P4 | 2,000 | 0.772 ± 0.003 | 0.915 ± 0.016 | 0.924 ± 0.032 | 0.831 ± 0.043 |
| P4 | 5,000 | 0.891 ± 0.008 | 0.957 ± 0.006 | 0.991 ± 0.004 | 0.943 ± 0.020 |
| P4 | 10,000 | 0.941 ± 0.005 | 0.975 ± 0.003 | 0.996 ± 0.002 | 0.975 ± 0.004 |
| P4 | 20,000 | 0.972 ± 0.002 | 0.981 ± 0.002 | 0.998 ± 0.000 | 0.976 ± 0.003 |
| P4 | 50,000 | 0.991 ± 0.000 | 0.985 ± 0.001 | 0.999 ± 0.000 |  |
| P4 | whole book | 1.000 | 0.986 | 0.999 |  |

## Prose candidates, all 87 books

AUC that a labelled pair is closer than a negative pair (3663 negatives; [95% bootstrap interval over the labelled pairs]). n = labelled pairs.

| block | translation_pair (n=10) | edition_pair (n=1) | same_author_unrelated (n=52) | same_author_orig_en (n=33) | same_author_same_translator (n=5) | same_author_diff_translator (n=14) | series (n=7) | retelling (n=8) | same_translator_diff_author (n=11) | same_genre (n=261) |
|---|---|---|---|---|---|---|---|---|---|---|
| P1_mfw100_all_noprop_nocull | 1.00 [1.00, 1.00] | 1.00 | 0.98 [0.97, 0.99] | 0.98 [0.96, 0.99] | 1.00 [1.00, 1.00] | 0.97 [0.95, 0.99] | 1.00 [0.99, 1.00] | 0.88 [0.78, 0.96] | 0.91 [0.81, 0.98] | 0.63 [0.59, 0.67] |
| P1_mfw200_all_noprop_nocull | 1.00 [1.00, 1.00] | 1.00 | 0.99 [0.98, 0.99] | 0.99 [0.97, 0.99] | 1.00 [1.00, 1.00] | 0.98 [0.97, 0.99] | 1.00 [0.99, 1.00] | 0.93 [0.85, 0.98] | 0.96 [0.92, 0.99] | 0.65 [0.61, 0.69] |
| P1_mfw500_all_noprop_nocull | 1.00 [1.00, 1.00] | 1.00 | 0.99 [0.98, 0.99] | 0.99 [0.99, 1.00] | 1.00 [1.00, 1.00] | 0.98 [0.96, 1.00] | 1.00 [1.00, 1.00] | 0.97 [0.94, 0.99] | 0.95 [0.90, 0.99] | 0.68 [0.65, 0.72] |
| P1_mfw500_all_raw_nocull | 1.00 [1.00, 1.00] | 1.00 | 0.99 [0.98, 0.99] | 0.99 [0.99, 1.00] | 1.00 [1.00, 1.00] | 0.98 [0.97, 1.00] | 1.00 [1.00, 1.00] | 0.97 [0.93, 0.99] | 0.96 [0.91, 0.99] | 0.68 [0.65, 0.72] |
| P1_mfw500_narr_noprop_nocull | 1.00 [1.00, 1.00] | 1.00 | 0.98 [0.96, 0.99] | 0.98 [0.96, 0.99] | 0.97 [0.91, 1.00] | 0.98 [0.96, 0.99] | 1.00 [0.99, 1.00] | 0.98 [0.97, 0.99] | 0.86 [0.70, 0.97] | 0.65 [0.62, 0.69] |
| P2_tag3_500 | 1.00 [0.99, 1.00] | 1.00 | 0.96 [0.94, 0.98] | 0.97 [0.95, 0.99] | 1.00 [1.00, 1.00] | 0.93 [0.87, 0.98] | 1.00 [0.99, 1.00] | 0.74 [0.55, 0.91] | 0.84 [0.73, 0.94] | 0.64 [0.60, 0.68] |
| P2_tag3_1000 | 1.00 [0.99, 1.00] | 1.00 | 0.97 [0.96, 0.99] | 0.98 [0.96, 0.99] | 1.00 [1.00, 1.00] | 0.95 [0.89, 0.99] | 1.00 [0.99, 1.00] | 0.77 [0.59, 0.92] | 0.88 [0.79, 0.95] | 0.65 [0.61, 0.68] |
| P2_tag3_500_words | 1.00 [0.99, 1.00] | 1.00 | 0.95 [0.91, 0.97] | 0.95 [0.90, 0.98] | 1.00 [1.00, 1.00] | 0.93 [0.87, 0.97] | 0.99 [0.97, 1.00] | 0.71 [0.53, 0.89] | 0.87 [0.77, 0.94] | 0.64 [0.60, 0.68] |
| P2_tag3_1000_words | 1.00 [0.99, 1.00] | 1.00 | 0.96 [0.93, 0.98] | 0.96 [0.91, 0.98] | 1.00 [1.00, 1.00] | 0.95 [0.90, 0.98] | 0.99 [0.98, 1.00] | 0.78 [0.62, 0.92] | 0.89 [0.80, 0.95] | 0.65 [0.62, 0.69] |
| P3_rhythm | 0.87 [0.72, 0.99] | 1.00 | 0.90 [0.85, 0.93] | 0.87 [0.81, 0.93] | 0.98 [0.97, 0.99] | 0.93 [0.90, 0.96] | 0.85 [0.64, 0.99] | 0.50 [0.25, 0.77] | 0.85 [0.79, 0.90] | 0.51 [0.47, 0.55] |
| P3_punct | 0.86 [0.73, 0.95] | 1.00 | 0.83 [0.78, 0.88] | 0.88 [0.81, 0.93] | 0.80 [0.72, 0.90] | 0.75 [0.63, 0.85] | 0.85 [0.72, 0.95] | 0.63 [0.45, 0.82] | 0.68 [0.55, 0.80] | 0.52 [0.49, 0.55] |
| P3_sentence | 0.69 [0.48, 0.88] | 1.00 | 0.82 [0.76, 0.87] | 0.77 [0.68, 0.85] | 0.91 [0.85, 0.98] | 0.90 [0.84, 0.95] | 0.81 [0.70, 0.92] | 0.36 [0.16, 0.58] | 0.84 [0.77, 0.89] | 0.48 [0.45, 0.51] |
| P3_lexical | 0.91 [0.76, 0.99] | 1.00 | 0.81 [0.74, 0.87] | 0.81 [0.71, 0.89] | 0.93 [0.84, 0.98] | 0.76 [0.66, 0.86] | 0.75 [0.40, 0.99] | 0.55 [0.28, 0.81] | 0.67 [0.57, 0.76] | 0.50 [0.47, 0.54] |
| P4_mfw500_tag3 | 1.00 [1.00, 1.00] | 1.00 | 0.99 [0.98, 0.99] | 0.99 [0.99, 1.00] | 1.00 [1.00, 1.00] | 0.97 [0.94, 1.00] | 1.00 [1.00, 1.00] | 0.92 [0.86, 0.98] | 0.93 [0.86, 0.98] | 0.67 [0.64, 0.71] |
| P4_mfw500_tag3_rhythm | 1.00 [1.00, 1.00] | 1.00 | 0.99 [0.98, 0.99] | 0.99 [0.98, 0.99] | 1.00 [1.00, 1.00] | 0.98 [0.96, 1.00] | 1.00 [0.99, 1.00] | 0.73 [0.44, 0.95] | 0.94 [0.90, 0.98] | 0.61 [0.57, 0.65] |
| P4_mfw100_tag3_rhythm | 1.00 [1.00, 1.00] | 1.00 | 0.99 [0.98, 0.99] | 0.99 [0.98, 0.99] | 1.00 [1.00, 1.00] | 0.98 [0.97, 0.99] | 1.00 [0.99, 1.00] | 0.71 [0.47, 0.92] | 0.93 [0.88, 0.98] | 0.60 [0.56, 0.64] |

AUC difference from `P1_mfw500_all_noprop_nocull` on the same pairs [paired bootstrap 95%].

| block | translation_pair (n=10) | edition_pair (n=1) | same_author_unrelated (n=52) | same_author_orig_en (n=33) | same_author_same_translator (n=5) | same_author_diff_translator (n=14) | series (n=7) | retelling (n=8) | same_translator_diff_author (n=11) | same_genre (n=261) |
|---|---|---|---|---|---|---|---|---|---|---|
| P1_mfw100_all_noprop_nocull | -0.00 [-0.00, +0.00] |  | -0.01 [-0.02, -0.00] | -0.01 [-0.03, +0.00] | -0.00 [-0.00, +0.00] | -0.01 [-0.03, +0.00] | -0.00 [-0.01, +0.00] | -0.09 [-0.17, -0.03] | -0.05 [-0.11, -0.01] | -0.05 [-0.07, -0.04] |
| P1_mfw200_all_noprop_nocull | +0.00 [-0.00, +0.00] |  | -0.00 [-0.01, +0.00] | -0.01 [-0.02, +0.00] | -0.00 [-0.00, +0.00] | +0.00 [-0.01, +0.01] | -0.00 [-0.00, +0.00] | -0.05 [-0.09, -0.01] | +0.00 [-0.01, +0.02] | -0.03 [-0.04, -0.02] |
| P1_mfw500_all_raw_nocull | +0.00 [+0.00, +0.00] |  | +0.00 [-0.00, +0.00] | -0.00 [-0.00, +0.00] | +0.00 [+0.00, +0.00] | +0.00 [-0.00, +0.01] | -0.00 [-0.00, +0.00] | -0.00 [-0.01, +0.00] | +0.00 [+0.00, +0.01] | +0.00 [-0.00, +0.00] |
| P1_mfw500_narr_noprop_nocull | +0.00 [+0.00, +0.00] |  | -0.01 [-0.03, +0.00] | -0.01 [-0.03, +0.00] | -0.03 [-0.09, +0.00] | -0.00 [-0.03, +0.02] | -0.00 [-0.01, +0.00] | +0.01 [-0.01, +0.04] | -0.10 [-0.21, +0.00] | -0.03 [-0.05, -0.01] |
| P2_tag3_500 | -0.00 [-0.00, -0.00] |  | -0.03 [-0.04, -0.01] | -0.02 [-0.04, -0.00] | -0.00 [-0.00, +0.00] | -0.05 [-0.09, -0.01] | -0.00 [-0.01, +0.00] | -0.23 [-0.43, -0.05] | -0.11 [-0.18, -0.05] | -0.04 [-0.07, -0.02] |
| P2_tag3_1000 | -0.00 [-0.00, -0.00] |  | -0.02 [-0.03, -0.00] | -0.01 [-0.03, -0.00] | +0.00 [-0.00, +0.00] | -0.03 [-0.07, -0.00] | -0.00 [-0.00, +0.00] | -0.20 [-0.40, -0.04] | -0.07 [-0.12, -0.03] | -0.04 [-0.06, -0.01] |
| P2_tag3_500_words | -0.00 [-0.01, -0.00] |  | -0.04 [-0.07, -0.02] | -0.04 [-0.09, -0.01] | -0.00 [-0.00, +0.00] | -0.05 [-0.08, -0.02] | -0.01 [-0.03, +0.00] | -0.26 [-0.45, -0.09] | -0.09 [-0.14, -0.05] | -0.04 [-0.06, -0.02] |
| P2_tag3_1000_words | -0.00 [-0.00, +0.00] |  | -0.03 [-0.06, -0.01] | -0.04 [-0.07, -0.01] | +0.00 [-0.00, +0.00] | -0.03 [-0.06, -0.01] | -0.01 [-0.02, +0.00] | -0.19 [-0.35, -0.06] | -0.06 [-0.11, -0.03] | -0.03 [-0.05, -0.01] |
| P3_rhythm | -0.13 [-0.28, -0.01] |  | -0.09 [-0.14, -0.06] | -0.12 [-0.19, -0.07] | -0.02 [-0.03, -0.00] | -0.05 [-0.08, -0.02] | -0.15 [-0.30, -0.00] | -0.47 [-0.72, -0.20] | -0.11 [-0.16, -0.06] | -0.17 [-0.21, -0.13] |
| P3_punct | -0.14 [-0.27, -0.05] |  | -0.16 [-0.21, -0.11] | -0.12 [-0.19, -0.06] | -0.20 [-0.27, -0.11] | -0.23 [-0.33, -0.13] | -0.15 [-0.28, -0.04] | -0.34 [-0.51, -0.16] | -0.28 [-0.42, -0.14] | -0.16 [-0.21, -0.12] |
| P3_sentence | -0.31 [-0.52, -0.12] |  | -0.17 [-0.24, -0.12] | -0.22 [-0.31, -0.14] | -0.08 [-0.15, -0.02] | -0.08 [-0.14, -0.04] | -0.18 [-0.30, -0.06] | -0.61 [-0.81, -0.38] | -0.11 [-0.18, -0.04] | -0.21 [-0.25, -0.16] |
| P3_lexical | -0.09 [-0.24, -0.00] |  | -0.18 [-0.25, -0.12] | -0.19 [-0.29, -0.10] | -0.07 [-0.16, -0.02] | -0.22 [-0.32, -0.12] | -0.25 [-0.50, -0.01] | -0.42 [-0.70, -0.15] | -0.29 [-0.36, -0.21] | -0.18 [-0.22, -0.14] |
| P4_mfw500_tag3 | -0.00 [-0.00, +0.00] |  | -0.00 [-0.01, +0.00] | -0.00 [-0.00, +0.00] | +0.00 [-0.00, +0.00] | -0.01 [-0.02, +0.00] | +0.00 [-0.00, +0.00] | -0.05 [-0.11, +0.00] | -0.02 [-0.04, -0.01] | -0.01 [-0.02, +0.00] |
| P4_mfw500_tag3_rhythm | +0.00 [-0.00, +0.00] |  | -0.00 [-0.01, +0.00] | -0.00 [-0.01, +0.00] | +0.00 [+0.00, +0.00] | +0.00 [-0.00, +0.01] | -0.00 [-0.00, +0.00] | -0.24 [-0.52, -0.02] | -0.01 [-0.02, +0.00] | -0.07 [-0.10, -0.05] |
| P4_mfw100_tag3_rhythm | -0.00 [-0.00, +0.00] |  | -0.00 [-0.01, +0.00] | -0.01 [-0.02, +0.00] | +0.00 [+0.00, +0.00] | +0.00 [-0.01, +0.01] | -0.00 [-0.01, +0.00] | -0.26 [-0.55, -0.04] | -0.02 [-0.04, -0.01] | -0.08 [-0.11, -0.06] |

Mean percentile rank of the partner (0 = nearest book) / recall@1 / recall@5.

| block | translation_pair (n=10) | edition_pair (n=1) | same_author_unrelated (n=52) | same_author_orig_en (n=33) | same_author_same_translator (n=5) | same_author_diff_translator (n=14) | series (n=7) | retelling (n=8) | same_translator_diff_author (n=11) | same_genre (n=261) |
|---|---|---|---|---|---|---|---|---|---|---|
| P1_mfw100_all_noprop_nocull | 0.00 / 0.88 / 1.00 | 0.00 / 1.00 / 1.00 | 0.03 / 0.65 / 0.98 | 0.02 / 0.72 / 0.97 | 0.01 / 0.86 / 1.00 | 0.04 / 0.12 / 0.94 | 0.00 / 1.00 / 1.00 | 0.13 / 0.30 / 0.80 | 0.11 / 0.00 / 0.83 | 0.38 / 0.13 / 0.75 |
| P1_mfw200_all_noprop_nocull | 0.01 / 0.88 / 0.94 | 0.00 / 1.00 / 1.00 | 0.02 / 0.71 / 1.00 | 0.02 / 0.81 / 1.00 | 0.01 / 0.86 / 1.00 | 0.03 / 0.12 / 0.94 | 0.00 / 1.00 / 1.00 | 0.09 / 0.30 / 0.80 | 0.07 / 0.00 / 1.00 | 0.36 / 0.17 / 0.74 |
| P1_mfw500_all_noprop_nocull | 0.00 / 0.94 / 0.94 | 0.00 / 1.00 / 1.00 | 0.02 / 0.69 / 1.00 | 0.01 / 0.81 / 1.00 | 0.01 / 0.71 / 1.00 | 0.03 / 0.12 / 0.94 | 0.00 / 1.00 / 1.00 | 0.04 / 0.50 / 0.80 | 0.07 / 0.00 / 1.00 | 0.33 / 0.19 / 0.79 |
| P1_mfw500_all_raw_nocull | 0.00 / 0.94 / 0.94 | 0.00 / 1.00 / 1.00 | 0.02 / 0.67 / 1.00 | 0.01 / 0.78 / 1.00 | 0.01 / 0.71 / 1.00 | 0.03 / 0.12 / 0.94 | 0.00 / 0.93 / 1.00 | 0.04 / 0.50 / 0.80 | 0.06 / 0.00 / 1.00 | 0.33 / 0.19 / 0.83 |
| P1_mfw500_narr_noprop_nocull | 0.00 / 0.94 / 0.94 | 0.00 / 1.00 / 1.00 | 0.03 / 0.65 / 1.00 | 0.02 / 0.75 / 1.00 | 0.04 / 0.71 / 1.00 | 0.03 / 0.12 / 0.88 | 0.00 / 0.86 / 1.00 | 0.04 / 0.50 / 0.90 | 0.16 / 0.00 / 0.83 | 0.36 / 0.21 / 0.68 |
| P2_tag3_500 | 0.00 / 0.94 / 0.94 | 0.00 / 1.00 / 1.00 | 0.04 / 0.58 / 0.88 | 0.03 / 0.66 / 0.97 | 0.01 / 0.71 / 1.00 | 0.07 / 0.12 / 0.62 | 0.00 / 0.93 / 1.00 | 0.27 / 0.30 / 0.60 | 0.18 / 0.00 / 0.83 | 0.38 / 0.11 / 0.77 |
| P2_tag3_1000 | 0.01 / 0.94 / 0.94 | 0.00 / 1.00 / 1.00 | 0.03 / 0.62 / 0.96 | 0.02 / 0.72 / 0.97 | 0.01 / 0.71 / 1.00 | 0.05 / 0.12 / 0.88 | 0.00 / 0.93 / 1.00 | 0.24 / 0.30 / 0.60 | 0.14 / 0.00 / 0.83 | 0.37 / 0.11 / 0.75 |
| P2_tag3_500_words | 0.00 / 0.88 / 1.00 | 0.00 / 1.00 / 1.00 | 0.06 / 0.58 / 0.83 | 0.06 / 0.62 / 0.88 | 0.01 / 0.86 / 1.00 | 0.07 / 0.12 / 0.62 | 0.00 / 0.93 / 1.00 | 0.31 / 0.20 / 0.50 | 0.16 / 0.00 / 0.83 | 0.37 / 0.04 / 0.70 |
| P2_tag3_1000_words | 0.01 / 0.88 / 0.94 | 0.00 / 1.00 / 1.00 | 0.05 / 0.60 / 0.88 | 0.05 / 0.66 / 0.88 | 0.01 / 0.86 / 1.00 | 0.06 / 0.12 / 0.81 | 0.00 / 0.93 / 1.00 | 0.25 / 0.30 / 0.50 | 0.13 / 0.00 / 0.83 | 0.36 / 0.06 / 0.77 |
| P3_rhythm | 0.02 / 0.59 / 1.00 | 0.00 / 1.00 / 1.00 | 0.12 / 0.48 / 0.73 | 0.14 / 0.56 / 0.75 | 0.03 / 0.57 / 0.57 | 0.10 / 0.06 / 0.62 | 0.10 / 0.50 / 0.71 | 0.43 / 0.20 / 0.60 | 0.20 / 0.17 / 0.67 | 0.49 / 0.09 / 0.43 |
| P3_punct | 0.10 / 0.24 / 0.65 | 0.00 / 1.00 / 1.00 | 0.14 / 0.42 / 0.79 | 0.11 / 0.50 / 0.84 | 0.15 / 0.14 / 0.57 | 0.21 / 0.19 / 0.50 | 0.19 / 0.29 / 0.43 | 0.35 / 0.20 / 0.50 | 0.25 / 0.33 / 0.83 | 0.50 / 0.02 / 0.36 |
| P3_sentence | 0.11 / 0.12 / 0.29 | 0.00 / 1.00 / 1.00 | 0.19 / 0.40 / 0.62 | 0.20 / 0.34 / 0.62 | 0.11 / 0.57 / 0.71 | 0.18 / 0.25 / 0.50 | 0.19 / 0.21 / 0.29 | 0.46 / 0.00 / 0.30 | 0.25 / 0.00 / 0.00 | 0.51 / 0.17 / 0.53 |
| P3_lexical | 0.10 / 0.76 / 0.88 | 0.00 / 1.00 / 1.00 | 0.19 / 0.27 / 0.62 | 0.20 / 0.38 / 0.72 | 0.07 / 0.00 / 0.71 | 0.22 / 0.06 / 0.31 | 0.16 / 0.43 / 0.64 | 0.45 / 0.30 / 0.40 | 0.37 / 0.17 / 0.17 | 0.48 / 0.09 / 0.53 |
| P4_mfw500_tag3 | 0.01 / 0.94 / 0.94 | 0.00 / 1.00 / 1.00 | 0.02 / 0.69 / 1.00 | 0.01 / 0.81 / 1.00 | 0.01 / 0.71 / 1.00 | 0.03 / 0.12 / 0.94 | 0.00 / 1.00 / 1.00 | 0.10 / 0.50 / 0.60 | 0.09 / 0.00 / 0.83 | 0.34 / 0.17 / 0.77 |
| P4_mfw500_tag3_rhythm | 0.00 / 0.94 / 1.00 | 0.00 / 1.00 / 1.00 | 0.02 / 0.69 / 0.98 | 0.02 / 0.81 / 0.97 | 0.01 / 0.71 / 1.00 | 0.03 / 0.12 / 0.94 | 0.00 / 0.86 / 1.00 | 0.24 / 0.30 / 0.50 | 0.09 / 0.00 / 0.83 | 0.38 / 0.09 / 0.72 |
| P4_mfw100_tag3_rhythm | 0.00 / 0.94 / 0.94 | 0.00 / 1.00 / 1.00 | 0.02 / 0.65 / 1.00 | 0.02 / 0.75 / 1.00 | 0.01 / 0.71 / 1.00 | 0.03 / 0.12 / 0.94 | 0.00 / 0.93 / 1.00 | 0.27 / 0.30 / 0.50 | 0.10 / 0.00 / 0.83 | 0.40 / 0.08 / 0.68 |

Split-half self-retrieval (accuracy; chance is 1/n), and Spearman of distance with |year difference| and |log word-count difference| (Mantel p in brackets; en = both books written in English; diff = different authors only).

| block | n | input | split a/b | split h1/h2 | rho year | rho year en | rho year en diff | rho logwords | rho logwords diff |
|---|---|---|---|---|---|---|---|---|---|
| P1_mfw100_all_noprop_nocull | 87 | ordered text | 0.97 | 0.89 | 0.15 (0.005) | 0.19 (0.005) | 0.15 | 0.04 (0.020) | 0.02 |
| P1_mfw200_all_noprop_nocull | 87 | ordered text | 0.96 | 0.89 | 0.17 (0.005) | 0.21 (0.005) | 0.18 | 0.04 (0.005) | 0.03 |
| P1_mfw500_all_noprop_nocull | 87 | ordered text | 0.97 | 0.92 | 0.18 (0.005) | 0.24 (0.005) | 0.21 | 0.06 (0.005) | 0.04 |
| P1_mfw500_all_raw_nocull | 87 | book bag | 0.97 | 0.93 | 0.18 (0.005) | 0.24 (0.005) | 0.21 | 0.06 (0.010) | 0.04 |
| P1_mfw500_narr_noprop_nocull | 87 | ordered text | 0.95 | 0.91 | 0.18 (0.005) | 0.25 (0.005) | 0.21 | 0.08 (0.005) | 0.07 |
| P2_tag3_500 | 87 | ordered text | 0.96 | 0.89 | 0.19 (0.005) | 0.26 (0.005) | 0.23 | 0.06 (0.005) | 0.05 |
| P2_tag3_1000 | 87 | ordered text | 0.97 | 0.90 | 0.21 (0.005) | 0.28 (0.005) | 0.25 | 0.06 (0.005) | 0.05 |
| P2_tag3_500_words | 87 | ordered text | 0.95 | 0.88 | 0.13 (0.005) | 0.19 (0.005) | 0.15 | 0.05 (0.010) | 0.04 |
| P2_tag3_1000_words | 87 | ordered text | 0.93 | 0.85 | 0.15 (0.005) | 0.21 (0.005) | 0.18 | 0.06 (0.010) | 0.04 |
| P3_rhythm | 87 | ordered text | 0.97 | 0.85 | 0.39 (0.005) | 0.27 (0.005) | 0.24 | 0.01 (0.845) | 0.00 |
| P3_punct | 87 | ordered text | 0.95 | 0.72 | 0.35 (0.005) | 0.32 (0.005) | 0.30 | -0.02 (0.655) | -0.04 |
| P3_sentence | 87 | ordered text | 0.79 | 0.43 | 0.40 (0.005) | 0.20 (0.010) | 0.18 | 0.01 (0.775) | 0.00 |
| P3_lexical | 87 | ordered text | 0.94 | 0.70 | 0.10 (0.050) | 0.17 (0.015) | 0.15 | 0.01 (0.905) | -0.00 |
| P4_mfw500_tag3 | 87 | ordered text | 0.97 | 0.90 | 0.20 (0.005) | 0.28 (0.005) | 0.24 | 0.06 (0.005) | 0.05 |
| P4_mfw500_tag3_rhythm | 87 | ordered text | 0.97 | 0.91 | 0.36 (0.005) | 0.34 (0.005) | 0.31 | 0.05 (0.195) | 0.03 |
| P4_mfw100_tag3_rhythm | 87 | ordered text | 0.97 | 0.91 | 0.33 (0.005) | 0.31 (0.005) | 0.28 | 0.04 (0.185) | 0.03 |

Top-5 neighbour make-up (observed / chance) and hubness (skew of the 5-nearest in-degree; share of books in nobody's top 5; largest in-degree and the book).

| block | same author | same genre | mean abs year diff | mean abs log-words diff | hub skew | in no top 5 | max in-degree |
|---|---|---|---|---|---|---|---|
| P1_mfw100_all_noprop_nocull | 0.39 / 0.02 | 0.42 / 0.12 | 34 / 56 | 0.66 / 0.78 | 0.25 | 0.02 | 11 (barsoom_gods) |
| P1_mfw200_all_noprop_nocull | 0.40 / 0.02 | 0.40 / 0.12 | 33 / 56 | 0.67 / 0.78 | 0.41 | 0.01 | 12 (barsoom_princess) |
| P1_mfw500_all_noprop_nocull | 0.41 / 0.02 | 0.47 / 0.12 | 32 / 56 | 0.63 / 0.78 | 0.33 | 0.02 | 11 (austen_emma) |
| P1_mfw500_all_raw_nocull | 0.41 / 0.02 | 0.45 / 0.12 | 31 / 56 | 0.64 / 0.78 | 0.33 | 0.02 | 11 (austen_emma) |
| P1_mfw500_narr_noprop_nocull | 0.39 / 0.02 | 0.40 / 0.12 | 29 / 56 | 0.61 / 0.78 | 0.18 | 0.01 | 11 (austen_emma) |
| P2_tag3_500 | 0.36 / 0.02 | 0.38 / 0.12 | 33 / 56 | 0.63 / 0.78 | 0.52 | 0.00 | 14 (wells_worlds) |
| P2_tag3_1000 | 0.38 / 0.02 | 0.37 / 0.12 | 34 / 56 | 0.62 / 0.78 | 0.84 | 0.02 | 15 (wells_worlds) |
| P2_tag3_500_words | 0.34 / 0.02 | 0.38 / 0.12 | 34 / 56 | 0.64 / 0.78 | 0.72 | 0.03 | 16 (wells_worlds) |
| P2_tag3_1000_words | 0.36 / 0.02 | 0.41 / 0.12 | 33 / 56 | 0.64 / 0.78 | 0.92 | 0.01 | 16 (wells_worlds) |
| P3_rhythm | 0.27 / 0.02 | 0.20 / 0.12 | 29 / 56 | 0.67 / 0.78 | 1.23 | 0.09 | 21 (woolf_voyage) |
| P3_punct | 0.21 / 0.02 | 0.16 / 0.12 | 31 / 56 | 0.71 / 0.78 | 0.42 | 0.07 | 14 (barset_towers) |
| P3_sentence | 0.18 / 0.02 | 0.21 / 0.12 | 34 / 56 | 0.76 / 0.78 | 0.23 | 0.02 | 12 (tolstoy_wp_maude) |
| P3_lexical | 0.22 / 0.02 | 0.22 / 0.12 | 46 / 56 | 0.65 / 0.78 | 1.14 | 0.03 | 17 (austen_northanger) |
| P4_mfw500_tag3 | 0.41 / 0.02 | 0.42 / 0.12 | 31 / 56 | 0.64 / 0.78 | 0.54 | 0.01 | 12 (austen_emma) |
| P4_mfw500_tag3_rhythm | 0.40 / 0.02 | 0.38 / 0.12 | 27 / 56 | 0.64 / 0.78 | 1.00 | 0.02 | 17 (wells_worlds) |
| P4_mfw100_tag3_rhythm | 0.39 / 0.02 | 0.37 / 0.12 | 28 / 56 | 0.65 / 0.78 | 0.98 | 0.02 | 17 (wells_worlds) |

Spearman between the pair distances of two blocks, all pairs.

| block | P1_mfw100_all_noprop_nocull | P1_mfw200_all_noprop_nocull | P1_mfw500_all_noprop_nocull | P1_mfw500_all_raw_nocull | P1_mfw500_narr_noprop_nocull | P2_tag3_500 | P2_tag3_1000 | P2_tag3_500_words | P2_tag3_1000_words | P3_rhythm | P3_punct | P3_sentence | P3_lexical | P4_mfw500_tag3 | P4_mfw500_tag3_rhythm | P4_mfw100_tag3_rhythm |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| P1_mfw100_all_noprop_nocull | 1.00 | 0.95 | 0.87 | 0.87 | 0.68 | 0.77 | 0.79 | 0.81 | 0.83 | 0.28 | 0.13 | 0.13 | 0.33 | 0.87 | 0.71 | 0.79 |
| P1_mfw200_all_noprop_nocull | 0.95 | 1.00 | 0.94 | 0.94 | 0.76 | 0.77 | 0.80 | 0.80 | 0.82 | 0.28 | 0.14 | 0.15 | 0.31 | 0.91 | 0.73 | 0.78 |
| P1_mfw500_all_noprop_nocull | 0.87 | 0.94 | 1.00 | 1.00 | 0.82 | 0.76 | 0.79 | 0.78 | 0.81 | 0.27 | 0.13 | 0.13 | 0.31 | 0.94 | 0.74 | 0.74 |
| P1_mfw500_all_raw_nocull | 0.87 | 0.94 | 1.00 | 1.00 | 0.82 | 0.76 | 0.79 | 0.78 | 0.81 | 0.27 | 0.13 | 0.13 | 0.32 | 0.93 | 0.74 | 0.74 |
| P1_mfw500_narr_noprop_nocull | 0.68 | 0.76 | 0.82 | 0.82 | 1.00 | 0.62 | 0.65 | 0.59 | 0.62 | 0.27 | 0.14 | 0.15 | 0.29 | 0.77 | 0.63 | 0.62 |
| P2_tag3_500 | 0.77 | 0.77 | 0.76 | 0.76 | 0.62 | 1.00 | 0.98 | 0.92 | 0.92 | 0.32 | 0.21 | 0.21 | 0.28 | 0.93 | 0.77 | 0.79 |
| P2_tag3_1000 | 0.79 | 0.80 | 0.79 | 0.79 | 0.65 | 0.98 | 1.00 | 0.92 | 0.93 | 0.33 | 0.22 | 0.22 | 0.29 | 0.95 | 0.79 | 0.81 |
| P2_tag3_500_words | 0.81 | 0.80 | 0.78 | 0.78 | 0.59 | 0.92 | 0.92 | 1.00 | 0.99 | 0.28 | 0.13 | 0.14 | 0.31 | 0.90 | 0.73 | 0.76 |
| P2_tag3_1000_words | 0.83 | 0.82 | 0.81 | 0.81 | 0.62 | 0.92 | 0.93 | 0.99 | 1.00 | 0.29 | 0.14 | 0.16 | 0.31 | 0.92 | 0.75 | 0.78 |
| P3_rhythm | 0.28 | 0.28 | 0.27 | 0.27 | 0.27 | 0.32 | 0.33 | 0.28 | 0.29 | 1.00 | 0.64 | 0.68 | 0.62 | 0.32 | 0.79 | 0.75 |
| P3_punct | 0.13 | 0.14 | 0.13 | 0.13 | 0.14 | 0.21 | 0.22 | 0.13 | 0.14 | 0.64 | 1.00 | 0.43 | 0.12 | 0.19 | 0.48 | 0.45 |
| P3_sentence | 0.13 | 0.15 | 0.13 | 0.13 | 0.15 | 0.21 | 0.22 | 0.14 | 0.16 | 0.68 | 0.43 | 1.00 | 0.08 | 0.19 | 0.52 | 0.48 |
| P3_lexical | 0.33 | 0.31 | 0.31 | 0.32 | 0.29 | 0.28 | 0.29 | 0.31 | 0.31 | 0.62 | 0.12 | 0.08 | 1.00 | 0.32 | 0.57 | 0.56 |
| P4_mfw500_tag3 | 0.87 | 0.91 | 0.94 | 0.93 | 0.77 | 0.93 | 0.95 | 0.90 | 0.92 | 0.32 | 0.19 | 0.19 | 0.32 | 1.00 | 0.81 | 0.82 |
| P4_mfw500_tag3_rhythm | 0.71 | 0.73 | 0.74 | 0.74 | 0.63 | 0.77 | 0.79 | 0.73 | 0.75 | 0.79 | 0.48 | 0.52 | 0.57 | 0.81 | 1.00 | 0.98 |
| P4_mfw100_tag3_rhythm | 0.79 | 0.78 | 0.74 | 0.74 | 0.62 | 0.79 | 0.81 | 0.76 | 0.78 | 0.75 | 0.45 | 0.48 | 0.56 | 0.82 | 0.98 | 1.00 |

Spearman between the pair distances of two blocks, different-author pairs only.

| block | P1_mfw100_all_noprop_nocull | P1_mfw200_all_noprop_nocull | P1_mfw500_all_noprop_nocull | P1_mfw500_all_raw_nocull | P1_mfw500_narr_noprop_nocull | P2_tag3_500 | P2_tag3_1000 | P2_tag3_500_words | P2_tag3_1000_words | P3_rhythm | P3_punct | P3_sentence | P3_lexical | P4_mfw500_tag3 | P4_mfw500_tag3_rhythm | P4_mfw100_tag3_rhythm |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| P1_mfw100_all_noprop_nocull | 1.00 | 0.94 | 0.86 | 0.86 | 0.66 | 0.75 | 0.78 | 0.80 | 0.82 | 0.25 | 0.10 | 0.10 | 0.31 | 0.87 | 0.69 | 0.78 |
| P1_mfw200_all_noprop_nocull | 0.94 | 1.00 | 0.94 | 0.94 | 0.75 | 0.76 | 0.79 | 0.79 | 0.81 | 0.25 | 0.10 | 0.12 | 0.29 | 0.91 | 0.71 | 0.76 |
| P1_mfw500_all_noprop_nocull | 0.86 | 0.94 | 1.00 | 1.00 | 0.81 | 0.75 | 0.78 | 0.77 | 0.80 | 0.24 | 0.10 | 0.10 | 0.29 | 0.93 | 0.72 | 0.73 |
| P1_mfw500_all_raw_nocull | 0.86 | 0.94 | 1.00 | 1.00 | 0.81 | 0.75 | 0.78 | 0.77 | 0.80 | 0.24 | 0.10 | 0.10 | 0.29 | 0.93 | 0.72 | 0.73 |
| P1_mfw500_narr_noprop_nocull | 0.66 | 0.75 | 0.81 | 0.81 | 1.00 | 0.60 | 0.63 | 0.57 | 0.60 | 0.24 | 0.11 | 0.12 | 0.27 | 0.75 | 0.61 | 0.60 |
| P2_tag3_500 | 0.75 | 0.76 | 0.75 | 0.75 | 0.60 | 1.00 | 0.98 | 0.92 | 0.92 | 0.29 | 0.18 | 0.19 | 0.25 | 0.93 | 0.76 | 0.78 |
| P2_tag3_1000 | 0.78 | 0.79 | 0.78 | 0.78 | 0.63 | 0.98 | 1.00 | 0.91 | 0.93 | 0.31 | 0.19 | 0.19 | 0.27 | 0.95 | 0.78 | 0.80 |
| P2_tag3_500_words | 0.80 | 0.79 | 0.77 | 0.77 | 0.57 | 0.92 | 0.91 | 1.00 | 0.98 | 0.25 | 0.10 | 0.12 | 0.28 | 0.90 | 0.71 | 0.75 |
| P2_tag3_1000_words | 0.82 | 0.81 | 0.80 | 0.80 | 0.60 | 0.92 | 0.93 | 0.98 | 1.00 | 0.26 | 0.11 | 0.13 | 0.29 | 0.92 | 0.73 | 0.77 |
| P3_rhythm | 0.25 | 0.25 | 0.24 | 0.24 | 0.24 | 0.29 | 0.31 | 0.25 | 0.26 | 1.00 | 0.63 | 0.67 | 0.61 | 0.29 | 0.78 | 0.74 |
| P3_punct | 0.10 | 0.10 | 0.10 | 0.10 | 0.11 | 0.18 | 0.19 | 0.10 | 0.11 | 0.63 | 1.00 | 0.43 | 0.10 | 0.15 | 0.46 | 0.43 |
| P3_sentence | 0.10 | 0.12 | 0.10 | 0.10 | 0.12 | 0.19 | 0.19 | 0.12 | 0.13 | 0.67 | 0.43 | 1.00 | 0.06 | 0.16 | 0.50 | 0.47 |
| P3_lexical | 0.31 | 0.29 | 0.29 | 0.29 | 0.27 | 0.25 | 0.27 | 0.28 | 0.29 | 0.61 | 0.10 | 0.06 | 1.00 | 0.29 | 0.56 | 0.55 |
| P4_mfw500_tag3 | 0.87 | 0.91 | 0.93 | 0.93 | 0.75 | 0.93 | 0.95 | 0.90 | 0.92 | 0.29 | 0.15 | 0.16 | 0.29 | 1.00 | 0.80 | 0.81 |
| P4_mfw500_tag3_rhythm | 0.69 | 0.71 | 0.72 | 0.72 | 0.61 | 0.76 | 0.78 | 0.71 | 0.73 | 0.78 | 0.46 | 0.50 | 0.56 | 0.80 | 1.00 | 0.98 |
| P4_mfw100_tag3_rhythm | 0.78 | 0.76 | 0.73 | 0.73 | 0.60 | 0.78 | 0.80 | 0.75 | 0.77 | 0.74 | 0.43 | 0.47 | 0.55 | 0.81 | 0.98 | 1.00 |


## Telling candidates, all 87 books

AUC that a labelled pair is closer than a negative pair (3663 negatives; [95% bootstrap interval over the labelled pairs]). n = labelled pairs.

| block | translation_pair (n=10) | edition_pair (n=1) | same_author_unrelated (n=52) | same_author_orig_en (n=33) | same_author_same_translator (n=5) | same_author_diff_translator (n=14) | series (n=7) | retelling (n=8) | same_translator_diff_author (n=11) | same_genre (n=261) |
|---|---|---|---|---|---|---|---|---|---|---|
| T1_scalars | 0.98 [0.95, 1.00] | 1.00 | 0.76 [0.68, 0.83] | 0.78 [0.70, 0.86] | 0.64 [0.29, 0.97] | 0.75 [0.60, 0.89] | 0.86 [0.74, 0.98] | 0.41 [0.17, 0.66] | 0.61 [0.40, 0.79] | 0.56 [0.52, 0.59] |
| T1_scalars_noquote | 0.99 [0.98, 1.00] | 1.00 | 0.83 [0.79, 0.87] | 0.85 [0.80, 0.89] | 0.84 [0.70, 0.95] | 0.78 [0.68, 0.88] | 0.90 [0.83, 0.97] | 0.40 [0.16, 0.65] | 0.65 [0.52, 0.79] | 0.56 [0.52, 0.60] |
| T1_bag | 1.00 [0.99, 1.00] | 1.00 | 0.79 [0.74, 0.84] | 0.82 [0.75, 0.88] | 0.80 [0.65, 0.93] | 0.73 [0.61, 0.85] | 0.87 [0.78, 0.97] | 0.38 [0.14, 0.66] | 0.63 [0.49, 0.78] | 0.55 [0.52, 0.59] |
| T2_curves20_euc | 0.95 [0.88, 1.00] | 1.00 | 0.55 [0.47, 0.64] | 0.64 [0.54, 0.74] | 0.44 [0.17, 0.71] | 0.39 [0.28, 0.51] | 0.64 [0.36, 0.89] | 0.37 [0.20, 0.56] | 0.50 [0.32, 0.70] | 0.48 [0.45, 0.52] |
| T2_curves50_euc | 0.94 [0.86, 1.00] | 1.00 | 0.60 [0.51, 0.68] | 0.68 [0.57, 0.78] | 0.63 [0.32, 0.87] | 0.39 [0.27, 0.51] | 0.63 [0.29, 0.90] | 0.33 [0.22, 0.45] | 0.56 [0.41, 0.71] | 0.47 [0.44, 0.51] |
| T2_curves20_dtw | 0.97 [0.93, 1.00] | 1.00 | 0.60 [0.52, 0.69] | 0.63 [0.52, 0.73] | 0.62 [0.34, 0.85] | 0.52 [0.39, 0.67] | 0.56 [0.33, 0.77] | 0.51 [0.33, 0.69] | 0.65 [0.48, 0.80] | 0.48 [0.45, 0.52] |
| T2_curves50_dtw | 0.94 [0.85, 1.00] | 1.00 | 0.62 [0.54, 0.70] | 0.61 [0.51, 0.72] | 0.57 [0.37, 0.77] | 0.65 [0.50, 0.77] | 0.51 [0.27, 0.76] | 0.51 [0.33, 0.68] | 0.75 [0.61, 0.87] | 0.47 [0.43, 0.50] |
| T2_shape | 1.00 [1.00, 1.00] | 1.00 | 0.62 [0.55, 0.68] | 0.67 [0.59, 0.74] | 0.43 [0.19, 0.68] | 0.56 [0.43, 0.67] | 0.60 [0.33, 0.84] | 0.51 [0.36, 0.67] | 0.54 [0.38, 0.70] | 0.50 [0.47, 0.54] |
| T2_shape_nosd | 1.00 [0.99, 1.00] | 1.00 | 0.58 [0.51, 0.64] | 0.63 [0.55, 0.71] | 0.38 [0.18, 0.61] | 0.52 [0.41, 0.63] | 0.58 [0.31, 0.83] | 0.50 [0.31, 0.71] | 0.60 [0.41, 0.78] | 0.48 [0.45, 0.52] |
| T2_dialogue20 | 0.87 [0.72, 0.97] | 1.00 | 0.45 [0.38, 0.52] | 0.48 [0.39, 0.58] | 0.38 [0.16, 0.62] | 0.41 [0.31, 0.50] | 0.63 [0.39, 0.86] | 0.43 [0.24, 0.62] | 0.54 [0.38, 0.68] | 0.48 [0.45, 0.52] |
| T2_sentence_length20 | 0.84 [0.71, 0.96] | 0.99 | 0.56 [0.49, 0.63] | 0.58 [0.49, 0.67] | 0.47 [0.37, 0.56] | 0.53 [0.38, 0.67] | 0.62 [0.36, 0.86] | 0.37 [0.21, 0.57] | 0.56 [0.43, 0.69] | 0.49 [0.46, 0.53] |
| T2_valence20 | 0.86 [0.74, 0.96] | 1.00 | 0.52 [0.44, 0.60] | 0.56 [0.45, 0.66] | 0.52 [0.23, 0.83] | 0.41 [0.31, 0.52] | 0.40 [0.26, 0.58] | 0.49 [0.39, 0.60] | 0.60 [0.43, 0.75] | 0.51 [0.47, 0.54] |
| T2_arousal20 | 0.90 [0.77, 1.00] | 1.00 | 0.48 [0.41, 0.56] | 0.50 [0.40, 0.59] | 0.38 [0.18, 0.58] | 0.48 [0.33, 0.62] | 0.59 [0.49, 0.68] | 0.36 [0.17, 0.57] | 0.42 [0.26, 0.58] | 0.48 [0.45, 0.52] |
| T2_first_person20 | 0.77 [0.62, 0.90] | 0.93 | 0.60 [0.51, 0.67] | 0.67 [0.58, 0.76] | 0.64 [0.52, 0.77] | 0.41 [0.28, 0.55] | 0.54 [0.32, 0.74] | 0.56 [0.37, 0.74] | 0.53 [0.41, 0.66] | 0.50 [0.46, 0.53] |
| T2_new_vocab20 | 0.92 [0.79, 0.99] | 1.00 | 0.57 [0.49, 0.65] | 0.59 [0.51, 0.68] | 0.46 [0.11, 0.82] | 0.54 [0.39, 0.70] | 0.47 [0.24, 0.69] | 0.61 [0.47, 0.76] | 0.44 [0.25, 0.64] | 0.51 [0.48, 0.55] |
| T3_scalars_dtw20 | 0.99 [0.97, 1.00] | 1.00 | 0.76 [0.68, 0.83] | 0.78 [0.69, 0.86] | 0.64 [0.29, 0.93] | 0.76 [0.62, 0.88] | 0.86 [0.72, 0.97] | 0.42 [0.17, 0.67] | 0.62 [0.43, 0.80] | 0.55 [0.51, 0.59] |
| T3_scalars_dtw20_sd | 0.99 [0.97, 1.00] | 1.00 | 0.72 [0.64, 0.79] | 0.73 [0.64, 0.82] | 0.62 [0.36, 0.88] | 0.72 [0.58, 0.84] | 0.78 [0.60, 0.91] | 0.45 [0.22, 0.68] | 0.64 [0.46, 0.80] | 0.52 [0.49, 0.56] |
| T3_scalars_shape | 1.00 [0.99, 1.00] | 1.00 | 0.75 [0.68, 0.81] | 0.78 [0.69, 0.85] | 0.60 [0.28, 0.93] | 0.73 [0.60, 0.85] | 0.79 [0.58, 0.96] | 0.43 [0.17, 0.68] | 0.61 [0.41, 0.79] | 0.55 [0.51, 0.58] |
| T3_scalars_dtw20_shape | 1.00 [0.99, 1.00] | 1.00 | 0.74 [0.67, 0.81] | 0.76 [0.68, 0.84] | 0.60 [0.28, 0.91] | 0.73 [0.59, 0.83] | 0.78 [0.56, 0.94] | 0.44 [0.22, 0.68] | 0.61 [0.42, 0.79] | 0.54 [0.50, 0.57] |
| T3_noquote_shape | 1.00 [1.00, 1.00] | 1.00 | 0.81 [0.76, 0.85] | 0.84 [0.79, 0.88] | 0.74 [0.54, 0.87] | 0.77 [0.69, 0.85] | 0.82 [0.63, 0.96] | 0.41 [0.18, 0.67] | 0.64 [0.48, 0.81] | 0.55 [0.52, 0.59] |
| T3_noquote_shape_sd | 1.00 [1.00, 1.00] | 1.00 | 0.79 [0.75, 0.84] | 0.82 [0.77, 0.88] | 0.70 [0.50, 0.86] | 0.75 [0.67, 0.83] | 0.79 [0.56, 0.94] | 0.42 [0.19, 0.66] | 0.63 [0.47, 0.80] | 0.55 [0.51, 0.58] |

AUC difference from `T1_scalars` on the same pairs [paired bootstrap 95%].

| block | translation_pair (n=10) | edition_pair (n=1) | same_author_unrelated (n=52) | same_author_orig_en (n=33) | same_author_same_translator (n=5) | same_author_diff_translator (n=14) | series (n=7) | retelling (n=8) | same_translator_diff_author (n=11) | same_genre (n=261) |
|---|---|---|---|---|---|---|---|---|---|---|
| T1_scalars_noquote | +0.01 [+0.00, +0.03] |  | +0.07 [+0.02, +0.13] | +0.07 [+0.02, +0.13] | +0.19 [-0.10, +0.51] | +0.03 [-0.06, +0.15] | +0.03 [-0.03, +0.10] | -0.01 [-0.07, +0.04] | +0.05 [-0.11, +0.20] | +0.00 [-0.01, +0.02] |
| T1_bag | +0.02 [-0.00, +0.04] |  | +0.03 [-0.02, +0.09] | +0.03 [-0.02, +0.09] | +0.15 [-0.11, +0.43] | -0.01 [-0.09, +0.10] | +0.01 [-0.08, +0.09] | -0.02 [-0.07, +0.03] | +0.02 [-0.08, +0.14] | -0.01 [-0.03, +0.02] |
| T2_curves20_euc | -0.03 [-0.10, +0.03] |  | -0.21 [-0.32, -0.09] | -0.14 [-0.27, -0.01] | -0.20 [-0.68, +0.36] | -0.36 [-0.56, -0.15] | -0.23 [-0.54, +0.04] | -0.04 [-0.18, +0.08] | -0.11 [-0.34, +0.13] | -0.07 [-0.12, -0.02] |
| T2_curves50_euc | -0.04 [-0.13, +0.03] |  | -0.16 [-0.27, -0.05] | -0.10 [-0.23, +0.02] | -0.01 [-0.49, +0.48] | -0.36 [-0.53, -0.18] | -0.24 [-0.56, +0.03] | -0.08 [-0.36, +0.18] | -0.05 [-0.25, +0.15] | -0.08 [-0.13, -0.04] |
| T2_curves20_dtw | -0.01 [-0.03, +0.01] |  | -0.16 [-0.26, -0.06] | -0.16 [-0.26, -0.06] | -0.02 [-0.45, +0.37] | -0.22 [-0.44, +0.00] | -0.30 [-0.55, -0.07] | +0.11 [-0.14, +0.32] | +0.04 [-0.19, +0.28] | -0.08 [-0.12, -0.03] |
| T2_curves50_dtw | -0.04 [-0.11, +0.00] |  | -0.14 [-0.24, -0.05] | -0.17 [-0.28, -0.07] | -0.07 [-0.41, +0.25] | -0.10 [-0.31, +0.09] | -0.36 [-0.64, -0.07] | +0.10 [-0.17, +0.38] | +0.14 [-0.05, +0.33] | -0.09 [-0.13, -0.04] |
| T2_shape | +0.02 [+0.00, +0.05] |  | -0.14 [-0.22, -0.07] | -0.11 [-0.19, -0.03] | -0.21 [-0.40, -0.04] | -0.19 [-0.36, -0.04] | -0.26 [-0.50, -0.06] | +0.11 [-0.17, +0.35] | -0.07 [-0.22, +0.06] | -0.06 [-0.09, -0.02] |
| T2_shape_nosd | +0.02 [+0.00, +0.05] |  | -0.18 [-0.26, -0.10] | -0.15 [-0.25, -0.05] | -0.26 [-0.49, -0.05] | -0.22 [-0.41, -0.04] | -0.28 [-0.54, -0.07] | +0.09 [-0.13, +0.31] | -0.01 [-0.17, +0.16] | -0.07 [-0.11, -0.03] |
| T2_dialogue20 | -0.11 [-0.26, -0.01] |  | -0.31 [-0.42, -0.19] | -0.30 [-0.42, -0.16] | -0.27 [-0.79, +0.27] | -0.34 [-0.55, -0.11] | -0.23 [-0.52, +0.03] | +0.03 [-0.16, +0.23] | -0.07 [-0.30, +0.18] | -0.07 [-0.12, -0.03] |
| T2_sentence_length20 | -0.14 [-0.25, -0.04] |  | -0.20 [-0.30, -0.10] | -0.20 [-0.32, -0.08] | -0.17 [-0.53, +0.19] | -0.22 [-0.47, +0.02] | -0.24 [-0.54, +0.05] | -0.04 [-0.21, +0.12] | -0.05 [-0.26, +0.19] | -0.06 [-0.11, -0.01] |
| T2_valence20 | -0.12 [-0.23, -0.02] |  | -0.24 [-0.34, -0.14] | -0.22 [-0.35, -0.09] | -0.12 [-0.52, +0.35] | -0.34 [-0.48, -0.19] | -0.46 [-0.66, -0.27] | +0.09 [-0.16, +0.31] | -0.01 [-0.15, +0.15] | -0.05 [-0.10, +0.00] |
| T2_arousal20 | -0.08 [-0.23, +0.03] |  | -0.28 [-0.37, -0.18] | -0.29 [-0.39, -0.18] | -0.26 [-0.70, +0.18] | -0.26 [-0.50, -0.03] | -0.27 [-0.44, -0.11] | -0.04 [-0.29, +0.19] | -0.19 [-0.40, +0.01] | -0.07 [-0.12, -0.03] |
| T2_first_person20 | -0.21 [-0.35, -0.08] |  | -0.16 [-0.26, -0.06] | -0.11 [-0.23, +0.01] | -0.00 [-0.42, +0.42] | -0.34 [-0.49, -0.15] | -0.32 [-0.52, -0.13] | +0.16 [-0.20, +0.48] | -0.08 [-0.29, +0.14] | -0.06 [-0.11, -0.01] |
| T2_new_vocab20 | -0.06 [-0.20, +0.02] |  | -0.19 [-0.27, -0.11] | -0.19 [-0.29, -0.08] | -0.18 [-0.49, +0.01] | -0.20 [-0.32, -0.10] | -0.40 [-0.55, -0.23] | +0.21 [-0.05, +0.46] | -0.17 [-0.37, +0.01] | -0.05 [-0.08, -0.01] |
| T3_scalars_dtw20 | +0.01 [+0.00, +0.02] |  | +0.00 [-0.02, +0.02] | -0.00 [-0.03, +0.02] | +0.00 [-0.06, +0.05] | +0.01 [-0.03, +0.06] | -0.01 [-0.05, +0.03] | +0.01 [-0.02, +0.04] | +0.01 [-0.03, +0.06] | -0.01 [-0.02, +0.00] |
| T3_scalars_dtw20_sd | +0.01 [-0.00, +0.02] |  | -0.04 [-0.10, +0.01] | -0.05 [-0.11, +0.01] | -0.02 [-0.26, +0.16] | -0.03 [-0.16, +0.09] | -0.08 [-0.21, +0.03] | +0.05 [-0.06, +0.15] | +0.03 [-0.09, +0.15] | -0.03 [-0.06, -0.01] |
| T3_scalars_shape | +0.02 [+0.00, +0.04] |  | -0.01 [-0.03, +0.01] | -0.01 [-0.03, +0.02] | -0.04 [-0.08, -0.01] | -0.01 [-0.05, +0.02] | -0.07 [-0.19, +0.02] | +0.02 [-0.04, +0.07] | -0.00 [-0.06, +0.04] | -0.01 [-0.02, +0.00] |
| T3_scalars_dtw20_shape | +0.02 [+0.00, +0.04] |  | -0.02 [-0.06, +0.01] | -0.02 [-0.06, +0.03] | -0.05 [-0.14, +0.01] | -0.02 [-0.10, +0.05] | -0.08 [-0.22, +0.03] | +0.04 [-0.02, +0.10] | +0.00 [-0.07, +0.07] | -0.02 [-0.04, -0.00] |
| T3_noquote_shape | +0.02 [+0.00, +0.05] |  | +0.05 [-0.00, +0.10] | +0.06 [+0.00, +0.12] | +0.09 [-0.12, +0.36] | +0.02 [-0.07, +0.13] | -0.04 [-0.16, +0.05] | +0.00 [-0.10, +0.07] | +0.03 [-0.10, +0.19] | -0.00 [-0.02, +0.02] |
| T3_noquote_shape_sd | +0.02 [+0.00, +0.05] |  | +0.03 [-0.02, +0.09] | +0.04 [-0.02, +0.10] | +0.06 [-0.14, +0.27] | +0.00 [-0.10, +0.12] | -0.07 [-0.22, +0.05] | +0.01 [-0.10, +0.08] | +0.03 [-0.11, +0.18] | -0.01 [-0.03, +0.01] |

Mean percentile rank of the partner (0 = nearest book) / recall@1 / recall@5.

| block | translation_pair (n=10) | edition_pair (n=1) | same_author_unrelated (n=52) | same_author_orig_en (n=33) | same_author_same_translator (n=5) | same_author_diff_translator (n=14) | series (n=7) | retelling (n=8) | same_translator_diff_author (n=11) | same_genre (n=261) |
|---|---|---|---|---|---|---|---|---|---|---|
| T1_scalars | 0.01 / 0.88 / 1.00 | 0.00 / 1.00 / 1.00 | 0.24 / 0.25 / 0.48 | 0.23 / 0.22 / 0.50 | 0.31 / 0.00 / 0.43 | 0.23 / 0.31 / 0.44 | 0.10 / 0.43 / 0.71 | 0.48 / 0.20 / 0.20 | 0.37 / 0.00 / 0.50 | 0.42 / 0.26 / 0.57 |
| T1_scalars_noquote | 0.00 / 1.00 / 1.00 | 0.00 / 1.00 / 1.00 | 0.16 / 0.33 / 0.52 | 0.17 / 0.34 / 0.53 | 0.12 / 0.00 / 0.43 | 0.17 / 0.31 / 0.44 | 0.09 / 0.36 / 0.64 | 0.46 / 0.20 / 0.20 | 0.33 / 0.00 / 0.83 | 0.44 / 0.13 / 0.47 |
| T1_bag | 0.00 / 0.94 / 1.00 | 0.00 / 1.00 / 1.00 | 0.19 / 0.17 / 0.52 | 0.19 / 0.16 / 0.53 | 0.16 / 0.00 / 0.43 | 0.20 / 0.19 / 0.44 | 0.10 / 0.43 / 0.64 | 0.45 / 0.20 / 0.30 | 0.37 / 0.00 / 0.50 | 0.44 / 0.11 / 0.43 |
| T2_curves20_euc | 0.05 / 0.71 / 0.76 | 0.00 / 1.00 / 1.00 | 0.45 / 0.10 / 0.23 | 0.37 / 0.12 / 0.31 | 0.59 / 0.14 / 0.14 | 0.58 / 0.00 / 0.00 | 0.36 / 0.07 / 0.14 | 0.57 / 0.00 / 0.00 | 0.50 / 0.00 / 0.50 | 0.51 / 0.04 / 0.49 |
| T2_curves50_euc | 0.06 / 0.76 / 0.76 | 0.00 / 1.00 / 1.00 | 0.41 / 0.08 / 0.25 | 0.33 / 0.09 / 0.34 | 0.40 / 0.14 / 0.14 | 0.60 / 0.00 / 0.00 | 0.35 / 0.14 / 0.29 | 0.63 / 0.00 / 0.00 | 0.45 / 0.00 / 0.50 | 0.53 / 0.08 / 0.47 |
| T2_curves20_dtw | 0.03 / 0.88 / 0.94 | 0.00 / 1.00 / 1.00 | 0.40 / 0.04 / 0.33 | 0.36 / 0.06 / 0.41 | 0.39 / 0.00 / 0.00 | 0.50 / 0.00 / 0.19 | 0.42 / 0.00 / 0.00 | 0.40 / 0.00 / 0.10 | 0.41 / 0.17 / 0.17 | 0.50 / 0.08 / 0.57 |
| T2_curves50_dtw | 0.04 / 0.82 / 0.94 | 0.00 / 1.00 / 1.00 | 0.38 / 0.04 / 0.25 | 0.36 / 0.06 / 0.38 | 0.46 / 0.00 / 0.00 | 0.41 / 0.00 / 0.00 | 0.47 / 0.00 / 0.00 | 0.39 / 0.00 / 0.30 | 0.32 / 0.17 / 0.83 | 0.50 / 0.15 / 0.53 |
| T2_shape | 0.00 / 1.00 / 1.00 | 0.00 / 1.00 / 1.00 | 0.41 / 0.02 / 0.17 | 0.34 / 0.03 / 0.25 | 0.56 / 0.00 / 0.00 | 0.51 / 0.00 / 0.00 | 0.38 / 0.07 / 0.14 | 0.45 / 0.00 / 0.00 | 0.48 / 0.17 / 0.33 | 0.49 / 0.17 / 0.53 |
| T2_shape_nosd | 0.00 / 0.94 / 1.00 | 0.00 / 1.00 / 1.00 | 0.45 / 0.02 / 0.17 | 0.38 / 0.03 / 0.25 | 0.61 / 0.00 / 0.00 | 0.55 / 0.00 / 0.00 | 0.42 / 0.00 / 0.07 | 0.45 / 0.00 / 0.00 | 0.44 / 0.33 / 0.33 | 0.50 / 0.19 / 0.49 |
| T2_dialogue20 | 0.14 / 0.59 / 0.59 | 0.00 / 1.00 / 1.00 | 0.55 / 0.00 / 0.04 | 0.53 / 0.00 / 0.06 | 0.63 / 0.00 / 0.00 | 0.57 / 0.00 / 0.00 | 0.35 / 0.07 / 0.29 | 0.53 / 0.00 / 0.00 | 0.42 / 0.00 / 0.00 | 0.53 / 0.13 / 0.45 |
| T2_sentence_length20 | 0.15 / 0.53 / 0.71 | 0.00 / 1.00 / 1.00 | 0.46 / 0.02 / 0.12 | 0.43 / 0.03 / 0.19 | 0.54 / 0.00 / 0.00 | 0.49 / 0.00 / 0.00 | 0.35 / 0.14 / 0.29 | 0.61 / 0.00 / 0.10 | 0.45 / 0.00 / 0.00 | 0.51 / 0.06 / 0.40 |
| T2_valence20 | 0.12 / 0.71 / 0.71 | 0.01 / 0.50 / 1.00 | 0.50 / 0.00 / 0.15 | 0.46 / 0.00 / 0.16 | 0.50 / 0.00 / 0.29 | 0.59 / 0.00 / 0.00 | 0.50 / 0.00 / 0.07 | 0.47 / 0.00 / 0.00 | 0.39 / 0.00 / 0.33 | 0.48 / 0.13 / 0.53 |
| T2_arousal20 | 0.11 / 0.76 / 0.76 | 0.00 / 1.00 / 1.00 | 0.52 / 0.08 / 0.08 | 0.50 / 0.12 / 0.12 | 0.64 / 0.00 / 0.00 | 0.52 / 0.00 / 0.00 | 0.44 / 0.00 / 0.00 | 0.61 / 0.00 / 0.00 | 0.60 / 0.00 / 0.00 | 0.52 / 0.09 / 0.43 |
| T2_first_person20 | 0.21 / 0.29 / 0.47 | 0.02 / 0.00 / 1.00 | 0.40 / 0.08 / 0.25 | 0.33 / 0.12 / 0.34 | 0.38 / 0.00 / 0.14 | 0.57 / 0.00 / 0.00 | 0.45 / 0.00 / 0.14 | 0.42 / 0.00 / 0.00 | 0.49 / 0.00 / 0.00 | 0.49 / 0.08 / 0.43 |
| T2_new_vocab20 | 0.07 / 0.71 / 0.71 | 0.00 / 1.00 / 1.00 | 0.44 / 0.04 / 0.17 | 0.43 / 0.03 / 0.12 | 0.52 / 0.00 / 0.29 | 0.45 / 0.06 / 0.12 | 0.51 / 0.00 / 0.07 | 0.38 / 0.00 / 0.00 | 0.54 / 0.00 / 0.00 | 0.50 / 0.19 / 0.53 |
| T3_scalars_dtw20 | 0.00 / 1.00 / 1.00 | 0.00 / 1.00 / 1.00 | 0.24 / 0.31 / 0.56 | 0.23 / 0.41 / 0.56 | 0.32 / 0.00 / 0.57 | 0.23 / 0.12 / 0.44 | 0.09 / 0.36 / 0.71 | 0.46 / 0.20 / 0.20 | 0.37 / 0.17 / 0.83 | 0.43 / 0.15 / 0.47 |
| T3_scalars_dtw20_sd | 0.01 / 0.94 / 1.00 | 0.00 / 1.00 / 1.00 | 0.29 / 0.15 / 0.52 | 0.27 / 0.22 / 0.62 | 0.37 / 0.00 / 0.29 | 0.31 / 0.00 / 0.25 | 0.18 / 0.14 / 0.29 | 0.42 / 0.00 / 0.30 | 0.38 / 0.17 / 0.67 | 0.45 / 0.17 / 0.55 |
| T3_scalars_shape | 0.00 / 1.00 / 1.00 | 0.00 / 1.00 / 1.00 | 0.25 / 0.19 / 0.44 | 0.23 / 0.22 / 0.44 | 0.36 / 0.00 / 0.43 | 0.27 / 0.12 / 0.38 | 0.15 / 0.43 / 0.50 | 0.47 / 0.10 / 0.20 | 0.38 / 0.17 / 0.83 | 0.43 / 0.09 / 0.55 |
| T3_scalars_dtw20_shape | 0.00 / 1.00 / 1.00 | 0.00 / 1.00 / 1.00 | 0.27 / 0.21 / 0.42 | 0.24 / 0.25 / 0.47 | 0.38 / 0.00 / 0.29 | 0.28 / 0.12 / 0.25 | 0.17 / 0.29 / 0.43 | 0.45 / 0.10 / 0.20 | 0.38 / 0.33 / 0.83 | 0.44 / 0.13 / 0.58 |
| T3_noquote_shape | 0.00 / 1.00 / 1.00 | 0.00 / 1.00 / 1.00 | 0.19 / 0.19 / 0.54 | 0.19 / 0.22 / 0.59 | 0.20 / 0.00 / 0.29 | 0.21 / 0.12 / 0.44 | 0.15 / 0.36 / 0.43 | 0.46 / 0.20 / 0.20 | 0.36 / 0.17 / 0.83 | 0.45 / 0.15 / 0.43 |
| T3_noquote_shape_sd | 0.00 / 1.00 / 1.00 | 0.00 / 1.00 / 1.00 | 0.21 / 0.19 / 0.48 | 0.20 / 0.22 / 0.53 | 0.25 / 0.00 / 0.29 | 0.23 / 0.12 / 0.38 | 0.18 / 0.36 / 0.43 | 0.46 / 0.10 / 0.20 | 0.36 / 0.17 / 1.00 | 0.45 / 0.09 / 0.43 |

Split-half self-retrieval (accuracy; chance is 1/n), and Spearman of distance with |year difference| and |log word-count difference| (Mantel p in brackets; en = both books written in English; diff = different authors only).

| block | n | input | split a/b | split h1/h2 | rho year | rho year en | rho year en diff | rho logwords | rho logwords diff |
|---|---|---|---|---|---|---|---|---|---|
| T1_scalars | 87 | ordered text | 0.90 | 0.71 | 0.17 (0.010) | 0.11 (0.155) | 0.08 | 0.02 (0.655) | 0.01 |
| T1_scalars_noquote | 87 | ordered text | 0.92 | 0.66 | 0.21 (0.005) | 0.13 (0.050) | 0.11 | 0.03 (0.500) | 0.02 |
| T1_bag | 87 | book bag | 0.90 | 0.49 | 0.19 (0.015) | 0.12 (0.120) | 0.09 | 0.05 (0.355) | 0.04 |
| T2_curves20_euc | 87 | ordered text | 0.68 |  | 0.03 (0.330) | 0.01 (0.745) | 0.00 | 0.07 (0.020) | 0.06 |
| T2_curves50_euc | 87 | ordered text | 0.75 |  | 0.03 (0.360) | 0.03 (0.440) | 0.02 | 0.08 (0.015) | 0.07 |
| T2_curves20_dtw | 87 | ordered text | 0.55 |  | 0.05 (0.180) | 0.02 (0.725) | 0.01 | 0.06 (0.145) | 0.05 |
| T2_curves50_dtw | 87 | ordered text | 0.47 |  | 0.07 (0.155) | -0.03 (0.710) | -0.04 | 0.04 (0.395) | 0.03 |
| T2_shape | 87 | ordered text | 0.70 |  | 0.09 (0.120) | 0.10 (0.145) | 0.09 | 0.22 (0.005) | 0.21 |
| T2_shape_nosd | 87 | ordered text | 0.57 |  | 0.08 (0.155) | 0.06 (0.390) | 0.05 | 0.12 (0.035) | 0.11 |
| T2_dialogue20 | 87 | ordered text | 0.36 |  | -0.02 (0.630) | 0.00 (0.940) | 0.00 | 0.03 (0.280) | 0.03 |
| T2_sentence_length20 | 87 | ordered text | 0.34 |  | 0.03 (0.285) | -0.01 (0.840) | -0.02 | 0.04 (0.070) | 0.03 |
| T2_valence20 | 87 | ordered text | 0.35 |  | -0.00 (0.905) | -0.02 (0.520) | -0.03 | 0.03 (0.200) | 0.03 |
| T2_arousal20 | 87 | ordered text | 0.25 |  | 0.06 (0.030) | 0.03 (0.295) | 0.03 | 0.05 (0.020) | 0.05 |
| T2_first_person20 | 87 | ordered text | 0.29 |  | 0.01 (0.605) | 0.01 (0.620) | 0.00 | 0.02 (0.470) | 0.01 |
| T2_new_vocab20 | 87 | ordered text | 0.37 |  | -0.03 (0.635) | -0.04 (0.550) | -0.05 | 0.16 (0.015) | 0.16 |
| T3_scalars_dtw20 | 87 | ordered text | 0.87 |  | 0.17 (0.005) | 0.10 (0.115) | 0.08 | 0.04 (0.450) | 0.02 |
| T3_scalars_dtw20_sd | 87 | ordered text | 0.74 |  | 0.14 (0.005) | 0.07 (0.285) | 0.05 | 0.05 (0.245) | 0.04 |
| T3_scalars_shape | 87 | ordered text | 0.88 |  | 0.17 (0.005) | 0.12 (0.105) | 0.09 | 0.06 (0.195) | 0.05 |
| T3_scalars_dtw20_shape | 87 | ordered text | 0.87 |  | 0.16 (0.005) | 0.10 (0.155) | 0.08 | 0.07 (0.150) | 0.06 |
| T3_noquote_shape | 87 | ordered text | 0.89 |  | 0.20 (0.005) | 0.14 (0.035) | 0.11 | 0.07 (0.155) | 0.06 |
| T3_noquote_shape_sd | 87 | ordered text | 0.87 |  | 0.20 (0.005) | 0.14 (0.055) | 0.11 | 0.08 (0.090) | 0.07 |

Top-5 neighbour make-up (observed / chance) and hubness (skew of the 5-nearest in-degree; share of books in nobody's top 5; largest in-degree and the book).

| block | same author | same genre | mean abs year diff | mean abs log-words diff | hub skew | in no top 5 | max in-degree |
|---|---|---|---|---|---|---|---|
| T1_scalars | 0.20 / 0.02 | 0.25 / 0.12 | 39 / 56 | 0.67 / 0.78 | 0.63 | 0.09 | 15 (hardy_mayor) |
| T1_scalars_noquote | 0.20 / 0.02 | 0.25 / 0.12 | 36 / 56 | 0.63 / 0.78 | 1.03 | 0.11 | 19 (woolf_voyage) |
| T1_bag | 0.21 / 0.02 | 0.23 / 0.12 | 38 / 56 | 0.64 / 0.78 | 0.69 | 0.06 | 13 (twain_yankee) |
| T2_curves20_euc | 0.10 / 0.02 | 0.15 / 0.12 | 47 / 56 | 0.68 / 0.78 | 0.81 | 0.02 | 16 (hammett_falcon) |
| T2_curves50_euc | 0.11 / 0.02 | 0.15 / 0.12 | 47 / 56 | 0.67 / 0.78 | 2.79 | 0.02 | 29 (hammett_falcon) |
| T2_curves20_dtw | 0.11 / 0.02 | 0.14 / 0.12 | 46 / 56 | 0.75 / 0.78 | 0.45 | 0.05 | 13 (fathers_garnett) |
| T2_curves50_dtw | 0.10 / 0.02 | 0.17 / 0.12 | 43 / 56 | 0.71 / 0.78 | 1.22 | 0.05 | 21 (charterhouse_moncrieff) |
| T2_shape | 0.10 / 0.02 | 0.14 / 0.12 | 46 / 56 | 0.57 / 0.78 | 2.77 | 0.14 | 38 (fathers_garnett) |
| T2_shape_nosd | 0.09 / 0.02 | 0.14 / 0.12 | 43 / 56 | 0.68 / 0.78 | 2.57 | 0.15 | 35 (fathers_garnett) |
| T2_dialogue20 | 0.05 / 0.02 | 0.12 / 0.12 | 54 / 56 | 0.78 / 0.78 | 8.12 | 0.00 | 75 (joyce_ulysses) |
| T2_sentence_length20 | 0.07 / 0.02 | 0.13 / 0.12 | 59 / 56 | 0.75 / 0.78 | 1.22 | 0.00 | 14 (dost_cp_garnett) |
| T2_valence20 | 0.07 / 0.02 | 0.14 / 0.12 | 52 / 56 | 0.68 / 0.78 | 0.55 | 0.01 | 13 (james_portrait) |
| T2_arousal20 | 0.07 / 0.02 | 0.12 / 0.12 | 47 / 56 | 0.71 / 0.78 | 1.13 | 0.01 | 13 (oz_land) |
| T2_first_person20 | 0.08 / 0.02 | 0.15 / 0.12 | 50 / 56 | 0.67 / 0.78 | 7.20 | 0.02 | 62 (hammett_falcon) |
| T2_new_vocab20 | 0.07 / 0.02 | 0.16 / 0.12 | 51 / 56 | 0.61 / 0.78 | 1.57 | 0.15 | 24 (dickens_pickwick) |
| T3_scalars_dtw20 | 0.21 / 0.02 | 0.23 / 0.12 | 38 / 56 | 0.65 / 0.78 | 1.19 | 0.11 | 18 (hardy_madding) |
| T3_scalars_dtw20_sd | 0.18 / 0.02 | 0.21 / 0.12 | 38 / 56 | 0.69 / 0.78 | 0.82 | 0.08 | 16 (twain_yankee) |
| T3_scalars_shape | 0.18 / 0.02 | 0.23 / 0.12 | 39 / 56 | 0.65 / 0.78 | 1.15 | 0.15 | 19 (austen_persuasion) |
| T3_scalars_dtw20_shape | 0.16 / 0.02 | 0.24 / 0.12 | 39 / 56 | 0.67 / 0.78 | 1.06 | 0.13 | 16 (hardy_madding) |
| T3_noquote_shape | 0.19 / 0.02 | 0.22 / 0.12 | 40 / 56 | 0.64 / 0.78 | 1.26 | 0.13 | 20 (hardy_madding) |
| T3_noquote_shape_sd | 0.18 / 0.02 | 0.20 / 0.12 | 39 / 56 | 0.65 / 0.78 | 1.10 | 0.16 | 21 (twain_yankee) |

Spearman between the pair distances of two blocks, all pairs.

| block | T1_scalars | T1_scalars_noquote | T1_bag | T2_curves20_euc | T2_curves50_euc | T2_curves20_dtw | T2_curves50_dtw | T2_shape | T2_shape_nosd | T2_dialogue20 | T2_sentence_length20 | T2_valence20 | T2_arousal20 | T2_first_person20 | T2_new_vocab20 | T3_scalars_dtw20 | T3_scalars_dtw20_sd | T3_scalars_shape | T3_scalars_dtw20_shape | T3_noquote_shape | T3_noquote_shape_sd |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| T1_scalars | 1.00 | 0.85 | 0.78 | 0.09 | 0.08 | 0.18 | 0.21 | 0.31 | 0.27 | -0.04 | 0.07 | 0.04 | -0.03 | 0.08 | 0.22 | 0.96 | 0.74 | 0.91 | 0.85 | 0.81 | 0.77 |
| T1_scalars_noquote | 0.85 | 1.00 | 0.92 | 0.08 | 0.06 | 0.15 | 0.16 | 0.21 | 0.18 | -0.02 | 0.07 | 0.02 | -0.01 | 0.08 | 0.13 | 0.82 | 0.63 | 0.76 | 0.70 | 0.88 | 0.82 |
| T1_bag | 0.78 | 0.92 | 1.00 | 0.08 | 0.07 | 0.10 | 0.12 | 0.18 | 0.15 | 0.00 | 0.05 | 0.02 | -0.00 | 0.08 | 0.10 | 0.74 | 0.55 | 0.69 | 0.64 | 0.81 | 0.75 |
| T2_curves20_euc | 0.09 | 0.08 | 0.08 | 1.00 | 0.81 | 0.64 | 0.45 | 0.43 | 0.48 | 0.55 | 0.54 | 0.37 | 0.40 | 0.41 | 0.14 | 0.24 | 0.47 | 0.26 | 0.37 | 0.28 | 0.32 |
| T2_curves50_euc | 0.08 | 0.06 | 0.07 | 0.81 | 1.00 | 0.53 | 0.41 | 0.40 | 0.43 | 0.46 | 0.45 | 0.31 | 0.31 | 0.32 | 0.17 | 0.20 | 0.39 | 0.23 | 0.32 | 0.25 | 0.29 |
| T2_curves20_dtw | 0.18 | 0.15 | 0.10 | 0.64 | 0.53 | 1.00 | 0.76 | 0.59 | 0.64 | 0.33 | 0.41 | 0.19 | 0.24 | 0.29 | 0.14 | 0.42 | 0.77 | 0.41 | 0.57 | 0.41 | 0.47 |
| T2_curves50_dtw | 0.21 | 0.16 | 0.12 | 0.45 | 0.41 | 0.76 | 1.00 | 0.49 | 0.51 | 0.20 | 0.28 | 0.13 | 0.16 | 0.24 | 0.13 | 0.39 | 0.64 | 0.37 | 0.49 | 0.36 | 0.40 |
| T2_shape | 0.31 | 0.21 | 0.18 | 0.43 | 0.40 | 0.59 | 0.49 | 1.00 | 0.94 | 0.19 | 0.30 | 0.13 | 0.13 | 0.18 | 0.33 | 0.43 | 0.58 | 0.63 | 0.68 | 0.58 | 0.67 |
| T2_shape_nosd | 0.27 | 0.18 | 0.15 | 0.48 | 0.43 | 0.64 | 0.51 | 0.94 | 1.00 | 0.24 | 0.31 | 0.15 | 0.16 | 0.18 | 0.32 | 0.40 | 0.59 | 0.61 | 0.68 | 0.59 | 0.68 |
| T2_dialogue20 | -0.04 | -0.02 | 0.00 | 0.55 | 0.46 | 0.33 | 0.20 | 0.19 | 0.24 | 1.00 | 0.22 | -0.01 | 0.07 | 0.01 | 0.04 | 0.06 | 0.20 | 0.08 | 0.14 | 0.10 | 0.13 |
| T2_sentence_length20 | 0.07 | 0.07 | 0.05 | 0.54 | 0.45 | 0.41 | 0.28 | 0.30 | 0.31 | 0.22 | 1.00 | -0.03 | 0.03 | 0.01 | 0.11 | 0.17 | 0.31 | 0.18 | 0.24 | 0.19 | 0.22 |
| T2_valence20 | 0.04 | 0.02 | 0.02 | 0.37 | 0.31 | 0.19 | 0.13 | 0.13 | 0.15 | -0.01 | -0.03 | 1.00 | -0.02 | 0.02 | 0.06 | 0.09 | 0.15 | 0.09 | 0.12 | 0.08 | 0.10 |
| T2_arousal20 | -0.03 | -0.01 | -0.00 | 0.40 | 0.31 | 0.24 | 0.16 | 0.13 | 0.16 | 0.07 | 0.03 | -0.02 | 1.00 | -0.02 | -0.03 | 0.04 | 0.14 | 0.04 | 0.09 | 0.06 | 0.08 |
| T2_first_person20 | 0.08 | 0.08 | 0.08 | 0.41 | 0.32 | 0.29 | 0.24 | 0.18 | 0.18 | 0.01 | 0.01 | 0.02 | -0.02 | 1.00 | 0.01 | 0.14 | 0.23 | 0.14 | 0.18 | 0.14 | 0.16 |
| T2_new_vocab20 | 0.22 | 0.13 | 0.10 | 0.14 | 0.17 | 0.14 | 0.13 | 0.33 | 0.32 | 0.04 | 0.11 | 0.06 | -0.03 | 0.01 | 1.00 | 0.23 | 0.22 | 0.29 | 0.28 | 0.24 | 0.26 |
| T3_scalars_dtw20 | 0.96 | 0.82 | 0.74 | 0.24 | 0.20 | 0.42 | 0.39 | 0.43 | 0.40 | 0.06 | 0.17 | 0.09 | 0.04 | 0.14 | 0.23 | 1.00 | 0.89 | 0.95 | 0.93 | 0.85 | 0.83 |
| T3_scalars_dtw20_sd | 0.74 | 0.63 | 0.55 | 0.47 | 0.39 | 0.77 | 0.64 | 0.58 | 0.59 | 0.20 | 0.31 | 0.15 | 0.14 | 0.23 | 0.22 | 0.89 | 1.00 | 0.85 | 0.93 | 0.78 | 0.80 |
| T3_scalars_shape | 0.91 | 0.76 | 0.69 | 0.26 | 0.23 | 0.41 | 0.37 | 0.63 | 0.61 | 0.08 | 0.18 | 0.09 | 0.04 | 0.14 | 0.29 | 0.95 | 0.85 | 1.00 | 0.98 | 0.90 | 0.91 |
| T3_scalars_dtw20_shape | 0.85 | 0.70 | 0.64 | 0.37 | 0.32 | 0.57 | 0.49 | 0.68 | 0.68 | 0.14 | 0.24 | 0.12 | 0.09 | 0.18 | 0.28 | 0.93 | 0.93 | 0.98 | 1.00 | 0.89 | 0.91 |
| T3_noquote_shape | 0.81 | 0.88 | 0.81 | 0.28 | 0.25 | 0.41 | 0.36 | 0.58 | 0.59 | 0.10 | 0.19 | 0.08 | 0.06 | 0.14 | 0.24 | 0.85 | 0.78 | 0.90 | 0.89 | 1.00 | 0.99 |
| T3_noquote_shape_sd | 0.77 | 0.82 | 0.75 | 0.32 | 0.29 | 0.47 | 0.40 | 0.67 | 0.68 | 0.13 | 0.22 | 0.10 | 0.08 | 0.16 | 0.26 | 0.83 | 0.80 | 0.91 | 0.91 | 0.99 | 1.00 |

Spearman between the pair distances of two blocks, different-author pairs only.

| block | T1_scalars | T1_scalars_noquote | T1_bag | T2_curves20_euc | T2_curves50_euc | T2_curves20_dtw | T2_curves50_dtw | T2_shape | T2_shape_nosd | T2_dialogue20 | T2_sentence_length20 | T2_valence20 | T2_arousal20 | T2_first_person20 | T2_new_vocab20 | T3_scalars_dtw20 | T3_scalars_dtw20_sd | T3_scalars_shape | T3_scalars_dtw20_shape | T3_noquote_shape | T3_noquote_shape_sd |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| T1_scalars | 1.00 | 0.85 | 0.77 | 0.08 | 0.06 | 0.17 | 0.20 | 0.30 | 0.26 | -0.04 | 0.06 | 0.03 | -0.03 | 0.07 | 0.21 | 0.96 | 0.73 | 0.91 | 0.84 | 0.81 | 0.76 |
| T1_scalars_noquote | 0.85 | 1.00 | 0.91 | 0.07 | 0.04 | 0.14 | 0.15 | 0.20 | 0.17 | -0.03 | 0.06 | 0.01 | -0.02 | 0.07 | 0.12 | 0.82 | 0.62 | 0.75 | 0.70 | 0.88 | 0.82 |
| T1_bag | 0.77 | 0.91 | 1.00 | 0.07 | 0.06 | 0.09 | 0.11 | 0.17 | 0.14 | -0.00 | 0.04 | 0.01 | -0.01 | 0.07 | 0.09 | 0.74 | 0.54 | 0.68 | 0.63 | 0.80 | 0.74 |
| T2_curves20_euc | 0.08 | 0.07 | 0.07 | 1.00 | 0.81 | 0.64 | 0.44 | 0.43 | 0.47 | 0.54 | 0.54 | 0.36 | 0.40 | 0.40 | 0.13 | 0.23 | 0.47 | 0.25 | 0.36 | 0.27 | 0.32 |
| T2_curves50_euc | 0.06 | 0.04 | 0.06 | 0.81 | 1.00 | 0.52 | 0.40 | 0.39 | 0.42 | 0.46 | 0.45 | 0.30 | 0.31 | 0.31 | 0.16 | 0.19 | 0.38 | 0.23 | 0.31 | 0.24 | 0.28 |
| T2_curves20_dtw | 0.17 | 0.14 | 0.09 | 0.64 | 0.52 | 1.00 | 0.76 | 0.58 | 0.64 | 0.33 | 0.40 | 0.18 | 0.24 | 0.28 | 0.14 | 0.41 | 0.77 | 0.40 | 0.56 | 0.41 | 0.46 |
| T2_curves50_dtw | 0.20 | 0.15 | 0.11 | 0.44 | 0.40 | 0.76 | 1.00 | 0.48 | 0.50 | 0.20 | 0.28 | 0.12 | 0.15 | 0.23 | 0.12 | 0.38 | 0.64 | 0.37 | 0.49 | 0.35 | 0.39 |
| T2_shape | 0.30 | 0.20 | 0.17 | 0.43 | 0.39 | 0.58 | 0.48 | 1.00 | 0.94 | 0.18 | 0.29 | 0.13 | 0.12 | 0.18 | 0.33 | 0.42 | 0.57 | 0.62 | 0.68 | 0.58 | 0.66 |
| T2_shape_nosd | 0.26 | 0.17 | 0.14 | 0.47 | 0.42 | 0.64 | 0.50 | 0.94 | 1.00 | 0.24 | 0.30 | 0.14 | 0.15 | 0.18 | 0.32 | 0.40 | 0.59 | 0.61 | 0.68 | 0.58 | 0.68 |
| T2_dialogue20 | -0.04 | -0.03 | -0.00 | 0.54 | 0.46 | 0.33 | 0.20 | 0.18 | 0.24 | 1.00 | 0.22 | -0.02 | 0.07 | 0.01 | 0.04 | 0.05 | 0.20 | 0.07 | 0.14 | 0.10 | 0.13 |
| T2_sentence_length20 | 0.06 | 0.06 | 0.04 | 0.54 | 0.45 | 0.40 | 0.28 | 0.29 | 0.30 | 0.22 | 1.00 | -0.04 | 0.02 | 0.00 | 0.11 | 0.16 | 0.31 | 0.17 | 0.24 | 0.18 | 0.21 |
| T2_valence20 | 0.03 | 0.01 | 0.01 | 0.36 | 0.30 | 0.18 | 0.12 | 0.13 | 0.14 | -0.02 | -0.04 | 1.00 | -0.02 | 0.02 | 0.05 | 0.08 | 0.15 | 0.08 | 0.11 | 0.07 | 0.09 |
| T2_arousal20 | -0.03 | -0.02 | -0.01 | 0.40 | 0.31 | 0.24 | 0.15 | 0.12 | 0.15 | 0.07 | 0.02 | -0.02 | 1.00 | -0.03 | -0.03 | 0.03 | 0.14 | 0.04 | 0.08 | 0.05 | 0.07 |
| T2_first_person20 | 0.07 | 0.07 | 0.07 | 0.40 | 0.31 | 0.28 | 0.23 | 0.18 | 0.18 | 0.01 | 0.00 | 0.02 | -0.03 | 1.00 | -0.00 | 0.14 | 0.23 | 0.13 | 0.17 | 0.13 | 0.15 |
| T2_new_vocab20 | 0.21 | 0.12 | 0.09 | 0.13 | 0.16 | 0.14 | 0.12 | 0.33 | 0.32 | 0.04 | 0.11 | 0.05 | -0.03 | -0.00 | 1.00 | 0.22 | 0.21 | 0.28 | 0.28 | 0.24 | 0.26 |
| T3_scalars_dtw20 | 0.96 | 0.82 | 0.74 | 0.23 | 0.19 | 0.41 | 0.38 | 0.42 | 0.40 | 0.05 | 0.16 | 0.08 | 0.03 | 0.14 | 0.22 | 1.00 | 0.89 | 0.94 | 0.93 | 0.85 | 0.83 |
| T3_scalars_dtw20_sd | 0.73 | 0.62 | 0.54 | 0.47 | 0.38 | 0.77 | 0.64 | 0.57 | 0.59 | 0.20 | 0.31 | 0.15 | 0.14 | 0.23 | 0.21 | 0.89 | 1.00 | 0.84 | 0.92 | 0.78 | 0.79 |
| T3_scalars_shape | 0.91 | 0.75 | 0.68 | 0.25 | 0.23 | 0.40 | 0.37 | 0.62 | 0.61 | 0.07 | 0.17 | 0.08 | 0.04 | 0.13 | 0.28 | 0.94 | 0.84 | 1.00 | 0.98 | 0.90 | 0.91 |
| T3_scalars_dtw20_shape | 0.84 | 0.70 | 0.63 | 0.36 | 0.31 | 0.56 | 0.49 | 0.68 | 0.68 | 0.14 | 0.24 | 0.11 | 0.08 | 0.17 | 0.28 | 0.93 | 0.92 | 0.98 | 1.00 | 0.89 | 0.91 |
| T3_noquote_shape | 0.81 | 0.88 | 0.80 | 0.27 | 0.24 | 0.41 | 0.35 | 0.58 | 0.58 | 0.10 | 0.18 | 0.07 | 0.05 | 0.13 | 0.24 | 0.85 | 0.78 | 0.90 | 0.89 | 1.00 | 0.99 |
| T3_noquote_shape_sd | 0.76 | 0.82 | 0.74 | 0.32 | 0.28 | 0.46 | 0.39 | 0.66 | 0.68 | 0.13 | 0.21 | 0.09 | 0.07 | 0.15 | 0.26 | 0.83 | 0.79 | 0.91 | 0.91 | 0.99 | 1.00 |


## Telling candidates (without joyce_ulysses, wells_time, wyss_swiss)

AUC that a labelled pair is closer than a negative pair (3413 negatives; [95% bootstrap interval over the labelled pairs]). n = labelled pairs.

| block | translation_pair (n=10) | edition_pair (n=1) | same_author_unrelated (n=50) | same_author_orig_en (n=31) | same_author_same_translator (n=5) | same_author_diff_translator (n=14) | series (n=7) | retelling (n=5) | same_translator_diff_author (n=11) | same_genre (n=231) |
|---|---|---|---|---|---|---|---|---|---|---|
| T1_scalars | 0.98 [0.95, 1.00] | 1.00 | 0.77 [0.69, 0.84] | 0.81 [0.72, 0.88] | 0.63 [0.26, 0.96] | 0.73 [0.56, 0.88] | 0.85 [0.71, 0.97] | 0.60 [0.31, 0.88] | 0.59 [0.38, 0.77] | 0.59 [0.55, 0.62] |
| T1_scalars_noquote | 0.99 [0.98, 1.00] | 1.00 | 0.82 [0.77, 0.87] | 0.84 [0.79, 0.89] | 0.82 [0.68, 0.94] | 0.77 [0.66, 0.87] | 0.89 [0.79, 0.96] | 0.56 [0.23, 0.89] | 0.63 [0.48, 0.78] | 0.58 [0.54, 0.61] |
| T1_bag | 0.99 [0.99, 1.00] | 1.00 | 0.78 [0.73, 0.84] | 0.81 [0.74, 0.88] | 0.79 [0.63, 0.92] | 0.72 [0.59, 0.85] | 0.87 [0.77, 0.96] | 0.58 [0.25, 0.92] | 0.62 [0.47, 0.76] | 0.57 [0.54, 0.61] |
| T2_curves20_euc | 0.95 [0.88, 1.00] | 1.00 | 0.54 [0.45, 0.63] | 0.63 [0.51, 0.74] | 0.44 [0.17, 0.71] | 0.39 [0.28, 0.51] | 0.63 [0.37, 0.89] | 0.51 [0.30, 0.72] | 0.50 [0.31, 0.70] | 0.49 [0.45, 0.53] |
| T2_curves50_euc | 0.94 [0.85, 1.00] | 1.00 | 0.59 [0.50, 0.67] | 0.67 [0.55, 0.77] | 0.63 [0.31, 0.86] | 0.38 [0.26, 0.51] | 0.63 [0.34, 0.90] | 0.34 [0.25, 0.43] | 0.56 [0.40, 0.72] | 0.48 [0.45, 0.52] |
| T2_curves20_dtw | 0.97 [0.92, 1.00] | 1.00 | 0.58 [0.50, 0.66] | 0.62 [0.51, 0.73] | 0.61 [0.33, 0.84] | 0.50 [0.37, 0.64] | 0.55 [0.31, 0.74] | 0.64 [0.43, 0.77] | 0.63 [0.46, 0.77] | 0.49 [0.45, 0.53] |
| T2_curves50_dtw | 0.94 [0.86, 1.00] | 1.00 | 0.61 [0.52, 0.69] | 0.61 [0.50, 0.72] | 0.55 [0.33, 0.76] | 0.62 [0.47, 0.76] | 0.48 [0.23, 0.73] | 0.60 [0.37, 0.77] | 0.73 [0.59, 0.86] | 0.48 [0.45, 0.52] |
| T2_shape | 1.00 [1.00, 1.00] | 1.00 | 0.61 [0.54, 0.67] | 0.67 [0.59, 0.75] | 0.41 [0.17, 0.66] | 0.53 [0.41, 0.65] | 0.59 [0.32, 0.83] | 0.60 [0.40, 0.79] | 0.51 [0.34, 0.69] | 0.51 [0.48, 0.55] |
| T2_shape_nosd | 1.00 [0.99, 1.00] | 1.00 | 0.56 [0.49, 0.64] | 0.63 [0.53, 0.71] | 0.36 [0.16, 0.59] | 0.50 [0.38, 0.60] | 0.57 [0.29, 0.82] | 0.64 [0.42, 0.79] | 0.58 [0.39, 0.75] | 0.50 [0.46, 0.53] |
| T2_dialogue20 | 0.88 [0.73, 0.98] | 1.00 | 0.45 [0.38, 0.53] | 0.48 [0.37, 0.58] | 0.38 [0.16, 0.63] | 0.42 [0.31, 0.51] | 0.64 [0.40, 0.85] | 0.46 [0.17, 0.75] | 0.55 [0.39, 0.70] | 0.48 [0.44, 0.52] |
| T2_sentence_length20 | 0.84 [0.69, 0.96] | 0.99 | 0.55 [0.48, 0.63] | 0.58 [0.50, 0.67] | 0.46 [0.35, 0.55] | 0.52 [0.37, 0.67] | 0.61 [0.36, 0.86] | 0.46 [0.22, 0.69] | 0.56 [0.41, 0.70] | 0.50 [0.46, 0.54] |
| T2_valence20 | 0.86 [0.74, 0.98] | 1.00 | 0.51 [0.43, 0.59] | 0.56 [0.44, 0.67] | 0.52 [0.20, 0.81] | 0.41 [0.30, 0.52] | 0.40 [0.25, 0.58] | 0.57 [0.45, 0.68] | 0.60 [0.43, 0.76] | 0.50 [0.47, 0.55] |
| T2_arousal20 | 0.90 [0.76, 1.00] | 1.00 | 0.49 [0.41, 0.56] | 0.51 [0.41, 0.60] | 0.38 [0.18, 0.58] | 0.48 [0.33, 0.63] | 0.59 [0.49, 0.68] | 0.53 [0.33, 0.73] | 0.42 [0.25, 0.59] | 0.49 [0.45, 0.52] |
| T2_first_person20 | 0.76 [0.60, 0.90] | 0.92 | 0.58 [0.50, 0.66] | 0.65 [0.55, 0.74] | 0.64 [0.51, 0.78] | 0.41 [0.27, 0.55] | 0.53 [0.32, 0.73] | 0.56 [0.33, 0.79] | 0.53 [0.40, 0.66] | 0.50 [0.47, 0.54] |
| T2_new_vocab20 | 0.91 [0.77, 0.99] | 1.00 | 0.56 [0.48, 0.64] | 0.60 [0.51, 0.68] | 0.44 [0.08, 0.81] | 0.52 [0.35, 0.68] | 0.44 [0.22, 0.68] | 0.71 [0.56, 0.85] | 0.42 [0.22, 0.63] | 0.52 [0.49, 0.56] |
| T3_scalars_dtw20 | 0.99 [0.96, 1.00] | 1.00 | 0.77 [0.69, 0.83] | 0.80 [0.71, 0.88] | 0.62 [0.28, 0.95] | 0.74 [0.60, 0.87] | 0.85 [0.70, 0.97] | 0.62 [0.35, 0.87] | 0.60 [0.39, 0.79] | 0.58 [0.55, 0.61] |
| T3_scalars_dtw20_sd | 0.99 [0.97, 1.00] | 1.00 | 0.72 [0.63, 0.79] | 0.74 [0.64, 0.84] | 0.59 [0.32, 0.87] | 0.70 [0.55, 0.83] | 0.76 [0.59, 0.91] | 0.66 [0.48, 0.87] | 0.61 [0.43, 0.79] | 0.55 [0.51, 0.58] |
| T3_scalars_shape | 1.00 [0.99, 1.00] | 1.00 | 0.75 [0.68, 0.82] | 0.80 [0.72, 0.87] | 0.58 [0.24, 0.93] | 0.71 [0.56, 0.84] | 0.78 [0.54, 0.96] | 0.61 [0.36, 0.86] | 0.58 [0.38, 0.79] | 0.58 [0.54, 0.61] |
| T3_scalars_dtw20_shape | 1.00 [0.99, 1.00] | 1.00 | 0.74 [0.67, 0.81] | 0.78 [0.70, 0.86] | 0.57 [0.23, 0.91] | 0.71 [0.57, 0.83] | 0.76 [0.53, 0.94] | 0.64 [0.45, 0.85] | 0.59 [0.39, 0.78] | 0.57 [0.53, 0.60] |
| T3_noquote_shape | 1.00 [1.00, 1.00] | 1.00 | 0.80 [0.75, 0.84] | 0.83 [0.78, 0.89] | 0.72 [0.51, 0.87] | 0.75 [0.67, 0.84] | 0.81 [0.60, 0.96] | 0.58 [0.29, 0.87] | 0.62 [0.45, 0.79] | 0.57 [0.54, 0.61] |
| T3_noquote_shape_sd | 1.00 [1.00, 1.00] | 1.00 | 0.78 [0.73, 0.83] | 0.82 [0.77, 0.88] | 0.68 [0.46, 0.85] | 0.73 [0.65, 0.82] | 0.78 [0.56, 0.94] | 0.58 [0.31, 0.86] | 0.61 [0.44, 0.78] | 0.57 [0.53, 0.60] |

AUC difference from `T1_scalars` on the same pairs [paired bootstrap 95%].

| block | translation_pair (n=10) | edition_pair (n=1) | same_author_unrelated (n=50) | same_author_orig_en (n=31) | same_author_same_translator (n=5) | same_author_diff_translator (n=14) | series (n=7) | retelling (n=5) | same_translator_diff_author (n=11) | same_genre (n=231) |
|---|---|---|---|---|---|---|---|---|---|---|
| T1_scalars_noquote | +0.01 [+0.00, +0.04] |  | +0.05 [+0.01, +0.11] | +0.04 [+0.00, +0.08] | +0.20 [-0.11, +0.55] | +0.04 [-0.06, +0.16] | +0.04 [-0.04, +0.11] | -0.04 [-0.11, +0.04] | +0.05 [-0.11, +0.21] | -0.01 [-0.03, +0.01] |
| T1_bag | +0.02 [-0.00, +0.05] |  | +0.02 [-0.03, +0.07] | +0.00 [-0.03, +0.04] | +0.16 [-0.12, +0.46] | -0.01 [-0.09, +0.11] | +0.01 [-0.08, +0.10] | -0.01 [-0.08, +0.07] | +0.03 [-0.08, +0.16] | -0.01 [-0.03, +0.01] |
| T2_curves20_euc | -0.03 [-0.11, +0.03] |  | -0.22 [-0.33, -0.11] | -0.18 [-0.30, -0.07] | -0.19 [-0.67, +0.38] | -0.34 [-0.54, -0.13] | -0.22 [-0.54, +0.05] | -0.09 [-0.28, +0.09] | -0.08 [-0.32, +0.15] | -0.10 [-0.15, -0.05] |
| T2_curves50_euc | -0.04 [-0.13, +0.03] |  | -0.18 [-0.28, -0.07] | -0.13 [-0.26, -0.02] | +0.00 [-0.48, +0.52] | -0.34 [-0.52, -0.16] | -0.23 [-0.52, +0.04] | -0.26 [-0.56, +0.00] | -0.03 [-0.22, +0.17] | -0.11 [-0.16, -0.06] |
| T2_curves20_dtw | -0.01 [-0.03, +0.01] |  | -0.18 [-0.28, -0.07] | -0.19 [-0.30, -0.08] | -0.02 [-0.46, +0.40] | -0.23 [-0.46, +0.01] | -0.31 [-0.55, -0.08] | +0.04 [-0.34, +0.41] | +0.04 [-0.17, +0.28] | -0.10 [-0.15, -0.05] |
| T2_curves50_dtw | -0.04 [-0.12, +0.00] |  | -0.16 [-0.27, -0.05] | -0.19 [-0.31, -0.07] | -0.08 [-0.44, +0.26] | -0.11 [-0.33, +0.11] | -0.37 [-0.70, -0.08] | -0.00 [-0.39, +0.41] | +0.15 [-0.05, +0.36] | -0.11 [-0.15, -0.06] |
| T2_shape | +0.02 [+0.00, +0.05] |  | -0.16 [-0.24, -0.08] | -0.13 [-0.22, -0.03] | -0.22 [-0.42, -0.03] | -0.20 [-0.37, -0.03] | -0.27 [-0.51, -0.07] | +0.00 [-0.40, +0.40] | -0.07 [-0.21, +0.06] | -0.07 [-0.12, -0.03] |
| T2_shape_nosd | +0.02 [+0.00, +0.05] |  | -0.20 [-0.29, -0.12] | -0.18 [-0.28, -0.08] | -0.27 [-0.50, -0.03] | -0.23 [-0.41, -0.05] | -0.28 [-0.55, -0.07] | +0.04 [-0.33, +0.39] | -0.01 [-0.17, +0.16] | -0.09 [-0.14, -0.05] |
| T2_dialogue20 | -0.10 [-0.26, +0.00] |  | -0.32 [-0.43, -0.20] | -0.33 [-0.46, -0.20] | -0.24 [-0.77, +0.31] | -0.31 [-0.54, -0.07] | -0.22 [-0.53, +0.06] | -0.14 [-0.23, -0.02] | -0.04 [-0.30, +0.21] | -0.10 [-0.15, -0.06] |
| T2_sentence_length20 | -0.14 [-0.26, -0.03] |  | -0.21 [-0.32, -0.11] | -0.22 [-0.33, -0.10] | -0.16 [-0.53, +0.22] | -0.21 [-0.44, +0.03] | -0.24 [-0.53, +0.05] | -0.14 [-0.33, +0.06] | -0.03 [-0.25, +0.21] | -0.09 [-0.14, -0.04] |
| T2_valence20 | -0.11 [-0.23, -0.02] |  | -0.25 [-0.35, -0.16] | -0.25 [-0.38, -0.12] | -0.11 [-0.52, +0.38] | -0.32 [-0.47, -0.17] | -0.45 [-0.65, -0.26] | -0.03 [-0.36, +0.28] | +0.01 [-0.14, +0.18] | -0.08 [-0.14, -0.03] |
| T2_arousal20 | -0.08 [-0.21, +0.04] |  | -0.28 [-0.38, -0.17] | -0.30 [-0.41, -0.18] | -0.25 [-0.70, +0.21] | -0.25 [-0.49, -0.02] | -0.26 [-0.44, -0.10] | -0.06 [-0.46, +0.33] | -0.17 [-0.40, +0.03] | -0.10 [-0.15, -0.05] |
| T2_first_person20 | -0.21 [-0.36, -0.08] |  | -0.19 [-0.29, -0.09] | -0.16 [-0.27, -0.06] | +0.01 [-0.42, +0.45] | -0.32 [-0.47, -0.14] | -0.32 [-0.50, -0.11] | -0.03 [-0.49, +0.42] | -0.06 [-0.28, +0.19] | -0.08 [-0.14, -0.03] |
| T2_new_vocab20 | -0.06 [-0.21, +0.03] |  | -0.21 [-0.29, -0.12] | -0.21 [-0.32, -0.09] | -0.18 [-0.51, +0.01] | -0.21 [-0.33, -0.11] | -0.41 [-0.56, -0.25] | +0.11 [-0.26, +0.49] | -0.17 [-0.37, +0.01] | -0.06 [-0.11, -0.02] |
| T3_scalars_dtw20 | +0.01 [+0.00, +0.02] |  | -0.00 [-0.02, +0.02] | -0.01 [-0.03, +0.02] | -0.00 [-0.06, +0.05] | +0.01 [-0.03, +0.06] | -0.01 [-0.05, +0.03] | +0.02 [-0.03, +0.06] | +0.01 [-0.03, +0.06] | -0.01 [-0.02, +0.00] |
| T3_scalars_dtw20_sd | +0.01 [-0.00, +0.02] |  | -0.05 [-0.11, +0.01] | -0.06 [-0.13, +0.00] | -0.03 [-0.28, +0.16] | -0.03 [-0.18, +0.10] | -0.09 [-0.23, +0.04] | +0.06 [-0.12, +0.22] | +0.03 [-0.10, +0.15] | -0.04 [-0.07, -0.01] |
| T3_scalars_shape | +0.02 [+0.00, +0.05] |  | -0.01 [-0.04, +0.01] | -0.01 [-0.04, +0.02] | -0.04 [-0.08, -0.01] | -0.02 [-0.06, +0.02] | -0.07 [-0.20, +0.02] | +0.02 [-0.08, +0.10] | -0.00 [-0.07, +0.04] | -0.01 [-0.03, +0.00] |
| T3_scalars_dtw20_shape | +0.02 [+0.00, +0.05] |  | -0.02 [-0.06, +0.01] | -0.02 [-0.07, +0.03] | -0.05 [-0.15, +0.00] | -0.02 [-0.10, +0.05] | -0.09 [-0.24, +0.03] | +0.04 [-0.05, +0.15] | +0.00 [-0.08, +0.07] | -0.02 [-0.05, +0.00] |
| T3_noquote_shape | +0.02 [+0.00, +0.05] |  | +0.03 [-0.01, +0.09] | +0.03 [-0.02, +0.08] | +0.09 [-0.13, +0.36] | +0.02 [-0.08, +0.14] | -0.05 [-0.17, +0.07] | -0.02 [-0.18, +0.09] | +0.03 [-0.11, +0.20] | -0.01 [-0.04, +0.01] |
| T3_noquote_shape_sd | +0.02 [+0.00, +0.05] |  | +0.02 [-0.03, +0.07] | +0.02 [-0.03, +0.08] | +0.05 [-0.15, +0.30] | +0.00 [-0.10, +0.11] | -0.08 [-0.22, +0.05] | -0.01 [-0.19, +0.10] | +0.02 [-0.12, +0.20] | -0.02 [-0.05, +0.00] |

Mean percentile rank of the partner (0 = nearest book) / recall@1 / recall@5.

| block | translation_pair (n=10) | edition_pair (n=1) | same_author_unrelated (n=50) | same_author_orig_en (n=31) | same_author_same_translator (n=5) | same_author_diff_translator (n=14) | series (n=7) | retelling (n=5) | same_translator_diff_author (n=11) | same_genre (n=231) |
|---|---|---|---|---|---|---|---|---|---|---|
| T1_scalars | 0.01 / 0.88 / 1.00 | 0.00 / 1.00 / 1.00 | 0.23 / 0.26 / 0.49 | 0.21 / 0.23 / 0.52 | 0.31 / 0.00 / 0.43 | 0.24 / 0.31 / 0.44 | 0.10 / 0.43 / 0.71 | 0.35 / 0.22 / 0.22 | 0.38 / 0.00 / 0.50 | 0.41 / 0.26 / 0.56 |
| T1_scalars_noquote | 0.00 / 1.00 / 1.00 | 0.00 / 1.00 / 1.00 | 0.17 / 0.32 / 0.49 | 0.17 / 0.32 / 0.48 | 0.12 / 0.00 / 0.43 | 0.18 / 0.31 / 0.44 | 0.09 / 0.43 / 0.64 | 0.37 / 0.22 / 0.22 | 0.34 / 0.00 / 0.83 | 0.44 / 0.12 / 0.46 |
| T1_bag | 0.00 / 0.94 / 1.00 | 0.00 / 1.00 / 1.00 | 0.20 / 0.17 / 0.49 | 0.20 / 0.16 / 0.48 | 0.17 / 0.00 / 0.43 | 0.21 / 0.19 / 0.44 | 0.10 / 0.43 / 0.64 | 0.32 / 0.22 / 0.33 | 0.38 / 0.00 / 0.50 | 0.43 / 0.12 / 0.42 |
| T2_curves20_euc | 0.05 / 0.71 / 0.76 | 0.00 / 1.00 / 1.00 | 0.46 / 0.09 / 0.19 | 0.38 / 0.10 / 0.26 | 0.59 / 0.14 / 0.14 | 0.58 / 0.00 / 0.00 | 0.36 / 0.07 / 0.21 | 0.45 / 0.00 / 0.00 | 0.50 / 0.00 / 0.50 | 0.51 / 0.02 / 0.46 |
| T2_curves50_euc | 0.06 / 0.76 / 0.76 | 0.00 / 1.00 / 1.00 | 0.42 / 0.09 / 0.23 | 0.35 / 0.10 / 0.32 | 0.40 / 0.14 / 0.14 | 0.60 / 0.00 / 0.00 | 0.35 / 0.14 / 0.29 | 0.64 / 0.00 / 0.00 | 0.45 / 0.00 / 0.50 | 0.52 / 0.08 / 0.42 |
| T2_curves20_dtw | 0.03 / 0.88 / 0.94 | 0.00 / 1.00 / 1.00 | 0.41 / 0.04 / 0.32 | 0.36 / 0.06 / 0.39 | 0.40 / 0.00 / 0.00 | 0.51 / 0.00 / 0.19 | 0.43 / 0.00 / 0.00 | 0.29 / 0.00 / 0.11 | 0.42 / 0.17 / 0.17 | 0.49 / 0.06 / 0.54 |
| T2_curves50_dtw | 0.04 / 0.82 / 0.94 | 0.00 / 1.00 / 1.00 | 0.39 / 0.04 / 0.26 | 0.37 / 0.06 / 0.39 | 0.47 / 0.00 / 0.00 | 0.42 / 0.00 / 0.00 | 0.48 / 0.00 / 0.00 | 0.35 / 0.00 / 0.22 | 0.33 / 0.17 / 0.83 | 0.50 / 0.14 / 0.50 |
| T2_shape | 0.00 / 1.00 / 1.00 | 0.00 / 1.00 / 1.00 | 0.42 / 0.02 / 0.17 | 0.35 / 0.03 / 0.26 | 0.57 / 0.00 / 0.00 | 0.52 / 0.00 / 0.00 | 0.39 / 0.07 / 0.14 | 0.39 / 0.00 / 0.00 | 0.50 / 0.17 / 0.33 | 0.48 / 0.18 / 0.54 |
| T2_shape_nosd | 0.00 / 0.94 / 1.00 | 0.00 / 1.00 / 1.00 | 0.46 / 0.02 / 0.17 | 0.39 / 0.03 / 0.26 | 0.63 / 0.00 / 0.00 | 0.56 / 0.00 / 0.00 | 0.43 / 0.00 / 0.07 | 0.35 / 0.00 / 0.00 | 0.46 / 0.33 / 0.33 | 0.50 / 0.18 / 0.50 |
| T2_dialogue20 | 0.14 / 0.59 / 0.59 | 0.00 / 1.00 / 1.00 | 0.56 / 0.00 / 0.04 | 0.54 / 0.00 / 0.06 | 0.63 / 0.00 / 0.00 | 0.57 / 0.00 / 0.00 | 0.35 / 0.07 / 0.29 | 0.51 / 0.00 / 0.00 | 0.41 / 0.00 / 0.00 | 0.52 / 0.12 / 0.46 |
| T2_sentence_length20 | 0.15 / 0.53 / 0.71 | 0.00 / 1.00 / 1.00 | 0.46 / 0.02 / 0.13 | 0.43 / 0.03 / 0.19 | 0.54 / 0.00 / 0.00 | 0.49 / 0.00 / 0.00 | 0.35 / 0.14 / 0.29 | 0.53 / 0.00 / 0.11 | 0.46 / 0.00 / 0.00 | 0.51 / 0.06 / 0.38 |
| T2_valence20 | 0.12 / 0.71 / 0.71 | 0.01 / 0.50 / 1.00 | 0.50 / 0.00 / 0.15 | 0.46 / 0.00 / 0.16 | 0.50 / 0.00 / 0.29 | 0.59 / 0.00 / 0.00 | 0.50 / 0.00 / 0.07 | 0.40 / 0.00 / 0.00 | 0.39 / 0.00 / 0.33 | 0.49 / 0.10 / 0.50 |
| T2_arousal20 | 0.11 / 0.76 / 0.76 | 0.00 / 1.00 / 1.00 | 0.51 / 0.09 / 0.09 | 0.49 / 0.13 / 0.13 | 0.64 / 0.00 / 0.00 | 0.52 / 0.00 / 0.00 | 0.44 / 0.00 / 0.00 | 0.45 / 0.00 / 0.00 | 0.61 / 0.00 / 0.00 | 0.52 / 0.08 / 0.46 |
| T2_first_person20 | 0.21 / 0.29 / 0.47 | 0.02 / 0.00 / 1.00 | 0.41 / 0.04 / 0.19 | 0.35 / 0.06 / 0.26 | 0.38 / 0.00 / 0.14 | 0.56 / 0.00 / 0.00 | 0.45 / 0.00 / 0.14 | 0.45 / 0.00 / 0.00 | 0.49 / 0.00 / 0.00 | 0.49 / 0.04 / 0.40 |
| T2_new_vocab20 | 0.08 / 0.71 / 0.71 | 0.00 / 1.00 / 1.00 | 0.45 / 0.04 / 0.17 | 0.43 / 0.03 / 0.13 | 0.53 / 0.00 / 0.29 | 0.46 / 0.06 / 0.12 | 0.52 / 0.00 / 0.07 | 0.30 / 0.00 / 0.00 | 0.55 / 0.00 / 0.00 | 0.49 / 0.20 / 0.52 |
| T3_scalars_dtw20 | 0.00 / 1.00 / 1.00 | 0.00 / 1.00 / 1.00 | 0.23 / 0.32 / 0.57 | 0.21 / 0.42 / 0.58 | 0.33 / 0.00 / 0.57 | 0.24 / 0.12 / 0.44 | 0.10 / 0.36 / 0.71 | 0.33 / 0.22 / 0.22 | 0.38 / 0.17 / 0.83 | 0.41 / 0.16 / 0.46 |
| T3_scalars_dtw20_sd | 0.01 / 0.94 / 1.00 | 0.00 / 1.00 / 1.00 | 0.29 / 0.15 / 0.53 | 0.27 / 0.23 / 0.65 | 0.38 / 0.00 / 0.29 | 0.32 / 0.00 / 0.25 | 0.18 / 0.14 / 0.29 | 0.28 / 0.00 / 0.33 | 0.40 / 0.17 / 0.67 | 0.44 / 0.16 / 0.54 |
| T3_scalars_shape | 0.00 / 1.00 / 1.00 | 0.00 / 1.00 / 1.00 | 0.25 / 0.19 / 0.45 | 0.22 / 0.23 / 0.45 | 0.37 / 0.00 / 0.43 | 0.28 / 0.12 / 0.38 | 0.16 / 0.43 / 0.50 | 0.34 / 0.11 / 0.22 | 0.39 / 0.17 / 0.83 | 0.42 / 0.10 / 0.54 |
| T3_scalars_dtw20_shape | 0.00 / 1.00 / 1.00 | 0.00 / 1.00 / 1.00 | 0.27 / 0.21 / 0.43 | 0.23 / 0.26 / 0.48 | 0.39 / 0.00 / 0.29 | 0.29 / 0.12 / 0.25 | 0.18 / 0.29 / 0.43 | 0.31 / 0.11 / 0.22 | 0.40 / 0.33 / 0.83 | 0.42 / 0.12 / 0.58 |
| T3_noquote_shape | 0.00 / 1.00 / 1.00 | 0.00 / 1.00 / 1.00 | 0.20 / 0.19 / 0.51 | 0.19 / 0.23 / 0.55 | 0.20 / 0.00 / 0.29 | 0.21 / 0.12 / 0.44 | 0.15 / 0.36 / 0.43 | 0.36 / 0.22 / 0.22 | 0.37 / 0.17 / 0.83 | 0.44 / 0.12 / 0.42 |
| T3_noquote_shape_sd | 0.00 / 1.00 / 1.00 | 0.00 / 1.00 / 1.00 | 0.22 / 0.19 / 0.45 | 0.21 / 0.23 / 0.48 | 0.26 / 0.00 / 0.29 | 0.24 / 0.12 / 0.38 | 0.18 / 0.36 / 0.43 | 0.36 / 0.11 / 0.22 | 0.38 / 0.17 / 1.00 | 0.44 / 0.08 / 0.42 |

Split-half self-retrieval (accuracy; chance is 1/n), and Spearman of distance with |year difference| and |log word-count difference| (Mantel p in brackets; en = both books written in English; diff = different authors only).

| block | n | input | split a/b | split h1/h2 | rho year | rho year en | rho year en diff | rho logwords | rho logwords diff |
|---|---|---|---|---|---|---|---|---|---|
| T1_scalars | 84 | ordered text | 0.90 | 0.70 | 0.17 (0.005) | 0.13 (0.070) | 0.11 | 0.00 (0.985) | -0.01 |
| T1_scalars_noquote | 84 | ordered text | 0.92 | 0.66 | 0.21 (0.005) | 0.16 (0.035) | 0.13 | 0.01 (0.780) | 0.00 |
| T1_bag | 84 | book bag | 0.90 | 0.49 | 0.18 (0.005) | 0.14 (0.030) | 0.12 | 0.03 (0.440) | 0.02 |
| T2_curves20_euc | 84 | ordered text | 0.68 |  | 0.02 (0.505) | 0.01 (0.760) | 0.00 | 0.07 (0.025) | 0.07 |
| T2_curves50_euc | 84 | ordered text | 0.74 |  | 0.02 (0.485) | 0.03 (0.470) | 0.02 | 0.09 (0.005) | 0.08 |
| T2_curves20_dtw | 84 | ordered text | 0.54 |  | 0.05 (0.210) | 0.03 (0.580) | 0.02 | 0.04 (0.355) | 0.03 |
| T2_curves50_dtw | 84 | ordered text | 0.46 |  | 0.07 (0.130) | -0.00 (0.960) | -0.01 | 0.01 (0.870) | -0.00 |
| T2_shape | 84 | ordered text | 0.69 |  | 0.09 (0.130) | 0.13 (0.100) | 0.11 | 0.20 (0.005) | 0.19 |
| T2_shape_nosd | 84 | ordered text | 0.57 |  | 0.08 (0.190) | 0.08 (0.260) | 0.07 | 0.09 (0.080) | 0.09 |
| T2_dialogue20 | 84 | ordered text | 0.36 |  | -0.02 (0.385) | -0.00 (0.960) | -0.00 | 0.05 (0.105) | 0.05 |
| T2_sentence_length20 | 84 | ordered text | 0.34 |  | 0.03 (0.425) | 0.00 (0.935) | -0.01 | 0.03 (0.220) | 0.03 |
| T2_valence20 | 84 | ordered text | 0.35 |  | -0.01 (0.880) | -0.03 (0.395) | -0.04 | 0.03 (0.335) | 0.03 |
| T2_arousal20 | 84 | ordered text | 0.24 |  | 0.05 (0.055) | 0.02 (0.490) | 0.02 | 0.06 (0.010) | 0.06 |
| T2_first_person20 | 84 | ordered text | 0.28 |  | 0.01 (0.650) | 0.02 (0.615) | 0.01 | 0.01 (0.550) | 0.01 |
| T2_new_vocab20 | 84 | ordered text | 0.36 |  | -0.05 (0.465) | -0.03 (0.660) | -0.04 | 0.14 (0.010) | 0.14 |
| T3_scalars_dtw20 | 84 | ordered text | 0.86 |  | 0.17 (0.005) | 0.13 (0.050) | 0.11 | 0.01 (0.815) | -0.00 |
| T3_scalars_dtw20_sd | 84 | ordered text | 0.74 |  | 0.14 (0.005) | 0.10 (0.070) | 0.08 | 0.03 (0.580) | 0.01 |
| T3_scalars_shape | 84 | ordered text | 0.88 |  | 0.17 (0.005) | 0.15 (0.025) | 0.12 | 0.04 (0.430) | 0.03 |
| T3_scalars_dtw20_shape | 84 | ordered text | 0.88 |  | 0.16 (0.005) | 0.13 (0.075) | 0.11 | 0.05 (0.310) | 0.03 |
| T3_noquote_shape | 84 | ordered text | 0.89 |  | 0.20 (0.005) | 0.17 (0.010) | 0.14 | 0.05 (0.290) | 0.04 |
| T3_noquote_shape_sd | 84 | ordered text | 0.88 |  | 0.20 (0.005) | 0.16 (0.025) | 0.14 | 0.06 (0.190) | 0.05 |

Top-5 neighbour make-up (observed / chance) and hubness (skew of the 5-nearest in-degree; share of books in nobody's top 5; largest in-degree and the book).

| block | same author | same genre | mean abs year diff | mean abs log-words diff | hub skew | in no top 5 | max in-degree |
|---|---|---|---|---|---|---|---|
| T1_scalars | 0.21 / 0.03 | 0.25 / 0.11 | 37 / 56 | 0.65 / 0.76 | 0.64 | 0.07 | 15 (hardy_mayor) |
| T1_scalars_noquote | 0.20 / 0.03 | 0.24 / 0.11 | 36 / 56 | 0.63 / 0.76 | 1.06 | 0.10 | 18 (woolf_voyage) |
| T1_bag | 0.20 / 0.03 | 0.22 / 0.11 | 37 / 56 | 0.64 / 0.76 | 0.74 | 0.05 | 15 (twain_yankee) |
| T2_curves20_euc | 0.10 / 0.03 | 0.14 / 0.11 | 47 / 56 | 0.66 / 0.76 | 0.88 | 0.02 | 17 (hammett_falcon) |
| T2_curves50_euc | 0.11 / 0.03 | 0.13 / 0.11 | 47 / 56 | 0.66 / 0.76 | 2.79 | 0.04 | 28 (hammett_falcon) |
| T2_curves20_dtw | 0.11 / 0.03 | 0.12 / 0.11 | 46 / 56 | 0.75 / 0.76 | 0.45 | 0.04 | 13 (fathers_garnett) |
| T2_curves50_dtw | 0.10 / 0.03 | 0.16 / 0.11 | 43 / 56 | 0.70 / 0.76 | 1.16 | 0.02 | 20 (charterhouse_moncrieff) |
| T2_shape | 0.10 / 0.03 | 0.13 / 0.11 | 46 / 56 | 0.56 / 0.76 | 2.73 | 0.12 | 37 (fathers_garnett) |
| T2_shape_nosd | 0.09 / 0.03 | 0.14 / 0.11 | 43 / 56 | 0.67 / 0.76 | 2.56 | 0.13 | 34 (fathers_garnett) |
| T2_dialogue20 | 0.05 / 0.03 | 0.12 / 0.11 | 54 / 56 | 0.72 / 0.76 | 1.02 | 0.00 | 12 (hardy_jude) |
| T2_sentence_length20 | 0.07 / 0.03 | 0.12 / 0.11 | 59 / 56 | 0.72 / 0.76 | 1.21 | 0.00 | 14 (dost_cp_garnett) |
| T2_valence20 | 0.07 / 0.03 | 0.14 / 0.11 | 50 / 56 | 0.67 / 0.76 | 0.50 | 0.01 | 13 (james_portrait) |
| T2_arousal20 | 0.07 / 0.03 | 0.13 / 0.11 | 47 / 56 | 0.69 / 0.76 | 1.06 | 0.00 | 13 (oz_land) |
| T2_first_person20 | 0.07 / 0.03 | 0.14 / 0.11 | 49 / 56 | 0.65 / 0.76 | 6.95 | 0.01 | 59 (hammett_falcon) |
| T2_new_vocab20 | 0.07 / 0.03 | 0.16 / 0.11 | 51 / 56 | 0.60 / 0.76 | 1.61 | 0.13 | 24 (dickens_pickwick) |
| T3_scalars_dtw20 | 0.22 / 0.03 | 0.23 / 0.11 | 35 / 56 | 0.64 / 0.76 | 1.24 | 0.08 | 18 (hardy_madding) |
| T3_scalars_dtw20_sd | 0.18 / 0.03 | 0.20 / 0.11 | 38 / 56 | 0.69 / 0.76 | 0.82 | 0.06 | 15 (hardy_madding) |
| T3_scalars_shape | 0.18 / 0.03 | 0.23 / 0.11 | 38 / 56 | 0.64 / 0.76 | 1.15 | 0.12 | 19 (austen_persuasion) |
| T3_scalars_dtw20_shape | 0.17 / 0.03 | 0.24 / 0.11 | 37 / 56 | 0.66 / 0.76 | 1.04 | 0.11 | 16 (hardy_madding) |
| T3_noquote_shape | 0.19 / 0.03 | 0.20 / 0.11 | 39 / 56 | 0.64 / 0.76 | 1.34 | 0.11 | 20 (austen_persuasion) |
| T3_noquote_shape_sd | 0.18 / 0.03 | 0.19 / 0.11 | 38 / 56 | 0.65 / 0.76 | 1.18 | 0.15 | 22 (twain_yankee) |

Spearman between the pair distances of two blocks, all pairs.

| block | T1_scalars | T1_scalars_noquote | T1_bag | T2_curves20_euc | T2_curves50_euc | T2_curves20_dtw | T2_curves50_dtw | T2_shape | T2_shape_nosd | T2_dialogue20 | T2_sentence_length20 | T2_valence20 | T2_arousal20 | T2_first_person20 | T2_new_vocab20 | T3_scalars_dtw20 | T3_scalars_dtw20_sd | T3_scalars_shape | T3_scalars_dtw20_shape | T3_noquote_shape | T3_noquote_shape_sd |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| T1_scalars | 1.00 | 0.84 | 0.80 | 0.09 | 0.08 | 0.10 | 0.09 | 0.23 | 0.18 | 0.02 | 0.05 | 0.03 | -0.03 | 0.08 | 0.12 | 0.96 | 0.69 | 0.90 | 0.82 | 0.79 | 0.74 |
| T1_scalars_noquote | 0.84 | 1.00 | 0.93 | 0.07 | 0.06 | 0.08 | 0.06 | 0.13 | 0.11 | 0.03 | 0.04 | 0.02 | -0.01 | 0.07 | 0.04 | 0.80 | 0.58 | 0.73 | 0.67 | 0.87 | 0.80 |
| T1_bag | 0.80 | 0.93 | 1.00 | 0.06 | 0.05 | 0.05 | 0.05 | 0.14 | 0.10 | -0.00 | 0.03 | 0.02 | -0.01 | 0.07 | 0.06 | 0.76 | 0.53 | 0.70 | 0.63 | 0.82 | 0.75 |
| T2_curves20_euc | 0.09 | 0.07 | 0.06 | 1.00 | 0.81 | 0.66 | 0.47 | 0.46 | 0.49 | 0.56 | 0.55 | 0.37 | 0.39 | 0.40 | 0.14 | 0.26 | 0.51 | 0.28 | 0.39 | 0.29 | 0.34 |
| T2_curves50_euc | 0.08 | 0.06 | 0.05 | 0.81 | 1.00 | 0.55 | 0.43 | 0.43 | 0.45 | 0.47 | 0.46 | 0.31 | 0.30 | 0.31 | 0.18 | 0.22 | 0.42 | 0.25 | 0.34 | 0.26 | 0.30 |
| T2_curves20_dtw | 0.10 | 0.08 | 0.05 | 0.66 | 0.55 | 1.00 | 0.74 | 0.55 | 0.61 | 0.40 | 0.40 | 0.20 | 0.26 | 0.28 | 0.06 | 0.36 | 0.76 | 0.34 | 0.53 | 0.35 | 0.41 |
| T2_curves50_dtw | 0.09 | 0.06 | 0.05 | 0.47 | 0.43 | 0.74 | 1.00 | 0.43 | 0.45 | 0.28 | 0.27 | 0.13 | 0.17 | 0.24 | 0.01 | 0.29 | 0.58 | 0.27 | 0.41 | 0.26 | 0.31 |
| T2_shape | 0.23 | 0.13 | 0.14 | 0.46 | 0.43 | 0.55 | 0.43 | 1.00 | 0.93 | 0.27 | 0.29 | 0.14 | 0.14 | 0.18 | 0.24 | 0.36 | 0.53 | 0.58 | 0.65 | 0.54 | 0.63 |
| T2_shape_nosd | 0.18 | 0.11 | 0.10 | 0.49 | 0.45 | 0.61 | 0.45 | 0.93 | 1.00 | 0.31 | 0.30 | 0.15 | 0.17 | 0.17 | 0.24 | 0.33 | 0.55 | 0.57 | 0.65 | 0.54 | 0.64 |
| T2_dialogue20 | 0.02 | 0.03 | -0.00 | 0.56 | 0.47 | 0.40 | 0.28 | 0.27 | 0.31 | 1.00 | 0.27 | 0.00 | 0.06 | 0.01 | 0.11 | 0.13 | 0.29 | 0.15 | 0.22 | 0.17 | 0.20 |
| T2_sentence_length20 | 0.05 | 0.04 | 0.03 | 0.55 | 0.46 | 0.40 | 0.27 | 0.29 | 0.30 | 0.27 | 1.00 | -0.04 | 0.04 | 0.00 | 0.09 | 0.15 | 0.31 | 0.16 | 0.24 | 0.17 | 0.20 |
| T2_valence20 | 0.03 | 0.02 | 0.02 | 0.37 | 0.31 | 0.20 | 0.13 | 0.14 | 0.15 | 0.00 | -0.04 | 1.00 | -0.02 | 0.02 | 0.06 | 0.09 | 0.16 | 0.09 | 0.12 | 0.08 | 0.09 |
| T2_arousal20 | -0.03 | -0.01 | -0.01 | 0.39 | 0.30 | 0.26 | 0.17 | 0.14 | 0.17 | 0.06 | 0.04 | -0.02 | 1.00 | -0.02 | -0.02 | 0.04 | 0.15 | 0.04 | 0.10 | 0.06 | 0.08 |
| T2_first_person20 | 0.08 | 0.07 | 0.07 | 0.40 | 0.31 | 0.28 | 0.24 | 0.18 | 0.17 | 0.01 | 0.00 | 0.02 | -0.02 | 1.00 | -0.01 | 0.15 | 0.24 | 0.14 | 0.18 | 0.14 | 0.16 |
| T2_new_vocab20 | 0.12 | 0.04 | 0.06 | 0.14 | 0.18 | 0.06 | 0.01 | 0.24 | 0.24 | 0.11 | 0.09 | 0.06 | -0.02 | -0.01 | 1.00 | 0.12 | 0.11 | 0.19 | 0.18 | 0.14 | 0.16 |
| T3_scalars_dtw20 | 0.96 | 0.80 | 0.76 | 0.26 | 0.22 | 0.36 | 0.29 | 0.36 | 0.33 | 0.13 | 0.15 | 0.09 | 0.04 | 0.15 | 0.12 | 1.00 | 0.87 | 0.94 | 0.92 | 0.83 | 0.80 |
| T3_scalars_dtw20_sd | 0.69 | 0.58 | 0.53 | 0.51 | 0.42 | 0.76 | 0.58 | 0.53 | 0.55 | 0.29 | 0.31 | 0.16 | 0.15 | 0.24 | 0.11 | 0.87 | 1.00 | 0.82 | 0.91 | 0.75 | 0.77 |
| T3_scalars_shape | 0.90 | 0.73 | 0.70 | 0.28 | 0.25 | 0.34 | 0.27 | 0.58 | 0.57 | 0.15 | 0.16 | 0.09 | 0.04 | 0.14 | 0.19 | 0.94 | 0.82 | 1.00 | 0.97 | 0.89 | 0.89 |
| T3_scalars_dtw20_shape | 0.82 | 0.67 | 0.63 | 0.39 | 0.34 | 0.53 | 0.41 | 0.65 | 0.65 | 0.22 | 0.24 | 0.12 | 0.10 | 0.18 | 0.18 | 0.92 | 0.91 | 0.97 | 1.00 | 0.88 | 0.90 |
| T3_noquote_shape | 0.79 | 0.87 | 0.82 | 0.29 | 0.26 | 0.35 | 0.26 | 0.54 | 0.54 | 0.17 | 0.17 | 0.08 | 0.06 | 0.14 | 0.14 | 0.83 | 0.75 | 0.89 | 0.88 | 1.00 | 0.99 |
| T3_noquote_shape_sd | 0.74 | 0.80 | 0.75 | 0.34 | 0.30 | 0.41 | 0.31 | 0.63 | 0.64 | 0.20 | 0.20 | 0.09 | 0.08 | 0.16 | 0.16 | 0.80 | 0.77 | 0.89 | 0.90 | 0.99 | 1.00 |

Spearman between the pair distances of two blocks, different-author pairs only.

| block | T1_scalars | T1_scalars_noquote | T1_bag | T2_curves20_euc | T2_curves50_euc | T2_curves20_dtw | T2_curves50_dtw | T2_shape | T2_shape_nosd | T2_dialogue20 | T2_sentence_length20 | T2_valence20 | T2_arousal20 | T2_first_person20 | T2_new_vocab20 | T3_scalars_dtw20 | T3_scalars_dtw20_sd | T3_scalars_shape | T3_scalars_dtw20_shape | T3_noquote_shape | T3_noquote_shape_sd |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| T1_scalars | 1.00 | 0.84 | 0.79 | 0.08 | 0.07 | 0.09 | 0.08 | 0.22 | 0.17 | 0.02 | 0.04 | 0.03 | -0.04 | 0.07 | 0.11 | 0.96 | 0.69 | 0.89 | 0.82 | 0.78 | 0.73 |
| T1_scalars_noquote | 0.84 | 1.00 | 0.93 | 0.06 | 0.04 | 0.06 | 0.05 | 0.12 | 0.09 | 0.02 | 0.03 | 0.01 | -0.02 | 0.06 | 0.02 | 0.80 | 0.57 | 0.73 | 0.67 | 0.87 | 0.80 |
| T1_bag | 0.79 | 0.93 | 1.00 | 0.05 | 0.04 | 0.04 | 0.04 | 0.13 | 0.09 | -0.01 | 0.02 | 0.01 | -0.02 | 0.06 | 0.04 | 0.75 | 0.52 | 0.69 | 0.63 | 0.81 | 0.75 |
| T2_curves20_euc | 0.08 | 0.06 | 0.05 | 1.00 | 0.81 | 0.66 | 0.47 | 0.45 | 0.48 | 0.56 | 0.55 | 0.36 | 0.39 | 0.39 | 0.14 | 0.25 | 0.51 | 0.27 | 0.39 | 0.28 | 0.33 |
| T2_curves50_euc | 0.07 | 0.04 | 0.04 | 0.81 | 1.00 | 0.54 | 0.42 | 0.42 | 0.44 | 0.47 | 0.46 | 0.30 | 0.30 | 0.30 | 0.17 | 0.21 | 0.42 | 0.24 | 0.34 | 0.25 | 0.29 |
| T2_curves20_dtw | 0.09 | 0.06 | 0.04 | 0.66 | 0.54 | 1.00 | 0.74 | 0.55 | 0.61 | 0.40 | 0.39 | 0.19 | 0.25 | 0.28 | 0.05 | 0.35 | 0.75 | 0.33 | 0.52 | 0.34 | 0.41 |
| T2_curves50_dtw | 0.08 | 0.05 | 0.04 | 0.47 | 0.42 | 0.74 | 1.00 | 0.42 | 0.44 | 0.27 | 0.27 | 0.13 | 0.16 | 0.23 | 0.00 | 0.28 | 0.58 | 0.26 | 0.40 | 0.25 | 0.30 |
| T2_shape | 0.22 | 0.12 | 0.13 | 0.45 | 0.42 | 0.55 | 0.42 | 1.00 | 0.93 | 0.27 | 0.28 | 0.13 | 0.13 | 0.17 | 0.24 | 0.35 | 0.52 | 0.58 | 0.64 | 0.53 | 0.63 |
| T2_shape_nosd | 0.17 | 0.09 | 0.09 | 0.48 | 0.44 | 0.61 | 0.44 | 0.93 | 1.00 | 0.31 | 0.29 | 0.14 | 0.16 | 0.17 | 0.23 | 0.33 | 0.54 | 0.56 | 0.65 | 0.54 | 0.64 |
| T2_dialogue20 | 0.02 | 0.02 | -0.01 | 0.56 | 0.47 | 0.40 | 0.27 | 0.27 | 0.31 | 1.00 | 0.27 | -0.01 | 0.05 | 0.01 | 0.11 | 0.13 | 0.29 | 0.15 | 0.22 | 0.16 | 0.20 |
| T2_sentence_length20 | 0.04 | 0.03 | 0.02 | 0.55 | 0.46 | 0.39 | 0.27 | 0.28 | 0.29 | 0.27 | 1.00 | -0.04 | 0.03 | -0.01 | 0.08 | 0.15 | 0.30 | 0.16 | 0.23 | 0.17 | 0.19 |
| T2_valence20 | 0.03 | 0.01 | 0.01 | 0.36 | 0.30 | 0.19 | 0.13 | 0.13 | 0.14 | -0.01 | -0.04 | 1.00 | -0.03 | 0.02 | 0.05 | 0.08 | 0.15 | 0.08 | 0.12 | 0.07 | 0.09 |
| T2_arousal20 | -0.04 | -0.02 | -0.02 | 0.39 | 0.30 | 0.25 | 0.16 | 0.13 | 0.16 | 0.05 | 0.03 | -0.03 | 1.00 | -0.03 | -0.03 | 0.03 | 0.15 | 0.04 | 0.09 | 0.05 | 0.07 |
| T2_first_person20 | 0.07 | 0.06 | 0.06 | 0.39 | 0.30 | 0.28 | 0.23 | 0.17 | 0.17 | 0.01 | -0.01 | 0.02 | -0.03 | 1.00 | -0.02 | 0.14 | 0.23 | 0.13 | 0.18 | 0.13 | 0.15 |
| T2_new_vocab20 | 0.11 | 0.02 | 0.04 | 0.14 | 0.17 | 0.05 | 0.00 | 0.24 | 0.23 | 0.11 | 0.08 | 0.05 | -0.03 | -0.02 | 1.00 | 0.11 | 0.10 | 0.17 | 0.17 | 0.13 | 0.15 |
| T3_scalars_dtw20 | 0.96 | 0.80 | 0.75 | 0.25 | 0.21 | 0.35 | 0.28 | 0.35 | 0.33 | 0.13 | 0.15 | 0.08 | 0.03 | 0.14 | 0.11 | 1.00 | 0.86 | 0.94 | 0.92 | 0.83 | 0.80 |
| T3_scalars_dtw20_sd | 0.69 | 0.57 | 0.52 | 0.51 | 0.42 | 0.75 | 0.58 | 0.52 | 0.54 | 0.29 | 0.30 | 0.15 | 0.15 | 0.23 | 0.10 | 0.86 | 1.00 | 0.81 | 0.91 | 0.75 | 0.76 |
| T3_scalars_shape | 0.89 | 0.73 | 0.69 | 0.27 | 0.24 | 0.33 | 0.26 | 0.58 | 0.56 | 0.15 | 0.16 | 0.08 | 0.04 | 0.13 | 0.17 | 0.94 | 0.81 | 1.00 | 0.97 | 0.89 | 0.89 |
| T3_scalars_dtw20_shape | 0.82 | 0.67 | 0.63 | 0.39 | 0.34 | 0.52 | 0.40 | 0.64 | 0.65 | 0.22 | 0.23 | 0.12 | 0.09 | 0.18 | 0.17 | 0.92 | 0.91 | 0.97 | 1.00 | 0.88 | 0.90 |
| T3_noquote_shape | 0.78 | 0.87 | 0.81 | 0.28 | 0.25 | 0.34 | 0.25 | 0.53 | 0.54 | 0.16 | 0.17 | 0.07 | 0.05 | 0.13 | 0.13 | 0.83 | 0.75 | 0.89 | 0.88 | 1.00 | 0.99 |
| T3_noquote_shape_sd | 0.73 | 0.80 | 0.75 | 0.33 | 0.29 | 0.41 | 0.30 | 0.63 | 0.64 | 0.20 | 0.19 | 0.09 | 0.07 | 0.15 | 0.15 | 0.80 | 0.76 | 0.89 | 0.90 | 0.99 | 1.00 |


## P1 most-frequent-word grid, all 87 books

AUC that a labelled pair is closer than a negative pair (3663 negatives; [95% bootstrap interval over the labelled pairs]). n = labelled pairs.

| block | translation_pair (n=10) | edition_pair (n=1) | same_author_unrelated (n=52) | same_author_orig_en (n=33) | same_author_same_translator (n=5) | same_author_diff_translator (n=14) | series (n=7) | retelling (n=8) | same_translator_diff_author (n=11) | same_genre (n=261) |
|---|---|---|---|---|---|---|---|---|---|---|
| P1_mfw100_all_noprop_cull | 1.00 [1.00, 1.00] | 1.00 | 0.98 [0.97, 0.99] | 0.98 [0.96, 0.99] | 1.00 [1.00, 1.00] | 0.97 [0.95, 0.99] | 1.00 [0.99, 1.00] | 0.88 [0.78, 0.96] | 0.91 [0.81, 0.98] | 0.63 [0.59, 0.67] |
| P1_mfw100_all_noprop_nocull | 1.00 [1.00, 1.00] | 1.00 | 0.98 [0.97, 0.99] | 0.98 [0.96, 0.99] | 1.00 [1.00, 1.00] | 0.97 [0.95, 0.99] | 1.00 [0.99, 1.00] | 0.88 [0.78, 0.96] | 0.91 [0.81, 0.98] | 0.63 [0.59, 0.67] |
| P1_mfw100_all_raw_cull | 1.00 [1.00, 1.00] | 1.00 | 0.98 [0.97, 0.99] | 0.98 [0.97, 0.99] | 1.00 [1.00, 1.00] | 0.97 [0.96, 0.99] | 1.00 [0.99, 1.00] | 0.88 [0.79, 0.96] | 0.91 [0.81, 0.98] | 0.63 [0.59, 0.67] |
| P1_mfw100_all_raw_nocull | 1.00 [1.00, 1.00] | 1.00 | 0.98 [0.97, 0.99] | 0.98 [0.97, 0.99] | 1.00 [1.00, 1.00] | 0.97 [0.95, 0.99] | 1.00 [0.99, 1.00] | 0.88 [0.78, 0.97] | 0.91 [0.82, 0.98] | 0.63 [0.59, 0.66] |
| P1_mfw100_narr_noprop_cull | 1.00 [1.00, 1.00] | 1.00 | 0.96 [0.94, 0.98] | 0.97 [0.94, 0.99] | 0.93 [0.80, 1.00] | 0.96 [0.92, 0.99] | 1.00 [0.99, 1.00] | 0.94 [0.89, 0.98] | 0.86 [0.71, 0.96] | 0.62 [0.58, 0.66] |
| P1_mfw100_narr_noprop_nocull | 1.00 [1.00, 1.00] | 1.00 | 0.96 [0.94, 0.98] | 0.97 [0.94, 0.99] | 0.93 [0.80, 1.00] | 0.96 [0.92, 0.99] | 1.00 [0.99, 1.00] | 0.94 [0.89, 0.98] | 0.86 [0.71, 1.00] | 0.62 [0.58, 0.65] |
| P1_mfw100_narr_raw_cull | 1.00 [1.00, 1.00] | 1.00 | 0.96 [0.94, 0.98] | 0.97 [0.94, 0.99] | 0.93 [0.81, 1.00] | 0.97 [0.93, 0.99] | 1.00 [0.99, 1.00] | 0.94 [0.89, 0.98] | 0.86 [0.72, 1.00] | 0.62 [0.59, 0.66] |
| P1_mfw100_narr_raw_nocull | 1.00 [1.00, 1.00] | 1.00 | 0.96 [0.94, 0.98] | 0.97 [0.94, 0.99] | 0.93 [0.81, 1.00] | 0.97 [0.93, 0.99] | 1.00 [0.99, 1.00] | 0.94 [0.89, 0.98] | 0.86 [0.72, 0.97] | 0.62 [0.59, 0.66] |
| P1_mfw200_all_noprop_cull | 1.00 [1.00, 1.00] | 1.00 | 0.99 [0.98, 0.99] | 0.99 [0.97, 0.99] | 1.00 [1.00, 1.00] | 0.98 [0.97, 0.99] | 1.00 [0.99, 1.00] | 0.93 [0.85, 0.98] | 0.96 [0.92, 0.99] | 0.65 [0.62, 0.69] |
| P1_mfw200_all_noprop_nocull | 1.00 [1.00, 1.00] | 1.00 | 0.99 [0.98, 0.99] | 0.99 [0.97, 0.99] | 1.00 [1.00, 1.00] | 0.98 [0.97, 0.99] | 1.00 [0.99, 1.00] | 0.93 [0.85, 0.98] | 0.96 [0.92, 0.99] | 0.65 [0.62, 0.69] |
| P1_mfw200_all_raw_cull | 1.00 [1.00, 1.00] | 1.00 | 0.99 [0.98, 0.99] | 0.99 [0.97, 0.99] | 1.00 [1.00, 1.00] | 0.98 [0.97, 0.99] | 1.00 [0.99, 1.00] | 0.91 [0.82, 0.98] | 0.96 [0.93, 0.99] | 0.66 [0.62, 0.69] |
| P1_mfw200_all_raw_nocull | 1.00 [1.00, 1.00] | 1.00 | 0.99 [0.98, 0.99] | 0.99 [0.97, 0.99] | 1.00 [1.00, 1.00] | 0.98 [0.97, 0.99] | 1.00 [0.99, 1.00] | 0.91 [0.82, 0.98] | 0.96 [0.92, 0.99] | 0.66 [0.62, 0.69] |
| P1_mfw200_narr_noprop_cull | 1.00 [1.00, 1.00] | 1.00 | 0.97 [0.95, 0.99] | 0.97 [0.93, 0.99] | 0.96 [0.90, 1.00] | 0.98 [0.96, 0.99] | 0.99 [0.99, 1.00] | 0.95 [0.91, 0.98] | 0.89 [0.78, 0.99] | 0.64 [0.60, 0.68] |
| P1_mfw200_narr_noprop_nocull | 1.00 [1.00, 1.00] | 1.00 | 0.97 [0.95, 0.99] | 0.97 [0.93, 0.99] | 0.96 [0.90, 1.00] | 0.98 [0.96, 0.99] | 0.99 [0.99, 1.00] | 0.95 [0.91, 0.98] | 0.89 [0.78, 0.99] | 0.64 [0.60, 0.68] |
| P1_mfw200_narr_raw_cull | 1.00 [1.00, 1.00] | 1.00 | 0.97 [0.95, 0.99] | 0.97 [0.94, 0.99] | 0.97 [0.92, 1.00] | 0.98 [0.96, 0.99] | 0.99 [0.99, 1.00] | 0.93 [0.88, 0.98] | 0.90 [0.78, 0.99] | 0.65 [0.61, 0.69] |
| P1_mfw200_narr_raw_nocull | 1.00 [1.00, 1.00] | 1.00 | 0.97 [0.95, 0.99] | 0.97 [0.94, 0.99] | 0.97 [0.92, 1.00] | 0.98 [0.97, 0.99] | 0.99 [0.99, 1.00] | 0.93 [0.89, 0.97] | 0.90 [0.78, 0.98] | 0.65 [0.61, 0.68] |
| P1_mfw500_all_noprop_cull | 1.00 [1.00, 1.00] | 1.00 | 0.99 [0.98, 0.99] | 0.99 [0.99, 1.00] | 1.00 [1.00, 1.00] | 0.98 [0.96, 1.00] | 1.00 [1.00, 1.00] | 0.97 [0.93, 0.99] | 0.95 [0.90, 0.99] | 0.68 [0.65, 0.72] |
| P1_mfw500_all_noprop_nocull | 1.00 [1.00, 1.00] | 1.00 | 0.99 [0.98, 0.99] | 0.99 [0.99, 1.00] | 1.00 [1.00, 1.00] | 0.98 [0.96, 1.00] | 1.00 [1.00, 1.00] | 0.97 [0.94, 0.99] | 0.95 [0.90, 0.99] | 0.68 [0.65, 0.72] |
| P1_mfw500_all_raw_cull | 1.00 [1.00, 1.00] | 1.00 | 0.99 [0.98, 0.99] | 0.99 [0.99, 1.00] | 1.00 [1.00, 1.00] | 0.98 [0.96, 1.00] | 1.00 [1.00, 1.00] | 0.97 [0.93, 0.99] | 0.96 [0.91, 0.99] | 0.68 [0.65, 0.72] |
| P1_mfw500_all_raw_nocull | 1.00 [1.00, 1.00] | 1.00 | 0.99 [0.98, 0.99] | 0.99 [0.99, 1.00] | 1.00 [1.00, 1.00] | 0.98 [0.97, 1.00] | 1.00 [1.00, 1.00] | 0.97 [0.93, 0.99] | 0.96 [0.91, 0.99] | 0.68 [0.65, 0.72] |
| P1_mfw500_narr_noprop_cull | 1.00 [1.00, 1.00] | 1.00 | 0.98 [0.96, 0.99] | 0.98 [0.96, 0.99] | 0.97 [0.91, 1.00] | 0.98 [0.96, 1.00] | 1.00 [0.99, 1.00] | 0.98 [0.97, 0.99] | 0.86 [0.71, 0.99] | 0.65 [0.61, 0.69] |
| P1_mfw500_narr_noprop_nocull | 1.00 [1.00, 1.00] | 1.00 | 0.98 [0.96, 0.99] | 0.98 [0.96, 0.99] | 0.97 [0.91, 1.00] | 0.98 [0.96, 0.99] | 1.00 [0.99, 1.00] | 0.98 [0.97, 0.99] | 0.86 [0.71, 0.99] | 0.65 [0.62, 0.69] |
| P1_mfw500_narr_raw_cull | 1.00 [1.00, 1.00] | 1.00 | 0.98 [0.96, 0.99] | 0.98 [0.96, 0.99] | 0.97 [0.92, 1.00] | 0.98 [0.96, 1.00] | 0.99 [0.99, 1.00] | 0.98 [0.97, 0.99] | 0.86 [0.71, 0.99] | 0.66 [0.62, 0.70] |
| P1_mfw500_narr_raw_nocull | 1.00 [1.00, 1.00] | 1.00 | 0.98 [0.97, 0.99] | 0.98 [0.96, 0.99] | 0.97 [0.92, 1.00] | 0.98 [0.96, 0.99] | 1.00 [0.99, 1.00] | 0.98 [0.96, 0.99] | 0.86 [0.71, 0.99] | 0.66 [0.62, 0.69] |

AUC difference from `P1_mfw500_all_raw_nocull` on the same pairs [paired bootstrap 95%].

| block | translation_pair (n=10) | edition_pair (n=1) | same_author_unrelated (n=52) | same_author_orig_en (n=33) | same_author_same_translator (n=5) | same_author_diff_translator (n=14) | series (n=7) | retelling (n=8) | same_translator_diff_author (n=11) | same_genre (n=261) |
|---|---|---|---|---|---|---|---|---|---|---|
| P1_mfw100_all_noprop_cull | -0.00 [-0.00, +0.00] |  | -0.01 [-0.02, -0.00] | -0.01 [-0.03, +0.00] | -0.00 [-0.00, +0.00] | -0.01 [-0.03, +0.00] | -0.00 [-0.01, +0.00] | -0.09 [-0.16, -0.03] | -0.05 [-0.11, -0.01] | -0.05 [-0.07, -0.04] |
| P1_mfw100_all_noprop_nocull | -0.00 [-0.00, +0.00] |  | -0.01 [-0.02, -0.00] | -0.01 [-0.03, +0.00] | -0.00 [-0.00, +0.00] | -0.01 [-0.03, +0.00] | -0.00 [-0.01, +0.00] | -0.09 [-0.16, -0.03] | -0.05 [-0.11, -0.01] | -0.05 [-0.07, -0.04] |
| P1_mfw100_all_raw_cull | -0.00 [-0.00, +0.00] |  | -0.01 [-0.02, -0.00] | -0.01 [-0.02, +0.00] | -0.00 [-0.00, +0.00] | -0.01 [-0.03, +0.00] | -0.00 [-0.00, +0.00] | -0.09 [-0.16, -0.03] | -0.05 [-0.11, -0.01] | -0.06 [-0.07, -0.04] |
| P1_mfw100_all_raw_nocull | -0.00 [-0.00, -0.00] |  | -0.01 [-0.02, +0.00] | -0.01 [-0.02, +0.00] | -0.00 [-0.00, +0.00] | -0.01 [-0.02, +0.00] | -0.00 [-0.00, +0.00] | -0.09 [-0.16, -0.03] | -0.05 [-0.11, -0.00] | -0.06 [-0.07, -0.04] |
| P1_mfw100_narr_noprop_cull | +0.00 [-0.00, +0.00] |  | -0.03 [-0.05, -0.01] | -0.02 [-0.04, -0.00] | -0.07 [-0.19, +0.00] | -0.02 [-0.06, +0.01] | -0.00 [-0.00, +0.00] | -0.03 [-0.08, +0.01] | -0.10 [-0.21, +0.01] | -0.07 [-0.09, -0.04] |
| P1_mfw100_narr_noprop_nocull | +0.00 [-0.00, +0.00] |  | -0.03 [-0.05, -0.01] | -0.02 [-0.05, -0.00] | -0.07 [-0.19, +0.00] | -0.02 [-0.07, +0.01] | -0.00 [-0.00, +0.00] | -0.03 [-0.08, +0.01] | -0.10 [-0.22, +0.00] | -0.07 [-0.09, -0.04] |
| P1_mfw100_narr_raw_cull | +0.00 [-0.00, +0.00] |  | -0.03 [-0.05, -0.01] | -0.02 [-0.05, -0.00] | -0.07 [-0.18, +0.00] | -0.02 [-0.06, +0.02] | -0.00 [-0.00, +0.00] | -0.03 [-0.08, +0.01] | -0.10 [-0.22, +0.01] | -0.06 [-0.08, -0.03] |
| P1_mfw100_narr_raw_nocull | +0.00 [-0.00, +0.00] |  | -0.03 [-0.05, -0.01] | -0.02 [-0.05, -0.01] | -0.07 [-0.18, +0.00] | -0.02 [-0.06, +0.01] | -0.00 [-0.00, +0.00] | -0.03 [-0.08, +0.01] | -0.10 [-0.22, +0.01] | -0.06 [-0.08, -0.03] |
| P1_mfw200_all_noprop_cull | -0.00 [-0.00, +0.00] |  | -0.00 [-0.01, +0.00] | -0.00 [-0.02, +0.00] | -0.00 [-0.00, +0.00] | -0.00 [-0.01, +0.00] | -0.00 [-0.00, +0.00] | -0.04 [-0.09, -0.01] | +0.00 [-0.02, +0.02] | -0.03 [-0.04, -0.02] |
| P1_mfw200_all_noprop_nocull | -0.00 [-0.00, +0.00] |  | -0.00 [-0.01, +0.00] | -0.00 [-0.02, +0.00] | -0.00 [-0.00, +0.00] | -0.00 [-0.01, +0.00] | -0.00 [-0.00, +0.00] | -0.04 [-0.09, -0.01] | +0.00 [-0.02, +0.02] | -0.03 [-0.04, -0.02] |
| P1_mfw200_all_raw_cull | +0.00 [-0.00, +0.00] |  | -0.00 [-0.01, +0.00] | -0.00 [-0.01, +0.00] | -0.00 [-0.00, +0.00] | -0.00 [-0.01, +0.01] | -0.00 [-0.00, +0.00] | -0.06 [-0.11, -0.01] | +0.00 [-0.01, +0.02] | -0.03 [-0.04, -0.02] |
| P1_mfw200_all_raw_nocull | +0.00 [-0.00, +0.00] |  | -0.00 [-0.01, +0.00] | -0.00 [-0.01, +0.00] | -0.00 [-0.00, +0.00] | -0.00 [-0.01, +0.00] | -0.00 [-0.00, +0.00] | -0.06 [-0.11, -0.02] | +0.00 [-0.01, +0.02] | -0.03 [-0.04, -0.02] |
| P1_mfw200_narr_noprop_cull | -0.00 [-0.00, +0.00] |  | -0.02 [-0.04, -0.00] | -0.02 [-0.06, -0.00] | -0.04 [-0.10, +0.00] | -0.00 [-0.03, +0.02] | -0.00 [-0.01, +0.00] | -0.02 [-0.05, +0.01] | -0.07 [-0.15, +0.00] | -0.04 [-0.07, -0.02] |
| P1_mfw200_narr_noprop_nocull | -0.00 [-0.00, +0.00] |  | -0.02 [-0.04, -0.00] | -0.02 [-0.06, -0.00] | -0.04 [-0.10, +0.00] | -0.00 [-0.03, +0.02] | -0.00 [-0.01, +0.00] | -0.02 [-0.05, +0.01] | -0.07 [-0.16, +0.00] | -0.04 [-0.07, -0.02] |
| P1_mfw200_narr_raw_cull | +0.00 [-0.00, +0.00] |  | -0.02 [-0.04, -0.00] | -0.02 [-0.05, -0.00] | -0.03 [-0.08, +0.00] | -0.00 [-0.02, +0.02] | -0.00 [-0.01, +0.00] | -0.04 [-0.08, -0.00] | -0.06 [-0.15, +0.01] | -0.03 [-0.06, -0.01] |
| P1_mfw200_narr_raw_nocull | +0.00 [-0.00, +0.00] |  | -0.02 [-0.04, -0.00] | -0.02 [-0.05, -0.00] | -0.03 [-0.08, +0.00] | -0.00 [-0.02, +0.02] | -0.00 [-0.01, +0.00] | -0.04 [-0.08, -0.00] | -0.06 [-0.15, +0.00] | -0.03 [-0.06, -0.01] |
| P1_mfw500_all_noprop_cull | -0.00 [-0.00, +0.00] |  | -0.00 [-0.00, +0.00] | +0.00 [-0.00, +0.00] | -0.00 [-0.00, -0.00] | -0.00 [-0.01, +0.00] | +0.00 [+0.00, +0.00] | +0.00 [-0.00, +0.00] | -0.00 [-0.01, -0.00] | -0.00 [-0.00, +0.00] |
| P1_mfw500_all_noprop_nocull | -0.00 [-0.00, +0.00] |  | -0.00 [-0.00, +0.00] | +0.00 [-0.00, +0.00] | -0.00 [-0.00, -0.00] | -0.00 [-0.01, +0.00] | +0.00 [+0.00, +0.00] | +0.00 [-0.00, +0.01] | -0.00 [-0.01, -0.00] | -0.00 [-0.00, +0.00] |
| P1_mfw500_all_raw_cull | -0.00 [-0.00, +0.00] |  | -0.00 [-0.00, +0.00] | +0.00 [-0.00, +0.00] | -0.00 [-0.00, +0.00] | -0.00 [-0.00, +0.00] | +0.00 [+0.00, +0.00] | -0.00 [-0.01, -0.00] | -0.00 [-0.00, -0.00] | -0.00 [-0.00, +0.00] |
| P1_mfw500_narr_noprop_cull | -0.00 [-0.00, +0.00] |  | -0.01 [-0.03, +0.00] | -0.01 [-0.03, +0.00] | -0.03 [-0.09, +0.00] | -0.00 [-0.02, +0.01] | -0.00 [-0.01, +0.00] | +0.01 [-0.00, +0.04] | -0.10 [-0.22, -0.01] | -0.03 [-0.05, -0.01] |
| P1_mfw500_narr_noprop_nocull | -0.00 [-0.00, +0.00] |  | -0.01 [-0.03, +0.00] | -0.01 [-0.03, +0.00] | -0.03 [-0.09, +0.00] | -0.00 [-0.03, +0.01] | -0.00 [-0.01, +0.00] | +0.01 [-0.00, +0.04] | -0.10 [-0.22, +0.00] | -0.03 [-0.05, -0.01] |
| P1_mfw500_narr_raw_cull | -0.00 [-0.00, +0.00] |  | -0.01 [-0.02, -0.00] | -0.01 [-0.03, +0.00] | -0.03 [-0.08, +0.00] | -0.00 [-0.02, +0.02] | -0.00 [-0.01, +0.00] | +0.01 [-0.01, +0.04] | -0.10 [-0.21, +0.00] | -0.03 [-0.05, -0.00] |
| P1_mfw500_narr_raw_nocull | +0.00 [+0.00, +0.00] |  | -0.01 [-0.02, +0.00] | -0.01 [-0.03, +0.00] | -0.03 [-0.08, +0.00] | -0.00 [-0.02, +0.01] | -0.00 [-0.01, +0.00] | +0.01 [-0.01, +0.03] | -0.09 [-0.21, +0.00] | -0.03 [-0.05, -0.01] |

Mean percentile rank of the partner (0 = nearest book) / recall@1 / recall@5.

| block | translation_pair (n=10) | edition_pair (n=1) | same_author_unrelated (n=52) | same_author_orig_en (n=33) | same_author_same_translator (n=5) | same_author_diff_translator (n=14) | series (n=7) | retelling (n=8) | same_translator_diff_author (n=11) | same_genre (n=261) |
|---|---|---|---|---|---|---|---|---|---|---|
| P1_mfw100_all_noprop_cull | 0.00 / 0.88 / 1.00 | 0.00 / 1.00 / 1.00 | 0.03 / 0.65 / 0.98 | 0.02 / 0.72 / 0.97 | 0.01 / 0.86 / 1.00 | 0.04 / 0.12 / 0.94 | 0.00 / 1.00 / 1.00 | 0.13 / 0.30 / 0.80 | 0.11 / 0.00 / 0.83 | 0.38 / 0.13 / 0.75 |
| P1_mfw100_all_noprop_nocull | 0.00 / 0.88 / 1.00 | 0.00 / 1.00 / 1.00 | 0.03 / 0.65 / 0.98 | 0.02 / 0.72 / 0.97 | 0.01 / 0.86 / 1.00 | 0.04 / 0.12 / 0.94 | 0.00 / 1.00 / 1.00 | 0.13 / 0.30 / 0.80 | 0.11 / 0.00 / 0.83 | 0.38 / 0.13 / 0.75 |
| P1_mfw100_all_raw_cull | 0.00 / 0.88 / 1.00 | 0.00 / 1.00 / 1.00 | 0.02 / 0.65 / 1.00 | 0.02 / 0.72 / 1.00 | 0.01 / 0.86 / 1.00 | 0.04 / 0.12 / 0.94 | 0.00 / 1.00 / 1.00 | 0.12 / 0.30 / 0.80 | 0.11 / 0.00 / 0.83 | 0.38 / 0.13 / 0.70 |
| P1_mfw100_all_raw_nocull | 0.00 / 0.88 / 1.00 | 0.00 / 1.00 / 1.00 | 0.02 / 0.65 / 1.00 | 0.02 / 0.72 / 1.00 | 0.01 / 0.86 / 1.00 | 0.04 / 0.12 / 0.94 | 0.00 / 1.00 / 1.00 | 0.12 / 0.30 / 0.80 | 0.11 / 0.00 / 0.83 | 0.38 / 0.13 / 0.70 |
| P1_mfw100_narr_noprop_cull | 0.01 / 0.88 / 0.94 | 0.00 / 1.00 / 1.00 | 0.05 / 0.60 / 0.92 | 0.03 / 0.72 / 0.97 | 0.09 / 0.71 / 1.00 | 0.06 / 0.06 / 0.69 | 0.00 / 0.93 / 1.00 | 0.09 / 0.40 / 0.80 | 0.16 / 0.17 / 0.83 | 0.39 / 0.13 / 0.62 |
| P1_mfw100_narr_noprop_nocull | 0.01 / 0.88 / 0.94 | 0.00 / 1.00 / 1.00 | 0.05 / 0.60 / 0.92 | 0.03 / 0.72 / 0.97 | 0.09 / 0.71 / 1.00 | 0.06 / 0.06 / 0.69 | 0.00 / 0.93 / 1.00 | 0.09 / 0.40 / 0.80 | 0.16 / 0.17 / 0.83 | 0.39 / 0.13 / 0.62 |
| P1_mfw100_narr_raw_cull | 0.01 / 0.88 / 0.94 | 0.00 / 1.00 / 1.00 | 0.05 / 0.65 / 0.94 | 0.03 / 0.78 / 0.97 | 0.08 / 0.71 / 1.00 | 0.06 / 0.06 / 0.75 | 0.00 / 0.93 / 1.00 | 0.09 / 0.40 / 0.70 | 0.16 / 0.17 / 0.83 | 0.39 / 0.15 / 0.62 |
| P1_mfw100_narr_raw_nocull | 0.01 / 0.88 / 0.94 | 0.00 / 1.00 / 1.00 | 0.05 / 0.65 / 0.94 | 0.03 / 0.78 / 0.97 | 0.08 / 0.71 / 1.00 | 0.06 / 0.06 / 0.75 | 0.00 / 0.93 / 1.00 | 0.09 / 0.40 / 0.70 | 0.16 / 0.17 / 0.83 | 0.39 / 0.15 / 0.62 |
| P1_mfw200_all_noprop_cull | 0.01 / 0.88 / 0.94 | 0.00 / 1.00 / 1.00 | 0.02 / 0.71 / 1.00 | 0.02 / 0.81 / 1.00 | 0.01 / 0.86 / 1.00 | 0.03 / 0.12 / 0.94 | 0.00 / 1.00 / 1.00 | 0.09 / 0.30 / 0.80 | 0.07 / 0.00 / 1.00 | 0.36 / 0.17 / 0.74 |
| P1_mfw200_all_noprop_nocull | 0.01 / 0.88 / 0.94 | 0.00 / 1.00 / 1.00 | 0.02 / 0.71 / 1.00 | 0.02 / 0.81 / 1.00 | 0.01 / 0.86 / 1.00 | 0.03 / 0.12 / 0.94 | 0.00 / 1.00 / 1.00 | 0.09 / 0.30 / 0.80 | 0.07 / 0.00 / 1.00 | 0.36 / 0.17 / 0.74 |
| P1_mfw200_all_raw_cull | 0.01 / 0.88 / 0.94 | 0.00 / 1.00 / 1.00 | 0.02 / 0.71 / 1.00 | 0.02 / 0.81 / 1.00 | 0.01 / 0.86 / 1.00 | 0.03 / 0.12 / 0.94 | 0.00 / 1.00 / 1.00 | 0.10 / 0.30 / 0.80 | 0.06 / 0.00 / 1.00 | 0.35 / 0.15 / 0.72 |
| P1_mfw200_all_raw_nocull | 0.01 / 0.88 / 0.94 | 0.00 / 1.00 / 1.00 | 0.02 / 0.71 / 1.00 | 0.02 / 0.81 / 1.00 | 0.01 / 0.86 / 1.00 | 0.03 / 0.12 / 0.94 | 0.00 / 1.00 / 1.00 | 0.10 / 0.30 / 0.80 | 0.06 / 0.00 / 1.00 | 0.35 / 0.15 / 0.72 |
| P1_mfw200_narr_noprop_cull | 0.00 / 0.88 / 1.00 | 0.00 / 1.00 / 1.00 | 0.03 / 0.62 / 0.96 | 0.03 / 0.72 / 0.94 | 0.05 / 0.71 / 1.00 | 0.03 / 0.12 / 0.88 | 0.01 / 0.86 / 0.93 | 0.10 / 0.30 / 0.60 | 0.13 / 0.00 / 0.83 | 0.36 / 0.21 / 0.70 |
| P1_mfw200_narr_noprop_nocull | 0.00 / 0.88 / 1.00 | 0.00 / 1.00 / 1.00 | 0.03 / 0.62 / 0.96 | 0.03 / 0.72 / 0.94 | 0.05 / 0.71 / 1.00 | 0.03 / 0.12 / 0.88 | 0.01 / 0.86 / 0.93 | 0.10 / 0.30 / 0.60 | 0.13 / 0.00 / 0.83 | 0.36 / 0.21 / 0.70 |
| P1_mfw200_narr_raw_cull | 0.00 / 0.88 / 1.00 | 0.00 / 1.00 / 1.00 | 0.03 / 0.62 / 0.98 | 0.03 / 0.72 / 0.97 | 0.04 / 0.71 / 1.00 | 0.03 / 0.12 / 0.88 | 0.01 / 0.86 / 0.93 | 0.11 / 0.20 / 0.60 | 0.13 / 0.00 / 0.83 | 0.36 / 0.21 / 0.74 |
| P1_mfw200_narr_raw_nocull | 0.00 / 0.88 / 1.00 | 0.00 / 1.00 / 1.00 | 0.03 / 0.65 / 0.98 | 0.03 / 0.75 / 0.97 | 0.04 / 0.71 / 1.00 | 0.03 / 0.12 / 0.88 | 0.01 / 0.86 / 0.93 | 0.11 / 0.30 / 0.60 | 0.13 / 0.00 / 0.83 | 0.36 / 0.19 / 0.75 |
| P1_mfw500_all_noprop_cull | 0.00 / 0.94 / 0.94 | 0.00 / 1.00 / 1.00 | 0.02 / 0.69 / 1.00 | 0.01 / 0.81 / 1.00 | 0.01 / 0.71 / 1.00 | 0.03 / 0.12 / 0.94 | 0.00 / 1.00 / 1.00 | 0.04 / 0.50 / 0.80 | 0.07 / 0.00 / 1.00 | 0.33 / 0.19 / 0.79 |
| P1_mfw500_all_noprop_nocull | 0.00 / 0.94 / 0.94 | 0.00 / 1.00 / 1.00 | 0.02 / 0.69 / 1.00 | 0.01 / 0.81 / 1.00 | 0.01 / 0.71 / 1.00 | 0.03 / 0.12 / 0.94 | 0.00 / 1.00 / 1.00 | 0.04 / 0.50 / 0.80 | 0.07 / 0.00 / 1.00 | 0.33 / 0.19 / 0.79 |
| P1_mfw500_all_raw_cull | 0.00 / 0.94 / 0.94 | 0.00 / 1.00 / 1.00 | 0.02 / 0.67 / 1.00 | 0.01 / 0.78 / 1.00 | 0.01 / 0.71 / 1.00 | 0.03 / 0.12 / 0.94 | 0.00 / 1.00 / 1.00 | 0.05 / 0.50 / 0.80 | 0.06 / 0.00 / 1.00 | 0.33 / 0.19 / 0.79 |
| P1_mfw500_all_raw_nocull | 0.00 / 0.94 / 0.94 | 0.00 / 1.00 / 1.00 | 0.02 / 0.67 / 1.00 | 0.01 / 0.78 / 1.00 | 0.01 / 0.71 / 1.00 | 0.03 / 0.12 / 0.94 | 0.00 / 0.93 / 1.00 | 0.04 / 0.50 / 0.80 | 0.06 / 0.00 / 1.00 | 0.33 / 0.19 / 0.83 |
| P1_mfw500_narr_noprop_cull | 0.00 / 0.94 / 0.94 | 0.00 / 1.00 / 1.00 | 0.03 / 0.65 / 1.00 | 0.02 / 0.75 / 1.00 | 0.05 / 0.71 / 1.00 | 0.03 / 0.12 / 0.88 | 0.00 / 0.86 / 1.00 | 0.04 / 0.50 / 0.90 | 0.16 / 0.00 / 0.83 | 0.36 / 0.21 / 0.70 |
| P1_mfw500_narr_noprop_nocull | 0.00 / 0.94 / 0.94 | 0.00 / 1.00 / 1.00 | 0.03 / 0.65 / 1.00 | 0.02 / 0.75 / 1.00 | 0.04 / 0.71 / 1.00 | 0.03 / 0.12 / 0.88 | 0.00 / 0.86 / 1.00 | 0.04 / 0.50 / 0.90 | 0.16 / 0.00 / 0.83 | 0.36 / 0.21 / 0.68 |
| P1_mfw500_narr_raw_cull | 0.00 / 0.94 / 0.94 | 0.00 / 1.00 / 1.00 | 0.03 / 0.67 / 1.00 | 0.02 / 0.78 / 1.00 | 0.04 / 0.71 / 1.00 | 0.03 / 0.12 / 0.88 | 0.01 / 0.79 / 0.93 | 0.04 / 0.50 / 0.90 | 0.16 / 0.00 / 0.83 | 0.35 / 0.21 / 0.72 |
| P1_mfw500_narr_raw_nocull | 0.00 / 0.94 / 1.00 | 0.00 / 1.00 / 1.00 | 0.03 / 0.67 / 1.00 | 0.02 / 0.78 / 1.00 | 0.04 / 0.71 / 1.00 | 0.03 / 0.12 / 0.88 | 0.01 / 0.79 / 0.93 | 0.04 / 0.50 / 0.80 | 0.15 / 0.00 / 0.83 | 0.35 / 0.21 / 0.70 |

Split-half self-retrieval (accuracy; chance is 1/n), and Spearman of distance with |year difference| and |log word-count difference| (Mantel p in brackets; en = both books written in English; diff = different authors only).

| block | n | input | split a/b | split h1/h2 | rho year | rho year en | rho year en diff | rho logwords | rho logwords diff |
|---|---|---|---|---|---|---|---|---|---|
| P1_mfw100_all_noprop_cull | 87 | ordered text | 0.97 | 0.89 | 0.15 (0.005) | 0.19 (0.005) | 0.15 | 0.04 (0.020) | 0.02 |
| P1_mfw100_all_noprop_nocull | 87 | ordered text | 0.97 | 0.89 | 0.15 (0.005) | 0.19 (0.005) | 0.15 | 0.04 (0.010) | 0.02 |
| P1_mfw100_all_raw_cull | 87 | book bag | 0.97 | 0.90 | 0.14 (0.005) | 0.19 (0.005) | 0.16 | 0.03 (0.010) | 0.02 |
| P1_mfw100_all_raw_nocull | 87 | book bag | 0.97 | 0.90 | 0.14 (0.005) | 0.19 (0.005) | 0.16 | 0.03 (0.020) | 0.02 |
| P1_mfw100_narr_noprop_cull | 87 | ordered text | 0.95 | 0.84 | 0.15 (0.005) | 0.19 (0.005) | 0.16 | 0.07 (0.005) | 0.06 |
| P1_mfw100_narr_noprop_nocull | 87 | ordered text | 0.95 | 0.84 | 0.15 (0.005) | 0.19 (0.005) | 0.16 | 0.07 (0.005) | 0.06 |
| P1_mfw100_narr_raw_cull | 87 | ordered text | 0.96 | 0.86 | 0.14 (0.005) | 0.18 (0.005) | 0.14 | 0.06 (0.005) | 0.05 |
| P1_mfw100_narr_raw_nocull | 87 | ordered text | 0.96 | 0.86 | 0.14 (0.005) | 0.18 (0.005) | 0.14 | 0.06 (0.005) | 0.05 |
| P1_mfw200_all_noprop_cull | 87 | ordered text | 0.96 | 0.89 | 0.17 (0.005) | 0.21 (0.005) | 0.18 | 0.04 (0.025) | 0.03 |
| P1_mfw200_all_noprop_nocull | 87 | ordered text | 0.96 | 0.89 | 0.17 (0.005) | 0.21 (0.005) | 0.18 | 0.04 (0.015) | 0.03 |
| P1_mfw200_all_raw_cull | 87 | book bag | 0.96 | 0.89 | 0.17 (0.005) | 0.22 (0.005) | 0.18 | 0.04 (0.015) | 0.02 |
| P1_mfw200_all_raw_nocull | 87 | book bag | 0.96 | 0.89 | 0.17 (0.005) | 0.22 (0.005) | 0.18 | 0.04 (0.035) | 0.02 |
| P1_mfw200_narr_noprop_cull | 87 | ordered text | 0.96 | 0.89 | 0.16 (0.005) | 0.22 (0.005) | 0.18 | 0.06 (0.005) | 0.05 |
| P1_mfw200_narr_noprop_nocull | 87 | ordered text | 0.96 | 0.89 | 0.16 (0.005) | 0.22 (0.005) | 0.18 | 0.06 (0.005) | 0.05 |
| P1_mfw200_narr_raw_cull | 87 | ordered text | 0.96 | 0.87 | 0.17 (0.005) | 0.22 (0.005) | 0.19 | 0.06 (0.005) | 0.05 |
| P1_mfw200_narr_raw_nocull | 87 | ordered text | 0.96 | 0.88 | 0.17 (0.005) | 0.22 (0.005) | 0.18 | 0.06 (0.010) | 0.05 |
| P1_mfw500_all_noprop_cull | 87 | ordered text | 0.97 | 0.92 | 0.18 (0.005) | 0.24 (0.005) | 0.21 | 0.06 (0.010) | 0.04 |
| P1_mfw500_all_noprop_nocull | 87 | ordered text | 0.97 | 0.92 | 0.18 (0.005) | 0.24 (0.005) | 0.21 | 0.06 (0.005) | 0.04 |
| P1_mfw500_all_raw_cull | 87 | book bag | 0.97 | 0.92 | 0.18 (0.005) | 0.24 (0.005) | 0.21 | 0.06 (0.005) | 0.04 |
| P1_mfw500_all_raw_nocull | 87 | book bag | 0.97 | 0.93 | 0.18 (0.005) | 0.24 (0.005) | 0.21 | 0.06 (0.005) | 0.04 |
| P1_mfw500_narr_noprop_cull | 87 | ordered text | 0.95 | 0.91 | 0.18 (0.005) | 0.24 (0.005) | 0.21 | 0.08 (0.005) | 0.07 |
| P1_mfw500_narr_noprop_nocull | 87 | ordered text | 0.95 | 0.91 | 0.18 (0.005) | 0.25 (0.005) | 0.21 | 0.08 (0.005) | 0.07 |
| P1_mfw500_narr_raw_cull | 87 | ordered text | 0.96 | 0.92 | 0.18 (0.005) | 0.24 (0.005) | 0.21 | 0.08 (0.005) | 0.06 |
| P1_mfw500_narr_raw_nocull | 87 | ordered text | 0.95 | 0.92 | 0.18 (0.005) | 0.24 (0.005) | 0.20 | 0.08 (0.005) | 0.07 |

Top-5 neighbour make-up (observed / chance) and hubness (skew of the 5-nearest in-degree; share of books in nobody's top 5; largest in-degree and the book).

| block | same author | same genre | mean abs year diff | mean abs log-words diff | hub skew | in no top 5 | max in-degree |
|---|---|---|---|---|---|---|---|
| P1_mfw100_all_noprop_cull | 0.39 / 0.02 | 0.42 / 0.12 | 34 / 56 | 0.66 / 0.78 | 0.25 | 0.02 | 11 (barsoom_gods) |
| P1_mfw100_all_noprop_nocull | 0.39 / 0.02 | 0.42 / 0.12 | 34 / 56 | 0.66 / 0.78 | 0.25 | 0.02 | 11 (barsoom_gods) |
| P1_mfw100_all_raw_cull | 0.40 / 0.02 | 0.40 / 0.12 | 34 / 56 | 0.66 / 0.78 | 0.34 | 0.00 | 10 (austen_emma) |
| P1_mfw100_all_raw_nocull | 0.40 / 0.02 | 0.40 / 0.12 | 34 / 56 | 0.66 / 0.78 | 0.34 | 0.00 | 10 (austen_emma) |
| P1_mfw100_narr_noprop_cull | 0.35 / 0.02 | 0.35 / 0.12 | 32 / 56 | 0.60 / 0.78 | 0.31 | 0.00 | 10 (fathers_garnett) |
| P1_mfw100_narr_noprop_nocull | 0.35 / 0.02 | 0.35 / 0.12 | 32 / 56 | 0.60 / 0.78 | 0.31 | 0.00 | 10 (fathers_garnett) |
| P1_mfw100_narr_raw_cull | 0.35 / 0.02 | 0.35 / 0.12 | 33 / 56 | 0.60 / 0.78 | 0.43 | 0.00 | 12 (fathers_garnett) |
| P1_mfw100_narr_raw_nocull | 0.35 / 0.02 | 0.35 / 0.12 | 33 / 56 | 0.60 / 0.78 | 0.43 | 0.00 | 12 (fathers_garnett) |
| P1_mfw200_all_noprop_cull | 0.40 / 0.02 | 0.40 / 0.12 | 33 / 56 | 0.67 / 0.78 | 0.41 | 0.01 | 12 (barsoom_princess) |
| P1_mfw200_all_noprop_nocull | 0.40 / 0.02 | 0.40 / 0.12 | 33 / 56 | 0.67 / 0.78 | 0.41 | 0.01 | 12 (barsoom_princess) |
| P1_mfw200_all_raw_cull | 0.40 / 0.02 | 0.40 / 0.12 | 33 / 56 | 0.67 / 0.78 | 0.31 | 0.01 | 10 (austen_emma) |
| P1_mfw200_all_raw_nocull | 0.40 / 0.02 | 0.40 / 0.12 | 33 / 56 | 0.67 / 0.78 | 0.31 | 0.01 | 10 (austen_emma) |
| P1_mfw200_narr_noprop_cull | 0.37 / 0.02 | 0.40 / 0.12 | 31 / 56 | 0.62 / 0.78 | 0.38 | 0.02 | 11 (barsoom_princess) |
| P1_mfw200_narr_noprop_nocull | 0.37 / 0.02 | 0.40 / 0.12 | 31 / 56 | 0.62 / 0.78 | 0.38 | 0.02 | 11 (barsoom_princess) |
| P1_mfw200_narr_raw_cull | 0.38 / 0.02 | 0.41 / 0.12 | 31 / 56 | 0.60 / 0.78 | 0.17 | 0.00 | 10 (fathers_garnett) |
| P1_mfw200_narr_raw_nocull | 0.38 / 0.02 | 0.42 / 0.12 | 32 / 56 | 0.60 / 0.78 | 0.21 | 0.00 | 10 (fathers_garnett) |
| P1_mfw500_all_noprop_cull | 0.41 / 0.02 | 0.47 / 0.12 | 32 / 56 | 0.63 / 0.78 | 0.33 | 0.02 | 11 (austen_emma) |
| P1_mfw500_all_noprop_nocull | 0.41 / 0.02 | 0.47 / 0.12 | 32 / 56 | 0.63 / 0.78 | 0.33 | 0.02 | 11 (austen_emma) |
| P1_mfw500_all_raw_cull | 0.40 / 0.02 | 0.45 / 0.12 | 32 / 56 | 0.64 / 0.78 | 0.34 | 0.03 | 12 (austen_emma) |
| P1_mfw500_all_raw_nocull | 0.41 / 0.02 | 0.45 / 0.12 | 31 / 56 | 0.64 / 0.78 | 0.33 | 0.02 | 11 (austen_emma) |
| P1_mfw500_narr_noprop_cull | 0.39 / 0.02 | 0.41 / 0.12 | 29 / 56 | 0.62 / 0.78 | 0.24 | 0.01 | 11 (austen_emma) |
| P1_mfw500_narr_noprop_nocull | 0.39 / 0.02 | 0.40 / 0.12 | 29 / 56 | 0.61 / 0.78 | 0.18 | 0.01 | 11 (austen_emma) |
| P1_mfw500_narr_raw_cull | 0.38 / 0.02 | 0.40 / 0.12 | 29 / 56 | 0.61 / 0.78 | 0.13 | 0.00 | 10 (austen_emma) |
| P1_mfw500_narr_raw_nocull | 0.39 / 0.02 | 0.40 / 0.12 | 29 / 56 | 0.61 / 0.78 | 0.15 | 0.00 | 11 (austen_emma) |

Spearman between the pair distances of two blocks, all pairs.

| block | P1_mfw100_all_noprop_cull | P1_mfw100_all_noprop_nocull | P1_mfw100_all_raw_cull | P1_mfw100_all_raw_nocull | P1_mfw100_narr_noprop_cull | P1_mfw100_narr_noprop_nocull | P1_mfw100_narr_raw_cull | P1_mfw100_narr_raw_nocull | P1_mfw200_all_noprop_cull | P1_mfw200_all_noprop_nocull | P1_mfw200_all_raw_cull | P1_mfw200_all_raw_nocull | P1_mfw200_narr_noprop_cull | P1_mfw200_narr_noprop_nocull | P1_mfw200_narr_raw_cull | P1_mfw200_narr_raw_nocull | P1_mfw500_all_noprop_cull | P1_mfw500_all_noprop_nocull | P1_mfw500_all_raw_cull | P1_mfw500_all_raw_nocull | P1_mfw500_narr_noprop_cull | P1_mfw500_narr_noprop_nocull | P1_mfw500_narr_raw_cull | P1_mfw500_narr_raw_nocull |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| P1_mfw100_all_noprop_cull | 1.00 | 1.00 | 1.00 | 1.00 | 0.74 | 0.74 | 0.74 | 0.74 | 0.95 | 0.95 | 0.94 | 0.94 | 0.72 | 0.72 | 0.72 | 0.72 | 0.87 | 0.87 | 0.87 | 0.87 | 0.68 | 0.68 | 0.67 | 0.68 |
| P1_mfw100_all_noprop_nocull | 1.00 | 1.00 | 1.00 | 1.00 | 0.74 | 0.74 | 0.74 | 0.74 | 0.95 | 0.95 | 0.94 | 0.94 | 0.72 | 0.72 | 0.72 | 0.72 | 0.87 | 0.87 | 0.87 | 0.87 | 0.68 | 0.68 | 0.67 | 0.68 |
| P1_mfw100_all_raw_cull | 1.00 | 1.00 | 1.00 | 1.00 | 0.74 | 0.74 | 0.74 | 0.74 | 0.94 | 0.94 | 0.95 | 0.95 | 0.72 | 0.72 | 0.72 | 0.72 | 0.87 | 0.87 | 0.87 | 0.87 | 0.67 | 0.67 | 0.67 | 0.68 |
| P1_mfw100_all_raw_nocull | 1.00 | 1.00 | 1.00 | 1.00 | 0.74 | 0.74 | 0.74 | 0.74 | 0.94 | 0.94 | 0.95 | 0.95 | 0.72 | 0.72 | 0.72 | 0.72 | 0.87 | 0.87 | 0.87 | 0.87 | 0.67 | 0.67 | 0.67 | 0.68 |
| P1_mfw100_narr_noprop_cull | 0.74 | 0.74 | 0.74 | 0.74 | 1.00 | 1.00 | 0.99 | 0.99 | 0.77 | 0.77 | 0.76 | 0.76 | 0.93 | 0.93 | 0.93 | 0.93 | 0.72 | 0.72 | 0.72 | 0.72 | 0.87 | 0.87 | 0.87 | 0.87 |
| P1_mfw100_narr_noprop_nocull | 0.74 | 0.74 | 0.74 | 0.74 | 1.00 | 1.00 | 0.99 | 0.99 | 0.77 | 0.77 | 0.76 | 0.76 | 0.93 | 0.93 | 0.93 | 0.93 | 0.72 | 0.72 | 0.72 | 0.72 | 0.87 | 0.87 | 0.87 | 0.87 |
| P1_mfw100_narr_raw_cull | 0.74 | 0.74 | 0.74 | 0.74 | 0.99 | 0.99 | 1.00 | 1.00 | 0.77 | 0.77 | 0.77 | 0.77 | 0.93 | 0.93 | 0.93 | 0.93 | 0.72 | 0.72 | 0.73 | 0.73 | 0.86 | 0.86 | 0.86 | 0.87 |
| P1_mfw100_narr_raw_nocull | 0.74 | 0.74 | 0.74 | 0.74 | 0.99 | 0.99 | 1.00 | 1.00 | 0.77 | 0.77 | 0.77 | 0.77 | 0.93 | 0.93 | 0.93 | 0.93 | 0.72 | 0.72 | 0.73 | 0.73 | 0.86 | 0.86 | 0.86 | 0.87 |
| P1_mfw200_all_noprop_cull | 0.95 | 0.95 | 0.94 | 0.94 | 0.77 | 0.77 | 0.77 | 0.77 | 1.00 | 1.00 | 0.99 | 0.99 | 0.80 | 0.80 | 0.80 | 0.80 | 0.94 | 0.94 | 0.94 | 0.94 | 0.76 | 0.76 | 0.76 | 0.76 |
| P1_mfw200_all_noprop_nocull | 0.95 | 0.95 | 0.94 | 0.94 | 0.77 | 0.77 | 0.77 | 0.77 | 1.00 | 1.00 | 0.99 | 0.99 | 0.80 | 0.80 | 0.80 | 0.80 | 0.94 | 0.94 | 0.94 | 0.94 | 0.76 | 0.76 | 0.76 | 0.76 |
| P1_mfw200_all_raw_cull | 0.94 | 0.94 | 0.95 | 0.95 | 0.76 | 0.76 | 0.77 | 0.77 | 0.99 | 0.99 | 1.00 | 1.00 | 0.80 | 0.80 | 0.80 | 0.80 | 0.94 | 0.94 | 0.94 | 0.94 | 0.75 | 0.75 | 0.76 | 0.76 |
| P1_mfw200_all_raw_nocull | 0.94 | 0.94 | 0.95 | 0.95 | 0.76 | 0.76 | 0.77 | 0.77 | 0.99 | 0.99 | 1.00 | 1.00 | 0.80 | 0.80 | 0.80 | 0.80 | 0.94 | 0.94 | 0.94 | 0.94 | 0.75 | 0.75 | 0.76 | 0.76 |
| P1_mfw200_narr_noprop_cull | 0.72 | 0.72 | 0.72 | 0.72 | 0.93 | 0.93 | 0.93 | 0.93 | 0.80 | 0.80 | 0.80 | 0.80 | 1.00 | 1.00 | 0.99 | 0.99 | 0.78 | 0.78 | 0.78 | 0.78 | 0.94 | 0.94 | 0.94 | 0.94 |
| P1_mfw200_narr_noprop_nocull | 0.72 | 0.72 | 0.72 | 0.72 | 0.93 | 0.93 | 0.93 | 0.93 | 0.80 | 0.80 | 0.80 | 0.80 | 1.00 | 1.00 | 0.99 | 0.99 | 0.78 | 0.78 | 0.78 | 0.78 | 0.94 | 0.94 | 0.94 | 0.94 |
| P1_mfw200_narr_raw_cull | 0.72 | 0.72 | 0.72 | 0.72 | 0.93 | 0.93 | 0.93 | 0.93 | 0.80 | 0.80 | 0.80 | 0.80 | 0.99 | 0.99 | 1.00 | 1.00 | 0.78 | 0.78 | 0.78 | 0.78 | 0.93 | 0.93 | 0.94 | 0.94 |
| P1_mfw200_narr_raw_nocull | 0.72 | 0.72 | 0.72 | 0.72 | 0.93 | 0.93 | 0.93 | 0.93 | 0.80 | 0.80 | 0.80 | 0.80 | 0.99 | 0.99 | 1.00 | 1.00 | 0.78 | 0.78 | 0.78 | 0.78 | 0.93 | 0.93 | 0.94 | 0.94 |
| P1_mfw500_all_noprop_cull | 0.87 | 0.87 | 0.87 | 0.87 | 0.72 | 0.72 | 0.72 | 0.72 | 0.94 | 0.94 | 0.94 | 0.94 | 0.78 | 0.78 | 0.78 | 0.78 | 1.00 | 1.00 | 1.00 | 1.00 | 0.82 | 0.82 | 0.82 | 0.82 |
| P1_mfw500_all_noprop_nocull | 0.87 | 0.87 | 0.87 | 0.87 | 0.72 | 0.72 | 0.72 | 0.72 | 0.94 | 0.94 | 0.94 | 0.94 | 0.78 | 0.78 | 0.78 | 0.78 | 1.00 | 1.00 | 1.00 | 1.00 | 0.82 | 0.82 | 0.82 | 0.82 |
| P1_mfw500_all_raw_cull | 0.87 | 0.87 | 0.87 | 0.87 | 0.72 | 0.72 | 0.73 | 0.73 | 0.94 | 0.94 | 0.94 | 0.94 | 0.78 | 0.78 | 0.78 | 0.78 | 1.00 | 1.00 | 1.00 | 1.00 | 0.82 | 0.82 | 0.82 | 0.82 |
| P1_mfw500_all_raw_nocull | 0.87 | 0.87 | 0.87 | 0.87 | 0.72 | 0.72 | 0.73 | 0.73 | 0.94 | 0.94 | 0.94 | 0.94 | 0.78 | 0.78 | 0.78 | 0.78 | 1.00 | 1.00 | 1.00 | 1.00 | 0.82 | 0.82 | 0.82 | 0.82 |
| P1_mfw500_narr_noprop_cull | 0.68 | 0.68 | 0.67 | 0.67 | 0.87 | 0.87 | 0.86 | 0.86 | 0.76 | 0.76 | 0.75 | 0.75 | 0.94 | 0.94 | 0.93 | 0.93 | 0.82 | 0.82 | 0.82 | 0.82 | 1.00 | 1.00 | 1.00 | 0.99 |
| P1_mfw500_narr_noprop_nocull | 0.68 | 0.68 | 0.67 | 0.67 | 0.87 | 0.87 | 0.86 | 0.86 | 0.76 | 0.76 | 0.75 | 0.75 | 0.94 | 0.94 | 0.93 | 0.93 | 0.82 | 0.82 | 0.82 | 0.82 | 1.00 | 1.00 | 1.00 | 0.99 |
| P1_mfw500_narr_raw_cull | 0.67 | 0.67 | 0.67 | 0.67 | 0.87 | 0.87 | 0.86 | 0.86 | 0.76 | 0.76 | 0.76 | 0.76 | 0.94 | 0.94 | 0.94 | 0.94 | 0.82 | 0.82 | 0.82 | 0.82 | 1.00 | 1.00 | 1.00 | 1.00 |
| P1_mfw500_narr_raw_nocull | 0.68 | 0.68 | 0.68 | 0.68 | 0.87 | 0.87 | 0.87 | 0.87 | 0.76 | 0.76 | 0.76 | 0.76 | 0.94 | 0.94 | 0.94 | 0.94 | 0.82 | 0.82 | 0.82 | 0.82 | 0.99 | 0.99 | 1.00 | 1.00 |

Spearman between the pair distances of two blocks, different-author pairs only.

| block | P1_mfw100_all_noprop_cull | P1_mfw100_all_noprop_nocull | P1_mfw100_all_raw_cull | P1_mfw100_all_raw_nocull | P1_mfw100_narr_noprop_cull | P1_mfw100_narr_noprop_nocull | P1_mfw100_narr_raw_cull | P1_mfw100_narr_raw_nocull | P1_mfw200_all_noprop_cull | P1_mfw200_all_noprop_nocull | P1_mfw200_all_raw_cull | P1_mfw200_all_raw_nocull | P1_mfw200_narr_noprop_cull | P1_mfw200_narr_noprop_nocull | P1_mfw200_narr_raw_cull | P1_mfw200_narr_raw_nocull | P1_mfw500_all_noprop_cull | P1_mfw500_all_noprop_nocull | P1_mfw500_all_raw_cull | P1_mfw500_all_raw_nocull | P1_mfw500_narr_noprop_cull | P1_mfw500_narr_noprop_nocull | P1_mfw500_narr_raw_cull | P1_mfw500_narr_raw_nocull |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| P1_mfw100_all_noprop_cull | 1.00 | 1.00 | 1.00 | 1.00 | 0.73 | 0.73 | 0.73 | 0.73 | 0.94 | 0.94 | 0.94 | 0.94 | 0.71 | 0.71 | 0.70 | 0.70 | 0.86 | 0.86 | 0.86 | 0.86 | 0.66 | 0.66 | 0.66 | 0.66 |
| P1_mfw100_all_noprop_nocull | 1.00 | 1.00 | 1.00 | 1.00 | 0.73 | 0.73 | 0.73 | 0.73 | 0.94 | 0.94 | 0.94 | 0.94 | 0.71 | 0.71 | 0.70 | 0.70 | 0.86 | 0.86 | 0.86 | 0.86 | 0.66 | 0.66 | 0.66 | 0.66 |
| P1_mfw100_all_raw_cull | 1.00 | 1.00 | 1.00 | 1.00 | 0.73 | 0.73 | 0.73 | 0.73 | 0.94 | 0.94 | 0.94 | 0.94 | 0.71 | 0.71 | 0.70 | 0.70 | 0.86 | 0.86 | 0.86 | 0.86 | 0.66 | 0.66 | 0.66 | 0.66 |
| P1_mfw100_all_raw_nocull | 1.00 | 1.00 | 1.00 | 1.00 | 0.73 | 0.73 | 0.73 | 0.73 | 0.94 | 0.94 | 0.94 | 0.94 | 0.71 | 0.71 | 0.70 | 0.70 | 0.86 | 0.86 | 0.86 | 0.86 | 0.66 | 0.66 | 0.66 | 0.66 |
| P1_mfw100_narr_noprop_cull | 0.73 | 0.73 | 0.73 | 0.73 | 1.00 | 1.00 | 0.99 | 0.99 | 0.76 | 0.76 | 0.75 | 0.75 | 0.93 | 0.93 | 0.93 | 0.93 | 0.71 | 0.71 | 0.71 | 0.71 | 0.86 | 0.86 | 0.86 | 0.86 |
| P1_mfw100_narr_noprop_nocull | 0.73 | 0.73 | 0.73 | 0.73 | 1.00 | 1.00 | 0.99 | 0.99 | 0.76 | 0.76 | 0.75 | 0.75 | 0.93 | 0.93 | 0.93 | 0.93 | 0.71 | 0.71 | 0.71 | 0.71 | 0.86 | 0.86 | 0.86 | 0.86 |
| P1_mfw100_narr_raw_cull | 0.73 | 0.73 | 0.73 | 0.73 | 0.99 | 0.99 | 1.00 | 1.00 | 0.76 | 0.76 | 0.76 | 0.76 | 0.93 | 0.93 | 0.93 | 0.93 | 0.71 | 0.71 | 0.71 | 0.71 | 0.86 | 0.86 | 0.86 | 0.86 |
| P1_mfw100_narr_raw_nocull | 0.73 | 0.73 | 0.73 | 0.73 | 0.99 | 0.99 | 1.00 | 1.00 | 0.76 | 0.76 | 0.76 | 0.76 | 0.93 | 0.93 | 0.93 | 0.93 | 0.71 | 0.71 | 0.71 | 0.71 | 0.86 | 0.86 | 0.86 | 0.86 |
| P1_mfw200_all_noprop_cull | 0.94 | 0.94 | 0.94 | 0.94 | 0.76 | 0.76 | 0.76 | 0.76 | 1.00 | 1.00 | 0.99 | 0.99 | 0.79 | 0.79 | 0.79 | 0.79 | 0.94 | 0.94 | 0.93 | 0.94 | 0.75 | 0.75 | 0.75 | 0.75 |
| P1_mfw200_all_noprop_nocull | 0.94 | 0.94 | 0.94 | 0.94 | 0.76 | 0.76 | 0.76 | 0.76 | 1.00 | 1.00 | 0.99 | 0.99 | 0.79 | 0.79 | 0.79 | 0.79 | 0.94 | 0.94 | 0.93 | 0.94 | 0.75 | 0.75 | 0.75 | 0.75 |
| P1_mfw200_all_raw_cull | 0.94 | 0.94 | 0.94 | 0.94 | 0.75 | 0.75 | 0.76 | 0.76 | 0.99 | 0.99 | 1.00 | 1.00 | 0.78 | 0.78 | 0.79 | 0.79 | 0.93 | 0.93 | 0.93 | 0.93 | 0.74 | 0.74 | 0.74 | 0.74 |
| P1_mfw200_all_raw_nocull | 0.94 | 0.94 | 0.94 | 0.94 | 0.75 | 0.75 | 0.76 | 0.76 | 0.99 | 0.99 | 1.00 | 1.00 | 0.78 | 0.78 | 0.79 | 0.79 | 0.93 | 0.93 | 0.93 | 0.93 | 0.74 | 0.74 | 0.74 | 0.74 |
| P1_mfw200_narr_noprop_cull | 0.71 | 0.71 | 0.71 | 0.71 | 0.93 | 0.93 | 0.93 | 0.93 | 0.79 | 0.79 | 0.78 | 0.78 | 1.00 | 1.00 | 0.99 | 0.99 | 0.77 | 0.77 | 0.77 | 0.77 | 0.93 | 0.93 | 0.93 | 0.94 |
| P1_mfw200_narr_noprop_nocull | 0.71 | 0.71 | 0.71 | 0.71 | 0.93 | 0.93 | 0.93 | 0.93 | 0.79 | 0.79 | 0.78 | 0.78 | 1.00 | 1.00 | 0.99 | 0.99 | 0.77 | 0.77 | 0.77 | 0.77 | 0.93 | 0.93 | 0.93 | 0.94 |
| P1_mfw200_narr_raw_cull | 0.70 | 0.70 | 0.70 | 0.70 | 0.93 | 0.93 | 0.93 | 0.93 | 0.79 | 0.79 | 0.79 | 0.79 | 0.99 | 0.99 | 1.00 | 1.00 | 0.77 | 0.77 | 0.77 | 0.77 | 0.93 | 0.93 | 0.93 | 0.94 |
| P1_mfw200_narr_raw_nocull | 0.70 | 0.70 | 0.70 | 0.70 | 0.93 | 0.93 | 0.93 | 0.93 | 0.79 | 0.79 | 0.79 | 0.79 | 0.99 | 0.99 | 1.00 | 1.00 | 0.77 | 0.77 | 0.77 | 0.77 | 0.93 | 0.93 | 0.93 | 0.94 |
| P1_mfw500_all_noprop_cull | 0.86 | 0.86 | 0.86 | 0.86 | 0.71 | 0.71 | 0.71 | 0.71 | 0.94 | 0.94 | 0.93 | 0.93 | 0.77 | 0.77 | 0.77 | 0.77 | 1.00 | 1.00 | 1.00 | 1.00 | 0.81 | 0.81 | 0.81 | 0.80 |
| P1_mfw500_all_noprop_nocull | 0.86 | 0.86 | 0.86 | 0.86 | 0.71 | 0.71 | 0.71 | 0.71 | 0.94 | 0.94 | 0.93 | 0.93 | 0.77 | 0.77 | 0.77 | 0.77 | 1.00 | 1.00 | 1.00 | 1.00 | 0.81 | 0.81 | 0.81 | 0.80 |
| P1_mfw500_all_raw_cull | 0.86 | 0.86 | 0.86 | 0.86 | 0.71 | 0.71 | 0.71 | 0.71 | 0.93 | 0.93 | 0.93 | 0.93 | 0.77 | 0.77 | 0.77 | 0.77 | 1.00 | 1.00 | 1.00 | 1.00 | 0.81 | 0.81 | 0.81 | 0.81 |
| P1_mfw500_all_raw_nocull | 0.86 | 0.86 | 0.86 | 0.86 | 0.71 | 0.71 | 0.71 | 0.71 | 0.94 | 0.94 | 0.93 | 0.93 | 0.77 | 0.77 | 0.77 | 0.77 | 1.00 | 1.00 | 1.00 | 1.00 | 0.81 | 0.81 | 0.81 | 0.81 |
| P1_mfw500_narr_noprop_cull | 0.66 | 0.66 | 0.66 | 0.66 | 0.86 | 0.86 | 0.86 | 0.86 | 0.75 | 0.75 | 0.74 | 0.74 | 0.93 | 0.93 | 0.93 | 0.93 | 0.81 | 0.81 | 0.81 | 0.81 | 1.00 | 1.00 | 1.00 | 0.99 |
| P1_mfw500_narr_noprop_nocull | 0.66 | 0.66 | 0.66 | 0.66 | 0.86 | 0.86 | 0.86 | 0.86 | 0.75 | 0.75 | 0.74 | 0.74 | 0.93 | 0.93 | 0.93 | 0.93 | 0.81 | 0.81 | 0.81 | 0.81 | 1.00 | 1.00 | 1.00 | 0.99 |
| P1_mfw500_narr_raw_cull | 0.66 | 0.66 | 0.66 | 0.66 | 0.86 | 0.86 | 0.86 | 0.86 | 0.75 | 0.75 | 0.74 | 0.74 | 0.93 | 0.93 | 0.93 | 0.93 | 0.81 | 0.81 | 0.81 | 0.81 | 1.00 | 1.00 | 1.00 | 1.00 |
| P1_mfw500_narr_raw_nocull | 0.66 | 0.66 | 0.66 | 0.66 | 0.86 | 0.86 | 0.86 | 0.86 | 0.75 | 0.75 | 0.74 | 0.74 | 0.94 | 0.94 | 0.94 | 0.94 | 0.80 | 0.80 | 0.81 | 0.81 | 0.99 | 0.99 | 1.00 | 1.00 |

