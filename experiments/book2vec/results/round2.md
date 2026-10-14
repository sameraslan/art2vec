# Round two: World, Story, Felt and a neural Prose

Experiments 3, 4 and 5 of FRAMEWORK.md section 11, plus the style encoder that round one left
open. Same 87 public-domain novels, same harness (`eval/`), same pair sets. Story and Felt
exist only for the 24 books a language-model reader went through. Code: `world/`,
`storyblock/`, `felt/`, `prose/style_embed.py`, `prose/closed_class.py`. The one-table summary
is `all_blocks.md`. Round one is `prose_telling.md`; the reading conventions there (AUC,
intervals, split halves) apply here.

Models: `Qwen/Qwen3-Embedding-0.6B` (revision `97b0c614be4d77ee51c0cef4e5f07c00f9eb65b3`,
Apache-2.0) through sentence-transformers on MPS, float32, batch 8, 512 tokens;
`StyleDistance/styledistance` (revision `b7df5f0b0480773c097ba3121d83ca32b71015ca`, MIT), batch
16, 256 tokens. Neither had to be substituted.

Pair counts. All 87 books: 10 translation pairs, 1 edition pair, 52 same-author pairs with
unrelated plots, 7 series pairs, 8 retelling pairs, 261 same-genre pairs, 3,663 negatives. The
24-book subset: 3 translation pairs (Fathers and Sons, A Nest of Gentlefolk, Journey to the
Centre of the Earth), 1 edition pair (Frankenstein 1818 / 1831), 1 retelling (Sara Crewe / A
Little Princess), 3 series pairs (Holmes, Oz, Tarzan), 5 same-author pairs (Wells x1; Turgenev
x4, which are the four crossings of the two translated novels and so are not four independent
facts), 26 same-genre pairs, 263 negatives. On the subset an AUC is the mean of three or five
numbers; the per-pair ranks are given for that reason.

## Headline

1. **World from name-masked passages passes its row.** `W1_qwen_maskB_c` (40 chunks per book,
   mean, centred): translations 1.00, series 0.99, split halves 0.96 / 0.91. It is also near
   for retellings (0.98) and for two unrelated novels by one author (0.91 [0.88, 0.94]), which
   the framework hoped it would not especially be.
2. **Names were doing work, and only for the translated Russians.** With names left in, two
   books by different authors translated by Garnett score 0.98; with person names masked,
   0.70; with places masked too, 0.65. English-language same-author pairs do not move (0.89
   clean, 0.93 masked). Masking places adds almost nothing to masking persons (Spearman 0.99
   between the two).
3. **The Story block cannot be told apart from recall on these books.** A block built from
   digests the same model wrote from the title alone passes every pair test the from-text
   block passes. Details and the honest reading are under "Leak".
4. **Story fails "same author, unrelated plots: apart"** (0.99, 5 pairs), and so does every
   other block on the subset. Four of the five pairs are Turgenev's two gentry novels.
5. **A content-controlled style encoder does put translations apart**, which no count-based
   Prose measure did: translation AUC 0.68 [0.47, 0.85] against 1.00, and a translation pair
   is closer than a same-author pair with probability 0.40 (0.76 for P4). The price is a much
   weaker author signal (0.77 against 0.99) and split-half accuracy of 0.70.
6. **Felt from the reader is consistent between two readings of one work** (Pearson 0.65 to
   0.84 after removing the shared profile; negatives -0.07) and is also almost the same as
   felt from the title alone (0.76). A no-reader projection of passage embeddings onto the 24
   words agrees with the reader moderately (mean Spearman per word 0.46 to 0.50).

## Experiment W: World

### What was built

| Block | What it is |
|---|---|
| `W0_tfidf_{maskB,clean}` | TF-IDF book bag (sublinear tf, word in at least 2 books and at most 95% of them), stand-ins removed, cosine. `_nostop` drops English stop words and is identical to two decimals |
| `W1_qwen_{maskB,maskA,clean}_{raw,c,pc1,pc2}` | 40 evenly spaced ~1,000-word chunks per book (3,445 in all), each cut to 512 tokens, embedded without an instruction. raw = mean; c = corpus mean subtracted, L2-normalised; pc1 / pc2 = first one / two principal directions removed as well |
| `W1_qwen_maskB_instr_*` | the same with the prefix "Represent the setting, period and subject matter of this passage of fiction" |

Per-chunk matrices are in `data/emb/<name>/<key>.npy` with the chunk idx beside them.
Timing: 24 chunks took 11 s including warm-up; a 3,445-chunk variant took 17 to 23 minutes.

### Reading

| | translation (10) | same author (52) | ... English originals (33) | ... translated, different translators (14) | series (7) | retelling (8) | same translator, different author (11) | same genre (261) | split a/b, h1/h2 |
|---|---|---|---|---|---|---|---|---|---|
| `W0_tfidf_clean` | 1.00 | 0.93 | 0.92 | 0.95 | 0.98 | 0.96 | 0.90 | 0.54 | 0.93, 0.96 |
| `W0_tfidf_maskB` | 1.00 | 0.92 | 0.90 | 0.95 | 0.94 | 0.94 | 0.90 | 0.53 | 0.93, 0.90 |
| `W1_qwen_clean_c` | 1.00 | 0.93 | 0.89 | 0.99 | 1.00 | 0.98 | 0.98 | 0.81 | 0.93, 0.91 |
| `W1_qwen_maskA_c` | 1.00 | 0.92 | 0.93 | 0.89 | 0.99 | 0.97 | 0.70 | 0.80 | |
| `W1_qwen_maskB_c` | 1.00 | 0.91 | 0.93 | 0.86 | 0.99 | 0.98 | 0.65 | 0.80 | 0.96, 0.91 |
| `W1_qwen_maskB_raw` | 0.98 | 0.82 | 0.87 | 0.69 | 0.98 | 0.67 | 0.78 | 0.65 | 0.95, 0.91 |
| `W1_qwen_maskB_pc1` | 1.00 | 0.90 | 0.91 | 0.84 | 0.99 | 0.92 | 0.62 | 0.62 | 0.96, 0.93 |
| `W1_qwen_maskB_instr_c` | 1.00 | 0.91 | 0.92 | 0.87 | 1.00 | 0.97 | 0.72 | 0.81 | 0.94, 0.82 |

- **Centring matters; removing principal components does harm.** Raw means sit in a narrow
  cone: retelling 0.67, genre 0.65, one book in 25 top-5 lists. Centring lifts retelling to
  0.98 and genre to 0.80 and halves the hubness. The first principal direction of the centred
  book vectors (20% of the variance) runs from Austen, James and Wharton to Verne, Defoe and
  Wyss: drawing rooms against survival and voyages. That is World content, and projecting it
  out drops same-genre from 0.80 to 0.62. Use `_c`.
- **Clean against masked.** Translation, series and retelling pairs do not need names (all
  0.97 or more masked). What names bought was a "Russian novel" cluster: same translator /
  different author 0.98 to 0.65 (paired difference -0.32 [-0.40, -0.23]) and translated
  same-author pairs 0.99 to 0.86 (-0.13 [-0.19, -0.07]). With names in, the nearest
  not-same-work neighbour of a Garnett book is another Garnett book by a different author in 3
  of 6 cases; masked, in 0 of 6. English same-author pairs rise a little when masked (+0.04
  [+0.01, +0.07]). Series pairs lose 0.01. So the framework's rule (mask before World) is
  supported: the masked block is the one that compares settings and subjects.
- **TF-IDF is a strong baseline on the labelled pairs and a poor World.** It matches the
  encoder on translation, author and retelling pairs, but same-genre is 0.53 (chance), it has
  one hub in 34 top-5 lists, and its Spearman with Prose is the highest of the World
  candidates (0.47). It is closer to a second Prose block than to a World block. Masking
  barely changes it because a name must occur in two books to count at all.
- **Instruction prefix: no measurable effect.** Spearman 0.93 with the uninstructed block;
  every pair-set difference is inside its interval except same-translator (+0.07 [+0.01,
  +0.13], the wrong direction); h1/h2 accuracy falls from 0.91 to 0.82.
- **Same author.** World puts two unrelated novels by one author at 0.91. With Prose regressed
  out it is 0.75, so part is shared manner and most is that authors return to their settings
  and subjects (Austen, Hardy, Verne). 30% of top-5 neighbours share the author (chance 2%),
  against 40% for Prose. I read this as correct behaviour that the framework's table should
  not call a failure.
- **How much of World is Prose.** Spearman with `P4_mfw500_tag3_rhythm` is 0.40 over all pairs
  and 0.37 over different-author pairs (0.34 / 0.30 for clean). About 15% of rank variance.
  With Prose regressed out World keeps translation 0.86, series 0.85, retelling 0.89, genre
  0.78.
- **Period and length.** Spearman with year difference 0.03 (English originals, different
  authors); with word-count difference 0.03. Neither is in the block.

### Sampling convergence

Twelve books of 158 to 199 chunks, every chunk embedded; k evenly spaced chunks with a random
phase, 5 draws.

| chunks | cosine with all-chunk vector, raw | ... centred | Spearman of distances to the other 86 | top-5 overlap | same nearest book | worst centred cosine |
|---|---|---|---|---|---|---|
| 5 | 0.927 | 0.688 | 0.808 | 0.66 | 0.65 | 0.358 |
| 10 | 0.965 | 0.815 | 0.907 | 0.76 | 0.73 | 0.650 |
| 20 | 0.984 | 0.901 | 0.948 | 0.81 | 0.82 | 0.738 |
| 40 | 0.993 | 0.954 | 0.981 | 0.88 | 0.95 | 0.900 |
| 80 | 0.998 | 0.984 | 0.991 | 0.94 | 0.93 | 0.964 |

Raw cosines flatter the picture; after centring, 10 chunks is not enough (0.82) and 40 is
adequate (0.95; nearest neighbour unchanged in 95% of draws). 40 chunks cut to 512 tokens is
about 15,000 words read per book.

### Why two books are neighbours

`world_why.md`: The Mysteries of Udolpho and The Monk are mutual nearest neighbours by
different authors. The three closest chunk pairs are a convent visit against an abbot
receiving a visitor, a torch-lit descent into a ruined chapel against a night flight with a
lamp and a key, and inset verse against inset verse. The other mutual pairs are Persuasion /
Old Friends and New Fancies (an Austen pastiche), The Ambassadors / The House of Mirth, The
Time Machine / We, Styles / The Maltese Falcon, The Mayor of Casterbridge / Ethan Frome.

## Experiment S: Story (24 books)

### What was built

