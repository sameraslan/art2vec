## W1 instruction prefix against none (maskB)

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

