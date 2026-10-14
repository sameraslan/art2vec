# All blocks against the framework's pair types

Blocks: Prose = `P4_mfw500_tag3_rhythm`, Prose (style encoder) = `P5_style_clean_c`, Telling = `T3_scalars_dtw20_sd`, World = `W1_qwen_maskB_c`, Story = `S_storychar_plain`, Felt = `F_reader`, Felt (no reader) = `F_proj_plain`.

Each cell: AUC that a labelled pair is closer than a negative pair [95% bootstrap interval over the labelled pairs], number of pairs, what FRAMEWORK.md section 9 expects, and the mark (rules in `storyblock/all_blocks.py`: near passes when the interval is above 0.5; apart fails when the interval is above 0.5; fewer than 3 pairs is always WITHIN-NOISE). The framework sets no expectation for Felt or for empty cells.

## Best variant of each block (Prose, Telling, World on 87 books, 3663 negatives; Story and Felt on the 24-book reader subset, 263 negatives)

| pair type | Prose | Prose (style encoder) | Telling | World | Story (24 books) | Felt (24 books) |
|---|---|---|---|---|---|---|
| Two halves of one book (a/b) | accuracy 0.97, 87 books (expects near) PASS | accuracy 0.70, 87 books (expects near) PASS | accuracy 0.74, 87 books (expects near) PASS | accuracy 0.96, 87 books (expects near) PASS | not defined | not defined |
| Two translations of one novel | 1.00 [1.00, 1.00], n=10 (expects apart) FAIL | 0.68 [0.47, 0.85], n=10 (expects apart) PASS | 0.99 [0.97, 1.00], n=10 (expects near) PASS | 1.00 [1.00, 1.00], n=10 (expects near) PASS | 1.00 [1.00, 1.00], n=3 (expects near) PASS | 0.99 [0.99, 1.00], n=3 |
| Two editions of one novel | 1.00, n=1 | 1.00, n=1 | 1.00, n=1 | 1.00, n=1 | 1.00, n=1 | 1.00, n=1 |
| Two novels by one author, unrelated plots | 0.99 [0.98, 0.99], n=52 (expects near) PASS | 0.77 [0.69, 0.84], n=52 (expects near) PASS | 0.72 [0.64, 0.78], n=52 | 0.91 [0.88, 0.94], n=52 | 0.99 [0.98, 0.99], n=5 (expects apart) FAIL | 0.98 [0.94, 1.00], n=5 |
| Two books of one series | 1.00 [0.99, 1.00], n=7 (expects near) PASS | 0.94 [0.88, 0.98], n=7 (expects near) PASS | 0.78 [0.62, 0.92], n=7 (expects near) PASS | 0.99 [0.97, 1.00], n=7 (expects near) PASS | 0.99 [0.98, 1.00], n=3 | 0.99 [0.98, 1.00], n=3 |
| A retelling and its source | 0.73 [0.44, 0.95], n=8 (expects apart) PASS | 0.71 [0.52, 0.86], n=8 (expects apart) FAIL | 0.45 [0.23, 0.68], n=8 | 0.98 [0.93, 1.00], n=8 | 1.00, n=1 (expects near) WITHIN-NOISE | 1.00, n=1 |
| Same genre, different authors (control) | 0.61 [0.57, 0.65], n=261 | 0.57 [0.53, 0.60], n=261 | 0.52 [0.49, 0.56], n=261 | 0.80 [0.78, 0.82], n=261 | 0.82 [0.76, 0.89], n=26 | 0.73 [0.62, 0.83], n=26 |

## The same five blocks on the 24-book subset only (263 negatives)

| pair type | Prose | Prose (style encoder) | Telling | World | Story | Felt | Felt (no reader) |
|---|---|---|---|---|---|---|---|
| Two halves of one book (a/b) | accuracy 0.88, 24 books (expects near) PASS | accuracy 0.92, 24 books (expects near) PASS | accuracy 0.71, 24 books (expects near) PASS | accuracy 0.94, 24 books (expects near) PASS | not defined | not defined | accuracy 0.65, 24 books  |
| Two translations of one novel | 1.00 [0.99, 1.00], n=3 (expects apart) FAIL | 0.28 [0.03, 0.70], n=3 (expects apart) PASS | 1.00 [1.00, 1.00], n=3 (expects near) PASS | 1.00 [1.00, 1.00], n=3 (expects near) PASS | 1.00 [1.00, 1.00], n=3 (expects near) PASS | 0.99 [0.99, 1.00], n=3 | 0.70 [0.15, 1.00], n=3 |
| Two editions of one novel | 1.00, n=1 | 0.99, n=1 | 1.00, n=1 | 1.00, n=1 | 1.00, n=1 | 1.00, n=1 | 1.00, n=1 |
| Two novels by one author, unrelated plots | 0.96 [0.89, 1.00], n=5 (expects near) PASS | 0.50 [0.17, 0.82], n=5 (expects near) WITHIN-NOISE | 0.76 [0.55, 0.93], n=5 | 0.90 [0.84, 0.96], n=5 | 0.99 [0.98, 0.99], n=5 (expects apart) FAIL | 0.98 [0.94, 1.00], n=5 | 0.71 [0.51, 0.90], n=5 |
| Two books of one series | 1.00 [0.99, 1.00], n=3 (expects near) PASS | 0.89 [0.84, 0.99], n=3 (expects near) PASS | 0.64 [0.33, 0.91], n=3 (expects near) WITHIN-NOISE | 1.00 [1.00, 1.00], n=3 (expects near) PASS | 0.99 [0.98, 1.00], n=3 | 0.99 [0.98, 1.00], n=3 | 0.84 [0.68, 0.95], n=3 |
| A retelling and its source | 1.00, n=1 (expects apart) WITHIN-NOISE | 0.52, n=1 (expects apart) WITHIN-NOISE | 0.99, n=1 | 1.00, n=1 | 1.00, n=1 (expects near) WITHIN-NOISE | 1.00, n=1 | 0.92, n=1 |
| Same genre, different authors (control) | 0.70 [0.60, 0.80], n=26 | 0.63 [0.53, 0.72], n=26 | 0.65 [0.55, 0.75], n=26 | 0.87 [0.82, 0.92], n=26 | 0.82 [0.76, 0.89], n=26 | 0.73 [0.62, 0.83], n=26 | 0.73 [0.65, 0.81], n=26 |

## Cross-block Spearman of pair distances

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