`S_story`, `S_characters`, `S_storychar` (the two unit vectors side by side), `W_digest` (the
reader's world field), each as `_plain` (Qwen3, no instruction), `_inst` ("Represent the plot
of this story: what happens and how it ends") and `_tfidf`; centred across the 24 books.
`SM_*`, `WM_*`: the same from the title-only digests (23 books).

### Pair tests

Every variant puts every same-work pair at rank 1 in both directions; the full per-pair table
for 12 variants is under "Full tables". Instruction against none: no difference that three
pairs can show. Against the other blocks on the same 24 books (rank of b from a / rank of a
from b among the 23 other books; share of negatives farther in brackets):

| set | pair | Prose P4 | Telling T3 | World W1 | Story | Felt (reader) |
|---|---|---|---|---|---|---|
| translation | fathers garnett ~ hogarth | 3 / 1 (0.99) | 1 / 1 (1.00) | 1 / 1 (1.00) | 1 / 1 (1.00) | 2 / 3 (0.99) |
| translation | gentlefolk garnett ~ ralston | 1 / 1 (1.00) | 1 / 1 (1.00) | 1 / 1 (1.00) | 1 / 1 (1.00) | 2 / 2 (1.00) |
| translation | journey 1871 ~ malleson | 1 / 1 (1.00) | 1 / 1 (1.00) | 1 / 1 (1.00) | 1 / 1 (1.00) | 1 / 1 (0.99) |
| edition | frankenstein 1818 ~ 1831 | 1 / 1 (1.00) | 1 / 1 (1.00) | 1 / 1 (1.00) | 1 / 1 (1.00) | 1 / 1 (1.00) |
| retelling | princess ~ sara crewe | 1 / 1 (1.00) | 3 / 1 (0.99) | 1 / 1 (1.00) | 1 / 1 (1.00) | 1 / 1 (1.00) |
| series | holmes hound ~ study | 1 / 1 (1.00) | 10 / 19 (0.33) | 1 / 1 (1.00) | 2 / 3 (0.98) | 3 / 1 (0.98) |
| series | oz land ~ wizard | 1 / 1 (0.99) | 3 / 4 (0.91) | 1 / 1 (1.00) | 1 / 1 (1.00) | 1 / 1 (1.00) |
| series | tarzan apes ~ return | 1 / 1 (1.00) | 9 / 8 (0.68) | 1 / 1 (1.00) | 1 / 1 (0.99) | 1 / 1 (1.00) |
| same author | fathers garnett ~ gentlefolk garnett | 1 / 2 (1.00) | 3 / 4 (0.96) | 2 / 2 (0.93) | 2 / 2 (0.99) | 3 / 3 (0.99) |
| same author | fathers garnett ~ gentlefolk ralston | 2 / 2 (1.00) | 7 / 8 (0.83) | 3 / 2 (0.89) | 3 / 2 (0.99) | 1 / 1 (1.00) |
| same author | fathers hogarth ~ gentlefolk garnett | 4 / 3 (0.84) | 2 / 5 (0.95) | 2 / 3 (0.91) | 2 / 3 (0.98) | 1 / 1 (1.00) |
| same author | fathers hogarth ~ gentlefolk ralston | 2 / 3 (0.94) | 7 / 12 (0.68) | 3 / 4 (0.79) | 3 / 3 (0.98) | 2 / 3 (1.00) |
| same author | wells time ~ worlds | 1 / 1 (1.00) | 4 / 19 (0.37) | 2 / 1 (1.00) | 1 / 1 (0.98) | 3 / 6 (0.90) |

- **Translations near, retelling near: yes**, for Story and for everything else. On this
  subset the tests do not separate Story from World or from Prose.
- **Same author apart: no.** Story ranks Turgenev's other novel second or third after the
  other translation, and the two Wells romances first. Reading the digests, that is a fair
  account of the plots (a returning man, a provincial estate, a love that fails; a lone
  narrator among a hostile non-human species), so the block is behaving, and the framework's
  cell assumes same-author plots are unrelated when in this subset they are not. Five pairs
  from two authors cannot settle it. A fair test needs authors with visibly different plots
  who were both read (Austen and Dickens were not).
- **Series only as near as the plots are:** the Holmes pair is the least close of the three
  series in Story (2 / 3), behind another detective novel in one direction, and Telling puts
  it far (10 / 19) because A Study in Scarlet has a long third-person inset. That is the
  direction the framework asks for.
- **Story is not Prose again:** Spearman with P4 0.31 (0.21 for different-author pairs); with
  World 0.56. Same-genre AUC 0.82, the highest of any block with World (0.87).
- **TF-IDF of the digests** does as well on every labelled pair and has no genre signal
  (0.57): with names removed the digests of one work still share rare words (nihilist, crater,
  attic).

### Leak

Twenty-three of 24 readers named their book, 21 of them within the first part, in spite of
masking; the clues they report are premises, prefaces, subtitles and names the masking
missed. The one not recognised is the fame control (`merriman_barlasch`).

**(a) The from-text digest retrieves its own title-only digest.** Of the 23 books with a
title-only digest, the from-text story digest is nearer to its own title-only digest than to
any other book's (same-work partners left out) for 22; the exception is The Return of Tarzan,
where the model's memory was "partial". Centred cosine to its own 0.54 on average, to others
-0.05. For the world field 22 of 23, characters 19 of 23.

**(b) Two readings of one work against memory** (story field, centred cosine):

| pair | reading a ~ reading b | a ~ own title digest | b ~ own title digest | title a ~ title b |
|---|---|---|---|---|
| fathers garnett ~ hogarth | 0.68 | 0.50 | 0.44 | 0.81 |
| gentlefolk garnett ~ ralston | 0.60 | 0.42 | 0.57 | 0.76 |
| journey 1871 ~ malleson | 0.81 | 0.57 | 0.49 | 0.77 |
| frankenstein 1818 ~ 1831 | 0.46 | 0.43 | 0.61 | 0.79 |
| princess ~ sara crewe | 0.67 | 0.67 | 0.54 | 0.76 |

The two readings agree with each other more than with either title-only digest in 3 of 5
pairs for the story field, 4 of 5 for characters and 2 of 5 for world. So the text adds
detail that memory did not supply: the from-text digests are longer on the middle of the
plot. But two title-only digests of the same work agree with each other at least as well
(0.76 to 0.81) as two readings do (0.46 to 0.81).

**(c) A block built only from title-only digests passes the same tests** (23 books):

| block | translation (3) | edition (1) | retelling (1) | series (3) | same author (5) | same genre (24) |
|---|---|---|---|---|---|---|
| `S_story_plain` (from text) | 1.00 | 1.00 | 1.00 | 0.98 | 0.98 | 0.84 |
| `SM_story_plain` (title only) | 1.00 | 1.00 | 1.00 | 0.97 | 0.94 | 0.83 |
| `S_storychar_plain` | 1.00 | 1.00 | 1.00 | 0.99 | 0.99 | 0.83 |
| `SM_storychar_plain` | 1.00 | 1.00 | 1.00 | 0.97 | 0.94 | 0.79 |
| `W_digest_plain` | 1.00 | 1.00 | 0.99 | 0.90 | 0.98 | 0.60 |
| `WM_digest_plain` | 1.00 | 1.00 | 1.00 | 0.84 | 1.00 | 0.67 |
| `F_reader` | 0.99 | 1.00 | 1.00 | 0.99 | 0.97 | 0.77 |
| `FM_title` | 1.00 | 1.00 | 1.00 | 0.97 | 0.99 | 0.80 |

Every same-work pair is rank 1 / 1 in the title-only blocks. Spearman between from-text and
title-only pair similarities over all pairs: 0.61 for story, 0.53 characters, 0.56 world.

**Reading.** On famous books the Story block as tested cannot be distinguished from recall.
The pair tests are passed equally by a model that never saw the text. The from-text digests
are not copies of memory (they agree with each other beyond what memory explains in most
pairs, and 60% of the rank variance of Story distances is not predicted by the title-only
distances), but nothing here shows that the extra part is what finds the pairs. The single
unrecognised book cannot carry the argument: its Story neighbours are the two Garnett
Turgenevs and a detective novel, which is not obviously wrong for a novel of the 1812
retreat and not obviously right. What would settle it: books the model does not know (recent
or obscure public-domain fiction, or the fame controls, in pairs: two translations of an
unknown novel), or the same pair tests with a reader that has no memory of the canon. Until
then Story should be labelled as a reading that may be partly recall, and its pair-test
results should not be quoted as evidence that reading from pieces works.

### The reader's telling field against the counts

`telling_reader_vs_counts.md`. The reader called 9 books first-person, 9 third and 6 mixed.
Counted first-singular pronouns in narration separate first from third perfectly (27.7 to
75.5 per 1,000 words against 0.0 to 0.6; AUC 1.00). The six "mixed" books have 0.5 to 19.6. Two
really are mixed (A Study in Scarlet, 19.6, with its third-person inset; Ethan Frome, 8.1,
with its first-person frame). The other four (Oz, The Secret Agent, A Little Princess,
Tarzan of the Apes; 0.5 to 2.0) are third-person narration with an author's preface or a
short first-person opening, which the reader also reports as "framed". So the
reader's person label agrees with the count wherever it commits, and its "mixed / framed"
partly records front matter that the prep kept. The reader has no dialogue-share field; the
counted share is unrelated to the person label (0.40 first, 0.35 third). Two readings of one
work give the same person / frame / order for both Turgenevs and Frankenstein and differ for
Journey (framed against letters) and the Burnett pair (the longer book has a preface).

## Experiment F: Felt (24 books)

- **The scale is used.** From text: 14% zeros, 39% ones, 36% twos, 12% threes; mean 1.45;
  per-book sd 0.83. Title-only readers use more zeros (38%). Two words barely vary (serene,
  cosy: never above 2, mostly 0 or 1) and "tense" is 2 or 3 for 22 of 24 books.
- **Two readings of one work agree.** Exact agreement on 71% to 83% of the 24 words (33% for
  the median negative pair); Pearson after z-scoring each word across books 0.65, 0.76, 0.68
  (translations), 0.84 (editions), 0.84 (retelling), against -0.07 for negatives. The partner
  is the nearest or second or third nearest book.
- **But Felt mostly ranks same-author and series books just as near** (Turgenev crossings
  0.68 to 0.78, Oz 0.82), and the partner translation is rank 2 or 3, behind the author's
  other novel, for both Turgenevs. Felt is coarse: it finds the kind of book.
- **From text against title only:** Pearson (z) 0.76 on average, exact agreement 48%, own
  title-only vector nearest for 17 of 23. The `FM_title` block passes the pair tests as well
  as `F_reader`, and their pair distances correlate at 0.84. The leak verdict for Story holds
  for Felt at least as strongly.
- **Cross-block (24 books, all pairs):** Felt with Prose 0.25, Telling 0.18, World 0.50, Story
  0.46. With different-author pairs only: 0.15, 0.10, 0.43, 0.37.

### Felt without a reader

`felt/project.py`: cosine of each maskB chunk embedding (the W1 ones, 40 or 20 per book) to
the embedding of "A passage that feels bleak." (plain) or the bare word behind a retrieval
instruction (inst), averaged per book, z-scored per word over the 87 books.

| projection | mean Spearman per word (24 books) | words above 0.4 | mean Spearman per book, both z-scored | against another book's reader scores | split a/b (87 books) |
|---|---|---|---|---|---|
| plain, 40 chunks | 0.46 | 15 | 0.54 | -0.02 | 0.48 |
| plain, 20 chunks | 0.44 | 11 | 0.51 | -0.02 | 0.27 |
| inst, 40 chunks | 0.50 | 17 | 0.49 | -0.02 | 0.51 |
| inst, 20 chunks | 0.48 | 16 | 0.47 | -0.02 | |

It works for about two thirds of the words (tender 0.80, wistful 0.76, solemn 0.72, cosy
0.72, eerie 0.69 to 0.81, dreamlike, melancholy, disorienting, desolate above 0.6) and fails
for the ones that describe what the reading does and not what the passage shows: playful
0.04, exhilarating 0.10, lush 0.09, funny 0.17, tense 0.30. As a block over 87 books it is
weak and unstable: translations 0.90 [0.74, 0.99], split halves 0.48, and it is 0.40
correlated with World. So a passage projection can stand in for a reader on atmosphere words
and not on effect words, and 40 chunks is too few for a stable vector. Since the reader's
felt scores are themselves 0.76 predictable from the title, the projection is the only felt
measurement here that is certainly made from the text.

## Experiment P5: a style encoder, and a closed-class control

`P5_style_{clean,maskA}_*`: 60 passages of 120 words per book at evenly spaced positions,
StyleDistance, mean, centred. `P6_closed_nopron`: Cosine Delta on a fixed list of 161
determiners, prepositions, conjunctions, auxiliaries and non-personal pronouns;
`P6_closed_pron` adds 35 personal and possessive pronouns; `P6_pron_only` is those alone.

| | translation (10) | same author (52) | series (7) | retelling (8) | same genre (261) | split a/b, h1/h2 | year (en, diff. authors) | P(translation pair closer than same-author pair) | author beats translator (14 v 11) | median d translation / same-author |
|---|---|---|---|---|---|---|---|---|---|---|
| `P4_mfw500_tag3_rhythm` | 1.00 [1.00, 1.00] | 0.99 | 1.00 | 0.73 | 0.61 | 0.97, 0.91 | 0.31 | 0.76 | 0.75 | 0.70 |
| `P3_rhythm` | 0.87 [0.72, 0.99] | 0.90 | 0.85 | 0.50 | 0.51 | 0.97, 0.85 | 0.24 | 0.58 | 0.75 | 0.80 |
| `P5_style_clean_raw` | 0.41 [0.25, 0.59] | 0.76 | 0.87 | 0.43 | 0.55 | 0.74, 0.62 | 0.20 | | | |
| `P5_style_clean_c` | 0.68 [0.48, 0.85] | 0.77 [0.69, 0.84] | 0.94 | 0.71 | 0.57 | 0.70, 0.63 | 0.21 | 0.40 | 0.42 | 1.25 |
| `P5_style_clean_pc1` | 0.78 [0.61, 0.92] | 0.78 | 0.91 | 0.47 | 0.56 | 0.75, 0.66 | 0.10 | 0.54 | 0.51 | 0.96 |
| `P5_style_maskA_c` | 0.68 [0.47, 0.85] | 0.77 | 0.94 | 0.70 | 0.56 | 0.71, 0.61 | 0.22 | 0.39 | 0.44 | 1.21 |
| `P6_closed_nopron` | 0.99 [0.97, 1.00] | 0.97 | 1.00 | 0.90 | 0.63 | 0.93, 0.88 | 0.20 | 0.63 | 0.34 | 0.68 |
| `P6_closed_pron` | 1.00 [0.99, 1.00] | 0.98 | 1.00 | 0.92 | 0.65 | 0.95, 0.89 | 0.19 | 0.75 | 0.35 | 0.62 |
| `P6_pron_only` | 1.00 [1.00, 1.00] | 0.87 | 0.92 | 0.84 | 0.65 | 0.68, 0.52 | 0.03 | 0.97 | 0.66 | 0.15 |

- **The style encoder behaves as the framework expected.** Two translations of one novel are
  no closer than a same-author pair (0.40; median translation-pair distance is 1.25 times the
  same-author median), and against negatives they sit at 0.68 with an interval that includes
  chance (0.41 before centring). Masking names changes nothing (Spearman 0.99 between clean
  and maskA).
- **It is a weaker instrument.** Same-author 0.77 against 0.99; a book's other half is its
  nearest for 70% of books against 97%; 16% of top-5 neighbours share the author against 40%.
  For the six Garnett books the nearest not-same-work neighbour shares neither author nor
  translator in 5 cases, and author does not beat translator (0.42). It is trained on short
  synthetic paraphrase contrasts, and 60 passages of 120 words is 7,200 words per book; more
  passages would help the split halves, but round one's counts reached 0.94 at 5,000 words.
- **Retelling:** 0.71 [0.52, 0.86], formally a fail of "apart" (the interval clears 0.5 by
  0.02), driven by the Robinsonades as in round one.
- **Pronouns are a large part of why count-based Prose joins translations.** Pronouns alone
  make a translation pair closer than a same-author pair with probability 0.97 and distance
  ratio 0.15: they record the cast and the person of the narration, which belong to the work.
  Taking them and every open-class word out lowers the figure from 0.85 (500 words) to 0.63,
  and translation pairs are still at 0.99 against negatives. So removing pronouns moves
  translations in the expected direction and does not pull them apart; closed-class syntax
  still follows the source text. It also flips the author-or-translator contest: on closed
  class words Garnett's hand beats the original author (0.34), where the 500-word list had
  the author ahead (0.75). The author signal in the longer list was partly content.
- **What I would do:** keep P4 as the Prose measurement and report the style encoder beside
  it as a second, lower-confidence view; and change the framework's cell. "Two translations:
  Prose apart" is true only for a measure that is deliberately blind to content and that is
  also much less sure of authors.

## What worked, what failed

Worked: World from masked passages (every "near" cell, split halves, no period or length
leak); centring; the masking contrast; 40-chunk sampling; reader agreement between two
readings (Story and Felt); the reader's person label against counts; the style encoder on the
translation row.

Failed or within noise: instruction prefix (no effect); principal-component removal (removes
genre); TF-IDF as World (no genre signal, hubs); Story "same author apart" (0.99); any
separation of Story from recall; the felt projection as a stable 87-book block (split halves
0.48); style encoder as an author measure. Everything on the 24-book subset rests on 1 to 5
pairs.

## Reproduce

    .venv/bin/python -m world.tfidf
    caffeinate -i .venv/bin/python -m world.embed --variant maskB --name qwen_maskB
    caffeinate -i .venv/bin/python -m world.embed --variant clean --name qwen_clean
    caffeinate -i .venv/bin/python -m world.embed --variant maskA --name qwen_maskA
    caffeinate -i .venv/bin/python -m world.embed --variant maskB --name qwen_maskB_instr --instruction world
    caffeinate -i .venv/bin/python -m world.embed --variant maskB --name qwen_maskB_all --per-book 0 --only $(.venv/bin/python -m world.convergence --pick)
    .venv/bin/python -m world.build qwen_maskB qwen_clean qwen_maskA qwen_maskB_instr
    .venv/bin/python -m world.convergence; .venv/bin/python -m world.why --a radcliffe_udolpho --b lewis_monk
    .venv/bin/python -m world.vs_prose P4_mfw500_tag3_rhythm BLOCK ... --tag world_vs_prose
    caffeinate -i .venv/bin/python -m storyblock.embed
    .venv/bin/python -m storyblock.build; .venv/bin/python -m storyblock.leak
    .venv/bin/python -m storyblock.subset BLOCK ... --tag NAME [--drop merriman_barlasch]
    .venv/bin/python -m storyblock.telling_check
    .venv/bin/python -m felt.build; .venv/bin/python -m felt.project
    caffeinate -i .venv/bin/python -m prose.style_embed --variant clean --name style_clean
    caffeinate -i .venv/bin/python -m prose.style_embed --variant maskA --name style_maskA
    .venv/bin/python -m world.build style_clean style_maskA --prefix P5 --model StyleDistance/styledistance
    .venv/bin/python -m prose.closed_class
    .venv/bin/python -m prose.translator BLOCK ... --tag p5_translator
    .venv/bin/python -m storyblock.all_blocks --prose P4_mfw500_tag3_rhythm --prose2 P5_style_clean_c --telling T3_scalars_dtw20_sd --world W1_qwen_maskB_c --story S_storychar_plain --felt F_reader --felt87 F_proj_plain

One process at a time, one model loaded at a time. Embedding runs resume from
`data/emb/<name>/<key>.npy`. Measured on the shared 16 GB M1 Pro: Qwen3 about 0.3 to 0.4 s per
512-token chunk on MPS (17 to 23 minutes per 3,445-chunk variant, 12 minutes for the 2,158
all-chunk set); StyleDistance about 90 to 120 s per 5,220-passage variant; the embedding
process held about 2.7 GB; system free memory stayed between 25% and 58%.

# Full tables


## All blocks against the framework's pair types

Blocks: Prose = `P4_mfw500_tag3_rhythm`, Prose (style encoder) = `P5_style_clean_c`, Telling = `T3_scalars_dtw20_sd`, World = `W1_qwen_maskB_c`, Story = `S_storychar_plain`, Felt = `F_reader`, Felt (no reader) = `F_proj_plain`.

Each cell: AUC that a labelled pair is closer than a negative pair [95% bootstrap interval over the labelled pairs], number of pairs, what FRAMEWORK.md section 9 expects, and the mark (rules in `storyblock/all_blocks.py`: near passes when the interval is above 0.5; apart fails when the interval is above 0.5; fewer than 3 pairs is always WITHIN-NOISE). The framework sets no expectation for Felt or for empty cells.

### Best variant of each block (Prose, Telling, World on 87 books, 3663 negatives; Story and Felt on the 24-book reader subset, 263 negatives)

| pair type | Prose | Prose (style encoder) | Telling | World | Story (24 books) | Felt (24 books) |
|---|---|---|---|---|---|---|
| Two halves of one book (a/b) | accuracy 0.97, 87 books (expects near) PASS | accuracy 0.70, 87 books (expects near) PASS | accuracy 0.74, 87 books (expects near) PASS | accuracy 0.96, 87 books (expects near) PASS | not defined | not defined |
| Two translations of one novel | 1.00 [1.00, 1.00], n=10 (expects apart) FAIL | 0.68 [0.47, 0.85], n=10 (expects apart) PASS | 0.99 [0.97, 1.00], n=10 (expects near) PASS | 1.00 [1.00, 1.00], n=10 (expects near) PASS | 1.00 [1.00, 1.00], n=3 (expects near) PASS | 0.99 [0.99, 1.00], n=3 |
| Two editions of one novel | 1.00, n=1 | 1.00, n=1 | 1.00, n=1 | 1.00, n=1 | 1.00, n=1 | 1.00, n=1 |
| Two novels by one author, unrelated plots | 0.99 [0.98, 0.99], n=52 (expects near) PASS | 0.77 [0.69, 0.84], n=52 (expects near) PASS | 0.72 [0.64, 0.78], n=52 | 0.91 [0.88, 0.94], n=52 | 0.99 [0.98, 0.99], n=5 (expects apart) FAIL | 0.98 [0.94, 1.00], n=5 |
| Two books of one series | 1.00 [0.99, 1.00], n=7 (expects near) PASS | 0.94 [0.88, 0.98], n=7 (expects near) PASS | 0.78 [0.62, 0.92], n=7 (expects near) PASS | 0.99 [0.97, 1.00], n=7 (expects near) PASS | 0.99 [0.98, 1.00], n=3 | 0.99 [0.98, 1.00], n=3 |
| A retelling and its source | 0.73 [0.44, 0.95], n=8 (expects apart) PASS | 0.71 [0.52, 0.86], n=8 (expects apart) FAIL | 0.45 [0.23, 0.68], n=8 | 0.98 [0.93, 1.00], n=8 | 1.00, n=1 (expects near) WITHIN-NOISE | 1.00, n=1 |
| Same genre, different authors (control) | 0.61 [0.57, 0.65], n=261 | 0.57 [0.53, 0.60], n=261 | 0.52 [0.49, 0.56], n=261 | 0.80 [0.78, 0.82], n=261 | 0.82 [0.76, 0.89], n=26 | 0.73 [0.62, 0.83], n=26 |

### The same five blocks on the 24-book subset only (263 negatives)

| pair type | Prose | Prose (style encoder) | Telling | World | Story | Felt | Felt (no reader) |
|---|---|---|---|---|---|---|---|
| Two halves of one book (a/b) | accuracy 0.88, 24 books (expects near) PASS | accuracy 0.92, 24 books (expects near) PASS | accuracy 0.71, 24 books (expects near) PASS | accuracy 0.94, 24 books (expects near) PASS | not defined | not defined | accuracy 0.65, 24 books  |
| Two translations of one novel | 1.00 [0.99, 1.00], n=3 (expects apart) FAIL | 0.28 [0.03, 0.70], n=3 (expects apart) PASS | 1.00 [1.00, 1.00], n=3 (expects near) PASS | 1.00 [1.00, 1.00], n=3 (expects near) PASS | 1.00 [1.00, 1.00], n=3 (expects near) PASS | 0.99 [0.99, 1.00], n=3 | 0.70 [0.15, 1.00], n=3 |
| Two editions of one novel | 1.00, n=1 | 0.99, n=1 | 1.00, n=1 | 1.00, n=1 | 1.00, n=1 | 1.00, n=1 | 1.00, n=1 |
| Two novels by one author, unrelated plots | 0.96 [0.89, 1.00], n=5 (expects near) PASS | 0.50 [0.17, 0.82], n=5 (expects near) WITHIN-NOISE | 0.76 [0.55, 0.93], n=5 | 0.90 [0.84, 0.96], n=5 | 0.99 [0.98, 0.99], n=5 (expects apart) FAIL | 0.98 [0.94, 1.00], n=5 | 0.71 [0.51, 0.90], n=5 |
| Two books of one series | 1.00 [0.99, 1.00], n=3 (expects near) PASS | 0.89 [0.84, 0.99], n=3 (expects near) PASS | 0.64 [0.33, 0.91], n=3 (expects near) WITHIN-NOISE | 1.00 [1.00, 1.00], n=3 (expects near) PASS | 0.99 [0.98, 1.00], n=3 | 0.99 [0.98, 1.00], n=3 | 0.84 [0.68, 0.95], n=3 |
| A retelling and its source | 1.00, n=1 (expects apart) WITHIN-NOISE | 0.52, n=1 (expects apart) WITHIN-NOISE | 0.99, n=1 | 1.00, n=1 | 1.00, n=1 (expects near) WITHIN-NOISE | 1.00, n=1 | 0.92, n=1 |
| Same genre, different authors (control) | 0.70 [0.60, 0.80], n=26 | 0.63 [0.53, 0.72], n=26 | 0.65 [0.55, 0.75], n=26 | 0.87 [0.82, 0.92], n=26 | 0.82 [0.76, 0.89], n=26 | 0.73 [0.62, 0.83], n=26 | 0.73 [0.65, 0.81], n=26 |

### Cross-block Spearman of pair distances

24-book subset, all 276 pairs.

| block | Prose | Prose (style encoder) | Telling | World | Story | Felt | Felt (no reader) |
|---|---|---|---|---|---|---|---|
| Prose | 1.00 | 0.40 | 0.39 | 0.56 | 0.31 | 0.25 | 0.26 |
| Prose (style encoder) | 0.40 | 1.00 | 0.21 | 0.31 | 0.07 | 0.04 | 0.05 |
| Telling | 0.39 | 0.21 | 1.00 | 0.22 | 0.29 | 0.18 | 0.13 |
| World | 0.56 | 0.31 | 0.22 | 1.00 | 0.56 | 0.50 | 0.54 |
| Story | 0.31 | 0.07 | 0.29 | 0.56 | 1.00 | 0.46 | 0.38 |
| Felt | 0.25 | 0.04 | 0.18 | 0.50 | 0.46 | 1.00 | 0.41 |
| Felt (no reader) | 0.26 | 0.05 | 0.13 | 0.54 | 0.38 | 0.41 | 1.00 |

24-book subset, different-author pairs only.

| block | Prose | Prose (style encoder) | Telling | World | Story | Felt | Felt (no reader) |
|---|---|---|---|---|---|---|---|
| Prose | 1.00 | 0.42 | 0.34 | 0.50 | 0.21 | 0.15 | 0.21 |
| Prose (style encoder) | 0.42 | 1.00 | 0.23 | 0.32 | 0.05 | 0.02 | 0.03 |
| Telling | 0.34 | 0.23 | 1.00 | 0.15 | 0.23 | 0.10 | 0.09 |
| World | 0.50 | 0.32 | 0.15 | 1.00 | 0.49 | 0.43 | 0.52 |
| Story | 0.21 | 0.05 | 0.23 | 0.49 | 1.00 | 0.37 | 0.34 |
| Felt | 0.15 | 0.02 | 0.10 | 0.43 | 0.37 | 1.00 | 0.37 |
| Felt (no reader) | 0.21 | 0.03 | 0.09 | 0.52 | 0.34 | 0.37 | 1.00 |

All 87 books (all pairs / different-author pairs only).

| block | Prose | Prose (style encoder) | Telling | World | Felt (no reader) |
|---|---|---|---|---|---|
| Prose | 1.00 / 1.00 | 0.43 / 0.42 | 0.32 / 0.31 | 0.40 / 0.37 | 0.18 / 0.16 |
| Prose (style encoder) | 0.43 / 0.42 | 1.00 / 1.00 | 0.10 / 0.09 | 0.20 / 0.18 | 0.09 / 0.08 |
| Telling | 0.32 / 0.31 | 0.10 / 0.09 | 1.00 / 1.00 | 0.17 / 0.15 | 0.05 / 0.03 |
| World | 0.40 / 0.37 | 0.20 / 0.18 | 0.17 / 0.15 | 1.00 / 1.00 | 0.40 / 0.38 |
| Felt (no reader) | 0.18 / 0.16 | 0.09 / 0.08 | 0.05 / 0.03 | 0.40 / 0.38 | 1.00 / 1.00 |

### World candidates, all 87 books

AUC that a labelled pair is closer than a negative pair (3663 negatives; [95% bootstrap interval over the labelled pairs]). n = labelled pairs.

| block | translation_pair (n=10) | edition_pair (n=1) | same_author_unrelated (n=52) | same_author_orig_en (n=33) | same_author_same_translator (n=5) | same_author_diff_translator (n=14) | series (n=7) | retelling (n=8) | same_translator_diff_author (n=11) | same_genre (n=261) |
|---|---|---|---|---|---|---|---|---|---|---|
| W1_qwen_clean_c | 1.00 [1.00, 1.00] | 1.00 | 0.93 [0.89, 0.96] | 0.89 [0.83, 0.94] | 0.99 [0.98, 1.00] | 0.99 [0.98, 0.99] | 1.00 [1.00, 1.00] | 0.98 [0.95, 1.00] | 0.98 [0.96, 1.00] | 0.81 [0.79, 0.83] |
| W1_qwen_maskA_c | 1.00 [1.00, 1.00] | 1.00 | 0.92 [0.89, 0.95] | 0.93 [0.89, 0.97] | 0.95 [0.94, 0.96] | 0.89 [0.84, 0.93] | 0.99 [0.97, 1.00] | 0.97 [0.93, 1.00] | 0.70 [0.61, 0.79] | 0.80 [0.78, 0.83] |
| W1_qwen_maskB_c | 1.00 [1.00, 1.00] | 1.00 | 0.91 [0.88, 0.94] | 0.93 [0.88, 0.97] | 0.93 [0.91, 0.95] | 0.86 [0.80, 0.92] | 0.99 [0.97, 1.00] | 0.98 [0.93, 1.00] | 0.65 [0.57, 0.75] | 0.80 [0.78, 0.83] |
| W1_qwen_maskB_instr_c | 1.00 [1.00, 1.00] | 1.00 | 0.91 [0.87, 0.94] | 0.92 [0.87, 0.96] | 0.94 [0.89, 0.98] | 0.87 [0.81, 0.92] | 1.00 [0.99, 1.00] | 0.97 [0.93, 1.00] | 0.72 [0.66, 0.80] | 0.81 [0.79, 0.83] |
| W1_qwen_clean_pc1 | 1.00 [1.00, 1.00] | 1.00 | 0.88 [0.83, 0.93] | 0.82 [0.75, 0.89] | 0.99 [0.99, 1.00] | 0.98 [0.98, 0.99] | 1.00 [1.00, 1.00] | 0.95 [0.92, 0.98] | 0.99 [0.97, 1.00] | 0.64 [0.61, 0.67] |
| W1_qwen_maskB_pc1 | 1.00 [1.00, 1.00] | 1.00 | 0.90 [0.86, 0.93] | 0.91 [0.86, 0.95] | 0.97 [0.96, 0.98] | 0.84 [0.78, 0.89] | 0.99 [0.97, 1.00] | 0.92 [0.88, 0.97] | 0.62 [0.49, 0.74] | 0.62 [0.58, 0.65] |
| W1_qwen_clean_raw | 1.00 [1.00, 1.00] | 1.00 | 0.87 [0.83, 0.91] | 0.84 [0.77, 0.90] | 0.96 [0.94, 0.98] | 0.93 [0.89, 0.95] | 1.00 [1.00, 1.00] | 0.92 [0.85, 0.97] | 0.92 [0.83, 0.98] | 0.74 [0.71, 0.76] |
| W1_qwen_maskB_raw | 0.98 [0.96, 1.00] | 1.00 | 0.82 [0.75, 0.87] | 0.87 [0.80, 0.93] | 0.83 [0.73, 0.94] | 0.69 [0.57, 0.81] | 0.98 [0.94, 1.00] | 0.67 [0.52, 0.84] | 0.78 [0.64, 0.90] | 0.65 [0.62, 0.68] |
| W0_tfidf_clean | 1.00 [1.00, 1.00] | 1.00 | 0.93 [0.90, 0.96] | 0.92 [0.87, 0.96] | 0.99 [0.97, 1.00] | 0.95 [0.90, 0.99] | 0.98 [0.94, 1.00] | 0.96 [0.92, 0.99] | 0.90 [0.79, 0.97] | 0.54 [0.51, 0.58] |
| W0_tfidf_maskB | 1.00 [1.00, 1.00] | 1.00 | 0.92 [0.89, 0.96] | 0.90 [0.84, 0.95] | 0.99 [0.98, 1.00] | 0.95 [0.92, 0.98] | 0.94 [0.88, 0.99] | 0.94 [0.89, 0.99] | 0.90 [0.80, 0.98] | 0.53 [0.50, 0.57] |
| P4_mfw500_tag3_rhythm | 1.00 [1.00, 1.00] | 1.00 | 0.99 [0.98, 0.99] | 0.99 [0.98, 0.99] | 1.00 [1.00, 1.00] | 0.98 [0.96, 1.00] | 1.00 [0.99, 1.00] | 0.73 [0.44, 0.95] | 0.94 [0.89, 0.98] | 0.61 [0.57, 0.65] |

AUC difference from `W1_qwen_clean_c` on the same pairs [paired bootstrap 95%].

| block | translation_pair (n=10) | edition_pair (n=1) | same_author_unrelated (n=52) | same_author_orig_en (n=33) | same_author_same_translator (n=5) | same_author_diff_translator (n=14) | series (n=7) | retelling (n=8) | same_translator_diff_author (n=11) | same_genre (n=261) |
|---|---|---|---|---|---|---|---|---|---|---|
| W1_qwen_maskA_c | -0.00 [-0.00, +0.00] |  | -0.00 [-0.03, +0.03] | +0.04 [+0.01, +0.08] | -0.04 [-0.05, -0.03] | -0.10 [-0.15, -0.05] | -0.01 [-0.03, -0.00] | -0.00 [-0.02, +0.01] | -0.27 [-0.35, -0.19] | -0.01 [-0.02, +0.01] |
| W1_qwen_maskB_c | -0.00 [-0.00, -0.00] |  | -0.01 [-0.05, +0.02] | +0.04 [+0.01, +0.08] | -0.05 [-0.08, -0.04] | -0.13 [-0.19, -0.07] | -0.01 [-0.03, -0.00] | -0.00 [-0.02, +0.01] | -0.32 [-0.41, -0.24] | -0.01 [-0.02, +0.00] |
| W1_qwen_maskB_instr_c | -0.00 [-0.00, -0.00] |  | -0.02 [-0.05, +0.01] | +0.03 [-0.00, +0.06] | -0.05 [-0.10, -0.02] | -0.12 [-0.17, -0.07] | -0.00 [-0.01, -0.00] | -0.00 [-0.02, +0.01] | -0.25 [-0.31, -0.19] | -0.00 [-0.02, +0.01] |
| W1_qwen_clean_pc1 | +0.00 [+0.00, +0.00] |  | -0.05 [-0.07, -0.02] | -0.07 [-0.11, -0.04] | +0.00 [+0.00, +0.00] | -0.00 [-0.01, +0.00] | -0.00 [-0.00, +0.00] | -0.03 [-0.04, -0.01] | +0.01 [+0.00, +0.02] | -0.17 [-0.20, -0.14] |
| W1_qwen_maskB_pc1 | -0.00 [-0.00, +0.00] |  | -0.03 [-0.06, +0.01] | +0.02 [-0.02, +0.06] | -0.02 [-0.03, -0.00] | -0.14 [-0.20, -0.09] | -0.01 [-0.02, +0.00] | -0.05 [-0.10, -0.01] | -0.36 [-0.48, -0.23] | -0.20 [-0.23, -0.16] |
| W1_qwen_clean_raw | +0.00 [+0.00, +0.00] |  | -0.05 [-0.08, -0.03] | -0.05 [-0.10, -0.01] | -0.03 [-0.05, -0.01] | -0.06 [-0.09, -0.03] | -0.00 [-0.00, +0.00] | -0.06 [-0.10, -0.03] | -0.06 [-0.13, -0.02] | -0.07 [-0.10, -0.05] |
| W1_qwen_maskB_raw | -0.02 [-0.04, -0.00] |  | -0.11 [-0.18, -0.04] | -0.02 [-0.10, +0.05] | -0.15 [-0.25, -0.06] | -0.29 [-0.41, -0.18] | -0.02 [-0.06, -0.00] | -0.31 [-0.47, -0.14] | -0.20 [-0.32, -0.09] | -0.16 [-0.20, -0.13] |
| W0_tfidf_clean | +0.00 [+0.00, +0.00] |  | +0.01 [-0.04, +0.05] | +0.03 [-0.03, +0.09] | -0.00 [-0.02, +0.01] | -0.04 [-0.09, +0.00] | -0.02 [-0.06, -0.00] | -0.01 [-0.06, +0.03] | -0.08 [-0.16, -0.02] | -0.27 [-0.31, -0.23] |
| W0_tfidf_maskB | -0.00 [-0.00, +0.00] |  | -0.00 [-0.05, +0.04] | +0.01 [-0.06, +0.07] | -0.00 [-0.01, +0.01] | -0.03 [-0.07, -0.00] | -0.06 [-0.13, -0.01] | -0.03 [-0.10, +0.02] | -0.08 [-0.16, -0.02] | -0.28 [-0.31, -0.24] |
| P4_mfw500_tag3_rhythm | -0.00 [-0.00, -0.00] |  | +0.06 [+0.03, +0.10] | +0.10 [+0.05, +0.15] | +0.01 [+0.00, +0.02] | -0.00 [-0.03, +0.02] | -0.00 [-0.01, +0.00] | -0.25 [-0.54, -0.02] | -0.03 [-0.07, -0.00] | -0.20 [-0.24, -0.17] |

Mean percentile rank of the partner (0 = nearest book) / recall@1 / recall@5.

| block | translation_pair (n=10) | edition_pair (n=1) | same_author_unrelated (n=52) | same_author_orig_en (n=33) | same_author_same_translator (n=5) | same_author_diff_translator (n=14) | series (n=7) | retelling (n=8) | same_translator_diff_author (n=11) | same_genre (n=261) |
|---|---|---|---|---|---|---|---|---|---|---|
| W1_qwen_clean_c | 0.00 / 1.00 / 1.00 | 0.00 / 1.00 / 1.00 | 0.10 / 0.21 / 0.73 | 0.12 / 0.25 / 0.62 | 0.04 / 0.29 / 0.71 | 0.05 / 0.00 / 0.81 | 0.00 / 1.00 / 1.00 | 0.03 / 0.60 / 0.80 | 0.06 / 0.17 / 0.83 | 0.21 / 0.21 / 0.87 |
| W1_qwen_maskA_c | 0.00 / 1.00 / 1.00 | 0.00 / 1.00 / 1.00 | 0.08 / 0.23 / 0.83 | 0.08 / 0.28 / 0.88 | 0.02 / 0.29 / 1.00 | 0.10 / 0.00 / 0.44 | 0.01 / 0.86 / 0.86 | 0.04 / 0.50 / 0.80 | 0.32 / 0.00 / 0.50 | 0.22 / 0.38 / 0.85 |
| W1_qwen_maskB_c | 0.00 / 1.00 / 1.00 | 0.00 / 1.00 / 1.00 | 0.09 / 0.23 / 0.81 | 0.08 / 0.28 / 0.88 | 0.03 / 0.29 / 0.86 | 0.13 / 0.00 / 0.38 | 0.01 / 0.86 / 0.93 | 0.03 / 0.40 / 0.80 | 0.38 / 0.00 / 0.33 | 0.22 / 0.40 / 0.85 |
| W1_qwen_maskB_instr_c | 0.00 / 1.00 / 1.00 | 0.00 / 1.00 / 1.00 | 0.10 / 0.27 / 0.71 | 0.09 / 0.31 / 0.72 | 0.04 / 0.43 / 0.71 | 0.13 / 0.00 / 0.44 | 0.00 / 1.00 / 1.00 | 0.04 / 0.50 / 0.80 | 0.32 / 0.17 / 0.50 | 0.21 / 0.28 / 0.85 |
| W1_qwen_clean_pc1 | 0.00 / 1.00 / 1.00 | 0.00 / 1.00 / 1.00 | 0.14 / 0.19 / 0.67 | 0.19 / 0.22 / 0.53 | 0.05 / 0.29 / 0.71 | 0.06 / 0.00 / 0.81 | 0.00 / 1.00 / 1.00 | 0.05 / 0.50 / 0.70 | 0.05 / 0.17 / 0.83 | 0.38 / 0.21 / 0.77 |
| W1_qwen_maskB_pc1 | 0.00 / 1.00 / 1.00 | 0.00 / 1.00 / 1.00 | 0.10 / 0.27 / 0.71 | 0.09 / 0.31 / 0.78 | 0.03 / 0.29 / 0.86 | 0.16 / 0.06 / 0.25 | 0.01 / 0.86 / 0.93 | 0.08 / 0.30 / 0.60 | 0.40 / 0.00 / 0.33 | 0.39 / 0.28 / 0.68 |
| W1_qwen_clean_raw | 0.00 / 1.00 / 1.00 | 0.00 / 1.00 / 1.00 | 0.12 / 0.23 / 0.69 | 0.16 / 0.28 / 0.56 | 0.05 / 0.29 / 0.71 | 0.06 / 0.00 / 0.75 | 0.00 / 0.93 / 1.00 | 0.06 / 0.50 / 0.80 | 0.09 / 0.00 / 0.83 | 0.26 / 0.17 / 0.81 |
| W1_qwen_maskB_raw | 0.00 / 0.94 / 0.94 | 0.00 / 1.00 / 1.00 | 0.12 / 0.25 / 0.79 | 0.10 / 0.38 / 0.81 | 0.15 / 0.00 / 0.71 | 0.17 / 0.00 / 0.50 | 0.01 / 0.86 / 0.93 | 0.06 / 0.30 / 0.80 | 0.28 / 0.17 / 0.67 | 0.29 / 0.19 / 0.85 |
| W0_tfidf_clean | 0.00 / 1.00 / 1.00 | 0.00 / 1.00 / 1.00 | 0.05 / 0.60 / 0.92 | 0.05 / 0.72 / 0.94 | 0.02 / 0.43 / 1.00 | 0.05 / 0.19 / 0.75 | 0.00 / 1.00 / 1.00 | 0.02 / 0.60 / 0.90 | 0.10 / 0.00 / 1.00 | 0.41 / 0.09 / 0.62 |
| W0_tfidf_maskB | 0.00 / 1.00 / 1.00 | 0.00 / 1.00 / 1.00 | 0.05 / 0.60 / 0.92 | 0.06 / 0.72 / 0.94 | 0.04 / 0.43 / 1.00 | 0.05 / 0.19 / 0.75 | 0.00 / 0.93 / 1.00 | 0.03 / 0.50 / 0.90 | 0.11 / 0.00 / 1.00 | 0.42 / 0.09 / 0.64 |
| P4_mfw500_tag3_rhythm | 0.00 / 0.94 / 1.00 | 0.00 / 1.00 / 1.00 | 0.02 / 0.69 / 0.98 | 0.02 / 0.81 / 0.97 | 0.01 / 0.71 / 1.00 | 0.03 / 0.12 / 0.94 | 0.00 / 0.86 / 1.00 | 0.24 / 0.30 / 0.50 | 0.09 / 0.00 / 0.83 | 0.38 / 0.09 / 0.72 |

Split-half self-retrieval (accuracy; chance is 1/n), and Spearman of distance with |year difference| and |log word-count difference| (Mantel p in brackets; en = both books written in English; diff = different authors only).

| block | n | input | split a/b | split h1/h2 | rho year | rho year en | rho year en diff | rho logwords | rho logwords diff |
|---|---|---|---|---|---|---|---|---|---|
| W1_qwen_clean_c | 87 | ordered text | 0.93 | 0.91 | 0.07 (0.005) | 0.05 (0.040) | 0.02 | 0.06 (0.005) | 0.05 |
| W1_qwen_maskA_c | 87 | ordered text | 0.95 | 0.91 | 0.08 (0.010) | 0.06 (0.020) | 0.02 | 0.05 (0.005) | 0.03 |
| W1_qwen_maskB_c | 87 | ordered text | 0.96 | 0.91 | 0.08 (0.005) | 0.07 (0.025) | 0.03 | 0.05 (0.015) | 0.03 |
| W1_qwen_maskB_instr_c | 87 | ordered text | 0.94 | 0.82 | 0.09 (0.005) | 0.07 (0.030) | 0.03 | 0.07 (0.010) | 0.05 |
| W1_qwen_clean_pc1 | 87 | ordered text | 0.93 | 0.91 | 0.10 (0.005) | 0.07 (0.015) | 0.04 | 0.11 (0.005) | 0.10 |
| W1_qwen_maskB_pc1 | 87 | ordered text | 0.96 | 0.93 | 0.13 (0.005) | 0.14 (0.005) | 0.11 | 0.09 (0.005) | 0.08 |
| W1_qwen_clean_raw | 87 | ordered text | 0.94 | 0.89 | 0.12 (0.030) | -0.04 (0.570) | -0.08 | 0.07 (0.145) | 0.06 |
| W1_qwen_maskB_raw | 87 | ordered text | 0.95 | 0.91 | 0.14 (0.030) | 0.04 (0.580) | 0.00 | 0.02 (0.645) | 0.00 |
| W0_tfidf_clean | 87 | book bag | 0.93 | 0.96 | 0.08 (0.200) | 0.04 (0.640) | -0.00 | 0.04 (0.475) | 0.03 |
| W0_tfidf_maskB | 87 | book bag | 0.93 | 0.90 | 0.07 (0.220) | 0.05 (0.540) | 0.01 | 0.03 (0.520) | 0.02 |
| P4_mfw500_tag3_rhythm | 87 | ordered text | 0.97 | 0.91 | 0.36 (0.005) | 0.34 (0.005) | 0.31 | 0.05 (0.205) | 0.03 |

Top-5 neighbour make-up (observed / chance) and hubness (skew of the 5-nearest in-degree; share of books in nobody's top 5; largest in-degree and the book).

| block | same author | same genre | mean abs year diff | mean abs log-words diff | hub skew | in no top 5 | max in-degree |
|---|---|---|---|---|---|---|---|
| W1_qwen_clean_c | 0.30 / 0.02 | 0.47 / 0.12 | 38 / 56 | 0.63 / 0.78 | 0.20 | 0.05 | 11 (austen_pp) |
| W1_qwen_maskA_c | 0.31 / 0.02 | 0.49 / 0.12 | 41 / 56 | 0.60 / 0.78 | 1.06 | 0.00 | 16 (austen_emma) |
| W1_qwen_maskB_c | 0.30 / 0.02 | 0.51 / 0.12 | 41 / 56 | 0.62 / 0.78 | 1.13 | 0.00 | 16 (austen_emma) |
| W1_qwen_maskB_instr_c | 0.29 / 0.02 | 0.53 / 0.12 | 38 / 56 | 0.61 / 0.78 | 1.10 | 0.02 | 16 (austen_emma) |
| W1_qwen_clean_pc1 | 0.27 / 0.02 | 0.38 / 0.12 | 36 / 56 | 0.66 / 0.78 | 0.43 | 0.01 | 13 (mystisland_kingston) |
| W1_qwen_maskB_pc1 | 0.27 / 0.02 | 0.38 / 0.12 | 39 / 56 | 0.63 / 0.78 | 0.42 | 0.00 | 11 (austen_emma) |
| W1_qwen_clean_raw | 0.27 / 0.02 | 0.39 / 0.12 | 36 / 56 | 0.66 / 0.78 | 2.96 | 0.09 | 39 (dickens_bleak) |
| W1_qwen_maskB_raw | 0.29 / 0.02 | 0.42 / 0.12 | 36 / 56 | 0.64 / 0.78 | 2.17 | 0.03 | 25 (dickens_great) |
| W0_tfidf_clean | 0.37 / 0.02 | 0.33 / 0.12 | 31 / 56 | 0.78 / 0.78 | 2.76 | 0.06 | 35 (dickens_bleak) |
| W0_tfidf_maskB | 0.37 / 0.02 | 0.32 / 0.12 | 31 / 56 | 0.79 / 0.78 | 2.58 | 0.08 | 34 (tolstoy_wp_maude) |
| P4_mfw500_tag3_rhythm | 0.40 / 0.02 | 0.38 / 0.12 | 27 / 56 | 0.64 / 0.78 | 1.00 | 0.02 | 17 (wells_worlds) |

Spearman between the pair distances of two blocks, all pairs.

| block | W1_qwen_clean_c | W1_qwen_maskA_c | W1_qwen_maskB_c | W1_qwen_maskB_instr_c | W1_qwen_clean_pc1 | W1_qwen_maskB_pc1 | W1_qwen_clean_raw | W1_qwen_maskB_raw | W0_tfidf_clean | W0_tfidf_maskB | P4_mfw500_tag3_rhythm |
|---|---|---|---|---|---|---|---|---|---|---|---|
| W1_qwen_clean_c | 1.00 | 0.78 | 0.76 | 0.78 | 0.63 | 0.39 | 0.67 | 0.47 | 0.29 | 0.27 | 0.34 |
| W1_qwen_maskA_c | 0.78 | 1.00 | 0.99 | 0.94 | 0.30 | 0.49 | 0.51 | 0.65 | 0.32 | 0.33 | 0.40 |
| W1_qwen_maskB_c | 0.76 | 0.99 | 1.00 | 0.93 | 0.27 | 0.49 | 0.50 | 0.65 | 0.32 | 0.33 | 0.40 |
| W1_qwen_maskB_instr_c | 0.78 | 0.94 | 0.93 | 1.00 | 0.29 | 0.43 | 0.52 | 0.64 | 0.35 | 0.36 | 0.40 |
| W1_qwen_clean_pc1 | 0.63 | 0.30 | 0.27 | 0.29 | 1.00 | 0.60 | 0.44 | 0.18 | 0.17 | 0.14 | 0.20 |
| W1_qwen_maskB_pc1 | 0.39 | 0.49 | 0.49 | 0.43 | 0.60 | 1.00 | 0.28 | 0.32 | 0.21 | 0.20 | 0.25 |
| W1_qwen_clean_raw | 0.67 | 0.51 | 0.50 | 0.52 | 0.44 | 0.28 | 1.00 | 0.56 | 0.47 | 0.41 | 0.27 |
| W1_qwen_maskB_raw | 0.47 | 0.65 | 0.65 | 0.64 | 0.18 | 0.32 | 0.56 | 1.00 | 0.48 | 0.52 | 0.36 |
| W0_tfidf_clean | 0.29 | 0.32 | 0.32 | 0.35 | 0.17 | 0.21 | 0.47 | 0.48 | 1.00 | 0.98 | 0.46 |
| W0_tfidf_maskB | 0.27 | 0.33 | 0.33 | 0.36 | 0.14 | 0.20 | 0.41 | 0.52 | 0.98 | 1.00 | 0.47 |
| P4_mfw500_tag3_rhythm | 0.34 | 0.40 | 0.40 | 0.40 | 0.20 | 0.25 | 0.27 | 0.36 | 0.46 | 0.47 | 1.00 |

Spearman between the pair distances of two blocks, different-author pairs only.

| block | W1_qwen_clean_c | W1_qwen_maskA_c | W1_qwen_maskB_c | W1_qwen_maskB_instr_c | W1_qwen_clean_pc1 | W1_qwen_maskB_pc1 | W1_qwen_clean_raw | W1_qwen_maskB_raw | W0_tfidf_clean | W0_tfidf_maskB | P4_mfw500_tag3_rhythm |
|---|---|---|---|---|---|---|---|---|---|---|---|
| W1_qwen_clean_c | 1.00 | 0.77 | 0.75 | 0.77 | 0.62 | 0.36 | 0.65 | 0.45 | 0.26 | 0.23 | 0.30 |
| W1_qwen_maskA_c | 0.77 | 1.00 | 0.99 | 0.93 | 0.27 | 0.47 | 0.49 | 0.64 | 0.29 | 0.30 | 0.37 |
| W1_qwen_maskB_c | 0.75 | 0.99 | 1.00 | 0.93 | 0.24 | 0.47 | 0.48 | 0.64 | 0.29 | 0.30 | 0.37 |
| W1_qwen_maskB_instr_c | 0.77 | 0.93 | 0.93 | 1.00 | 0.26 | 0.40 | 0.50 | 0.63 | 0.31 | 0.33 | 0.37 |
| W1_qwen_clean_pc1 | 0.62 | 0.27 | 0.24 | 0.26 | 1.00 | 0.58 | 0.42 | 0.15 | 0.14 | 0.10 | 0.16 |
| W1_qwen_maskB_pc1 | 0.36 | 0.47 | 0.47 | 0.40 | 0.58 | 1.00 | 0.25 | 0.30 | 0.17 | 0.16 | 0.22 |
| W1_qwen_clean_raw | 0.65 | 0.49 | 0.48 | 0.50 | 0.42 | 0.25 | 1.00 | 0.55 | 0.45 | 0.39 | 0.23 |
| W1_qwen_maskB_raw | 0.45 | 0.64 | 0.64 | 0.63 | 0.15 | 0.30 | 0.55 | 1.00 | 0.46 | 0.50 | 0.33 |
| W0_tfidf_clean | 0.26 | 0.29 | 0.29 | 0.31 | 0.14 | 0.17 | 0.45 | 0.46 | 1.00 | 0.98 | 0.43 |
| W0_tfidf_maskB | 0.23 | 0.30 | 0.30 | 0.33 | 0.10 | 0.16 | 0.39 | 0.50 | 0.98 | 1.00 | 0.45 |
| P4_mfw500_tag3_rhythm | 0.30 | 0.37 | 0.37 | 0.37 | 0.16 | 0.22 | 0.23 | 0.33 | 0.43 | 0.45 | 1.00 |


### W1 instruction prefix against none (maskB)

AUC that a labelled pair is closer than a negative pair (3663 negatives; [95% bootstrap interval over the labelled pairs]). n = labelled pairs.

| block | translation_pair (n=10) | edition_pair (n=1) | same_author_unrelated (n=52) | same_author_orig_en (n=33) | same_author_same_translator (n=5) | same_author_diff_translator (n=14) | series (n=7) | retelling (n=8) | same_translator_diff_author (n=11) | same_genre (n=261) |
|---|---|---|---|---|---|---|---|---|---|---|
| W1_qwen_maskB_c | 1.00 [1.00, 1.00] | 1.00 | 0.91 [0.88, 0.94] | 0.93 [0.89, 0.96] | 0.93 [0.91, 0.95] | 0.86 [0.80, 0.92] | 0.99 [0.97, 1.00] | 0.98 [0.93, 1.00] | 0.65 [0.57, 0.75] | 0.80 [0.78, 0.83] |
| W1_qwen_maskB_instr_c | 1.00 [1.00, 1.00] | 1.00 | 0.91 [0.87, 0.94] | 0.92 [0.87, 0.96] | 0.94 [0.89, 0.98] | 0.87 [0.81, 0.92] | 1.00 [0.99, 1.00] | 0.97 [0.93, 1.00] | 0.72 [0.66, 0.80] | 0.81 [0.79, 0.83] |
| W1_qwen_maskB_raw | 0.98 [0.96, 1.00] | 1.00 | 0.82 [0.76, 0.87] | 0.87 [0.80, 0.93] | 0.83 [0.73, 0.94] | 0.69 [0.56, 0.81] | 0.98 [0.94, 1.00] | 0.67 [0.52, 0.83] | 0.78 [0.64, 0.90] | 0.65 [0.62, 0.68] |
| W1_qwen_maskB_instr_raw | 1.00 [1.00, 1.00] | 1.00 | 0.81 [0.75, 0.87] | 0.83 [0.76, 0.91] | 0.90 [0.79, 0.98] | 0.71 [0.60, 0.82] | 0.98 [0.96, 1.00] | 0.80 [0.70, 0.90] | 0.88 [0.83, 0.94] | 0.64 [0.61, 0.67] |
| W1_qwen_maskB_pc1 | 1.00 [1.00, 1.00] | 1.00 | 0.90 [0.86, 0.93] | 0.91 [0.86, 0.95] | 0.97 [0.96, 0.98] | 0.84 [0.78, 0.89] | 0.99 [0.97, 1.00] | 0.92 [0.88, 0.97] | 0.62 [0.49, 0.75] | 0.62 [0.58, 0.65] |
| W1_qwen_maskB_instr_pc1 | 1.00 [1.00, 1.00] | 1.00 | 0.88 [0.84, 0.92] | 0.87 [0.82, 0.92] | 0.97 [0.95, 0.99] | 0.86 [0.82, 0.90] | 1.00 [0.99, 1.00] | 0.96 [0.93, 0.99] | 0.66 [0.56, 0.75] | 0.64 [0.60, 0.67] |

AUC difference from `W1_qwen_maskB_c` on the same pairs [paired bootstrap 95%].

| block | translation_pair (n=10) | edition_pair (n=1) | same_author_unrelated (n=52) | same_author_orig_en (n=33) | same_author_same_translator (n=5) | same_author_diff_translator (n=14) | series (n=7) | retelling (n=8) | same_translator_diff_author (n=11) | same_genre (n=261) |
|---|---|---|---|---|---|---|---|---|---|---|
| W1_qwen_maskB_instr_c | +0.00 [-0.00, +0.00] |  | -0.00 [-0.02, +0.01] | -0.01 [-0.03, +0.01] | +0.01 [-0.02, +0.03] | +0.01 [-0.03, +0.05] | +0.01 [-0.00, +0.02] | -0.00 [-0.00, +0.00] | +0.07 [+0.01, +0.13] | +0.01 [-0.01, +0.02] |
| W1_qwen_maskB_raw | -0.01 [-0.04, +0.00] |  | -0.09 [-0.16, -0.04] | -0.06 [-0.12, -0.01] | -0.10 [-0.19, -0.01] | -0.17 [-0.34, -0.02] | -0.02 [-0.03, -0.00] | -0.30 [-0.48, -0.12] | +0.13 [+0.02, +0.23] | -0.15 [-0.18, -0.12] |
| W1_qwen_maskB_instr_raw | +0.00 [+0.00, +0.00] |  | -0.10 [-0.16, -0.05] | -0.09 [-0.16, -0.03] | -0.04 [-0.12, +0.03] | -0.15 [-0.30, -0.00] | -0.01 [-0.03, +0.01] | -0.17 [-0.28, -0.07] | +0.23 [+0.16, +0.30] | -0.16 [-0.19, -0.13] |
| W1_qwen_maskB_pc1 | +0.00 [+0.00, +0.00] |  | -0.01 [-0.03, +0.01] | -0.02 [-0.04, +0.00] | +0.04 [+0.02, +0.05] | -0.02 [-0.07, +0.03] | +0.00 [-0.00, +0.00] | -0.05 [-0.11, +0.01] | -0.04 [-0.10, +0.02] | -0.19 [-0.22, -0.15] |
| W1_qwen_maskB_instr_pc1 | +0.00 [+0.00, +0.00] |  | -0.03 [-0.07, -0.00] | -0.06 [-0.10, -0.02] | +0.04 [+0.03, +0.04] | +0.00 [-0.05, +0.06] | +0.01 [-0.00, +0.02] | -0.01 [-0.03, +0.01] | +0.01 [-0.06, +0.08] | -0.16 [-0.20, -0.13] |

Mean percentile rank of the partner (0 = nearest book) / recall@1 / recall@5.

| block | translation_pair (n=10) | edition_pair (n=1) | same_author_unrelated (n=52) | same_author_orig_en (n=33) | same_author_same_translator (n=5) | same_author_diff_translator (n=14) | series (n=7) | retelling (n=8) | same_translator_diff_author (n=11) | same_genre (n=261) |
|---|---|---|---|---|---|---|---|---|---|---|
| W1_qwen_maskB_c | 0.00 / 1.00 / 1.00 | 0.00 / 1.00 / 1.00 | 0.09 / 0.23 / 0.81 | 0.08 / 0.28 / 0.88 | 0.03 / 0.29 / 0.86 | 0.13 / 0.00 / 0.38 | 0.01 / 0.86 / 0.93 | 0.03 / 0.40 / 0.80 | 0.38 / 0.00 / 0.33 | 0.22 / 0.40 / 0.85 |
| W1_qwen_maskB_instr_c | 0.00 / 1.00 / 1.00 | 0.00 / 1.00 / 1.00 | 0.10 / 0.27 / 0.71 | 0.09 / 0.31 / 0.72 | 0.04 / 0.43 / 0.71 | 0.13 / 0.00 / 0.44 | 0.00 / 1.00 / 1.00 | 0.04 / 0.50 / 0.80 | 0.32 / 0.17 / 0.50 | 0.21 / 0.28 / 0.85 |
| W1_qwen_maskB_raw | 0.00 / 0.94 / 0.94 | 0.00 / 1.00 / 1.00 | 0.12 / 0.25 / 0.79 | 0.10 / 0.38 / 0.81 | 0.15 / 0.00 / 0.71 | 0.17 / 0.00 / 0.50 | 0.01 / 0.86 / 0.93 | 0.06 / 0.30 / 0.80 | 0.28 / 0.17 / 0.67 | 0.29 / 0.19 / 0.85 |
| W1_qwen_maskB_instr_raw | 0.00 / 1.00 / 1.00 | 0.00 / 1.00 / 1.00 | 0.12 / 0.35 / 0.79 | 0.11 / 0.44 / 0.81 | 0.08 / 0.43 / 0.71 | 0.18 / 0.00 / 0.50 | 0.00 / 0.93 / 1.00 | 0.05 / 0.50 / 0.80 | 0.20 / 0.17 / 0.83 | 0.29 / 0.21 / 0.79 |
| W1_qwen_maskB_pc1 | 0.00 / 1.00 / 1.00 | 0.00 / 1.00 / 1.00 | 0.10 / 0.27 / 0.71 | 0.09 / 0.31 / 0.78 | 0.03 / 0.29 / 0.86 | 0.16 / 0.06 / 0.25 | 0.01 / 0.86 / 0.93 | 0.08 / 0.30 / 0.60 | 0.40 / 0.00 / 0.33 | 0.39 / 0.28 / 0.68 |
| W1_qwen_maskB_instr_pc1 | 0.00 / 1.00 / 1.00 | 0.00 / 1.00 / 1.00 | 0.12 / 0.29 / 0.71 | 0.12 / 0.34 / 0.75 | 0.04 / 0.29 / 0.71 | 0.13 / 0.06 / 0.44 | 0.00 / 0.79 / 1.00 | 0.04 / 0.60 / 0.80 | 0.34 / 0.00 / 0.17 | 0.37 / 0.28 / 0.77 |

Split-half self-retrieval (accuracy; chance is 1/n), and Spearman of distance with |year difference| and |log word-count difference| (Mantel p in brackets; en = both books written in English; diff = different authors only).

| block | n | input | split a/b | split h1/h2 | rho year | rho year en | rho year en diff | rho logwords | rho logwords diff |
|---|---|---|---|---|---|---|---|---|---|
| W1_qwen_maskB_c | 87 | ordered text | 0.96 | 0.91 | 0.08 (0.005) | 0.07 (0.015) | 0.03 | 0.05 (0.015) | 0.03 |
| W1_qwen_maskB_instr_c | 87 | ordered text | 0.94 | 0.82 | 0.09 (0.005) | 0.07 (0.040) | 0.03 | 0.07 (0.005) | 0.05 |
| W1_qwen_maskB_raw | 87 | ordered text | 0.95 | 0.91 | 0.14 (0.015) | 0.04 (0.665) | 0.00 | 0.02 (0.700) | 0.00 |
| W1_qwen_maskB_instr_raw | 87 | ordered text | 0.94 | 0.79 | 0.13 (0.030) | 0.02 (0.805) | -0.02 | 0.04 (0.465) | 0.03 |
| W1_qwen_maskB_pc1 | 87 | ordered text | 0.96 | 0.93 | 0.13 (0.005) | 0.14 (0.005) | 0.11 | 0.09 (0.005) | 0.08 |
| W1_qwen_maskB_instr_pc1 | 87 | ordered text | 0.94 | 0.82 | 0.15 (0.005) | 0.14 (0.005) | 0.11 | 0.10 (0.005) | 0.10 |

Top-5 neighbour make-up (observed / chance) and hubness (skew of the 5-nearest in-degree; share of books in nobody's top 5; largest in-degree and the book).

| block | same author | same genre | mean abs year diff | mean abs log-words diff | hub skew | in no top 5 | max in-degree |
|---|---|---|---|---|---|---|---|
| W1_qwen_maskB_c | 0.30 / 0.02 | 0.51 / 0.12 | 41 / 56 | 0.62 / 0.78 | 1.13 | 0.00 | 16 (austen_emma) |
| W1_qwen_maskB_instr_c | 0.29 / 0.02 | 0.53 / 0.12 | 38 / 56 | 0.61 / 0.78 | 1.10 | 0.02 | 16 (austen_emma) |
| W1_qwen_maskB_raw | 0.29 / 0.02 | 0.42 / 0.12 | 36 / 56 | 0.64 / 0.78 | 2.17 | 0.03 | 25 (dickens_great) |
| W1_qwen_maskB_instr_raw | 0.29 / 0.02 | 0.42 / 0.12 | 36 / 56 | 0.66 / 0.78 | 1.70 | 0.03 | 21 (dickens_great) |
| W1_qwen_maskB_pc1 | 0.27 / 0.02 | 0.38 / 0.12 | 39 / 56 | 0.63 / 0.78 | 0.42 | 0.00 | 11 (austen_emma) |
| W1_qwen_maskB_instr_pc1 | 0.27 / 0.02 | 0.43 / 0.12 | 38 / 56 | 0.64 / 0.78 | 0.91 | 0.00 | 14 (anne_avonlea) |

Spearman between the pair distances of two blocks, all pairs.

| block | W1_qwen_maskB_c | W1_qwen_maskB_instr_c | W1_qwen_maskB_raw | W1_qwen_maskB_instr_raw | W1_qwen_maskB_pc1 | W1_qwen_maskB_instr_pc1 |
|---|---|---|---|---|---|---|
| W1_qwen_maskB_c | 1.00 | 0.93 | 0.65 | 0.62 | 0.49 | 0.45 |
| W1_qwen_maskB_instr_c | 0.93 | 1.00 | 0.64 | 0.69 | 0.43 | 0.52 |
| W1_qwen_maskB_raw | 0.65 | 0.64 | 1.00 | 0.93 | 0.32 | 0.29 |
| W1_qwen_maskB_instr_raw | 0.62 | 0.69 | 0.93 | 1.00 | 0.28 | 0.32 |
| W1_qwen_maskB_pc1 | 0.49 | 0.43 | 0.32 | 0.28 | 1.00 | 0.85 |
| W1_qwen_maskB_instr_pc1 | 0.45 | 0.52 | 0.29 | 0.32 | 0.85 | 1.00 |

Spearman between the pair distances of two blocks, different-author pairs only.

| block | W1_qwen_maskB_c | W1_qwen_maskB_instr_c | W1_qwen_maskB_raw | W1_qwen_maskB_instr_raw | W1_qwen_maskB_pc1 | W1_qwen_maskB_instr_pc1 |
|---|---|---|---|---|---|---|
| W1_qwen_maskB_c | 1.00 | 0.93 | 0.64 | 0.60 | 0.47 | 0.43 |
| W1_qwen_maskB_instr_c | 0.93 | 1.00 | 0.63 | 0.68 | 0.40 | 0.49 |
| W1_qwen_maskB_raw | 0.64 | 0.63 | 1.00 | 0.93 | 0.30 | 0.27 |
| W1_qwen_maskB_instr_raw | 0.60 | 0.68 | 0.93 | 1.00 | 0.25 | 0.30 |
| W1_qwen_maskB_pc1 | 0.47 | 0.40 | 0.30 | 0.25 | 1.00 | 0.85 |
| W1_qwen_maskB_instr_pc1 | 0.43 | 0.49 | 0.27 | 0.30 | 0.85 | 1.00 |


### Blocks against `P4_mfw500_tag3_rhythm`

| block | Spearman with P4_mfw500_tag3_rhythm | ... different authors only | translation_pair: raw / ref regressed out | same_author_unrelated: raw / ref regressed out | series: raw / ref regressed out | retelling: raw / ref regressed out | same_genre: raw / ref regressed out |
|---|---|---|---|---|---|---|---|
| P5_style_clean_c | 0.43 | 0.42 | 0.68 / 0.50 | 0.77 / 0.58 | 0.94 / 0.77 | 0.71 / 0.63 | 0.57 / 0.52 |
| P5_style_maskA_c | 0.42 | 0.41 | 0.68 / 0.50 | 0.77 / 0.59 | 0.94 / 0.77 | 0.70 / 0.63 | 0.56 / 0.52 |
| P6_closed_nopron | 0.67 | 0.66 | 0.99 / 0.75 | 0.97 / 0.74 | 1.00 / 0.78 | 0.90 / 0.79 | 0.63 / 0.57 |
| W1_qwen_maskB_c | 0.40 | 0.37 | 1.00 / 0.86 | 0.91 / 0.75 | 0.99 / 0.85 | 0.98 / 0.89 | 0.80 / 0.78 |
| W1_qwen_clean_c | 0.34 | 0.30 | 1.00 / 0.88 | 0.93 / 0.79 | 1.00 / 0.88 | 0.98 / 0.90 | 0.81 / 0.79 |
| W1_qwen_maskB_pc1 | 0.25 | 0.22 | 1.00 / 0.90 | 0.90 / 0.79 | 0.99 / 0.89 | 0.92 / 0.88 | 0.62 / 0.59 |
| W0_tfidf_maskB | 0.47 | 0.45 | 1.00 / 0.84 | 0.92 / 0.74 | 0.94 / 0.75 | 0.94 / 0.88 | 0.53 / 0.49 |
| W0_tfidf_clean | 0.46 | 0.43 | 1.00 / 0.84 | 0.93 / 0.75 | 0.98 / 0.80 | 0.96 / 0.89 | 0.54 / 0.50 |
| F_proj_plain | 0.18 | 0.16 | 0.90 / 0.82 | 0.70 / 0.61 | 0.83 / 0.75 | 0.91 / 0.86 | 0.62 / 0.60 |

### Author or translator (6 Garnett books)

| block | nearest: author+translator | author only | translator only | neither | AUC author beats translator (14 vs 11) | AUC translation pair closer than same-author pair (10 vs 52) | ... than orig-English same-author pair (10 vs 33) | median d translation pair / median d same-author |
|---|---|---|---|---|---|---|---|---|
| W1_qwen_clean_c | 2 | 0 | 3 | 1 | 0.33 | 1.00 | 1.00 | 0.10 |
| W1_qwen_maskA_c | 3 | 0 | 0 | 3 | 0.85 | 0.96 | 0.94 | 0.29 |
| W1_qwen_maskB_c | 3 | 0 | 0 | 3 | 0.85 | 0.93 | 0.91 | 0.30 |
| W0_tfidf_clean | 3 | 1 | 2 | 0 | 0.64 | 1.00 | 1.00 | 0.53 |
| W0_tfidf_maskB | 4 | 1 | 1 | 0 | 0.60 | 0.98 | 0.98 | 0.59 |

Nearest book that is not the same work, per Garnett book (ranks count from 1).

| block | anchor | nearest_not_same_work | shares | rank_nearest_same_author_other_translator | rank_nearest_garnett_other_author |
|---|---|---|---|---|---|
| W1_qwen_clean_c | dost_cp_garnett | dost_bk_garnett | author+translator | 5 | 2 |
| W1_qwen_clean_c | dost_bk_garnett | dost_cp_garnett | author+translator | 7 | 2 |
| W1_qwen_clean_c | dost_notes_garnett | zamyatin_we | neither | 10 | 8 |
| W1_qwen_clean_c | tolstoy_ak_garnett | gentlefolk_garnett | translator only | 8 | 1 |
| W1_qwen_clean_c | fathers_garnett | tolstoy_ak_garnett | translator only | 3 | 1 |
| W1_qwen_clean_c | gentlefolk_garnett | tolstoy_ak_garnett | translator only | 4 | 1 |
| W1_qwen_maskA_c | dost_cp_garnett | dost_bk_garnett | author+translator | 13 | 19 |
| W1_qwen_maskA_c | dost_bk_garnett | dost_cp_garnett | author+translator | 12 | 4 |
| W1_qwen_maskA_c | dost_notes_garnett | zamyatin_we | neither | 15 | 17 |
| W1_qwen_maskA_c | tolstoy_ak_garnett | gentlefolk_ralston | neither | 9 | 2 |
| W1_qwen_maskA_c | fathers_garnett | woolf_voyage | neither | 3 | 24 |
| W1_qwen_maskA_c | gentlefolk_garnett | fathers_garnett | author+translator | 3 | 2 |
| W1_qwen_maskB_c | dost_cp_garnett | dost_bk_garnett | author+translator | 14 | 21 |
| W1_qwen_maskB_c | dost_bk_garnett | dost_cp_garnett | author+translator | 18 | 6 |
| W1_qwen_maskB_c | dost_notes_garnett | zamyatin_we | neither | 16 | 21 |
| W1_qwen_maskB_c | tolstoy_ak_garnett | hardy_jude | neither | 15 | 4 |
| W1_qwen_maskB_c | fathers_garnett | woolf_voyage | neither | 5 | 27 |
| W1_qwen_maskB_c | gentlefolk_garnett | fathers_garnett | author+translator | 4 | 2 |
| W0_tfidf_clean | dost_cp_garnett | dost_bk_garnett | author+translator | 2 | 3 |
| W0_tfidf_clean | dost_bk_garnett | dost_cp_garnett | author+translator | 3 | 2 |
| W0_tfidf_clean | dost_notes_garnett | dost_cp_garnett | author+translator | 3 | 4 |
| W0_tfidf_clean | tolstoy_ak_garnett | tolstoy_wp_maude | author only | 1 | 2 |
| W0_tfidf_clean | fathers_garnett | tolstoy_ak_garnett | translator only | 8 | 1 |
| W0_tfidf_clean | gentlefolk_garnett | tolstoy_ak_garnett | translator only | 8 | 1 |
| W0_tfidf_maskB | dost_cp_garnett | dost_bk_garnett | author+translator | 2 | 3 |
| W0_tfidf_maskB | dost_bk_garnett | dost_cp_garnett | author+translator | 2 | 3 |
| W0_tfidf_maskB | dost_notes_garnett | dost_cp_garnett | author+translator | 3 | 4 |
| W0_tfidf_maskB | tolstoy_ak_garnett | tolstoy_wp_maude | author only | 1 | 2 |
| W0_tfidf_maskB | fathers_garnett | tolstoy_ak_garnett | translator only | 7 | 1 |
| W0_tfidf_maskB | gentlefolk_garnett | fathers_garnett | author+translator | 8 | 2 |

### World convergence (qwen_maskB; 12 books with every chunk embedded)

Means over 12 books x 5 draws. cos = cosine of the k-chunk book vector with the all-chunk vector; rho_dist = Spearman of the distances to the other 86 books.

| k | cos_raw | cos_centred | rho_dist | top5_overlap | same_nearest | worst cos_centred |
|---|---|---|---|---|---|---|
| 5 | 0.927 | 0.688 | 0.808 | 0.663 | 0.650 | 0.358 |
| 10 | 0.965 | 0.815 | 0.907 | 0.760 | 0.733 | 0.650 |
| 20 | 0.984 | 0.901 | 0.948 | 0.813 | 0.817 | 0.738 |
| 40 | 0.993 | 0.954 | 0.981 | 0.883 | 0.950 | 0.900 |
| 80 | 0.998 | 0.984 | 0.991 | 0.943 | 0.933 | 0.964 |

Per book at k = 40.

| key | n_chunks | cos_centred | rho_dist | top5_overlap | same_nearest |
|---|---|---|---|---|---|
| austen_emma | 158 | 0.955 | 0.995 | 0.920 | 1.000 |
| barset_towers | 198 | 0.963 | 0.990 | 1.000 | 1.000 |
| charterhouse_loyd | 199 | 0.961 | 0.979 | 0.800 | 1.000 |
| collins_moonstone | 197 | 0.935 | 0.958 | 0.920 | 0.800 |
| dickens_great | 186 | 0.913 | 0.955 | 0.800 | 1.000 |
| dost_cp_garnett | 199 | 0.931 | 0.964 | 0.640 | 1.000 |
| james_ambassadors | 165 | 0.954 | 0.990 | 1.000 | 1.000 |
| mystisland_kingston | 195 | 0.981 | 0.997 | 1.000 | 1.000 |
| mystisland_white | 162 | 0.977 | 0.997 | 1.000 | 1.000 |
| stoker_dracula | 161 | 0.941 | 0.980 | 0.840 | 0.600 |
| tolstoy_res_maude | 172 | 0.957 | 0.974 | 0.840 | 1.000 |
| wyss_swiss | 166 | 0.977 | 0.995 | 0.840 | 1.000 |

### Why are these two books World neighbours? (W1_qwen_maskB_c)

Mutual nearest neighbours by different authors, not related by translation, edition, series or retelling (cosine distance):

- austen_persuasion ~ brinton_old_friends: 0.327
- james_ambassadors ~ wharton_mirth: 0.385
- wells_time ~ zamyatin_we: 0.444
- christie_styles ~ hammett_falcon: 0.525
- hardy_mayor ~ wharton_frome: 0.654
- radcliffe_udolpho ~ lewis_monk: 0.660

#### The Mysteries of Udolpho (Ann Radcliffe, 1794) and The Monk (Matthew Gregory Lewis, 1796)

The three most similar chunk pairs (centred cosine; the median over all sampled chunk pairs of the two books is 0.05). The encoder saw the name-masked text; the clean text is printed.

**cosine 0.47**

- `radcliffe_udolpho` chunk 37: On the following morning, she was visited by a sister of the convent, who came, with kind offices and a second invitation from the lady abbess; and Emily, though she could not forsake the cottage, while the remains of her father were in it, consented, however painful such a visit must be, in the present state of her spirits, to ...
- `lewis_monk` chunk 97: Ambrosio was by no means disposed to grant the petition of his visitor. He refused it positively, and bad the lay-brother tell the stranger to return the next day. Matilda interrupted him. “See this woman,” said she in a low voice; “I have my reasons.” The abbot obeyed her, and signified that he would go to the parlour immediately. With ...

**cosine 0.40**

- `radcliffe_udolpho` chunk 149: He then took up the torch, and led her along the passage, at the extremity of which he unlocked another door, whence they descended, a few steps, into a chapel, which, as Barnardine held up the torch to light her, Emily observed to be in ruins, and she immediately recollected a former conversation of Annette, concerning it, with very unpleasant ...
- `lewis_monk` chunk 69: “I have been expecting you with impatience,” said she; “My life depends upon these moments. Have you the key?” “I have.” “Away then to the garden. We have no time to lose. Follow me!” She took a small covered basket from the table. Bearing this in one hand, and the lamp, which was flaming upon the hearth, in the other, ...

**cosine 0.37**

- `radcliffe_udolpho` chunk 201: The Mariner Soft came the breath of spring; smooth flow’d the tide; And blue the heaven in its mirror smil’d; The white sail trembled, swell’d, expanded wide, The busy sailors at the anchor toil’d. With anxious friends, that shed the parting tear, The deck was throng’d—how swift the moments fly! The vessel heaves, the farewell signs appear; Mute is each ...
- `lewis_monk` chunk 59: “What! is it thou?” the startled sire In sullen tone exclaimed, while ire With crimson flushed his pale and wrinkled cheek: “Wouldst thou again with amorous rage Inflame my bosom? Steeled by age, Vain boy, to pierce my breast thine arrows are too weak. “What seek you in this desert drear? No smiles or sports inhabit here; Ne’er did these ...


### W0 TF-IDF

AUC that a labelled pair is closer than a negative pair (3663 negatives; [95% bootstrap interval over the labelled pairs]). n = labelled pairs.

| block | translation_pair (n=10) | edition_pair (n=1) | same_author_unrelated (n=52) | same_author_orig_en (n=33) | same_author_same_translator (n=5) | same_author_diff_translator (n=14) | series (n=7) | retelling (n=8) | same_translator_diff_author (n=11) | same_genre (n=261) |
|---|---|---|---|---|---|---|---|---|---|---|
| W0_tfidf_maskB | 1.00 [1.00, 1.00] | 1.00 | 0.92 [0.88, 0.96] | 0.90 [0.84, 0.95] | 0.99 [0.98, 1.00] | 0.95 [0.92, 0.98] | 0.94 [0.88, 0.99] | 0.94 [0.89, 0.99] | 0.90 [0.80, 0.97] | 0.53 [0.50, 0.57] |
| W0_tfidf_clean | 1.00 [1.00, 1.00] | 1.00 | 0.93 [0.90, 0.96] | 0.92 [0.87, 0.96] | 0.99 [0.97, 1.00] | 0.95 [0.90, 0.99] | 0.98 [0.94, 1.00] | 0.96 [0.92, 0.99] | 0.90 [0.79, 0.98] | 0.54 [0.51, 0.58] |
| W0_tfidf_maskB_nostop | 1.00 [1.00, 1.00] | 1.00 | 0.92 [0.88, 0.96] | 0.90 [0.84, 0.95] | 0.99 [0.98, 1.00] | 0.95 [0.92, 0.98] | 0.94 [0.87, 0.99] | 0.94 [0.89, 0.99] | 0.90 [0.80, 0.97] | 0.53 [0.50, 0.57] |
| W0_tfidf_clean_nostop | 1.00 [1.00, 1.00] | 1.00 | 0.93 [0.90, 0.96] | 0.92 [0.87, 0.96] | 0.99 [0.97, 1.00] | 0.95 [0.90, 0.98] | 0.98 [0.93, 1.00] | 0.96 [0.92, 0.99] | 0.89 [0.79, 0.98] | 0.54 [0.51, 0.57] |
| P4_mfw500_tag3_rhythm | 1.00 [1.00, 1.00] | 1.00 | 0.99 [0.98, 0.99] | 0.99 [0.98, 0.99] | 1.00 [1.00, 1.00] | 0.98 [0.96, 1.00] | 1.00 [0.99, 1.00] | 0.73 [0.44, 0.95] | 0.94 [0.89, 0.98] | 0.61 [0.57, 0.65] |

Mean percentile rank of the partner (0 = nearest book) / recall@1 / recall@5.

| block | translation_pair (n=10) | edition_pair (n=1) | same_author_unrelated (n=52) | same_author_orig_en (n=33) | same_author_same_translator (n=5) | same_author_diff_translator (n=14) | series (n=7) | retelling (n=8) | same_translator_diff_author (n=11) | same_genre (n=261) |
|---|---|---|---|---|---|---|---|---|---|---|
| W0_tfidf_maskB | 0.00 / 1.00 / 1.00 | 0.00 / 1.00 / 1.00 | 0.05 / 0.60 / 0.92 | 0.06 / 0.72 / 0.94 | 0.04 / 0.43 / 1.00 | 0.05 / 0.19 / 0.75 | 0.00 / 0.93 / 1.00 | 0.03 / 0.50 / 0.90 | 0.11 / 0.00 / 1.00 | 0.42 / 0.09 / 0.64 |
| W0_tfidf_clean | 0.00 / 1.00 / 1.00 | 0.00 / 1.00 / 1.00 | 0.05 / 0.60 / 0.92 | 0.05 / 0.72 / 0.94 | 0.02 / 0.43 / 1.00 | 0.05 / 0.19 / 0.75 | 0.00 / 1.00 / 1.00 | 0.02 / 0.60 / 0.90 | 0.10 / 0.00 / 1.00 | 0.41 / 0.09 / 0.62 |
| W0_tfidf_maskB_nostop | 0.00 / 1.00 / 1.00 | 0.00 / 1.00 / 1.00 | 0.05 / 0.60 / 0.92 | 0.06 / 0.72 / 0.94 | 0.04 / 0.43 / 1.00 | 0.05 / 0.19 / 0.75 | 0.00 / 0.93 / 1.00 | 0.03 / 0.50 / 0.90 | 0.11 / 0.00 / 1.00 | 0.42 / 0.09 / 0.64 |
| W0_tfidf_clean_nostop | 0.00 / 1.00 / 1.00 | 0.00 / 1.00 / 1.00 | 0.05 / 0.60 / 0.92 | 0.05 / 0.72 / 0.94 | 0.02 / 0.43 / 1.00 | 0.05 / 0.19 / 0.75 | 0.00 / 1.00 / 1.00 | 0.02 / 0.60 / 0.90 | 0.10 / 0.00 / 1.00 | 0.41 / 0.09 / 0.62 |
| P4_mfw500_tag3_rhythm | 0.00 / 0.94 / 1.00 | 0.00 / 1.00 / 1.00 | 0.02 / 0.69 / 0.98 | 0.02 / 0.81 / 0.97 | 0.01 / 0.71 / 1.00 | 0.03 / 0.12 / 0.94 | 0.00 / 0.86 / 1.00 | 0.24 / 0.30 / 0.50 | 0.09 / 0.00 / 0.83 | 0.38 / 0.09 / 0.72 |

Split-half self-retrieval (accuracy; chance is 1/n), and Spearman of distance with |year difference| and |log word-count difference| (Mantel p in brackets; en = both books written in English; diff = different authors only).

| block | n | input | split a/b | split h1/h2 | rho year | rho year en | rho year en diff | rho logwords | rho logwords diff |
|---|---|---|---|---|---|---|---|---|---|
| W0_tfidf_maskB | 87 | book bag | 0.93 | 0.90 | 0.07 (0.290) | 0.05 (0.565) | 0.01 | 0.03 (0.575) | 0.02 |
| W0_tfidf_clean | 87 | book bag | 0.93 | 0.96 | 0.08 (0.150) | 0.04 (0.635) | -0.00 | 0.04 (0.400) | 0.03 |
| W0_tfidf_maskB_nostop | 87 | book bag | 0.93 | 0.90 | 0.07 (0.270) | 0.05 (0.590) | 0.01 | 0.03 (0.575) | 0.02 |
| W0_tfidf_clean_nostop | 87 | book bag | 0.93 | 0.96 | 0.08 (0.180) | 0.04 (0.600) | -0.00 | 0.04 (0.425) | 0.03 |
| P4_mfw500_tag3_rhythm | 87 | ordered text | 0.97 | 0.91 | 0.36 (0.005) | 0.34 (0.005) | 0.31 | 0.05 (0.130) | 0.03 |

Top-5 neighbour make-up (observed / chance) and hubness (skew of the 5-nearest in-degree; share of books in nobody's top 5; largest in-degree and the book).

| block | same author | same genre | mean abs year diff | mean abs log-words diff | hub skew | in no top 5 | max in-degree |
|---|---|---|---|---|---|---|---|
| W0_tfidf_maskB | 0.37 / 0.02 | 0.32 / 0.12 | 31 / 56 | 0.79 / 0.78 | 2.58 | 0.08 | 34 (tolstoy_wp_maude) |
| W0_tfidf_clean | 0.37 / 0.02 | 0.33 / 0.12 | 31 / 56 | 0.78 / 0.78 | 2.76 | 0.06 | 35 (dickens_bleak) |
| W0_tfidf_maskB_nostop | 0.37 / 0.02 | 0.33 / 0.12 | 31 / 56 | 0.80 / 0.78 | 2.66 | 0.08 | 36 (tolstoy_wp_maude) |
| W0_tfidf_clean_nostop | 0.37 / 0.02 | 0.33 / 0.12 | 31 / 56 | 0.78 / 0.78 | 2.82 | 0.07 | 36 (dickens_bleak) |
| P4_mfw500_tag3_rhythm | 0.40 / 0.02 | 0.38 / 0.12 | 27 / 56 | 0.64 / 0.78 | 1.00 | 0.02 | 17 (wells_worlds) |

Spearman between the pair distances of two blocks, all pairs.

| block | W0_tfidf_maskB | W0_tfidf_clean | W0_tfidf_maskB_nostop | W0_tfidf_clean_nostop | P4_mfw500_tag3_rhythm |
|---|---|---|---|---|---|
| W0_tfidf_maskB | 1.00 | 0.98 | 1.00 | 0.98 | 0.47 |
| W0_tfidf_clean | 0.98 | 1.00 | 0.98 | 1.00 | 0.46 |
| W0_tfidf_maskB_nostop | 1.00 | 0.98 | 1.00 | 0.98 | 0.47 |
| W0_tfidf_clean_nostop | 0.98 | 1.00 | 0.98 | 1.00 | 0.46 |
| P4_mfw500_tag3_rhythm | 0.47 | 0.46 | 0.47 | 0.46 | 1.00 |

Spearman between the pair distances of two blocks, different-author pairs only.

| block | W0_tfidf_maskB | W0_tfidf_clean | W0_tfidf_maskB_nostop | W0_tfidf_clean_nostop | P4_mfw500_tag3_rhythm |
|---|---|---|---|---|---|
| W0_tfidf_maskB | 1.00 | 0.98 | 1.00 | 0.98 | 0.45 |
| W0_tfidf_clean | 0.98 | 1.00 | 0.98 | 1.00 | 0.43 |
| W0_tfidf_maskB_nostop | 1.00 | 0.98 | 1.00 | 0.98 | 0.45 |
| W0_tfidf_clean_nostop | 0.98 | 1.00 | 0.98 | 1.00 | 0.43 |
| P4_mfw500_tag3_rhythm | 0.45 | 0.43 | 0.45 | 0.43 | 1.00 |


### All blocks on the 24-book reader subset

AUC that a labelled pair is closer than a negative pair (263 negatives; [95% bootstrap interval over the labelled pairs]). n = labelled pairs.

| block | translation_pair (n=3) | edition_pair (n=1) | same_author_unrelated (n=5) | same_author_orig_en (n=1) | same_author_same_translator (n=1) | same_author_diff_translator (n=3) | series (n=3) | retelling (n=1) | same_genre (n=26) |
|---|---|---|---|---|---|---|---|---|---|
| P4_mfw500_tag3_rhythm | 1.00 [0.99, 1.00] | 1.00 | 0.96 [0.89, 1.00] | 1.00 | 1.00 | 0.93 [0.84, 1.00] | 1.00 [0.99, 1.00] | 1.00 | 0.70 [0.60, 0.80] |
| T3_scalars_dtw20_sd | 1.00 [1.00, 1.00] | 1.00 | 0.76 [0.55, 0.93] | 0.37 | 0.96 | 0.82 [0.68, 0.95] | 0.64 [0.33, 0.91] | 0.99 | 0.65 [0.55, 0.75] |
| W1_qwen_maskB_c | 1.00 [1.00, 1.00] | 1.00 | 0.90 [0.84, 0.96] | 1.00 | 0.93 | 0.86 [0.79, 0.91] | 1.00 [1.00, 1.00] | 1.00 | 0.87 [0.82, 0.92] |
| W0_tfidf_maskB | 1.00 [1.00, 1.00] | 1.00 | 1.00 [1.00, 1.00] | 0.99 | 1.00 | 1.00 [1.00, 1.00] | 1.00 [1.00, 1.00] | 1.00 | 0.60 [0.50, 0.70] |
| W_digest_plain | 1.00 [1.00, 1.00] | 1.00 | 0.98 [0.96, 1.00] | 1.00 | 0.93 | 1.00 [0.99, 1.00] | 0.90 [0.69, 1.00] | 0.99 | 0.59 [0.48, 0.70] |
| S_story_plain | 1.00 [1.00, 1.00] | 1.00 | 0.98 [0.97, 0.99] | 1.00 | 0.99 | 0.97 [0.95, 0.98] | 0.98 [0.95, 1.00] | 1.00 | 0.82 [0.74, 0.89] |
| S_storychar_plain | 1.00 [1.00, 1.00] | 1.00 | 0.99 [0.98, 0.99] | 0.98 | 0.99 | 0.99 [0.98, 0.99] | 0.99 [0.98, 1.00] | 1.00 | 0.82 [0.75, 0.88] |
| S_story_tfidf | 1.00 [1.00, 1.00] | 1.00 | 0.99 [0.98, 0.99] | 0.98 | 1.00 | 0.98 [0.97, 0.99] | 0.99 [0.97, 1.00] | 1.00 | 0.57 [0.45, 0.69] |
| F_reader | 0.99 [0.99, 1.00] | 1.00 | 0.98 [0.94, 1.00] | 0.90 | 0.99 | 1.00 [1.00, 1.00] | 0.99 [0.98, 1.00] | 1.00 | 0.73 [0.62, 0.82] |
| F_proj_plain | 0.70 [0.15, 1.00] | 1.00 | 0.71 [0.52, 0.90] | 0.95 | 0.73 | 0.63 [0.35, 0.92] | 0.84 [0.68, 0.95] | 0.92 | 0.73 [0.65, 0.81] |

Mean percentile rank of the partner (0 = nearest book) / recall@1 / recall@5.

| block | translation_pair (n=3) | edition_pair (n=1) | same_author_unrelated (n=5) | same_author_orig_en (n=1) | same_author_same_translator (n=1) | same_author_diff_translator (n=3) | series (n=3) | retelling (n=1) | same_genre (n=26) |
|---|---|---|---|---|---|---|---|---|---|
| P4_mfw500_tag3_rhythm | 0.02 / 0.83 / 1.00 | 0.00 / 1.00 / 1.00 | 0.05 / 0.50 / 1.00 | 0.00 / 1.00 / 1.00 | 0.02 / 0.50 / 1.00 | 0.08 / 0.00 / 1.00 | 0.00 / 1.00 / 1.00 | 0.00 / 1.00 / 1.00 | 0.32 / 0.12 / 0.88 |
| T3_scalars_dtw20_sd | 0.00 / 1.00 / 1.00 | 0.00 / 1.00 / 1.00 | 0.28 / 0.00 / 0.67 | 0.48 / 0.00 / 0.50 | 0.11 / 0.00 / 1.00 | 0.27 / 0.00 / 0.50 | 0.36 / 0.00 / 0.33 | 0.05 / 0.50 / 1.00 | 0.28 / 0.41 / 0.82 |
| W1_qwen_maskB_c | 0.00 / 1.00 / 1.00 | 0.00 / 1.00 / 1.00 | 0.06 / 0.17 / 1.00 | 0.02 / 0.50 / 1.00 | 0.05 / 0.00 / 1.00 | 0.08 / 0.00 / 1.00 | 0.00 / 1.00 / 1.00 | 0.00 / 1.00 / 1.00 | 0.17 / 0.24 / 0.82 |
| W0_tfidf_maskB | 0.00 / 1.00 / 1.00 | 0.00 / 1.00 / 1.00 | 0.05 / 0.33 / 1.00 | 0.00 / 1.00 / 1.00 | 0.05 / 0.00 / 1.00 | 0.08 / 0.00 / 1.00 | 0.00 / 1.00 / 1.00 | 0.00 / 1.00 / 1.00 | 0.35 / 0.06 / 0.94 |
| W_digest_plain | 0.00 / 1.00 / 1.00 | 0.00 / 1.00 / 1.00 | 0.05 / 0.33 / 1.00 | 0.00 / 1.00 / 1.00 | 0.09 / 0.00 / 1.00 | 0.06 / 0.00 / 1.00 | 0.11 / 0.67 / 0.67 | 0.00 / 1.00 / 1.00 | 0.43 / 0.12 / 0.59 |
| S_story_plain | 0.00 / 1.00 / 1.00 | 0.00 / 1.00 / 1.00 | 0.06 / 0.33 / 1.00 | 0.00 / 1.00 / 1.00 | 0.07 / 0.00 / 1.00 | 0.08 / 0.00 / 1.00 | 0.02 / 0.83 / 1.00 | 0.00 / 1.00 / 1.00 | 0.20 / 0.24 / 0.82 |
| S_storychar_plain | 0.00 / 1.00 / 1.00 | 0.00 / 1.00 / 1.00 | 0.05 / 0.33 / 1.00 | 0.00 / 1.00 / 1.00 | 0.05 / 0.00 / 1.00 | 0.08 / 0.00 / 1.00 | 0.02 / 0.67 / 1.00 | 0.00 / 1.00 / 1.00 | 0.20 / 0.24 / 0.94 |
| S_story_tfidf | 0.00 / 1.00 / 1.00 | 0.00 / 1.00 / 1.00 | 0.06 / 0.33 / 1.00 | 0.00 / 1.00 / 1.00 | 0.05 / 0.00 / 1.00 | 0.09 / 0.00 / 1.00 | 0.02 / 0.67 / 1.00 | 0.00 / 1.00 / 1.00 | 0.41 / 0.24 / 0.65 |
| F_reader | 0.04 / 0.33 / 1.00 | 0.00 / 1.00 / 1.00 | 0.06 / 0.67 / 0.83 | 0.16 / 0.00 / 0.50 | 0.09 / 0.00 / 1.00 | 0.02 / 1.00 / 1.00 | 0.02 / 0.83 / 1.00 | 0.00 / 1.00 / 1.00 | 0.31 / 0.18 / 0.82 |
| F_proj_plain | 0.22 / 0.67 / 0.67 | 0.00 / 1.00 / 1.00 | 0.20 / 0.00 / 1.00 | 0.05 / 0.00 / 1.00 | 0.23 / 0.00 / 0.50 | 0.23 / 0.00 / 1.00 | 0.15 / 0.50 / 0.67 | 0.07 / 0.50 / 1.00 | 0.28 / 0.18 / 0.82 |

Split-half self-retrieval (accuracy; chance is 1/n), and Spearman of distance with |year difference| and |log word-count difference| (Mantel p in brackets; en = both books written in English; diff = different authors only).

| block | n | input | split a/b | split h1/h2 | rho year | rho year en | rho year en diff | rho logwords | rho logwords diff |
|---|---|---|---|---|---|---|---|---|---|
| P4_mfw500_tag3_rhythm | 24 | ordered text | 0.88 | 0.77 | 0.32 (0.005) | 0.37 (0.005) | 0.34 | 0.06 (0.475) | 0.02 |
| T3_scalars_dtw20_sd | 24 | ordered text | 0.71 |  | 0.09 (0.300) | 0.14 (0.280) | 0.13 | 0.06 (0.505) | 0.02 |
| W1_qwen_maskB_c | 24 | ordered text | 0.94 | 0.88 | 0.17 (0.015) | 0.08 (0.340) | 0.03 | -0.04 (0.585) | -0.09 |
| W0_tfidf_maskB | 24 | book bag | 0.81 | 0.85 | 0.05 (0.640) | 0.09 (0.555) | 0.04 | 0.40 (0.010) | 0.39 |
| W_digest_plain | 24 | ordered text |  |  | 0.15 (0.010) | 0.07 (0.340) | 0.02 | -0.01 (0.790) | -0.07 |
| S_story_plain | 24 | ordered text |  |  | 0.09 (0.070) | -0.09 (0.245) | -0.15 | 0.01 (0.855) | -0.04 |
| S_storychar_plain | 24 | ordered text |  |  | 0.09 (0.080) | -0.07 (0.345) | -0.13 | 0.02 (0.725) | -0.03 |
| S_story_tfidf | 24 | ordered text |  |  | 0.14 (0.105) | 0.06 (0.645) | 0.00 | 0.12 (0.170) | 0.08 |
| F_reader | 24 | ordered text |  |  | 0.01 (0.835) | -0.03 (0.690) | -0.08 | -0.04 (0.305) | -0.10 |
| F_proj_plain | 24 | ordered text | 0.65 | 0.48 | 0.09 (0.225) | 0.02 (0.860) | -0.02 | -0.04 (0.645) | -0.06 |

Top-5 neighbour make-up (observed / chance) and hubness (skew of the 5-nearest in-degree; share of books in nobody's top 5; largest in-degree and the book).

| block | same author | same genre | mean abs year diff | mean abs log-words diff | hub skew | in no top 5 | max in-degree |
|---|---|---|---|---|---|---|---|
| P4_mfw500_tag3_rhythm | 0.29 / 0.06 | 0.43 / 0.15 | 22 / 33 | 0.41 / 0.42 | 0.85 | 0.00 | 12 (wells_worlds) |
| T3_scalars_dtw20_sd | 0.19 / 0.06 | 0.39 / 0.15 | 30 / 33 | 0.44 / 0.42 | 0.54 | 0.00 | 12 (merriman_barlasch) |
| W1_qwen_maskB_c | 0.29 / 0.06 | 0.54 / 0.15 | 24 / 33 | 0.41 / 0.42 | 0.80 | 0.00 | 9 (wells_worlds) |
| W0_tfidf_maskB | 0.29 / 0.06 | 0.38 / 0.15 | 25 / 33 | 0.33 / 0.42 | 0.87 | 0.12 | 16 (conrad_agent) |
| W_digest_plain | 0.27 / 0.06 | 0.31 / 0.15 | 24 / 33 | 0.37 / 0.42 | -0.18 | 0.00 | 8 (wells_worlds) |
| S_story_plain | 0.29 / 0.06 | 0.53 / 0.15 | 28 / 33 | 0.39 / 0.42 | -0.55 | 0.00 | 7 (wharton_frome) |
| S_storychar_plain | 0.29 / 0.06 | 0.50 / 0.15 | 25 / 33 | 0.36 / 0.42 | 0.06 | 0.00 | 8 (merriman_barlasch) |
| S_story_tfidf | 0.29 / 0.06 | 0.34 / 0.15 | 26 / 33 | 0.38 / 0.42 | 0.69 | 0.00 | 12 (fathers_garnett) |
| F_reader | 0.28 / 0.06 | 0.39 / 0.15 | 28 / 33 | 0.45 / 0.42 | 0.14 | 0.00 | 8 (zamyatin_we) |
| F_proj_plain | 0.21 / 0.06 | 0.43 / 0.15 | 31 / 33 | 0.42 / 0.42 | -0.21 | 0.00 | 8 (wharton_frome) |

Spearman between the pair distances of two blocks, all pairs.

| block | P4_mfw500_tag3_rhythm | T3_scalars_dtw20_sd | W1_qwen_maskB_c | W0_tfidf_maskB | W_digest_plain | S_story_plain | S_storychar_plain | S_story_tfidf | F_reader | F_proj_plain |
|---|---|---|---|---|---|---|---|---|---|---|
| P4_mfw500_tag3_rhythm | 1.00 | 0.39 | 0.56 | 0.54 | 0.28 | 0.35 | 0.31 | 0.26 | 0.25 | 0.26 |
| T3_scalars_dtw20_sd | 0.39 | 1.00 | 0.22 | 0.20 | 0.14 | 0.29 | 0.29 | 0.24 | 0.18 | 0.13 |
| W1_qwen_maskB_c | 0.56 | 0.22 | 1.00 | 0.40 | 0.43 | 0.59 | 0.56 | 0.27 | 0.50 | 0.54 |
| W0_tfidf_maskB | 0.54 | 0.20 | 0.40 | 1.00 | 0.25 | 0.31 | 0.30 | 0.38 | 0.27 | 0.17 |
| W_digest_plain | 0.28 | 0.14 | 0.43 | 0.25 | 1.00 | 0.37 | 0.35 | 0.32 | 0.27 | 0.21 |
| S_story_plain | 0.35 | 0.29 | 0.59 | 0.31 | 0.37 | 1.00 | 0.87 | 0.44 | 0.36 | 0.40 |
| S_storychar_plain | 0.31 | 0.29 | 0.56 | 0.30 | 0.35 | 0.87 | 1.00 | 0.40 | 0.46 | 0.38 |
| S_story_tfidf | 0.26 | 0.24 | 0.27 | 0.38 | 0.32 | 0.44 | 0.40 | 1.00 | 0.18 | 0.15 |
| F_reader | 0.25 | 0.18 | 0.50 | 0.27 | 0.27 | 0.36 | 0.46 | 0.18 | 1.00 | 0.41 |
| F_proj_plain | 0.26 | 0.13 | 0.54 | 0.17 | 0.21 | 0.40 | 0.38 | 0.15 | 0.41 | 1.00 |

Spearman between the pair distances of two blocks, different-author pairs only.

| block | P4_mfw500_tag3_rhythm | T3_scalars_dtw20_sd | W1_qwen_maskB_c | W0_tfidf_maskB | W_digest_plain | S_story_plain | S_storychar_plain | S_story_tfidf | F_reader | F_proj_plain |
|---|---|---|---|---|---|---|---|---|---|---|
| P4_mfw500_tag3_rhythm | 1.00 | 0.34 | 0.50 | 0.48 | 0.18 | 0.25 | 0.21 | 0.15 | 0.15 | 0.21 |
| T3_scalars_dtw20_sd | 0.34 | 1.00 | 0.15 | 0.13 | 0.06 | 0.23 | 0.23 | 0.17 | 0.10 | 0.09 |
| W1_qwen_maskB_c | 0.50 | 0.15 | 1.00 | 0.31 | 0.36 | 0.54 | 0.49 | 0.17 | 0.43 | 0.52 |
| W0_tfidf_maskB | 0.48 | 0.13 | 0.31 | 1.00 | 0.14 | 0.21 | 0.20 | 0.28 | 0.16 | 0.10 |
| W_digest_plain | 0.18 | 0.06 | 0.36 | 0.14 | 1.00 | 0.29 | 0.26 | 0.22 | 0.17 | 0.16 |
| S_story_plain | 0.25 | 0.23 | 0.54 | 0.21 | 0.29 | 1.00 | 0.84 | 0.35 | 0.27 | 0.36 |
| S_storychar_plain | 0.21 | 0.23 | 0.49 | 0.20 | 0.26 | 0.84 | 1.00 | 0.31 | 0.37 | 0.34 |
| S_story_tfidf | 0.15 | 0.17 | 0.17 | 0.28 | 0.22 | 0.35 | 0.31 | 1.00 | 0.06 | 0.08 |
| F_reader | 0.15 | 0.10 | 0.43 | 0.16 | 0.17 | 0.27 | 0.37 | 0.06 | 1.00 | 0.37 |
| F_proj_plain | 0.21 | 0.09 | 0.52 | 0.10 | 0.16 | 0.36 | 0.34 | 0.08 | 0.37 | 1.00 |


Every labelled pair: rank of b from a / rank of a from b (1 = nearest), and in brackets the share of negative pairs that are farther apart.

| set | pair | P4_mfw500_tag3_rhythm | T3_scalars_dtw20_sd | W1_qwen_maskB_c | W0_tfidf_maskB | W_digest_plain | S_story_plain | S_storychar_plain | S_story_tfidf | F_reader | F_proj_plain |
|---|---|---|---|---|---|---|---|---|---|---|---|
| translation_pair | fathers_garnett ~ fathers_hogarth | 3 / 1 (0.99) | 1 / 1 (1.00) | 1 / 1 (1.00) | 1 / 1 (1.00) | 1 / 1 (1.00) | 1 / 1 (1.00) | 1 / 1 (1.00) | 1 / 1 (1.00) | 2 / 3 (0.99) | 18 / 13 (0.15) |
| translation_pair | gentlefolk_garnett ~ gentlefolk_ralston | 1 / 1 (1.00) | 1 / 1 (1.00) | 1 / 1 (1.00) | 1 / 1 (1.00) | 1 / 1 (1.00) | 1 / 1 (1.00) | 1 / 1 (1.00) | 1 / 1 (1.00) | 2 / 2 (1.00) | 1 / 1 (0.97) |
| translation_pair | journey_1871 ~ journey_malleson | 1 / 1 (1.00) | 1 / 1 (1.00) | 1 / 1 (1.00) | 1 / 1 (1.00) | 1 / 1 (1.00) | 1 / 1 (1.00) | 1 / 1 (1.00) | 1 / 1 (1.00) | 1 / 1 (0.99) | 1 / 1 (1.00) |
| edition_pair | frankenstein_1818 ~ frankenstein_1831 | 1 / 1 (1.00) | 1 / 1 (1.00) | 1 / 1 (1.00) | 1 / 1 (1.00) | 1 / 1 (1.00) | 1 / 1 (1.00) | 1 / 1 (1.00) | 1 / 1 (1.00) | 1 / 1 (1.00) | 1 / 1 (1.00) |
| retelling | burnett_princess ~ burnett_sara_crewe | 1 / 1 (1.00) | 3 / 1 (0.99) | 1 / 1 (1.00) | 1 / 1 (1.00) | 1 / 1 (0.99) | 1 / 1 (1.00) | 1 / 1 (1.00) | 1 / 1 (1.00) | 1 / 1 (1.00) | 4 / 1 (0.92) |
| series | holmes_hound ~ holmes_study | 1 / 1 (1.00) | 10 / 19 (0.33) | 1 / 1 (1.00) | 1 / 1 (1.00) | 10 / 6 (0.69) | 1 / 3 (0.98) | 2 / 3 (0.98) | 2 / 3 (0.97) | 3 / 1 (0.98) | 1 / 1 (0.95) |
| series | oz_land ~ oz_wizard | 1 / 1 (0.99) | 3 / 4 (0.91) | 1 / 1 (1.00) | 1 / 1 (1.00) | 1 / 1 (1.00) | 1 / 1 (1.00) | 1 / 1 (1.00) | 1 / 1 (1.00) | 1 / 1 (1.00) | 1 / 3 (0.90) |
| series | tarzan_apes ~ tarzan_return | 1 / 1 (1.00) | 9 / 8 (0.68) | 1 / 1 (1.00) | 1 / 1 (1.00) | 1 / 1 (1.00) | 1 / 1 (0.95) | 1 / 1 (0.99) | 1 / 1 (1.00) | 1 / 1 (1.00) | 11 / 9 (0.68) |
| same_author_unrelated | fathers_garnett ~ gentlefolk_garnett | 1 / 2 (1.00) | 3 / 4 (0.96) | 2 / 2 (0.93) | 2 / 2 (1.00) | 3 / 3 (0.93) | 2 / 3 (0.99) | 2 / 2 (0.99) | 2 / 2 (1.00) | 3 / 3 (0.99) | 10 / 2 (0.73) |
| same_author_unrelated | fathers_garnett ~ gentlefolk_ralston | 2 / 2 (1.00) | 7 / 8 (0.83) | 3 / 2 (0.89) | 3 / 2 (1.00) | 2 / 3 (0.99) | 3 / 2 (0.98) | 3 / 2 (0.99) | 3 / 4 (0.97) | 1 / 1 (1.00) | 3 / 2 (0.92) |
| same_author_unrelated | fathers_hogarth ~ gentlefolk_garnett | 4 / 3 (0.84) | 2 / 5 (0.95) | 2 / 3 (0.91) | 3 / 3 (1.00) | 2 / 2 (1.00) | 3 / 4 (0.95) | 2 / 3 (0.98) | 2 / 3 (0.99) | 1 / 1 (1.00) | 3 / 4 (0.62) |
| same_author_unrelated | fathers_hogarth ~ gentlefolk_ralston | 2 / 3 (0.94) | 7 / 12 (0.68) | 3 / 4 (0.79) | 2 / 3 (1.00) | 3 / 2 (1.00) | 2 / 3 (0.98) | 3 / 3 (0.98) | 3 / 3 (0.98) | 2 / 3 (1.00) | 12 / 13 (0.35) |
| same_author_unrelated | wells_time ~ wells_worlds | 1 / 1 (1.00) | 4 / 19 (0.37) | 2 / 1 (1.00) | 1 / 1 (0.99) | 1 / 1 (1.00) | 1 / 1 (1.00) | 1 / 1 (0.98) | 1 / 1 (0.98) | 3 / 6 (0.90) | 2 / 2 (0.95) |

### Story and digest-World variants, 24 books

AUC that a labelled pair is closer than a negative pair (263 negatives; [95% bootstrap interval over the labelled pairs]). n = labelled pairs.

| block | translation_pair (n=3) | edition_pair (n=1) | same_author_unrelated (n=5) | same_author_orig_en (n=1) | same_author_same_translator (n=1) | same_author_diff_translator (n=3) | series (n=3) | retelling (n=1) | same_genre (n=26) |
|---|---|---|---|---|---|---|---|---|---|
| S_story_plain | 1.00 [1.00, 1.00] | 1.00 | 0.98 [0.97, 0.99] | 1.00 | 0.99 | 0.97 [0.95, 0.98] | 0.98 [0.95, 1.00] | 1.00 | 0.82 [0.74, 0.89] |
| S_story_inst | 1.00 [1.00, 1.00] | 1.00 | 0.99 [0.99, 0.99] | 0.99 | 0.99 | 0.99 [0.98, 0.99] | 0.95 [0.86, 1.00] | 1.00 | 0.82 [0.74, 0.89] |
| S_story_tfidf | 1.00 [1.00, 1.00] | 1.00 | 0.99 [0.98, 0.99] | 0.98 | 1.00 | 0.98 [0.97, 0.99] | 0.99 [0.97, 1.00] | 1.00 | 0.57 [0.46, 0.69] |
| S_characters_plain | 1.00 [1.00, 1.00] | 1.00 | 0.98 [0.96, 0.99] | 0.94 | 0.99 | 0.99 [0.99, 0.99] | 1.00 [0.99, 1.00] | 1.00 | 0.77 [0.69, 0.84] |
| S_characters_inst | 1.00 [1.00, 1.00] | 1.00 | 0.98 [0.96, 0.99] | 0.95 | 0.99 | 0.99 [0.98, 1.00] | 0.99 [0.98, 1.00] | 1.00 | 0.80 [0.73, 0.88] |
| S_storychar_plain | 1.00 [1.00, 1.00] | 1.00 | 0.99 [0.98, 0.99] | 0.98 | 0.99 | 0.99 [0.98, 0.99] | 0.99 [0.98, 1.00] | 1.00 | 0.82 [0.75, 0.89] |
| S_storychar_inst | 1.00 [1.00, 1.00] | 1.00 | 0.99 [0.98, 0.99] | 0.98 | 0.99 | 0.99 [0.98, 1.00] | 0.99 [0.98, 1.00] | 1.00 | 0.84 [0.76, 0.90] |
| S_storychar_tfidf | 1.00 [1.00, 1.00] | 1.00 | 0.98 [0.97, 0.99] | 0.99 | 1.00 | 0.98 [0.97, 0.98] | 0.97 [0.91, 1.00] | 1.00 | 0.56 [0.44, 0.67] |
| W_digest_plain | 1.00 [1.00, 1.00] | 1.00 | 0.98 [0.96, 1.00] | 1.00 | 0.93 | 1.00 [0.99, 1.00] | 0.90 [0.69, 1.00] | 0.99 | 0.59 [0.47, 0.71] |
| W_digest_inst | 1.00 [1.00, 1.00] | 1.00 | 0.99 [0.98, 1.00] | 0.98 | 0.97 | 1.00 [0.99, 1.00] | 0.94 [0.81, 1.00] | 1.00 | 0.61 [0.51, 0.71] |
| W_digestsubj_plain | 1.00 [1.00, 1.00] | 1.00 | 1.00 [0.99, 1.00] | 1.00 | 0.99 | 1.00 [0.99, 1.00] | 0.89 [0.66, 1.00] | 1.00 | 0.71 [0.61, 0.80] |
| W_digest_tfidf | 1.00 [1.00, 1.00] | 1.00 | 0.93 [0.82, 1.00] | 0.70 | 1.00 | 0.99 [0.98, 1.00] | 0.98 [0.94, 1.00] | 1.00 | 0.47 [0.35, 0.59] |

Mean percentile rank of the partner (0 = nearest book) / recall@1 / recall@5.

| block | translation_pair (n=3) | edition_pair (n=1) | same_author_unrelated (n=5) | same_author_orig_en (n=1) | same_author_same_translator (n=1) | same_author_diff_translator (n=3) | series (n=3) | retelling (n=1) | same_genre (n=26) |
|---|---|---|---|---|---|---|---|---|---|
| S_story_plain | 0.00 / 1.00 / 1.00 | 0.00 / 1.00 / 1.00 | 0.06 / 0.33 / 1.00 | 0.00 / 1.00 / 1.00 | 0.07 / 0.00 / 1.00 | 0.08 / 0.00 / 1.00 | 0.02 / 0.83 / 1.00 | 0.00 / 1.00 / 1.00 | 0.20 / 0.24 / 0.82 |
| S_story_inst | 0.00 / 1.00 / 1.00 | 0.00 / 1.00 / 1.00 | 0.06 / 0.33 / 1.00 | 0.00 / 1.00 / 1.00 | 0.05 / 0.00 / 1.00 | 0.08 / 0.00 / 1.00 | 0.04 / 0.67 / 1.00 | 0.00 / 1.00 / 1.00 | 0.22 / 0.18 / 0.88 |
| S_story_tfidf | 0.00 / 1.00 / 1.00 | 0.00 / 1.00 / 1.00 | 0.06 / 0.33 / 1.00 | 0.00 / 1.00 / 1.00 | 0.05 / 0.00 / 1.00 | 0.09 / 0.00 / 1.00 | 0.02 / 0.67 / 1.00 | 0.00 / 1.00 / 1.00 | 0.41 / 0.24 / 0.65 |
| S_characters_plain | 0.00 / 1.00 / 1.00 | 0.00 / 1.00 / 1.00 | 0.06 / 0.17 / 1.00 | 0.02 / 0.50 / 1.00 | 0.05 / 0.00 / 1.00 | 0.08 / 0.00 / 1.00 | 0.02 / 0.67 / 1.00 | 0.00 / 1.00 / 1.00 | 0.27 / 0.24 / 0.94 |
| S_characters_inst | 0.00 / 1.00 / 1.00 | 0.00 / 1.00 / 1.00 | 0.06 / 0.00 / 1.00 | 0.05 / 0.00 / 1.00 | 0.07 / 0.00 / 1.00 | 0.07 / 0.00 / 1.00 | 0.03 / 0.67 / 1.00 | 0.00 / 1.00 / 1.00 | 0.22 / 0.35 / 0.94 |
| S_storychar_plain | 0.00 / 1.00 / 1.00 | 0.00 / 1.00 / 1.00 | 0.05 / 0.33 / 1.00 | 0.00 / 1.00 / 1.00 | 0.05 / 0.00 / 1.00 | 0.08 / 0.00 / 1.00 | 0.02 / 0.67 / 1.00 | 0.00 / 1.00 / 1.00 | 0.20 / 0.24 / 0.94 |
| S_storychar_inst | 0.00 / 1.00 / 1.00 | 0.00 / 1.00 / 1.00 | 0.05 / 0.33 / 1.00 | 0.00 / 1.00 / 1.00 | 0.07 / 0.00 / 1.00 | 0.07 / 0.00 / 1.00 | 0.02 / 0.67 / 1.00 | 0.00 / 1.00 / 1.00 | 0.19 / 0.29 / 0.94 |
| S_storychar_tfidf | 0.00 / 1.00 / 1.00 | 0.00 / 1.00 / 1.00 | 0.06 / 0.33 / 1.00 | 0.00 / 1.00 / 1.00 | 0.05 / 0.00 / 1.00 | 0.09 / 0.00 / 1.00 | 0.07 / 0.67 / 0.83 | 0.00 / 1.00 / 1.00 | 0.41 / 0.29 / 0.59 |
| W_digest_plain | 0.00 / 1.00 / 1.00 | 0.00 / 1.00 / 1.00 | 0.05 / 0.33 / 1.00 | 0.00 / 1.00 / 1.00 | 0.09 / 0.00 / 1.00 | 0.06 / 0.00 / 1.00 | 0.11 / 0.67 / 0.67 | 0.00 / 1.00 / 1.00 | 0.43 / 0.12 / 0.59 |
| W_digest_inst | 0.00 / 1.00 / 1.00 | 0.00 / 1.00 / 1.00 | 0.06 / 0.17 / 1.00 | 0.02 / 0.50 / 1.00 | 0.09 / 0.00 / 1.00 | 0.06 / 0.00 / 1.00 | 0.07 / 0.67 / 0.83 | 0.00 / 1.00 / 1.00 | 0.40 / 0.12 / 0.59 |
| W_digestsubj_plain | 0.00 / 1.00 / 1.00 | 0.00 / 1.00 / 1.00 | 0.05 / 0.33 / 1.00 | 0.00 / 1.00 / 1.00 | 0.07 / 0.00 / 1.00 | 0.07 / 0.00 / 1.00 | 0.13 / 0.67 / 0.67 | 0.00 / 1.00 / 1.00 | 0.32 / 0.18 / 0.76 |
| W_digest_tfidf | 0.00 / 1.00 / 1.00 | 0.00 / 1.00 / 1.00 | 0.14 / 0.00 / 0.67 | 0.43 / 0.00 / 0.00 | 0.05 / 0.00 / 1.00 | 0.08 / 0.00 / 1.00 | 0.03 / 0.50 / 1.00 | 0.00 / 1.00 / 1.00 | 0.55 / 0.12 / 0.47 |

Split-half self-retrieval (accuracy; chance is 1/n), and Spearman of distance with |year difference| and |log word-count difference| (Mantel p in brackets; en = both books written in English; diff = different authors only).

| block | n | input | split a/b | split h1/h2 | rho year | rho year en | rho year en diff | rho logwords | rho logwords diff |
|---|---|---|---|---|---|---|---|---|---|
| S_story_plain | 24 | ordered text |  |  | 0.09 (0.060) | -0.09 (0.195) | -0.15 | 0.01 (0.775) | -0.04 |
| S_story_inst | 24 | ordered text |  |  | 0.07 (0.220) | -0.07 (0.300) | -0.13 | -0.02 (0.690) | -0.07 |
| S_story_tfidf | 24 | ordered text |  |  | 0.14 (0.095) | 0.06 (0.645) | 0.00 | 0.12 (0.115) | 0.08 |
| S_characters_plain | 24 | ordered text |  |  | 0.11 (0.065) | -0.03 (0.645) | -0.09 | 0.04 (0.410) | -0.01 |
| S_characters_inst | 24 | ordered text |  |  | 0.13 (0.010) | -0.01 (0.905) | -0.07 | 0.02 (0.595) | -0.03 |
| S_storychar_plain | 24 | ordered text |  |  | 0.09 (0.065) | -0.07 (0.340) | -0.13 | 0.02 (0.735) | -0.03 |
| S_storychar_inst | 24 | ordered text |  |  | 0.10 (0.060) | -0.05 (0.485) | -0.11 | -0.01 (0.850) | -0.06 |
| S_storychar_tfidf | 24 | ordered text |  |  | 0.07 (0.475) | 0.03 (0.850) | -0.03 | 0.19 (0.065) | 0.16 |
| W_digest_plain | 24 | ordered text |  |  | 0.15 (0.005) | 0.07 (0.295) | 0.02 | -0.01 (0.820) | -0.07 |
| W_digest_inst | 24 | ordered text |  |  | 0.20 (0.005) | 0.12 (0.070) | 0.08 | -0.03 (0.535) | -0.09 |
| W_digestsubj_plain | 24 | ordered text |  |  | 0.14 (0.010) | 0.12 (0.135) | 0.08 | -0.06 (0.255) | -0.11 |
| W_digest_tfidf | 24 | ordered text |  |  | 0.22 (0.005) | 0.19 (0.100) | 0.16 | 0.04 (0.660) | -0.01 |

Top-5 neighbour make-up (observed / chance) and hubness (skew of the 5-nearest in-degree; share of books in nobody's top 5; largest in-degree and the book).

| block | same author | same genre | mean abs year diff | mean abs log-words diff | hub skew | in no top 5 | max in-degree |
|---|---|---|---|---|---|---|---|
| S_story_plain | 0.29 / 0.06 | 0.53 / 0.15 | 28 / 33 | 0.39 / 0.42 | -0.55 | 0.00 | 7 (wharton_frome) |
| S_story_inst | 0.29 / 0.06 | 0.53 / 0.15 | 28 / 33 | 0.41 / 0.42 | -0.49 | 0.00 | 7 (merriman_barlasch) |
| S_story_tfidf | 0.29 / 0.06 | 0.34 / 0.15 | 26 / 33 | 0.38 / 0.42 | 0.69 | 0.00 | 12 (fathers_garnett) |
| S_characters_plain | 0.29 / 0.06 | 0.44 / 0.15 | 24 / 33 | 0.36 / 0.42 | -0.49 | 0.00 | 7 (wells_time) |
| S_characters_inst | 0.29 / 0.06 | 0.49 / 0.15 | 26 / 33 | 0.35 / 0.42 | 0.35 | 0.00 | 9 (conrad_agent) |
| S_storychar_plain | 0.29 / 0.06 | 0.50 / 0.15 | 25 / 33 | 0.36 / 0.42 | 0.06 | 0.00 | 8 (merriman_barlasch) |
| S_storychar_inst | 0.29 / 0.06 | 0.53 / 0.15 | 26 / 33 | 0.39 / 0.42 | -0.44 | 0.00 | 8 (wells_time) |
| S_storychar_tfidf | 0.28 / 0.06 | 0.30 / 0.15 | 26 / 33 | 0.35 / 0.42 | 0.73 | 0.00 | 13 (fathers_garnett) |
| W_digest_plain | 0.27 / 0.06 | 0.31 / 0.15 | 24 / 33 | 0.37 / 0.42 | -0.18 | 0.00 | 8 (wells_worlds) |
| W_digest_inst | 0.28 / 0.06 | 0.30 / 0.15 | 24 / 33 | 0.39 / 0.42 | -0.11 | 0.00 | 8 (burnett_princess) |
| W_digestsubj_plain | 0.27 / 0.06 | 0.40 / 0.15 | 24 / 33 | 0.40 / 0.42 | 0.17 | 0.00 | 8 (wells_time) |
| W_digest_tfidf | 0.27 / 0.06 | 0.23 / 0.15 | 24 / 33 | 0.39 / 0.42 | 0.34 | 0.00 | 11 (holmes_hound) |

Spearman between the pair distances of two blocks, all pairs.

| block | S_story_plain | S_story_inst | S_story_tfidf | S_characters_plain | S_characters_inst | S_storychar_plain | S_storychar_inst | S_storychar_tfidf | W_digest_plain | W_digest_inst | W_digestsubj_plain | W_digest_tfidf |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| S_story_plain | 1.00 | 0.95 | 0.44 | 0.57 | 0.62 | 0.87 | 0.86 | 0.41 | 0.37 | 0.43 | 0.46 | 0.17 |
| S_story_inst | 0.95 | 1.00 | 0.42 | 0.58 | 0.64 | 0.84 | 0.90 | 0.39 | 0.35 | 0.41 | 0.45 | 0.16 |
| S_story_tfidf | 0.44 | 0.42 | 1.00 | 0.29 | 0.32 | 0.40 | 0.40 | 0.86 | 0.32 | 0.34 | 0.33 | 0.25 |
| S_characters_plain | 0.57 | 0.58 | 0.29 | 1.00 | 0.89 | 0.89 | 0.81 | 0.32 | 0.29 | 0.35 | 0.40 | 0.17 |
| S_characters_inst | 0.62 | 0.64 | 0.32 | 0.89 | 1.00 | 0.85 | 0.90 | 0.32 | 0.26 | 0.32 | 0.38 | 0.13 |
| S_storychar_plain | 0.87 | 0.84 | 0.40 | 0.89 | 0.85 | 1.00 | 0.94 | 0.40 | 0.35 | 0.42 | 0.47 | 0.19 |
| S_storychar_inst | 0.86 | 0.90 | 0.40 | 0.81 | 0.90 | 0.94 | 1.00 | 0.39 | 0.32 | 0.38 | 0.45 | 0.15 |
| S_storychar_tfidf | 0.41 | 0.39 | 0.86 | 0.32 | 0.32 | 0.40 | 0.39 | 1.00 | 0.32 | 0.33 | 0.34 | 0.29 |
| W_digest_plain | 0.37 | 0.35 | 0.32 | 0.29 | 0.26 | 0.35 | 0.32 | 0.32 | 1.00 | 0.89 | 0.86 | 0.52 |
| W_digest_inst | 0.43 | 0.41 | 0.34 | 0.35 | 0.32 | 0.42 | 0.38 | 0.33 | 0.89 | 1.00 | 0.82 | 0.43 |
| W_digestsubj_plain | 0.46 | 0.45 | 0.33 | 0.40 | 0.38 | 0.47 | 0.45 | 0.34 | 0.86 | 0.82 | 1.00 | 0.42 |
| W_digest_tfidf | 0.17 | 0.16 | 0.25 | 0.17 | 0.13 | 0.19 | 0.15 | 0.29 | 0.52 | 0.43 | 0.42 | 1.00 |

Spearman between the pair distances of two blocks, different-author pairs only.

| block | S_story_plain | S_story_inst | S_story_tfidf | S_characters_plain | S_characters_inst | S_storychar_plain | S_storychar_inst | S_storychar_tfidf | W_digest_plain | W_digest_inst | W_digestsubj_plain | W_digest_tfidf |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| S_story_plain | 1.00 | 0.95 | 0.35 | 0.50 | 0.56 | 0.84 | 0.84 | 0.32 | 0.29 | 0.34 | 0.39 | 0.05 |
| S_story_inst | 0.95 | 1.00 | 0.33 | 0.51 | 0.59 | 0.82 | 0.89 | 0.30 | 0.26 | 0.32 | 0.37 | 0.05 |
| S_story_tfidf | 0.35 | 0.33 | 1.00 | 0.18 | 0.22 | 0.31 | 0.31 | 0.84 | 0.22 | 0.24 | 0.23 | 0.15 |
| S_characters_plain | 0.50 | 0.51 | 0.18 | 1.00 | 0.87 | 0.88 | 0.77 | 0.21 | 0.19 | 0.25 | 0.32 | 0.06 |
| S_characters_inst | 0.56 | 0.59 | 0.22 | 0.87 | 1.00 | 0.83 | 0.89 | 0.22 | 0.16 | 0.22 | 0.29 | 0.01 |
| S_storychar_plain | 0.84 | 0.82 | 0.31 | 0.88 | 0.83 | 1.00 | 0.93 | 0.30 | 0.26 | 0.33 | 0.39 | 0.07 |
| S_storychar_inst | 0.84 | 0.89 | 0.31 | 0.77 | 0.89 | 0.93 | 1.00 | 0.29 | 0.23 | 0.29 | 0.37 | 0.03 |
| S_storychar_tfidf | 0.32 | 0.30 | 0.84 | 0.21 | 0.22 | 0.30 | 0.29 | 1.00 | 0.22 | 0.23 | 0.24 | 0.19 |
| W_digest_plain | 0.29 | 0.26 | 0.22 | 0.19 | 0.16 | 0.26 | 0.23 | 0.22 | 1.00 | 0.88 | 0.84 | 0.46 |
| W_digest_inst | 0.34 | 0.32 | 0.24 | 0.25 | 0.22 | 0.33 | 0.29 | 0.23 | 0.88 | 1.00 | 0.80 | 0.36 |
| W_digestsubj_plain | 0.39 | 0.37 | 0.23 | 0.32 | 0.29 | 0.39 | 0.37 | 0.24 | 0.84 | 0.80 | 1.00 | 0.34 |
| W_digest_tfidf | 0.05 | 0.05 | 0.15 | 0.06 | 0.01 | 0.07 | 0.03 | 0.19 | 0.46 | 0.36 | 0.34 | 1.00 |


Every labelled pair: rank of b from a / rank of a from b (1 = nearest), and in brackets the share of negative pairs that are farther apart.

| set | pair | S_story_plain | S_story_inst | S_story_tfidf | S_characters_plain | S_characters_inst | S_storychar_plain | S_storychar_inst | S_storychar_tfidf | W_digest_plain | W_digest_inst | W_digestsubj_plain | W_digest_tfidf |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| translation_pair | fathers_garnett ~ fathers_hogarth | 1 / 1 (1.00) | 1 / 1 (1.00) | 1 / 1 (1.00) | 1 / 1 (1.00) | 1 / 1 (1.00) | 1 / 1 (1.00) | 1 / 1 (1.00) | 1 / 1 (1.00) | 1 / 1 (1.00) | 1 / 1 (1.00) | 1 / 1 (1.00) | 1 / 1 (1.00) |
| translation_pair | gentlefolk_garnett ~ gentlefolk_ralston | 1 / 1 (1.00) | 1 / 1 (1.00) | 1 / 1 (1.00) | 1 / 1 (1.00) | 1 / 1 (1.00) | 1 / 1 (1.00) | 1 / 1 (1.00) | 1 / 1 (1.00) | 1 / 1 (1.00) | 1 / 1 (1.00) | 1 / 1 (1.00) | 1 / 1 (1.00) |
| translation_pair | journey_1871 ~ journey_malleson | 1 / 1 (1.00) | 1 / 1 (1.00) | 1 / 1 (1.00) | 1 / 1 (1.00) | 1 / 1 (1.00) | 1 / 1 (1.00) | 1 / 1 (1.00) | 1 / 1 (1.00) | 1 / 1 (1.00) | 1 / 1 (1.00) | 1 / 1 (1.00) | 1 / 1 (1.00) |
| edition_pair | frankenstein_1818 ~ frankenstein_1831 | 1 / 1 (1.00) | 1 / 1 (1.00) | 1 / 1 (1.00) | 1 / 1 (1.00) | 1 / 1 (1.00) | 1 / 1 (1.00) | 1 / 1 (1.00) | 1 / 1 (1.00) | 1 / 1 (1.00) | 1 / 1 (1.00) | 1 / 1 (1.00) | 1 / 1 (1.00) |
| retelling | burnett_princess ~ burnett_sara_crewe | 1 / 1 (1.00) | 1 / 1 (1.00) | 1 / 1 (1.00) | 1 / 1 (1.00) | 1 / 1 (1.00) | 1 / 1 (1.00) | 1 / 1 (1.00) | 1 / 1 (1.00) | 1 / 1 (0.99) | 1 / 1 (1.00) | 1 / 1 (1.00) | 1 / 1 (1.00) |
| series | holmes_hound ~ holmes_study | 1 / 3 (0.98) | 1 / 1 (1.00) | 2 / 3 (0.97) | 2 / 2 (0.99) | 3 / 3 (0.98) | 2 / 3 (0.98) | 2 / 3 (0.99) | 6 / 5 (0.91) | 10 / 6 (0.69) | 5 / 6 (0.81) | 10 / 9 (0.66) | 3 / 2 (0.94) |
| series | oz_land ~ oz_wizard | 1 / 1 (1.00) | 1 / 1 (1.00) | 1 / 1 (1.00) | 1 / 1 (1.00) | 1 / 1 (1.00) | 1 / 1 (1.00) | 1 / 1 (1.00) | 1 / 1 (1.00) | 1 / 1 (1.00) | 1 / 1 (1.00) | 1 / 1 (1.00) | 1 / 1 (1.00) |
| series | tarzan_apes ~ tarzan_return | 1 / 1 (0.95) | 3 / 4 (0.86) | 1 / 1 (1.00) | 1 / 1 (1.00) | 1 / 1 (1.00) | 1 / 1 (0.99) | 1 / 1 (0.98) | 1 / 1 (1.00) | 1 / 1 (1.00) | 1 / 1 (1.00) | 1 / 1 (1.00) | 1 / 2 (0.99) |
| same_author_unrelated | fathers_garnett ~ gentlefolk_garnett | 2 / 3 (0.99) | 2 / 2 (0.99) | 2 / 2 (1.00) | 2 / 2 (0.99) | 2 / 3 (0.99) | 2 / 2 (0.99) | 2 / 3 (0.99) | 2 / 2 (1.00) | 3 / 3 (0.93) | 3 / 3 (0.97) | 2 / 3 (0.99) | 2 / 2 (1.00) |
| same_author_unrelated | fathers_garnett ~ gentlefolk_ralston | 3 / 2 (0.98) | 3 / 2 (0.99) | 3 / 4 (0.97) | 3 / 2 (0.99) | 3 / 3 (0.98) | 3 / 2 (0.99) | 3 / 3 (0.98) | 3 / 3 (0.98) | 2 / 3 (0.99) | 2 / 3 (0.99) | 3 / 3 (0.99) | 3 / 3 (0.98) |
| same_author_unrelated | fathers_hogarth ~ gentlefolk_garnett | 3 / 4 (0.95) | 2 / 4 (0.98) | 2 / 3 (0.99) | 2 / 3 (0.99) | 2 / 2 (1.00) | 2 / 3 (0.98) | 2 / 2 (1.00) | 2 / 3 (0.98) | 2 / 2 (1.00) | 2 / 2 (1.00) | 2 / 2 (1.00) | 3 / 3 (0.98) |
| same_author_unrelated | fathers_hogarth ~ gentlefolk_ralston | 2 / 3 (0.98) | 3 / 3 (0.98) | 3 / 3 (0.98) | 3 / 3 (0.99) | 3 / 2 (0.99) | 3 / 3 (0.98) | 3 / 2 (0.99) | 3 / 4 (0.97) | 3 / 2 (1.00) | 3 / 2 (1.00) | 3 / 2 (1.00) | 2 / 2 (1.00) |
| same_author_unrelated | wells_time ~ wells_worlds | 1 / 1 (1.00) | 1 / 1 (0.99) | 1 / 1 (0.98) | 1 / 2 (0.94) | 2 / 2 (0.95) | 1 / 1 (0.98) | 1 / 1 (0.98) | 1 / 1 (0.99) | 1 / 1 (1.00) | 2 / 1 (0.98) | 1 / 1 (1.00) | 10 / 11 (0.70) |

### Story leak: from-text digests against title-only digests

#### (a) Does the from-text digest retrieve its own title-only digest?

| field | cosine | books | own title digest is rank 1 | mean rank | mean cos to own | mean cos to others | smallest margin over best other |
|---|---|---|---|---|---|---|---|
| story | raw | 23 | 22 | 1.04 | 0.75 | 0.43 | -0.06 |
| story | centred | 23 | 22 | 1.04 | 0.54 | -0.05 | -0.01 |
| characters | raw | 23 | 19 | 1.87 | 0.72 | 0.48 | -0.07 |
| characters | centred | 23 | 19 | 1.35 | 0.42 | -0.06 | -0.13 |
| world | raw | 23 | 22 | 1.04 | 0.78 | 0.56 | -0.09 |
| world | centred | 23 | 22 | 1.04 | 0.47 | -0.04 | -0.03 |
| subjects | raw | 23 | 20 | 1.17 | 0.73 | 0.46 | -0.08 |
| subjects | centred | 23 | 21 | 1.09 | 0.47 | -0.05 | -0.10 |

Per book, story field, centred cosine (best other includes the same work in another translation).

| id | key | recognised | at part | title-only memory | cos to own title digest | best other | rank of own |
|---|---|---|---|---|---|---|---|
| b01 | wharton_frome | True | 1 | confident | 0.58 | 0.21 | 1.00 |
| b02 | journey_1871 | True | 1 | confident | 0.58 | 0.54 | 1.00 |
| b03 | oz_land | True | 1 | partial | 0.43 | 0.39 | 1.00 |
| b04 | conrad_agent | True | 1 | confident | 0.58 | 0.12 | 1.00 |
| b05 | tarzan_return | True | 1 | partial | 0.18 | 0.19 | 2.00 |
| b06 | wells_worlds | True | 1 | confident | 0.62 | 0.20 | 1.00 |
| b07 | zamyatin_we | True | 1 | confident | 0.66 | 0.16 | 1.00 |
| b08 | fathers_garnett | True | 1 | confident | 0.50 | 0.47 | 1.00 |
| b09 | christie_styles | True | 3 | confident | 0.39 | 0.18 | 1.00 |
| b10 | merriman_barlasch | False | 0 | none |  | 0.15 |  |
| b11 | wells_time | True | 1 | confident | 0.64 | 0.24 | 1.00 |
| b12 | gentlefolk_ralston | True | 1 | confident | 0.57 | 0.39 | 1.00 |
| b13 | holmes_hound | True | 1 | confident | 0.64 | 0.20 | 1.00 |
| b14 | holmes_study | True | 1 | confident | 0.55 | 0.47 | 1.00 |
| b15 | oz_wizard | True | 1 | confident | 0.85 | 0.38 | 1.00 |
| b16 | hammett_falcon | True | 3 | confident | 0.69 | 0.27 | 1.00 |
| b17 | frankenstein_1818 | True | 1 | confident | 0.43 | 0.45 | 1.00 |
| b18 | gentlefolk_garnett | True | 1 | confident | 0.42 | 0.48 | 1.00 |
| b19 | burnett_princess | True | 1 | confident | 0.67 | 0.61 | 1.00 |
| b20 | journey_malleson | True | 1 | confident | 0.49 | 0.54 | 1.00 |
| b21 | frankenstein_1831 | True | 1 | confident | 0.61 | 0.63 | 1.00 |
| b22 | tarzan_apes | True | 1 | confident | 0.46 | 0.36 | 1.00 |
| b23 | fathers_hogarth | True | 1 | confident | 0.44 | 0.46 | 1.00 |
| b24 | burnett_sara_crewe | True | 1 | confident | 0.54 | 0.62 | 1.00 |

#### (b) Two independent readings of one work, against memory

If `text a ~ text b` is above both `text ~ title` columns, the two readings agree with each other more than either agrees with what the model remembers from the title.

| field | cosine | set | pair | text a ~ text b | text a ~ title a | text b ~ title b | text a ~ title b | text b ~ title a | title a ~ title b | median text ~ text, all pairs |
|---|---|---|---|---|---|---|---|---|---|---|
| story | raw | translation_pair | fathers_garnett ~ fathers_hogarth | 0.85 | 0.77 | 0.73 | 0.77 | 0.74 | 0.91 | 0.47 |
| story | raw | translation_pair | gentlefolk_garnett ~ gentlefolk_ralston | 0.80 | 0.68 | 0.76 | 0.71 | 0.68 | 0.86 | 0.47 |
| story | raw | translation_pair | journey_1871 ~ journey_malleson | 0.91 | 0.77 | 0.69 | 0.72 | 0.76 | 0.85 | 0.47 |
| story | raw | edition_pair | frankenstein_1818 ~ frankenstein_1831 | 0.78 | 0.74 | 0.83 | 0.75 | 0.84 | 0.90 | 0.47 |
| story | raw | retelling | burnett_princess ~ burnett_sara_crewe | 0.83 | 0.83 | 0.75 | 0.80 | 0.80 | 0.87 | 0.47 |
| story | centred | translation_pair | fathers_garnett ~ fathers_hogarth | 0.68 | 0.50 | 0.44 | 0.47 | 0.46 | 0.80 | -0.04 |
| story | centred | translation_pair | gentlefolk_garnett ~ gentlefolk_ralston | 0.60 | 0.42 | 0.57 | 0.48 | 0.39 | 0.76 | -0.04 |
| story | centred | translation_pair | journey_1871 ~ journey_malleson | 0.81 | 0.58 | 0.49 | 0.54 | 0.54 | 0.78 | -0.04 |
| story | centred | edition_pair | frankenstein_1818 ~ frankenstein_1831 | 0.46 | 0.43 | 0.61 | 0.45 | 0.63 | 0.78 | -0.04 |
| story | centred | retelling | burnett_princess ~ burnett_sara_crewe | 0.66 | 0.67 | 0.54 | 0.61 | 0.62 | 0.76 | -0.04 |
| characters | raw | translation_pair | fathers_garnett ~ fathers_hogarth | 0.92 | 0.65 | 0.60 | 0.65 | 0.63 | 0.88 | 0.53 |
| characters | raw | translation_pair | gentlefolk_garnett ~ gentlefolk_ralston | 0.80 | 0.76 | 0.72 | 0.74 | 0.72 | 0.91 | 0.53 |
| characters | raw | translation_pair | journey_1871 ~ journey_malleson | 0.79 | 0.71 | 0.71 | 0.68 | 0.70 | 0.91 | 0.53 |
| characters | raw | edition_pair | frankenstein_1818 ~ frankenstein_1831 | 0.79 | 0.78 | 0.75 | 0.62 | 0.87 | 0.80 | 0.53 |
| characters | raw | retelling | burnett_princess ~ burnett_sara_crewe | 0.86 | 0.85 | 0.77 | 0.83 | 0.78 | 0.96 | 0.53 |
| characters | centred | translation_pair | fathers_garnett ~ fathers_hogarth | 0.82 | 0.19 | 0.15 | 0.22 | 0.18 | 0.76 | -0.03 |
| characters | centred | translation_pair | gentlefolk_garnett ~ gentlefolk_ralston | 0.52 | 0.42 | 0.37 | 0.36 | 0.37 | 0.80 | -0.03 |
| characters | centred | translation_pair | journey_1871 ~ journey_malleson | 0.49 | 0.36 | 0.44 | 0.35 | 0.39 | 0.84 | -0.03 |
| characters | centred | edition_pair | frankenstein_1818 ~ frankenstein_1831 | 0.54 | 0.54 | 0.45 | 0.22 | 0.70 | 0.59 | -0.03 |
| characters | centred | retelling | burnett_princess ~ burnett_sara_crewe | 0.69 | 0.64 | 0.49 | 0.58 | 0.51 | 0.91 | -0.03 |
| world | raw | translation_pair | fathers_garnett ~ fathers_hogarth | 0.81 | 0.85 | 0.81 | 0.85 | 0.82 | 0.98 | 0.59 |
| world | raw | translation_pair | gentlefolk_garnett ~ gentlefolk_ralston | 0.85 | 0.85 | 0.84 | 0.83 | 0.84 | 0.96 | 0.59 |
| world | raw | translation_pair | journey_1871 ~ journey_malleson | 0.85 | 0.76 | 0.79 | 0.76 | 0.80 | 0.93 | 0.59 |
| world | raw | edition_pair | frankenstein_1818 ~ frankenstein_1831 | 0.87 | 0.80 | 0.80 | 0.79 | 0.77 | 0.92 | 0.59 |
| world | raw | retelling | burnett_princess ~ burnett_sara_crewe | 0.74 | 0.78 | 0.79 | 0.77 | 0.82 | 0.98 | 0.59 |
| world | centred | translation_pair | fathers_garnett ~ fathers_hogarth | 0.44 | 0.51 | 0.42 | 0.55 | 0.43 | 0.92 | -0.04 |
| world | centred | translation_pair | gentlefolk_garnett ~ gentlefolk_ralston | 0.57 | 0.59 | 0.57 | 0.55 | 0.53 | 0.91 | -0.04 |
| world | centred | translation_pair | journey_1871 ~ journey_malleson | 0.55 | 0.38 | 0.50 | 0.44 | 0.48 | 0.85 | -0.04 |
| world | centred | edition_pair | frankenstein_1818 ~ frankenstein_1831 | 0.68 | 0.53 | 0.47 | 0.49 | 0.42 | 0.80 | -0.04 |
| world | centred | retelling | burnett_princess ~ burnett_sara_crewe | 0.26 | 0.35 | 0.42 | 0.33 | 0.50 | 0.93 | -0.04 |

| field | cosine | pairs where the readings agree more | pairs |
|---|---|---|---|
| characters | centred | 4 | 5 |
| characters | raw | 5 | 5 |
| story | centred | 3 | 5 |
| story | raw | 3 | 5 |
| world | centred | 2 | 5 |
| world | raw | 3 | 5 |

#### (c) From-text against title-only pair similarities

| field | books | pairs | Spearman, from-text vs title-only pair similarity |
|---|---|---|---|
| story | 23 | 253 | 0.66 |
| characters | 23 | 253 | 0.53 |
| world | 23 | 253 | 0.56 |
| subjects | 23 | 253 | 0.59 |


### From-text against title-only blocks, 23 books

AUC that a labelled pair is closer than a negative pair (240 negatives; [95% bootstrap interval over the labelled pairs]). n = labelled pairs.

| block | translation_pair (n=3) | edition_pair (n=1) | same_author_unrelated (n=5) | same_author_orig_en (n=1) | same_author_same_translator (n=1) | same_author_diff_translator (n=3) | series (n=3) | retelling (n=1) | same_genre (n=24) |
|---|---|---|---|---|---|---|---|---|---|
| S_story_plain | 1.00 [1.00, 1.00] | 1.00 | 0.98 [0.97, 0.99] | 1.00 | 0.99 | 0.97 [0.96, 0.99] | 0.98 [0.95, 1.00] | 1.00 | 0.84 [0.76, 0.91] |
| SM_story_plain | 1.00 [1.00, 1.00] | 1.00 | 0.94 [0.91, 0.96] | 0.98 | 0.89 | 0.94 [0.91, 0.96] | 0.97 [0.91, 1.00] | 1.00 | 0.83 [0.74, 0.90] |
| S_storychar_plain | 1.00 [1.00, 1.00] | 1.00 | 0.99 [0.98, 0.99] | 0.98 | 0.99 | 0.98 [0.98, 0.99] | 0.99 [0.98, 1.00] | 1.00 | 0.83 [0.77, 0.90] |
| SM_storychar_plain | 1.00 [1.00, 1.00] | 1.00 | 0.94 [0.92, 0.95] | 0.95 | 0.91 | 0.94 [0.93, 0.95] | 0.97 [0.95, 1.00] | 1.00 | 0.79 [0.70, 0.87] |
| S_story_tfidf | 1.00 [1.00, 1.00] | 1.00 | 0.98 [0.98, 0.99] | 0.98 | 1.00 | 0.98 [0.97, 0.99] | 0.99 [0.97, 1.00] | 1.00 | 0.57 [0.45, 0.69] |
| SM_story_tfidf | 1.00 [1.00, 1.00] | 1.00 | 0.91 [0.77, 0.98] | 0.62 | 0.97 | 0.98 [0.97, 0.98] | 1.00 [0.99, 1.00] | 1.00 | 0.62 [0.51, 0.73] |
| W_digest_plain | 1.00 [1.00, 1.00] | 1.00 | 0.98 [0.96, 1.00] | 1.00 | 0.94 | 1.00 [0.99, 1.00] | 0.90 [0.69, 1.00] | 0.99 | 0.60 [0.48, 0.71] |
| WM_digest_plain | 1.00 [1.00, 1.00] | 1.00 | 1.00 [1.00, 1.00] | 1.00 | 1.00 | 1.00 [1.00, 1.00] | 0.83 [0.50, 1.00] | 1.00 | 0.67 [0.57, 0.76] |
| F_reader | 0.99 [0.99, 1.00] | 1.00 | 0.97 [0.93, 1.00] | 0.89 | 0.99 | 1.00 [1.00, 1.00] | 0.99 [0.98, 1.00] | 1.00 | 0.77 [0.68, 0.85] |
| FM_title | 1.00 [1.00, 1.00] | 1.00 | 0.99 [0.98, 1.00] | 0.97 | 1.00 | 1.00 [1.00, 1.00] | 0.97 [0.91, 1.00] | 1.00 | 0.80 [0.72, 0.88] |

Mean percentile rank of the partner (0 = nearest book) / recall@1 / recall@5.

| block | translation_pair (n=3) | edition_pair (n=1) | same_author_unrelated (n=5) | same_author_orig_en (n=1) | same_author_same_translator (n=1) | same_author_diff_translator (n=3) | series (n=3) | retelling (n=1) | same_genre (n=24) |
|---|---|---|---|---|---|---|---|---|---|
| S_story_plain | 0.00 / 1.00 / 1.00 | 0.00 / 1.00 / 1.00 | 0.06 / 0.33 / 1.00 | 0.00 / 1.00 / 1.00 | 0.05 / 0.00 / 1.00 | 0.08 / 0.00 / 1.00 | 0.02 / 0.83 / 1.00 | 0.00 / 1.00 / 1.00 | 0.19 / 0.29 / 1.00 |
| SM_story_plain | 0.00 / 1.00 / 1.00 | 0.00 / 1.00 / 1.00 | 0.08 / 0.33 / 1.00 | 0.00 / 1.00 / 1.00 | 0.14 / 0.00 / 1.00 | 0.09 / 0.00 / 1.00 | 0.03 / 0.67 / 1.00 | 0.00 / 1.00 / 1.00 | 0.19 / 0.29 / 1.00 |
| S_storychar_plain | 0.00 / 1.00 / 1.00 | 0.00 / 1.00 / 1.00 | 0.06 / 0.33 / 1.00 | 0.00 / 1.00 / 1.00 | 0.05 / 0.00 / 1.00 | 0.08 / 0.00 / 1.00 | 0.02 / 0.67 / 1.00 | 0.00 / 1.00 / 1.00 | 0.20 / 0.29 / 1.00 |
| SM_storychar_plain | 0.00 / 1.00 / 1.00 | 0.00 / 1.00 / 1.00 | 0.09 / 0.33 / 1.00 | 0.00 / 1.00 / 1.00 | 0.17 / 0.00 / 0.50 | 0.10 / 0.00 / 1.00 | 0.03 / 0.67 / 1.00 | 0.00 / 1.00 / 1.00 | 0.23 / 0.29 / 1.00 |
| S_story_tfidf | 0.00 / 1.00 / 1.00 | 0.00 / 1.00 / 1.00 | 0.07 / 0.33 / 1.00 | 0.00 / 1.00 / 1.00 | 0.05 / 0.00 / 1.00 | 0.10 / 0.00 / 1.00 | 0.02 / 0.67 / 1.00 | 0.00 / 1.00 / 1.00 | 0.41 / 0.21 / 0.71 |
| SM_story_tfidf | 0.00 / 1.00 / 1.00 | 0.00 / 1.00 / 1.00 | 0.15 / 0.00 / 0.67 | 0.48 / 0.00 / 0.00 | 0.10 / 0.00 / 1.00 | 0.06 / 0.00 / 1.00 | 0.01 / 0.83 / 1.00 | 0.00 / 1.00 / 1.00 | 0.36 / 0.21 / 0.71 |
| W_digest_plain | 0.00 / 1.00 / 1.00 | 0.00 / 1.00 / 1.00 | 0.06 / 0.33 / 1.00 | 0.00 / 1.00 / 1.00 | 0.10 / 0.00 / 1.00 | 0.06 / 0.00 / 1.00 | 0.10 / 0.67 / 0.83 | 0.00 / 1.00 / 1.00 | 0.43 / 0.14 / 0.64 |
| WM_digest_plain | 0.00 / 1.00 / 1.00 | 0.00 / 1.00 / 1.00 | 0.06 / 0.17 / 1.00 | 0.02 / 0.50 / 1.00 | 0.07 / 0.00 / 1.00 | 0.07 / 0.00 / 1.00 | 0.25 / 0.67 / 0.67 | 0.00 / 1.00 / 1.00 | 0.38 / 0.07 / 0.71 |
| F_reader | 0.04 / 0.33 / 1.00 | 0.00 / 1.00 / 1.00 | 0.07 / 0.67 / 0.83 | 0.17 / 0.00 / 0.50 | 0.10 / 0.00 / 1.00 | 0.02 / 1.00 / 1.00 | 0.02 / 0.83 / 1.00 | 0.00 / 1.00 / 1.00 | 0.27 / 0.21 / 1.00 |
| FM_title | 0.00 / 1.00 / 1.00 | 0.00 / 1.00 / 1.00 | 0.06 / 0.33 / 1.00 | 0.00 / 1.00 / 1.00 | 0.08 / 0.00 / 1.00 | 0.07 / 0.00 / 1.00 | 0.02 / 0.83 / 1.00 | 0.00 / 1.00 / 1.00 | 0.23 / 0.21 / 0.93 |

Split-half self-retrieval (accuracy; chance is 1/n), and Spearman of distance with |year difference| and |log word-count difference| (Mantel p in brackets; en = both books written in English; diff = different authors only).

| block | n | input | split a/b | split h1/h2 | rho year | rho year en | rho year en diff | rho logwords | rho logwords diff |
|---|---|---|---|---|---|---|---|---|---|
| S_story_plain | 23 | ordered text |  |  | 0.11 (0.065) | -0.06 (0.440) | -0.14 | -0.00 (0.915) | -0.06 |
| SM_story_plain | 23 | ordered text |  |  | 0.11 (0.070) | 0.03 (0.750) | -0.04 | 0.02 (0.660) | -0.03 |
| S_storychar_plain | 23 | ordered text |  |  | 0.10 (0.100) | -0.05 (0.550) | -0.13 | -0.01 (0.795) | -0.07 |
| SM_storychar_plain | 23 | ordered text |  |  | 0.14 (0.020) | -0.01 (0.895) | -0.08 | -0.01 (0.900) | -0.07 |
| S_story_tfidf | 23 | ordered text |  |  | 0.14 (0.075) | 0.05 (0.720) | -0.02 | 0.09 (0.305) | 0.04 |
| SM_story_tfidf | 23 | ordered text |  |  | 0.10 (0.245) | 0.01 (0.945) | -0.04 | 0.02 (0.830) | -0.04 |
| W_digest_plain | 23 | ordered text |  |  | 0.16 (0.015) | 0.12 (0.130) | 0.06 | 0.00 (0.935) | -0.06 |
| WM_digest_plain | 23 | ordered text |  |  | 0.23 (0.005) | 0.16 (0.065) | 0.11 | -0.02 (0.785) | -0.08 |
| F_reader | 23 | ordered text |  |  | 0.03 (0.585) | -0.01 (0.855) | -0.08 | -0.04 (0.275) | -0.11 |
| FM_title | 23 | ordered text |  |  | 0.06 (0.275) | -0.01 (0.930) | -0.08 | -0.06 (0.255) | -0.12 |

Top-5 neighbour make-up (observed / chance) and hubness (skew of the 5-nearest in-degree; share of books in nobody's top 5; largest in-degree and the book).

| block | same author | same genre | mean abs year diff | mean abs log-words diff | hub skew | in no top 5 | max in-degree |
|---|---|---|---|---|---|---|---|
| S_story_plain | 0.29 / 0.07 | 0.56 / 0.16 | 27 / 34 | 0.44 / 0.42 | -0.49 | 0.00 | 7 (wharton_frome) |
| SM_story_plain | 0.29 / 0.07 | 0.53 / 0.16 | 28 / 34 | 0.40 / 0.42 | -0.49 | 0.00 | 7 (fathers_garnett) |
| S_storychar_plain | 0.29 / 0.07 | 0.51 / 0.16 | 24 / 34 | 0.39 / 0.42 | 0.00 | 0.00 | 8 (wells_time) |
| SM_storychar_plain | 0.28 / 0.07 | 0.51 / 0.16 | 27 / 34 | 0.41 / 0.42 | 0.55 | 0.00 | 9 (wells_time) |
| S_story_tfidf | 0.29 / 0.07 | 0.35 / 0.16 | 26 / 34 | 0.40 / 0.42 | 1.17 | 0.00 | 14 (fathers_garnett) |
| SM_story_tfidf | 0.27 / 0.07 | 0.34 / 0.16 | 24 / 34 | 0.41 / 0.42 | 0.90 | 0.00 | 13 (wharton_frome) |
| W_digest_plain | 0.28 / 0.07 | 0.33 / 0.16 | 25 / 34 | 0.38 / 0.42 | 0.10 | 0.00 | 8 (wells_worlds) |
| WM_digest_plain | 0.27 / 0.07 | 0.29 / 0.16 | 26 / 34 | 0.39 / 0.42 | 0.27 | 0.00 | 8 (wharton_frome) |
| F_reader | 0.28 / 0.07 | 0.42 / 0.16 | 28 / 34 | 0.46 / 0.42 | 0.52 | 0.00 | 9 (zamyatin_we) |
| FM_title | 0.28 / 0.07 | 0.46 / 0.16 | 31 / 34 | 0.45 / 0.42 | 0.34 | 0.00 | 8 (conrad_agent) |

Spearman between the pair distances of two blocks, all pairs.

| block | S_story_plain | SM_story_plain | S_storychar_plain | SM_storychar_plain | S_story_tfidf | SM_story_tfidf | W_digest_plain | WM_digest_plain | F_reader | FM_title |
|---|---|---|---|---|---|---|---|---|---|---|
| S_story_plain | 1.00 | 0.68 | 0.86 | 0.67 | 0.45 | 0.35 | 0.37 | 0.41 | 0.37 | 0.36 |
| SM_story_plain | 0.68 | 1.00 | 0.70 | 0.89 | 0.42 | 0.51 | 0.46 | 0.56 | 0.41 | 0.48 |
| S_storychar_plain | 0.86 | 0.70 | 1.00 | 0.72 | 0.40 | 0.33 | 0.34 | 0.37 | 0.48 | 0.46 |
| SM_storychar_plain | 0.67 | 0.89 | 0.72 | 1.00 | 0.43 | 0.46 | 0.35 | 0.48 | 0.42 | 0.48 |
| S_story_tfidf | 0.45 | 0.42 | 0.40 | 0.43 | 1.00 | 0.43 | 0.33 | 0.32 | 0.18 | 0.17 |
| SM_story_tfidf | 0.35 | 0.51 | 0.33 | 0.46 | 0.43 | 1.00 | 0.34 | 0.45 | 0.29 | 0.27 |
| W_digest_plain | 0.37 | 0.46 | 0.34 | 0.35 | 0.33 | 0.34 | 1.00 | 0.61 | 0.30 | 0.27 |
| WM_digest_plain | 0.41 | 0.56 | 0.37 | 0.48 | 0.32 | 0.45 | 0.61 | 1.00 | 0.37 | 0.35 |
| F_reader | 0.37 | 0.41 | 0.48 | 0.42 | 0.18 | 0.29 | 0.30 | 0.37 | 1.00 | 0.84 |
| FM_title | 0.36 | 0.48 | 0.46 | 0.48 | 0.17 | 0.27 | 0.27 | 0.35 | 0.84 | 1.00 |

Spearman between the pair distances of two blocks, different-author pairs only.

| block | S_story_plain | SM_story_plain | S_storychar_plain | SM_storychar_plain | S_story_tfidf | SM_story_tfidf | W_digest_plain | WM_digest_plain | F_reader | FM_title |
|---|---|---|---|---|---|---|---|---|---|---|
| S_story_plain | 1.00 | 0.63 | 0.84 | 0.61 | 0.36 | 0.24 | 0.28 | 0.32 | 0.26 | 0.25 |
| SM_story_plain | 0.63 | 1.00 | 0.65 | 0.87 | 0.33 | 0.44 | 0.38 | 0.50 | 0.32 | 0.39 |
| S_storychar_plain | 0.84 | 0.65 | 1.00 | 0.68 | 0.29 | 0.22 | 0.24 | 0.27 | 0.39 | 0.37 |
| SM_storychar_plain | 0.61 | 0.87 | 0.68 | 1.00 | 0.34 | 0.37 | 0.25 | 0.41 | 0.32 | 0.40 |
| S_story_tfidf | 0.36 | 0.33 | 0.29 | 0.34 | 1.00 | 0.34 | 0.23 | 0.22 | 0.04 | 0.03 |
| SM_story_tfidf | 0.24 | 0.44 | 0.22 | 0.37 | 0.34 | 1.00 | 0.24 | 0.38 | 0.18 | 0.16 |
| W_digest_plain | 0.28 | 0.38 | 0.24 | 0.25 | 0.23 | 0.24 | 1.00 | 0.56 | 0.20 | 0.16 |
| WM_digest_plain | 0.32 | 0.50 | 0.27 | 0.41 | 0.22 | 0.38 | 0.56 | 1.00 | 0.28 | 0.25 |
| F_reader | 0.26 | 0.32 | 0.39 | 0.32 | 0.04 | 0.18 | 0.20 | 0.28 | 1.00 | 0.82 |
| FM_title | 0.25 | 0.39 | 0.37 | 0.40 | 0.03 | 0.16 | 0.16 | 0.25 | 0.82 | 1.00 |


Every labelled pair: rank of b from a / rank of a from b (1 = nearest), and in brackets the share of negative pairs that are farther apart.

| set | pair | S_story_plain | SM_story_plain | S_storychar_plain | SM_storychar_plain | S_story_tfidf | SM_story_tfidf | W_digest_plain | WM_digest_plain | F_reader | FM_title |
|---|---|---|---|---|---|---|---|---|---|---|---|
| translation_pair | fathers_garnett ~ fathers_hogarth | 1 / 1 (1.00) | 1 / 1 (1.00) | 1 / 1 (1.00) | 1 / 1 (1.00) | 1 / 1 (1.00) | 1 / 1 (1.00) | 1 / 1 (1.00) | 1 / 1 (1.00) | 2 / 3 (0.99) | 1 / 1 (1.00) |
| translation_pair | gentlefolk_garnett ~ gentlefolk_ralston | 1 / 1 (1.00) | 1 / 1 (1.00) | 1 / 1 (1.00) | 1 / 1 (1.00) | 1 / 1 (1.00) | 1 / 1 (1.00) | 1 / 1 (1.00) | 1 / 1 (1.00) | 2 / 2 (1.00) | 1 / 1 (1.00) |
| translation_pair | journey_1871 ~ journey_malleson | 1 / 1 (1.00) | 1 / 1 (1.00) | 1 / 1 (1.00) | 1 / 1 (1.00) | 1 / 1 (1.00) | 1 / 1 (1.00) | 1 / 1 (1.00) | 1 / 1 (1.00) | 1 / 1 (0.99) | 1 / 1 (1.00) |
| edition_pair | frankenstein_1818 ~ frankenstein_1831 | 1 / 1 (1.00) | 1 / 1 (1.00) | 1 / 1 (1.00) | 1 / 1 (1.00) | 1 / 1 (1.00) | 1 / 1 (1.00) | 1 / 1 (1.00) | 1 / 1 (1.00) | 1 / 1 (1.00) | 1 / 1 (1.00) |
| retelling | burnett_princess ~ burnett_sara_crewe | 1 / 1 (1.00) | 1 / 1 (1.00) | 1 / 1 (1.00) | 1 / 1 (1.00) | 1 / 1 (1.00) | 1 / 1 (1.00) | 1 / 1 (0.99) | 1 / 1 (1.00) | 1 / 1 (1.00) | 1 / 1 (1.00) |
| series | holmes_hound ~ holmes_study | 1 / 3 (0.99) | 3 / 3 (0.91) | 2 / 3 (0.98) | 3 / 3 (0.95) | 2 / 3 (0.97) | 2 / 1 (0.99) | 10 / 5 (0.69) | 17 / 16 (0.50) | 3 / 1 (0.98) | 1 / 3 (0.91) |
| series | oz_land ~ oz_wizard | 1 / 1 (1.00) | 1 / 1 (1.00) | 1 / 1 (1.00) | 1 / 1 (0.97) | 1 / 1 (1.00) | 1 / 1 (1.00) | 1 / 1 (1.00) | 1 / 1 (1.00) | 1 / 1 (1.00) | 1 / 1 (1.00) |
| series | tarzan_apes ~ tarzan_return | 1 / 1 (0.95) | 1 / 1 (1.00) | 1 / 1 (0.99) | 1 / 1 (1.00) | 1 / 1 (1.00) | 1 / 1 (1.00) | 1 / 1 (1.00) | 1 / 1 (1.00) | 1 / 1 (1.00) | 1 / 1 (1.00) |
| same_author_unrelated | fathers_garnett ~ gentlefolk_garnett | 2 / 2 (0.99) | 4 / 4 (0.89) | 2 / 2 (0.99) | 3 / 6 (0.91) | 2 / 2 (1.00) | 3 / 3 (0.97) | 3 / 3 (0.94) | 2 / 3 (1.00) | 3 / 3 (0.99) | 3 / 2 (1.00) |
| same_author_unrelated | fathers_garnett ~ gentlefolk_ralston | 3 / 2 (0.99) | 2 / 4 (0.91) | 3 / 2 (0.99) | 2 / 5 (0.93) | 3 / 4 (0.97) | 2 / 3 (0.97) | 2 / 3 (0.99) | 3 / 3 (1.00) | 1 / 1 (1.00) | 2 / 2 (1.00) |
| same_author_unrelated | fathers_hogarth ~ gentlefolk_garnett | 3 / 3 (0.96) | 3 / 3 (0.95) | 2 / 3 (0.98) | 3 / 3 (0.95) | 2 / 3 (0.99) | 3 / 2 (0.97) | 2 / 2 (1.00) | 2 / 2 (1.00) | 1 / 1 (1.00) | 3 / 2 (1.00) |
| same_author_unrelated | fathers_hogarth ~ gentlefolk_ralston | 2 / 3 (0.98) | 2 / 3 (0.96) | 3 / 3 (0.98) | 2 / 3 (0.95) | 3 / 3 (0.98) | 2 / 2 (0.98) | 3 / 2 (1.00) | 3 / 2 (1.00) | 2 / 3 (1.00) | 2 / 2 (1.00) |
| same_author_unrelated | wells_time ~ wells_worlds | 1 / 1 (1.00) | 1 / 1 (0.98) | 1 / 1 (0.98) | 1 / 1 (0.95) | 1 / 1 (0.98) | 11 / 11 (0.62) | 1 / 1 (1.00) | 1 / 2 (1.00) | 3 / 6 (0.89) | 1 / 1 (0.97) |

### Reader's telling field against the counted Telling features (24 books)

| id | key | reader person | reader frame | reader order | first-sg / 1000 narration | third / 1000 narration | dialogue share | counted person | quote flag | agree |
|---|---|---|---|---|---|---|---|---|---|---|
| b01 | wharton_frome | mixed | framed | flashbacks | 8.07 | 100.96 | 0.21 | third |  | mixed |
| b02 | journey_1871 | first | framed | chronological | 47.03 | 22.59 | 0.22 | first |  | yes |
| b03 | oz_land | mixed | framed | chronological | 0.53 | 57.19 | 0.42 | third |  | mixed |
| b04 | conrad_agent | mixed | framed | chronological | 1.98 | 71.79 | 0.25 | third |  | mixed |
| b05 | tarzan_return | third | none | chronological | 0.52 | 85.64 | 0.26 | third |  | yes |
| b06 | wells_worlds | first | framed | chronological | 35.17 | 27.97 | 0.09 | first |  | yes |
| b07 | zamyatin_we | first | letters or documents | chronological | 60.87 | 31.70 | 0.19 | first |  | yes |
| b08 | fathers_garnett | third | none | chronological | 0.02 | 97.95 | 0.44 | third |  | yes |
| b09 | christie_styles | first | framed | chronological | 45.66 | 61.91 | 0.60 | first |  | yes |
| b10 | merriman_barlasch | third | none | chronological | 0.44 | 75.87 | 0.25 | third |  | yes |
| b11 | wells_time | first | framed | chronological | 27.74 | 56.21 | 0.87 | first | ALMOST_ALL_QUOTED (unbalanced marks or framed narration?) | yes |
| b12 | gentlefolk_ralston | third | none | flashbacks | 0.16 | 99.64 | 0.28 | third |  | yes |
| b13 | holmes_hound | first | letters or documents | chronological | 33.13 | 46.65 | 0.59 | first |  | yes |
| b14 | holmes_study | mixed | multiple narrators | flashbacks | 19.60 | 72.76 | 0.50 | first |  | mixed |
| b15 | oz_wizard | third | none | chronological | 0.00 | 81.72 | 0.39 | third |  | yes |
| b16 | hammett_falcon | third | none | chronological | 0.00 | 116.16 | 0.50 | third |  | yes |
| b17 | frankenstein_1818 | first | multiple narrators | flashbacks | 75.53 | 33.81 | 0.42 | first |  | yes |
| b18 | gentlefolk_garnett | third | none | flashbacks | 0.18 | 102.09 | 0.28 | third |  | yes |
| b19 | burnett_princess | mixed | framed | chronological | 0.83 | 100.39 | 0.35 | third |  | mixed |
| b20 | journey_malleson | first | letters or documents | chronological | 45.97 | 25.69 | 0.23 | first |  | yes |
| b21 | frankenstein_1831 | first | multiple narrators | flashbacks | 74.90 | 34.92 | 0.39 | first |  | yes |
| b22 | tarzan_apes | mixed | framed | chronological | 1.58 | 77.75 | 0.16 | third |  | mixed |
| b23 | fathers_hogarth | third | none | chronological | 0.19 | 84.91 | 0.47 | third |  | yes |
| b24 | burnett_sara_crewe | third | none | chronological | 0.59 | 101.11 | 0.30 | third |  | yes |

Reader says first: 9 books; third: 9; mixed: 6. Probability that a book the reader calls first-person has a higher counted first-singular rate than one it calls third-person: 1.00. Agreement of the thresholded count with the reader on the first / third books: 18 of 18.

| reader person | first-sg / 1000 narration mean | first-sg / 1000 narration min | first-sg / 1000 narration max | third / 1000 narration mean | third / 1000 narration min | third / 1000 narration max | dialogue share mean | dialogue share min | dialogue share max |
|---|---|---|---|---|---|---|---|---|---|
| first | 49.56 | 27.74 | 75.53 | 37.94 | 22.59 | 61.91 | 0.40 | 0.09 | 0.87 |
| mixed | 5.43 | 0.53 | 19.60 | 80.14 | 57.19 | 100.96 | 0.31 | 0.16 | 0.50 |
| third | 0.23 | 0.00 | 0.59 | 93.90 | 75.87 | 116.16 | 0.35 | 0.25 | 0.50 |

### Felt: the reader's 24 word scores

#### Is the scale used?

| source | share of 0s | share of 1s | share of 2s | share of 3s | mean | mean per-book sd |
|---|---|---|---|---|---|---|
| from text (24 books) | 0.14 | 0.39 | 0.36 | 0.12 | 1.45 | 0.83 |
| title only (23 books) | 0.38 | 0.33 | 0.19 | 0.11 | 1.03 | 0.95 |

Per word, from text.

| word | mean | sd across books | 0 | 1 | 2 | 3 | Spearman text vs title (23 books) |
|---|---|---|---|---|---|---|---|
| tense | 2.29 | 0.61 | 0 | 2 | 13 | 9 | 0.58 |
| anxious | 2.04 | 0.73 | 0 | 6 | 11 | 7 | 0.71 |
| melancholy | 1.92 | 0.70 | 0 | 7 | 12 | 5 | 0.85 |
| desolate | 1.88 | 0.93 | 2 | 6 | 9 | 7 | 0.80 |
| menacing | 1.79 | 0.87 | 1 | 9 | 8 | 6 | 0.89 |
| grotesque | 1.67 | 0.55 | 0 | 9 | 14 | 1 | 0.85 |
| cold | 1.67 | 0.99 | 4 | 5 | 10 | 5 | 0.80 |
| bitter | 1.67 | 0.75 | 2 | 6 | 14 | 2 | 0.93 |
| bleak | 1.67 | 0.85 | 2 | 8 | 10 | 4 | 0.79 |
| funny | 1.67 | 0.75 | 2 | 6 | 14 | 2 | 0.74 |
| wistful | 1.62 | 0.75 | 1 | 10 | 10 | 3 | 0.83 |
| tender | 1.62 | 0.63 | 0 | 11 | 11 | 2 | 0.82 |
| solemn | 1.42 | 0.70 | 3 | 8 | 13 | 0 | 0.67 |
| lush | 1.42 | 0.57 | 1 | 12 | 11 | 0 | 0.67 |
| eerie | 1.29 | 0.73 | 3 | 12 | 8 | 1 | 0.86 |
| playful | 1.25 | 0.83 | 4 | 12 | 6 | 2 | 0.83 |
| claustrophobic | 1.21 | 0.96 | 6 | 10 | 5 | 3 | 0.74 |
| exhilarating | 1.21 | 0.91 | 6 | 9 | 7 | 2 | 0.74 |
| dreamlike | 1.21 | 0.82 | 5 | 10 | 8 | 1 | 0.91 |
| warm | 1.08 | 0.81 | 5 | 14 | 3 | 2 | 0.68 |
| disorienting | 1.08 | 0.86 | 6 | 12 | 4 | 2 | 0.67 |
| hopeful | 1.04 | 0.79 | 5 | 15 | 2 | 2 | 0.74 |
| serene | 0.58 | 0.49 | 10 | 14 | 0 | 0 | 0.46 |
| cosy | 0.58 | 0.64 | 12 | 10 | 2 | 0 | 0.63 |

#### Two independent readings of one work (and series / same-author pairs)

Pearson z = correlation after each word is z-scored across the 24 books, which takes out the profile all books share. Ranks are among the 23 other books (1 = nearest).

| set | pair | Pearson raw | Spearman raw | Pearson z | mean abs diff | exact agreement | rank of b from a (z) | rank of a from b (z) |
|---|---|---|---|---|---|---|---|---|
| translation_pair | fathers_garnett ~ fathers_hogarth | 0.81 | 0.79 | 0.65 | 0.29 | 0.71 | 3.00 | 3.00 |
| translation_pair | gentlefolk_garnett ~ gentlefolk_ralston | 0.79 | 0.77 | 0.76 | 0.29 | 0.71 | 2.00 | 2.00 |
| translation_pair | journey_1871 ~ journey_malleson | 0.82 | 0.82 | 0.68 | 0.29 | 0.71 | 1.00 | 1.00 |
| edition_pair | frankenstein_1818 ~ frankenstein_1831 | 0.91 | 0.92 | 0.84 | 0.17 | 0.83 | 1.00 | 1.00 |
| retelling | burnett_princess ~ burnett_sara_crewe | 0.76 | 0.73 | 0.84 | 0.25 | 0.75 | 1.00 | 1.00 |
| series | holmes_hound ~ holmes_study | 0.75 | 0.77 | 0.55 | 0.42 | 0.58 | 3.00 | 2.00 |
| series | oz_land ~ oz_wizard | 0.80 | 0.76 | 0.82 | 0.33 | 0.67 | 1.00 | 1.00 |
| series | tarzan_apes ~ tarzan_return | 0.83 | 0.82 | 0.71 | 0.33 | 0.67 | 1.00 | 1.00 |
| same_author_unrelated | fathers_garnett ~ gentlefolk_garnett | 0.79 | 0.79 | 0.72 | 0.33 | 0.67 | 2.00 | 3.00 |
| same_author_unrelated | fathers_garnett ~ gentlefolk_ralston | 0.83 | 0.84 | 0.78 | 0.21 | 0.79 | 1.00 | 1.00 |
| same_author_unrelated | fathers_hogarth ~ gentlefolk_garnett | 0.86 | 0.89 | 0.76 | 0.21 | 0.79 | 1.00 | 1.00 |
| same_author_unrelated | fathers_hogarth ~ gentlefolk_ralston | 0.76 | 0.79 | 0.68 | 0.33 | 0.67 | 2.00 | 3.00 |
| same_author_unrelated | wells_time ~ wells_worlds | 0.72 | 0.71 | 0.35 | 0.46 | 0.54 | 3.00 | 7.00 |
| negatives (median) | 263 pairs | 0.20 |  | -0.07 | 0.88 | 0.33 |  |  |

#### From-text felt against title-only felt

| key | Pearson raw | Pearson z | rank of own title vector (z) | mean abs diff | exact agreement |
|---|---|---|---|---|---|
| wharton_frome | 0.92 | 0.80 | 1.00 | 0.33 | 0.67 |
| journey_1871 | 0.50 | 0.60 | 1.00 | 1.00 | 0.25 |
| oz_land | 0.77 | 0.88 | 1.00 | 0.42 | 0.62 |
| conrad_agent | 0.90 | 0.91 | 1.00 | 0.29 | 0.71 |
| tarzan_return | 0.78 | 0.77 | 2.00 | 0.38 | 0.62 |
| wells_worlds | 0.79 | 0.75 | 1.00 | 0.58 | 0.46 |
| zamyatin_we | 0.81 | 0.78 | 1.00 | 0.50 | 0.50 |
| fathers_garnett | 0.74 | 0.81 | 1.00 | 0.38 | 0.62 |
| christie_styles | 0.65 | 0.73 | 1.00 | 0.71 | 0.29 |
| wells_time | 0.77 | 0.53 | 1.00 | 0.58 | 0.50 |
| gentlefolk_ralston | 0.55 | 0.69 | 4.00 | 0.67 | 0.46 |
| holmes_hound | 0.64 | 0.59 | 4.00 | 0.67 | 0.38 |
| holmes_study | 0.67 | 0.63 | 1.00 | 0.79 | 0.25 |
| oz_wizard | 0.77 | 0.91 | 1.00 | 0.67 | 0.33 |
| hammett_falcon | 0.88 | 0.85 | 1.00 | 0.33 | 0.67 |
| frankenstein_1818 | 0.81 | 0.63 | 2.00 | 0.46 | 0.54 |
| gentlefolk_garnett | 0.67 | 0.80 | 3.00 | 0.58 | 0.54 |
| burnett_princess | 0.76 | 0.85 | 1.00 | 0.62 | 0.42 |
| journey_malleson | 0.68 | 0.79 | 1.00 | 0.71 | 0.33 |
| frankenstein_1831 | 0.86 | 0.65 | 1.00 | 0.38 | 0.62 |
| tarzan_apes | 0.72 | 0.77 | 2.00 | 0.71 | 0.29 |
| fathers_hogarth | 0.66 | 0.76 | 1.00 | 0.58 | 0.46 |
| burnett_sara_crewe | 0.82 | 0.89 | 1.00 | 0.46 | 0.54 |
| MEAN | 0.74 | 0.76 | 1.48 | 0.56 | 0.48 |

Own title-only vector is the nearest of the 23 for 17 of 23 books (same-work partners are among the candidates).


### Felt from passage embeddings, against the reader

| projection | per word: mean Spearman over 24 words | words with Spearman > 0.4 | per book: mean Spearman, raw reader scores | per book: mean Spearman, both z-scored | ... against another book's reader scores | books where own reader vector is the best match |
|---|---|---|---|---|---|---|
| F_proj_plain | 0.46 | 15 | 0.47 | 0.54 | -0.02 | 6 |
| F_proj_plain_n20 | 0.44 | 11 | 0.47 | 0.51 | -0.02 | 6 |
| F_proj_inst | 0.50 | 17 | 0.44 | 0.49 | -0.02 | 5 |
| F_proj_inst_n20 | 0.48 | 16 | 0.43 | 0.47 | -0.02 | 4 |

Spearman per word across the 24 books (reader score against projection).

| word | reader sd | F_proj_plain | F_proj_plain_n20 | F_proj_inst | F_proj_inst_n20 |
|---|---|---|---|---|---|
| tender | 0.63 | 0.80 | 0.77 | 0.72 | 0.73 |
| wistful | 0.75 | 0.76 | 0.74 | 0.73 | 0.72 |
| solemn | 0.70 | 0.72 | 0.73 | 0.69 | 0.67 |
| cosy | 0.64 | 0.72 | 0.68 | 0.68 | 0.64 |
| eerie | 0.73 | 0.69 | 0.66 | 0.81 | 0.77 |
| dreamlike | 0.82 | 0.66 | 0.68 | 0.76 | 0.77 |
| melancholy | 0.70 | 0.64 | 0.70 | 0.78 | 0.77 |
| disorienting | 0.86 | 0.64 | 0.62 | 0.74 | 0.78 |
| desolate | 0.93 | 0.60 | 0.60 | 0.67 | 0.66 |
| warm | 0.81 | 0.53 | 0.54 | 0.42 | 0.41 |
| menacing | 0.87 | 0.52 | 0.50 | 0.69 | 0.61 |
| bleak | 0.85 | 0.45 | 0.40 | 0.58 | 0.54 |
| cold | 0.99 | 0.45 | 0.39 | 0.51 | 0.53 |
| anxious | 0.73 | 0.43 | 0.35 | 0.65 | 0.66 |
| bitter | 0.75 | 0.43 | 0.30 | 0.39 | 0.38 |
| claustrophobic | 0.96 | 0.38 | 0.29 | 0.47 | 0.42 |
| hopeful | 0.79 | 0.37 | 0.39 | 0.43 | 0.35 |
| grotesque | 0.55 | 0.34 | 0.28 | 0.07 | 0.08 |
| tense | 0.61 | 0.30 | 0.23 | 0.21 | 0.15 |
| serene | 0.49 | 0.26 | 0.29 | 0.46 | 0.46 |
| funny | 0.75 | 0.17 | 0.23 | 0.14 | 0.10 |
| exhilarating | 0.91 | 0.10 | 0.09 | 0.08 | 0.15 |
| lush | 0.57 | 0.09 | 0.10 | 0.21 | 0.18 |
| playful | 0.83 | 0.04 | 0.03 | 0.00 | 0.00 |


### Felt projection, 87 books

AUC that a labelled pair is closer than a negative pair (3663 negatives; [95% bootstrap interval over the labelled pairs]). n = labelled pairs.

| block | translation_pair (n=10) | edition_pair (n=1) | same_author_unrelated (n=52) | same_author_orig_en (n=33) | same_author_same_translator (n=5) | same_author_diff_translator (n=14) | series (n=7) | retelling (n=8) | same_translator_diff_author (n=11) | same_genre (n=261) |
|---|---|---|---|---|---|---|---|---|---|---|
| F_proj_plain | 0.90 [0.74, 0.99] | 1.00 | 0.70 [0.64, 0.76] | 0.71 [0.62, 0.79] | 0.69 [0.51, 0.86] | 0.67 [0.59, 0.75] | 0.83 [0.73, 0.92] | 0.91 [0.88, 0.95] | 0.43 [0.31, 0.55] | 0.62 [0.59, 0.65] |
| F_proj_inst | 0.95 [0.87, 1.00] | 1.00 | 0.75 [0.69, 0.81] | 0.78 [0.69, 0.86] | 0.69 [0.39, 0.94] | 0.71 [0.64, 0.78] | 0.96 [0.94, 0.98] | 0.75 [0.63, 0.88] | 0.43 [0.31, 0.56] | 0.65 [0.62, 0.68] |
| F_proj_plain_n20 | 0.89 [0.73, 1.00] | 1.00 | 0.69 [0.63, 0.76] | 0.71 [0.62, 0.80] | 0.64 [0.42, 0.82] | 0.68 [0.59, 0.77] | 0.85 [0.78, 0.92] | 0.86 [0.81, 0.91] | 0.45 [0.32, 0.57] | 0.59 [0.56, 0.62] |
| W1_qwen_maskB_c | 1.00 [1.00, 1.00] | 1.00 | 0.91 [0.88, 0.94] | 0.93 [0.89, 0.96] | 0.93 [0.91, 0.95] | 0.86 [0.80, 0.92] | 0.99 [0.97, 1.00] | 0.98 [0.93, 1.00] | 0.65 [0.57, 0.75] | 0.80 [0.78, 0.82] |
| P4_mfw500_tag3_rhythm | 1.00 [1.00, 1.00] | 1.00 | 0.99 [0.98, 0.99] | 0.99 [0.98, 0.99] | 1.00 [1.00, 1.00] | 0.98 [0.96, 1.00] | 1.00 [0.99, 1.00] | 0.73 [0.44, 0.95] | 0.94 [0.89, 0.98] | 0.61 [0.57, 0.65] |

Mean percentile rank of the partner (0 = nearest book) / recall@1 / recall@5.

| block | translation_pair (n=10) | edition_pair (n=1) | same_author_unrelated (n=52) | same_author_orig_en (n=33) | same_author_same_translator (n=5) | same_author_diff_translator (n=14) | series (n=7) | retelling (n=8) | same_translator_diff_author (n=11) | same_genre (n=261) |
|---|---|---|---|---|---|---|---|---|---|---|
| F_proj_plain | 0.09 / 0.65 / 0.82 | 0.00 / 1.00 / 1.00 | 0.29 / 0.15 / 0.35 | 0.30 / 0.19 / 0.44 | 0.26 / 0.14 / 0.14 | 0.29 / 0.00 / 0.19 | 0.13 / 0.29 / 0.50 | 0.11 / 0.10 / 0.70 | 0.61 / 0.00 / 0.00 | 0.36 / 0.32 / 0.75 |
| F_proj_inst | 0.05 / 0.76 / 0.82 | 0.00 / 1.00 / 1.00 | 0.24 / 0.17 / 0.44 | 0.21 / 0.25 / 0.53 | 0.30 / 0.00 / 0.43 | 0.30 / 0.00 / 0.12 | 0.01 / 0.71 / 1.00 | 0.24 / 0.20 / 0.50 | 0.60 / 0.00 / 0.00 | 0.34 / 0.25 / 0.74 |
| F_proj_plain_n20 | 0.11 / 0.59 / 0.76 | 0.00 / 1.00 / 1.00 | 0.29 / 0.31 / 0.44 | 0.29 / 0.41 / 0.50 | 0.33 / 0.00 / 0.14 | 0.28 / 0.12 / 0.31 | 0.08 / 0.21 / 0.57 | 0.14 / 0.20 / 0.60 | 0.57 / 0.00 / 0.00 | 0.39 / 0.11 / 0.60 |
| W1_qwen_maskB_c | 0.00 / 1.00 / 1.00 | 0.00 / 1.00 / 1.00 | 0.09 / 0.23 / 0.81 | 0.08 / 0.28 / 0.88 | 0.03 / 0.29 / 0.86 | 0.13 / 0.00 / 0.38 | 0.01 / 0.86 / 0.93 | 0.03 / 0.40 / 0.80 | 0.38 / 0.00 / 0.33 | 0.22 / 0.40 / 0.85 |
| P4_mfw500_tag3_rhythm | 0.00 / 0.94 / 1.00 | 0.00 / 1.00 / 1.00 | 0.02 / 0.69 / 0.98 | 0.02 / 0.81 / 0.97 | 0.01 / 0.71 / 1.00 | 0.03 / 0.12 / 0.94 | 0.00 / 0.86 / 1.00 | 0.24 / 0.30 / 0.50 | 0.09 / 0.00 / 0.83 | 0.38 / 0.09 / 0.72 |

Split-half self-retrieval (accuracy; chance is 1/n), and Spearman of distance with |year difference| and |log word-count difference| (Mantel p in brackets; en = both books written in English; diff = different authors only).

| block | n | input | split a/b | split h1/h2 | rho year | rho year en | rho year en diff | rho logwords | rho logwords diff |
|---|---|---|---|---|---|---|---|---|---|
| F_proj_plain | 87 | ordered text | 0.48 | 0.27 | 0.01 (0.320) | -0.01 (0.550) | -0.04 | 0.06 (0.015) | 0.06 |
| F_proj_inst | 87 | ordered text | 0.51 | 0.39 | 0.00 (0.780) | -0.01 (0.495) | -0.05 | 0.07 (0.005) | 0.06 |
| F_proj_plain_n20 | 87 | ordered text | 0.27 | 0.24 | 0.02 (0.090) | -0.01 (0.705) | -0.03 | 0.07 (0.005) | 0.06 |
| W1_qwen_maskB_c | 87 | ordered text | 0.96 | 0.91 | 0.08 (0.005) | 0.07 (0.020) | 0.03 | 0.05 (0.015) | 0.03 |
| P4_mfw500_tag3_rhythm | 87 | ordered text | 0.97 | 0.91 | 0.36 (0.005) | 0.34 (0.005) | 0.31 | 0.05 (0.130) | 0.03 |

Top-5 neighbour make-up (observed / chance) and hubness (skew of the 5-nearest in-degree; share of books in nobody's top 5; largest in-degree and the book).

| block | same author | same genre | mean abs year diff | mean abs log-words diff | hub skew | in no top 5 | max in-degree |
|---|---|---|---|---|---|---|---|
| F_proj_plain | 0.14 / 0.02 | 0.31 / 0.12 | 58 / 56 | 0.71 / 0.78 | 1.07 | 0.05 | 18 (dq_motteux) |
| F_proj_inst | 0.19 / 0.02 | 0.37 / 0.12 | 48 / 56 | 0.67 / 0.78 | 0.79 | 0.05 | 15 (tolstoy_res_maude) |
| F_proj_plain_n20 | 0.15 / 0.02 | 0.26 / 0.12 | 56 / 56 | 0.69 / 0.78 | 1.01 | 0.07 | 17 (dq_motteux) |
| W1_qwen_maskB_c | 0.30 / 0.02 | 0.51 / 0.12 | 41 / 56 | 0.62 / 0.78 | 1.13 | 0.00 | 16 (austen_emma) |
| P4_mfw500_tag3_rhythm | 0.40 / 0.02 | 0.38 / 0.12 | 27 / 56 | 0.64 / 0.78 | 1.00 | 0.02 | 17 (wells_worlds) |

Spearman between the pair distances of two blocks, all pairs.

| block | F_proj_plain | F_proj_inst | F_proj_plain_n20 | W1_qwen_maskB_c | P4_mfw500_tag3_rhythm |
|---|---|---|---|---|---|
| F_proj_plain | 1.00 | 0.70 | 0.90 | 0.40 | 0.18 |
| F_proj_inst | 0.70 | 1.00 | 0.65 | 0.48 | 0.24 |
| F_proj_plain_n20 | 0.90 | 0.65 | 1.00 | 0.36 | 0.17 |
| W1_qwen_maskB_c | 0.40 | 0.48 | 0.36 | 1.00 | 0.40 |
| P4_mfw500_tag3_rhythm | 0.18 | 0.24 | 0.17 | 0.40 | 1.00 |

Spearman between the pair distances of two blocks, different-author pairs only.

| block | F_proj_plain | F_proj_inst | F_proj_plain_n20 | W1_qwen_maskB_c | P4_mfw500_tag3_rhythm |
|---|---|---|---|---|---|
| F_proj_plain | 1.00 | 0.70 | 0.90 | 0.38 | 0.16 |
| F_proj_inst | 0.70 | 1.00 | 0.64 | 0.47 | 0.21 |
| F_proj_plain_n20 | 0.90 | 0.64 | 1.00 | 0.35 | 0.15 |
| W1_qwen_maskB_c | 0.38 | 0.47 | 0.35 | 1.00 | 0.37 |
| P4_mfw500_tag3_rhythm | 0.16 | 0.21 | 0.15 | 0.37 | 1.00 |


### P5 StyleDistance and P6 closed-class against P4

AUC that a labelled pair is closer than a negative pair (3663 negatives; [95% bootstrap interval over the labelled pairs]). n = labelled pairs.

| block | translation_pair (n=10) | edition_pair (n=1) | same_author_unrelated (n=52) | same_author_orig_en (n=33) | same_author_same_translator (n=5) | same_author_diff_translator (n=14) | series (n=7) | retelling (n=8) | same_translator_diff_author (n=11) | same_genre (n=261) |
|---|---|---|---|---|---|---|---|---|---|---|
| P4_mfw500_tag3_rhythm | 1.00 [1.00, 1.00] | 1.00 | 0.99 [0.98, 0.99] | 0.99 [0.98, 0.99] | 1.00 [1.00, 1.00] | 0.98 [0.96, 1.00] | 1.00 [0.99, 1.00] | 0.73 [0.44, 0.95] | 0.94 [0.89, 0.98] | 0.61 [0.57, 0.65] |
| P5_style_clean_raw | 0.41 [0.25, 0.59] | 0.84 | 0.76 [0.69, 0.83] | 0.81 [0.74, 0.88] | 0.83 [0.76, 0.91] | 0.62 [0.44, 0.79] | 0.87 [0.69, 0.97] | 0.43 [0.29, 0.60] | 0.87 [0.81, 0.93] | 0.55 [0.51, 0.58] |
| P5_style_clean_c | 0.68 [0.48, 0.85] | 1.00 | 0.77 [0.69, 0.84] | 0.81 [0.73, 0.88] | 0.81 [0.70, 0.91] | 0.65 [0.47, 0.82] | 0.94 [0.88, 0.98] | 0.71 [0.53, 0.87] | 0.80 [0.69, 0.89] | 0.57 [0.53, 0.60] |
| P5_style_clean_pc1 | 0.78 [0.61, 0.92] | 0.87 | 0.78 [0.71, 0.84] | 0.81 [0.73, 0.88] | 0.80 [0.70, 0.88] | 0.70 [0.54, 0.84] | 0.91 [0.86, 0.97] | 0.47 [0.20, 0.74] | 0.75 [0.64, 0.84] | 0.56 [0.53, 0.60] |
| P5_style_maskA_c | 0.68 [0.47, 0.85] | 1.00 | 0.77 [0.69, 0.83] | 0.82 [0.75, 0.88] | 0.79 [0.66, 0.91] | 0.64 [0.46, 0.82] | 0.94 [0.89, 0.98] | 0.70 [0.52, 0.86] | 0.79 [0.68, 0.89] | 0.56 [0.53, 0.60] |
| P5_style_maskA_pc1 | 0.80 [0.67, 0.93] | 0.91 | 0.79 [0.72, 0.85] | 0.81 [0.73, 0.88] | 0.82 [0.74, 0.89] | 0.72 [0.57, 0.86] | 0.91 [0.85, 0.96] | 0.47 [0.21, 0.74] | 0.72 [0.62, 0.81] | 0.56 [0.53, 0.60] |
| P6_closed_nopron | 0.99 [0.97, 1.00] | 1.00 | 0.97 [0.95, 0.99] | 0.98 [0.98, 0.99] | 1.00 [1.00, 1.00] | 0.93 [0.87, 0.98] | 1.00 [1.00, 1.00] | 0.90 [0.83, 0.96] | 0.99 [0.98, 1.00] | 0.63 [0.59, 0.66] |
| P6_closed_pron | 1.00 [0.99, 1.00] | 1.00 | 0.98 [0.97, 0.99] | 0.99 [0.98, 0.99] | 1.00 [1.00, 1.00] | 0.95 [0.92, 0.98] | 1.00 [1.00, 1.00] | 0.92 [0.86, 0.97] | 0.98 [0.96, 1.00] | 0.65 [0.61, 0.69] |
| P6_pron_only | 1.00 [1.00, 1.00] | 1.00 | 0.87 [0.82, 0.91] | 0.85 [0.79, 0.91] | 0.90 [0.81, 0.99] | 0.88 [0.83, 0.93] | 0.92 [0.84, 0.98] | 0.84 [0.75, 0.92] | 0.75 [0.56, 0.90] | 0.65 [0.61, 0.68] |
| P3_rhythm | 0.87 [0.72, 0.99] | 1.00 | 0.90 [0.85, 0.93] | 0.87 [0.81, 0.93] | 0.98 [0.97, 0.99] | 0.93 [0.90, 0.96] | 0.85 [0.64, 0.99] | 0.50 [0.25, 0.77] | 0.85 [0.79, 0.90] | 0.51 [0.47, 0.55] |

AUC difference from `P4_mfw500_tag3_rhythm` on the same pairs [paired bootstrap 95%].

| block | translation_pair (n=10) | edition_pair (n=1) | same_author_unrelated (n=52) | same_author_orig_en (n=33) | same_author_same_translator (n=5) | same_author_diff_translator (n=14) | series (n=7) | retelling (n=8) | same_translator_diff_author (n=11) | same_genre (n=261) |
|---|---|---|---|---|---|---|---|---|---|---|
| P5_style_clean_raw | -0.59 [-0.76, -0.40] |  | -0.23 [-0.29, -0.16] | -0.18 [-0.25, -0.12] | -0.17 [-0.24, -0.09] | -0.36 [-0.54, -0.19] | -0.13 [-0.31, -0.03] | -0.30 [-0.47, -0.10] | -0.07 [-0.14, -0.01] | -0.06 [-0.10, -0.03] |
| P5_style_clean_c | -0.32 [-0.52, -0.14] |  | -0.22 [-0.29, -0.15] | -0.18 [-0.25, -0.11] | -0.19 [-0.30, -0.10] | -0.33 [-0.51, -0.17] | -0.06 [-0.12, -0.02] | -0.02 [-0.17, +0.14] | -0.14 [-0.24, -0.07] | -0.04 [-0.08, -0.01] |
| P5_style_clean_pc1 | -0.22 [-0.38, -0.08] |  | -0.21 [-0.28, -0.15] | -0.18 [-0.26, -0.11] | -0.20 [-0.30, -0.12] | -0.28 [-0.44, -0.14] | -0.08 [-0.14, -0.03] | -0.27 [-0.49, -0.07] | -0.20 [-0.29, -0.12] | -0.05 [-0.08, -0.01] |
| P5_style_maskA_c | -0.32 [-0.52, -0.15] |  | -0.22 [-0.29, -0.15] | -0.17 [-0.24, -0.11] | -0.21 [-0.32, -0.09] | -0.34 [-0.52, -0.17] | -0.06 [-0.11, -0.02] | -0.03 [-0.20, +0.15] | -0.15 [-0.25, -0.08] | -0.04 [-0.08, -0.01] |
| P5_style_maskA_pc1 | -0.20 [-0.33, -0.08] |  | -0.20 [-0.26, -0.15] | -0.18 [-0.25, -0.11] | -0.18 [-0.26, -0.11] | -0.26 [-0.40, -0.12] | -0.08 [-0.15, -0.03] | -0.26 [-0.49, -0.06] | -0.23 [-0.32, -0.14] | -0.05 [-0.09, -0.01] |
| P6_closed_nopron | -0.01 [-0.03, -0.00] |  | -0.02 [-0.03, -0.00] | -0.00 [-0.01, +0.00] | -0.00 [-0.00, +0.00] | -0.05 [-0.10, -0.01] | +0.00 [-0.00, +0.01] | +0.17 [-0.02, +0.39] | +0.05 [+0.01, +0.09] | +0.02 [-0.01, +0.05] |
| P6_closed_pron | -0.00 [-0.01, +0.00] |  | -0.01 [-0.02, -0.00] | -0.00 [-0.01, +0.01] | -0.00 [-0.00, +0.00] | -0.03 [-0.05, -0.01] | +0.00 [-0.00, +0.01] | +0.19 [+0.01, +0.41] | +0.04 [+0.01, +0.07] | +0.04 [+0.01, +0.07] |
| P6_pron_only | +0.00 [+0.00, +0.00] |  | -0.12 [-0.17, -0.08] | -0.13 [-0.20, -0.08] | -0.10 [-0.19, -0.01] | -0.10 [-0.16, -0.05] | -0.08 [-0.16, -0.02] | +0.11 [-0.05, +0.30] | -0.20 [-0.36, -0.07] | +0.04 [-0.00, +0.08] |
| P3_rhythm | -0.13 [-0.27, -0.01] |  | -0.09 [-0.13, -0.05] | -0.12 [-0.18, -0.07] | -0.02 [-0.03, -0.01] | -0.05 [-0.08, -0.03] | -0.15 [-0.29, -0.01] | -0.23 [-0.40, -0.08] | -0.10 [-0.14, -0.06] | -0.10 [-0.12, -0.08] |

Mean percentile rank of the partner (0 = nearest book) / recall@1 / recall@5.

| block | translation_pair (n=10) | edition_pair (n=1) | same_author_unrelated (n=52) | same_author_orig_en (n=33) | same_author_same_translator (n=5) | same_author_diff_translator (n=14) | series (n=7) | retelling (n=8) | same_translator_diff_author (n=11) | same_genre (n=261) |
|---|---|---|---|---|---|---|---|---|---|---|
| P4_mfw500_tag3_rhythm | 0.00 / 0.94 / 1.00 | 0.00 / 1.00 / 1.00 | 0.02 / 0.69 / 0.98 | 0.02 / 0.81 / 0.97 | 0.01 / 0.71 / 1.00 | 0.03 / 0.12 / 0.94 | 0.00 / 0.86 / 1.00 | 0.24 / 0.30 / 0.50 | 0.09 / 0.00 / 0.83 | 0.38 / 0.09 / 0.72 |
| P5_style_clean_raw | 0.43 / 0.00 / 0.18 | 0.03 / 0.00 / 1.00 | 0.23 / 0.31 / 0.67 | 0.19 / 0.38 / 0.72 | 0.19 / 0.00 / 0.14 | 0.36 / 0.19 / 0.50 | 0.09 / 0.36 / 0.64 | 0.42 / 0.00 / 0.10 | 0.18 / 0.33 / 0.83 | 0.46 / 0.15 / 0.49 |
| P5_style_clean_c | 0.30 / 0.12 / 0.29 | 0.01 / 0.50 / 1.00 | 0.23 / 0.29 / 0.62 | 0.18 / 0.34 / 0.69 | 0.16 / 0.00 / 0.43 | 0.36 / 0.19 / 0.38 | 0.05 / 0.43 / 0.57 | 0.29 / 0.00 / 0.30 | 0.19 / 0.17 / 0.67 | 0.44 / 0.11 / 0.55 |
| P5_style_clean_pc1 | 0.24 / 0.12 / 0.35 | 0.09 / 0.00 / 0.50 | 0.22 / 0.33 / 0.60 | 0.18 / 0.44 / 0.69 | 0.14 / 0.00 / 0.29 | 0.32 / 0.12 / 0.38 | 0.10 / 0.36 / 0.36 | 0.51 / 0.00 / 0.40 | 0.24 / 0.33 / 0.83 | 0.44 / 0.21 / 0.57 |
| P5_style_maskA_c | 0.30 / 0.12 / 0.12 | 0.01 / 0.50 / 1.00 | 0.23 / 0.31 / 0.60 | 0.17 / 0.38 / 0.62 | 0.18 / 0.00 / 0.43 | 0.37 / 0.19 / 0.44 | 0.05 / 0.50 / 0.64 | 0.29 / 0.00 / 0.30 | 0.21 / 0.17 / 0.67 | 0.44 / 0.13 / 0.55 |
| P5_style_maskA_pc1 | 0.21 / 0.12 / 0.35 | 0.08 / 0.00 / 0.50 | 0.21 / 0.31 / 0.60 | 0.18 / 0.41 / 0.69 | 0.11 / 0.00 / 0.43 | 0.31 / 0.12 / 0.38 | 0.10 / 0.36 / 0.36 | 0.51 / 0.00 / 0.40 | 0.26 / 0.33 / 0.67 | 0.44 / 0.21 / 0.64 |
| P6_closed_nopron | 0.01 / 0.82 / 0.94 | 0.00 / 1.00 / 1.00 | 0.03 / 0.69 / 0.94 | 0.02 / 0.81 / 0.94 | 0.01 / 0.71 / 1.00 | 0.07 / 0.12 / 0.81 | 0.00 / 0.86 / 1.00 | 0.13 / 0.20 / 0.50 | 0.04 / 0.17 / 1.00 | 0.38 / 0.08 / 0.62 |
| P6_closed_pron | 0.01 / 0.88 / 0.94 | 0.00 / 1.00 / 1.00 | 0.03 / 0.67 / 0.94 | 0.02 / 0.78 / 0.91 | 0.01 / 0.86 / 1.00 | 0.06 / 0.06 / 0.88 | 0.00 / 1.00 / 1.00 | 0.09 / 0.20 / 0.70 | 0.05 / 0.17 / 1.00 | 0.36 / 0.11 / 0.68 |
| P6_pron_only | 0.00 / 1.00 / 1.00 | 0.00 / 1.00 / 1.00 | 0.13 / 0.48 / 0.62 | 0.14 / 0.56 / 0.66 | 0.10 / 0.29 / 0.71 | 0.11 / 0.19 / 0.50 | 0.07 / 0.43 / 0.50 | 0.13 / 0.10 / 0.50 | 0.26 / 0.00 / 0.83 | 0.36 / 0.19 / 0.72 |
| P3_rhythm | 0.02 / 0.59 / 1.00 | 0.00 / 1.00 / 1.00 | 0.12 / 0.48 / 0.73 | 0.14 / 0.56 / 0.75 | 0.03 / 0.57 / 0.57 | 0.10 / 0.06 / 0.62 | 0.10 / 0.50 / 0.71 | 0.43 / 0.20 / 0.60 | 0.20 / 0.17 / 0.67 | 0.49 / 0.09 / 0.43 |

Split-half self-retrieval (accuracy; chance is 1/n), and Spearman of distance with |year difference| and |log word-count difference| (Mantel p in brackets; en = both books written in English; diff = different authors only).

| block | n | input | split a/b | split h1/h2 | rho year | rho year en | rho year en diff | rho logwords | rho logwords diff |
|---|---|---|---|---|---|---|---|---|---|
| P4_mfw500_tag3_rhythm | 87 | ordered text | 0.97 | 0.91 | 0.36 (0.005) | 0.34 (0.005) | 0.31 | 0.05 (0.180) | 0.03 |
| P5_style_clean_raw | 87 | ordered text | 0.74 | 0.62 | 0.29 (0.005) | 0.22 (0.005) | 0.20 | -0.01 (0.850) | -0.02 |
| P5_style_clean_c | 87 | ordered text | 0.70 | 0.63 | 0.18 (0.005) | 0.24 (0.005) | 0.21 | 0.02 (0.375) | 0.01 |
| P5_style_clean_pc1 | 87 | ordered text | 0.75 | 0.66 | 0.13 (0.005) | 0.12 (0.010) | 0.10 | 0.04 (0.085) | 0.03 |
| P5_style_maskA_c | 87 | ordered text | 0.71 | 0.61 | 0.18 (0.005) | 0.24 (0.005) | 0.22 | 0.02 (0.335) | 0.01 |
| P5_style_maskA_pc1 | 87 | ordered text | 0.75 | 0.68 | 0.13 (0.005) | 0.12 (0.005) | 0.10 | 0.04 (0.065) | 0.03 |
| P6_closed_nopron | 87 | book bag | 0.93 | 0.88 | 0.17 (0.005) | 0.23 (0.005) | 0.20 | 0.06 (0.005) | 0.05 |
| P6_closed_pron | 87 | book bag | 0.95 | 0.89 | 0.18 (0.005) | 0.22 (0.005) | 0.19 | 0.05 (0.010) | 0.04 |
| P6_pron_only | 87 | book bag | 0.68 | 0.52 | 0.11 (0.005) | 0.06 (0.050) | 0.03 | 0.02 (0.115) | 0.01 |
| P3_rhythm | 87 | ordered text | 0.97 | 0.85 | 0.39 (0.005) | 0.27 (0.005) | 0.24 | 0.01 (0.845) | 0.00 |

Top-5 neighbour make-up (observed / chance) and hubness (skew of the 5-nearest in-degree; share of books in nobody's top 5; largest in-degree and the book).

| block | same author | same genre | mean abs year diff | mean abs log-words diff | hub skew | in no top 5 | max in-degree |
|---|---|---|---|---|---|---|---|
| P4_mfw500_tag3_rhythm | 0.40 / 0.02 | 0.38 / 0.12 | 27 / 56 | 0.64 / 0.78 | 1.00 | 0.02 | 17 (wells_worlds) |
| P5_style_clean_raw | 0.17 / 0.02 | 0.20 / 0.12 | 35 / 56 | 0.68 / 0.78 | 0.93 | 0.05 | 16 (eliot_middlemarch) |
| P5_style_clean_c | 0.16 / 0.02 | 0.22 / 0.12 | 39 / 56 | 0.67 / 0.78 | 0.37 | 0.05 | 12 (anne_gables) |
| P5_style_clean_pc1 | 0.16 / 0.02 | 0.22 / 0.12 | 44 / 56 | 0.68 / 0.78 | 0.62 | 0.06 | 13 (oz_land) |
| P5_style_maskA_c | 0.15 / 0.02 | 0.22 / 0.12 | 41 / 56 | 0.68 / 0.78 | 0.37 | 0.05 | 13 (anne_gables) |
| P5_style_maskA_pc1 | 0.17 / 0.02 | 0.22 / 0.12 | 43 / 56 | 0.71 / 0.78 | 0.51 | 0.06 | 13 (mystisland_white) |
| P6_closed_nopron | 0.38 / 0.02 | 0.36 / 0.12 | 33 / 56 | 0.66 / 0.78 | 0.20 | 0.06 | 12 (sinclair_olivier) |
| P6_closed_pron | 0.38 / 0.02 | 0.39 / 0.12 | 33 / 56 | 0.68 / 0.78 | 0.13 | 0.06 | 13 (sinclair_olivier) |
| P6_pron_only | 0.24 / 0.02 | 0.27 / 0.12 | 37 / 56 | 0.73 / 0.78 | 0.41 | 0.00 | 11 (gentlefolk_garnett) |
| P3_rhythm | 0.27 / 0.02 | 0.20 / 0.12 | 29 / 56 | 0.67 / 0.78 | 1.23 | 0.09 | 21 (woolf_voyage) |

Spearman between the pair distances of two blocks, all pairs.

| block | P4_mfw500_tag3_rhythm | P5_style_clean_raw | P5_style_clean_c | P5_style_clean_pc1 | P5_style_maskA_c | P5_style_maskA_pc1 | P6_closed_nopron | P6_closed_pron | P6_pron_only | P3_rhythm |
|---|---|---|---|---|---|---|---|---|---|---|
| P4_mfw500_tag3_rhythm | 1.00 | 0.49 | 0.43 | 0.30 | 0.42 | 0.29 | 0.67 | 0.69 | 0.39 | 0.79 |
| P5_style_clean_raw | 0.49 | 1.00 | 0.62 | 0.47 | 0.61 | 0.45 | 0.22 | 0.22 | 0.13 | 0.59 |
| P5_style_clean_c | 0.43 | 0.62 | 1.00 | 0.55 | 0.99 | 0.54 | 0.41 | 0.40 | 0.14 | 0.28 |
| P5_style_clean_pc1 | 0.30 | 0.47 | 0.55 | 1.00 | 0.55 | 0.99 | 0.19 | 0.18 | 0.09 | 0.26 |
| P5_style_maskA_c | 0.42 | 0.61 | 0.99 | 0.55 | 1.00 | 0.54 | 0.41 | 0.40 | 0.15 | 0.28 |
| P5_style_maskA_pc1 | 0.29 | 0.45 | 0.54 | 0.99 | 0.54 | 1.00 | 0.19 | 0.18 | 0.08 | 0.26 |
| P6_closed_nopron | 0.67 | 0.22 | 0.41 | 0.19 | 0.41 | 0.19 | 1.00 | 0.95 | 0.32 | 0.26 |
| P6_closed_pron | 0.69 | 0.22 | 0.40 | 0.18 | 0.40 | 0.18 | 0.95 | 1.00 | 0.57 | 0.27 |
| P6_pron_only | 0.39 | 0.13 | 0.14 | 0.09 | 0.15 | 0.08 | 0.32 | 0.57 | 1.00 | 0.18 |
| P3_rhythm | 0.79 | 0.59 | 0.28 | 0.26 | 0.28 | 0.26 | 0.26 | 0.27 | 0.18 | 1.00 |

Spearman between the pair distances of two blocks, different-author pairs only.

| block | P4_mfw500_tag3_rhythm | P5_style_clean_raw | P5_style_clean_c | P5_style_clean_pc1 | P5_style_maskA_c | P5_style_maskA_pc1 | P6_closed_nopron | P6_closed_pron | P6_pron_only | P3_rhythm |
|---|---|---|---|---|---|---|---|---|---|---|
| P4_mfw500_tag3_rhythm | 1.00 | 0.49 | 0.42 | 0.27 | 0.41 | 0.27 | 0.66 | 0.67 | 0.36 | 0.78 |
| P5_style_clean_raw | 0.49 | 1.00 | 0.61 | 0.46 | 0.61 | 0.44 | 0.20 | 0.20 | 0.11 | 0.59 |
| P5_style_clean_c | 0.42 | 0.61 | 1.00 | 0.54 | 0.99 | 0.53 | 0.40 | 0.38 | 0.13 | 0.27 |
| P5_style_clean_pc1 | 0.27 | 0.46 | 0.54 | 1.00 | 0.53 | 0.99 | 0.16 | 0.16 | 0.06 | 0.24 |
| P5_style_maskA_c | 0.41 | 0.61 | 0.99 | 0.53 | 1.00 | 0.53 | 0.40 | 0.38 | 0.13 | 0.26 |
| P5_style_maskA_pc1 | 0.27 | 0.44 | 0.53 | 0.99 | 0.53 | 1.00 | 0.16 | 0.16 | 0.06 | 0.24 |
| P6_closed_nopron | 0.66 | 0.20 | 0.40 | 0.16 | 0.40 | 0.16 | 1.00 | 0.95 | 0.30 | 0.23 |
| P6_closed_pron | 0.67 | 0.20 | 0.38 | 0.16 | 0.38 | 0.16 | 0.95 | 1.00 | 0.55 | 0.23 |
| P6_pron_only | 0.36 | 0.11 | 0.13 | 0.06 | 0.13 | 0.06 | 0.30 | 0.55 | 1.00 | 0.15 |
| P3_rhythm | 0.78 | 0.59 | 0.27 | 0.24 | 0.26 | 0.24 | 0.23 | 0.23 | 0.15 | 1.00 |


### Author or translator (6 Garnett books)

| block | nearest: author+translator | author only | translator only | neither | AUC author beats translator (14 vs 11) | AUC translation pair closer than same-author pair (10 vs 52) | ... than orig-English same-author pair (10 vs 33) | median d translation pair / median d same-author |
|---|---|---|---|---|---|---|---|---|
| P4_mfw500_tag3_rhythm | 5 | 1 | 0 | 0 | 0.75 | 0.76 | 0.72 | 0.70 |
| P1_mfw500_all_noprop_nocull | 5 | 1 | 0 | 0 | 0.75 | 0.85 | 0.83 | 0.48 |
| P3_rhythm | 4 | 0 | 1 | 1 | 0.75 | 0.58 | 0.55 | 0.80 |
| P5_style_clean_c | 0 | 0 | 1 | 5 | 0.42 | 0.40 | 0.36 | 1.25 |
| P5_style_clean_pc1 | 0 | 0 | 2 | 4 | 0.51 | 0.54 | 0.50 | 0.96 |
| P5_style_maskA_c | 0 | 0 | 1 | 5 | 0.44 | 0.39 | 0.35 | 1.21 |
| P6_closed_nopron | 5 | 0 | 1 | 0 | 0.34 | 0.63 | 0.58 | 0.68 |
| P6_closed_pron | 5 | 0 | 1 | 0 | 0.35 | 0.75 | 0.72 | 0.62 |
| P6_pron_only | 1 | 2 | 1 | 2 | 0.66 | 0.97 | 0.97 | 0.15 |

Nearest book that is not the same work, per Garnett book (ranks count from 1).

| block | anchor | nearest_not_same_work | shares | rank_nearest_same_author_other_translator | rank_nearest_garnett_other_author |
|---|---|---|---|---|---|
| P4_mfw500_tag3_rhythm | dost_cp_garnett | dost_bk_garnett | author+translator | 2 | 4 |
| P4_mfw500_tag3_rhythm | dost_bk_garnett | dost_cp_garnett | author+translator | 2 | 4 |
| P4_mfw500_tag3_rhythm | dost_notes_garnett | dost_bk_garnett | author+translator | 3 | 6 |
| P4_mfw500_tag3_rhythm | tolstoy_ak_garnett | tolstoy_wp_maude | author only | 1 | 3 |
| P4_mfw500_tag3_rhythm | fathers_garnett | gentlefolk_garnett | author+translator | 3 | 2 |
| P4_mfw500_tag3_rhythm | gentlefolk_garnett | fathers_garnett | author+translator | 15 | 2 |
| P1_mfw500_all_noprop_nocull | dost_cp_garnett | dost_bk_garnett | author+translator | 2 | 3 |
| P1_mfw500_all_noprop_nocull | dost_bk_garnett | dost_cp_garnett | author+translator | 2 | 4 |
| P1_mfw500_all_noprop_nocull | dost_notes_garnett | dost_bk_garnett | author+translator | 3 | 4 |
| P1_mfw500_all_noprop_nocull | tolstoy_ak_garnett | tolstoy_wp_maude | author only | 1 | 2 |
| P1_mfw500_all_noprop_nocull | fathers_garnett | gentlefolk_garnett | author+translator | 4 | 2 |
| P1_mfw500_all_noprop_nocull | gentlefolk_garnett | fathers_garnett | author+translator | 11 | 2 |
| P3_rhythm | dost_cp_garnett | dost_bk_garnett | author+translator | 2 | 4 |
| P3_rhythm | dost_bk_garnett | dost_cp_garnett | author+translator | 2 | 4 |
| P3_rhythm | dost_notes_garnett | dost_bk_garnett | author+translator | 6 | 8 |
| P3_rhythm | tolstoy_ak_garnett | dost_bk_garnett | translator only | 2 | 1 |
| P3_rhythm | fathers_garnett | gentlefolk_garnett | author+translator | 4 | 3 |
| P3_rhythm | gentlefolk_garnett | tolstoy_res_maude | neither | 28 | 16 |
| P5_style_clean_c | dost_cp_garnett | richardson_pointed | neither | 29 | 2 |
| P5_style_clean_c | dost_bk_garnett | anne_avonlea | neither | 25 | 6 |
| P5_style_clean_c | dost_notes_garnett | zamyatin_we | neither | 61 | 13 |
| P5_style_clean_c | tolstoy_ak_garnett | woolf_voyage | neither | 6 | 3 |
| P5_style_clean_c | fathers_garnett | dost_cp_garnett | translator only | 82 | 1 |
| P5_style_clean_c | gentlefolk_garnett | charterhouse_moncrieff | neither | 85 | 3 |
| P5_style_clean_pc1 | dost_cp_garnett | zamyatin_we | neither | 15 | 3 |
| P5_style_clean_pc1 | dost_bk_garnett | tolstoy_ak_garnett | translator only | 2 | 1 |
| P5_style_clean_pc1 | dost_notes_garnett | zamyatin_we | neither | 56 | 20 |
| P5_style_clean_pc1 | tolstoy_ak_garnett | dost_idiot_martin | neither | 14 | 2 |
| P5_style_clean_pc1 | fathers_garnett | dost_cp_garnett | translator only | 72 | 1 |
| P5_style_clean_pc1 | gentlefolk_garnett | charterhouse_moncrieff | neither | 83 | 3 |
| P5_style_maskA_c | dost_cp_garnett | richardson_pointed | neither | 31 | 2 |
| P5_style_maskA_c | dost_bk_garnett | anne_avonlea | neither | 26 | 4 |
| P5_style_maskA_c | dost_notes_garnett | zamyatin_we | neither | 58 | 16 |
| P5_style_maskA_c | tolstoy_ak_garnett | hammett_falcon | neither | 5 | 2 |
| P5_style_maskA_c | fathers_garnett | dost_cp_garnett | translator only | 84 | 1 |
| P5_style_maskA_c | gentlefolk_garnett | tolstoy_wp_maude | neither | 83 | 8 |
| P6_closed_nopron | dost_cp_garnett | dost_bk_garnett | author+translator | 2 | 4 |
| P6_closed_nopron | dost_bk_garnett | dost_cp_garnett | author+translator | 2 | 4 |
| P6_closed_nopron | dost_notes_garnett | dost_cp_garnett | author+translator | 3 | 5 |
| P6_closed_nopron | tolstoy_ak_garnett | fathers_garnett | translator only | 5 | 1 |
| P6_closed_nopron | fathers_garnett | gentlefolk_garnett | author+translator | 6 | 2 |
| P6_closed_nopron | gentlefolk_garnett | fathers_garnett | author+translator | 32 | 2 |
| P6_closed_pron | dost_cp_garnett | dost_bk_garnett | author+translator | 2 | 3 |
| P6_closed_pron | dost_bk_garnett | dost_cp_garnett | author+translator | 2 | 4 |
| P6_closed_pron | dost_notes_garnett | dost_cp_garnett | author+translator | 3 | 4 |
| P6_closed_pron | tolstoy_ak_garnett | gentlefolk_garnett | translator only | 4 | 1 |
| P6_closed_pron | fathers_garnett | gentlefolk_garnett | author+translator | 6 | 2 |
| P6_closed_pron | gentlefolk_garnett | fathers_garnett | author+translator | 24 | 2 |
| P6_pron_only | dost_cp_garnett | dost_idiot_martin | author only | 1 | 3 |
| P6_pron_only | dost_bk_garnett | dost_cp_garnett | author+translator | 2 | 3 |
| P6_pron_only | dost_notes_garnett | frankenstein_1831 | neither | 18 | 12 |
| P6_pron_only | tolstoy_ak_garnett | tolstoy_res_smith | author only | 1 | 3 |
| P6_pron_only | fathers_garnett | dost_cp_garnett | translator only | 9 | 1 |
| P6_pron_only | gentlefolk_garnett | charterhouse_moncrieff | neither | 17 | 3 |

### P6 closed-class control

AUC that a labelled pair is closer than a negative pair (3663 negatives; [95% bootstrap interval over the labelled pairs]). n = labelled pairs.

| block | translation_pair (n=10) | edition_pair (n=1) | same_author_unrelated (n=52) | same_author_orig_en (n=33) | same_author_same_translator (n=5) | same_author_diff_translator (n=14) | series (n=7) | retelling (n=8) | same_translator_diff_author (n=11) | same_genre (n=261) |
|---|---|---|---|---|---|---|---|---|---|---|
| P4_mfw500_tag3_rhythm | 1.00 [1.00, 1.00] | 1.00 | 0.99 [0.98, 0.99] | 0.99 [0.98, 0.99] | 1.00 [1.00, 1.00] | 0.98 [0.96, 1.00] | 1.00 [0.99, 1.00] | 0.73 [0.44, 0.95] | 0.94 [0.89, 0.98] | 0.61 [0.57, 0.65] |
| P1_mfw500_all_noprop_nocull | 1.00 [1.00, 1.00] | 1.00 | 0.99 [0.98, 0.99] | 0.99 [0.99, 1.00] | 1.00 [1.00, 1.00] | 0.98 [0.96, 1.00] | 1.00 [1.00, 1.00] | 0.97 [0.94, 0.99] | 0.95 [0.90, 0.99] | 0.68 [0.65, 0.72] |
| P6_closed_nopron | 0.99 [0.97, 1.00] | 1.00 | 0.97 [0.95, 0.99] | 0.98 [0.98, 0.99] | 1.00 [1.00, 1.00] | 0.93 [0.87, 0.98] | 1.00 [1.00, 1.00] | 0.90 [0.83, 0.96] | 0.99 [0.98, 1.00] | 0.63 [0.59, 0.66] |
| P6_closed_pron | 1.00 [0.99, 1.00] | 1.00 | 0.98 [0.97, 0.99] | 0.99 [0.98, 0.99] | 1.00 [1.00, 1.00] | 0.95 [0.92, 0.98] | 1.00 [1.00, 1.00] | 0.92 [0.86, 0.97] | 0.98 [0.96, 1.00] | 0.65 [0.61, 0.69] |
| P6_pron_only | 1.00 [1.00, 1.00] | 1.00 | 0.87 [0.82, 0.91] | 0.85 [0.79, 0.91] | 0.90 [0.81, 0.99] | 0.88 [0.83, 0.93] | 0.92 [0.84, 0.98] | 0.84 [0.75, 0.92] | 0.75 [0.56, 0.89] | 0.65 [0.61, 0.68] |

AUC difference from `P1_mfw500_all_noprop_nocull` on the same pairs [paired bootstrap 95%].

| block | translation_pair (n=10) | edition_pair (n=1) | same_author_unrelated (n=52) | same_author_orig_en (n=33) | same_author_same_translator (n=5) | same_author_diff_translator (n=14) | series (n=7) | retelling (n=8) | same_translator_diff_author (n=11) | same_genre (n=261) |
|---|---|---|---|---|---|---|---|---|---|---|
| P4_mfw500_tag3_rhythm | +0.00 [-0.00, +0.00] |  | -0.00 [-0.01, +0.00] | -0.00 [-0.01, +0.00] | +0.00 [+0.00, +0.00] | +0.00 [-0.00, +0.01] | -0.00 [-0.00, +0.00] | -0.24 [-0.47, -0.02] | -0.01 [-0.02, +0.00] | -0.07 [-0.10, -0.05] |
| P6_closed_nopron | -0.01 [-0.03, -0.00] |  | -0.02 [-0.03, -0.01] | -0.01 [-0.02, -0.00] | -0.00 [-0.00, +0.00] | -0.05 [-0.09, -0.01] | +0.00 [+0.00, +0.00] | -0.07 [-0.14, -0.03] | +0.03 [+0.01, +0.08] | -0.06 [-0.07, -0.04] |
| P6_closed_pron | -0.00 [-0.01, -0.00] |  | -0.01 [-0.02, -0.00] | -0.01 [-0.01, +0.00] | +0.00 [-0.00, +0.00] | -0.03 [-0.04, -0.01] | +0.00 [+0.00, +0.00] | -0.05 [-0.10, -0.02] | +0.03 [+0.01, +0.06] | -0.03 [-0.05, -0.02] |
| P6_pron_only | +0.00 [+0.00, +0.00] |  | -0.12 [-0.17, -0.08] | -0.14 [-0.20, -0.08] | -0.10 [-0.19, -0.01] | -0.10 [-0.16, -0.04] | -0.08 [-0.16, -0.02] | -0.13 [-0.22, -0.04] | -0.21 [-0.36, -0.08] | -0.03 [-0.07, +0.01] |

Mean percentile rank of the partner (0 = nearest book) / recall@1 / recall@5.

| block | translation_pair (n=10) | edition_pair (n=1) | same_author_unrelated (n=52) | same_author_orig_en (n=33) | same_author_same_translator (n=5) | same_author_diff_translator (n=14) | series (n=7) | retelling (n=8) | same_translator_diff_author (n=11) | same_genre (n=261) |
|---|---|---|---|---|---|---|---|---|---|---|
| P4_mfw500_tag3_rhythm | 0.00 / 0.94 / 1.00 | 0.00 / 1.00 / 1.00 | 0.02 / 0.69 / 0.98 | 0.02 / 0.81 / 0.97 | 0.01 / 0.71 / 1.00 | 0.03 / 0.12 / 0.94 | 0.00 / 0.86 / 1.00 | 0.24 / 0.30 / 0.50 | 0.09 / 0.00 / 0.83 | 0.38 / 0.09 / 0.72 |
| P1_mfw500_all_noprop_nocull | 0.00 / 0.94 / 0.94 | 0.00 / 1.00 / 1.00 | 0.02 / 0.69 / 1.00 | 0.01 / 0.81 / 1.00 | 0.01 / 0.71 / 1.00 | 0.03 / 0.12 / 0.94 | 0.00 / 1.00 / 1.00 | 0.04 / 0.50 / 0.80 | 0.07 / 0.00 / 1.00 | 0.33 / 0.19 / 0.79 |
| P6_closed_nopron | 0.01 / 0.82 / 0.94 | 0.00 / 1.00 / 1.00 | 0.03 / 0.69 / 0.94 | 0.02 / 0.81 / 0.94 | 0.01 / 0.71 / 1.00 | 0.07 / 0.12 / 0.81 | 0.00 / 0.86 / 1.00 | 0.13 / 0.20 / 0.50 | 0.04 / 0.17 / 1.00 | 0.38 / 0.08 / 0.62 |
| P6_closed_pron | 0.01 / 0.88 / 0.94 | 0.00 / 1.00 / 1.00 | 0.03 / 0.67 / 0.94 | 0.02 / 0.78 / 0.91 | 0.01 / 0.86 / 1.00 | 0.06 / 0.06 / 0.88 | 0.00 / 1.00 / 1.00 | 0.09 / 0.20 / 0.70 | 0.05 / 0.17 / 1.00 | 0.36 / 0.11 / 0.68 |
| P6_pron_only | 0.00 / 1.00 / 1.00 | 0.00 / 1.00 / 1.00 | 0.13 / 0.48 / 0.62 | 0.14 / 0.56 / 0.66 | 0.10 / 0.29 / 0.71 | 0.11 / 0.19 / 0.50 | 0.07 / 0.43 / 0.50 | 0.13 / 0.10 / 0.50 | 0.26 / 0.00 / 0.83 | 0.36 / 0.19 / 0.72 |

Split-half self-retrieval (accuracy; chance is 1/n), and Spearman of distance with |year difference| and |log word-count difference| (Mantel p in brackets; en = both books written in English; diff = different authors only).

| block | n | input | split a/b | split h1/h2 | rho year | rho year en | rho year en diff | rho logwords | rho logwords diff |
|---|---|---|---|---|---|---|---|---|---|
| P4_mfw500_tag3_rhythm | 87 | ordered text | 0.97 | 0.91 | 0.36 (0.005) | 0.34 (0.005) | 0.31 | 0.05 (0.180) | 0.03 |
| P1_mfw500_all_noprop_nocull | 87 | ordered text | 0.97 | 0.92 | 0.18 (0.005) | 0.24 (0.005) | 0.21 | 0.06 (0.005) | 0.04 |
| P6_closed_nopron | 87 | book bag | 0.93 | 0.88 | 0.17 (0.005) | 0.23 (0.005) | 0.20 | 0.06 (0.005) | 0.05 |
| P6_closed_pron | 87 | book bag | 0.95 | 0.89 | 0.18 (0.005) | 0.22 (0.005) | 0.19 | 0.05 (0.020) | 0.04 |
| P6_pron_only | 87 | book bag | 0.68 | 0.52 | 0.11 (0.005) | 0.06 (0.025) | 0.03 | 0.02 (0.175) | 0.01 |

Top-5 neighbour make-up (observed / chance) and hubness (skew of the 5-nearest in-degree; share of books in nobody's top 5; largest in-degree and the book).

| block | same author | same genre | mean abs year diff | mean abs log-words diff | hub skew | in no top 5 | max in-degree |
|---|---|---|---|---|---|---|---|
| P4_mfw500_tag3_rhythm | 0.40 / 0.02 | 0.38 / 0.12 | 27 / 56 | 0.64 / 0.78 | 1.00 | 0.02 | 17 (wells_worlds) |
| P1_mfw500_all_noprop_nocull | 0.41 / 0.02 | 0.47 / 0.12 | 32 / 56 | 0.63 / 0.78 | 0.33 | 0.02 | 11 (austen_emma) |
| P6_closed_nopron | 0.38 / 0.02 | 0.36 / 0.12 | 33 / 56 | 0.66 / 0.78 | 0.20 | 0.06 | 12 (sinclair_olivier) |
| P6_closed_pron | 0.38 / 0.02 | 0.39 / 0.12 | 33 / 56 | 0.68 / 0.78 | 0.13 | 0.06 | 13 (sinclair_olivier) |
| P6_pron_only | 0.24 / 0.02 | 0.27 / 0.12 | 37 / 56 | 0.73 / 0.78 | 0.41 | 0.00 | 11 (gentlefolk_garnett) |

Spearman between the pair distances of two blocks, all pairs.

| block | P4_mfw500_tag3_rhythm | P1_mfw500_all_noprop_nocull | P6_closed_nopron | P6_closed_pron | P6_pron_only |
|---|---|---|---|---|---|
| P4_mfw500_tag3_rhythm | 1.00 | 0.74 | 0.67 | 0.69 | 0.39 |
| P1_mfw500_all_noprop_nocull | 0.74 | 1.00 | 0.86 | 0.88 | 0.46 |
| P6_closed_nopron | 0.67 | 0.86 | 1.00 | 0.95 | 0.32 |
| P6_closed_pron | 0.69 | 0.88 | 0.95 | 1.00 | 0.57 |
| P6_pron_only | 0.39 | 0.46 | 0.32 | 0.57 | 1.00 |

Spearman between the pair distances of two blocks, different-author pairs only.

| block | P4_mfw500_tag3_rhythm | P1_mfw500_all_noprop_nocull | P6_closed_nopron | P6_closed_pron | P6_pron_only |
|---|---|---|---|---|---|
| P4_mfw500_tag3_rhythm | 1.00 | 0.72 | 0.66 | 0.67 | 0.36 |
| P1_mfw500_all_noprop_nocull | 0.72 | 1.00 | 0.85 | 0.87 | 0.43 |
| P6_closed_nopron | 0.66 | 0.85 | 1.00 | 0.95 | 0.30 |
| P6_closed_pron | 0.67 | 0.87 | 0.95 | 1.00 | 0.55 |
| P6_pron_only | 0.36 | 0.43 | 0.30 | 0.55 | 1.00 |

