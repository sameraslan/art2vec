## Felt projection, 87 books

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

